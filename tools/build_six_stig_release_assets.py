#!/usr/bin/env python3
"""Publishable, checksum-verifiable six-STIG authoring ZIPs from one validated candidate run.

This creates assets only. It does not claim runtime-conformance or Board acceptance.
"""
import argparse
import hashlib
import json
import shutil
import zipfile
from pathlib import Path

import yaml

KEYS = (
    "rhel9",
    "oracle-linux9",
    "windows11",
    "windows-server-2025",
    "windows-server-dns",
    "apache-unix-server",
)


def _sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1048576), b""):
            digest.update(block)
    return digest.hexdigest()


def _count_filters(document, *, origin):
    if isinstance(document, list):
        return sum(_count_filters(value, origin=origin) for value in document)
    if not isinstance(document, dict):
        return 0
    count = 0
    if "filters" in document:
        entries = document["filters"]
        if not isinstance(entries, list):
            raise ValueError(f"{origin}: filters is not an array")
        for predicate in entries:
            if not isinstance(predicate, dict) or predicate.get("action") not in {"include", "exclude"}:
                raise ValueError(f"{origin}: missing explicit include/exclude action")
            if any(name in predicate for name in ("state", "capability", "state_title", "filter_title")):
                raise ValueError(f"{origin}: legacy/redundant Filter state/capability/title")
            if not any(name in predicate for name in ("field", "all", "any", "one", "odd")):
                raise ValueError(f"{origin}: Filter lacks embedded predicate")
        count += len(entries)
    return count + sum(_count_filters(value, origin=origin) for value in document.values())


def build(input_root, output, sha, niwc_revision):
    root = input_root / "scap-ng-0.3-human-review"
    benchmark_root = root / "benchmarks"
    present = sorted(path.name for path in benchmark_root.iterdir() if path.is_dir())
    if present != sorted(KEYS):
        raise ValueError(f"Expected exactly six completed STIGs, found {present}")
    combined = input_root / "scap-ng-0.3-board-review.zip"
    check = input_root / "scap-ng-0.3-board-review.zip.sha256"
    if not combined.is_file() or not check.is_file():
        raise ValueError("Missing combined candidate ZIP or SHA-256")
    if _sha256(combined) != check.read_text().split()[0]:
        raise ValueError("Combined ZIP has incorrect digest")
    output.mkdir(parents=True, exist_ok=True)
    manifest = {
        "kind": "SCAP-NG 0.3 pre-alpha authoring preview, not release acceptance",
        "source_sha": sha,
        "niwc_revision": niwc_revision,
        "benchmarks": {},
    }
    total_filters = 0
    epoch = (1980, 1, 1, 0, 0, 0)
    for key in KEYS:
        base = benchmark_root / key
        if not (base / "candidate-authoring").is_dir() or not (base / "faithful-authoring").is_dir():
            raise ValueError(f"{key} missing faithful/candidate authoring trees")
        documents = sorted((base / "candidate-authoring").rglob("*.yaml"))
        if not documents:
            raise ValueError(f"{key}: no YAML")
        filters = 0
        for source in documents:
            data = yaml.safe_load(source.read_text(encoding="utf-8"))
            filters += _count_filters(data, origin=str(source.relative_to(base)))
        manifest["benchmarks"][key] = {"native_yaml_files": len(documents), "embedded_filter_count": filters}
        total_filters += filters
        archive = output / f"scap-ng-0.3-{key}-source-preview.zip"
        with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
            for source in sorted(p for p in base.rglob("*") if p.is_file()):
                arcname = (Path(key) / source.relative_to(base)).as_posix()
                info = zipfile.ZipInfo(arcname, date_time=epoch)
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = (0o100644 & 0xFFFF) << 16
                bundle.writestr(info, source.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
        with zipfile.ZipFile(archive) as bundle:
            names = bundle.namelist()
            if not any("/candidate-authoring/" in name for name in names):
                raise ValueError(f"{key}: generated ZIP lacks candidate files")
            if not any("/faithful-authoring/" in name for name in names):
                raise ValueError(f"{key}: generated ZIP lacks faithful files")
    if total_filters < 1:
        raise ValueError("No embedded Filter predicates found across six conversions: stale showcase?")
    manifest["total_embedded_filters"] = total_filters
    shutil.copy2(combined, output / "scap-ng-0.3-six-stig-source-preview.zip")
    (output / "BUILD-MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    assets = sorted(path for path in output.iterdir() if path.is_file())
    (output / "SHA256SUMS.txt").write_text(
        "".join(f"{_sha256(path)}  {path.name}\n" for path in assets), encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    for path in sorted(output.iterdir()):
        print("RELEASE_ASSET", path.name, path.stat().st_size)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input-root", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--source-sha", required=True)
    p.add_argument("--niwc-revision", required=True)
    args = p.parse_args()
    build(args.input_root, args.output, args.source_sha, args.niwc_revision)


if __name__ == "__main__":
    main()
