#!/usr/bin/env python3
"""Validate the Skill package before commit or publish."""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from calendar import monthrange
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SELF = Path(__file__).resolve()
WRITING_REPORT = False

REQUIRED_PATHS = [
    "VERSION",
    "SKILL.md",
    "CHANGELOG.md",
    "SECURITY.md",
    "RELEASE-MANIFEST.json",
    "RELEASE-VALIDATION.json",
    "agents/openai.yaml",
    "assets/launch-decision-card.md",
    "assets/examples/image-flagship-launch.md",
    "assets/examples/ai-claim-review.md",
    "assets/examples/headphone-comment-analysis.md",
    "assets/examples/open-ear-creative-directions.md",
    "assets/examples/hypershell-links-boss-proposal.md",
    "schemas/launch-decision.schema.json",
    "schemas/evidence-ledger.schema.json",
    "schemas/negative-signal-batch.schema.json",
    "docs/agent-router.md",
    "docs/platform-listing.md",
    "docs/platform-publish-fields.json",
    "docs/maintainer-guide.md",
    "docs/data-index.md",
    "docs/data-sources.json",
    "docs/evidence-ledger.json",
    "docs/runtime-capabilities.json",
    "docs/package-license.txt",
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
    "docs/routes/platform-publish.md",
    "docs/templates/strategy-decision-system.md",
    "docs/templates/message-house.md",
    "docs/templates/channel-kol-activation.md",
    "docs/templates/audience-layering.md",
    "docs/templates/execution-readiness-gate.md",
    "docs/templates/post-launch-war-room.md",
    "docs/templates/output-mode-policy.md",
    "docs/templates/launch-decision-package.md",
    "docs/templates/executive-decision-memo.md",
    "docs/templates/route-scorecard.md",
    "docs/templates/evidence-freshness-gate.md",
    "docs/templates/route-switch-playbook.md",
    "docs/templates/decision-consistency-gate.md",
    "docs/templates/decision-learning-record.md",
    "docs/templates/risk-ledger.md",
    "docs/templates/creative-output.md",
    "docs/templates/risk-assessment.md",
    "docs/templates/quality-check-tools.md",
    "docs/ecosystem/market-signals-2026.md",
    "docs/ecosystem/negative-early-warning.md",
    "docs/ecosystem/negative-signal-rules.json",
    "docs/evals/marketing-task-samples.md",
    "docs/evals/negative-signal-samples.md",
    "docs/evals/negative-signal-adversarial-samples.json",
    "docs/evals/negative-propagation-samples.json",
    "docs/evals/trigger-queries.json",
    "docs/evals/output-mode-samples.json",
    "docs/evals/audience-layering-samples.json",
    "docs/evals/freshness-claim-samples.json",
    "docs/evals/evidence-claim-samples.json",
    "docs/evals/decision-package-samples.json",
    "docs/evals/executive-memo-samples.json",
    "docs/evals/route-scorecard-samples.json",
    "docs/evals/route-switch-samples.json",
    "docs/evals/execution-gate-samples.json",
    "docs/evals/post-launch-samples.json",
    "docs/evals/decision-learning-samples.json",
    "docs/evals/risk-ledger-samples.json",
    "docs/evals/launch-decision-card-samples.json",
    "docs/evals/output-quality-rubric.json",
    "docs/evals/golden-example-assertions.json",
    "docs/evals/cross-agent-benchmark.json",
    "docs/evals/live-release-status.json",
    "docs/evals/legacy-compatibility-samples.json",
    "scripts/preprocess.py",
    "scripts/evaluate_negative_signals.py",
    "scripts/evaluate_audience_layering.py",
    "scripts/analyze_signal_batch.py",
    "scripts/evaluate_negative_propagation.py",
    "scripts/evaluate_execution_gate.py",
    "scripts/evaluate_golden_examples.py",
    "scripts/evaluate_freshness_claims.py",
    "scripts/evaluate_evidence_claims.py",
    "scripts/evaluate_decision_package.py",
    "scripts/evaluate_executive_memo.py",
    "scripts/evaluate_route_scorecard.py",
    "scripts/evaluate_route_switches.py",
    "scripts/evaluate_post_launch_samples.py",
    "scripts/evaluate_decision_learning.py",
    "scripts/evaluate_risk_ledger.py",
    "scripts/evaluate_quality_rubric.py",
    "scripts/validate_decision_output.py",
    "scripts/check_internal_links.py",
    "scripts/audit_script_safety.py",
    "scripts/audit_knowledge_claims.py",
    "scripts/audit_evidence_ledger.py",
    "scripts/evaluate_cross_agent_runs.py",
    "scripts/evaluate_legacy_compatibility.py",
    "scripts/install_local.py",
    "scripts/validate_platform_fields.py",
    "scripts/verify_release_artifacts.py",
    "scripts/build_release_manifest.py",
    "scripts/build_publish_package.py",
]

FORCED_WORD = "必" + "须"
PRIVATE_KEY_PATTERN = "BEGIN " + ".*" + "PRIVATE " + "KEY"

FORBIDDEN_PATTERNS = [
    ("legacy scan filename", re.compile("weibo-news-" + "signal-scan")),
    ("forced weibo news scan", re.compile("微博/新闻" + "信号扫描")),
    ("forced scan wording", re.compile(FORCED_WORD + "扫描")),
    ("forced recent search", re.compile("搜索近 30 " + "天")),
    ("forced browser wording", re.compile(FORCED_WORD + r".{0,20}" + "browser", re.I)),
    ("forced network wording", re.compile(FORCED_WORD + r".{0,20}" + "联网")),
]

SECRET_PATTERNS = [
    ("clawhub token", re.compile(r"clh_[A-Za-z0-9]+")),
    ("skillhub token", re.compile(r"skh_[A-Za-z0-9]+")),
    ("private key", re.compile(PRIVATE_KEY_PATTERN)),
    ("ssh private key filename", re.compile("id_" + "ed25519")),
    ("clawhub token env", re.compile("CLAW" + "HUB_TOKEN")),
]

TEXT_SUFFIXES = {".md", ".yaml", ".yml", ".json", ".py", ".txt", ".gitignore"}
REPORT_FILENAME = "RELEASE-VALIDATION.json"


def fail(message):
    print(f"FAIL {message}")
    return 1


def iter_text_files():
    for path in ROOT.rglob("*"):
        if any(part in {".git", "dist", "__pycache__"} or part.startswith("dist-v") for part in path.parts) or path == SELF:
            continue
        if path.is_file() and (path.suffix in TEXT_SUFFIXES or path.name == ".gitignore"):
            yield path


def validate_skill_metadata():
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not match:
        return fail("SKILL.md missing YAML frontmatter")
    fields = {}
    for line in match.group(1).splitlines():
        if ": " in line:
            key, value = line.split(": ", 1)
            fields[key] = value
    name = fields.get("name", "")
    description = fields.get("description", "")
    if not re.fullmatch(r"[a-z0-9-]{1,64}", name):
        return fail("invalid skill name")
    if not description or len(description) > 1024 or "<" in description or ">" in description:
        return fail("invalid skill description")
    print(f"PASS skill metadata: {name}")
    return 0


def validate_skill_router_shape():
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    lines = text.splitlines()
    if len(lines) > 130:
        return fail(f"SKILL.md should stay router-sized, got {len(lines)} lines")
    required_terms = [
        "docs/agent-router.md",
        "docs/templates/output-mode-policy.md",
        "docs/templates/audience-layering.md",
        "docs/templates/launch-decision-package.md",
        "docs/templates/executive-decision-memo.md",
        "docs/templates/route-scorecard.md",
        "docs/templates/evidence-freshness-gate.md",
        "docs/templates/route-switch-playbook.md",
        "docs/templates/execution-readiness-gate.md",
        "docs/templates/decision-consistency-gate.md",
        "docs/templates/decision-learning-record.md",
        "docs/templates/risk-ledger.md",
        "docs/routes/creative-campaign.md",
        "schemas/launch-decision.schema.json",
        "scripts/validate_decision_output.py",
    ]
    missing = [term for term in required_terms if term not in text]
    if missing:
        return fail("SKILL.md missing router terms: " + ", ".join(missing))
    print(f"PASS SKILL.md router shape: {len(lines)} lines")
    return 0


