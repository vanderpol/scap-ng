#!/usr/bin/env python3
"""Curate six-STIG reviewer ZIPs: native SCAP-NG YAML, not migration evidence.

Never rewrite native YAML: it contains authoritative Rule identifiers,
publisher metadata, policy references, and any other required traceability.
Engineering sidecars remain in the original verified Actions artifact.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path, PurePosixPath
import zipfile

BENCHMARKS = frozenset({
    "rhel_9", "oracle_linux_9", "ms_windows_11",
    "ms_windows_server_2025", "ms_windows_server_dns",
    "apache_server_2-4_unix_server",
})
ENGINEERING_SIDECARS = frozenset({
    "applicability-evidence.json", "evidence.json", "grouping-provenance.json",
    "profile-selection-audit.json", "profile-selection-provenance.json",
    "rule-source-audit.json", "source-generation.json", "validation.json",
})
README = """# SCAP-NG 0.3 — six-STIG native authoring preview

Start at `authoring/<benchmark>/benchmark.yaml`; Rule and Assessment YAML
and shared Assessments under `authoring/shared/assessments/` are native authoring.
Original DISA Rule identifiers, references, publisher metadata and other
native traceability are preserved byte-for-byte in the YAML files.

Converter source-generation, Rule audit, grouping, validation and evidence
JSON are engineering records, not authoring files. They remain available
in the original CI artifacts but are deliberately excluded from this ZIP.

Pre-alpha example content: not DISA-issued or production-certified.
"""


def native_yaml(name: str) -> bool:
    path = PurePosixPath(name)
    parts = path.parts
    if path.is_absolute() or ".." in parts or "\\" in name or not name.endswith(".yaml"):
        return False
    if len(parts) < 3 or parts[0] != "authoring":
        return False
    if parts[1] == "shared":
        return len(parts) >= 5 and parts[2] == "assessments"
    if parts[1] not in BENCHMARKS:
        return False
    if len(parts) == 3:
        return parts[2] in {"benchmark.yaml", "applicability.yaml"}
    return len(parts) >= 4 and parts[2] in {"rules", "assessments"}


def curate(source: Path, destination: Path, expected_yaml: int | None = None) -> dict:
    excluded = []
    retained = {}
    seen = set()
    with zipfile.ZipFile(source) as src:
        if src.testzip() is not None:
            raise ValueError("Input ZIP failed integrity verification")
        for info in src.infolist():
            name = info.filename
            if name in seen:
                raise ValueError(f"Duplicate input member: {name}")
            seen.add(name)
            if info.is_dir():
                continue
            if native_yaml(name):
                retained[name] = src.read(info)
            elif name == "README.md":
                continue
            elif name.startswith("authoring/") and PurePosixPath(name).name in ENGINEERING_SIDECARS:
                excluded.append(name)
            else:
                raise ValueError(f"Unclassified source member: {name}; classify explicitly")
    roots = {f"authoring/{key}/benchmark.yaml" for key in BENCHMARKS}
    if not roots.issubset(retained):
        raise ValueError(f"Missing Benchmark roots: {sorted(roots - retained.keys())}")
    if not any(name.startswith("authoring/shared/assessments/") for name in retained):
        raise ValueError("Shared Assessments missing")
    if expected_yaml is not None and len(retained) != expected_yaml:
        raise ValueError(f"Expected {expected_yaml} YAML files; got {len(retained)}")
    if len(excluded) != len(ENGINEERING_SIDECARS) * len(BENCHMARKS):
        raise ValueError(f"Expected 48 engineering reports, got {len(excluded)}")
    if Counter(PurePosixPath(name).name for name in excluded) != Counter(
        {sidecar: len(BENCHMARKS) for sidecar in ENGINEERING_SIDECARS}
    ):
        raise ValueError("Unexpected engineering report distribution")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as dst:
        for name, data in [("README.md", README.encode("utf-8"))] + sorted(retained.items()):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o100644 & 0xffff) << 16
            dst.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    with zipfile.ZipFile(destination) as dst:
        if dst.testzip() is not None:
            raise ValueError("Output ZIP integrity verification failed")
        output_yaml = {name: dst.read(name) for name in dst.namelist() if name.endswith(".yaml")}
        if output_yaml != retained or len(dst.namelist()) != len(retained) + 1:
            raise ValueError("Native YAML bytes changed or non-native files leaked")
    return {
        "source_zip_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "curated_zip_sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
        "native_yaml_unchanged": True,
        "native_yaml_files": len(retained),
        "removed_engineering_json_files": len(excluded),
        "removed_types": dict(sorted(Counter(PurePosixPath(n).name for n in excluded).items())),
        "benchmarks": sorted(BENCHMARKS),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_zip", type=Path)
    parser.add_argument("output_zip", type=Path)
    parser.add_argument("--expected-yaml", type=int)
    args = parser.parse_args()
    print(json.dumps(curate(args.input_zip, args.output_zip, args.expected_yaml), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
