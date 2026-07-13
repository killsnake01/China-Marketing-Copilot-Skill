#!/usr/bin/env python3
"""Check repository-local links and path references before publishing."""
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent

SKIP_DIRS = {".git", "dist", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
TEXT_SUFFIXES = {".md", ".yaml", ".yml", ".json", ".py", ".txt", ".gitignore"}

MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]\n]+\]\(([^)\n]+)\)")
PATH_TOKEN_RE = re.compile(
    r"(?<![A-Za-z0-9_./-])"
    r"("
    r"(?:docs|assets|schemas|scripts|agents)/(?:[A-Za-z0-9._~+%-]+/)*[A-Za-z0-9._~+%-]+"
    r"(?:#[A-Za-z0-9._~+%:-]+)?"
    r"|(?:README|SKILL|CHANGELOG|SECURITY)\.md"
    r"|RELEASE-MANIFEST\.json"
    r"|VERSION"
    r")"
    r"(?![A-Za-z0-9_./-])"
)
EXTERNAL_SCHEME_RE = re.compile(r"^[a-z][a-z0-9+.-]*:", re.I)


@dataclass(frozen=True)
class Finding:
    source: Path
    line: int
    target: str
    kind: str


def iter_text_files():
    for path in ROOT.rglob("*"):
        if any(part in SKIP_DIRS or part.startswith("dist-v") for part in path.relative_to(ROOT).parts):
            continue
        if path.is_file() and (path.suffix in TEXT_SUFFIXES or path.name == ".gitignore"):
            yield path


def line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def markdown_target(raw: str) -> str:
    target = raw.strip()
    if target.startswith("<") and ">" in target:
        target = target[1:].split(">", 1)[0]
    else:
        target = target.split()[0] if target.split() else ""
    return target.strip()


def is_external_or_anchor(target: str) -> bool:
    return not target or target.startswith("#") or bool(EXTERNAL_SCHEME_RE.match(target))


def strip_fragment(target: str) -> str:
    return unquote(target.split("#", 1)[0]).strip()


def resolve_candidates(source: Path, target: str, root_relative_only: bool) -> list[Path]:
    path_part = strip_fragment(target)
    if not path_part:
        return []
    if Path(path_part).is_absolute():
        return [ROOT / path_part.lstrip("/")]
    if root_relative_only:
        return [ROOT / path_part]
    candidates = [source.parent / path_part, ROOT / path_part]
    unique = []
    seen = set()
    for candidate in candidates:
        key = candidate.resolve(strict=False)
        if key not in seen:
            unique.append(candidate)
            seen.add(key)
    return unique


def target_exists(source: Path, target: str, root_relative_only: bool) -> bool:
    if is_external_or_anchor(target):
        return True
    candidates = resolve_candidates(source, target, root_relative_only)
    return bool(candidates) and any(candidate.exists() for candidate in candidates)


def scan_file(path: Path) -> tuple[list[Finding], int]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    findings: list[Finding] = []
    checked = 0

    for match in MARKDOWN_LINK_RE.finditer(text):
        target = markdown_target(match.group(1))
        if is_external_or_anchor(target):
            continue
        checked += 1
        if not target_exists(path, target, root_relative_only=False):
            findings.append(Finding(path, line_number(text, match.start()), target, "markdown-link"))

    for match in PATH_TOKEN_RE.finditer(text):
        target = match.group(1)
        checked += 1
        if not target_exists(path, target, root_relative_only=True):
            findings.append(Finding(path, line_number(text, match.start()), target, "path-token"))

    return findings, checked


def main() -> int:
    global ROOT
    parser = argparse.ArgumentParser(description="Check internal links and path references.")
    parser.add_argument("--quiet", action="store_true", help="only print failures")
    parser.add_argument("--root", help="alternate package root to inspect")
    args = parser.parse_args()
    if args.root:
        ROOT = Path(args.root).resolve()

    all_findings: list[Finding] = []
    checked_count = 0
    for path in iter_text_files():
        findings, checked = scan_file(path)
        all_findings.extend(findings)
        checked_count += checked

    deduped = []
    seen = set()
    for finding in all_findings:
        key = (finding.source, finding.line, finding.target, finding.kind)
        if key not in seen:
            deduped.append(finding)
            seen.add(key)

    if deduped:
        print("FAIL internal reference check")
        for finding in deduped[:50]:
            rel = finding.source.relative_to(ROOT)
            print(f"{rel}:{finding.line}: missing {finding.kind}: {finding.target}")
        if len(deduped) > 50:
            print(f"... {len(deduped) - 50} more finding(s)")
        return 1

    if not args.quiet:
        print(f"internal reference check passed: {checked_count} reference(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
