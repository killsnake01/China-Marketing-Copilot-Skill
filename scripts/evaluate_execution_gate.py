#!/usr/bin/env python3
"""Validate and lightly classify execution readiness gate samples."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SAMPLES_PATH = ROOT / "docs/evals/execution-gate-samples.json"

DECISIONS = ["直接执行", "调整后执行", "暂停重做"]

HARD_BLOCKER_TERMS = [
    "互相冲突",
    "不同来源",
    "没有任务级",
    "没有证据",
    "法务审核也未完成",
    "审核也未完成",
    "首发价",
    "补贴",
    "赠品",
    "渠道权益说法不一致",
    "页面写",
]

ADJUSTMENT_TERMS = [
    "还缺",
    "需要24小时",
    "24小时内补齐",
    "缺渠道确认",
    "缺负责人",
    "停投阈值",
    "FAQ",
]

READY_TERMS = [
    "已确认",
    "均已确认",
    "已补",
    "物料",
    "负责人",
    "监控指标",
    "72小时",
    "7天",
]


def load_samples() -> dict:
    return json.loads(SAMPLES_PATH.read_text(encoding="utf-8"))


def classify(text: str) -> str:
    if any(term in text for term in HARD_BLOCKER_TERMS):
        return "暂停重做"
    if any(term in text for term in ADJUSTMENT_TERMS):
        return "调整后执行"
    ready_hits = sum(1 for term in READY_TERMS if term in text)
    if ready_hits >= 3:
        return "直接执行"
    return "调整后执行"


def fail(message: str) -> int:
    print(f"FAIL {message}")
    return 1


def validate_samples() -> int:
    data = load_samples()
    if data.get("decisions") != DECISIONS:
        return fail("execution gate decisions mismatch")
    samples = data.get("samples", [])
    if len(samples) < 6:
        return fail("execution gate samples must include at least 6 items")
    ids = set()
    seen = set()
    failures = []
    for item in samples:
        sample_id = item.get("id", "")
        if not sample_id or sample_id in ids:
            failures.append(f"{sample_id or '<missing>'}: duplicate or missing id")
            continue
        ids.add(sample_id)
        decision = item.get("expected_decision")
        if decision not in DECISIONS:
            failures.append(f"{sample_id}: invalid decision")
            continue
        seen.add(decision)
        for key in ["input", "required_terms"]:
            if not item.get(key):
                failures.append(f"{sample_id}: missing {key}")
        predicted = classify(item.get("input", ""))
        if predicted != decision:
            failures.append(f"{sample_id}: expected {decision}, got {predicted}")
    missing = sorted(set(DECISIONS) - seen)
    if missing:
        failures.append("missing decision coverage: " + ", ".join(missing))
    if failures:
        for failure in failures:
            print(failure)
        return 1
    print(f"execution gate sample check passed: {len(samples)} samples")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate execution readiness gate samples.")
    parser.add_argument("--check", action="store_true", help="validate bundled samples")
    parser.add_argument("--text", help="classify one execution readiness snippet")
    args = parser.parse_args()

    if args.check or not args.text:
        result = validate_samples()
        if result != 0:
            return result
    if args.text:
        print("execution_gate_decision: " + classify(args.text))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
