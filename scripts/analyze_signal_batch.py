#!/usr/bin/env python3
"""Analyze structured comment batches for negative propagation signals."""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from preprocess import LEVEL_ORDER, detect_negative_signals, load_negative_signal_rules


VALID_CATEGORIES = {"mobile", "headphones", "laptops", "wearables", "smart-home"}
VALID_ROLES = {"user", "kol", "media", "verified", "customer_service", "channel", "unknown"}
VALID_IMPACTS = {
    "none",
    "purchase_hesitation",
    "return_refund",
    "support_spike",
    "channel_delay",
    "launch_change",
}
AUTHORITY_ROLES = {"kol", "media", "verified"}
BUSINESS_ROLES = {"customer_service", "channel"}
HARD_STOP_SINGLE_SIGNALS = {"价值观冒犯", "KOL合作反噬"}
STAGE_ORDER = {"S0": 0, "S1": 1, "S2": 2, "S3": 3, "S4": 4}
STAGE_ACTIONS = {
    "S0": ("继续", "保留原文和来源，观察同类独立反馈。"),
    "S1": ("继续", "补充证据和客服口径，建立2小时滚动监测。"),
    "S2": ("缩窄", "缩窄争议主张，暂停继续放大同一卖点。"),
    "S3": ("暂停", "暂停争议物料扩散，统一事实口径并评估切换路线。"),
    "S4": ("暂停", "升级公关、产品、客服和渠道联合处理，记录业务影响。"),
}


def parse_timestamp(value: Any) -> datetime | None:
    if value in (None, ""):
        return None
    if not isinstance(value, str):
        raise ValueError("timestamp must be a string or null")
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError(f"invalid timestamp {value!r}") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"timestamp requires timezone offset: {value!r}")
    return parsed.astimezone(timezone.utc)


def content_fingerprint(content: str) -> str:
    normalized = content.casefold()
    normalized = re.sub(r"[\s\W_]+", "", normalized, flags=re.UNICODE)
    return normalized[:500]


def validate_record(item: dict[str, Any], line_number: int) -> dict[str, Any]:
    record_id = item.get("id") or f"line-{line_number}"
    content = item.get("content")
    if not isinstance(content, str) or not content.strip():
        raise ValueError(f"line {line_number}: content must be a non-empty string")
    platform = item.get("platform", "unknown")
    if not isinstance(platform, str) or not platform.strip():
        raise ValueError(f"line {line_number}: platform must be a non-empty string")
    author_id = item.get("author_id")
    if author_id is not None and not isinstance(author_id, str):
        raise ValueError(f"line {line_number}: author_id must be a string or null")
    role = item.get("author_role", "unknown")
    if role not in VALID_ROLES:
        raise ValueError(f"line {line_number}: invalid author_role {role!r}")
    engagement = item.get("engagement", 0)
    if not isinstance(engagement, int) or isinstance(engagement, bool) or engagement < 0:
        raise ValueError(f"line {line_number}: engagement must be a non-negative integer")
    impact = item.get("business_impact", "none")
    if impact not in VALID_IMPACTS:
        raise ValueError(f"line {line_number}: invalid business_impact {impact!r}")
    timestamp = parse_timestamp(item.get("timestamp"))
    return {
        "id": str(record_id),
        "content": content.strip(),
        "timestamp": timestamp,
        "timestamp_raw": item.get("timestamp"),
        "platform": platform.strip(),
        "author_id": author_id.strip() if isinstance(author_id, str) and author_id.strip() else None,
        "author_role": role,
        "engagement": engagement,
        "business_impact": impact,
        "url": item.get("url") if isinstance(item.get("url"), str) else None,
    }


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise ValueError(f"input file does not exist: {path}")
    records: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            raw = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"line {line_number}: invalid JSON: {exc}") from exc
        if not isinstance(raw, dict):
            raise ValueError(f"line {line_number}: each JSONL line must be an object")
        record = validate_record(raw, line_number)
        if record["id"] in seen_ids:
            raise ValueError(f"line {line_number}: duplicate id {record['id']!r}")
        seen_ids.add(record["id"])
        records.append(record)
    if not records:
        raise ValueError("input contains no records")
    return records


