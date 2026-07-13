#!/usr/bin/env python3
"""Validate decision-package samples and classify package status snippets."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SAMPLES_PATH = ROOT / "docs/evals/decision-package-samples.json"

STATUSES = ["可评审", "需补证据", "暂停评审"]
REQUIRED_SECTION_IDS = [
    "launch_brief",
    "control_summary",
    "executive_memo",
    "route_verdict",
    "route_scorecard",
    "evidence",
    "risk_ledger",
    "negative_radar",
    "route_switch",
    "readiness_gate",
    "next_actions",
]

PAUSE_TERMS = ["硬阻断", "证据冲突", "口径不一致", "P0", "资质", "法务审核未完成", "监管风险"]
NEEDS_EVIDENCE_TERMS = ["待补", "待验证", "缺任务级证据", "低于3分", "缺口", "补证据"]
READY_TERMS = ["已核验", "已确认", "无硬阻断", "同源横评", "用户原话", "包内目录完整"]


def load_samples() -> dict:
    return json.loads(SAMPLES_PATH.read_text(encoding="utf-8"))


def classify_status(text: str) -> str:
    risk_text = text.replace("无硬阻断", "")
    if any(term in risk_text for term in PAUSE_TERMS):
        return "暂停评审"
    if any(term in text for term in NEEDS_EVIDENCE_TERMS):
        return "需补证据"
    ready_hits = sum(1 for term in READY_TERMS if term in text)
    if ready_hits >= 2:
        return "可评审"
    return "需补证据"


def fail(message: str) -> int:
    print(f"FAIL {message}")
    return 1


def validate_samples(data: dict) -> int:
    if data.get("package_statuses") != STATUSES:
        return fail("decision-package statuses mismatch")
    if data.get("required_section_ids") != REQUIRED_SECTION_IDS:
        return fail("decision-package required section ids mismatch")
    samples = data.get("samples", [])
    if len(samples) < 6:
        return fail("decision-package samples must include at least 6 rows")
    ids = set()
    seen = set()
    for item in samples:
        sample_id = item.get("id", "")
        if not sample_id or sample_id in ids:
            return fail("decision-package sample missing or duplicate id")
        ids.add(sample_id)
        status = item.get("expected_status")
        if status not in STATUSES:
            return fail(f"decision-package sample has invalid status: {sample_id}")
        seen.add(status)
        for key in ["input", "required_terms"]:
            if not item.get(key):
                return fail(f"decision-package sample missing {key}: {sample_id}")
        predicted = classify_status(item["input"])
        if predicted != status:
            return fail(f"decision-package status mismatch: {sample_id} expected {status}, got {predicted}")
    if seen != set(STATUSES):
        return fail("decision-package samples must cover all statuses")
    print(f"decision-package sample check passed: {len(samples)} samples")
    return 0


def scan_text(text: str) -> int:
    print("package_status: " + classify_status(text))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate or scan launch decision package samples.")
    parser.add_argument("--check", action="store_true", help="validate bundled samples")
    parser.add_argument("--text", help="scan one package note")
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
