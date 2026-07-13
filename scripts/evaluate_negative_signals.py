#!/usr/bin/env python3
"""Run calibration checks for early negative-signal rules."""
import argparse
import json
import sys
from pathlib import Path

import preprocess

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_EVAL_PATH = ROOT / "docs" / "evals" / "negative-signal-samples.md"
ADVERSARIAL_EVAL_PATH = ROOT / "docs" / "evals" / "negative-signal-adversarial-samples.json"


def parse_signal_cell(value):
    value = value.strip()
    if not value or value == "无":
        return set()
    return {item.strip() for item in value.split("、") if item.strip()}


def parse_markdown_table(path):
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) != 6 or cells[0] in {"ID", "----"}:
            continue
        sample_id, mode, category, text, expected, not_expected = cells
        if not sample_id or sample_id.startswith("-"):
            continue
        rows.append({
            "id": sample_id,
            "mode": mode,
            "category": category,
            "text": text,
            "expected": parse_signal_cell(expected),
            "not_expected": parse_signal_cell(not_expected),
        })
    return rows


def evaluate(rows):
    results = []
    for row in rows:
        detected = {
            item["name"]
            for item in preprocess.detect_negative_signals(
                row["text"],
                row["category"],
                row["mode"],
            )
        }
        missing = row["expected"] - detected
        unexpected = row["not_expected"] & detected
        results.append({
            **row,
            "detected": detected,
            "missing": missing,
            "unexpected": unexpected,
            "passed": not missing and not unexpected,
        })
    return results


def evaluate_adversarial(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    results = []
    for sample in data.get("samples", []):
        detected_items = preprocess.detect_negative_signals(
            sample["text"],
            sample["category"],
            sample["mode"],
        )
        detected = {item["name"]: item for item in detected_items}
        findings = []
        for name, expected in sample.get("expected", {}).items():
            actual = detected.get(name)
            if not actual:
                findings.append(f"missing {name}")
                continue
            for field in ("level", "stage"):
                if expected.get(field) and actual.get(field) != expected[field]:
                    findings.append(f"{name} {field}: expected {expected[field]}, got {actual.get(field)}")
        for name in sample.get("forbidden", []):
            if name in detected:
                findings.append(f"unexpected {name}")
        results.append({
            "id": sample.get("id", "unknown"),
            "detected": detected,
            "findings": findings,
            "passed": not findings,
        })
    return results


def main():
    parser = argparse.ArgumentParser(description="Evaluate negative-signal rule samples.")
    parser.add_argument("--eval-file", default=str(DEFAULT_EVAL_PATH), help="Markdown sample table path")
    parser.add_argument("--show-passed", action="store_true", help="Print passed cases too")
    args = parser.parse_args()

    eval_path = Path(args.eval_file)
    if not eval_path.exists():
        print(f"错误: 样本文件不存在 {eval_path}", file=sys.stderr)
        return 1

    rows = parse_markdown_table(eval_path)
    if not rows:
        print(f"错误: 未读取到样本 {eval_path}", file=sys.stderr)
        return 1

    results = evaluate(rows)
    failed = [item for item in results if not item["passed"]]
    passed_count = len(results) - len(failed)

    adversarial_results = evaluate_adversarial(ADVERSARIAL_EVAL_PATH)
    adversarial_failed = [item for item in adversarial_results if not item["passed"]]
    adversarial_passed = len(adversarial_results) - len(adversarial_failed)

    print(
        f"negative-signal eval: {passed_count}/{len(results)} passed; "
        f"adversarial: {adversarial_passed}/{len(adversarial_results)} passed"
    )
    for item in results:
        if item["passed"] and not args.show_passed:
            continue
        status = "PASS" if item["passed"] else "FAIL"
        detected = "、".join(sorted(item["detected"])) or "无"
        print(f"{status} {item['id']}: detected={detected}")
        if item["missing"]:
            print(f"  missing: {'、'.join(sorted(item['missing']))}")
        if item["unexpected"]:
            print(f"  unexpected: {'、'.join(sorted(item['unexpected']))}")

    for item in adversarial_results:
        if item["passed"] and not args.show_passed:
            continue
        status = "PASS" if item["passed"] else "FAIL"
        detected = "、".join(sorted(item["detected"])) or "无"
        print(f"{status} {item['id']}: detected={detected}")
        for finding in item["findings"]:
            print(f"  {finding}")

    return 1 if failed or adversarial_failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
