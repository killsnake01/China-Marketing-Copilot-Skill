#!/usr/bin/env python3
"""Validate blind benchmark cases and score captured cross-agent runs."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from build_publish_package import runtime_fingerprint, version


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BENCHMARK = ROOT / "docs/evals/cross-agent-benchmark.json"
VALID_MODES = {"快速版", "标准版", "深度版", "不适用"}
VALID_PACKAGE_PROFILES = {"codex", "clawhub", "skillhub", "hermes-personal"}
VALID_ROUTES = {
    f"docs/routes/{path.name}"
    for path in (ROOT / "docs/routes").glob("*.md")
    if path.name != "platform-publish.md"
}
DEFAULT_FRONTSTAGE_MARKERS = ["## 前台可见层", "## 可见页面", "# 前台可见层", "# 可见页面"]
DEFAULT_BACKSTAGE_MARKERS = ["## 演讲者备注", "## 内部附录", "## 后台审核层"]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def split_audience_layers(output: str, case: dict[str, Any]) -> tuple[str, str]:
    frontstage_markers = case.get("frontstage_markers", DEFAULT_FRONTSTAGE_MARKERS)
    backstage_markers = case.get("backstage_markers", DEFAULT_BACKSTAGE_MARKERS)
    frontstage_hits = [(output.find(marker), marker) for marker in frontstage_markers]
    frontstage_hits = [(index, marker) for index, marker in frontstage_hits if index >= 0]
    if not frontstage_hits:
        return "", ""
    frontstage_start, frontstage_marker = min(frontstage_hits, key=lambda item: item[0])
    content_start = frontstage_start + len(frontstage_marker)
    backstage_hits = [(output.find(marker, content_start), marker) for marker in backstage_markers]
    backstage_hits = [(index, marker) for index, marker in backstage_hits if index >= 0]
    if not backstage_hits:
        return output[content_start:], ""
    backstage_start, _marker = min(backstage_hits, key=lambda item: item[0])
    return output[content_start:backstage_start], output[backstage_start:]


def validate_benchmark(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if data.get("status") != "benchmark_ready_no_live_results":
        errors.append("status must state that live results are not bundled")
    target_agents = data.get("target_agents")
    if not isinstance(target_agents, list) or len(set(target_agents)) < 4:
        errors.append("target_agents must include at least four unique agents")
    package_profiles = data.get("agent_package_profiles")
    if not isinstance(package_profiles, dict) or set(package_profiles) != set(target_agents or []):
        errors.append("agent_package_profiles must map every target agent")
    elif not set(package_profiles.values()).issubset(VALID_PACKAGE_PROFILES):
        errors.append("agent_package_profiles contains an unsupported package profile")
    run_contract = data.get("run_contract", {})
    required_fields = run_contract.get("required_fields")
    release_required_fields = run_contract.get("release_required_fields")
    if not isinstance(required_fields, list) or "output" not in required_fields:
        errors.append("run_contract.required_fields must include output")
    expected_release_fields = {
        "captured_at",
        "skill_version",
        "runtime_package_fingerprint_sha256",
    }
    if not isinstance(release_required_fields, list) or not expected_release_fields.issubset(release_required_fields):
        errors.append("run_contract.release_required_fields is incomplete")

    cases = data.get("cases")
    if not isinstance(cases, list) or len(cases) < 16:
        errors.append("benchmark must include at least 16 cases")
        return errors

    seen: set[str] = set()
    positive_routes: set[str] = set()
    negative_count = 0
    scoped_count = 0
    direct_count = 0
    for case in cases:
        case_id = case.get("id")
        if not isinstance(case_id, str) or not re.fullmatch(r"XA\d{3}", case_id):
            errors.append(f"invalid case id: {case_id!r}")
            continue
        if case_id in seen:
            errors.append(f"duplicate case id: {case_id}")
        seen.add(case_id)
        if not isinstance(case.get("prompt"), str) or len(case["prompt"].strip()) < 8:
            errors.append(f"{case_id}: prompt is missing or too short")
        expected_trigger = case.get("expected_trigger")
        if not isinstance(expected_trigger, bool):
            errors.append(f"{case_id}: expected_trigger must be boolean")
        route = case.get("expected_route")
        if expected_trigger:
            if route not in VALID_ROUTES:
                errors.append(f"{case_id}: invalid expected_route {route!r}")
            else:
                positive_routes.add(route)
        else:
            negative_count += 1
            if route is not None:
                errors.append(f"{case_id}: non-trigger case must use null route")
        modes = case.get("accepted_modes")
        if not isinstance(modes, list) or not modes or not set(modes).issubset(VALID_MODES):
            errors.append(f"{case_id}: invalid accepted_modes")
        if not isinstance(case.get("required_all"), list):
            errors.append(f"{case_id}: required_all must be a list")
        groups = case.get("required_any_groups")
        if not isinstance(groups, list) or any(not isinstance(group, list) or not group for group in groups):
            errors.append(f"{case_id}: required_any_groups must contain non-empty lists")
        patterns = case.get("forbidden_regex")
        if not isinstance(patterns, list):
            errors.append(f"{case_id}: forbidden_regex must be a list")
        else:
            for pattern in patterns:
                try:
                    re.compile(pattern)
                except re.error as exc:
                    errors.append(f"{case_id}: invalid forbidden regex {pattern!r}: {exc}")
        for field in ["visible_forbidden_regex"]:
            layer_patterns = case.get(field, [])
            if not isinstance(layer_patterns, list):
                errors.append(f"{case_id}: {field} must be a list")
                continue
            for pattern in layer_patterns:
                try:
                    re.compile(pattern)
                except re.error as exc:
                    errors.append(f"{case_id}: invalid {field} pattern {pattern!r}: {exc}")
        for field in [
            "visible_required_all",
            "backstage_required_all",
            "frontstage_markers",
            "backstage_markers",
        ]:
            values = case.get(field, [])
            if not isinstance(values, list) or any(not isinstance(item, str) for item in values):
                errors.append(f"{case_id}: {field} must be a string list")
        backstage_groups = case.get("backstage_required_any_groups", [])
        if not isinstance(backstage_groups, list) or any(
            not isinstance(group, list) or not group for group in backstage_groups
        ):
            errors.append(f"{case_id}: backstage_required_any_groups must contain non-empty lists")
        if case.get("visible_required_all") and (
            not case.get("frontstage_markers") or not case.get("backstage_markers")
        ):
            errors.append(f"{case_id}: layered case must define frontstage and backstage markers")
        forbidden_sections = case.get("forbidden_sections", [])
        if not isinstance(forbidden_sections, list) or any(not isinstance(item, str) for item in forbidden_sections):
            errors.append(f"{case_id}: forbidden_sections must be a string list")
        elif forbidden_sections:
            scoped_count += 1
        direct_terms = case.get("direct_answer_terms", [])
        direct_window = case.get("direct_answer_within_chars")
        if not isinstance(direct_terms, list) or any(not isinstance(item, str) for item in direct_terms):
            errors.append(f"{case_id}: direct_answer_terms must be a string list")
        elif direct_terms:
            direct_count += 1
            if not isinstance(direct_window, int) or direct_window < 50:
                errors.append(f"{case_id}: direct_answer_within_chars must be at least 50")
        if not isinstance(case.get("max_output_chars"), int) or case["max_output_chars"] < 100:
            errors.append(f"{case_id}: max_output_chars must be at least 100")
        if not isinstance(case.get("require_self_check"), bool):
            errors.append(f"{case_id}: require_self_check must be boolean")

    expected_routes = {
        "docs/routes/launch-decision.md",
        "docs/routes/messaging-review.md",
        "docs/routes/creative-campaign.md",
        "docs/routes/channel-kol.md",
        "docs/routes/competitor-intelligence.md",
        "docs/routes/risk-review.md",
        "docs/routes/post-launch-war-room.md",
        "docs/routes/data-import.md",
        "docs/routes/material-audit.md",
        "docs/routes/output-quality.md",
    }
    missing_routes = sorted(expected_routes - positive_routes)
    if missing_routes:
        errors.append("benchmark route coverage missing: " + ", ".join(missing_routes))
    if negative_count < 3:
        errors.append("benchmark must include at least three non-trigger cases")
    if scoped_count < 6:
        errors.append("benchmark needs at least six scoped-output cases")
    if direct_count < 4:
        errors.append("benchmark needs at least four direct-answer checks")
    return errors


def read_runs(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
        if not isinstance(item, dict):
            raise ValueError(f"{path}:{line_number}: each line must contain an object")
        item["_line"] = line_number
        records.append(item)
    return records


def score_run(run: dict[str, Any], case: dict[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    output = run.get("output")
    if not isinstance(output, str):
        failures.append("format:output")
        output = ""
    if run.get("triggered") is not case["expected_trigger"]:
        failures.append("trigger:mismatch")
    if run.get("selected_route") != case["expected_route"]:
        failures.append("route:mismatch")
    if run.get("selected_mode") not in case["accepted_modes"]:
        failures.append("mode:mismatch")
    missing_all = [term for term in case["required_all"] if term not in output]
    if missing_all:
        failures.append("evidence:required_all=" + ",".join(missing_all))
    for group in case["required_any_groups"]:
        if not any(term in output for term in group):
            failures.append("evidence:required_any=" + "|".join(group))
    matched_forbidden = [pattern for pattern in case["forbidden_regex"] if re.search(pattern, output)]
    if matched_forbidden:
        failures.append("safety:forbidden_regex=" + ",".join(matched_forbidden))
    leaked_sections = [term for term in case.get("forbidden_sections", []) if term in output]
    if leaked_sections:
        failures.append("scope:advanced_section=" + ",".join(leaked_sections))
    if case.get("visible_required_all") or case.get("visible_forbidden_regex"):
        visible, backstage = split_audience_layers(output, case)
        if not visible:
            failures.append("layering:missing_frontstage")
        if not backstage:
            failures.append("layering:missing_backstage")
        missing_visible = [term for term in case.get("visible_required_all", []) if term not in visible]
        if missing_visible:
            failures.append("layering:visible_required=" + ",".join(missing_visible))
        visible_forbidden = [
            pattern
            for pattern in case.get("visible_forbidden_regex", [])
            if re.search(pattern, visible)
        ]
        if visible_forbidden:
            failures.append("layering:visible_forbidden=" + ",".join(visible_forbidden))
        missing_backstage = [term for term in case.get("backstage_required_all", []) if term not in backstage]
        if missing_backstage:
            failures.append("layering:backstage_required=" + ",".join(missing_backstage))
        for group in case.get("backstage_required_any_groups", []):
            if not any(term in backstage for term in group):
                failures.append("layering:backstage_required_any=" + "|".join(group))
    direct_terms = case.get("direct_answer_terms", [])
    if direct_terms:
        window = case["direct_answer_within_chars"]
        if not any(term in output[:window] for term in direct_terms):
            failures.append(f"directness:answer_window={window}")
    if len(output) > case["max_output_chars"]:
        failures.append(f"format:length={len(output)}>{case['max_output_chars']}")
    if case["require_self_check"] and "自检:" not in output:
        failures.append("format:self_check")
    return not failures, failures


def package_fingerprints(data: dict[str, Any]) -> dict[str, str]:
    profiles = set(data["agent_package_profiles"].values())
    return {profile: runtime_fingerprint(profile) for profile in sorted(profiles)}


def validate_release_metadata(
    records: list[dict[str, Any]],
    data: dict[str, Any],
    fingerprints: dict[str, str],
) -> list[str]:
    errors: list[str] = []
    expected_version = version()
    for run in records:
        line = run.get("_line")
        captured_at = run.get("captured_at")
        if not isinstance(captured_at, str):
            errors.append(f"line {line}: missing captured_at")
        else:
            normalized = captured_at[:-1] + "+00:00" if captured_at.endswith("Z") else captured_at
            try:
                parsed = datetime.fromisoformat(normalized)
            except ValueError:
                errors.append(f"line {line}: invalid captured_at")
            else:
                if parsed.tzinfo is None:
                    errors.append(f"line {line}: captured_at requires a timezone")
        if run.get("skill_version") != expected_version:
            errors.append(f"line {line}: skill_version does not match {expected_version}")
        profile = data["agent_package_profiles"].get(run.get("agent"))
        expected_fingerprint = fingerprints.get(profile, "")
        if run.get("runtime_package_fingerprint_sha256") != expected_fingerprint:
            errors.append(f"line {line}: runtime package fingerprint mismatch for {profile}")
    return errors


def write_summary(path: Path, summary: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run_scorer_self_test(data: dict[str, Any]) -> int:
    fingerprints = package_fingerprints(data)
    records: list[dict[str, Any]] = []
    for agent in data["target_agents"]:
        profile = data["agent_package_profiles"][agent]
        for case in data["cases"]:
            output_terms = list(case.get("direct_answer_terms", [])[:1])
            output_terms.extend(case["required_all"])
            output_terms.extend(group[0] for group in case["required_any_groups"])
            if case.get("visible_required_all"):
                output_terms.extend(case["visible_required_all"])
                backstage_terms = list(case.get("backstage_required_all", []))
                backstage_terms.extend(group[0] for group in case.get("backstage_required_any_groups", []))
                if case["require_self_check"]:
                    backstage_terms.append("自检: 0个数值已核 | 0个产品已核 | 0个来源已标注 | 置信度:低")
                output = (
                    f"{case['frontstage_markers'][0]}\n"
                    + "。".join(dict.fromkeys(output_terms))
                    + f"\n{case['backstage_markers'][0]}\n"
                    + "。".join(dict.fromkeys(backstage_terms))
                )
            else:
                if case["require_self_check"]:
                    output_terms.append("自检: 0个数值已核 | 0个产品已核 | 0个来源已标注 | 置信度:低")
                output = "。".join(dict.fromkeys(output_terms))
            run = {
                "case_id": case["id"],
                "agent": agent,
                "triggered": case["expected_trigger"],
                "selected_route": case["expected_route"],
                "selected_mode": case["accepted_modes"][0],
                "output": output,
                "captured_at": "2026-07-15T00:00:00+00:00",
                "skill_version": version(),
                "runtime_package_fingerprint_sha256": fingerprints[profile],
                "_line": len(records) + 1,
            }
            passed, failures = score_run(run, case)
            if not passed:
                print(f"scorer self-test failed for {agent}/{case['id']}: {', '.join(failures)}")
                return 1
            records.append(run)
    metadata_errors = validate_release_metadata(records, data, fingerprints)
    if metadata_errors:
        print("scorer self-test metadata failed: " + "; ".join(metadata_errors[:5]))
        return 1
    invalid = dict(records[0])
    invalid["runtime_package_fingerprint_sha256"] = "invalid"
    if not validate_release_metadata([invalid], data, fingerprints):
        print("scorer self-test failed to reject a package fingerprint mismatch")
        return 1
    print(f"cross-agent scorer self-test passed: {len(records)} synthetic mechanics checks; zero live claims")
    return 0


def score_runs(
    data: dict[str, Any],
    records: list[dict[str, Any]],
    *,
    benchmark_path: Path,
    require_complete: bool,
    release_gate: bool,
    summary_output: Path | None,
) -> int:
    case_map = {case["id"]: case for case in data["cases"]}
    agents = set(data["target_agents"])
    errors: list[str] = []
    results: dict[str, list[tuple[str, bool, list[str]]]] = defaultdict(list)
    seen_pairs: set[tuple[str, str]] = set()
    fingerprints = package_fingerprints(data)

    for run in records:
        line = run.get("_line")
        case_id = run.get("case_id")
        agent = run.get("agent")
        if case_id not in case_map:
            errors.append(f"line {line}: unknown case_id {case_id!r}")
            continue
        if agent not in agents:
            errors.append(f"line {line}: unknown agent {agent!r}")
            continue
        pair = (agent, case_id)
        if pair in seen_pairs:
            errors.append(f"line {line}: duplicate run {agent}/{case_id}")
            continue
        seen_pairs.add(pair)
        passed, failures = score_run(run, case_map[case_id])
        results[agent].append((case_id, passed, failures))

    if release_gate:
        errors.extend(validate_release_metadata(records, data, fingerprints))
    if errors:
        print("cross-agent run input failed")
        for error in errors[:80]:
            print(error)
        if len(errors) > 80:
            print(f"... {len(errors) - 80} more errors")

    threshold = float(data["pass_policy"]["minimum_case_pass_rate"])
    expected_case_ids = set(case_map)
    effective_require_complete = require_complete or release_gate
    agent_summaries: dict[str, dict[str, Any]] = {}
    overall_ok = not errors and bool(results)

    for agent in sorted(results):
        agent_results = results[agent]
        passed_count = sum(1 for _case_id, passed, _failures in agent_results if passed)
        rate = passed_count / len(agent_results) if agent_results else 0.0
        missing = sorted(expected_case_ids - {case_id for case_id, _passed, _failures in agent_results})
        passed = rate >= threshold and (not effective_require_complete or not missing)
        status = "PASS" if passed else "FAIL"
        print(f"{status} {agent}: {passed_count}/{len(agent_results)} ({rate:.1%})")
        failure_types: Counter[str] = Counter()
        for case_id, case_passed, failures in agent_results:
            if not case_passed:
                print(f"  {case_id}: {', '.join(failures)}")
                failure_types.update(failure.split(":", 1)[0] for failure in failures)
        if effective_require_complete and missing:
            print("  missing: " + ", ".join(missing))
        if not passed:
            overall_ok = False
        agent_summaries[agent] = {
            "completed_cases": len(agent_results),
            "passed_cases": passed_count,
            "pass_rate": round(rate, 4),
            "missing_cases": missing,
            "failure_types": dict(sorted(failure_types.items())),
            "passed": passed,
        }

    missing_agents = sorted(agents - set(results)) if release_gate else []
    if missing_agents:
        overall_ok = False
        print("release gate missing agents: " + ", ".join(missing_agents))
    if not results:
        print("cross-agent run input failed: no valid records")

    complete_agents = sum(
        summary["completed_cases"] == len(case_map) and not summary["missing_cases"]
        for summary in agent_summaries.values()
    )
    passed_agents = sum(summary["passed"] for summary in agent_summaries.values())
    summary = {
        "schema_version": 1,
        "status": "passed" if release_gate and overall_ok else "failed" if release_gate else "scored",
        "skill_version": version(),
        "package_fingerprints_sha256": fingerprints,
        "benchmark_sha256": file_sha256(benchmark_path),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "release_gate": release_gate,
        "target_agents": len(agents),
        "target_agent_names": sorted(agents),
        "total_cases": len(case_map),
        "run_records": len(seen_pairs),
        "complete_agents": complete_agents,
        "passed_agents": passed_agents,
        "minimum_case_pass_rate": threshold,
        "agent_results": agent_summaries,
        "raw_outputs_bundled": False,
    }
    if summary_output:
        write_summary(summary_output, summary)
        print(f"sanitized run summary written: {summary_output}")
    return 0 if overall_ok else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate or score cross-agent blind benchmark runs")
    parser.add_argument("--benchmark", default=str(DEFAULT_BENCHMARK))
    parser.add_argument("--input", help="JSONL file containing captured agent runs")
    parser.add_argument("--require-complete", action="store_true", help="require every case for each recorded agent")
    parser.add_argument("--release-gate", action="store_true", help="require every target agent, current version metadata, and full case coverage")
    parser.add_argument("--summary-output", help="write a sanitized score summary without raw outputs")
    parser.add_argument("--print-runtime-fingerprint", action="store_true")
    parser.add_argument("--package-profile", choices=sorted(VALID_PACKAGE_PROFILES), default="codex")
    parser.add_argument("--self-test", action="store_true", help="test scorer mechanics with synthetic records; produces no live result")
    parser.add_argument("--check", action="store_true", help="validate benchmark readiness only")
    args = parser.parse_args()

    if args.print_runtime_fingerprint:
        print(runtime_fingerprint(args.package_profile))
        return 0
    benchmark_path = Path(args.benchmark)
    benchmark = load_json(benchmark_path)
    errors = validate_benchmark(benchmark)
    if errors:
        print("cross-agent benchmark validation failed")
        for error in errors:
            print(error)
        return 1
    if args.self_test:
        return run_scorer_self_test(benchmark)
    print(
        "cross-agent benchmark ready: "
        f"{len(benchmark['cases'])} cases, {len(benchmark['target_agents'])} target agents, no live results bundled"
    )
    if args.release_gate and (not args.input or not args.summary_output):
        print("--release-gate requires --input and --summary-output", file=sys.stderr)
        return 1
    if args.input:
        try:
            records = read_runs(Path(args.input))
        except (OSError, ValueError) as exc:
            print(f"cross-agent run input failed: {exc}", file=sys.stderr)
            return 1
        return score_runs(
            benchmark,
            records,
            benchmark_path=benchmark_path,
            require_complete=args.require_complete,
            release_gate=args.release_gate,
            summary_output=Path(args.summary_output) if args.summary_output else None,
        )
    if not args.check:
        print("provide --input runs.jsonl to score captured runs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
