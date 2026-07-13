#!/usr/bin/env python3
"""Build platform-specific publish packages."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent

PUBLIC_PLATFORMS = ("codex", "clawhub", "skillhub")
OPTIONAL_PLATFORMS = ("hermes-personal",)
SUPPORTED_PLATFORMS = PUBLIC_PLATFORMS + OPTIONAL_PLATFORMS
COMMON_SKIP_DIRS = {".git", "dist", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
COMMON_SKIP_FILES = {".DS_Store"}
SOURCE_ONLY_PRIVATE_PATHS = {
    "docs/evals/cross-agent-benchmark.json",
    "docs/evals/legacy-compatibility-samples.json",
    "scripts/audit_evidence_ledger.py",
    "scripts/evaluate_cross_agent_runs.py",
    "scripts/evaluate_legacy_compatibility.py",
}
ROOT_FILES_BY_PLATFORM = {
    "codex": {"SKILL.md", "LICENSE", "VERSION"},
    "clawhub": {"SKILL.md", "LICENSE", "VERSION"},
    "skillhub": {"SKILL.md"},
    "hermes-personal": {
        "SKILL.md",
        "LICENSE",
        "VERSION",
        "quickstart-example.md",
    },
}
RUNTIME_EVAL_FILES = {
    "decision-learning-samples.json",
    "decision-package-samples.json",
    "evidence-claim-samples.json",
    "execution-gate-samples.json",
    "executive-memo-samples.json",
    "freshness-claim-samples.json",
    "launch-decision-card-samples.json",
    "negative-signal-adversarial-samples.json",
    "negative-propagation-samples.json",
    "negative-signal-samples.md",
    "output-quality-rubric.json",
    "post-launch-samples.json",
    "risk-ledger-samples.json",
    "route-scorecard-samples.json",
    "route-switch-samples.json",
}
RUNTIME_SCRIPT_FILES = {
    "evaluate_decision_learning.py",
    "evaluate_decision_package.py",
    "evaluate_evidence_claims.py",
    "evaluate_execution_gate.py",
    "evaluate_executive_memo.py",
    "evaluate_freshness_claims.py",
    "evaluate_negative_signals.py",
    "analyze_signal_batch.py",
    "evaluate_negative_propagation.py",
    "evaluate_post_launch_samples.py",
    "evaluate_quality_rubric.py",
    "evaluate_risk_ledger.py",
    "evaluate_route_scorecard.py",
    "evaluate_route_switches.py",
    "preprocess.py",
    "validate_decision_output.py",
}
COMMON_PACKAGE_REQUIRED_PATHS = [
    "SKILL.md",
    "agents/openai.yaml",
    "assets/launch-decision-card.md",
    "schemas/launch-decision.schema.json",
    "schemas/evidence-ledger.schema.json",
    "schemas/negative-signal-batch.schema.json",
    "docs/agent-router.md",
    "docs/data-index.md",
    "docs/data-sources.json",
    "docs/evidence-ledger.json",
    "docs/runtime-capabilities.json",
    "docs/routes/launch-decision.md",
    "docs/routes/creative-campaign.md",
    "docs/routes/post-launch-war-room.md",
    "docs/routes/output-quality.md",
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
    "docs/ecosystem/negative-signal-rules.json",
    "docs/evals/negative-signal-samples.md",
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
    "docs/evals/negative-signal-adversarial-samples.json",
    "docs/evals/negative-propagation-samples.json",
    "scripts/preprocess.py",
    "scripts/evaluate_negative_signals.py",
    "scripts/analyze_signal_batch.py",
    "scripts/evaluate_negative_propagation.py",
    "scripts/evaluate_execution_gate.py",
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
]
PLATFORM_REQUIRED_PATHS = {
    "codex": ["LICENSE", "VERSION"],
    "clawhub": ["LICENSE", "VERSION"],
    "skillhub": ["docs/package-license.txt"],
    "hermes-personal": [
        "LICENSE",
        "VERSION",
        "quickstart-example.md",
        "HERMES-PACKAGE.json",
        "assets/examples/ai-claim-review.md",
        "assets/examples/headphone-comment-analysis.md",
        "assets/examples/image-flagship-launch.md",
        "docs/evals/marketing-task-samples.md",
        "docs/evals/trigger-queries.json",
        "docs/evals/golden-example-assertions.json",
        "docs/evals/output-mode-samples.json",
        "docs/templates/new-category-playbook.md",
        "docs/templates/knowledge-base-structure.md",
        "knowledge-base/other/_index.md",
        "scripts/evaluate_golden_examples.py",
    ],
}


def version() -> str:
    return (ROOT / "VERSION").read_text(encoding="utf-8").strip()


def package_name(platform: str) -> str:
    if platform == "hermes-personal":
        return f"hermes-personal-china-marketing-copilot-v{version()}"
    return f"{platform}-china-marketing-copilot-v{version()}"


def should_skip(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    if any(part in COMMON_SKIP_DIRS for part in rel.parts):
        return True
    if any(part.startswith("dist-v") for part in rel.parts):
        return True
    if path.name in COMMON_SKIP_FILES:
        return True
    return False


def should_include(path: Path, platform: str) -> bool:
    rel = path.relative_to(ROOT)
    if should_skip(path):
        return False
    if rel.as_posix() in SOURCE_ONLY_PRIVATE_PATHS:
        return False
    if len(rel.parts) == 1:
        return rel.name in ROOT_FILES_BY_PLATFORM[platform]
    root = rel.parts[0]
    if platform == "hermes-personal":
        if root in {"agents", "assets", "knowledge-base", "schemas"}:
            return True
        if root == "scripts":
            return rel.name in RUNTIME_SCRIPT_FILES | {"evaluate_golden_examples.py"}
        if root != "docs":
            return False
        if rel.as_posix() in {
            "docs/agent-router.md",
            "docs/data-index.md",
            "docs/data-sources.json",
            "docs/evidence-ledger.json",
            "docs/runtime-capabilities.json",
        }:
            return True
        if len(rel.parts) < 3:
            return False
        section = rel.parts[1]
        if section == "routes":
            return rel.name != "platform-publish.md"
        if section in {"templates", "references", "ecosystem"}:
            return True
        if section == "evals":
            return rel.as_posix() not in SOURCE_ONLY_PRIVATE_PATHS
        return False
    if root in {"agents", "knowledge-base", "schemas"}:
        return True
    if root == "assets":
        return rel.as_posix() == "assets/launch-decision-card.md"
    if root == "scripts":
        return rel.name in RUNTIME_SCRIPT_FILES
    if root != "docs":
        return False
    if rel.as_posix() == "docs/package-license.txt":
        return platform == "skillhub"
    if rel.as_posix() in {
        "docs/agent-router.md",
        "docs/data-index.md",
        "docs/data-sources.json",
        "docs/evidence-ledger.json",
        "docs/runtime-capabilities.json",
    }:
        return True
    if len(rel.parts) < 3:
        return False
    section = rel.parts[1]
    if section == "templates":
        return rel.name != "knowledge-base-structure.md"
    if section in {"references", "ecosystem"}:
        return True
    if section == "routes":
        return rel.name != "platform-publish.md"
    if section == "evals":
        return rel.name in RUNTIME_EVAL_FILES
    return False


def copy_package_tree(destination: Path, platform: str) -> None:
    destination = destination.resolve()
    for path in ROOT.rglob("*"):
        resolved_path = path.resolve()
        if resolved_path == destination or destination in resolved_path.parents or not should_include(path, platform):
            continue
        if path.is_dir():
            continue
        rel = path.relative_to(ROOT)
        target = destination / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)


def read_frontmatter(text: str) -> tuple[dict[str, str], str]:
    match = re.match(r"^---\n(.*?)\n---\n?", text, re.S)
    if not match:
        raise ValueError("SKILL.md missing frontmatter")
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ": " in line:
            key, value = line.split(": ", 1)
            fields[key] = value.strip().strip('"')
    return fields, text[match.end():]


def patch_skillhub_frontmatter(package_dir: Path) -> None:
    skill_path = package_dir / "SKILL.md"
    fields, body = read_frontmatter(skill_path.read_text(encoding="utf-8"))
    frontmatter = {
        "name": fields.get("name", "china-marketing-copilot"),
        "slug": "china-marketing-copilot",
        "version": version(),
        "displayName": "中国3C营销助手",
        "description": fields.get("description", ""),
    }
    lines = ["---"] + [f"{key}: {value}" for key, value in frontmatter.items()] + ["---", ""]
    skill_path.write_text("\n".join(lines) + body, encoding="utf-8")


def patch_hermes_frontmatter(package_dir: Path) -> None:
    skill_path = package_dir / "SKILL.md"
    fields, body = read_frontmatter(skill_path.read_text(encoding="utf-8"))
    hermes_note = """## Hermes 个人全量版运行说明