def metadata_quality(records: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(records)
    coverage = {
        "timestamp": sum(record["timestamp"] is not None for record in records) / total,
        "author": sum(record["author_id"] is not None for record in records) / total,
        "platform": sum(record["platform"] != "unknown" for record in records) / total,
        "role": sum(record["author_role"] != "unknown" for record in records) / total,
    }
    score = (
        coverage["timestamp"] * 0.35
        + coverage["author"] * 0.35
        + coverage["platform"] * 0.2
        + coverage["role"] * 0.1
    )
    level = "高" if score >= 0.8 else "中" if score >= 0.5 else "低"
    warnings = []
    if coverage["timestamp"] < 0.8:
        warnings.append("时间字段不足，传播速度和高阶段判断受限")
    if coverage["author"] < 0.8:
        warnings.append("账号字段不足，独立用户数可能被高估")
    if coverage["platform"] < 0.8:
        warnings.append("平台字段不足，无法确认跨平台扩散")
    if coverage["role"] < 0.5:
        warnings.append("角色字段不足，无法确认权威放大")
    return {
        "level": level,
        "score": round(score, 3),
        "coverage": {key: round(value, 3) for key, value in coverage.items()},
        "warnings": warnings,
    }


def velocity_metrics(records: list[dict[str, Any]]) -> dict[str, Any]:
    timestamps = sorted(record["timestamp"] for record in records if record["timestamp"] is not None)
    if not timestamps:
        return {
            "window_hours": 2,
            "recent_mentions": 0,
            "previous_mentions": 0,
            "ratio": None,
            "spike": False,
            "earliest": None,
            "latest": None,
        }
    latest = timestamps[-1]
    recent_start = latest - timedelta(hours=2)
    previous_start = latest - timedelta(hours=4)
    recent = sum(timestamp > recent_start for timestamp in timestamps)
    previous = sum(previous_start < timestamp <= recent_start for timestamp in timestamps)
    ratio = round(recent / max(previous, 1), 2)
    return {
        "window_hours": 2,
        "recent_mentions": recent,
        "previous_mentions": previous,
        "ratio": ratio,
        "spike": recent >= 3 and ratio >= 2,
        "earliest": timestamps[0].isoformat(),
        "latest": latest.isoformat(),
    }


def infer_batch_stage(
    mention_count: int,
    independent_count: int,
    unique_authors: int,
    author_coverage: float,
    timestamp_coverage: float,
    platform_count: int,
    authority_count: int,
    business_impact_count: int,
    institutional_impact_count: int,
    refund_count: int,
    repetition_noise: bool,
) -> str:
    stage = 0
    if independent_count >= 2:
        stage = 1
    if mention_count >= 4 and independent_count >= 4:
        stage = 2
    if stage >= 2 and ((platform_count >= 2 and authority_count >= 1) or authority_count >= 2):
        stage = 3
    if independent_count >= 2 and (
        (institutional_impact_count >= 1 and business_impact_count >= 2)
        or refund_count >= 3
    ):
        stage = 4
    if author_coverage >= 0.5 and unique_authors <= 1:
        stage = 0
    elif repetition_noise:
        stage = min(stage, 1)
    if author_coverage < 0.5:
        stage = min(stage, 1)
    if timestamp_coverage < 0.5:
        stage = min(stage, 2)
    return f"S{stage}"


def aggregate_signal(name: str, items: list[dict[str, Any]]) -> dict[str, Any]:
    records = [item["record"] for item in items]
    signal_quality = metadata_quality(records)
    mention_count = len(records)
    author_ids = {record["author_id"] for record in records if record["author_id"]}
    platforms = {record["platform"] for record in records if record["platform"] != "unknown"}
    fingerprints = [content_fingerprint(record["content"]) for record in records]
    unique_content = len(set(fingerprints))
    duplicate_ratio = 1 - (unique_content / mention_count)
    author_coverage = sum(record["author_id"] is not None for record in records) / mention_count
    timestamp_coverage = sum(record["timestamp"] is not None for record in records) / mention_count
    if author_coverage >= 0.5:
        independent_count = len(author_ids)
    else:
        independent_count = unique_content
    authority_count = sum(record["author_role"] in AUTHORITY_ROLES for record in records)
    business_impact_count = sum(record["business_impact"] != "none" for record in records)
    institutional_impact_count = sum(
        record["business_impact"] in {"support_spike", "channel_delay", "launch_change"}
        for record in records
    )
    refund_count = sum(record["business_impact"] == "return_refund" for record in records)
    business_role_count = sum(record["author_role"] in BUSINESS_ROLES for record in records)
    repetition_noise = (
        mention_count >= 3
        and (
            (author_coverage >= 0.5 and len(author_ids) <= 1)
            or duplicate_ratio >= 0.8
        )
    )
    stage = infer_batch_stage(
        mention_count=mention_count,
        independent_count=independent_count,
        unique_authors=len(author_ids),
        author_coverage=author_coverage,
        timestamp_coverage=timestamp_coverage,
        platform_count=len(platforms),
        authority_count=authority_count,
        business_impact_count=business_impact_count,
        institutional_impact_count=institutional_impact_count,
        refund_count=refund_count,
        repetition_noise=repetition_noise,
    )
    velocity = velocity_metrics(records)
    base_level = max(
        (item["signal"]["level"] for item in items),
        key=lambda level: LEVEL_ORDER[level],
    )
    level = base_level
    if STAGE_ORDER[stage] >= 2 and LEVEL_ORDER[level] < LEVEL_ORDER["高"]:
        level = "高"
    route_impact, stage_action = STAGE_ACTIONS[stage]
    if name in HARD_STOP_SINGLE_SIGNALS:
        route_impact = "暂停"
        stage_action = "暂停相关物料或合作，先复核事实和价值观风险。"
    flags = []
    if repetition_noise:
        flags.append("重复传播噪声")
    if velocity["spike"]:
        flags.append("传播速度上升")
    if len(platforms) >= 2:
        flags.append("跨平台")
    if authority_count:
        flags.append("权威角色放大")
    if business_impact_count:
        flags.append("业务影响")
    if author_coverage < 0.5 or timestamp_coverage < 0.5:
        flags.append("元数据缺口")
    action = items[0]["signal"].get("action", "人工复核该负面信号。")
    samples = sorted(records, key=lambda record: (-record["engagement"], record["id"]))[:3]
    return {
        "name": name,
        "level": level,
        "stage": stage,
        "route_impact": route_impact,
        "mentions": mention_count,
        "independent_count": independent_count,
        "unique_authors": len(author_ids),
        "platforms": sorted(platforms),
        "authority_mentions": authority_count,
        "business_impact_mentions": business_impact_count,
        "business_role_mentions": business_role_count,
        "engagement_total": sum(record["engagement"] for record in records),
        "duplicate_ratio": round(duplicate_ratio, 3),
        "velocity": velocity,
        "flags": flags,
        "metadata_quality": signal_quality["level"],
        "recommended_action": f"{stage_action} {action}",
        "samples": [
            {
                "id": record["id"],
                "content": record["content"][:160],
                "platform": record["platform"],
                "author_role": record["author_role"],
                "engagement": record["engagement"],
                "url": record["url"],
            }
            for record in samples
        ],
    }


def analyze_records(records: list[dict[str, Any]], category: str) -> dict[str, Any]:
    if category not in VALID_CATEGORIES:
        raise ValueError(f"unsupported category: {category}")
    quality = metadata_quality(records)
    rules = load_negative_signal_rules(category)
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        detected = detect_negative_signals(record["content"], category, "comments", rules=rules)
        for signal in detected:
            grouped[signal["name"]].append({"record": record, "signal": signal})
    signals = [aggregate_signal(name, items) for name, items in grouped.items()]
    signals.sort(
        key=lambda item: (
            -STAGE_ORDER[item["stage"]],
            -LEVEL_ORDER[item["level"]],
            -item["mentions"],
            item["name"],
        )
    )
    platform_counts = Counter(record["platform"] for record in records)
    return {
        "version": 1,
        "category": category,
        "record_count": len(records),
        "platform_counts": dict(sorted(platform_counts.items())),
        "metadata_quality": quality,
        "signals": signals,
        "notes": [
            "阶段依据当前导入批次计算，不代表全网舆情规模。",
            "S3需要权威角色或跨平台证据，S4需要业务影响记录。",
            "重复内容或单账号刷屏会限制阶段升级。",
        ],
    }


def markdown_cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ").strip()


def render_markdown(result: dict[str, Any]) -> str:
    quality = result["metadata_quality"]
    lines = [
        "# 负面传播批次分析",
        "",
        f"> 品类: {result['category']}",
        f"> 记录数: {result['record_count']}",
        f"> 元数据质量: {quality['level']}（{quality['score']:.3f}）",
        "> 口径: 只判断当前导入批次，不代表全网舆情规模",
        "",
        "## 数据质量",
        "",
        f"- 时间覆盖: {quality['coverage']['timestamp']:.1%}",
        f"- 账号覆盖: {quality['coverage']['author']:.1%}",
        f"- 平台覆盖: {quality['coverage']['platform']:.1%}",
        f"- 角色覆盖: {quality['coverage']['role']:.1%}",
    ]
    lines.extend(f"- 提醒: {warning}" for warning in quality["warnings"])
    lines.extend(["", "## 信号总览", ""])
    if not result["signals"]:
        lines.append("- 当前批次未命中负面规则，仍需人工检查规则外问题。")
    else:
        lines.extend([
            "| 信号 | 等级 | 阶段 | 路线影响 | 提及 | 独立账号 | 平台 | 2小时速度 | 标记 |",
            "|------|------|------|----------|------|----------|------|-----------|------|",
        ])
        for signal in result["signals"]:
            velocity = signal["velocity"]
            ratio = "缺数据" if velocity["ratio"] is None else f"{velocity['ratio']:.2f}x"
            lines.append(
                f"| {markdown_cell(signal['name'])} | {signal['level']} | {signal['stage']} | "
                f"{signal['route_impact']} | {signal['mentions']} | {signal['unique_authors']} | "
                f"{markdown_cell('、'.join(signal['platforms']) or '未知')} | {ratio} | "
                f"{markdown_cell('、'.join(signal['flags']) or '无')} |"
            )
        lines.extend(["", "## 优先动作", ""])
        for signal in result["signals"][:3]:
            lines.append(f"- **{signal['name']} / {signal['stage']}**：{signal['recommended_action']}")
    lines.extend(["", "## 口径说明", ""])
    lines.extend(f"- {note}" for note in result["notes"])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze a structured negative-signal JSONL batch")
    parser.add_argument("--input", required=True, help="JSONL input path")
    parser.add_argument("--category", required=True, choices=sorted(VALID_CATEGORIES))
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--output", help="output path; defaults to stdout")
    args = parser.parse_args()
    try:
        records = load_jsonl(Path(args.input))
        result = analyze_records(records, args.category)
    except ValueError as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 1
    output = (
        json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        if args.format == "json"
        else render_markdown(result)
    )
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"已保存到: {args.output}")
    else:
        print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
