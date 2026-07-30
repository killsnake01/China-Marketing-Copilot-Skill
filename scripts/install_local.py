#!/usr/bin/env python3
"""Build, compare, and synchronize the local Codex skill installation."""
from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from build_publish_package import build_platform, runtime_fingerprint, version


SKIP_NAMES = {".DS_Store"}
SKIP_SUFFIXES = {".pyc", ".pyo"}


def default_target() -> Path:
    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()
    return codex_home / "skills/china-marketing-copilot"


def include_file(path: Path) -> bool:
    return (
        path.is_file()
        and path.name not in SKIP_NAMES
        and path.suffix not in SKIP_SUFFIXES
        and "__pycache__" not in path.parts
    )


def tree_snapshot(root: Path) -> dict[str, str]:
    if not root.is_dir():
        return {}
    snapshot: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if not include_file(path):
            continue
        rel = path.relative_to(root).as_posix()
        snapshot[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    return snapshot


def tree_fingerprint(root: Path) -> str | None:
    files = [path for path in sorted(root.rglob("*")) if include_file(path)] if root.is_dir() else []
    if not files:
        return None
    digest = hashlib.sha256()
    for path in files:
        rel = path.relative_to(root).as_posix()
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def compare_trees(expected: Path, installed: Path) -> dict[str, list[str]]:
    expected_files = tree_snapshot(expected)
    installed_files = tree_snapshot(installed)
    expected_paths = set(expected_files)
    installed_paths = set(installed_files)
    return {
        "missing": sorted(expected_paths - installed_paths),
        "extra": sorted(installed_paths - expected_paths),
        "changed": sorted(
            path
            for path in expected_paths & installed_paths
            if expected_files[path] != installed_files[path]
        ),
    }


def is_match(diff: dict[str, list[str]]) -> bool:
    return not any(diff.values())


def read_installed_version(target: Path) -> str:
    version_path = target / "VERSION"
    if not version_path.is_file():
        return "missing"
    return version_path.read_text(encoding="utf-8").strip()


def print_diff(diff: dict[str, list[str]]) -> None:
    for label in ("missing", "extra", "changed"):
        values = diff[label]
        if values:
            preview = ", ".join(values[:8])
            suffix = f" (+{len(values) - 8})" if len(values) > 8 else ""
            print(f"{label}: {preview}{suffix}")


def next_backup_path(backup_root: Path) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    candidate = backup_root / f"china-marketing-copilot-{stamp}"
    counter = 1
    while candidate.exists():
        candidate = backup_root / f"china-marketing-copilot-{stamp}-{counter}"
        counter += 1
    return candidate


def validate_target(target: Path) -> None:
    resolved = target.resolve()
    if resolved in {Path("/"), Path.home().resolve()}:
        raise ValueError(f"refusing unsafe install target: {resolved}")


def sync_tree(expected: Path, target: Path, backup_root: Path) -> Path | None:
    validate_target(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    backup: Path | None = None
    staging = Path(tempfile.mkdtemp(prefix=f".{target.name}.staging-", dir=target.parent))
    try:
        shutil.copytree(expected, staging, dirs_exist_ok=True)
        if target.exists():
            backup_root.mkdir(parents=True, exist_ok=True)
            backup = next_backup_path(backup_root)
            target.replace(backup)
        staging.replace(target)
    except Exception:
        if target.exists() and backup is not None:
            shutil.rmtree(target)
        if backup is not None and backup.exists() and not target.exists():
            backup.replace(target)
        raise
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    return backup


def build_expected(temp_root: Path) -> Path:
    package_dir, _zip_path = build_platform("codex", temp_root, "dir")
    return package_dir


def run_check(expected: Path, target: Path) -> int:
    diff = compare_trees(expected, target)
    print(f"source version: {version()}")
    print(f"installed version: {read_installed_version(target)}")
    print(f"runtime fingerprint: {runtime_fingerprint('codex')}")
    print(f"installed fingerprint: {tree_fingerprint(target) or 'missing'}")
    if is_match(diff):
        print(f"local install matches: {target}")
        return 0
    print(f"local install drift detected: {target}")
    print_diff(diff)
    return 1


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="china-marketing-install-selftest-") as temp_dir:
        root = Path(temp_dir)
        expected = build_expected(root / "build")
        target = root / "codex/skills/china-marketing-copilot"
        backup_root = root / "backups"
        sync_tree(expected, target, backup_root)
        if not is_match(compare_trees(expected, target)):
            print("local install self-test failed: synchronized tree differs")
            return 1
        skill_path = target / "SKILL.md"
        skill_path.write_text(skill_path.read_text(encoding="utf-8") + "\nself-test-drift\n", encoding="utf-8")
        if is_match(compare_trees(expected, target)):
            print("local install self-test failed: drift was not detected")
            return 1
    print("local install self-test passed: sync and drift detection")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Synchronize the local Codex China marketing skill")
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--check", action="store_true", help="compare the installed skill with the current Codex runtime package")
    action.add_argument("--sync", action="store_true", help="back up and replace the installed skill with the current Codex runtime package")
    action.add_argument("--self-test", action="store_true", help="test synchronization and drift detection in a temporary directory")
    action.add_argument("--print-fingerprint", action="store_true", help="print the current Codex runtime package fingerprint")
    parser.add_argument("--target", default=str(default_target()))
    parser.add_argument("--backup-root")
    args = parser.parse_args()

    if args.print_fingerprint:
        print(runtime_fingerprint("codex"))
        return 0
    if args.self_test:
        return run_self_test()

    target = Path(args.target).expanduser().resolve()
    backup_root = (
        Path(args.backup_root).expanduser().resolve()
        if args.backup_root
        else target.parent.parent / "skill-backups"
    )
    with tempfile.TemporaryDirectory(prefix="china-marketing-local-install-") as temp_dir:
        expected = build_expected(Path(temp_dir))
        if args.sync:
            backup = sync_tree(expected, target, backup_root)
            diff = compare_trees(expected, target)
            if not is_match(diff):
                print("local install synchronization failed")
                print_diff(diff)
                return 1
            print(f"local install synchronized: {target}")
            print(f"version: {version()}")
            print(f"installed fingerprint: {tree_fingerprint(target)}")
            if backup:
                print(f"previous install backed up: {backup}")
            return 0
        return run_check(expected, target)


if __name__ == "__main__":
    raise SystemExit(main())