def validate_platform_listing():
    text = (ROOT / "docs" / "platform-listing.md").read_text(encoding="utf-8")
    required_terms = [
        "中国3C营销助手",
        "中国3C上市决策系统",
        "新品上市策略、负面预警与上线决策工作流",
        "上市任务简报",
        "上市决策包",
        "管理层决策纪要",
        "路线裁决",
        "路线评分卡",
        "证据架构",
        "评论区压力测试",
        "风险账本",
        "负面雷达",
        "上线闸门",
        "决策学习记录",
        "旧用法兼容",
        "能力边界",
        "displayName",
        "slug",
    ]
    missing = [term for term in required_terms if term not in text]
    if missing:
        return fail("platform-listing.md missing terms: " + ", ".join(missing))
    if "browser-use" in text or "微博扫描" in text:
        return fail("platform-listing.md should not promise live browser or weibo scanning")
    print("PASS docs/platform-listing.md")
    return 0


def validate_readme_landing():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    required_terms = [
        "中国3C上市决策系统",
        "深度版可交付",
        "日常创意、文案、KOL、竞品和评论分析默认直接完成当前任务",
        "旧用法兼容",
        "上市决策包",
        "上市总控台",
        "管理层决策纪要",
        "路线评分卡",
        "风险账本",
        "负面雷达",
        "路线切换剧本",
        "上线闸门",
        "战情复盘",
        "决策学习记录",
        "docs/maintainer-guide.md",
    ]
    missing = [term for term in required_terms if term not in text]
    if missing:
        return fail("README.md missing landing terms: " + ", ".join(missing))
    if "目录结构" in text or "子智能体指令" in text or "快速开始" in text:
        return fail("README.md should stay user-facing; move maintainer material to docs/maintainer-guide.md")
    if len(text.splitlines()) > 190:
        return fail("README.md should stay platform-facing and concise")
    print("PASS README.md landing page")
    return 0


