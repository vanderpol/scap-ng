#!/usr/bin/env python3
"""Build the self-contained SCAP-NG 0.4.1 authoring schema family.

The published 0.4.0 schema/ tree is read-only input. An exact pinned
0.4.1 copy is emitted at schema/v0.4.1/ with new absolute $id/URI targets.
Only the 0.4.1 Variable declaration/type-inference contract is changed.

  python3 tools/build_schema_v041.py
  python3 tools/build_schema_v041.py --check

This has no external dependencies and NEVER overwrites schema/*.schema.json.
Do not count schema/v0.4.1 as part of the historical 0.4.0 root family.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "schema"
DEST = SOURCE / "v0.4.1"
OLD = "0.4.0"
NEW = "0.4.1"
SOURCE_URI = "https://scap-ng.dev/schema/v0.4.0/"
TARGET_URI = "https://scap-ng.dev/schema/v0.4.1/"
MANIFEST = "scap-ng/v0.4.1/source-and-output-sha256/1"


def normalized_content(relative: Path, original: bytes) -> bytes:
    text = original.decode("utf-8")
    # This is a publication version, not a semantic clone at the old URI.
    text = text.replace(SOURCE_URI, TARGET_URI).replace(OLD, NEW)
    if relative.name == "variable-expression.schema.json":
        schema = json.loads(text)
        declaration = schema["$defs"]["declaration"]
        assert declaration["required"] == ["kind", "datatype", "expression"]
        assert "datatype" in declaration["properties"]
        declaration["required"] = ["kind", "expression"]
        del declaration["properties"]["datatype"]
        declaration["allOf"] = [
            item for item in declaration.get("allOf", [])
            if "datatype" not in item.get("then", {}).get("properties", {})
        ]
        declaration["description"] = (
            "Declare a native Variable with kind and expression; the resulting "
            "datatype is inferred from typed literals, referenced Variables, "
            "canonical collected Item fields, and function output contracts. "
            "Declaration datatype is forbidden. A typed literal remains "
            "available for non-JSON value domains and ambiguous values. "
            "Neither a numeric-looking string nor unavailable evidence "
            "authorizes an implicit cast."
        )
        schema["description"] = (
            "SCAP-NG 0.4.1 Variable expressions with inferred result datatypes. "
            "Type, status, and cardinality are separate semantic dimensions."
        )
        schema["x-last-modified"] = "2026-11-13"
        text = json.dumps(schema, ensure_ascii=False, indent=2) + "\n"
    elif relative.name == "assessment.schema.json":
        schema = json.loads(text)
        schema["properties"]["assessment"]["properties"]["variables"]["description"] = (
            "Named Variables with inferred result types, defined by kind and "
            "expression. No redundant declaration datatype is accepted. "
            "Typed literal payloads and collected field contracts are retained."
        )
        schema["properties"]["assessment"]["properties"]["specification"][
            "properties"]["version"] = {
                "const": "0.4.1",
                "description": "This Assessment uses the 0.4.1 authoring contract."
            }
        schema["x-last-modified"] = "2026-11-13"
        text = json.dumps(schema, ensure_ascii=False, indent=2) + "\n"
    return text.encode("utf-8")


def all_files():
    for path in sorted(SOURCE.rglob("*")):
        if not path.is_file() or DEST in path.parents:
            continue
        if path.is_symlink():
            raise ValueError(f"unexpected symlink in source schema: {path}")
        yield path.relative_to(SOURCE), path.read_bytes()


def manifest_payload(pairs):
    return {
        "format": MANIFEST,
        "source_schema_version": OLD,
        "target_schema_version": NEW,
        "source_schema_uri": SOURCE_URI,
        "target_schema_uri": TARGET_URI,
        "original_0_4_0_untouched": True,
        "files": [
            {
                "path": str(path).replace("\\", "/"),
                "source_sha256": hashlib.sha256(raw).hexdigest(),
                "target_sha256": hashlib.sha256(out).hexdigest(),
            }
            for path, raw, out in pairs
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify committed outputs, never write")
    args = parser.parse_args()
    pairs = [
        (path, raw, normalized_content(path, raw))
        for path, raw in all_files()
    ]
    files = {path for path, _, _ in pairs}
    expected_manifest = json.dumps(manifest_payload(pairs), indent=2) + "\n"
    outputs = {path: contents for path, _, contents in pairs}
    outputs[Path("source-and-output-sha256.json")] = expected_manifest.encode("utf-8")
    missing, mismatched = [], []
    for relative, body in outputs.items():
        dest = DEST / relative
        if args.check:
            if not dest.exists():
                missing.append(str(relative))
            elif dest.read_bytes() != body:
                mismatched.append(str(relative))
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(body)

    if args.check:
        unexpected = sorted(
            str(p.relative_to(DEST))
            for p in DEST.rglob("*")
            if p.is_file() and p.relative_to(DEST) not in outputs
        )
        if missing or mismatched or unexpected:
            raise SystemExit(
                f"0.4.1 is not an exact copy of its source contract: "
                f"missing={missing[:10]}, changed={mismatched[:10]}, "
                f"unexpected={unexpected[:10]}"
            )

    print(
        f"SCAP-NG {NEW}: {len(files)} source files, "
        f"{len(outputs)} versioned outputs; "
        f"{'exactly verified' if args.check else 'generated'}"
    )


if __name__ == "__main__":
    main()
