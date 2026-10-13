#!/usr/bin/env python3
"""Issue #215: publish one clean authoring ZIP and one compiled bundle per STIG.

Only preverified grouped native source is accepted. Faithful converter evidence
remains preserved in its original CI/release; it is intentionally not re-shipped.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile

import yaml

from scap_ng_content_compiler import compile_benchmark, verify_bundle
from scap_ng_repo_normalizer import validate_normalized_repository


# Public names are presentation aliases, not Assessment, Benchmark, or Rule IDs.
BENCHMARKS = {
    "rhel_9": ("rhel9", "Red Hat Enterprise Linux 9"),
    "oracle_linux_9": ("oracle-linux9", "Oracle Linux 9"),
    "ms_windows_11": ("windows11", "Windows 11"),
    "ms_windows_server_2025": ("windows-server-2025", "Windows Server 2025"),
    "ms_windows_server_dns": ("windows-server-dns", "Windows Server DNS"),
    "apache_server_2-4_unix_server": ("apache-unix-server", "Apache HTTP Server 2.4 (UNIX)"),
}

SOURCE_TAG = "v0.3.0-shared-layout-preview-29591bda05ab"
SOURCE_REVISION = "29591bda05abb0006971268fca3e1b98b7d0f3f7"
NIWC_REVISION = "8c8e5dff860af6b1290ee9273a282db24278f8d5"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1048576), b""):
            h.update(block)
    return h.hexdigest()


def write_archive(output: Path, root: Path, *, top: str | None = None) -> None:
    """Build a reproducible ZIP, keeping source references in place."""
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in sorted(p for p in root.rglob("*") if p.is_file()):
            if path.name == "CANDIDATE-STATUS.md":
                continue
            rel = path.relative_to(root)
            arcname = (Path(top) / rel).as_posix() if top else rel.as_posix()
            if any(part in {"faithful-authoring", "candidate-authoring"} for part in rel.parts):
                raise ValueError(f"Research-stage tree must not be distributed: {rel}")
            info = zipfile.ZipInfo(arcname, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o100644 & 0xffff) << 16
            zf.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def check_archive(output: Path, expected: list[str] | None = None) -> None:
    with zipfile.ZipFile(output) as zf:
        if zf.testzip():
            raise ValueError(f"Corrupted archive: {output}")
        names = zf.namelist()
        if any("faithful-authoring" in n or "candidate-authoring" in n or "CANDIDATE-STATUS" in n for n in names):
            raise ValueError(f"Legacy review-stage names leaked: {output}")
        for name in expected or []:
            if name not in names:
                raise ValueError(f"Missing {name} in {output}")


def build(source: Path, output: Path, revision: str) -> None:
    if source.name != "authoring" or not (source / "shared" / "assessments").is_dir():
        raise ValueError(f"Expected grouped authoring root, got {source}")
    actual = {p.name for p in source.iterdir() if p.is_dir() and p.name != "shared"}
    if actual != set(BENCHMARKS):
        raise ValueError(f"Incorrect six-benchmark set: {actual}")
    output.mkdir(parents=True, exist_ok=True)
    # Fail closed on the old DoD-ambiguous folder and duplicated OS prefix.
    for path in (source / "shared" / "assessments").rglob("*.assessment.yaml"):
        rel = path.relative_to(source / "shared" / "assessments")
        if "unclassified" in rel.parts:
            raise ValueError(f"Deprecated shared folder in source: {rel}")
        if rel.parts[0] == "linux" and path.name.startswith("linux-"):
            raise ValueError(f"Redundant Linux filename prefix: {rel}")
    validation = validate_normalized_repository(source)
    if validation["unresolved_rule_references"] or validation["assessment_identity_conflicts"]:
        raise ValueError(f"Invalid source references: {validation}")

    metrics = output / "build-metrics.json"
    compiled = output / "compiled"
    subprocess.run([
        sys.executable, "tools/scap_ng_content_compiler.py", str(source),
        "--output-dir", str(compiled), "--metrics", str(metrics),
        "--source-revision", NIWC_REVISION, "--scap-ng-revision", revision,
    ], check=True)
    bundles = sorted(compiled.glob("*.scapng"))
    if len(bundles) != len(BENCHMARKS):
        raise ValueError(f"Expected exactly six .scapng bundles, got {bundles}")

    # Map shared logical identities to their exact source paths, avoiding
    # unrelated Linux/Windows content in a benchmark-specific authoring ZIP.
    shared_by_id = {}
    for path in sorted((source / "shared").rglob("*.assessment.yaml")):
        obj = yaml.safe_load(path.read_text(encoding="utf-8")).get("assessment") or {}
        identity = obj.get("id")
        if not identity or identity in shared_by_id:
            raise ValueError(f"Duplicate/missing shared Assessment identity: {identity}")
        shared_by_id[identity] = path

    releases = {}
    for key, (short, title) in BENCHMARKS.items():
        original = compiled / f"benchmark.{key}.scapng"
        if not original.exists():
            raise ValueError(f"Missing compiled Benchmark {key} ({original})")
        verified = verify_bundle(original)
        with zipfile.ZipFile(original) as zf:
            manifest = json.loads(zf.read("META-INF/manifest.json"))
        manifest_objects = manifest["objects"]
        for identity, record in manifest_objects.items():
            member = record["path"]
            if "unclassified" in member.split("/"):
                raise ValueError(f"Deprecated classification in {key}: {member}")
            if (identity.startswith("ng.shared.")
                    and record["type"] == "assessment"
                    and not member.startswith("assessments/shared/")):
                raise ValueError(f"Shared Assessment outside shared package directory: {member}")
        if manifest["benchmark_id"] != f"benchmark.{key}":
            raise ValueError(f"Compiled Benchmark ID changed for {key}")

        selected_shared = {
            identity: shared_by_id[identity]
            for identity, row in manifest_objects.items()
            if row["type"] == "assessment" and identity in shared_by_id
        }
        with tempfile.TemporaryDirectory(prefix="ng-authoring-") as temp:
            root = Path(temp)
            authoring = root / "authoring"
            authoring.mkdir(parents=True)
            shutil.copytree(source / key, authoring / key,
                            ignore=shutil.ignore_patterns("CANDIDATE-STATUS.md"))
            for identity, path in sorted(selected_shared.items()):
                dest = authoring / path.relative_to(source)
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, dest)

            # Compiler must independently resolve the extracted standalone
            # authoring subset to exactly the same immutable package objects.
            validate_normalized_repository(authoring)
            benchmark, members, index = compile_benchmark(authoring, authoring / key)
            if benchmark["id"] != manifest["benchmark_id"]:
                raise ValueError(f"Authoring Benchmark changed for {key}")
            original_index = {
                ident: (record["type"], record["sha256"])
                for ident, record in manifest_objects.items()
            }
            new_index = {
                ident: (record["type"], record["sha256"])
                for ident, record in index.items()
            }
            if original_index != new_index:
                missing = sorted(set(original_index) - set(new_index))[:12]
                extra = sorted(set(new_index) - set(original_index))[:12]
                mismatched = sorted(
                    name for name in original_index.keys() & new_index.keys()
                    if original_index[name] != new_index[name]
                )[:12]
                raise ValueError(
                    f"Isolated {key} source does not reproduce compiled content: "
                    f"missing={missing}, extra={extra}, mismatched={mismatched}"
                )

            (root / "README.md").write_text(
                f"# {title} — SCAP-NG 0.3 authoring source\n\n"
                f"Open \`authoring/{key}/benchmark.yaml\` to start.\n"
                "All Rules, Assessments and required shared Assessments are under \`authoring/\`.\n"
                "This is the **modernized native authoring form**, not a faithful\n"
                "SCAP 1.4 migration dump. No competing candidate source is included.\n"
                "The compiled scanning-content download is a separate \`.scapng\` file.\n"
                "Pre-alpha research demonstration, not DISA-approved content or\n"
                "a production-authorized scanner package.\n",
                encoding="utf-8",
            )
            authoring_asset = f"scap-ng-0.3-{short}-authoring.zip"
            write_archive(output / authoring_asset, root)
            check_archive(output / authoring_asset, [f"authoring/{key}/benchmark.yaml"])

        bundle_asset = f"scap-ng-0.3-{short}.scapng"
        shutil.copy2(original, output / bundle_asset)
        if verify_bundle(output / bundle_asset)["manifest_sha256"] != verified["manifest_sha256"]:
            raise ValueError(f"Compiled bundle changed during packaging: {key}")
        releases[key] = {
            "label": title,
            "authoring_file": authoring_asset,
            "scanning_file": bundle_asset,
            "benchmark_id": manifest["benchmark_id"],
            "shared_assessments_included": len(selected_shared),
            "compiled_objects": len(manifest_objects),
            "compiled_bundle_signed": bool(manifest.get("signature", {}).get("format")),
        }

    # One convenient combined source ZIP, still without faithful/candidate trees.
    combined = "scap-ng-0.3-six-stig-authoring.zip"
    with tempfile.TemporaryDirectory(prefix="ng-authoring-all-") as temp:
        root = Path(temp)
        shutil.copytree(source, root / "authoring",
                        ignore=shutil.ignore_patterns("CANDIDATE-STATUS.md"))
        (root / "README.md").write_text(
            "# SCAP-NG 0.3 — six complete modernized STIG authoring trees\n\n"
            "Start with \`authoring/<benchmark>/benchmark.yaml\`. Reusable Assessments\n"
            "live in \`authoring/shared/assessments/<os-family>/<subject>/\`.\n"
            "Only current modernized authoring is included. Faithful conversion\n"
            "evidence remains available in earlier development artifacts.\n"
            "Pre-alpha: not a DISA-issued or production-certified package.\n",
            encoding="utf-8",
        )
        write_archive(output / combined, root)
        check_archive(output / combined)

    # Publishing products only; compiler scratch output is not public.
    shutil.rmtree(compiled)
    metrics.unlink()
    manifest = {
        "format": "scap-ng-six-stig-two-product-preview-0.1",
        "status": "pre-alpha, not runtime scanner conformance or publisher trust",
        "source_release": SOURCE_TAG,
        "source_revision": SOURCE_REVISION,
        "niwc_source_revision": NIWC_REVISION,
        "build_revision": revision,
        "authoring_combined": combined,
        "benchmarks": releases,
    }
    (output / "DOWNLOADS.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8",
    )
    files = sorted(path for path in output.iterdir() if path.is_file())
    (output / "SHA256SUMS.txt").write_text(
        "".join(f"{sha256(p)}  {p.name}\n" for p in files), encoding="utf-8",
    )
    if len([x for x in output.glob("*-authoring.zip")]) != 7:
        raise ValueError("Missing six authoring ZIPs or combined authoring ZIP")
    if len(list(output.glob("*.scapng"))) != 6:
        raise ValueError("Missing six scanning bundles")
    print(json.dumps(manifest, indent=2, sort_keys=True))
    for path in sorted(output.iterdir()):
        print("RELEASE_ASSET", path.name, path.stat().st_size)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--build-revision", required=True)
    args = p.parse_args()
    build(args.source.resolve(), args.output.resolve(), args.build_revision)


if __name__ == "__main__":
    main()
