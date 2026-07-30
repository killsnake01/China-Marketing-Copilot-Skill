#!/usr/bin/env python3
"""Verify platform release artifacts and zip integrity."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

from build_publish_package import COMMON_PACKAGE_REQUIRED_PATHS, PLATFORM_REQUIRED_PATHS

ROOT = Path(__file__).resolve().parent.parent
PLATFORMS = ("codex", "clawhub", "skillhub")
PACKAGE_STEM = "china-marketing-copilot"
COMMON_FORBIDDEN_PARTS = {".git", "dist", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
COMMON_FORBIDDEN_FILES = {".DS_Store"}
ROOT_SKIP_BY_PLATFORM = {
    "codex": set(),
    "clawhub": {".gitignore"},
    "skillhub": {".gitignore", "LICENSE", "VERSION"},
}
FORBIDDEN_RUNTIME_PATHS = {
    "quickstart-example.md",
    "CONTRIBUTING.md",
    "docs/maintainer-guide.md",
    "docs/platform-listing.md",
    "docs/platform-publish-fields.json",
    "docs/routes/platform-publish.md",
    "scripts/build_publish_package.py",
    "scripts/build_release_manifest.py",
    "scripts/validate_skill_pack.py",
}


def version() -> str:
    return (ROOT / "VERSION").read_text(encoding="utf-8").strip()


def package_name(platform: str) -> str:
    return f"{platform}-{PACKAGE_STEM}-v{version()}"


def fail(message: str) -> int:
    print(f"FAIL {message}")
    return 1


def read_frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not match:
        raise ValueError("missing frontmatter")
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ": " in line:
            key, value = line.split(": ", 1)
            fields[key] = value.strip().strip('"')
    return fields


def zip_entries(zip_path: Path) -> set[str]:
    with zipfile.ZipFile(zip_path) as archive:
        bad = archive.testzip()
        if bad:
            raise ValueError(f"corrupt zip entry: {bad}")
        entries = set()
        for info in archive.infolist():
            name = info.filename
            if name.startswith("/") or ".." in Path(name).parts:
                raise ValueError(f"unsafe zip entry path: {name}")
            if info.is_dir():
                continue
            entries.add(name)
        return entries


def file_entries(package_dir: Path) -> set[str]:
    entries = set()
    for path in package_dir.rglob("*"):
        if path.is_file():
            entries.add(str(path.relative_to(package_dir)))
    return entries


def check_forbidden(rel_paths: set[str], platform: str) -> list[str]:
    findings = []
    for rel in sorted(rel_paths):
        parts = set(Path(rel).parts)
        name = Path(rel).name
        if parts & COMMON_FORBIDDEN_PARTS:
            findings.append(rel)
        if any(part.startswith("dist-v") for part in Path(rel).parts):
            findings.append(rel)
        if name in COMMON_FORBIDDEN_FILES:
            findings.append(rel)
        if len(Path(rel).parts) == 1 and rel in ROOT_SKIP_BY_PLATFORM[platform]:
            findings.append(rel)
    return findings


def validate_package_dir(package_dir: Path, platform: str) -> list[str]:
    findings = []
    if not package_dir.is_dir():
        return [f"missing package directory: {package_dir.name}"]
    rel_paths = file_entries(package_dir)
    required_paths = COMMON_PACKAGE_REQUIRED_PATHS + PLATFORM_REQUIRED_PATHS[platform]
    for rel in required_paths:
        if rel not in rel_paths:
            findings.append(f"{package_dir.name} missing {rel}")
    findings.extend(f"{package_dir.name} contains forbidden file {rel}" for rel in check_forbidden(rel_paths, platform))
    for rel in sorted(FORBIDDEN_RUNTIME_PATHS & rel_paths):
        findings.append(f"{package_dir.name} contains maintainer-only path {rel}")

    manifest_path = package_dir / "RELEASE-MANIFEST.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("version") != version():
            findings.append(f"{package_dir.name} manifest version mismatch")

    readme_path = package_dir / "README.md"
    if readme_path.exists() and f"v{version()}" not in readme_path.read_text(encoding="utf-8"):
        findings.append(f"{package_dir.name} README missing current version")

    if platform in {"codex", "clawhub"}:
        version_path = package_dir / "VERSION"
        if not version_path.exists() or version_path.read_text(encoding="utf-8").strip() != version():
            findings.append(f"{package_dir.name} VERSION mismatch")

    if platform == "skillhub":
        skill_path = package_dir / "SKILL.md"
        if skill_path.exists():
            fields = read_frontmatter(skill_path.read_text(encoding="utf-8"))
            expected = {
                "name": "china-marketing-copilot",
                "slug": "china-marketing-copilot",
                "version": version(),
                "displayName": "中国3C营销助手",
            }
            for key, value in expected.items():
                if fields.get(key) != value:
                    findings.append(f"{package_dir.name} frontmatter mismatch: {key}")
    link_result = subprocess.run(
        [sys.executable, "-B", "scripts/check_internal_links.py", "--root", str(package_dir), "--quiet"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if link_result.returncode != 0:
        detail = link_result.stdout.strip().splitlines()
        findings.append(f"{package_dir.name} has broken runtime references")
        findings.extend(f"{package_dir.name}: {line}" for line in detail[:12])
    return findings


def validate_zip(zip_path: Path, package_dir: Path, platform: str) -> list[str]:
    findings = []
    if not zip_path.is_file():
        return [f"missing zip: {zip_path.name}"]
    try:
        zip_rel_paths = zip_entries(zip_path)
    except ValueError as exc:
        return [f"{zip_path.name} {exc}"]
    dir_rel_paths = file_entries(package_dir) if package_dir.is_dir() else set()
    if dir_rel_paths and zip_rel_paths != dir_rel_paths:
        findings.append(f"{zip_path.name} entries differ from package directory")
    findings.extend(f"{zip_path.name} contains forbidden file {rel}" for rel in check_forbidden(zip_rel_paths, platform))
    if not package_dir.is_dir():
        with tempfile.TemporaryDirectory(prefix=f"china-marketing-{platform}-zip-") as temp_dir:
            extracted_dir = Path(temp_dir)
            with zipfile.ZipFile(zip_path) as archive:
                archive.extractall(extracted_dir)
            findings.extend(validate_package_dir(extracted_dir, platform))
    return findings


def validate_artifact_set(output_dir: Path) -> list[str]:
    findings = []
    expected_names = {package_name(platform) for platform in PLATFORMS}
    required_paths = {f"{name}.zip" for name in expected_names}
    allowed_paths = required_paths | expected_names
    actual_release_paths = {
        path.name
        for path in output_dir.iterdir()
        if re.fullmatch(rf"(?:{'|'.join(PLATFORMS)})-{PACKAGE_STEM}-v.+(?:\.zip)?", path.name)
    }
    extra = sorted(actual_release_paths - allowed_paths)
    missing = sorted(required_paths - actual_release_paths)
    findings.extend(f"unexpected release artifact: {name}" for name in extra)
    findings.extend(f"missing release artifact: {name}" for name in missing)
    for platform in PLATFORMS:
        name = package_name(platform)
        package_dir = output_dir / name
        zip_path = output_dir / f"{name}.zip"
        if package_dir.exists():
            findings.extend(validate_package_dir(package_dir, platform))
        findings.extend(validate_zip(zip_path, package_dir, platform))
    return findings


def build_temp_artifacts(output_dir: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-B",
            "scripts/build_publish_package.py",
            "--platform",
            "all",
            "--output",
            str(output_dir),
            "--format",
            "both",
            "--candidate",
        ],
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
        raise RuntimeError("publish package build failed")


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify release artifact directories and zips.")
    parser.add_argument("--build-temp", action="store_true", help="build artifacts in a temp directory before verifying")
    parser.add_argument("--output", default="dist", help="artifact directory to verify when --build-temp is not used")
    args = parser.parse_args()

    try:
        if args.build_temp:
            with tempfile.TemporaryDirectory(prefix="china-marketing-release-") as temp_dir:
                output_dir = Path(temp_dir)
                build_temp_artifacts(output_dir)
                findings = validate_artifact_set(output_dir)
        else:
            output_dir = (ROOT / args.output).resolve()
            if not output_dir.exists():
                return fail(f"artifact directory missing: {output_dir}")
            findings = validate_artifact_set(output_dir)
    except RuntimeError as exc:
        return fail(str(exc))

    if findings:
        print("FAIL release artifact verification")
        for finding in findings[:80]:
            print(finding)
        if len(findings) > 80:
            print(f"... {len(findings) - 80} more finding(s)")
        return 1
    print(f"release artifact verification passed: {', '.join(package_name(platform) for platform in PLATFORMS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
