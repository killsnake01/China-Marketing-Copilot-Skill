#!/usr/bin/env python3
"""Validate golden example assertions."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSERTION_PATH = ROOT / "docs/evals/golden-example-assertions.json"
REQUIRED_SECTIONS = ["## 原始输入", "## 任务路由", "## 最终输出片段", "## 关键判断依据", "## 预期断言"]


def heading_index(text: str, heading: str, start: int = 0) -> int:
    pattern = re.compile(rf"^{re.escape(heading)}\s*$", re.M)
    match = pattern.search(text, start)
    return -1 if not match else match.start()


def section_text(text: str, heading: str) -> str:
    pattern = re.compile(rf"^{re.escape(heading)}\s*$", re.M)
    match = pattern.search(text)
    if not match:
        return ""
    next_indexes = [
        heading_index(text, candidate, match.end())
        for candidate in REQUIRED_SECTIONS
        if candidate != heading
    ]
    next_indexes = [index for index in next_indexes if index != -1]
    end = min(next_indexes) if next_indexes else len(text)
    return text[match.end():end]


def final_output_snippet(text: str) -> str:
    output_section = section_text(text, "## 最终输出片段")
    fence = re.search(r"```[a-zA-Z0-9_-]*\n(.*?)```", output_section, re.S)
    if not fence:
        return output_section
    return fence.group(1)


def fail(message: str) -> int:
    print(f"FAIL {message}")
    return 1


def validate_sample(sample: dict) -> list[str]:
    findings: list[str] = []
    sample_id = sample.get("id", "unknown")
    rel_path = sample.get("path", "")
    path = ROOT / rel_path
    if not rel_path or not path.exists():
        return [f"{sample_id}: missing sample path {rel_path}"]

    text = path.read_text(encoding="utf-8")
    snippet = final_output_snippet(text)
    for section in REQUIRED_SECTIONS:
        if section not in text:
            findings.append(f"{sample_id}: missing section {section}")
    for route in sample.get("required_routes", []):
        if route not in text:
            findings.append(f"{sample_id}: missing route {route}")
        if not (ROOT / route).exists():
            findings.append(f"{sample_id}: route path not found {route}")
    for term in sample.get("output_required_terms", []):
        if term not in snippet:
            findings.append(f"{sample_id}: output missing term {term}")
    for term in sample.get("forbidden_output_terms", []):
        if term in snippet:
            findings.append(f"{sample_id}: output contains forbidden term {term}")
    for pair in sample.get("order_constraints", []):
        if len(pair) != 2:
            findings.append(f"{sample_id}: invalid order constraint {pair}")
            continue
        first, second = pair
        first_index = snippet.find(first)
        second_index = snippet.find(second)
        if first_index == -1 or second_index == -1 or first_index >= second_index:
            findings.append(f"{sample_id}: order mismatch {first} -> {second}")
    if "不能" not in section_text(text, "## 预期断言"):
        findings.append(f"{sample_id}: assertions missing negative guard")
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate golden examples against explicit assertions.")
    parser.add_argument("--check", action="store_true", help="validate assertion data and sample files")
    args = parser.parse_args()

    data = json.loads(ASSERTION_PATH.read_text(encoding="utf-8"))
    samples = data.get("samples", [])
    if len(samples) < 3:
        return fail("golden-example-assertions.json needs at least 3 samples")
    ids = set()
    findings: list[str] = []
    for sample in samples:
        sample_id = sample.get("id")
        if not sample_id or sample_id in ids:
            findings.append("missing or duplicate sample id")
        ids.add(sample_id)
        findings.extend(validate_sample(sample))
    if findings:
        print("FAIL golden example assertions")
        for finding in findings[:60]:
            print(finding)
        if len(findings) > 60:
            print(f"... {len(findings) - 60} more finding(s)")
        return 1
    suffix = " check" if args.check else ""
    print(f"golden example assertion{suffix} passed: {len(samples)} samples")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
