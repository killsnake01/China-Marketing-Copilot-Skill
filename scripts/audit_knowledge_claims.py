#!/usr/bin/env python3
"""Audit bundled knowledge for unsupported absolute claims and unsafe examples."""
from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_ROOT = ROOT / "knowledge-base"

HIGH_RISK_PATTERNS = [
    re.compile(pattern)
    for pattern in (
        r"唯一",
        r"最强",
        r"天花板",
        r"断代领先",
        r"无敌",
        r"极高",
        r"(?:全球|中国市场|出货量|市场份额)[^。|]{0,24}第一",
        r"倒数第一",
    )
]
EVIDENCE_MARKERS = ("[来源观点]", "[历史数据]", "[待验证]")
RISK_CONTEXT_MARKERS = (
    "风险",
    "禁止",
    "避免",
    "不可",
    "慎用",
    "禁用",
    "疲劳",
    "不再",
    "复核",
)
UNSAFE_EXAMPLE_PATTERNS = [
    re.compile(r"(?:KOL|B站|UP主)\s*XX", re.I),
    re.compile(r"技术事实核查\s*:\s*✅"),
]


def knowledge_findings() -> list[str]:
    findings: list[str] = []
    for path in sorted(KNOWLEDGE_ROOT.rglob("*.md")):
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not any(pattern.search(line) for pattern in HIGH_RISK_PATTERNS):
                continue
            if any(marker in line for marker in EVIDENCE_MARKERS):
                continue
            if any(marker in line for marker in RISK_CONTEXT_MARKERS):
                continue
            findings.append(f"{path.relative_to(ROOT)}:{line_number}: unsupported high-risk claim: {line.strip()}")
    return findings


def example_findings() -> list[str]:
    path = ROOT / "quickstart-example.md"
    findings: list[str] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        for pattern in UNSAFE_EXAMPLE_PATTERNS:
            if pattern.search(line):
                findings.append(f"{path.name}:{line_number}: unsafe example placeholder: {line.strip()}")
    return findings


def main() -> int:
    findings = knowledge_findings() + example_findings()
    if findings:
        print("knowledge claim audit failed")
        for finding in findings:
            print(finding)
        return 1
    print("knowledge claim audit passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
