#!/usr/bin/env python3
"""Validate the Skill package before commit or publish."""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SELF = Path(__file__).resolve()

REQUIRED_PATHS = [
    "VERSION",
    "SKILL.md",
    "agents/openai.yaml",
    "docs/data-index.md",
    "docs/data-sources.json",
    "docs/templates/strategy-decision-system.md",
    "docs/templates/message-house.md",
    "docs/templates/channel-kol-activation.md",
    "docs/templates/creative-output.md",
    "docs/templates/risk-assessment.md",
    "docs/templates/quality-check-tools.md",
    "docs/ecosystem/market-signals-2026.md",
    "docs/ecosystem/negative-early-warning.md",
    "docs/ecosystem/negative-signal-rules.json",
    "docs/evals/marketing-task-samples.md",
    "docs/evals/negative-signal-samples.md",
    "scripts/preprocess.py",
    "scripts/evaluate_negative_signals.py",
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
    ("private key", re.compile(PRIVATE_KEY_PATTERN)),
    ("ssh private key filename", re.compile("id_" + "ed25519")),
    ("clawhub token env", re.compile("CLAW" + "HUB_TOKEN")),
]

TEXT_SUFFIXES = {".md", ".yaml", ".yml", ".json", ".py", ".txt", ".gitignore"}


def fail(message):
    print(f"FAIL {message}")
    return 1


def iter_text_files():
    for path in ROOT.rglob("*"):
        if ".git" in path.parts or path == SELF:
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
    for item in data["categories"]:
        category = item.get("category")
        if not category or category in seen:
            return fail("data-sources.json has missing or duplicate category")
        seen.add(category)
        if not item.get("data_cutoff") or not isinstance(item.get("must_refresh"), list) or not item["must_refresh"]:
            return fail(f"data-sources.json category missing freshness fields: {category}")
        if not isinstance(item.get("refresh_after_days"), int):
            return fail(f"data-sources.json category missing refresh_after_days: {category}")
        for rel in item.get("primary_files", []):
            if not (ROOT / rel).exists():
                return fail(f"data-sources.json references missing file: {rel}")
    for item in data.get("cross_references", []):
        rel = item.get("path", "")
        if not rel or not (ROOT / rel).exists():
            return fail(f"data-sources.json references missing cross file: {rel}")
    print(f"PASS data-sources categories: {len(seen)}")
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
    if len(rows) < 16:
        return fail("marketing-task-samples.md must include at least 16 task rows")
    ids = set()
    allowed_types = {"策略诊断", "信息架构", "渠道KOL", "风控评估", "风险评估", "竞品洞察", "创意策划", "新品类破局", "负面预警", "正式审核", "数据导入", "平台兼容"}
    for cells in rows:
        sample_id, task_type, _category, _prompt, required_files, required_output, risk, pass_standard = cells
        if sample_id in ids:
            return fail(f"duplicate marketing eval id: {sample_id}")
        ids.add(sample_id)
        if task_type not in allowed_types:
            return fail(f"unknown marketing eval task type: {task_type}")
        if not required_output or not risk or not pass_standard:
            return fail(f"marketing eval row missing scoring fields: {sample_id}")
        for rel in re.findall(r"(?:docs|knowledge-base|SKILL\.md)[^; ]*", required_files):
            if rel == "SKILL.md":
                check_path = ROOT / rel
            else:
                check_path = ROOT / rel.rstrip("；,，")
            if not check_path.exists():
                return fail(f"marketing eval references missing file: {sample_id} -> {rel}")
    print(f"PASS marketing-task eval rows: {len(rows)}")
    return 0


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


def main():
    checks = [
        validate_skill_metadata,
        validate_required_paths,
        validate_json,
        validate_data_sources,
        validate_marketing_eval,
        validate_release_version,
        lambda: scan_patterns("legacy forced-scan wording", FORBIDDEN_PATTERNS),
        lambda: scan_patterns("secret scan", SECRET_PATTERNS),
        run_negative_eval,
    ]
    failures = sum(check() for check in checks)
    if failures:
        print(f"skill pack validation failed: {failures} check(s)")
        return 1
    print("skill pack validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
