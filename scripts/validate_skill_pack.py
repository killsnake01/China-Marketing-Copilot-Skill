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
    "docs/templates/strategy-decision-system.md",
    "docs/templates/message-house.md",
    "docs/templates/channel-kol-activation.md",
    "docs/templates/creative-output.md",
    "docs/templates/risk-assessment.md",
    "docs/templates/quality-check-tools.md",
    "docs/ecosystem/market-signals-2026.md",
    "docs/ecosystem/negative-early-warning.md",
    "docs/ecosystem/negative-signal-rules.json",
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
    json_path = ROOT / "docs" / "ecosystem" / "negative-signal-rules.json"
    json.loads(json_path.read_text(encoding="utf-8"))
    print("PASS negative-signal-rules.json")
    return 0


def validate_release_version():
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        return fail("VERSION must be semantic version like 1.3.3")
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
