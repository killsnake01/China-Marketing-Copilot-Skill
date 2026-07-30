#!/usr/bin/env python3
"""Validate audience-visible and backstage material separation."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PATH = ROOT / "docs/evals/audience-layering-samples.json"
VALID_ARTIFACT_TYPES = {"frontstage_proposal", "internal_risk_audit"}


def load_contract(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def split_layers(text: str, frontstage_marker: str, backstage_markers: list[str]) -> tuple[str, str]:
    frontstage_start = text.find(frontstage_marker)
    if frontstage_start < 0:
        return "", ""
    content_start = frontstage_start + len(frontstage_marker)
    backstage_hits = [(text.find(marker, content_start), marker) for marker in backstage_markers]
    backstage_hits = [(index, marker) for index, marker in backstage_hits if index >= 0]
    if not backstage_hits:
        return text[content_start:].strip(), ""
    backstage_start, marker = min(backstage_hits, key=lambda item: item[0])
    visible = text[content_start:backstage_start].strip()
    backstage = text[backstage_start + len(marker):].strip()
    return visible, backstage


def evaluate_frontstage(
    text: str,
    contract: dict[str, Any],
    required_visible_terms: list[str],
    required_backstage_terms: list[str],
) -> list[str]:
    errors: list[str] = []
    visible, backstage = split_layers(
        text,
        contract["frontstage_marker"],
        contract["backstage_markers"],
    )
    if not visible:
        errors.append("missing or empty frontstage layer")
        return errors
    if not backstage:
        errors.append("missing or empty backstage layer")

    leak_terms = contract["frontstage_leak_terms"]
    leaked = sorted({term for term in leak_terms if term in visible})
    if leaked:
        errors.append("frontstage leaks internal language: " + ", ".join(leaked))

    command_patterns = [
        r"控制在\s*\d+(?:\s*[-–]\s*\d+)?\s*秒",
        r"镜头组合\s*[:：]",
        r"(?:必须|禁止)\s*(?:补齐|使用|出现|混用|拍摄|发布)",
    ]
    for pattern in command_patterns:
        if re.search(pattern, visible):
            errors.append(f"frontstage contains production or audit command: {pattern}")

    missing_visible = [term for term in required_visible_terms if term not in visible]
    if missing_visible:
        errors.append("frontstage missing required terms: " + ", ".join(missing_visible))
    missing_backstage = [term for term in required_backstage_terms if term not in backstage]
    if missing_backstage:
        errors.append("backstage missing required terms: " + ", ".join(missing_backstage))

    for heading in re.findall(r"^#{2,6}\s+(.+)$", visible, flags=re.M):
        heading_leaks = [term for term in leak_terms if term in heading]
        if heading_leaks:
            errors.append("frontstage heading uses internal label: " + heading)
    return errors


def evaluate_internal_audit(text: str, required_output_terms: list[str]) -> list[str]:
    missing = [term for term in required_output_terms if term not in text]
    if missing:
        return ["internal audit missing required terms: " + ", ".join(missing)]
    return []


def evaluate_case(case: dict[str, Any], contract: dict[str, Any]) -> list[str]:
    artifact_type = case.get("artifact_type")
    text = case.get("output", "")
    if artifact_type == "frontstage_proposal":
        return evaluate_frontstage(
            text,
            contract,
            case.get("required_visible_terms", []),
            case.get("required_backstage_terms", []),
        )
    if artifact_type == "internal_risk_audit":
        return evaluate_internal_audit(text, case.get("required_output_terms", []))
    return [f"unsupported artifact_type: {artifact_type!r}"]


def validate_contract(contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if contract.get("status") != "static_contract_ready_no_live_results":
        errors.append("status must separate static contract from live behavior")
    if not contract.get("frontstage_marker") or not contract.get("backstage_markers"):
        errors.append("layer markers are required")
    leak_terms = contract.get("frontstage_leak_terms")
    if not isinstance(leak_terms, list) or len(leak_terms) < 12:
        errors.append("frontstage leak vocabulary must include at least 12 terms")

    samples = contract.get("samples")
    if not isinstance(samples, list) or len(samples) < 8:
        return errors + ["audience layering contract must include at least 8 samples"]
    seen: set[str] = set()
    positive = 0
    negative = 0
    internal_audits = 0
    for case in samples:
        case_id = case.get("id")
        if not isinstance(case_id, str) or not re.fullmatch(r"AL\d{3}", case_id):
            errors.append(f"invalid case id: {case_id!r}")
            continue
        if case_id in seen:
            errors.append(f"duplicate case id: {case_id}")
        seen.add(case_id)
        if case.get("artifact_type") not in VALID_ARTIFACT_TYPES:
            errors.append(f"{case_id}: invalid artifact_type")
        if not isinstance(case.get("output"), str) or len(case["output"].strip()) < 30:
            errors.append(f"{case_id}: output is missing or too short")
        expected_pass = case.get("expected_pass")
        if not isinstance(expected_pass, bool):
            errors.append(f"{case_id}: expected_pass must be boolean")
            continue
        if expected_pass:
            positive += 1
        else:
            negative += 1
        if case.get("artifact_type") == "internal_risk_audit":
            internal_audits += 1
        case_errors = evaluate_case(case, contract)
        actual_pass = not case_errors
        if actual_pass != expected_pass:
            errors.append(
                f"{case_id}: expected_pass={expected_pass}, actual_pass={actual_pass}; "
                + "; ".join(case_errors)
            )
    if positive < 4 or negative < 3:
        errors.append("contract needs at least four positive and three negative cases")
    if internal_audits < 1:
        errors.append("contract must preserve an internal risk audit case")
    return errors


def validate_policy_files() -> list[str]:
    requirements = {
        "docs/templates/audience-layering.md": [
            "最终受众",
            "前台可见层",
            "演讲者备注",
            "内部附录",
            "多技能协作优先级",
            "正式物料创作至少交付前台可见层和一个后台层",
            "后台审核不能只停留在智能体内部推理",
        ],
        "docs/templates/creative-output.md": [
            "前台创意成品",
            "观众会看到什么",
            "内部创意审核",
        ],
        "docs/templates/risk-assessment.md": [
            "默认呈现位置",
            "完整风险报告作为后台产物",
        ],
        "docs/templates/execution-readiness-gate.md": [
            "适用范围与呈现位置",
            "六道门在后台运行",
        ],
        "docs/templates/quality-check-tools.md": [
            "正式物料内部语言泄露扫描",
            "触发重写",
        ],
        "docs/agent-router.md": [
            "最终受众表达要求优先于内部审核模板的可见呈现要求",
            "不能接管前台结构",
        ],
    }
    errors: list[str] = []
    for relative_path, terms in requirements.items():
        path = ROOT / relative_path
        if not path.is_file():
            errors.append(f"missing policy file: {relative_path}")
            continue
        text = path.read_text(encoding="utf-8")
        for term in terms:
            if term not in text:
                errors.append(f"{relative_path} missing policy term: {term}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate formal-material audience layering")
    parser.add_argument("--eval-file", default=str(DEFAULT_PATH))
    parser.add_argument("--check", action="store_true", help="validate the static regression contract")
    parser.add_argument("--input", help="evaluate an actual markdown artifact")
    parser.add_argument(
        "--artifact-type",
        choices=sorted(VALID_ARTIFACT_TYPES),
        default="frontstage_proposal",
    )
    args = parser.parse_args()

    contract = load_contract(Path(args.eval_file))
    if args.input:
        text = Path(args.input).read_text(encoding="utf-8")
        if args.artifact_type == "frontstage_proposal":
            errors = evaluate_frontstage(text, contract, [], [])
        else:
            errors = evaluate_internal_audit(
                text,
                ["总体判定", "依据", "建议动作"],
            )
    else:
        errors = validate_contract(contract) + validate_policy_files()

    if errors:
        print("audience layering check failed")
        for error in errors:
            print(error)
        return 1
    if args.input:
        print(f"audience layering artifact passed: {args.artifact_type}")
        return 0
    print(
        "audience layering check passed: "
        f"{len(contract['samples'])} static cases, live behavior remains unclaimed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
