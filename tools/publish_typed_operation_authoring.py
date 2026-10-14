#!/usr/bin/env python3
"""Publish a conservative readable 0.3 authoring ZIP with typed operations.

The canonical Assessment remains unchanged after source expansion. Round-trip
editing preserves author comments/quotes when possible (ruamel round-trip),
and every edited YAML document is reparsed with the production PyYAML parser
to prove an exact AST match with the approved typed-operator rewrite.

This is a source transform, not an OVAL runtime or scanner equivalence proof.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
from io import StringIO
import json
from pathlib import Path
import zipfile

from ruamel.yaml import YAML
import yaml

from research_type_syntax_codec import to_authoring
from native_v03_authoring_codec import canonicalize_assessment_document


def compact_into_roundtrip(root, original, compact):
    """Change only keys removed/changed by the verified typed rewrite."""
    if isinstance(original, dict):
        if set(original) - set(compact) not in (set(), {"datatype"}):
            raise ValueError("unexpected deleted authoring keys")
        if not isinstance(root, dict) or not isinstance(compact, dict):
            raise ValueError("roundtrip YAML mismatch")
        for key in list(original):
            if key not in compact:
                del root[key]
            elif key in original and isinstance(original[key], (dict, list)):
                compact_into_roundtrip(root[key], original[key], compact[key])
            elif original[key] != compact[key]:
                if key != "operation" or not (isinstance(original[key], str) and
                                               isinstance(compact[key], str)):
                    raise ValueError("unexpected authored scalar mutation")
                root[key] = compact[key]
    elif isinstance(original, list):
        if len(original) != len(compact) or len(root) != len(original):
            raise ValueError("unexpected authoring array mutation")
        for a, b, c in zip(root, original, compact):
            compact_into_roundtrip(a, b, c)
    elif original != compact:
        raise ValueError("unexpected non-dict semantic authoring change")


def prepare_zip(input_zip: Path, output_zip: Path, *, expected_assessments=2433):
    statistics = Counter()
    created = {}
    source_hash = sha256(input_zip.read_bytes()).hexdigest()
    renderer = YAML(typ="rt")
    renderer.version = (1, 1)
    renderer.preserve_quotes = True
    renderer.width = 180

    with zipfile.ZipFile(input_zip) as archive:
        if archive.testzip() is not None:
            raise ValueError("Invalid input ZIP member checksum")
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError("Duplicate input ZIP member")
        for name in names:
            raw = archive.read(name)
            if not name.endswith(".yaml"):
                created[name] = raw
                continue
            original = yaml.safe_load(raw)
            if "assessment" not in original:
                created[name] = raw
                statistics["nonassessment_yaml"] += 1
                continue
            statistics["assessment_yaml"] += 1
            version = ((original["assessment"].get("specification") or {}).get("version"))
            if version != "0.3.0":
                raise ValueError(f"Unexpected non-0.3 Assessment: {name}")
            compact = to_authoring(original, strategy="typed-operators", stats=statistics)
            assert canonicalize_assessment_document(compact) == original, name
            if compact == original:
                created[name] = raw
                continue
            rt = renderer.load(raw.decode("utf-8"))
            compact_into_roundtrip(rt, original, compact)
            output = StringIO()
            renderer.dump(rt, output)
            rewritten = output.getvalue().encode("utf-8")
            if yaml.safe_load(rewritten) != compact:
                raise ValueError(f"Incorrect edited source YAML: {name}")
            assert canonicalize_assessment_document(yaml.safe_load(rewritten)) == original, name
            created[name] = rewritten
            statistics["rewritten_assessment_yaml"] += 1

    if statistics["assessment_yaml"] != expected_assessments:
        raise ValueError(f"Unexpected Assessment count: {statistics}")
    if statistics["inferred_scalar"] != 4528 or statistics["typed_operator"] != 4:
        raise ValueError(f"Unexpected six-STIG datatype simplifications: {statistics}")
    if statistics["explicit_compare_as"]:
        raise ValueError("Rejected compare_as unexpectedly generated")

    output_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_zip, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as dst:
        for name, data in sorted(created.items()):
            item = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            item.compress_type = zipfile.ZIP_DEFLATED
            item.external_attr = (0o100644 & 0xffff) << 16
            dst.writestr(item, data)
    with zipfile.ZipFile(output_zip) as out:
        if out.testzip() is not None or set(out.namelist()) != set(created):
            raise ValueError("Output archive corrupt/incomplete")
        for name, value in created.items():
            if out.read(name) != value:
                raise ValueError(f"Output byte mismatch: {name}")

    return {
        "input_sha256": source_hash,
        "output_sha256": sha256(output_zip.read_bytes()).hexdigest(),
        "documents": len(created),
        "counts": dict(sorted(statistics.items())),
        "scope": "source-only, canonical assessment AST preserved, no scanner execution",
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("input_zip",type=Path)
    p.add_argument("output_zip",type=Path)
    p.add_argument("--report",type=Path)
    args=p.parse_args()
    result=prepare_zip(args.input_zip,args.output_zip)
    data=json.dumps(result,sort_keys=True,indent=2)+"\n"
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(data,encoding="utf-8")
    print(data)


if __name__ == "__main__":
    main()
