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
VALID_TASK_SCOPES = {"daily", "standard", "explicit_full"}


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


def layered_snippet(snippet: str) -> tuple[str, str]:
    frontstage_marker = "## 前台可见层"
    backstage_markers = ["## 演讲者备注", "## 内部附录", "## 后台审核层"]
    frontstage_index = snippet.find(frontstage_marker)
    if frontstage_index < 0:
        return "", ""
    content_start = frontstage_index + len(frontstage_marker)
    backstage_indexes = [
        snippet.find(marker, content_start)
        for marker in backstage_markers
        if snippet.find(marker, content_start) >= 0
    ]
    if not backstage_indexes:
        return snippet[content_start:], ""
    backstage_index = min(backstage_indexes)
    return snippet[content_start:backstage_index], snippet[backstage_index:]


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
    task_scope = sample.get("task_scope")
    if task_scope not in VALID_TASK_SCOPES:
        findings.append(f"{sample_id}: invalid task_scope {task_scope!r}")
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
    for term in sample.get("forbidden_advanced_sections", []):
        if term in snippet:
            findings.append(f"{sample_id}: scoped output leaked advanced section {term}")
    layered_assertions = any(
        sample.get(key)
        for key in ["visible_required_terms", "visible_forbidden_terms", "backstage_required_terms"]
    )
    if layered_assertions:
        visible, backstage = layered_snippet(snippet)
        if not visible:
            findings.append(f"{sample_id}: layered sample missing frontstage content")
        if not backstage:
            findings.append(f"{sample_id}: layered sample missing backstage content")
        for term in sample.get("visible_required_terms", []):
            if term not in visible:
                findings.append(f"{sample_id}: visible layer missing term {term}")
        for term in sample.get("visible_forbidden_terms", []):
            if term in visible:
                findings.append(f"{sample_id}: visible layer contains internal term {term}")
        for term in sample.get("backstage_required_terms", []):
            if term not in backstage:
                findings.append(f"{sample_id}: backstage layer missing term {term}")
    max_output_chars = sample.get("max_output_chars")
    if not isinstance(max_output_chars, int) or max_output_chars < 200:
        findings.append(f"{sample_id}: invalid max_output_chars")
    elif len(snippet) > max_output_chars:
        findings.append(f"{sample_id}: output length {len(snippet)} exceeds {max_output_chars}")
    direct_terms = sample.get("direct_answer_terms", [])
    direct_window = sample.get("direct_answer_within_chars")
    if not isinstance(direct_terms, list) or not direct_terms:
        findings.append(f"{sample_id}: direct_answer_terms must be a non-empty list")
    elif not isinstance(direct_window, int) or direct_window < 50:
        findings.append(f"{sample_id}: invalid direct_answer_within_chars")
    elif not any(term in snippet[:direct_window] for term in direct_terms):
        findings.append(f"{sample_id}: direct answer missing from first {direct_window} characters")
    if task_scope != "explicit_full" and len(sample.get("forbidden_advanced_sections", [])) < 3:
        findings.append(f"{sample_id}: scoped sample needs at least three advanced-section guards")
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
    scope_counts = {scope: 0 for scope in VALID_TASK_SCOPES}
    for sample in samples:
        sample_id = sample.get("id")
        if not sample_id or sample_id in ids:
            findings.append("missing or duplicate sample id")
        ids.add(sample_id)
        if sample.get("task_scope") in scope_counts:
            scope_counts[sample["task_scope"]] += 1
        findings.extend(validate_sample(sample))
    if scope_counts["explicit_full"] < 1:
        findings.append("golden examples need at least one explicit_full sample")
    if scope_counts["daily"] + scope_counts["standard"] < 3:
        findings.append("golden examples need at least three scoped daily or standard samples")
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
