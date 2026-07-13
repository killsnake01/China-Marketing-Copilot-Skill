#!/usr/bin/env python3
"""Validate executive memo samples and classify Go/No-Go snippets."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SAMPLES_PATH = ROOT / "docs" / "evals" / "executive-memo-samples.json"

DECISIONS = ["直接执行", "调整后执行", "暂停重做"]
PAUSE_TERMS = ["存在硬阻断", "核心证据冲突", "监管", "资质", "关键物料赶不上", "解禁时间不可控"]
ADJUST_TERMS = ["待验证", "补证据", "样张条件", "同源竞品", "PPT功能", "套壳", "固定梗", "需要切换"]
READY_TERMS = ["已核验", "已统一", "无硬阻断", "已交付", "S0单点异常", "复盘指标已写清"]


def load_samples() -> dict:
    return json.loads(SAMPLES_PATH.read_text(encoding="utf-8"))


def classify_verdict(text: str) -> str:
    if any(term in text for term in PAUSE_TERMS):
        return "暂停重做"
    if any(term in text for term in ADJUST_TERMS):
        return "调整后执行"
    if any(term in text for term in READY_TERMS):
        return "直接执行"
    return "调整后执行"


def marker(verdict: str) -> str:
    return {
        "直接执行": "无硬阻断，证据和动作已就绪",
        "调整后执行": "可推进，但需补证据或缩窄路线",
        "暂停重做": "存在硬阻断或关键交付缺口",
    }[verdict]


def fail(message: str) -> int:
    print(f"FAIL {message}")
    return 1


def validate_samples(data: dict) -> int:
    if data.get("decisions") != DECISIONS:
        return fail("executive memo decisions mismatch")
    samples = data.get("samples", [])
    if len(samples) < 6:
        return fail("executive memo samples must include at least 6 rows")
    ids = set()
    seen = set()
    for item in samples:
        sample_id = item.get("id", "")
        if not sample_id or sample_id in ids:
            return fail("executive memo sample missing or duplicate id")
        ids.add(sample_id)
        verdict = item.get("expected_verdict")
        if verdict not in DECISIONS:
            return fail(f"executive memo sample has invalid verdict: {sample_id}")
        seen.add(verdict)
        for key in ["input", "required_terms"]:
            if not item.get(key):
                return fail(f"executive memo sample missing {key}: {sample_id}")
        predicted = classify_verdict(item["input"])
        if predicted != verdict:
            return fail(f"executive memo verdict mismatch: {sample_id} expected {verdict}, got {predicted}")
    if seen != set(DECISIONS):
        return fail("executive memo samples must cover all decisions")
    print(f"executive memo sample check passed: {len(samples)} samples")
    return 0


def scan_text(text: str) -> int:
    verdict = classify_verdict(text)
    print(f"verdict: {verdict}")
    print(f"marker: {marker(verdict)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate or scan executive decision memo samples.")
    parser.add_argument("--check", action="store_true", help="validate sample structure")
    parser.add_argument("--text", help="scan one decision note")
    parser.add_argument("--input", help="scan a text file")
    args = parser.parse_args()

    status = validate_samples(load_samples())
    if status:
        return status
    if args.text:
        return scan_text(args.text)
    if args.input:
        return scan_text(Path(args.input).read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
