#!/usr/bin/env python3
"""Audit evidence provenance coverage without requiring third-party packages."""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
LEDGER_PATH = ROOT / "docs/evidence-ledger.json"
DATA_SOURCES_PATH = ROOT / "docs/data-sources.json"
VALID_STATUSES = {"verified", "partial", "missing"}
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}(?:-\d{2})?$")
SOURCE_ID_PATTERN = re.compile(r"^SRC-[A-Z-]+-\d{3}$")
REQUIRED_FIELDS = {
    "source_id",
    "category",
    "source_type",
    "source_name",
    "publishers",
    "source_locators",
    "data_cutoff",
    "provenance_status",
    "claim_scope",
    "allowed_use",
    "must_reverify",
    "files",
}
HIGH_VOLATILITY_TERMS = {"当前价格", "当前排名", "当前市场份额", "新品规格", "KOL近期状态", "平台实时热度"}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    ledger = load_json(LEDGER_PATH)
    data_sources = load_json(DATA_SOURCES_PATH)
    errors: list[str] = []
    source_ids: set[str] = set()
    covered_files: dict[str, list[str]] = {}
    status_counts: Counter[str] = Counter()

    if ledger.get("updated") and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", ledger["updated"]):
        errors.append("ledger updated must use YYYY-MM-DD")
    if set(ledger.get("status_definitions", {})) != VALID_STATUSES:
        errors.append("status_definitions must define verified, partial and missing")
    policy_terms = set(ledger.get("policy", {}).get("verified_required_for", []))
    if policy_terms != HIGH_VOLATILITY_TERMS:
        errors.append("verified_required_for must cover all high-volatility terms")

    sources = ledger.get("sources")
    if not isinstance(sources, list) or not sources:
        errors.append("sources must be a non-empty list")
        sources = []

    for index, source in enumerate(sources, 1):
        missing = sorted(REQUIRED_FIELDS - set(source))
        if missing:
            errors.append(f"source #{index} missing fields: {', '.join(missing)}")
            continue
        source_id = source["source_id"]
        if not isinstance(source_id, str) or not SOURCE_ID_PATTERN.fullmatch(source_id):
            errors.append(f"source #{index} has invalid source_id: {source_id!r}")
            continue
        if source_id in source_ids:
            errors.append(f"duplicate source_id: {source_id}")
        source_ids.add(source_id)
        status = source["provenance_status"]
        if status not in VALID_STATUSES:
            errors.append(f"{source_id}: invalid provenance_status {status!r}")
            continue
        status_counts[status] += 1

        for field in ("publishers", "source_locators", "claim_scope", "allowed_use", "must_reverify", "files"):
            if not isinstance(source[field], list):
                errors.append(f"{source_id}: {field} must be a list")
        for field in ("claim_scope", "allowed_use", "must_reverify", "files"):
            if isinstance(source[field], list) and not source[field]:
                errors.append(f"{source_id}: {field} must not be empty")
        for date_field in ("published_at", "captured_at"):
            value = source.get(date_field)
            if value is not None and (not isinstance(value, str) or not DATE_PATTERN.fullmatch(value)):
                errors.append(f"{source_id}: invalid {date_field} {value!r}")
        cutoff = source.get("data_cutoff")
        if cutoff != "none" and (not isinstance(cutoff, str) or not re.fullmatch(r"\d{4}-\d{2}", cutoff)):
            errors.append(f"{source_id}: invalid data_cutoff {cutoff!r}")
        if status == "verified":
            if not source["publishers"] or not source["source_locators"] or not source.get("published_at"):
                errors.append(f"{source_id}: verified source requires publisher, locator and published_at")
        else:
            if not source["must_reverify"]:
                errors.append(f"{source_id}: partial or missing source requires must_reverify")
            if status == "missing" and source["source_locators"]:
                errors.append(f"{source_id}: missing source must not claim locators")

        for rel in source["files"]:
            path = ROOT / rel
            if not path.is_file():
                errors.append(f"{source_id}: missing file {rel}")
                continue
            covered_files.setdefault(rel, []).append(source_id)

    knowledge_files = {
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "knowledge-base").rglob("*.md")
    }
    missing_coverage = sorted(knowledge_files - set(covered_files))
    if missing_coverage:
        errors.append("knowledge files missing evidence coverage: " + ", ".join(missing_coverage))
    duplicate_coverage = sorted(rel for rel, ids in covered_files.items() if len(ids) > 1)
    if duplicate_coverage:
        errors.append("knowledge files mapped to multiple primary sources: " + ", ".join(duplicate_coverage))

    primary_files = {
        rel
        for category in data_sources.get("categories", [])
        for rel in category.get("primary_files", [])
    }
    missing_primary = sorted(primary_files - set(covered_files))
    if missing_primary:
        errors.append("data source primary files missing evidence coverage: " + ", ".join(missing_primary))

    expected_markers = {rel: ids[0] for rel, ids in covered_files.items() if rel in knowledge_files}
    for rel, source_id in expected_markers.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        if f"证据台账：`{source_id}`" not in text:
            errors.append(f"{rel}: missing evidence marker {source_id}")

    if errors:
        print("evidence ledger audit failed")
        for error in errors:
            print(error)
        return 1
    print(
        "evidence ledger audit passed: "
        f"{len(source_ids)} sources, {len(knowledge_files)} knowledge files, "
        f"verified={status_counts['verified']}, partial={status_counts['partial']}, missing={status_counts['missing']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
