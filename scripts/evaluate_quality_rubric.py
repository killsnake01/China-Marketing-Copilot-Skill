#!/usr/bin/env python3
"""Validate and optionally apply the output quality rubric."""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUBRIC_PATH = ROOT / "docs" / "evals" / "output-quality-rubric.json"

HEURISTICS = {
    "routing_and_context": ["路线", "路由", "品类", "数据源", "知识库"],
    "fact_discipline": ["已核验", "待验证", "推测", "来源", "同源"],
    "evidence_ledger": ["证据柱", "证据缺口", "反对意见", "补证"],
    "route_verdict": ["推荐路线", "备选路线", "弃用路线", "切换条件"],
    "negative_early_warning": ["负面", "S0", "S1", "S2", "S3", "S4", "触发阈值", "负责人"],
    "execution_readiness": ["直接执行", "调整后执行", "暂停重做", "72小时", "7天跟进"],
    "china_3c_language": ["禁用表达", "替代表达", "评论区", "参数党", "数码"],
    "platform_compatibility": ["包内", "外部工具", "OpenClaw", "Hermes", "密钥"],
}


def load_rubric() -> dict:
    return json.loads(RUBRIC_PATH.read_text(encoding="utf-8"))


def fail(message: str) -> int:
    print(f"FAIL {message}")
    return 1


def validate_rubric(rubric: dict) -> int:
    dimensions = rubric.get("dimensions", [])
    if len(dimensions) < 8:
        return fail("rubric must include at least 8 dimensions")
    if rubric.get("passing_score") != 80 or rubric.get("max_score") != 100:
        return fail("rubric passing_score/max_score mismatch")

    ids = set()
    total_weight = 0
    for item in dimensions:
        dimension_id = item.get("id", "")
        if not re.fullmatch(r"[a-z0-9_]+", dimension_id):
            return fail(f"invalid dimension id: {dimension_id}")
        if dimension_id in ids:
            return fail(f"duplicate dimension id: {dimension_id}")
        ids.add(dimension_id)
        weight = item.get("weight")
        if not isinstance(weight, int) or weight <= 0:
            return fail(f"invalid weight: {dimension_id}")
        total_weight += weight
        for key in ["name", "description", "positive_indicators", "hard_fail_conditions"]:
            if not item.get(key):
                return fail(f"dimension missing {key}: {dimension_id}")
        if dimension_id not in HEURISTICS:
            return fail(f"dimension missing heuristic terms: {dimension_id}")

    if total_weight != 100:
        return fail(f"rubric weights must sum to 100, got {total_weight}")
    if len(rubric.get("global_hard_fails", [])) < 5:
        return fail("rubric must include at least 5 global hard fails")
    if len(rubric.get("score_bands", [])) < 4:
        return fail("rubric must include at least 4 score bands")

    print(f"quality rubric check passed: {len(dimensions)} dimensions, {total_weight} points")
    return 0


def score_text(text: str, rubric: dict) -> int:
    total = 0
    print("dimension_scores:")
    for item in rubric["dimensions"]:
        dimension_id = item["id"]
        terms = HEURISTICS[dimension_id]
        hit_count = sum(1 for term in terms if term in text)
        ratio = min(1.0, hit_count / max(2, min(4, len(terms))))
        score = round(item["weight"] * ratio)
        total += score
        print(f"- {dimension_id}: {score}/{item['weight']} ({hit_count} indicators)")
    print(f"total_score: {total}/{rubric['max_score']}")
    return 0 if total >= rubric["passing_score"] else 2


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate or apply the output quality rubric.")
    parser.add_argument("--check", action="store_true", help="validate rubric structure")
    parser.add_argument("--input", help="score a markdown output file with lightweight heuristics")
    args = parser.parse_args()

    rubric = load_rubric()
    status = validate_rubric(rubric)
    if status:
        return status
    if args.input:
        text = Path(args.input).read_text(encoding="utf-8")
        return score_text(text, rubric)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
