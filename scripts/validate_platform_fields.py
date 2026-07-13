#!/usr/bin/env python3
"""Validate platform listing fields against public copy and release version."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIELDS_PATH = ROOT / "docs" / "platform-publish-fields.json"
PLATFORMS = ("github", "clawhub", "skillhub", "codex", "openclaw_hermes")


def fail(message: str) -> int:
    print(f"FAIL {message}")
    return 1


def load_fields() -> dict:
    return json.loads(FIELDS_PATH.read_text(encoding="utf-8"))


def version() -> str:
    return (ROOT / "VERSION").read_text(encoding="utf-8").strip()


def require_terms(text: str, terms: list[str], label: str) -> list[str]:
    return [f"{label} missing {term}" for term in terms if term not in text]


def validate_fields(data: dict) -> list[str]:
    findings: list[str] = []
    current = version()
    if data.get("version") != current:
        findings.append("platform fields version mismatch")
    if data.get("skill_name") != "china-marketing-copilot":
        findings.append("skill_name mismatch")
    if data.get("display_name") != "中国3C营销助手":
        findings.append("display_name mismatch")
    if data.get("slug") != "china-marketing-copilot":
        findings.append("slug mismatch")
    short_description = data.get("short_description", "")
    if not short_description or len(short_description) > 80:
        findings.append("short_description should be nonempty and no more than 80 characters")
    if "中国3C上市决策系统" != data.get("positioning"):
        findings.append("positioning should preserve decision-system wording")
    if "上线决策" not in data.get("subtitle", ""):
        findings.append("subtitle missing 上线决策")
    if len(data.get("keywords", [])) < 6:
        findings.append("keywords should include at least 6 items")
    if len(data.get("first_screen_modules", [])) < 6:
        findings.append("first_screen_modules should include at least 6 items")

    platforms = data.get("platforms", {})
    for platform in PLATFORMS:
        item = platforms.get(platform)
        if not isinstance(item, dict):
            findings.append(f"missing platform fields: {platform}")
            continue
        if item.get("version_label") != f"v{current}":
            findings.append(f"{platform} version label mismatch")

    expected_packages = {
        "clawhub": f"clawhub-china-marketing-copilot-v{current}.zip",
        "skillhub": f"skillhub-china-marketing-copilot-v{current}.zip",
        "codex": f"codex-china-marketing-copilot-v{current}.zip",
        "openclaw_hermes": f"hermes-personal-china-marketing-copilot-v{current}.zip",
    }
    for platform, package_name in expected_packages.items():
        if platforms.get(platform, {}).get("package_name") != package_name:
            findings.append(f"{platform} package name mismatch")
    hermes = platforms.get("openclaw_hermes", {})
    if hermes.get("package_profile") != "personal_full":
        findings.append("openclaw_hermes package profile mismatch")
    if hermes.get("install_target") != "~/.hermes/skills/china-marketing-copilot/":
        findings.append("openclaw_hermes install target mismatch")

    copy_order = data.get("copy_order", [])
    required_order = [
        "positioning",
        "primary_promise",
        "first_screen_modules",
        "trial_prompts",
        "capability_boundaries",
        "trust_materials",
    ]
    if copy_order != required_order:
        findings.append("copy_order mismatch")
    return findings


def validate_public_copy(data: dict) -> list[str]:
    current = version()
    terms = [
        data["display_name"],
        data["positioning"],
        data["subtitle"],
        data["primary_promise"],
        f"v{current}",
        "上市决策包",
        "负面雷达",
        "上线闸门",
    ]
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    listing = (ROOT / "docs" / "platform-listing.md").read_text(encoding="utf-8")
    agent = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    findings: list[str] = []
    findings.extend(require_terms(readme, terms, "README.md"))
    findings.extend(require_terms(listing, terms[:-1], "docs/platform-listing.md"))
    findings.extend(require_terms(agent, [data["display_name"], "负面预警", "$china-marketing-copilot"], "agents/openai.yaml"))
    findings.extend(require_terms(skill, [data["display_name"], "上市决策包", "上线判断"], "SKILL.md"))
    if re.search(r"目录结构|脚本列表|发布包清理规则", readme):
        findings.append("README.md includes maintainer-only wording")
    if "docs/platform-publish-fields.json" not in listing:
        findings.append("docs/platform-listing.md should reference platform-publish-fields.json")
    if "docs/platform-publish-fields.json" not in (ROOT / "docs" / "maintainer-guide.md").read_text(encoding="utf-8"):
        findings.append("docs/maintainer-guide.md should reference platform-publish-fields.json")
    return findings


def main() -> int:
    data = load_fields()
    findings = validate_fields(data) + validate_public_copy(data)
    if findings:
        for finding in findings:
            print(f"FAIL {finding}")
        return 1
    print(
        "platform publish fields check passed: "
        + ", ".join(data.get("platforms", {}).keys())
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