def validate_platform_publish_fields():
    result = subprocess.run(
        [sys.executable, "-B", "scripts/validate_platform_fields.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip(), file=sys.stderr)
    if result.returncode != 0:
        return fail("platform publish fields check failed")
    print("PASS platform publish fields")
    return 0


def validate_trust_documents():
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    security = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
    if f"## v{version}" not in changelog:
        return fail("CHANGELOG.md missing current version entry")
    for term in ["SECURITY.md", "发布清单", "包级校验"]:
        if term not in changelog:
            return fail(f"CHANGELOG.md missing trust term: {term}")
    required_security_terms = [
        "默认网络访问",
        "密钥要求",
        "写入范围",
        "不把 ClawHub、SkillHub、GitHub token 写入仓库",
        "浏览器、实时搜索、微博、新闻和平台后台能力只作增强",
        "包级验证会扫描",
        "scripts/audit_script_safety.py",
    ]
    missing = [term for term in required_security_terms if term not in security]
    if missing:
        return fail("SECURITY.md missing terms: " + ", ".join(missing))
    print("PASS CHANGELOG.md and SECURITY.md")
    return 0


def validate_required_paths():
    missing = [path for path in REQUIRED_PATHS if not (ROOT / path).exists()]
    if missing:
        return fail("missing required paths: " + ", ".join(missing))
    print(f"PASS required paths: {len(REQUIRED_PATHS)}")
    return 0


def validate_json():
    for rel in [
        "docs/ecosystem/negative-signal-rules.json",
        "docs/data-sources.json",
        "docs/evidence-ledger.json",
        "docs/runtime-capabilities.json",
        "docs/platform-publish-fields.json",
        "schemas/launch-decision.schema.json",
        "schemas/evidence-ledger.schema.json",
        "schemas/negative-signal-batch.schema.json",
        "docs/evals/trigger-queries.json",
        "docs/evals/output-mode-samples.json",
        "docs/evals/audience-layering-samples.json",
        "docs/evals/freshness-claim-samples.json",
        "docs/evals/evidence-claim-samples.json",
        "docs/evals/decision-package-samples.json",
        "docs/evals/executive-memo-samples.json",
        "docs/evals/route-scorecard-samples.json",
        "docs/evals/route-switch-samples.json",
        "docs/evals/execution-gate-samples.json",
        "docs/evals/post-launch-samples.json",
        "docs/evals/decision-learning-samples.json",
        "docs/evals/risk-ledger-samples.json",
        "docs/evals/launch-decision-card-samples.json",
        "docs/evals/output-quality-rubric.json",
        "docs/evals/golden-example-assertions.json",
        "docs/evals/cross-agent-benchmark.json",
        "docs/evals/legacy-compatibility-samples.json",
        "docs/evals/negative-propagation-samples.json",
        "RELEASE-MANIFEST.json",
        "RELEASE-VALIDATION.json",
    ]:
        json_path = ROOT / rel
        json.loads(json_path.read_text(encoding="utf-8"))
        print(f"PASS {rel}")
    return 0


def validate_data_sources():
    data_path = ROOT / "docs" / "data-sources.json"
    data = json.loads(data_path.read_text(encoding="utf-8"))
    if not isinstance(data.get("categories"), list) or len(data["categories"]) < 6:
        return fail("data-sources.json must include at least 6 categories")
    seen = set()
    freshness_summary = []
    today = date.today()
    for item in data["categories"]:
        category = item.get("category")
        if not category or category in seen:
            return fail("data-sources.json has missing or duplicate category")
        seen.add(category)
        if not item.get("data_cutoff") or not isinstance(item.get("must_refresh"), list) or not item["must_refresh"]:
            return fail(f"data-sources.json category missing freshness fields: {category}")
        if not isinstance(item.get("refresh_after_days"), int):
            return fail(f"data-sources.json category missing refresh_after_days: {category}")
        cutoff = item.get("data_cutoff")
        if cutoff != "none":
            try:
                year, month = (int(part) for part in cutoff.split("-"))
                cutoff_date = date(year, month, monthrange(year, month)[1])
            except (TypeError, ValueError):
                return fail(f"data-sources.json invalid data_cutoff: {category} -> {cutoff}")
            refresh_date = cutoff_date + timedelta(days=item["refresh_after_days"])
            state = "expired" if today > refresh_date else "current"
            freshness_summary.append(f"{category}={state}")
            if state == "expired" and not item.get("status", "").startswith(("needs_refresh", "requires_")):
                return fail(f"data-sources.json expired category lacks refresh status: {category}")
        for rel in item.get("primary_files", []):
            if not (ROOT / rel).exists():
                return fail(f"data-sources.json references missing file: {rel}")
    for item in data.get("cross_references", []):
        rel = item.get("path", "")
        if not rel or not (ROOT / rel).exists():
            return fail(f"data-sources.json references missing cross file: {rel}")
    print(f"PASS data-sources categories: {len(seen)} ({', '.join(freshness_summary)})")
    return 0


def validate_runtime_capabilities():
    data = json.loads((ROOT / "docs/runtime-capabilities.json").read_text(encoding="utf-8"))
    modes = data.get("modes", {})
    expected_modes = {"markdown_only", "script_enhanced", "connected"}
    if set(modes) != expected_modes:
        return fail("runtime capabilities modes mismatch")
    if data.get("default_mode") != "markdown_only":
        return fail("runtime capabilities must default to markdown_only")
    if modes["markdown_only"].get("requires") != []:
        return fail("markdown_only mode must not require tools")
    if modes["script_enhanced"].get("fallback_mode") != "markdown_only":
        return fail("script_enhanced mode must fall back to markdown_only")
    if modes["connected"].get("fallback_mode") != "markdown_only":
        return fail("connected mode must fall back to markdown_only")
    print("PASS runtime capabilities: markdown-only core + optional script and connected enhancements")
    return 0


def validate_evidence_ledger():
    result = subprocess.run(
        [sys.executable, "-B", "scripts/audit_evidence_ledger.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip(), file=sys.stderr)
    if result.returncode != 0:
        return fail("evidence ledger audit failed")
    print("PASS evidence ledger")
    return 0


def validate_cross_agent_benchmark():
    result = subprocess.run(
        [sys.executable, "-B", "scripts/evaluate_cross_agent_runs.py", "--self-test"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip(), file=sys.stderr)
    if result.returncode != 0:
        return fail("cross-agent benchmark readiness failed")
    print("PASS cross-agent benchmark readiness; live compatibility remains unclaimed")
    return 0


def validate_live_release_status():
    status_path = ROOT / "docs/evals/live-release-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    benchmark = json.loads((ROOT / "docs/evals/cross-agent-benchmark.json").read_text(encoding="utf-8"))
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if status.get("schema_version") != 1:
        return fail("live release status schema_version mismatch")
    if status.get("status") not in {"no_live_runs", "failed", "passed"}:
        return fail("live release status value is invalid")
    if status.get("skill_version") != version:
        return fail("live release status version mismatch")
    if status.get("target_agents") != len(benchmark.get("target_agents", [])):
        return fail("live release status target-agent count mismatch")
    if set(status.get("target_agent_names", [])) != set(benchmark.get("target_agents", [])):
        return fail("live release status target-agent names mismatch")
    if status.get("total_cases") != len(benchmark.get("cases", [])):
        return fail("live release status case count mismatch")
    if status.get("raw_outputs_bundled") is not False:
        return fail("live release status must exclude raw outputs")
    if status.get("status") == "no_live_runs":
        for field in ("run_records", "complete_agents", "passed_agents"):
            if status.get(field) != 0:
                return fail(f"no-live release status must set {field}=0")
        if status.get("package_fingerprints_sha256") != {}:
            return fail("no-live release status must not claim package fingerprints")
    if status.get("status") == "passed":
        from build_publish_package import live_release_gate_errors

        errors = live_release_gate_errors()
        if errors:
            return fail("live release status is stale: " + "; ".join(errors))
    print(
        "PASS live release status: "
        f"{status.get('status')}, {status.get('run_records', 0)} sanitized run record(s)"
    )
    return 0


def validate_local_installer():
    result = subprocess.run(
        [sys.executable, "-B", "scripts/install_local.py", "--self-test"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip(), file=sys.stderr)
    if result.returncode != 0:
        return fail("local install synchronization self-test failed")
    print("PASS local install synchronization and drift detection")
    return 0


def validate_legacy_compatibility():
    result = subprocess.run(
        [sys.executable, "-B", "scripts/evaluate_legacy_compatibility.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip(), file=sys.stderr)
    if result.returncode != 0:
        return fail("legacy compatibility contract failed")
    print("PASS old-user interaction compatibility contract")
    return 0


def validate_negative_propagation():
    result = subprocess.run(
        [sys.executable, "-B", "scripts/evaluate_negative_propagation.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip(), file=sys.stderr)
    if result.returncode != 0:
        return fail("negative propagation eval failed")
    print("PASS structured negative propagation eval")
    return 0


def validate_launch_decision_schema():
    schema_path = ROOT / "schemas" / "launch-decision.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    required = set(schema.get("required", []))
    expected = {
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
    }
    missing = sorted(expected - required)
    if missing:
        return fail("launch-decision schema missing required fields: " + ", ".join(missing))
    brief_required = (
        schema.get("properties", {})
        .get("launch_brief", {})
        .get("required", [])
    )
    if set(brief_required) != {
        "product_category",
        "launch_window",
        "business_goal",
        "target_audience",
        "budget_level",
        "evidence_available",
        "competitors",
        "planned_platforms",
        "risk_constraints",
        "missing_info",
    }:
        return fail("launch-decision schema launch_brief fields mismatch")
    package_required = (
        schema.get("properties", {})
        .get("decision_package", {})
        .get("required", [])
    )
    if set(package_required) != {
        "package_title",
        "package_version",
        "package_status",
        "primary_audience",
        "decision_owner",
        "handoff_summary",
        "included_sections",
        "open_decisions",
    }:
        return fail("launch-decision schema decision_package fields mismatch")
    package_properties = (
        schema.get("properties", {})
        .get("decision_package", {})
        .get("properties", {})
    )
    if set(package_properties.get("package_status", {}).get("enum", [])) != {"可评审", "需补证据", "暂停评审"}:
        return fail("launch-decision schema decision_package statuses mismatch")
    package_section_properties = (
        package_properties
        .get("included_sections", {})
        .get("items", {})
        .get("properties", {})
    )
    if set(package_section_properties.get("section_id", {}).get("enum", [])) != {
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
        "self_check",
    }:
        return fail("launch-decision schema decision_package section ids mismatch")
    if set(package_section_properties.get("status", {}).get("enum", [])) != {"已完成", "待补", "阻断"}:
        return fail("launch-decision schema decision_package section statuses mismatch")
    control_required = (
        schema.get("properties", {})
        .get("control_summary", {})
        .get("required", [])
    )
    if set(control_required) != {
        "verdict",
        "recommended_route",
        "confidence",
        "key_evidence_status",
        "top_risk",
        "hard_blocker_status",
        "next_72h_priority",
        "switch_trigger",
    }:
        return fail("launch-decision schema control_summary fields mismatch")
    memo_required = (
        schema.get("properties", {})
        .get("executive_memo", {})
        .get("required", [])
    )
    if set(memo_required) != {
        "decision_question",
        "verdict",
        "recommended_route",
        "one_line_answer",
        "evidence_basis",
        "core_tradeoff",
        "top_risk",
        "no_go_condition",
        "next_owner_action",
        "confidence",
    }:
        return fail("launch-decision schema executive_memo fields mismatch")
    decision_enum = (
        schema.get("properties", {})
        .get("decision", {})
        .get("enum", [])
    )
    if set(decision_enum) != {"直接执行", "调整后执行", "暂停重做"}:
        return fail("launch-decision schema has invalid decision enum")
    radar_items = (
        schema.get("properties", {})
        .get("negative_radar", {})
        .get("items", {})
        .get("properties", {})
    )
    risk_items = (
        schema.get("properties", {})
        .get("risk_ledger", {})
        .get("items", {})
    )
    if set(risk_items.get("required", [])) != {
        "risk_id",
        "priority",
        "evidence_anchor",
        "fact_status",
        "trigger",
        "actor",
        "compressed_narrative",
        "platform_path",
        "business_impact",
        "early_signal",
        "route_impact",
        "recommended_action",
        "side_effect",
        "disconfirming_evidence",
        "confidence",
    }:
        return fail("launch-decision schema risk_ledger fields mismatch")
    risk_properties = risk_items.get("properties", {})
    if set(risk_properties.get("priority", {}).get("enum", [])) != {"P0", "P1", "P2", "P3"}:
        return fail("launch-decision schema risk_ledger priorities mismatch")
    if set(risk_properties.get("fact_status", {}).get("enum", [])) != {"known", "inferred", "needs_verification"}:
        return fail("launch-decision schema risk_ledger fact statuses mismatch")
    if set(risk_properties.get("route_impact", {}).get("enum", [])) != {"继续", "缩窄", "切换", "暂停"}:
        return fail("launch-decision schema risk_ledger route impact mismatch")
    if set(radar_items.get("stage", {}).get("enum", [])) != {"S0", "S1", "S2", "S3", "S4"}:
        return fail("launch-decision schema missing narrative stages")
    if set(radar_items.get("route_impact", {}).get("enum", [])) != {"继续", "缩窄", "切换", "暂停"}:
        return fail("launch-decision schema missing route impact enum")
    recommended_required = (
        schema.get("properties", {})
        .get("route_verdict", {})
        .get("properties", {})
        .get("recommended", {})
        .get("required", [])
    )
    if set(recommended_required) != {"route_name", "rationale", "conditions"}:
        return fail("launch-decision schema recommended route fields mismatch")
    route_scorecard_items = (
        schema.get("properties", {})
        .get("route_scorecard", {})
        .get("items", {})
    )
    if set(route_scorecard_items.get("required", [])) != {
        "route_name",
        "route_role",
        "evidence_score",
        "audience_fit_score",
        "competitor_defense_score",
        "risk_control_score",
        "resource_fit_score",
        "timing_score",
        "total_score",
        "verdict",
        "rationale",
        "improvement_needed",
    }:
        return fail("launch-decision schema route_scorecard fields mismatch")
    route_scorecard_properties = route_scorecard_items.get("properties", {})
    if set(route_scorecard_properties.get("route_role", {}).get("enum", [])) != {"推荐", "备选", "弃用"}:
        return fail("launch-decision schema route_scorecard roles mismatch")
    if set(route_scorecard_properties.get("verdict", {}).get("enum", [])) != {"押主线", "保留备选", "弃用"}:
        return fail("launch-decision schema route_scorecard verdicts mismatch")
    for field in [
        "evidence_score",
        "audience_fit_score",
        "competitor_defense_score",
        "risk_control_score",
        "resource_fit_score",
        "timing_score",
    ]:
        spec = route_scorecard_properties.get(field, {})
        if spec.get("minimum") != 0 or spec.get("maximum") != 5:
            return fail(f"launch-decision schema route_scorecard {field} range mismatch")
    if route_scorecard_properties.get("total_score", {}).get("maximum") != 30:
        return fail("launch-decision schema route_scorecard total_score range mismatch")
    next_72_required = (
        schema.get("properties", {})
        .get("next_72_hours", {})
        .get("items", {})
        .get("required", [])
    )
    if set(next_72_required) != {"time", "action", "owner_role", "deliverable", "completion_standard"}:
        return fail("launch-decision schema next_72_hours fields mismatch")
    confidence_enum = (
        schema.get("properties", {})
        .get("self_check", {})
        .get("properties", {})
        .get("confidence", {})
        .get("enum", [])
    )
    if set(confidence_enum) != {"高", "中", "低"}:
        return fail("launch-decision schema confidence enum mismatch")
    route_switch_required = (
        schema.get("properties", {})
        .get("route_switch_playbook", {})
        .get("items", {})
        .get("required", [])
    )
    if set(route_switch_required) != {"trigger", "signal_stage", "route_action", "action", "owner_role", "evidence_to_check", "deadline"}:
        return fail("launch-decision schema route_switch_playbook fields mismatch")
    print("PASS schemas/launch-decision.schema.json contract")
    return 0


def validate_trigger_queries():
    trigger_path = ROOT / "docs" / "evals" / "trigger-queries.json"
    data = json.loads(trigger_path.read_text(encoding="utf-8"))
    queries = data.get("queries", [])
    if len(queries) < 12:
        return fail("trigger-queries.json must include at least 12 queries")
    ids = set()
    positive_count = 0
    negative_count = 0
    for item in queries:
        query_id = item.get("id")
        if not query_id or query_id in ids:
            return fail("trigger-queries.json has missing or duplicate id")
        ids.add(query_id)
        should_trigger = item.get("should_trigger")
        if not isinstance(should_trigger, bool):
            return fail(f"trigger query missing boolean should_trigger: {query_id}")
        route = item.get("expected_route")
        if should_trigger:
            positive_count += 1
            if not route or not (ROOT / route).exists():
                return fail(f"trigger query references missing route: {query_id} -> {route}")
            if not item.get("required_terms"):
                return fail(f"trigger query missing required terms: {query_id}")
        else:
            negative_count += 1
            if route is not None:
                return fail(f"negative trigger query must set expected_route=null: {query_id}")
            if not item.get("reason"):
                return fail(f"negative trigger query missing reason: {query_id}")
        for rel in item.get("expected_artifacts", []):
            if not (ROOT / rel).exists():
                return fail(f"trigger query references missing artifact: {query_id} -> {rel}")
    if positive_count < 8 or negative_count < 3:
        return fail("trigger-queries.json must cover positive routes and at least 3 non-trigger cases")
    print(f"PASS trigger queries: {positive_count} positive, {negative_count} negative")
    return 0


def validate_knowledge_claims():
    result = subprocess.run(
        [sys.executable, "-B", "scripts/audit_knowledge_claims.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip(), file=sys.stderr)
    if result.returncode != 0:
        return fail("knowledge claim audit failed")
    print("PASS knowledge claim audit")
    return 0


def validate_golden_examples():
    example_dir = ROOT / "assets" / "examples"
    examples = sorted(example_dir.glob("*.md"))
    if len(examples) < 3:
        return fail("assets/examples must include at least 3 golden examples")
    required_sections = ["## 原始输入", "## 任务路由", "## 最终输出片段", "## 关键判断依据", "## 预期断言"]
    for path in examples:
        text = path.read_text(encoding="utf-8")
        missing = [section for section in required_sections if section not in text]
        if missing:
            return fail(f"golden example missing sections: {path.relative_to(ROOT)} -> {', '.join(missing)}")
    result = subprocess.run(
        [sys.executable, "-B", "scripts/evaluate_golden_examples.py", "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip(), file=sys.stderr)
    if result.returncode != 0:
        return fail("golden example assertion check failed")
    print(f"PASS golden examples: {len(examples)}")
    return 0


def validate_output_modes():
    modes_path = ROOT / "docs" / "evals" / "output-mode-samples.json"
    data = json.loads(modes_path.read_text(encoding="utf-8"))
    modes = data.get("modes", [])
    if modes != ["快速版", "标准版", "深度版"]:
        return fail("output-mode-samples.json must define 快速版/标准版/深度版")
    samples = data.get("samples", [])
    if len(samples) < 5:
        return fail("output-mode-samples.json must include at least 5 samples")
    ids = set()
    seen_modes = set()
    for item in samples:
        sample_id = item.get("id")
        if not sample_id or sample_id in ids:
            return fail("output-mode-samples.json has missing or duplicate id")
        ids.add(sample_id)
        mode = item.get("expected_mode")
        if mode not in modes:
            return fail(f"output-mode-samples.json invalid mode: {sample_id}")
        seen_modes.add(mode)
        if not item.get("query") or not item.get("required_terms"):
            return fail(f"output-mode-samples.json missing query or terms: {sample_id}")
    if seen_modes != set(modes):
        return fail("output-mode-samples.json must cover all modes")
    policy = (ROOT / "docs/templates/output-mode-policy.md").read_text(encoding="utf-8")
    for mode in modes:
        if mode not in policy:
            return fail(f"output-mode-policy.md missing mode: {mode}")
    print(f"PASS output-mode samples: {len(samples)}")
    return 0


def validate_audience_layering():
    result = subprocess.run(
        [sys.executable, "-B", "scripts/evaluate_audience_layering.py", "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip(), file=sys.stderr)
    if result.returncode != 0:
        return fail("formal-material audience layering check failed")
    print("PASS formal-material frontstage and backstage separation")
    return 0


def validate_freshness_claims():
    samples_path = ROOT / "docs" / "evals" / "freshness-claim-samples.json"
    data = json.loads(samples_path.read_text(encoding="utf-8"))
    actions = data.get("actions", [])
    expected_actions = ["must_refresh", "mark_pending", "stable", "unsupported"]
    if actions != expected_actions:
        return fail("freshness-claim-samples.json actions mismatch")
    samples = data.get("samples", [])
    if len(samples) < 8:
        return fail("freshness-claim-samples.json must include at least 8 samples")
    ids = set()
    seen = set()
    for item in samples:
        sample_id = item.get("id")
        if not sample_id or sample_id in ids:
            return fail("freshness-claim-samples.json has missing or duplicate id")
        ids.add(sample_id)
        action = item.get("expected_action")
        if action not in actions:
            return fail(f"freshness-claim-samples.json invalid action: {sample_id}")
        seen.add(action)
        for key in ["claim", "claim_type", "required_marker"]:
            if not item.get(key):
                return fail(f"freshness-claim-samples.json missing {key}: {sample_id}")
    if seen != set(actions):
        return fail("freshness-claim-samples.json must cover all actions")
    result = subprocess.run(
        [sys.executable, "-B", "scripts/evaluate_freshness_claims.py", "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip(), file=sys.stderr)
    if result.returncode != 0:
        return fail("freshness claim script check failed")
    print(f"PASS freshness-claim samples: {len(samples)}")
    return 0


def validate_evidence_claims():
    samples_path = ROOT / "docs" / "evals" / "evidence-claim-samples.json"
    data = json.loads(samples_path.read_text(encoding="utf-8"))
    actions = data.get("actions", [])
    expected_actions = ["verified", "mark_pending", "same_source_required", "unsupported", "forbidden_absolute"]
    if actions != expected_actions:
        return fail("evidence-claim-samples.json actions mismatch")
    samples = data.get("samples", [])
    if len(samples) < 10:
        return fail("evidence-claim-samples.json must include at least 10 samples")
    ids = set()
    seen = set()
    for item in samples:
        sample_id = item.get("id")
        if not sample_id or sample_id in ids:
            return fail("evidence-claim-samples.json has missing or duplicate id")
        ids.add(sample_id)
        action = item.get("expected_action")
        if action not in actions:
            return fail(f"evidence-claim-samples.json invalid action: {sample_id}")
        seen.add(action)
        for key in ["claim", "claim_type", "required_marker"]:
            if not item.get(key):
                return fail(f"evidence-claim-samples.json missing {key}: {sample_id}")
    if seen != set(actions):
        return fail("evidence-claim-samples.json must cover all actions")
    result = subprocess.run(
        [sys.executable, "-B", "scripts/evaluate_evidence_claims.py", "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip(), file=sys.stderr)
    if result.returncode != 0:
        return fail("evidence claim script check failed")
    print(f"PASS evidence-claim samples: {len(samples)}")
    return 0


def validate_executive_memo_samples():
    samples_path = ROOT / "docs" / "evals" / "executive-memo-samples.json"
    data = json.loads(samples_path.read_text(encoding="utf-8"))
    decisions = data.get("decisions", [])
    expected_decisions = ["直接执行", "调整后执行", "暂停重做"]
    if decisions != expected_decisions:
        return fail("executive-memo-samples.json decisions mismatch")
    samples = data.get("samples", [])
    if len(samples) < 6:
        return fail("executive-memo-samples.json must include at least 6 samples")
    ids = set()
    seen = set()
    for item in samples:
        sample_id = item.get("id")
        if not sample_id or sample_id in ids:
            return fail("executive-memo-samples.json has missing or duplicate id")
        ids.add(sample_id)
        verdict = item.get("expected_verdict")
        if verdict not in decisions:
            return fail(f"executive-memo-samples.json invalid verdict: {sample_id}")
        seen.add(verdict)
        for key in ["input", "required_terms"]:
            if not item.get(key):
                return fail(f"executive-memo-samples.json missing {key}: {sample_id}")
    if seen != set(decisions):
        return fail("executive-memo-samples.json must cover all decisions")
    result = subprocess.run(
        [sys.executable, "-B", "scripts/evaluate_executive_memo.py", "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip(), file=sys.stderr)
    if result.returncode != 0:
        return fail("executive memo sample script check failed")
    print(f"PASS executive-memo samples: {len(samples)}")
    return 0


def validate_decision_package_samples():
    samples_path = ROOT / "docs" / "evals" / "decision-package-samples.json"
    data = json.loads(samples_path.read_text(encoding="utf-8"))
    statuses = data.get("package_statuses", [])
    expected_statuses = ["可评审", "需补证据", "暂停评审"]
    if statuses != expected_statuses:
        return fail("decision-package-samples.json statuses mismatch")
    required_section_ids = data.get("required_section_ids", [])
    if required_section_ids != [
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
    ]:
        return fail("decision-package-samples.json section ids mismatch")
    samples = data.get("samples", [])
    if len(samples) < 6:
        return fail("decision-package-samples.json must include at least 6 samples")
    ids = set()
    seen = set()
    for item in samples:
        sample_id = item.get("id")
        if not sample_id or sample_id in ids:
            return fail("decision-package-samples.json has missing or duplicate id")
        ids.add(sample_id)
        status = item.get("expected_status")
        if status not in statuses:
            return fail(f"decision-package-samples.json invalid status: {sample_id}")
        seen.add(status)
        for key in ["input", "required_terms"]:
            if not item.get(key):
                return fail(f"decision-package-samples.json missing {key}: {sample_id}")
    if seen != set(statuses):
        return fail("decision-package-samples.json must cover all statuses")
    result = subprocess.run(
        [sys.executable, "-B", "scripts/evaluate_decision_package.py", "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip(), file=sys.stderr)
    if result.returncode != 0:
        return fail("decision-package sample script check failed")
    print(f"PASS decision-package samples: {len(samples)}")
    return 0


def validate_execution_gate_samples():
    samples_path = ROOT / "docs" / "evals" / "execution-gate-samples.json"
    data = json.loads(samples_path.read_text(encoding="utf-8"))
    decisions = data.get("decisions", [])
    expected_decisions = ["直接执行", "调整后执行", "暂停重做"]
    if decisions != expected_decisions:
        return fail("execution-gate-samples.json decisions mismatch")
    samples = data.get("samples", [])
    if len(samples) < 6:
        return fail("execution-gate-samples.json must include at least 6 samples")
    ids = set()
    seen = set()
    for item in samples:
        sample_id = item.get("id")
        if not sample_id or sample_id in ids:
            return fail("execution-gate-samples.json has missing or duplicate id")
        ids.add(sample_id)
        decision = item.get("expected_decision")
        if decision not in decisions:
            return fail(f"execution-gate-samples.json invalid decision: {sample_id}")
        seen.add(decision)
        for key in ["input", "required_terms"]:
            if not item.get(key):
                return fail(f"execution-gate-samples.json missing {key}: {sample_id}")
    if seen != set(decisions):
        return fail("execution-gate-samples.json must cover all decisions")
    result = subprocess.run(
        [sys.executable, "-B", "scripts/evaluate_execution_gate.py", "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip(), file=sys.stderr)
    if result.returncode != 0:
        return fail("execution-gate sample script check failed")
    print(f"PASS execution-gate samples: {len(samples)}")
    return 0


def validate_route_scorecard_samples():
    samples_path = ROOT / "docs" / "evals" / "route-scorecard-samples.json"
    data = json.loads(samples_path.read_text(encoding="utf-8"))
    roles = data.get("route_roles", [])
    expected_roles = ["推荐", "备选", "弃用"]
    if roles != expected_roles:
        return fail("route-scorecard-samples.json roles mismatch")
    score_fields = data.get("score_fields", [])
    if score_fields != [
        "evidence_score",
        "audience_fit_score",
        "competitor_defense_score",
        "risk_control_score",
        "resource_fit_score",
        "timing_score",
    ]:
        return fail("route-scorecard-samples.json score fields mismatch")
    samples = data.get("samples", [])
    if len(samples) < 6:
        return fail("route-scorecard-samples.json must include at least 6 samples")
    ids = set()
    seen_roles = set()
    for item in samples:
        sample_id = item.get("id")
        if not sample_id or sample_id in ids:
            return fail("route-scorecard-samples.json has missing or duplicate id")
        ids.add(sample_id)
        role = item.get("expected_role")
        if role not in roles:
            return fail(f"route-scorecard-samples.json invalid role: {sample_id}")
        seen_roles.add(role)
        if item.get("expected_verdict") not in {"押主线", "保留备选", "弃用"}:
            return fail(f"route-scorecard-samples.json invalid verdict: {sample_id}")
        for key in ["input", "required_terms"]:
            if not item.get(key):
                return fail(f"route-scorecard-samples.json missing {key}: {sample_id}")
    if seen_roles != set(roles):
        return fail("route-scorecard-samples.json must cover all roles")
    result = subprocess.run(
        [sys.executable, "-B", "scripts/evaluate_route_scorecard.py", "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip(), file=sys.stderr)
    if result.returncode != 0:
        return fail("route-scorecard sample script check failed")
    print(f"PASS route-scorecard samples: {len(samples)}")
    return 0


def validate_route_switch_samples():
    samples_path = ROOT / "docs" / "evals" / "route-switch-samples.json"
    data = json.loads(samples_path.read_text(encoding="utf-8"))
    actions = data.get("actions", [])
    expected_actions = ["continue", "narrow_claim", "switch_route", "pause_spread"]
    if actions != expected_actions:
        return fail("route-switch-samples.json actions mismatch")
    samples = data.get("samples", [])
    if len(samples) < 7:
        return fail("route-switch-samples.json must include at least 7 samples")
    ids = set()
    seen = set()
    for item in samples:
        sample_id = item.get("id")
        if not sample_id or sample_id in ids:
            return fail("route-switch-samples.json has missing or duplicate id")
        ids.add(sample_id)
        action = item.get("expected_action")
        if action not in actions:
            return fail(f"route-switch-samples.json invalid action: {sample_id}")
        seen.add(action)
        for key in ["input", "required_terms"]:
            if not item.get(key):
                return fail(f"route-switch-samples.json missing {key}: {sample_id}")
    if seen != set(actions):
        return fail("route-switch-samples.json must cover all actions")
    result = subprocess.run(
        [sys.executable, "-B", "scripts/evaluate_route_switches.py", "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip(), file=sys.stderr)
    if result.returncode != 0:
        return fail("route switch sample script check failed")
    print(f"PASS route-switch samples: {len(samples)}")
    return 0


def validate_quality_rubric():
    rubric_path = ROOT / "docs" / "evals" / "output-quality-rubric.json"
    rubric = json.loads(rubric_path.read_text(encoding="utf-8"))
    dimensions = rubric.get("dimensions", [])
    if len(dimensions) < 8:
        return fail("output-quality-rubric.json must include at least 8 dimensions")
    if rubric.get("passing_score") != 80 or rubric.get("max_score") != 100:
        return fail("output-quality-rubric.json score thresholds mismatch")
    ids = set()
    total_weight = 0
    for item in dimensions:
        dimension_id = item.get("id", "")
        if not re.fullmatch(r"[a-z0-9_]+", dimension_id) or dimension_id in ids:
            return fail(f"output-quality-rubric.json invalid or duplicate dimension id: {dimension_id}")
        ids.add(dimension_id)
        weight = item.get("weight")
        if not isinstance(weight, int) or weight <= 0:
            return fail(f"output-quality-rubric.json invalid weight: {dimension_id}")
        total_weight += weight
        for key in ["name", "description", "positive_indicators", "hard_fail_conditions"]:
            if not item.get(key):
                return fail(f"output-quality-rubric.json missing {key}: {dimension_id}")
    if total_weight != 100:
        return fail(f"output-quality-rubric.json weights must sum to 100, got {total_weight}")
    if len(rubric.get("global_hard_fails", [])) < 5:
        return fail("output-quality-rubric.json needs at least 5 global hard fails")
    result = subprocess.run(
        [sys.executable, "-B", "scripts/evaluate_quality_rubric.py", "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip(), file=sys.stderr)
    if result.returncode != 0:
        return fail("quality rubric script check failed")
    print(f"PASS output-quality-rubric dimensions: {len(dimensions)}")
    return 0


def validate_post_launch_samples():
    samples_path = ROOT / "docs" / "evals" / "post-launch-samples.json"
    data = json.loads(samples_path.read_text(encoding="utf-8"))
    decisions = data.get("decisions", [])
    expected_decisions = ["continue", "narrow_claim", "switch_route", "pause_spread"]
    if decisions != expected_decisions:
        return fail("post-launch-samples.json decisions mismatch")
    samples = data.get("samples", [])
    if len(samples) < 6:
        return fail("post-launch-samples.json must include at least 6 samples")
    ids = set()
    seen = set()
    for item in samples:
        sample_id = item.get("id")
        if not sample_id or sample_id in ids:
            return fail("post-launch-samples.json has missing or duplicate id")
        ids.add(sample_id)
        decision = item.get("expected_decision")
        if decision not in decisions:
            return fail(f"post-launch-samples.json invalid decision: {sample_id}")
        seen.add(decision)
        for key in ["window", "input", "required_terms"]:
            if not item.get(key):
                return fail(f"post-launch-samples.json missing {key}: {sample_id}")
    if seen != set(decisions):
        return fail("post-launch-samples.json must cover all decisions")
    result = subprocess.run(
        [sys.executable, "-B", "scripts/evaluate_post_launch_samples.py", "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip(), file=sys.stderr)
    if result.returncode != 0:
        return fail("post-launch sample script check failed")
    print(f"PASS post-launch samples: {len(samples)}")
    return 0


def validate_decision_learning_samples():
    samples_path = ROOT / "docs" / "evals" / "decision-learning-samples.json"
    data = json.loads(samples_path.read_text(encoding="utf-8"))
    actions = data.get("actions", [])
    expected_actions = ["keep_route", "update_evidence", "ban_phrase", "raise_threshold", "update_kol_record"]
    if actions != expected_actions:
        return fail("decision-learning-samples.json actions mismatch")
    samples = data.get("samples", [])
    if len(samples) < 7:
        return fail("decision-learning-samples.json must include at least 7 samples")
    ids = set()
    seen = set()
    for item in samples:
        sample_id = item.get("id")
        if not sample_id or sample_id in ids:
            return fail("decision-learning-samples.json has missing or duplicate id")
        ids.add(sample_id)
        action = item.get("expected_action")
        if action not in actions:
            return fail(f"decision-learning-samples.json invalid action: {sample_id}")
        seen.add(action)
        for key in ["input", "required_terms"]:
            if not item.get(key):
                return fail(f"decision-learning-samples.json missing {key}: {sample_id}")
    if seen != set(actions):
        return fail("decision-learning-samples.json must cover all actions")
    result = subprocess.run(
        [sys.executable, "-B", "scripts/evaluate_decision_learning.py", "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip(), file=sys.stderr)
    if result.returncode != 0:
        return fail("decision-learning sample script check failed")
    print(f"PASS decision-learning samples: {len(samples)}")
    return 0


def validate_risk_ledger_samples():
    samples_path = ROOT / "docs" / "evals" / "risk-ledger-samples.json"
    data = json.loads(samples_path.read_text(encoding="utf-8"))
    priorities = data.get("priorities", [])
    impacts = data.get("route_impacts", [])
    statuses = data.get("fact_statuses", [])
    expected_priorities = ["P0", "P1", "P2", "P3"]
    expected_impacts = ["继续", "缩窄", "切换", "暂停"]
    expected_statuses = ["known", "inferred", "needs_verification"]
    if priorities != expected_priorities:
        return fail("risk-ledger-samples.json priorities mismatch")
    if impacts != expected_impacts:
        return fail("risk-ledger-samples.json route impacts mismatch")
    if statuses != expected_statuses:
        return fail("risk-ledger-samples.json fact statuses mismatch")
    samples = data.get("samples", [])
    if len(samples) < 8:
        return fail("risk-ledger-samples.json must include at least 8 samples")
    ids = set()
    seen_priorities = set()
    seen_impacts = set()
    for item in samples:
        sample_id = item.get("id")
        if not sample_id or sample_id in ids:
            return fail("risk-ledger-samples.json has missing or duplicate id")
        ids.add(sample_id)
        priority = item.get("expected_priority")
        impact = item.get("expected_route_impact")
        if priority not in priorities:
            return fail(f"risk-ledger-samples.json invalid priority: {sample_id}")
        if impact not in impacts:
            return fail(f"risk-ledger-samples.json invalid route impact: {sample_id}")
        seen_priorities.add(priority)
        seen_impacts.add(impact)
        for key in ["input", "required_terms"]:
            if not item.get(key):
                return fail(f"risk-ledger-samples.json missing {key}: {sample_id}")
    if seen_priorities != set(priorities):
        return fail("risk-ledger-samples.json must cover all priorities")
    if seen_impacts != set(impacts):
        return fail("risk-ledger-samples.json must cover all route impacts")
    result = subprocess.run(
        [sys.executable, "-B", "scripts/evaluate_risk_ledger.py", "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip(), file=sys.stderr)
    if result.returncode != 0:
        return fail("risk-ledger sample script check failed")
    print(f"PASS risk-ledger samples: {len(samples)}")
    return 0


def validate_decision_card_samples():
    samples_path = ROOT / "docs" / "evals" / "launch-decision-card-samples.json"
    data = json.loads(samples_path.read_text(encoding="utf-8"))
    valid = data.get("valid", [])
    invalid = data.get("invalid", [])
    if len(valid) < 1 or len(invalid) < 1:
        return fail("launch-decision-card-samples.json must include valid and invalid samples")
    ids = set()
    for group_name, group in [("valid", valid), ("invalid", invalid)]:
        for item in group:
            sample_id = item.get("id")
            if not sample_id or sample_id in ids:
                return fail("launch-decision-card-samples.json has missing or duplicate id")
            ids.add(sample_id)
            if not isinstance(item.get("payload"), dict):
                return fail(f"launch-decision-card-samples.json missing payload: {group_name}/{sample_id}")
    result = subprocess.run(
        [sys.executable, "-B", "scripts/validate_decision_output.py", "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip(), file=sys.stderr)
    if result.returncode != 0:
        return fail("decision-card sample script check failed")
    print(f"PASS launch-decision-card samples: {len(valid) + len(invalid)}")
    return 0


def validate_internal_links():
    result = subprocess.run(
        [sys.executable, "-B", "scripts/check_internal_links.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip(), file=sys.stderr)
    if result.returncode != 0:
        return fail("internal link check failed")
    print("PASS internal links and path references")
    return 0


def validate_script_safety():
    result = subprocess.run(
        [sys.executable, "-B", "scripts/audit_script_safety.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip(), file=sys.stderr)
    if result.returncode != 0:
        return fail("script safety audit failed")
    print("PASS script safety audit")
    return 0


def validate_release_manifest():
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    manifest_path = ROOT / "RELEASE-MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("version") != version:
        return fail("RELEASE-MANIFEST.json version does not match VERSION")
    for key in ["network_required", "secrets_required", "install_hooks"]:
        if manifest.get(key) is not False:
            return fail(f"RELEASE-MANIFEST.json must set {key}=false")
    publish = manifest.get("publish", {})
    if set(publish.get("platforms", [])) != {"codex", "clawhub", "skillhub"}:
        return fail("RELEASE-MANIFEST.json publish platforms mismatch")
    if set(publish.get("trust_documents", [])) != {"CHANGELOG.md", "SECURITY.md", "RELEASE-MANIFEST.json", "RELEASE-VALIDATION.json"}:
        return fail("RELEASE-MANIFEST.json trust documents mismatch")
    package_builder = publish.get("package_builder", "")
    if not package_builder or not (ROOT / package_builder).exists():
        return fail("RELEASE-MANIFEST.json publish package_builder missing")
    if publish.get("runtime_capabilities") != "docs/runtime-capabilities.json":
        return fail("RELEASE-MANIFEST.json runtime capabilities path mismatch")
    if publish.get("live_release_gate") != "docs/evals/live-release-status.json":
        return fail("RELEASE-MANIFEST.json live release gate path mismatch")
    hermes = publish.get("personal_packages", {}).get("hermes", {})
    expected_hermes = {
        "profile": "personal_full",
        "package_name": f"hermes-personal-china-marketing-copilot-v{version}.zip",
        "install_target": "~/.hermes/skills/china-marketing-copilot/",
        "network_mode": "offline_first",
    }
    if hermes != expected_hermes:
        return fail("RELEASE-MANIFEST.json Hermes personal package mismatch")
    evidence_ledger = json.loads((ROOT / "docs/evidence-ledger.json").read_text(encoding="utf-8"))
    expected_status_counts = {"verified": 0, "partial": 0, "missing": 0}
    for source in evidence_ledger.get("sources", []):
        status = source.get("provenance_status")
        if status in expected_status_counts:
            expected_status_counts[status] += 1
    expected_provenance = {
        "ledger": "docs/evidence-ledger.json",
        "schema": "schemas/evidence-ledger.schema.json",
        "sources": len(evidence_ledger.get("sources", [])),
        "status_counts": expected_status_counts,
        "release_claim": "provenance_inventory_only",
    }
    if manifest.get("evidence_provenance") != expected_provenance:
        return fail("RELEASE-MANIFEST.json evidence provenance summary mismatch")
    counts = manifest.get("eval_counts", {})
    expected_counts = {
        "trigger_queries": len(json.loads((ROOT / "docs/evals/trigger-queries.json").read_text(encoding="utf-8")).get("queries", [])),
        "output_mode_samples": len(json.loads((ROOT / "docs/evals/output-mode-samples.json").read_text(encoding="utf-8")).get("samples", [])),
        "audience_layering_samples": len(json.loads((ROOT / "docs/evals/audience-layering-samples.json").read_text(encoding="utf-8")).get("samples", [])),
        "freshness_claim_samples": len(json.loads((ROOT / "docs/evals/freshness-claim-samples.json").read_text(encoding="utf-8")).get("samples", [])),
        "evidence_claim_samples": len(json.loads((ROOT / "docs/evals/evidence-claim-samples.json").read_text(encoding="utf-8")).get("samples", [])),
        "decision_package_samples": len(json.loads((ROOT / "docs/evals/decision-package-samples.json").read_text(encoding="utf-8")).get("samples", [])),
        "executive_memo_samples": len(json.loads((ROOT / "docs/evals/executive-memo-samples.json").read_text(encoding="utf-8")).get("samples", [])),
        "route_scorecard_samples": len(json.loads((ROOT / "docs/evals/route-scorecard-samples.json").read_text(encoding="utf-8")).get("samples", [])),
        "route_switch_samples": len(json.loads((ROOT / "docs/evals/route-switch-samples.json").read_text(encoding="utf-8")).get("samples", [])),
        "execution_gate_samples": len(json.loads((ROOT / "docs/evals/execution-gate-samples.json").read_text(encoding="utf-8")).get("samples", [])),
        "post_launch_samples": len(json.loads((ROOT / "docs/evals/post-launch-samples.json").read_text(encoding="utf-8")).get("samples", [])),
        "decision_learning_samples": len(json.loads((ROOT / "docs/evals/decision-learning-samples.json").read_text(encoding="utf-8")).get("samples", [])),
        "risk_ledger_samples": len(json.loads((ROOT / "docs/evals/risk-ledger-samples.json").read_text(encoding="utf-8")).get("samples", [])),
        "decision_card_samples": (
            len(json.loads((ROOT / "docs/evals/launch-decision-card-samples.json").read_text(encoding="utf-8")).get("valid", []))
            + len(json.loads((ROOT / "docs/evals/launch-decision-card-samples.json").read_text(encoding="utf-8")).get("invalid", []))
        ),
        "marketing_tasks": count_marketing_rows(),
        "negative_signal_samples": len(parse_markdown_table(ROOT / "docs/evals/negative-signal-samples.md", 6)),
        "negative_signal_adversarial_samples": len(
            json.loads((ROOT / "docs/evals/negative-signal-adversarial-samples.json").read_text(encoding="utf-8")).get("samples", [])
        ),
        "negative_propagation_samples": len(
            json.loads((ROOT / "docs/evals/negative-propagation-samples.json").read_text(encoding="utf-8")).get("samples", [])
        ),
        "golden_examples": len(list((ROOT / "assets/examples").glob("*.md"))),
        "golden_example_assertion_sets": len(json.loads((ROOT / "docs/evals/golden-example-assertions.json").read_text(encoding="utf-8")).get("samples", [])),
        "route_files": len(list((ROOT / "docs/routes").glob("*.md"))),
        "quality_rubric_dimensions": len(json.loads((ROOT / "docs/evals/output-quality-rubric.json").read_text(encoding="utf-8")).get("dimensions", [])),
        "cross_agent_benchmark_cases": len(
            json.loads((ROOT / "docs/evals/cross-agent-benchmark.json").read_text(encoding="utf-8")).get("cases", [])
        ),
        "cross_agent_live_results": json.loads(
            (ROOT / "docs/evals/live-release-status.json").read_text(encoding="utf-8")
        ).get("run_records", 0),
        "legacy_compatibility_cases": len(
            json.loads((ROOT / "docs/evals/legacy-compatibility-samples.json").read_text(encoding="utf-8")).get("cases", [])
        ),
        "legacy_compatibility_live_results": 0,
    }
    for key, value in expected_counts.items():
        if counts.get(key) != value:
            return fail(f"RELEASE-MANIFEST.json count mismatch: {key} expected {value}, got {counts.get(key)}")
    result = subprocess.run(
        [sys.executable, "-B", "scripts/build_release_manifest.py", "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip(), file=sys.stderr)
    if result.returncode != 0:
        return fail("release manifest check failed")
    quality_gate = manifest.get("quality_gate", {})
    if quality_gate.get("rubric") != "docs/evals/output-quality-rubric.json":
        return fail("RELEASE-MANIFEST.json quality gate missing rubric path")
    if quality_gate.get("passing_score") != 80 or quality_gate.get("max_score") != 100:
        return fail("RELEASE-MANIFEST.json quality gate score mismatch")
    validation = manifest.get("validation", {})
    expected_validation = {
        "report": "RELEASE-VALIDATION.json",
        "command": "python3 -B scripts/validate_skill_pack.py --write-report",
        "semantics": "actual_run_results",
        "live_release_status": "docs/evals/live-release-status.json",
    }
    if validation != expected_validation:
        return fail("RELEASE-MANIFEST.json validation contract mismatch")
    print("PASS RELEASE-MANIFEST.json")
    return 0


def validate_release_validation_report():
    if WRITING_REPORT:
        print("PASS RELEASE-VALIDATION.json refresh mode")
        return 0
    report = json.loads((ROOT / REPORT_FILENAME).read_text(encoding="utf-8"))
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if report.get("version") != version:
        return fail("RELEASE-VALIDATION.json version mismatch")
    if report.get("source_fingerprint_sha256") != source_fingerprint():
        return fail("RELEASE-VALIDATION.json source fingerprint is stale")
    summary = report.get("summary", {})
    if summary.get("failed") != 0 or not summary.get("passed"):
        return fail("RELEASE-VALIDATION.json reports failed or missing checks")
    print(f"PASS RELEASE-VALIDATION.json: {summary['passed']} checks")
    return 0


def validate_publish_package_builder():
    for platform in ["all", "hermes-personal"]:
        result = subprocess.run(
            [sys.executable, "-B", "scripts/build_publish_package.py", "--platform", platform, "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.stdout.strip():
            print(result.stdout.strip())
        if result.stderr.strip():
            print(result.stderr.strip(), file=sys.stderr)
        if result.returncode != 0:
            return fail(f"publish package builder check failed: {platform}")
    print("PASS publish package builder: public runtime + Hermes personal full")
    return 0


def validate_release_artifacts():
    result = subprocess.run(
        [sys.executable, "-B", "scripts/verify_release_artifacts.py", "--build-temp"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip(), file=sys.stderr)
    if result.returncode != 0:
        return fail("release artifact verification failed")
    print("PASS release artifact verification")
    return 0


def parse_markdown_table(path, columns):
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) != columns or cells[0] in {"ID", "----"}:
            continue
        if not cells[0] or cells[0].startswith("-"):
            continue
        rows.append(cells)
    return rows


def validate_marketing_eval():
    eval_path = ROOT / "docs" / "evals" / "marketing-task-samples.md"
    rows = parse_markdown_table(eval_path, 8)
    if len(rows) < 24:
        return fail("marketing-task-samples.md must include at least 24 task rows")
    ids = set()
    allowed_types = {"上市决策", "策略诊断", "信息架构", "渠道KOL", "执行质检", "风控评估", "风险评估", "竞品洞察", "创意策划", "新品类破局", "负面预警", "正式审核", "数据导入", "平台兼容", "平台发布", "质量评分", "证据时效", "证据主张", "战情复盘", "决策单验收"}
    for cells in rows:
        sample_id, task_type, _category, _prompt, required_files, required_output, risk, pass_standard = cells
        if sample_id in ids:
            return fail(f"duplicate marketing eval id: {sample_id}")
        ids.add(sample_id)
        if task_type not in allowed_types:
            return fail(f"unknown marketing eval task type: {task_type}")
        if not required_output or not risk or not pass_standard:
            return fail(f"marketing eval row missing scoring fields: {sample_id}")
        for rel in re.findall(r"(?:docs|knowledge-base|assets|schemas|SKILL\.md)[^; ]*", required_files):
            if rel == "SKILL.md":
                check_path = ROOT / rel
            else:
                check_path = ROOT / rel.rstrip("；,，")
            if not check_path.exists():
                return fail(f"marketing eval references missing file: {sample_id} -> {rel}")
    print(f"PASS marketing-task eval rows: {len(rows)}")
    return 0


def count_marketing_rows():
    return len(parse_markdown_table(ROOT / "docs" / "evals" / "marketing-task-samples.md", 8))


def validate_release_version():
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        return fail("VERSION must use semantic version format x.y.z")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    if f"`v{version}`" not in readme or f"`{version}`" not in readme:
        return fail("README.md missing current release version")
    print(f"PASS release version: {version}")
    return 0


def scan_patterns(label, patterns):
    hits = []
    for path in iter_text_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        for name, pattern in patterns:
            if pattern.search(text):
                rel = path.relative_to(ROOT)
                hits.append(f"{rel}: {name}")
    if hits:
        return fail(f"{label}: " + "; ".join(hits[:10]))
    print(f"PASS {label}")
    return 0


def run_negative_eval():
    result = subprocess.run(
        [sys.executable, "-B", "scripts/evaluate_negative_signals.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip(), file=sys.stderr)
    if result.returncode != 0:
        return fail("negative-signal eval failed")
    print("PASS negative-signal eval")
    return 0


def validate_forbidden_patterns():
    return scan_patterns("legacy forced-scan wording", FORBIDDEN_PATTERNS)


def validate_secret_patterns():
    return scan_patterns("secret scan", SECRET_PATTERNS)


def source_fingerprint():
    digest = hashlib.sha256()
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        if rel.name == REPORT_FILENAME:
            continue
        if any(part == ".git" or part == "dist" or part.startswith("dist-v") for part in rel.parts):
            continue
        if "__pycache__" in rel.parts or path.name == ".DS_Store":
            continue
        digest.update(str(rel).encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def git_state():
    commit_result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    status_result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return {
        "commit": commit_result.stdout.strip() if commit_result.returncode == 0 else "unknown",
        "working_tree_dirty": bool(status_result.stdout.strip()) if status_result.returncode == 0 else None,
    }


def write_validation_report(path, check_results):
    state = git_state()
    payload = {
        "version": (ROOT / "VERSION").read_text(encoding="utf-8").strip(),
        "validated_at": datetime.now(timezone.utc).isoformat(),
        "source_fingerprint_sha256": source_fingerprint(),
        "git_commit": state["commit"],
        "working_tree_dirty": state["working_tree_dirty"],
        "validator": "scripts/validate_skill_pack.py",
        "checks": [
            {"name": name, "status": "passed" if status == 0 else "failed"}
            for name, status in check_results
        ],
        "summary": {
            "passed": sum(1 for _name, status in check_results if status == 0),
            "failed": sum(1 for _name, status in check_results if status != 0),
        },
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote validation report: {path.relative_to(ROOT)}")


def main():
    global WRITING_REPORT
    parser = argparse.ArgumentParser(description="Validate the China marketing skill package")
    parser.add_argument("--write-report", action="store_true", help="write an evidence-backed release validation report")
    parser.add_argument("--report-path", default=REPORT_FILENAME, help="validation report path relative to the repository")
    args = parser.parse_args()
    WRITING_REPORT = args.write_report

    checks = [
        validate_skill_metadata,
        validate_skill_router_shape,
        validate_platform_listing,
        validate_readme_landing,
        validate_platform_publish_fields,
        validate_trust_documents,
        validate_required_paths,
        validate_json,
        validate_data_sources,
        validate_runtime_capabilities,
        validate_evidence_ledger,
        validate_launch_decision_schema,
        validate_trigger_queries,
        validate_cross_agent_benchmark,
        validate_live_release_status,
        validate_local_installer,
        validate_legacy_compatibility,
        validate_negative_propagation,
        validate_golden_examples,
        validate_output_modes,
        validate_audience_layering,
        validate_freshness_claims,
        validate_evidence_claims,
        validate_decision_package_samples,
        validate_executive_memo_samples,
        validate_route_scorecard_samples,
        validate_route_switch_samples,
        validate_execution_gate_samples,
        validate_quality_rubric,
        validate_post_launch_samples,
        validate_decision_learning_samples,
        validate_risk_ledger_samples,
        validate_decision_card_samples,
        validate_internal_links,
        validate_script_safety,
        validate_knowledge_claims,
        validate_marketing_eval,
        validate_release_manifest,
        validate_release_validation_report,
        validate_publish_package_builder,
        validate_release_artifacts,
        validate_release_version,
        validate_forbidden_patterns,
        validate_secret_patterns,
        run_negative_eval,
    ]
    check_results = []
    for check in checks:
        status = check()
        check_results.append((check.__name__, status))
    failures = sum(status for _name, status in check_results)
    if failures:
        print(f"skill pack validation failed: {failures} check(s)")
        return 1
    if args.write_report:
        report_path = Path(args.report_path)
        if not report_path.is_absolute():
            report_path = ROOT / report_path
        write_validation_report(report_path, check_results)
    print("skill pack validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
