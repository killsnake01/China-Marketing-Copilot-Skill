#!/usr/bin/env python3
"""Validate the old-user interaction compatibility contract."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PATH = ROOT / "docs/evals/legacy-compatibility-samples.json"
VALID_MODES = {"快速版", "标准版", "深度版", "不适用"}
REQUIRED_ROUTES = {
    "docs/routes/launch-decision.md",
    "docs/routes/messaging-review.md",
    "docs/routes/creative-campaign.md",
    "docs/routes/channel-kol.md",
    "docs/routes/competitor-intelligence.md",
    "docs/routes/risk-review.md",
    "docs/routes/data-import.md",
}


def validate_cases(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if data.get("status") != "compatibility_contract_ready_no_live_results":
        errors.append("status must separate the static contract from live results")
    cases = data.get("cases")
    if not isinstance(cases, list) or len(cases) < 12:
        return errors + ["compatibility contract must contain at least 12 cases"]
    seen: set[str] = set()
    positive_routes: set[str] = set()
    negative_count = 0
    quick_count = 0
    scoped_count = 0
    for case in cases:
        case_id = case.get("id")
        if not isinstance(case_id, str) or not re.fullmatch(r"LC\d{3}", case_id):
            errors.append(f"invalid case id: {case_id!r}")
            continue
        if case_id in seen:
            errors.append(f"duplicate case id: {case_id}")
        seen.add(case_id)
        if not isinstance(case.get("prompt"), str) or len(case["prompt"].strip()) < 8:
            errors.append(f"{case_id}: prompt is missing or too short")
        should_trigger = case.get("should_trigger")
        if not isinstance(should_trigger, bool):
            errors.append(f"{case_id}: should_trigger must be boolean")
            continue
        route = case.get("expected_route")
        mode = case.get("expected_mode")
        if mode not in VALID_MODES:
            errors.append(f"{case_id}: invalid expected_mode {mode!r}")
        if mode == "快速版":
            quick_count += 1
        if should_trigger:
            if route not in REQUIRED_ROUTES or not (ROOT / route).is_file():
                errors.append(f"{case_id}: invalid route {route!r}")
            else:
                positive_routes.add(route)
            if not case.get("required_output_terms"):
                errors.append(f"{case_id}: required_output_terms must not be empty")
            forbidden = case.get("forbidden_default_modules")
            if not isinstance(forbidden, list) or not forbidden:
                errors.append(f"{case_id}: forbidden_default_modules must not be empty")
            else:
                scoped_count += 1
        else:
            negative_count += 1
            if route is not None or mode != "不适用":
                errors.append(f"{case_id}: non-trigger case must use null route and 不适用 mode")
    if REQUIRED_ROUTES - positive_routes:
        errors.append("route coverage missing: " + ", ".join(sorted(REQUIRED_ROUTES - positive_routes)))
    if negative_count < 1:
        errors.append("contract must include a non-trigger purchase case")
    if quick_count < 4:
        errors.append("contract must preserve at least four quick old-user tasks")
    if scoped_count < 10:
        errors.append("contract must constrain advanced modules for old-user tasks")
    return errors


def validate_policy_text() -> list[str]:
    policy = (ROOT / "docs/templates/output-mode-policy.md").read_text(encoding="utf-8")
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    router = (ROOT / "docs/agent-router.md").read_text(encoding="utf-8")
    required_policy_terms = [
        "模式属于智能体内部选择",
        "输入材料很长不会自动进入深度版",
        "只交付该任务需要的内容",
        "默认不显示“模式：快速版/标准版/深度版”",
        "材料长度本身不决定模式",
    ]
    required_skill_terms = ["## 旧用法兼容", "信息屋", "上市打法", "只改这句"]
    required_router_terms = ["## 旧术语映射", "个人购买咨询", "营销竞品洞察"]
    errors = [f"output mode policy missing: {term}" for term in required_policy_terms if term not in policy]
    errors.extend(f"SKILL.md missing: {term}" for term in required_skill_terms if term not in skill)
    errors.extend(f"agent router missing: {term}" for term in required_router_terms if term not in router)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate old-user interaction compatibility")
    parser.add_argument("--eval-file", default=str(DEFAULT_PATH))
    args = parser.parse_args()
    data = json.loads(Path(args.eval_file).read_text(encoding="utf-8"))
    errors = validate_cases(data) + validate_policy_text()
    if errors:
        print("legacy compatibility contract failed")
        for error in errors:
            print(error)
        return 1
    print(
        "legacy compatibility contract passed: "
        f"{len(data['cases'])} cases, {len(REQUIRED_ROUTES)} routes, live behavior remains unclaimed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
