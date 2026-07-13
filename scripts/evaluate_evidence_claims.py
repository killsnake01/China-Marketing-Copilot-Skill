#!/usr/bin/env python3
"""Validate evidence claim samples and classify unsupported marketing claims."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SAMPLES_PATH = ROOT / "docs" / "evals" / "evidence-claim-samples.json"

ACTIONS = [
    "verified",
    "mark_pending",
    "same_source_required",
    "unsupported",
    "forbidden_absolute",
]

HIGH_TEMPORAL_TERMS = [
    "现在",
    "当前",
    "最新",
    "近期",
    "到手价",
    "首发价",
    "补贴",
    "第一",
    "销量",
    "排名",
    "份额",
    "全网",
    "热搜",
    "刷屏",
    "新品",
    "规格",
    "KOL",
    "口碑",
]

ABSOLUTE_TERMS = [
    "唯一",
    "最强",
    "遥遥领先",
    "没有任何机会",
    "绝对领先",
    "全面碾压",
    "行业第一",
]

COMPARISON_TERMS = ["比竞品", "更强", "更好", "领先", "超过", "胜过", "对比"]
SAME_SOURCE_TERMS = ["同源", "同一份", "同场景", "同口径"]
SAME_SOURCE_GAP_TERMS = ["没有同源", "缺同源", "同源不足", "不同源"]
SUPPORTED_EVIDENCE_TERMS = ["用户提供", "历史案例", "横评显示", "数据显示", "来源"]


def load_samples() -> dict:
    return json.loads(SAMPLES_PATH.read_text(encoding="utf-8"))


def fail(message: str) -> int:
    print(f"FAIL {message}")
    return 1


def classify_claim(text: str) -> str:
    if "知识库暂无" in text or "知识库没有" in text or "没有" in text and "评测数据" in text:
        return "unsupported"
    if any(term in text for term in ABSOLUTE_TERMS):
        return "forbidden_absolute"
    if any(term in text for term in SAME_SOURCE_GAP_TERMS):
        return "same_source_required"
    if any(term in text for term in HIGH_TEMPORAL_TERMS):
        return "mark_pending"
    if any(term in text for term in COMPARISON_TERMS) and not any(term in text for term in SAME_SOURCE_TERMS):
        return "same_source_required"
    if any(term in text for term in SUPPORTED_EVIDENCE_TERMS + SAME_SOURCE_TERMS):
        return "verified"
    return "mark_pending"


def marker_for_action(action: str) -> str:
    return {
        "verified": "来源/证据已标注",
        "mark_pending": "[待验证]",
        "same_source_required": "同源数据不足",
        "unsupported": "知识库暂无此数据",
        "forbidden_absolute": "禁用绝对化表达",
    }[action]


def validate_samples(data: dict) -> int:
    actions = data.get("actions", [])
    if actions != ACTIONS:
        return fail("evidence claim actions mismatch")
    samples = data.get("samples", [])
    if len(samples) < 10:
        return fail("evidence claim samples must include at least 10 rows")
    ids = set()
    seen_actions = set()
    for item in samples:
        sample_id = item.get("id", "")
        if not sample_id or sample_id in ids:
            return fail("evidence claim sample missing or duplicate id")
        ids.add(sample_id)
        action = item.get("expected_action")
        if action not in actions:
            return fail(f"evidence claim sample has invalid action: {sample_id}")
        seen_actions.add(action)
        for key in ["claim", "claim_type", "required_marker"]:
            if not item.get(key):
                return fail(f"evidence claim sample missing {key}: {sample_id}")
        predicted = classify_claim(item["claim"])
        if predicted != action:
            return fail(f"evidence claim classification mismatch: {sample_id} expected {action}, got {predicted}")
    if seen_actions != set(actions):
        return fail("evidence claim samples must cover all actions")
    print(f"evidence claim check passed: {len(samples)} samples")
    return 0


def scan_text(text: str) -> int:
    action = classify_claim(text)
    print(f"claim_action: {action}")
    print(f"marker: {marker_for_action(action)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate or scan evidence claims.")
    parser.add_argument("--check", action="store_true", help="validate sample structure")
    parser.add_argument("--text", help="scan one claim")
    parser.add_argument("--input", help="scan a text file")
    args = parser.parse_args()

    status = validate_samples(load_samples())
    if status:
        return status
    if args.text:
        return scan_text(args.text)
    if args.input:
        return scan_text(Path(args.input).read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
