#!/usr/bin/env python3
"""Validate the blind benchmark corpus or score captured cross-agent runs."""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BENCHMARK = ROOT / "docs/evals/cross-agent-benchmark.json"
VALID_MODES = {"快速版", "标准版", "深度版", "不适用"}
VALID_ROUTES = {
    f"docs/routes/{path.name}"
    for path in (ROOT / "docs/routes").glob("*.md")
    if path.name != "platform-publish.md"
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_benchmark(data: dict) -> list[str]:
    errors: list[str] = []
    if data.get("status") != "benchmark_ready_no_live_results":
        errors.append("status must state that live results are not bundled")
    target_agents = data.get("target_agents")
    if not isinstance(target_agents, list) or len(set(target_agents)) < 4:
        errors.append("target_agents must include at least four unique agents")
    cases = data.get("cases")
    if not isinstance(cases, list) or len(cases) < 16:
        errors.append("benchmark must include at least 16 cases")
        return errors

    seen: set[str] = set()
    positive_routes: set[str] = set()
    negative_count = 0
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
    return errors


def read_runs(path: Path) -> list[dict]:
    records: list[dict] = []
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


def score_run(run: dict, case: dict) -> tuple[bool, list[str]]:
    failures: list[str] = []
    output = run.get("output")
    if not isinstance(output, str):
        failures.append("output")
        output = ""
    if run.get("triggered") is not case["expected_trigger"]:
        failures.append("trigger")
    if run.get("selected_route") != case["expected_route"]:
        failures.append("route")
    if run.get("selected_mode") not in case["accepted_modes"]:
        failures.append("mode")
    missing_all = [term for term in case["required_all"] if term not in output]
    if missing_all:
        failures.append("required_all:" + ",".join(missing_all))
    for group in case["required_any_groups"]:
        if not any(term in output for term in group):
            failures.append("required_any:" + "|".join(group))
    matched_forbidden = [pattern for pattern in case["forbidden_regex"] if re.search(pattern, output)]
    if matched_forbidden:
        failures.append("forbidden_regex:" + ",".join(matched_forbidden))
    if len(output) > case["max_output_chars"]:
        failures.append(f"length:{len(output)}>{case['max_output_chars']}")
    if case["require_self_check"] and "自检:" not in output:
        failures.append("self_check")
    return not failures, failures


def score_runs(data: dict, records: list[dict], require_complete: bool) -> int:
    case_map = {case["id"]: case for case in data["cases"]}
    agents = set(data["target_agents"])
    errors: list[str] = []
    results: dict[str, list[tuple[str, bool, list[str]]]] = defaultdict(list)
    seen_pairs: set[tuple[str, str]] = set()

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

    if errors:
        print("cross-agent run input failed")
        for error in errors:
            print(error)
        return 1

    threshold = float(data["pass_policy"]["minimum_case_pass_rate"])
    overall_ok = True
    expected_case_ids = set(case_map)
    for agent in sorted(results):
        agent_results = results[agent]
        passed_count = sum(1 for _case_id, passed, _failures in agent_results if passed)
        rate = passed_count / len(agent_results) if agent_results else 0.0
        missing = sorted(expected_case_ids - {case_id for case_id, _passed, _failures in agent_results})
        status = "PASS" if rate >= threshold and (not require_complete or not missing) else "FAIL"
        print(f"{status} {agent}: {passed_count}/{len(agent_results)} ({rate:.1%})")
        for case_id, passed, failures in agent_results:
            if not passed:
                print(f"  {case_id}: {', '.join(failures)}")
        if require_complete and missing:
            print("  missing: " + ", ".join(missing))
        if status == "FAIL":
            overall_ok = False
    if not results:
        print("cross-agent run input failed: no valid records")
        return 1
    return 0 if overall_ok else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate or score cross-agent blind benchmark runs")
    parser.add_argument("--benchmark", default=str(DEFAULT_BENCHMARK))
    parser.add_argument("--input", help="JSONL file containing captured agent runs")
    parser.add_argument("--require-complete", action="store_true", help="require every case for each recorded agent")
    parser.add_argument("--check", action="store_true", help="validate benchmark readiness only")
    args = parser.parse_args()

    benchmark = load_json(Path(args.benchmark))
    errors = validate_benchmark(benchmark)
    if errors:
        print("cross-agent benchmark validation failed")
        for error in errors:
            print(error)
        return 1
    print(
        "cross-agent benchmark ready: "
        f"{len(benchmark['cases'])} cases, {len(benchmark['target_agents'])} target agents, no live results bundled"
    )
    if args.input:
        return score_runs(benchmark, read_runs(Path(args.input)), args.require_complete)
    if not args.check:
        print("provide --input runs.jsonl to score captured runs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
