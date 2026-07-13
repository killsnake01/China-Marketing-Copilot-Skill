#!/usr/bin/env python3
"""Validate and lightly classify post-launch war-room samples."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SAMPLES_PATH = ROOT / "docs/evals/post-launch-samples.json"

DECISIONS = ["continue", "narrow_claim", "switch_route", "pause_spread"]

KEYWORDS = {
    "pause_spread": ["控评", "删评", "虚假宣传", "数据造假", "隐私", "冒犯", "批量缺陷", "安全"],
    "switch_route": ["主打", "主线", "路线", "发热", "掉帧", "PPT功能", "套壳", "固定梗"],
    "narrow_claim": ["数据哪来的", "实测呢", "影像第一", "首发冤种", "背刺", "价格权益", "客服"],
    "continue": ["自发复述", "收藏", "询价", "正向", "二创", "种草"],
}


def load_samples() -> dict:
    return json.loads(SAMPLES_PATH.read_text(encoding="utf-8"))


def classify(text: str) -> str:
    scores = {}
    for decision, words in KEYWORDS.items():
        scores[decision] = sum(1 for word in words if word in text)
    for decision in ["pause_spread", "switch_route", "narrow_claim", "continue"]:
        if scores.get(decision, 0) > 0:
            return decision
    return "narrow_claim"


def check_samples() -> int:
    data = load_samples()
    if data.get("decisions") != DECISIONS:
        print("post-launch decisions mismatch")
        return 1
    samples = data.get("samples", [])
    if len(samples) < 6:
        print("post-launch samples must include at least 6 items")
        return 1
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
        for key in ["window", "input", "required_terms"]:
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
    print(f"post-launch sample check passed: {len(samples)} samples")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate post-launch war-room samples.")
    parser.add_argument("--check", action="store_true", help="validate bundled samples")
    parser.add_argument("--text", help="classify one post-launch feedback snippet")
    args = parser.parse_args()

    if args.check or not args.text:
        result = check_samples()
        if result != 0:
            return result
    if args.text:
        print("post_launch_action: " + classify(args.text))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
