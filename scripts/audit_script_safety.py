#!/usr/bin/env python3
"""Audit bundled scripts for risky publish-time behavior."""
from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = ROOT / "scripts"

NETWORK_IMPORTS = {
    "boto3",
    "ftplib",
    "http.client",
    "httpx",
    "paramiko",
    "requests",
    "smtplib",
    "socket",
    "urllib.request",
    "urllib3",
}
RISKY_CALLS = {
    "eval": "dynamic code execution",
    "exec": "dynamic code execution",
    "input": "interactive input",
    "getpass.getpass": "interactive secret prompt",
    "os.system": "shell command",
    "os.popen": "shell command",
}
SECRET_MARKERS = ("TOKEN", "KEY", "SECRET", "PASSWORD")


@dataclass(frozen=True)
class Finding:
    path: Path
    line: int
    rule: str
    detail: str


def dotted_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = dotted_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    return ""


def string_value(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def truthy_constant(node: ast.AST) -> bool:
    return isinstance(node, ast.Constant) and node.value is True


def is_network_import(name: str) -> bool:
    return name in NETWORK_IMPORTS


def is_sensitive_env_name(value: str) -> bool:
    upper = value.upper()
    return any(marker in upper for marker in SECRET_MARKERS)


def scan_imports(path: Path, tree: ast.AST) -> list[Finding]:
    findings: list[Finding] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if is_network_import(alias.name):
                    findings.append(Finding(path, node.lineno, "network-import", alias.name))
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if is_network_import(module):
                findings.append(Finding(path, node.lineno, "network-import", module))
    return findings


def scan_calls(path: Path, tree: ast.AST) -> list[Finding]:
    findings: list[Finding] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        call_name = dotted_name(node.func)
        if call_name in RISKY_CALLS:
            findings.append(Finding(path, node.lineno, "risky-call", f"{call_name}: {RISKY_CALLS[call_name]}"))
        if call_name in {"subprocess.run", "subprocess.call", "subprocess.check_call", "subprocess.Popen"}:
            for keyword in node.keywords:
                if keyword.arg == "shell" and truthy_constant(keyword.value):
                    findings.append(Finding(path, node.lineno, "shell-true", call_name))
        if call_name in {"os.getenv", "os.environ.get"} and node.args:
            env_name = string_value(node.args[0])
            if env_name and is_sensitive_env_name(env_name):
                findings.append(Finding(path, node.lineno, "secret-env-read", env_name))
        if call_name == "__import__" and node.args:
            module_name = string_value(node.args[0])
            if module_name and is_network_import(module_name):
                findings.append(Finding(path, node.lineno, "dynamic-network-import", module_name))
    return findings


def scan_file(path: Path) -> list[Finding]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError as exc:
        return [Finding(path, exc.lineno or 1, "syntax-error", exc.msg)]
    return scan_imports(path, tree) + scan_calls(path, tree)


def iter_script_files():
    yield from sorted(SCRIPTS_DIR.glob("*.py"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit bundled Python scripts for risky behavior.")
    parser.add_argument("--quiet", action="store_true", help="only print failures")
    args = parser.parse_args()

    findings: list[Finding] = []
    scripts = list(iter_script_files())
    for path in scripts:
        findings.extend(scan_file(path))

    if findings:
        print("FAIL script safety audit")
        for finding in findings[:50]:
            rel = finding.path.relative_to(ROOT)
            print(f"{rel}:{finding.line}: {finding.rule}: {finding.detail}")
        if len(findings) > 50:
            print(f"... {len(findings) - 50} more finding(s)")
        return 1

    if not args.quiet:
        print(f"script safety audit passed: {len(scripts)} script(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
