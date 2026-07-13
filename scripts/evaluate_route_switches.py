#!/usr/bin/env python3
"""Validate route-switch samples and classify launch route actions."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SAMPLES_PATH = ROOT / "docs" / "evals" / "route-switch-samples.json"

ACTIONS = ["continue", "narrow_claim", "switch_route", "pause_spread"]

PAUSE_TERMS = ["控评", "删评", "虚假宣传", "隐私", "安全", "批量缺陷", "投诉", "价值观", "S3", "S4"]
SWITCH_TERMS = ["打穿", "备选", "套壳", "PPT功能", "成立条件被", "主打卖点", "切换"]
NARROW_TERMS = ["没有同源", "第一", "口径", "待验证", "还没有统一", "缺证据"]
CONTINUE_TERMS = ["已确认", "已排班", "可用", "正向", "收藏", "询价"]


def load_samples() -> dict:
    return json.loads(SAMPLES_PATH.read_text(encoding="utf-8"))


def fail(message: str) -> int:
    print(f"FAIL {message}")
    return 1


def classify_text(text: str) -> str:
    if any(term in text for term in PAUSE_TERMS):
        return "pause_spread"
    if any(term in text for term in SWITCH_TERMS):
        return "switch_route"
    if any(term in text for term in NARROW_TERMS):
        return "narrow_claim"
    if any(term in text for term in CONTINUE_TERMS):
        return "continue"
    return "narrow_claim"


def marker_for_action(action: str) -> str:
    return {
        "continue": "继续主路线，保留监控项",
        "narrow_claim": "缩窄主张，补证据或改口径",
        "switch_route": "切换到备选路线，替换首发物料",
        "pause_spread": "暂停扩散，复核事实并统一口径",
    }[action]


def validate_samples(data: dict) -> int:
    actions = data.get("actions", [])
    if actions != ACTIONS:
        return fail("route switch actions mismatch")
    samples = data.get("samples", [])
    if len(samples) < 7:
        return fail("route switch samples must include at least 7 rows")
    ids = set()
    seen_actions = set()
    for item in samples:
        sample_id = item.get("id", "")
        if not sample_id or sample_id in ids:
            return fail("route switch sample missing or duplicate id")
        ids.add(sample_id)
        action = item.get("expected_action")
        if action not in actions:
            return fail(f"route switch sample has invalid action: {sample_id}")
        seen_actions.add(action)
        for key in ["input", "required_terms"]:
            if not item.get(key):
                return fail(f"route switch sample missing {key}: {sample_id}")
        predicted = classify_text(item["input"])
        if predicted != action:
            return fail(f"route switch classification mismatch: {sample_id} expected {action}, got {predicted}")
    if seen_actions != set(actions):
        return fail("route switch samples must cover all actions")
    print(f"route switch sample check passed: {len(samples)} samples")
    return 0


def scan_text(text: str) -> int:
    action = classify_text(text)
    print(f"route_switch_action: {action}")
    print(f"marker: {marker_for_action(action)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate or scan route-switch actions.")
    parser.add_argument("--check", action="store_true", help="validate sample structure")
    parser.add_argument("--text", help="scan one launch route signal")
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
