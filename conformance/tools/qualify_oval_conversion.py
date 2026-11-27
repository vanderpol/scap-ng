#!/usr/bin/env python3
"""Replay current production conversion and verify supplemental source identity."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory

from jsonschema.exceptions import ValidationError

from oval_source_audit import scan_xml
from runner import CONFORMANCE, ROOT, SCHEMA, load, validator

SOURCE_PIN = "4f116d86ac1218586aa0a1294c696947121a1ccc"
CORPUS = CONFORMANCE / "oval-self-assertion"


def convert(converter, path, checksum, definition, test, output):
    command = [
        converter, "--schema-root", str(SCHEMA), "--sha256", checksum,
        "--source-commit", SOURCE_PIN, "--source-path", path.relative_to(ROOT).as_posix(),
        "--oval-definition", definition, "--output", str(output), str(path),
    ]
    process = subprocess.run(command, capture_output=True, text=True)
    row = {"definition": definition, "source_test": test, "exit_code": process.returncode}
    if process.returncode:
        row.update(structural="rejected", diagnostic=process.stderr.strip())
        return row
    yaml_path = output / "assessment.yaml"
    json_path = output / "assessment.json"
    trace_path = output / "source-trace.json"
    assessment = load(yaml_path)
    if assessment != load(json_path):
        raise ValueError(f"{definition}: JSON and YAML Assessment disagree")
    validator().validate(assessment)
    trace = load(trace_path)
    if (trace["definition_id"], trace["source_commit"], trace["source_sha256"]) != (definition, SOURCE_PIN, checksum):
        raise ValueError(f"{definition}: incorrect source identity in trace")
    test_bindings = {
        node["native_id"]: node["source_id"] for node in trace["native_identities"]
        if node["kind"] == "test"
    }
    if test_bindings.keys() != assessment["assessment"]["tests"].keys() or set(test_bindings.values()) != {test}:
        raise ValueError(f"{definition}: silently omitted or changed native/source Test identity")
    row.update(
        structural="schema-valid",
        native_tests=test_bindings,
        output_sha256={p.name: sha256(p.read_bytes()).hexdigest() for p in (yaml_path, json_path, trace_path)},
    )
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--converter", default="scapng-convert-v04")
    parser.add_argument("--jobs", type=int, default=4)
    args = parser.parse_args()
    version = json.loads(subprocess.check_output([args.converter, "--version"], text=True))
    manifest = load(CONFORMANCE / "manifest.json")
    if version["flat_schema_family_sha256"] != manifest["schema_family_sha256"]:
        raise SystemExit("production converter schema family differs from canonical corpus")

    jobs = []
    with TemporaryDirectory(prefix="scap-ng-oval-conversion-") as directory:
        output_root = Path(directory)
        for path in sorted(CORPUS.glob("*/*.xml")):
            raw = path.read_bytes()
            source_raw = subprocess.check_output(
                ["git", "-C", str(ROOT), "show", f"{SOURCE_PIN}:{path.relative_to(ROOT).as_posix()}"],
            )
            if raw != source_raw:
                raise SystemExit(f"source bytes changed since the pinned commit: {path}")
            doc, tests = scan_xml(raw)
            by_suffix = {test.rsplit(":", 1)[-1]: test for _, test in tests}
            checksum = sha256(raw).hexdigest()
            for definition in doc["ids"]["definitions"]:
                suffix = definition.rsplit(":", 1)[-1]
                jobs.append((args.converter, path, checksum, definition, by_suffix[suffix], output_root / suffix))
        try:
            with ThreadPoolExecutor(max_workers=args.jobs) as pool:
                records = list(pool.map(lambda job: convert(*job), jobs))
        except (ValueError, ValidationError) as error:
            raise SystemExit(str(error)) from error
    print(json.dumps({"source_pin": SOURCE_PIN, "converter": version, "definitions": records},
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