- 通过 `skill_view(\"china-marketing-copilot\", \"相对路径\")` 按需读取包内资料。
- 先读取一个主任务路由和一个品类索引，再补充模板、生态资料或评测规则，避免一次加载全部文件。
- 没有网页或终端工具时继续使用离线知识库；涉及当前价格、排名、份额、新品参数或KOL近况时标注 `[待验证]`。
- 具备终端工具时，可通过 `${HERMES_SKILL_DIR}/scripts/` 下的脚本运行负面信号、证据、路线和决策单校验。

"""
    frontmatter = [
        "---",
        f"name: {fields.get('name', 'china-marketing-copilot')}",
        f"description: {fields.get('description', '')}",
        f"version: {version()}",
        "author: killsnake01",
        "metadata:",
        "  hermes:",
        "    tags: [china-marketing, china-3c, launch-strategy, risk-intelligence, offline-first]",
        "    category: marketing",
        "---",
        "",
    ]
    body = body.lstrip("\n")
    title = "# 中国3C营销助手\n\n"
    if body.startswith(title):
        body = title + hermes_note + body[len(title):]
    else:
        body = hermes_note + body
    skill_path.write_text("\n".join(frontmatter) + "\n" + body, encoding="utf-8")


def patch_hermes_runtime_evals(package_dir: Path) -> None:
    samples_path = package_dir / "docs/evals/marketing-task-samples.md"
    lines = samples_path.read_text(encoding="utf-8").splitlines()
    lines = [line for line in lines if not line.startswith("| M020 |")]
    samples_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def source_fingerprint(package_dir: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(package_dir.rglob("*")):
        if not path.is_file() or path.name == "HERMES-PACKAGE.json":
            continue
        rel = path.relative_to(package_dir).as_posix()
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def write_hermes_manifest(package_dir: Path) -> None:
    data_sources = json.loads((package_dir / "docs/data-sources.json").read_text(encoding="utf-8"))
    evidence_ledger = json.loads((package_dir / "docs/evidence-ledger.json").read_text(encoding="utf-8"))
    categories = data_sources.get("categories", [])
    provenance_status = {}
    for source in evidence_ledger.get("sources", []):
        status = source.get("provenance_status", "unknown")
        provenance_status[status] = provenance_status.get(status, 0) + 1
    files = [path for path in package_dir.rglob("*") if path.is_file() and path.name != "HERMES-PACKAGE.json"]
    manifest = {
        "profile": "hermes_personal_full",
        "version": version(),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "entrypoint": "SKILL.md",
        "install_target": "~/.hermes/skills/china-marketing-copilot/",
        "offline_first": True,
        "network_required": False,
        "dependencies": [],
        "source_fingerprint_sha256": source_fingerprint(package_dir),
        "content": {
            "files_excluding_manifest": len(files),
            "knowledge_files": len(list((package_dir / "knowledge-base").rglob("*.md"))),
            "routes": len(list((package_dir / "docs/routes").glob("*.md"))),
            "templates": len(list((package_dir / "docs/templates").glob("*.md"))),
            "references": len(list((package_dir / "docs/references").glob("*.md"))),
            "ecosystem_files": len(list((package_dir / "docs/ecosystem").glob("*"))),
            "evaluation_files": len(list((package_dir / "docs/evals").glob("*"))),
            "example_files": len(list((package_dir / "assets/examples").glob("*.md"))),
            "scripts": len(list((package_dir / "scripts").glob("*.py"))),
            "categories": [item.get("category") for item in categories],
            "category_status": {item.get("category"): item.get("status") for item in categories},
            "evidence_sources": len(evidence_ledger.get("sources", [])),
            "provenance_status": provenance_status,
        },
        "excluded_from_package": [
            "git_metadata",
            "generated_release_artifacts",
            "cache_files",
            "operating_system_metadata",
        ],
    }
    (package_dir / "HERMES-PACKAGE.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def validate_hermes_package(package_dir: Path) -> None:
    expected = {
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("*")
        if path.is_file() and should_include(path, "hermes-personal")
    }
    actual = {
        path.relative_to(package_dir).as_posix()
        for path in package_dir.rglob("*")
        if path.is_file() and path.name != "HERMES-PACKAGE.json"
    }
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise ValueError(f"hermes-personal content mismatch; missing={missing[:5]}, extra={extra[:5]}")

    skill_text = (package_dir / "SKILL.md").read_text(encoding="utf-8")
    required_terms = [
        f"version: {version()}",
        "metadata:\n  hermes:",
        "category: marketing",
        "${HERMES_SKILL_DIR}/scripts/",
        "Hermes 个人全量版运行说明",
    ]
    missing_terms = [term for term in required_terms if term not in skill_text]
    if missing_terms:
        raise ValueError(f"hermes-personal SKILL.md missing terms: {', '.join(missing_terms)}")

    forbidden_patterns = {
        "clawhub token": re.compile(r"clh_[A-Za-z0-9]{16,}"),
        "skillhub token": re.compile(r"skh_[A-Za-z0-9]{16,}"),
        "github token": re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
    }
    for path in package_dir.rglob("*"):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for label, pattern in forbidden_patterns.items():
            if pattern.search(text):
                raise ValueError(f"hermes-personal package contains {label}: {path.relative_to(package_dir)}")

    link_result = subprocess.run(
        [sys.executable, "-B", "scripts/check_internal_links.py", "--root", str(package_dir), "--quiet"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if link_result.returncode != 0:
        detail = link_result.stdout.strip() or link_result.stderr.strip()
        raise ValueError(f"hermes-personal package has broken references: {detail[:800]}")


def validate_package(package_dir: Path, platform: str) -> None:
    if platform == "hermes-personal":
        required_paths = ["SKILL.md", "docs/agent-router.md", "docs/data-index.md", "docs/data-sources.json"] + PLATFORM_REQUIRED_PATHS[platform]
    else:
        required_paths = COMMON_PACKAGE_REQUIRED_PATHS + PLATFORM_REQUIRED_PATHS[platform]
    missing = [rel for rel in required_paths if not (package_dir / rel).exists()]
    if missing:
        raise ValueError(f"{platform} package missing required paths: {', '.join(missing)}")

    forbidden_hits = []
    for path in package_dir.rglob("*"):
        rel = path.relative_to(package_dir)
        if any(part in COMMON_SKIP_DIRS for part in rel.parts) or path.name in COMMON_SKIP_FILES:
            forbidden_hits.append(str(rel))
    if forbidden_hits:
        raise ValueError(f"{platform} package contains forbidden files: {', '.join(forbidden_hits[:10])}")

    if platform != "hermes-personal":
        forbidden_runtime_paths = [
            "quickstart-example.md",
            "CONTRIBUTING.md",
            "docs/maintainer-guide.md",
            "docs/platform-listing.md",
            "docs/platform-publish-fields.json",
            "docs/routes/platform-publish.md",
            "scripts/build_publish_package.py",
            "scripts/build_release_manifest.py",
            "scripts/validate_skill_pack.py",
        ]
        for rel in forbidden_runtime_paths:
            if (package_dir / rel).exists():
                raise ValueError(f"{platform} package contains maintainer-only path: {rel}")

    if platform == "skillhub":
        fields, _body = read_frontmatter((package_dir / "SKILL.md").read_text(encoding="utf-8"))
        expected = {
            "name": "china-marketing-copilot",
            "slug": "china-marketing-copilot",
            "version": version(),
            "displayName": "中国3C营销助手",
        }
        for key, value in expected.items():
                if fields.get(key) != value:
                    raise ValueError(f"skillhub SKILL.md frontmatter mismatch: {key}")
    if platform == "hermes-personal":
        validate_hermes_package(package_dir)


def zip_package(package_dir: Path) -> Path:
    zip_path = package_dir.parent / f"{package_dir.name}.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(package_dir.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(package_dir))
    return zip_path


def build_platform(platform: str, output_dir: Path, output_format: str) -> tuple[Path, Optional[Path]]:
    package_dir = output_dir / package_name(platform)
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir(parents=True)
    copy_package_tree(package_dir, platform)
    if platform == "skillhub":
        patch_skillhub_frontmatter(package_dir)
    if platform == "hermes-personal":
        patch_hermes_frontmatter(package_dir)
        patch_hermes_runtime_evals(package_dir)
        write_hermes_manifest(package_dir)
    validate_package(package_dir, platform)

    zip_path = None
    if output_format in {"zip", "both"}:
        zip_path = zip_package(package_dir)
    if output_format == "zip":
        shutil.rmtree(package_dir)
    return package_dir, zip_path


def selected_platforms(value: str) -> list[str]:
    if value == "all":
        return list(PUBLIC_PLATFORMS)
    if value == "all-with-personal":
        return list(SUPPORTED_PLATFORMS)
    if value not in SUPPORTED_PLATFORMS:
        raise ValueError(f"unknown platform: {value}")
    return [value]


def main() -> int:
    parser = argparse.ArgumentParser(description="Build publish packages for external platforms.")
    parser.add_argument(
        "--platform",
        default="all",
        help="codex, clawhub, skillhub, hermes-personal, all, or all-with-personal",
    )
    parser.add_argument("--output", default="dist", help="output directory")
    parser.add_argument("--format", choices=["dir", "zip", "both"], default="both")
    parser.add_argument("--check", action="store_true", help="build in a temp directory and validate only")
    args = parser.parse_args()

    platforms = selected_platforms(args.platform)
    if args.check:
        with tempfile.TemporaryDirectory(prefix="china-marketing-publish-") as temp_dir:
            output_dir = Path(temp_dir)
            for platform in platforms:
                build_platform(platform, output_dir, "dir")
        print("publish package check passed: " + ", ".join(platforms))
        return 0

    output_dir = (ROOT / args.output).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    for platform in platforms:
        package_dir, zip_path = build_platform(platform, output_dir, args.format)
        print(f"{platform}: {package_dir}")
        if zip_path:
            print(f"{platform} zip: {zip_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
