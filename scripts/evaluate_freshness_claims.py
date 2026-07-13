#!/usr/bin/env python3
"""Validate freshness claim samples and flag high-temporal claims."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SAMPLES_PATH = ROOT / "docs" / "evals" / "freshness-claim-samples.json"

HIGH_TEMPORAL_TERMS = [
    "现在",
    "当前",
    "最新",
    "近期",
    "今年",
    "到手价",
    "补贴",
    "首发价",
    "第一",
    "销量",
    "排名",
    "市场份额",
    "热搜",
    "全网",
    "新品",
    "规格",
    "KOL",
    "口碑",
]

STABLE_TERMS = ["方法", "模板", "同源", "人群", "测试条件", "流程", "评分"]


def load_samples() -> dict:
    return json.loads(SAMPLES_PATH.read_text(encoding="utf-8"))


def fail(message: str) -> int:
    print(f"FAIL {message}")
    return 1


def classify_claim(text: str) -> str:
    if "知识库里没有" in text or "知识库暂无" in text:
        return "unsupported"
    if any(term in text for term in HIGH_TEMPORAL_TERMS):
        return "must_refresh"
    if any(term in text for term in STABLE_TERMS):
        return "stable"
    return "mark_pending"


def validate_samples(data: dict) -> int:
    actions = data.get("actions", [])
    if actions != ["must_refresh", "mark_pending", "stable", "unsupported"]:
        return fail("freshness actions mismatch")
    samples = data.get("samples", [])
    if len(samples) < 8:
        return fail("freshness samples must include at least 8 rows")
    ids = set()
    seen_actions = set()
    for item in samples:
        sample_id = item.get("id", "")
        if not sample_id or sample_id in ids:
            return fail("freshness sample missing or duplicate id")
        ids.add(sample_id)
        action = item.get("expected_action")
        if action not in actions:
            return fail(f"freshness sample has invalid action: {sample_id}")
        seen_actions.add(action)
        if not item.get("claim") or not item.get("claim_type") or not item.get("required_marker"):
            return fail(f"freshness sample missing fields: {sample_id}")
        predicted = classify_claim(item["claim"])
        if action == "must_refresh" and predicted != "must_refresh":
            return fail(f"freshness sample should trigger refresh: {sample_id}")
    if seen_actions != set(actions):
        return fail("freshness samples must cover all actions")
    print(f"freshness sample check passed: {len(samples)} samples")
    return 0


def scan_text(text: str) -> int:
    action = classify_claim(text)
    print(f"freshness_action: {action}")
    if action == "must_refresh":
        print("marker: [待验证]")
        return 0
    if action == "unsupported":
        print("marker: 知识库暂无此数据")
        return 0
    if action == "mark_pending":
        print("marker: [待验证]")
        return 0
    print("marker: stable")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate or scan freshness claims.")
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
