#!/usr/bin/env python3
"""Build or check the public release manifest."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def count_markdown_table_rows(path: Path, columns: int) -> int:
    rows = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) != columns or cells[0] in {"ID", "----"}:
            continue
        if not cells[0] or cells[0].startswith("-"):
            continue
        rows += 1
    return rows


def count_trigger_queries() -> int:
    data = json.loads((ROOT / "docs/evals/trigger-queries.json").read_text(encoding="utf-8"))
    return len(data.get("queries", []))


def count_output_mode_samples() -> int:
    data = json.loads((ROOT / "docs/evals/output-mode-samples.json").read_text(encoding="utf-8"))
    return len(data.get("samples", []))


def count_audience_layering_samples() -> int:
    data = json.loads((ROOT / "docs/evals/audience-layering-samples.json").read_text(encoding="utf-8"))
    return len(data.get("samples", []))


def count_freshness_claim_samples() -> int:
    data = json.loads((ROOT / "docs/evals/freshness-claim-samples.json").read_text(encoding="utf-8"))
    return len(data.get("samples", []))


def count_evidence_claim_samples() -> int:
    data = json.loads((ROOT / "docs/evals/evidence-claim-samples.json").read_text(encoding="utf-8"))
    return len(data.get("samples", []))


def count_executive_memo_samples() -> int:
    data = json.loads((ROOT / "docs/evals/executive-memo-samples.json").read_text(encoding="utf-8"))
    return len(data.get("samples", []))


def count_decision_package_samples() -> int:
    data = json.loads((ROOT / "docs/evals/decision-package-samples.json").read_text(encoding="utf-8"))
    return len(data.get("samples", []))


def count_execution_gate_samples() -> int:
    data = json.loads((ROOT / "docs/evals/execution-gate-samples.json").read_text(encoding="utf-8"))
    return len(data.get("samples", []))


def count_route_switch_samples() -> int:
    data = json.loads((ROOT / "docs/evals/route-switch-samples.json").read_text(encoding="utf-8"))
    return len(data.get("samples", []))


def count_route_scorecard_samples() -> int:
    data = json.loads((ROOT / "docs/evals/route-scorecard-samples.json").read_text(encoding="utf-8"))
    return len(data.get("samples", []))


def count_post_launch_samples() -> int:
    data = json.loads((ROOT / "docs/evals/post-launch-samples.json").read_text(encoding="utf-8"))
    return len(data.get("samples", []))


def count_decision_learning_samples() -> int:
    data = json.loads((ROOT / "docs/evals/decision-learning-samples.json").read_text(encoding="utf-8"))
    return len(data.get("samples", []))


def count_risk_ledger_samples() -> int:
    data = json.loads((ROOT / "docs/evals/risk-ledger-samples.json").read_text(encoding="utf-8"))
    return len(data.get("samples", []))


def count_decision_card_samples() -> int:
    data = json.loads((ROOT / "docs/evals/launch-decision-card-samples.json").read_text(encoding="utf-8"))
    return len(data.get("valid", [])) + len(data.get("invalid", []))


def count_golden_example_assertion_sets() -> int:
    data = json.loads((ROOT / "docs/evals/golden-example-assertions.json").read_text(encoding="utf-8"))
    return len(data.get("samples", []))


def load_live_release_status() -> dict:
    return json.loads((ROOT / "docs/evals/live-release-status.json").read_text(encoding="utf-8"))


def load_quality_rubric() -> dict:
    return json.loads((ROOT / "docs/evals/output-quality-rubric.json").read_text(encoding="utf-8"))


def load_data_freshness() -> dict:
    data = json.loads((ROOT / "docs/data-sources.json").read_text(encoding="utf-8"))
    cutoffs = sorted(
        item["data_cutoff"]
        for item in data.get("categories", [])
        if item.get("data_cutoff") and item["data_cutoff"] != "none"
    )
    refresh_required = [
        item["category"]
        for item in data.get("categories", [])
        if item.get("status", "").startswith(("needs_refresh", "requires_"))
    ]
    return {
        "ledger": "docs/data-sources.json",
        "oldest_category_cutoff": cutoffs[0] if cutoffs else "none",
        "latest_category_cutoff": cutoffs[-1] if cutoffs else "none",
        "refresh_required_categories": refresh_required,
    }


def load_evidence_provenance() -> dict:
    data = json.loads((ROOT / "docs/evidence-ledger.json").read_text(encoding="utf-8"))
    status_counts = {"verified": 0, "partial": 0, "missing": 0}
    for source in data.get("sources", []):
        status = source.get("provenance_status")
        if status in status_counts:
            status_counts[status] += 1
    return {
        "ledger": "docs/evidence-ledger.json",
        "schema": "schemas/evidence-ledger.schema.json",
        "sources": len(data.get("sources", [])),
        "status_counts": status_counts,
        "release_claim": "provenance_inventory_only",
    }


def build_manifest() -> dict:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    rubric = load_quality_rubric()
    return {
        "version": version,
        "data_freshness": load_data_freshness(),
        "evidence_provenance": load_evidence_provenance(),
        "network_required": False,
        "secrets_required": False,
        "install_hooks": False,
        "write_scope": "user-specified output path only",
        "dependencies": [],
        "publish": {
            "platforms": ["codex", "clawhub", "skillhub"],
            "platform_fields": "docs/platform-publish-fields.json",
            "platform_fields_validator": "scripts/validate_platform_fields.py",
            "package_builder": "scripts/build_publish_package.py",
            "live_release_gate": "docs/evals/live-release-status.json",
            "skillhub_filtered_root_files": [".gitignore", "LICENSE", "VERSION"],
            "package_profile": "runtime_only",
            "runtime_capabilities": "docs/runtime-capabilities.json",
            "personal_packages": {
                "hermes": {
                    "profile": "personal_full",
                    "package_name": f"hermes-personal-china-marketing-copilot-v{version}.zip",
                    "install_target": "~/.hermes/skills/china-marketing-copilot/",
                    "network_mode": "offline_first",
                }
            },
            "source_only_paths": [
                "quickstart-example.md",
                "docs/maintainer-guide.md",
                "docs/platform-listing.md",
                "docs/routes/platform-publish.md",
                "scripts/build_publish_package.py",
                "scripts/validate_skill_pack.py",
                "docs/evals/cross-agent-benchmark.json",
                "docs/evals/live-release-status.json",
                "docs/evals/legacy-compatibility-samples.json",
                "scripts/evaluate_cross_agent_runs.py",
                "scripts/evaluate_legacy_compatibility.py",
                "scripts/install_local.py",
                "scripts/audit_evidence_ledger.py",
            ],
            "skillhub_license_path": "docs/package-license.txt",
            "trust_documents": ["CHANGELOG.md", "SECURITY.md", "RELEASE-MANIFEST.json", "RELEASE-VALIDATION.json"],
        },
        "eval_counts": {
            "trigger_queries": count_trigger_queries(),
            "output_mode_samples": count_output_mode_samples(),
            "audience_layering_samples": count_audience_layering_samples(),
            "freshness_claim_samples": count_freshness_claim_samples(),
            "evidence_claim_samples": count_evidence_claim_samples(),
            "decision_package_samples": count_decision_package_samples(),
            "executive_memo_samples": count_executive_memo_samples(),
            "route_scorecard_samples": count_route_scorecard_samples(),
            "route_switch_samples": count_route_switch_samples(),
            "execution_gate_samples": count_execution_gate_samples(),
            "post_launch_samples": count_post_launch_samples(),
            "decision_learning_samples": count_decision_learning_samples(),
            "risk_ledger_samples": count_risk_ledger_samples(),
            "decision_card_samples": count_decision_card_samples(),
            "marketing_tasks": count_markdown_table_rows(ROOT / "docs/evals/marketing-task-samples.md", 8),
            "negative_signal_samples": count_markdown_table_rows(ROOT / "docs/evals/negative-signal-samples.md", 6),
            "negative_signal_adversarial_samples": len(
                json.loads((ROOT / "docs/evals/negative-signal-adversarial-samples.json").read_text(encoding="utf-8")).get("samples", [])
            ),
            "negative_propagation_samples": len(
                json.loads((ROOT / "docs/evals/negative-propagation-samples.json").read_text(encoding="utf-8")).get("samples", [])
            ),
            "golden_examples": len(list((ROOT / "assets/examples").glob("*.md"))),
            "golden_example_assertion_sets": count_golden_example_assertion_sets(),
            "route_files": len(list((ROOT / "docs/routes").glob("*.md"))),
            "quality_rubric_dimensions": len(rubric.get("dimensions", [])),
            "cross_agent_benchmark_cases": len(
                json.loads((ROOT / "docs/evals/cross-agent-benchmark.json").read_text(encoding="utf-8")).get("cases", [])
            ),
            "cross_agent_live_results": load_live_release_status().get("run_records", 0),
            "legacy_compatibility_cases": len(
                json.loads((ROOT / "docs/evals/legacy-compatibility-samples.json").read_text(encoding="utf-8")).get("cases", [])
            ),
            "legacy_compatibility_live_results": 0,
        },
        "quality_gate": {
            "rubric": "docs/evals/output-quality-rubric.json",
            "passing_score": rubric.get("passing_score"),
            "max_score": rubric.get("max_score"),
        },
        "validation": {
            "report": "RELEASE-VALIDATION.json",
            "command": "python3 -B scripts/validate_skill_pack.py --write-report",
            "semantics": "actual_run_results",
            "live_release_status": "docs/evals/live-release-status.json",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build or check RELEASE-MANIFEST.json")
    parser.add_argument("--check", action="store_true", help="fail if RELEASE-MANIFEST.json differs")
    args = parser.parse_args()

    generated = build_manifest()
    manifest_path = ROOT / "RELEASE-MANIFEST.json"
    if args.check:
        current = json.loads(manifest_path.read_text(encoding="utf-8"))
        if current != generated:
            print(json.dumps({"expected": generated, "actual": current}, ensure_ascii=False, indent=2))
            return 1
        print("release manifest is current")
        return 0

    manifest_path.write_text(json.dumps(generated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {manifest_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
