#!/usr/bin/env python3
"""Validate route-scorecard samples and classify route score snippets."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SAMPLES_PATH = ROOT / "docs" / "evals" / "route-scorecard-samples.json"

ROLES = ["推荐", "备选", "弃用"]
SCORE_FIELDS = [
    "evidence_score",
    "audience_fit_score",
    "competitor_defense_score",
    "risk_control_score",
    "resource_fit_score",
    "timing_score",
]


def load_samples() -> dict:
    return json.loads(SAMPLES_PATH.read_text(encoding="utf-8"))


def classify_route(text: str) -> tuple[str, str, int]:
    if any(term in text for term in ["弃用", "缺少任务级证据", "套壳", "固定梗", "资质", "监管", "风险不可控"]):
        return "弃用", "弃用", 11
    if any(term in text for term in ["备选", "切换", "辅助路线", "承接普通用户"]):
        return "备选", "保留备选", 18
    if any(term in text for term in ["同源横评", "用户原话", "已准备"]):
        return "推荐", "押主线", 25
    return "推荐", "押主线", 21


def fail(message: str) -> int:
    print(f"FAIL {message}")
    return 1


def validate_samples(data: dict) -> int:
    if data.get("route_roles") != ROLES:
        return fail("route-scorecard roles mismatch")
    if data.get("score_fields") != SCORE_FIELDS:
        return fail("route-scorecard score fields mismatch")
    samples = data.get("samples", [])
    if len(samples) < 6:
        return fail("route-scorecard samples must include at least 6 rows")
    ids = set()
    seen_roles = set()
    for item in samples:
        sample_id = item.get("id", "")
        if not sample_id or sample_id in ids:
            return fail("route-scorecard sample missing or duplicate id")
        ids.add(sample_id)
        role = item.get("expected_role")
        verdict = item.get("expected_verdict")
        if role not in ROLES:
            return fail(f"route-scorecard sample has invalid role: {sample_id}")
        seen_roles.add(role)
        if verdict not in {"押主线", "保留备选", "弃用"}:
            return fail(f"route-scorecard sample has invalid verdict: {sample_id}")
        for key in ["input", "required_terms"]:
            if not item.get(key):
                return fail(f"route-scorecard sample missing {key}: {sample_id}")
        predicted_role, predicted_verdict, total = classify_route(item["input"])
        if predicted_role != role:
            return fail(f"route-scorecard role mismatch: {sample_id} expected {role}, got {predicted_role}")
        if predicted_verdict != verdict:
            return fail(f"route-scorecard verdict mismatch: {sample_id} expected {verdict}, got {predicted_verdict}")
        if "minimum_total" in item and total < item["minimum_total"]:
            return fail(f"route-scorecard total too low: {sample_id} expected >= {item['minimum_total']}, got {total}")
        if "maximum_total" in item and total > item["maximum_total"]:
            return fail(f"route-scorecard total too high: {sample_id} expected <= {item['maximum_total']}, got {total}")
    if seen_roles != set(ROLES):
        return fail("route-scorecard samples must cover all route roles")
    print(f"route-scorecard sample check passed: {len(samples)} samples")
    return 0


def scan_text(text: str) -> int:
    role, verdict, total = classify_route(text)
    print(f"route_role: {role}")
    print(f"route_verdict: {verdict}")
    print(f"estimated_total: {total}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate or scan route scorecard samples.")
    parser.add_argument("--check", action="store_true", help="validate sample structure")
    parser.add_argument("--text", help="scan one route note")
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
