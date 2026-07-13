#!/usr/bin/env python3
"""Validate risk-ledger samples and classify launch risk snippets."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SAMPLES_PATH = ROOT / "docs" / "evals" / "risk-ledger-samples.json"

PRIORITIES = ["P0", "P1", "P2", "P3"]
ROUTE_IMPACTS = ["继续", "缩窄", "切换", "暂停"]
FACT_STATUSES = ["known", "inferred", "needs_verification"]

P0_TERMS = ["医疗", "隐私", "安全", "监管", "批量缺陷", "虚假宣传", "客服机器人", "官方承认"]
P1_TERMS = ["AI全面", "PPT功能", "套壳", "固定梗", "影像第一", "数据来源", "样张条件", "首发冤种", "价格权益", "KOL", "恰饭", "唯一", "最强"]
P2_TERMS = ["审美", "外观", "颜色", "手感", "轻微"]
POSITIVE_TERMS = ["自发复述", "收藏", "询价", "可放大", "负面没有攻击"]


def load_samples() -> dict:
    return json.loads(SAMPLES_PATH.read_text(encoding="utf-8"))


def classify_priority(text: str) -> str:
    if any(term in text for term in P0_TERMS):
        return "P0"
    if any(term in text for term in P1_TERMS):
        return "P1"
    if any(term in text for term in P2_TERMS):
        return "P2"
    if any(term in text for term in POSITIVE_TERMS):
        return "P3"
    return "P2"


def classify_route_impact(text: str) -> str:
    priority = classify_priority(text)
    if priority == "P0":
        return "暂停"
    if "PPT功能" in text or "套壳" in text or "固定梗" in text:
        return "切换"
    if priority == "P1":
        return "缩窄"
    return "继续"


def marker(priority: str, route_impact: str) -> str:
    return {
        ("P0", "暂停"): "P0风险，先暂停并统一口径",
        ("P1", "切换"): "P1风险，准备切换路线",
        ("P1", "缩窄"): "P1风险，缩窄主张并补证据",
        ("P2", "继续"): "P2风险，继续但保留监控",
        ("P3", "继续"): "P3信号，可继续放大并观察",
    }.get((priority, route_impact), f"{priority}风险，路线影响:{route_impact}")


def fail(message: str) -> int:
    print(f"FAIL {message}")
    return 1


def validate_samples(data: dict) -> int:
    if data.get("priorities") != PRIORITIES:
        return fail("risk-ledger priorities mismatch")
    if data.get("route_impacts") != ROUTE_IMPACTS:
        return fail("risk-ledger route impacts mismatch")
    if data.get("fact_statuses") != FACT_STATUSES:
        return fail("risk-ledger fact statuses mismatch")
    samples = data.get("samples", [])
    if len(samples) < 8:
        return fail("risk-ledger samples must include at least 8 rows")
    ids = set()
    seen_priorities = set()
    seen_impacts = set()
    for item in samples:
        sample_id = item.get("id", "")
        if not sample_id or sample_id in ids:
            return fail("risk-ledger sample missing or duplicate id")
        ids.add(sample_id)
        priority = item.get("expected_priority")
        impact = item.get("expected_route_impact")
        if priority not in PRIORITIES:
            return fail(f"risk-ledger sample has invalid priority: {sample_id}")
        if impact not in ROUTE_IMPACTS:
            return fail(f"risk-ledger sample has invalid route impact: {sample_id}")
        seen_priorities.add(priority)
        seen_impacts.add(impact)
        for key in ["input", "required_terms"]:
            if not item.get(key):
                return fail(f"risk-ledger sample missing {key}: {sample_id}")
        predicted_priority = classify_priority(item["input"])
        predicted_impact = classify_route_impact(item["input"])
        if predicted_priority != priority:
            return fail(f"risk-ledger priority mismatch: {sample_id} expected {priority}, got {predicted_priority}")
        if predicted_impact != impact:
            return fail(f"risk-ledger route impact mismatch: {sample_id} expected {impact}, got {predicted_impact}")
    if seen_priorities != set(PRIORITIES):
        return fail("risk-ledger samples must cover all priorities")
    if seen_impacts != set(ROUTE_IMPACTS):
        return fail("risk-ledger samples must cover all route impacts")
    print(f"risk-ledger sample check passed: {len(samples)} samples")
    return 0


def scan_text(text: str) -> int:
    priority = classify_priority(text)
    impact = classify_route_impact(text)
    print(f"risk_priority: {priority}")
    print(f"route_impact: {impact}")
    print(f"marker: {marker(priority, impact)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate or scan launch risk-ledger samples.")
    parser.add_argument("--check", action="store_true", help="validate sample structure")
    parser.add_argument("--text", help="scan one launch risk note")
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
