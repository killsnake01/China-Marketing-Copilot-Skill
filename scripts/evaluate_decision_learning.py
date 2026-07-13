#!/usr/bin/env python3
"""Validate decision-learning samples and classify post-launch learning actions."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SAMPLES_PATH = ROOT / "docs" / "evals" / "decision-learning-samples.json"

ACTIONS = ["keep_route", "update_evidence", "ban_phrase", "raise_threshold", "update_kol_record"]

BAN_TERMS = ["禁用", "PPT功能", "套壳", "固定梗", "医疗暗示", "全面重塑", "全天候守护"]
KOL_TERMS = ["KOL", "口播", "恰饭", "合作"]
THRESHOLD_TERMS = ["阈值过低", "误报", "低赞", "过早改稿"]
EVIDENCE_TERMS = ["数据来源", "样张条件", "同源对比", "价格权益", "补贴条件", "官方价"]
KEEP_TERMS = ["自发复述", "询价", "收藏", "负面没有攻击", "继续观察"]


def load_samples() -> dict:
    return json.loads(SAMPLES_PATH.read_text(encoding="utf-8"))


def fail(message: str) -> int:
    print(f"FAIL {message}")
    return 1


def classify_text(text: str) -> str:
    if any(term in text for term in BAN_TERMS):
        return "ban_phrase"
    if any(term in text for term in KOL_TERMS):
        return "update_kol_record"
    if any(term in text for term in THRESHOLD_TERMS):
        return "raise_threshold"
    if any(term in text for term in EVIDENCE_TERMS):
        return "update_evidence"
    if any(term in text for term in KEEP_TERMS):
        return "keep_route"
    return "update_evidence"


def marker_for_action(action: str) -> str:
    return {
        "keep_route": "路线保留，沉淀可复用证据",
        "update_evidence": "补证据，更新证据要求",
        "ban_phrase": "禁用话术，补替代表达",
        "raise_threshold": "更新阈值，降低误报",
        "update_kol_record": "更新KOL记录，复核合作口播",
    }[action]


def validate_samples(data: dict) -> int:
    actions = data.get("actions", [])
    if actions != ACTIONS:
        return fail("decision learning actions mismatch")
    samples = data.get("samples", [])
    if len(samples) < 7:
        return fail("decision learning samples must include at least 7 rows")
    ids = set()
    seen_actions = set()
    for item in samples:
        sample_id = item.get("id", "")
        if not sample_id or sample_id in ids:
            return fail("decision learning sample missing or duplicate id")
        ids.add(sample_id)
        action = item.get("expected_action")
        if action not in actions:
            return fail(f"decision learning sample has invalid action: {sample_id}")
        seen_actions.add(action)
        for key in ["input", "required_terms"]:
            if not item.get(key):
                return fail(f"decision learning sample missing {key}: {sample_id}")
        predicted = classify_text(item["input"])
        if predicted != action:
            return fail(f"decision learning classification mismatch: {sample_id} expected {action}, got {predicted}")
    if seen_actions != set(actions):
        return fail("decision learning samples must cover all actions")
    print(f"decision learning sample check passed: {len(samples)} samples")
    return 0


def scan_text(text: str) -> int:
    action = classify_text(text)
    print(f"decision_learning_action: {action}")
    print(f"marker: {marker_for_action(action)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate or scan decision-learning actions.")
    parser.add_argument("--check", action="store_true", help="validate sample structure")
    parser.add_argument("--text", help="scan one post-launch learning note")
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
