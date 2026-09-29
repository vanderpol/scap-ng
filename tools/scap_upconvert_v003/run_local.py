#!/usr/bin/env python3
"""Run SCAP-NG v003 conversions locally with the same gates used by CI."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import zipfile

import yaml

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from scap_upconvert_v003.cleanliness import assert_native_clean


def run(cmd, *, env=None):
    print("+", " ".join(str(x) for x in cmd), flush=True)
    subprocess.run(cmd, cwd=ROOT, env=env, check=True)


def validate_native_source(root: Path) -> int:
    files = sorted(root.rglob("*.yaml"))
    if not files:
        raise RuntimeError(f"no native YAML files found under {root}")
    for path in files:
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert_native_clean(doc)
    print(f"Native cleanliness: PASS ({len(files)} YAML files)")
    return len(files)


def validate_package(package: Path) -> dict:
    with zipfile.ZipFile(package) as zf:
        names = set(zf.namelist())
        manifest = json.loads(zf.read("manifest.json"))
        objects = manifest["objects"]

        for object_id, item in objects.items():
            member = item["path"]
            if member not in names:
                raise RuntimeError(f"manifest path missing: {object_id} -> {member}")
            data = zf.read(member)
            if hashlib.sha256(data).hexdigest() != item["sha256"]:
                raise RuntimeError(f"digest mismatch: {object_id}")
            if len(data) != item["size"]:
                raise RuntimeError(f"size mismatch: {object_id}")

        benchmark_id = manifest["benchmark"]
        benchmark_item = objects.get(benchmark_id)
        if not benchmark_item or benchmark_item["type"] != "benchmark":
            raise RuntimeError(f"benchmark object unresolved: {benchmark_id}")
        benchmark = json.loads(zf.read(benchmark_item["path"]))["benchmark"]

        for rule_id in benchmark["rules"]:
            item = objects.get(rule_id)
            if not item or item["type"] != "rule":
                raise RuntimeError(f"Benchmark Rule unresolved: {rule_id}")

        catalog_id = benchmark["applicability_catalog"]
        catalog_item = objects.get(catalog_id)
        if not catalog_item or catalog_item["type"] != "applicability_catalog":
            raise RuntimeError(f"applicability catalog unresolved: {catalog_id}")

        catalog = json.loads(zf.read(catalog_item["path"]))["applicability_catalog"]
        for condition in catalog["conditions"]:
            assessment_id = condition["assessment"]
            item = objects.get(assessment_id)
            if not item or item["type"] != "assessment":
                raise RuntimeError(
                    f"applicability Assessment unresolved: {assessment_id}"
                )

        result = {
            "package_members": len(names),
            "logical_objects": len(objects),
            "benchmark_rules": len(benchmark["rules"]),
            "sha256": hashlib.sha256(package.read_bytes()).hexdigest(),
        }
        print("Package integrity/resolution: PASS")
        print(json.dumps(result, indent=2))
        return result


def show_diagnostics(path: Path, fail_on_error: bool) -> int:
    doc = json.loads(path.read_text(encoding="utf-8"))
    summary = doc["summary"]
    counts = summary["counts"]
    print(
        "Diagnostics:",
        " ".join(
            f"{level.upper()}={counts.get(level, 0)}"
            for level in ("info", "warn", "error", "fatal")
        ),
    )
    if counts.get("fatal", 0):
        return 2
    if fail_on_error and counts.get("error", 0):
        return 1
    return 0


def run_rhel9(mode: str, fail_on_error: bool) -> int:
    env = os.environ.copy()
    env["SCAP_NG_V003_MODE"] = mode

    run(
        [sys.executable, "tools/scap_upconvert_v003/build_rhel9_review_slice.py"],
        env=env,
    )

    build_name = "rhel9-full" if mode == "full" else "rhel9-review-slice"
    source_root = (
        ROOT
        / "research/iterations/003/source/split-rule-assessment"
        / build_name
    )
    diagnostics = ROOT / "research/iterations/003/evidence" / build_name / "diagnostics.json"
    package = ROOT / "research/iterations/003/packages" / f"{build_name}.scap-ng.zip"

    validate_native_source(source_root)
    validate_package(package)
    return show_diagnostics(diagnostics, fail_on_error)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run SCAP-NG v003 conversions locally."
    )
    parser.add_argument(
        "target",
        choices=["rhel9"],
        help="source benchmark target (Windows 11 will be added to this runner)",
    )
    parser.add_argument(
        "--mode",
        choices=["slice", "full"],
        default="full",
        help="conversion scope; default: full",
    )
    parser.add_argument(
        "--fail-on-error",
        action="store_true",
        help="return non-zero when conversion ERROR diagnostics remain",
    )
    args = parser.parse_args()

    if args.target == "rhel9":
        return run_rhel9(args.mode, args.fail_on_error)
    raise AssertionError(args.target)


if __name__ == "__main__":
    raise SystemExit(main())
