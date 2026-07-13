#!/usr/bin/env python3
"""Validate a structured launch decision card without external dependencies."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SAMPLES_PATH = ROOT / "docs/evals/launch-decision-card-samples.json"

TOP_LEVEL_REQUIRED = [
    "launch_brief",
    "decision_package",
    "control_summary",
    "executive_memo",
    "decision",
    "one_line_judgment",
    "route_verdict",
    "route_scorecard",
    "claim_evidence",
    "comment_pressure_test",
    "risk_ledger",
    "negative_radar",
    "readiness_gate",
    "route_switch_playbook",
    "next_72_hours",
    "next_7_days",
    "self_check",
]

DECISIONS = {"直接执行", "调整后执行", "暂停重做"}
STAGES = {"S0", "S1", "S2", "S3", "S4"}
SEVERITIES = {"低", "中", "高"}
ROUTE_IMPACTS = {"继续", "缩窄", "切换", "暂停"}
CONFIDENCE = {"高", "中", "低"}
RISK_PRIORITIES = {"P0", "P1", "P2", "P3"}
FACT_STATUSES = {"known", "inferred", "needs_verification"}
PACKAGE_STATUSES = {"可评审", "需补证据", "暂停评审"}
PACKAGE_SECTION_STATUSES = {"已完成", "待补", "阻断"}
PACKAGE_SECTION_IDS = {
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
}
ROUTE_ROLES = {"推荐", "备选", "弃用"}
ROUTE_SCORE_VERDICTS = {"押主线", "保留备选", "弃用"}
ROUTE_SCORE_FIELDS = [
    "evidence_score",
    "audience_fit_score",
    "competitor_defense_score",
    "risk_control_score",
    "resource_fit_score",
    "timing_score",
]


def decision_consistency_errors(data: dict) -> list[str]:
    errors: list[str] = []
    package = data.get("decision_package", {}) if isinstance(data.get("decision_package"), dict) else {}
    control = data.get("control_summary", {}) if isinstance(data.get("control_summary"), dict) else {}
    memo = data.get("executive_memo", {}) if isinstance(data.get("executive_memo"), dict) else {}
    route = data.get("route_verdict", {}) if isinstance(data.get("route_verdict"), dict) else {}
    claim = data.get("claim_evidence", {}) if isinstance(data.get("claim_evidence"), dict) else {}
    gate = data.get("readiness_gate", {}) if isinstance(data.get("readiness_gate"), dict) else {}
    self_check = data.get("self_check", {}) if isinstance(data.get("self_check"), dict) else {}
    switch_rows = data.get("route_switch_playbook") if isinstance(data.get("route_switch_playbook"), list) else []
    radar_rows = data.get("negative_radar") if isinstance(data.get("negative_radar"), list) else []
    ledger_rows = data.get("risk_ledger") if isinstance(data.get("risk_ledger"), list) else []
    score_rows = data.get("route_scorecard") if isinstance(data.get("route_scorecard"), list) else []
    recommended = route.get("recommended", {}) if isinstance(route.get("recommended"), dict) else {}
    backup = route.get("backup", {}) if isinstance(route.get("backup"), dict) else {}
    rejected = route.get("rejected", {}) if isinstance(route.get("rejected"), dict) else {}
    decision = data.get("decision")
    package_status = package.get("package_status")

    if control.get("verdict") in DECISIONS and data.get("decision") in DECISIONS and control.get("verdict") != data.get("decision"):
        errors.append("$.control_summary.verdict must match $.decision")
    if package_status == "暂停评审" and decision != "暂停重做":
        errors.append("$.decision_package.package_status 暂停评审 requires decision 暂停重做")
    if decision == "暂停重做" and package_status != "暂停评审":
        errors.append("$.decision_package.package_status must be 暂停评审 when decision is 暂停重做")
    if decision == "直接执行" and package_status != "可评审":
        errors.append("$.decision_package.package_status must be 可评审 when decision is 直接执行")
    if memo.get("verdict") in DECISIONS and data.get("decision") in DECISIONS and memo.get("verdict") != data.get("decision"):
        errors.append("$.executive_memo.verdict must match $.decision")
    if control.get("confidence") in CONFIDENCE and self_check.get("confidence") in CONFIDENCE and control.get("confidence") != self_check.get("confidence"):
        errors.append("$.control_summary.confidence must match $.self_check.confidence")
    if memo.get("confidence") in CONFIDENCE and control.get("confidence") in CONFIDENCE and memo.get("confidence") != control.get("confidence"):
        errors.append("$.executive_memo.confidence must match $.control_summary.confidence")
    if control.get("recommended_route") and recommended.get("route_name") and control.get("recommended_route") != recommended.get("route_name"):
        errors.append("$.control_summary.recommended_route must match $.route_verdict.recommended.route_name")
    if memo.get("recommended_route") and recommended.get("route_name") and memo.get("recommended_route") != recommended.get("route_name"):
        errors.append("$.executive_memo.recommended_route must match $.route_verdict.recommended.route_name")
    score_by_role = {
        row.get("route_role"): row
        for row in score_rows
        if isinstance(row, dict) and row.get("route_role") in ROUTE_ROLES
    }
    if set(score_by_role) == ROUTE_ROLES:
        expected_names = {
            "推荐": recommended.get("route_name"),
            "备选": backup.get("route_name"),
            "弃用": rejected.get("route_name"),
        }
        for role, expected_name in expected_names.items():
            if expected_name and score_by_role[role].get("route_name") != expected_name:
                errors.append(f"route_scorecard {role} route_name must match route_verdict")
        rec_score = score_by_role["推荐"].get("total_score")
        backup_score = score_by_role["备选"].get("total_score")
        rejected_score = score_by_role["弃用"].get("total_score")
        if all(isinstance(value, int) for value in [rec_score, backup_score, rejected_score]):
            if rec_score <= backup_score:
                errors.append("route_scorecard 推荐 total_score must be higher than 备选")
            if backup_score <= rejected_score:
                errors.append("route_scorecard 备选 total_score must be higher than 弃用")
        for role, expected_verdict in {"推荐": "押主线", "备选": "保留备选", "弃用": "弃用"}.items():
            if score_by_role[role].get("verdict") != expected_verdict:
                errors.append(f"route_scorecard {role} verdict must be {expected_verdict}")
        if decision == "直接执行":
            rec = score_by_role["推荐"]
            if rec.get("evidence_score", 0) < 3 or rec.get("risk_control_score", 0) < 3:
                errors.append("直接执行 requires recommended route evidence_score and risk_control_score >= 3")

    hard_blockers = gate.get("hard_blockers", []) if isinstance(gate.get("hard_blockers"), list) else []
    gaps = gate.get("gaps", []) if isinstance(gate.get("gaps"), list) else []
    to_verify = claim.get("to_verify", []) if isinstance(claim.get("to_verify"), list) else []
    inferred = claim.get("inferred", []) if isinstance(claim.get("inferred"), list) else []
    verified = claim.get("verified", []) if isinstance(claim.get("verified"), list) else []
    if (hard_blockers or self_check.get("hard_blockers", 0) > 0) and decision != "暂停重做":
        errors.append("hard blockers require decision 暂停重做")
    if hard_blockers and package_status != "暂停评审":
        errors.append("hard blockers require decision_package.package_status 暂停评审")
    if decision == "直接执行":
        if gaps or to_verify or inferred:
            errors.append("直接执行 requires no gaps, to_verify, or inferred claims")
        if package.get("open_decisions"):
            errors.append("直接执行 requires empty decision_package.open_decisions")
        if self_check.get("confidence") != "高":
            errors.append("直接执行 requires confidence 高")
        if self_check.get("high_risks", 0) > 0:
            errors.append("直接执行 requires zero high_risks")
    if package_status == "可评审" and (gaps or to_verify or inferred):
        errors.append("decision_package.package_status 可评审 requires no gaps, to_verify, or inferred claims")
    section_statuses = {
        row.get("section_id"): row.get("status")
        for row in package.get("included_sections", [])
        if isinstance(row, dict)
    }
    if package_status == "暂停评审" and "阻断" not in set(section_statuses.values()):
        errors.append("decision_package.package_status 暂停评审 requires at least one 阻断 section")
    if package_status == "需补证据" and not ({"待补", "阻断"} & set(section_statuses.values())):
        errors.append("decision_package.package_status 需补证据 requires at least one 待补 or 阻断 section")

    expected_counts = {
        "verified_facts": len(verified),
        "to_verify": len(to_verify),
        "inferred": len(inferred),
        "hard_blockers": len(hard_blockers),
    }
    for key, expected in expected_counts.items():
        value = self_check.get(key)
        if isinstance(value, int) and value != expected:
            errors.append(f"$.self_check.{key} must equal related list count")

    switch_actions = {row.get("route_action") for row in switch_rows if isinstance(row, dict)}
    radar_impacts = {row.get("route_impact") for row in radar_rows if isinstance(row, dict)}
    ledger_impacts = {row.get("route_impact") for row in ledger_rows if isinstance(row, dict)}
    for impact in radar_impacts:
        if impact in {"缩窄", "切换", "暂停"} and impact not in switch_actions:
            errors.append(f"route_switch_playbook must include action for radar impact {impact}")
    for impact in ledger_impacts:
        if impact in {"缩窄", "切换", "暂停"} and impact not in switch_actions:
            errors.append(f"route_switch_playbook must include action for risk-ledger impact {impact}")
    high_priority_rows = [
        row for row in ledger_rows
        if isinstance(row, dict) and row.get("priority") in {"P0", "P1"}
    ]
    if high_priority_rows and not radar_rows:
        errors.append("P0/P1 risk-ledger rows require negative_radar rows")
    if any(row.get("priority") == "P0" for row in high_priority_rows):
        p0_impacts = {row.get("route_impact") for row in high_priority_rows if row.get("priority") == "P0"}
        if "暂停" in p0_impacts and "暂停" not in switch_actions:
            errors.append("P0 暂停 risk requires a 暂停 route_switch_playbook action")
    if decision == "暂停重做" and "暂停" not in switch_actions:
        errors.append("暂停重做 requires a 暂停 route_switch_playbook action")
    return errors


def require_keys(data: dict, keys: list[str], path: str, errors: list[str]) -> None:
    for key in keys:
        if key not in data:
            errors.append(f"{path} missing {key}")


def require_non_empty_string(data: dict, key: str, path: str, errors: list[str]) -> None:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{path}.{key} must be a non-empty string")


def require_list(data: dict, key: str, path: str, errors: list[str], min_items: int = 0) -> None:
    value = data.get(key)
    if not isinstance(value, list) or len(value) < min_items:
        errors.append(f"{path}.{key} must be a list with at least {min_items} item(s)")


def validate_decision(data: dict) -> list[str]:
    errors: list[str] = []
    require_keys(data, TOP_LEVEL_REQUIRED, "$", errors)
    brief = data.get("launch_brief", {})
    if not isinstance(brief, dict):
        errors.append("$.launch_brief must be an object")
        brief = {}
    for key in [
        "product_category",
        "launch_window",
        "business_goal",
        "target_audience",
        "budget_level",
    ]:
        require_non_empty_string(brief, key, "$.launch_brief", errors)
    for key, min_items in {
        "evidence_available": 1,
        "competitors": 0,
        "planned_platforms": 1,
        "risk_constraints": 0,
        "missing_info": 0,
    }.items():
        require_list(brief, key, "$.launch_brief", errors, min_items)

    package = data.get("decision_package", {})
    if not isinstance(package, dict):
        errors.append("$.decision_package must be an object")
        package = {}
    for key in [
        "package_title",
        "package_version",
        "primary_audience",
        "decision_owner",
        "handoff_summary",
    ]:
        require_non_empty_string(package, key, "$.decision_package", errors)
    if package.get("package_status") not in PACKAGE_STATUSES:
        errors.append("$.decision_package.package_status has invalid value")
    require_list(package, "included_sections", "$.decision_package", errors, 8)
    require_list(package, "open_decisions", "$.decision_package", errors)
    seen_section_ids = set()
    for index, row in enumerate(package.get("included_sections", []) if isinstance(package.get("included_sections"), list) else []):
        path = f"$.decision_package.included_sections[{index}]"
        if not isinstance(row, dict):
            errors.append(f"{path} must be an object")
            continue
        section_id = row.get("section_id")
        if section_id not in PACKAGE_SECTION_IDS | {"self_check"}:
            errors.append(f"{path}.section_id has invalid value")
        elif section_id in seen_section_ids:
            errors.append(f"{path}.section_id must be unique")
        else:
            seen_section_ids.add(section_id)
        if row.get("status") not in PACKAGE_SECTION_STATUSES:
            errors.append(f"{path}.status has invalid value")
        for key in ["section_name", "source", "owner_role", "next_action"]:
            require_non_empty_string(row, key, path, errors)
    missing_section_ids = sorted(PACKAGE_SECTION_IDS - seen_section_ids)
    if package.get("included_sections") and missing_section_ids:
        errors.append("$.decision_package.included_sections missing section ids: " + ", ".join(missing_section_ids))

    control = data.get("control_summary", {})
    if not isinstance(control, dict):
        errors.append("$.control_summary must be an object")
        control = {}
    if control.get("verdict") not in DECISIONS:
        errors.append("$.control_summary.verdict has invalid value")
    if control.get("confidence") not in CONFIDENCE:
        errors.append("$.control_summary.confidence has invalid value")
    for key in [
        "recommended_route",
        "key_evidence_status",
        "top_risk",
        "hard_blocker_status",
        "next_72h_priority",
        "switch_trigger",
    ]:
        require_non_empty_string(control, key, "$.control_summary", errors)

    if data.get("decision") not in DECISIONS:
        errors.append("$.decision has invalid value")
    require_non_empty_string(data, "one_line_judgment", "$", errors)

    memo = data.get("executive_memo", {})
    if not isinstance(memo, dict):
        errors.append("$.executive_memo must be an object")
        memo = {}
    for key in [
        "decision_question",
        "recommended_route",
        "one_line_answer",
        "core_tradeoff",
        "top_risk",
        "no_go_condition",
        "next_owner_action",
    ]:
        require_non_empty_string(memo, key, "$.executive_memo", errors)
    if memo.get("verdict") not in DECISIONS:
        errors.append("$.executive_memo.verdict has invalid value")
    if memo.get("confidence") not in CONFIDENCE:
        errors.append("$.executive_memo.confidence has invalid value")
    require_list(memo, "evidence_basis", "$.executive_memo", errors, 1)
    if isinstance(memo.get("evidence_basis"), list) and len(memo["evidence_basis"]) > 3:
        errors.append("$.executive_memo.evidence_basis must contain at most 3 item(s)")

    route = data.get("route_verdict", {})
    if not isinstance(route, dict):
        errors.append("$.route_verdict must be an object")
        route = {}
    require_keys(route, ["recommended", "backup", "rejected"], "$.route_verdict", errors)
    recommended = route.get("recommended", {}) if isinstance(route.get("recommended"), dict) else {}
    backup = route.get("backup", {}) if isinstance(route.get("backup"), dict) else {}
    rejected = route.get("rejected", {}) if isinstance(route.get("rejected"), dict) else {}
    for key in ["route_name", "rationale"]:
        require_non_empty_string(recommended, key, "$.route_verdict.recommended", errors)
    require_list(recommended, "conditions", "$.route_verdict.recommended", errors, 1)
    for key in ["route_name", "switch_condition"]:
        require_non_empty_string(backup, key, "$.route_verdict.backup", errors)
    for key in ["route_name", "rejection_reason"]:
        require_non_empty_string(rejected, key, "$.route_verdict.rejected", errors)

    scorecard = data.get("route_scorecard")
    if not isinstance(scorecard, list) or len(scorecard) < 3:
        errors.append("$.route_scorecard must be a list with at least 3 item(s)")
        scorecard = []
    seen_roles = set()
    seen_names = set()
    for index, row in enumerate(scorecard):
        path = f"$.route_scorecard[{index}]"
        if not isinstance(row, dict):
            errors.append(f"{path} must be an object")
            continue
        for key in ["route_name", "rationale", "improvement_needed"]:
            require_non_empty_string(row, key, path, errors)
        role = row.get("route_role")
        if role not in ROUTE_ROLES:
            errors.append(f"{path}.route_role has invalid value")
        elif role in seen_roles:
            errors.append(f"{path}.route_role must be unique")
        else:
            seen_roles.add(role)
        route_name = row.get("route_name")
        if isinstance(route_name, str):
            if route_name in seen_names:
                errors.append(f"{path}.route_name must be unique")
            seen_names.add(route_name)
        if row.get("verdict") not in ROUTE_SCORE_VERDICTS:
            errors.append(f"{path}.verdict has invalid value")
        subtotal = 0
        for field in ROUTE_SCORE_FIELDS:
            value = row.get(field)
            if not isinstance(value, int) or value < 0 or value > 5:
                errors.append(f"{path}.{field} must be an integer from 0 to 5")
            else:
                subtotal += value
        total = row.get("total_score")
        if not isinstance(total, int) or total < 0 or total > 30:
            errors.append(f"{path}.total_score must be an integer from 0 to 30")
        elif subtotal != total:
            errors.append(f"{path}.total_score must equal the sum of score fields")
    if scorecard and seen_roles != ROUTE_ROLES:
        errors.append("$.route_scorecard must include 推荐, 备选, and 弃用 rows")

    claim = data.get("claim_evidence", {})
    if not isinstance(claim, dict):
        errors.append("$.claim_evidence must be an object")
        claim = {}
    require_non_empty_string(claim, "core_claim", "$.claim_evidence", errors)
    require_list(claim, "evidence_pillars", "$.claim_evidence", errors, 3)
    for key in ["verified", "to_verify", "inferred"]:
        require_list(claim, key, "$.claim_evidence", errors)

    pressure = data.get("comment_pressure_test", {})
    if not isinstance(pressure, dict):
        errors.append("$.comment_pressure_test must be an object")
        pressure = {}
    for key in ["parameter_driven", "ordinary_user", "deconstruction"]:
        require_non_empty_string(pressure, key, "$.comment_pressure_test", errors)
    require_list(pressure, "evidence_to_prepare", "$.comment_pressure_test", errors, 1)

    ledger = data.get("risk_ledger")
    if not isinstance(ledger, list) or not ledger:
        errors.append("$.risk_ledger must be a non-empty list")
        ledger = []
    ledger_ids = set()
    for index, item in enumerate(ledger):
        path = f"$.risk_ledger[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{path} must be an object")
            continue
        risk_id = item.get("risk_id")
        if not isinstance(risk_id, str) or not risk_id.startswith("R") or len(risk_id) != 4 or not risk_id[1:].isdigit():
            errors.append(f"{path}.risk_id has invalid value")
        elif risk_id in ledger_ids:
            errors.append(f"{path}.risk_id must be unique")
        else:
            ledger_ids.add(risk_id)
        for key in [
            "evidence_anchor",
            "trigger",
            "actor",
            "compressed_narrative",
            "platform_path",
            "business_impact",
            "early_signal",
            "recommended_action",
            "side_effect",
            "disconfirming_evidence",
        ]:
            require_non_empty_string(item, key, path, errors)
        if item.get("priority") not in RISK_PRIORITIES:
            errors.append(f"{path}.priority has invalid value")
        if item.get("fact_status") not in FACT_STATUSES:
            errors.append(f"{path}.fact_status has invalid value")
        if item.get("route_impact") not in ROUTE_IMPACTS:
            errors.append(f"{path}.route_impact has invalid value")
        if item.get("confidence") not in CONFIDENCE:
            errors.append(f"{path}.confidence has invalid value")

    radar = data.get("negative_radar")
    if not isinstance(radar, list) or not radar:
        errors.append("$.negative_radar must be a non-empty list")
        radar = []
    for index, item in enumerate(radar):
        path = f"$.negative_radar[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{path} must be an object")
            continue
        for key in ["signal", "trigger_condition", "owner_role"]:
            require_non_empty_string(item, key, path, errors)
        if item.get("stage") not in STAGES:
            errors.append(f"{path}.stage has invalid value")
        if item.get("severity") not in SEVERITIES:
            errors.append(f"{path}.severity has invalid value")
        if item.get("route_impact") not in ROUTE_IMPACTS:
            errors.append(f"{path}.route_impact has invalid value")

    gate = data.get("readiness_gate", {})
    if not isinstance(gate, dict):
        errors.append("$.readiness_gate must be an object")
        gate = {}
    for key in ["hard_blockers", "gaps"]:
        require_list(gate, key, "$.readiness_gate", errors)
    require_list(gate, "owner_roles", "$.readiness_gate", errors, 1)
    require_non_empty_string(gate, "completion_deadline", "$.readiness_gate", errors)

    switch_rows = data.get("route_switch_playbook")
    if not isinstance(switch_rows, list) or not switch_rows:
        errors.append("$.route_switch_playbook must be a non-empty list")
        switch_rows = []
    for index, row in enumerate(switch_rows):
        path = f"$.route_switch_playbook[{index}]"
        if not isinstance(row, dict):
            errors.append(f"{path} must be an object")
            continue
        for field in ["trigger", "action", "owner_role", "deadline"]:
            require_non_empty_string(row, field, path, errors)
        if row.get("signal_stage") not in STAGES:
            errors.append(f"{path}.signal_stage has invalid value")
        if row.get("route_action") not in ROUTE_IMPACTS:
            errors.append(f"{path}.route_action has invalid value")
        require_list(row, "evidence_to_check", path, errors, 1)

    for key, required in {
        "next_72_hours": ["time", "action", "owner_role", "deliverable", "completion_standard"],
        "next_7_days": ["metric", "signal", "threshold", "action"],
    }.items():
        rows = data.get(key)
        if not isinstance(rows, list) or not rows:
            errors.append(f"$.{key} must be a non-empty list")
            continue
        for index, row in enumerate(rows):
            path = f"$.{key}[{index}]"
            if not isinstance(row, dict):
                errors.append(f"{path} must be an object")
                continue
            for field in required:
                require_non_empty_string(row, field, path, errors)

    self_check = data.get("self_check", {})
    if not isinstance(self_check, dict):
        errors.append("$.self_check must be an object")
        self_check = {}
    for key in ["verified_facts", "to_verify", "inferred", "high_risks", "hard_blockers"]:
        value = self_check.get(key)
        if not isinstance(value, int) or value < 0:
            errors.append(f"$.self_check.{key} must be a non-negative integer")
    if self_check.get("confidence") not in CONFIDENCE:
        errors.append("$.self_check.confidence has invalid value")
    if not errors:
        errors.extend(decision_consistency_errors(data))
    return errors


def check_samples() -> int:
    data = json.loads(SAMPLES_PATH.read_text(encoding="utf-8"))
    failures: list[str] = []
    for item in data.get("valid", []):
        errors = validate_decision(item.get("payload", {}))
        if errors:
            failures.append(f"{item.get('id')}: expected valid, got {errors[:3]}")
    for item in data.get("invalid", []):
        errors = validate_decision(item.get("payload", {}))
        if not errors:
            failures.append(f"{item.get('id')}: expected invalid, got valid")
    if failures:
        for failure in failures:
            print(failure)
        return 1
    print(
        "decision card sample check passed: "
        f"{len(data.get('valid', []))} valid, {len(data.get('invalid', []))} invalid"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a structured launch decision card.")
    parser.add_argument("--check", action="store_true", help="validate bundled decision-card samples")
    parser.add_argument("--input", help="path to a JSON decision card")
    args = parser.parse_args()

    if args.check or not args.input:
        result = check_samples()
        if result != 0:
            return result
    if args.input:
        payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
        errors = validate_decision(payload)
        if errors:
            for error in errors:
                print(error)
            return 1
        print("decision card is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
