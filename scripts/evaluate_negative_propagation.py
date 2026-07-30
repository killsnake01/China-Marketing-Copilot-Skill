#!/usr/bin/env python3
"""Evaluate structured negative propagation samples."""
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

from analyze_signal_batch import STAGE_ORDER, analyze_records, load_records, validate_record


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_EVAL_PATH = ROOT / "docs/evals/negative-propagation-samples.json"


def prepare_records(raw_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [validate_record(item, index) for index, item in enumerate(raw_records, 1)]


def evaluate_sample(sample: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    result = analyze_records(prepare_records(sample["records"]), sample["category"])
    expected = sample["expected"]
    signal = next((item for item in result["signals"] if item["name"] == expected["signal"]), None)
    if signal is None:
        return [f"missing signal {expected['signal']}"]
    for field in (
        "stage",
        "level",
        "trend",
        "route_impact",
        "unique_authors",
        "business_impact_mentions",
        "metadata_quality",
    ):
        if field in expected and signal.get(field) != expected[field]:
            findings.append(f"{field}: expected {expected[field]!r}, got {signal.get(field)!r}")
    for flag in expected.get("required_flags", []):
        if flag not in signal["flags"]:
            findings.append(f"missing flag {flag}")
    for flag in expected.get("forbidden_flags", []):
        if flag in signal["flags"]:
            findings.append(f"unexpected flag {flag}")
    if "max_stage" in expected and STAGE_ORDER[signal["stage"]] > STAGE_ORDER[expected["max_stage"]]:
        findings.append(f"stage exceeds {expected['max_stage']}: {signal['stage']}")
    return findings


def validate_eval_data(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    samples = data.get("samples")
    if not isinstance(samples, list) or len(samples) < 8:
        return ["evaluation set must contain at least eight samples"]
    seen: set[str] = set()
    required_stages: set[str] = set()
    for sample in samples:
        sample_id = sample.get("id")
        if not isinstance(sample_id, str) or not sample_id.startswith("NP"):
            errors.append(f"invalid sample id: {sample_id!r}")
            continue
        if sample_id in seen:
            errors.append(f"duplicate sample id: {sample_id}")
        seen.add(sample_id)
        if not isinstance(sample.get("records"), list) or not sample["records"]:
            errors.append(f"{sample_id}: missing records")
        expected = sample.get("expected", {})
        if expected.get("stage"):
            required_stages.add(expected["stage"])
    missing_stages = {"S0", "S1", "S2", "S3", "S4"} - required_stages
    if missing_stages:
        errors.append("stage coverage missing: " + ", ".join(sorted(missing_stages)))
    return errors


def validate_import_formats() -> list[str]:
    findings: list[str] = []
    with tempfile.TemporaryDirectory(prefix="china-marketing-negative-import-") as temp_dir:
        root = Path(temp_dir)
        csv_path = root / "comments.csv"
        csv_path.write_text(
            "评论ID,评论内容,评论时间,平台,账号,角色,互动量\n"
            "c1,刚买就跳水，首发用户像冤种。,2026-07-13 08:00:00,微博,u1,用户,1.2万\n",
            encoding="utf-8",
        )
        tsv_path = root / "comments.tsv"
        tsv_path.write_text(
            "id\tcomment\ttimestamp\tplatform\tuser_id\n"
            "t1\t骑车时风噪压不住。\t2026-07-13T09:00:00+08:00\txiaohongshu\tu2\n",
            encoding="utf-8",
        )
        text_path = root / "comments.txt"
        text_path.write_text("戴半小时耳朵疼。\n\n地铁上漏音明显。\n", encoding="utf-8")

        csv_records, csv_format = load_records(csv_path)
        tsv_records, tsv_format = load_records(tsv_path)
        text_records, text_format = load_records(text_path)
        if csv_format != "csv" or len(csv_records) != 1:
            findings.append("CSV auto detection or row loading failed")
        elif csv_records[0]["engagement"] != 12000:
            findings.append("CSV engagement normalization failed")
        elif not csv_records[0]["timestamp_assumed_timezone"]:
            findings.append("CSV naive timestamp assumption was not recorded")
        if tsv_format != "tsv" or len(tsv_records) != 1:
            findings.append("TSV auto detection or row loading failed")
        if text_format != "text" or len(text_records) != 2:
            findings.append("text auto detection or line loading failed")
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate structured negative propagation samples")
    parser.add_argument("--eval-file", default=str(DEFAULT_EVAL_PATH))
    parser.add_argument("--show-passed", action="store_true")
    args = parser.parse_args()
    data = json.loads(Path(args.eval_file).read_text(encoding="utf-8"))
    data_errors = validate_eval_data(data)
    if data_errors:
        print("negative propagation eval data failed")
        for error in data_errors:
            print(error)
        return 1
    import_findings = validate_import_formats()
    if import_findings:
        print("negative import format checks failed")
        for finding in import_findings:
            print(finding)
        return 1
    print("negative import formats: CSV/TSV/text passed")
    failed = 0
    for sample in data["samples"]:
        findings = evaluate_sample(sample)
        if findings:
            failed += 1
        if findings or args.show_passed:
            status = "FAIL" if findings else "PASS"
            print(f"{status} {sample['id']}")
            for finding in findings:
                print(f"  {finding}")
    passed = len(data["samples"]) - failed
    print(f"negative propagation eval: {passed}/{len(data['samples'])} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
