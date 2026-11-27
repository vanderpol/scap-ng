#!/usr/bin/env python3
"""Build the small Issue #87 content package from the canonical YAML witnesses."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

try:
    from .runner import CONFORMANCE, load, schema_validator
except ImportError:
    from runner import CONFORMANCE, load, schema_validator


def json_bytes(document):
    return (json.dumps(document, indent=2, sort_keys=True) + "\n").encode()


def build(output):
    sources = load(CONFORMANCE / "content-package/sources.json")
    if sources["schema_pin"] != load(CONFORMANCE / "manifest.json")["schema_commit"]:
        raise ValueError("content fixture sources use a different schema pin")

    payloads = {}
    objects = {}
    for row in sources["members"]:
        kind = row["kind"]
        document = load(CONFORMANCE / row["source"])
        body = document[kind]
        if kind == "rule":
            body["organizational_input_requirements"] = sources["compiled_rule_requirements"][body["id"]]
        schema_validator(kind + ".schema.json").validate(document)

        object_type = "applicability_catalog" if kind == "applicability" else kind
        identity = object_type + ":" + body["id"]
        version = body.get("version", 1)
        if kind == "benchmark":
            benchmark_id = body["id"]
            benchmark_version = version
            identity = kind
        if kind == "assessment":
            document = {
                "schema_family_sha256": sources["assessment_closure_sha256"],
                "assessment_document": document,
            }
        payload = json_bytes(document)
        objects[identity] = {
            "type": object_type, "version": version, "path": row["path"],
            "sha256": sha256(payload).hexdigest(), "size": len(payload),
        }
        payloads[row["path"]] = payload

    manifest = {
        "format": "scap-ng-package-manifest", "format_version": "0.4.1",
        "benchmark_id": benchmark_id, "benchmark_version": benchmark_version,
        "entrypoint": sources["entrypoint"], "objects": objects,
        "integrity": {"algorithm": "sha-256", "unexpected_members": "reject"},
        "build_provenance": {"source": "canonical Issue #87 policy fixtures",
                             "schema_commit": sources["schema_pin"]},
        "signature": {"format": None, "path": None, "certificate_path": None, "trust": None},
    }
    schema_validator("package-manifest.schema.json").validate(manifest)
    output.mkdir()
    payloads["manifest.json"] = json_bytes(manifest)
    for name, payload in payloads.items():
        path = output / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="new directory for the assembled fixture")
    build(parser.parse_args().output)
