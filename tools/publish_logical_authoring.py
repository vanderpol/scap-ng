#!/usr/bin/env python3
"""Promote six-STIG authoring ZIP references from legacy paths to logical IDs.

Only reference scalar values are edited; all Assessment content remains unchanged.
Duplicate Assessment IDs fail within every Benchmark's local+shared scope.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import posixpath
from pathlib import Path, PurePosixPath
import re
import zipfile
import yaml

BENCHMARKS = frozenset({
    "rhel_9", "oracle_linux_9", "ms_windows_11",
    "ms_windows_server_2025", "ms_windows_server_dns",
    "apache_server_2-4_unix_server",
})
README = """# SCAP-NG 0.3 — six complete authoring trees

Open `authoring/<benchmark>/benchmark.yaml` and the Rule YAML files.
Rules select Assessments by stable logical IDs. Directory names and file paths
are storage/navigation choices, never authored dependency references.
All six Benchmarks share `authoring/shared/assessments/`.
Each Assessment identity must be unique in its Benchmark's local+shared scope.
Compilation SHALL reject duplicate IDs, missing bindings and ambiguous refs.
Existing Assessment metadata (including the current v0.3 `version` field)
is preserved, pending the separate authoring simplification review.

Experimental pre-alpha content, not DISA-issued or certified.
"""
ASSESSMENT_REF = re.compile(r"^(?P<prefix>[ \t]+assessment:[ \t]+)(?P<ref>[^\s#]+)(?P<suffix>[ \t]*(?:#.*)?)$", re.MULTILINE)
CATALOG_REF = re.compile(r"^(?P<prefix>[ \t]+applicability_catalog:[ \t]+)(?P<ref>[^\s#]+)(?P<suffix>[ \t]*(?:#.*)?)$", re.MULTILINE)


def promote(input_zip: Path, output_zip: Path, *, expected_yaml: int = 4012) -> dict:
    with zipfile.ZipFile(input_zip) as archive:
        if archive.testzip() is not None:
            raise ValueError("Bad input ZIP CRC")
        members = {i.filename: archive.read(i) for i in archive.infolist() if not i.is_dir()}
    if len(members) != expected_yaml + 1 or len([k for k in members if k.endswith(".yaml")]) != expected_yaml:
        raise ValueError("Source is not the expected clean native authoring ZIP")
    if set(members) - {"README.md"} - {n for n in members if n.endswith(".yaml")}:
        raise ValueError("Unexpected non-authoring file")
    data = {}
    assessments_by_path = {}
    for path, body in members.items():
        if not path.endswith(".yaml"):
            continue
        doc = yaml.safe_load(body)
        if not isinstance(doc, dict) or len(doc) != 1:
            raise ValueError(f"Invalid native document: {path}")
        kind, payload = next(iter(doc.items()))
        if not isinstance(payload, dict):
            raise ValueError(f"Invalid native content: {path}")
        data[path] = (kind, payload)
        if kind == "assessment":
            aid = payload.get("id")
            if not isinstance(aid, str) or not aid:
                raise ValueError(f"Assessment has no logical ID: {path}")
            assessments_by_path[path] = aid
    if len(assessments_by_path) != 2433:
        raise ValueError(f"Expected 2433 Assessments, found {len(assessments_by_path)}")
    for key in BENCHMARKS:
        visible = defaultdict(list)
        prefixes = (f"authoring/{key}/assessments/", f"authoring/{key}/shared/", "authoring/shared/")
        for path, aid in assessments_by_path.items():
            if path.startswith(prefixes):
                visible[aid].append(path)
        duplicates = {aid: paths for aid, paths in visible.items() if len(paths) > 1}
        if duplicates:
            raise ValueError(f"Duplicate Assessment IDs in {key} scope: {duplicates}")

    changed = dict(members)
    counts = Counter()
    for path, (kind, payload) in data.items():
        parts = PurePosixPath(path).parts
        if len(parts) < 3 or parts[0] != "authoring" or parts[1] not in BENCHMARKS:
            continue
        original = members[path].decode("utf-8")
        if kind == "rule" and parts[2] == "rules":
            category = "rule_choices"
        elif kind == "applicability" and parts[2] == "applicability.yaml":
            category = "applicability_bindings"
        else:
            category = None
        if category:
            def replace(match):
                ref = match.group("ref")
                if "/" not in ref and "\\" not in ref and not ref.endswith((".yaml", ".yml")):
                    if ref not in assessments_by_path.values():
                        raise ValueError(f"Unknown Assessment logical ID {ref} in {path}")
                    return match.group(0)
                target = posixpath.normpath(posixpath.join(posixpath.dirname(path), ref))
                if target not in assessments_by_path:
                    raise ValueError(f"Missing Assessment {ref} from {path} -> {target}")
                counts[category] += 1
                return match.group("prefix") + assessments_by_path[target] + match.group("suffix")
            changed[path] = ASSESSMENT_REF.sub(replace, original).encode("utf-8")
        elif kind == "benchmark" and parts[2] == "benchmark.yaml":
            def replace_catalog(match):
                ref = match.group("ref")
                if "/" not in ref and not ref.endswith((".yaml", ".yml")):
                    return match.group(0)
                target = posixpath.normpath(posixpath.join(posixpath.dirname(path), ref))
                if target not in data or data[target][0] != "applicability":
                    raise ValueError(f"Missing applicability catalog {ref}: {path}")
                counts["benchmark_catalogs"] += 1
                return match.group("prefix") + data[target][1]["id"] + match.group("suffix")
            changed[path] = CATALOG_REF.sub(replace_catalog, original).encode("utf-8")

    expected = {"rule_choices": 4525, "applicability_bindings": 49, "benchmark_catalogs": 6}
    if dict(counts) != expected:
        raise ValueError(f"Unexpected reference rewrite coverage: {dict(counts)} != {expected}")
    for path in assessments_by_path:
        if members[path] != changed[path]:
            raise ValueError(f"Assessment payload modified: {path}")
    for path, body in changed.items():
        if path.endswith(".yaml") and (b"assessment: ../" in body or b"assessment: assessments/" in body or b"applicability_catalog: applicability.yaml" in body):
            raise ValueError(f"Path references remained: {path}")
    changed["README.md"] = README.encode("utf-8")
    output_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_zip, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as out:
        for path, body in sorted(changed.items()):
            info = zipfile.ZipInfo(path, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o100644 & 0xffff) << 16
            out.writestr(info, body, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    with zipfile.ZipFile(output_zip) as out:
        if out.testzip() is not None or {n: out.read(n) for n in out.namelist()} != changed:
            raise ValueError("Output archive not verified")
    return {
        "yaml_count": expected_yaml,
        "assessment_files_byte_identical": len(assessments_by_path),
        "rewrites": dict(counts),
        "sha256": hashlib.sha256(output_zip.read_bytes()).hexdigest(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_zip", type=Path)
    parser.add_argument("output_zip", type=Path)
    args = parser.parse_args()
    print(json.dumps(promote(args.input_zip, args.output_zip), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
