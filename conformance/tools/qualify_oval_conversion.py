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

from oval_source_audit import require_pin, scan_xml
from runner import CONFORMANCE, ROOT, load, validator

SOURCE_PIN = "4f116d86ac1218586aa0a1294c696947121a1ccc"
CORPUS = CONFORMANCE / "oval-self-assertion"


def convert(converter, schema, schema_commit, source_pin, path, checksum, definition, test, output,
            expected_native_test=None):
    command = [
        converter, "--schema-root", str(schema), "--sha256", checksum,
        "--source-commit", source_pin, "--source-path", path.relative_to(ROOT).as_posix(),
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
    if (trace["definition_id"], trace["source_commit"], trace["source_sha256"]) != (definition, source_pin, checksum):
        raise ValueError(f"{definition}: incorrect source identity in trace")
    if trace["schema_commit"] != schema_commit:
        raise ValueError(f"{definition}: converter trace scanned a different schema commit")
    test_bindings = {
        node["native_id"]: node["source_id"] for node in trace["native_identities"]
        if node["kind"] == "test"
    }
    if test_bindings.keys() != assessment["assessment"]["tests"].keys() or set(test_bindings.values()) != {test}:
        raise ValueError(f"{definition}: silently omitted or changed native/source Test identity")
    if expected_native_test is not None:
        actual_test, = assessment["assessment"]["tests"].values()
        if actual_test != expected_native_test:
            raise ValueError(f"{definition}: production Test differs from the authored boundary Test")
        row["authored_test_equivalent"] = True
    row.update(
        structural="schema-valid",
        native_tests=test_bindings,
        output_sha256={p.name: sha256(p.read_bytes()).hexdigest() for p in (yaml_path, json_path, trace_path)},
    )
    return row


def authored_boundary_tests(expectation_path):
    if expectation_path is None:
        return {}
    manifest = load(expectation_path)
    by_source = {}
    for index, platform in enumerate(manifest["platforms"].values()):
        source = (expectation_path.parent / platform["xml"]).resolve(strict=True)
        native = load(expectation_path.parent / platform["native"])["assessment"]["tests"]
        for case, row in manifest["cases"].items():
            number = row["source_ids"][index]
            by_source[(source, str(number))] = native[f"{case}-test"]
    return by_source


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--converter", default="scapng-convert-v04")
    parser.add_argument("--schema-root", type=Path, required=True,
                        help="flat schema/ directory checked out at the exact conformance schema commit")
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--source-pin", default=SOURCE_PIN)
    parser.add_argument("--boundary-expectations", type=Path,
                        help="paired boundary manifest used to compare exact emitted Test payloads")
    parser.add_argument("--receipt", type=Path, default=CONFORMANCE / "qualification/oval-supplement-conversion.json")
    parser.add_argument("paths", type=Path, nargs="*", help="optional explicit corpus XML documents")
    args = parser.parse_args()
    version = json.loads(subprocess.check_output([args.converter, "--version"], text=True))
    manifest = load(CONFORMANCE / "manifest.json")
    schema = args.schema_root.resolve(strict=True)
    schema_commit = manifest["schema_commit"]
    require_pin(schema.parent, schema_commit)
    if version["flat_schema_family_sha256"] != manifest["schema_family_sha256"]:
        raise SystemExit("production converter schema family differs from canonical corpus")

    authored = authored_boundary_tests(args.boundary_expectations)
    jobs = []
    with TemporaryDirectory(prefix="scap-ng-oval-conversion-") as directory:
        output_root = Path(directory)
        paths = [path.resolve(strict=True) for path in args.paths] or sorted(CORPUS.glob("*/*.xml"))
        for path in sorted(paths):
            raw = path.read_bytes()
            source_raw = subprocess.check_output(
                ["git", "-C", str(ROOT), "show", f"{args.source_pin}:{path.relative_to(ROOT).as_posix()}"],
            )
            if raw != source_raw:
                raise SystemExit(f"source bytes changed since the pinned commit: {path}")
            doc, tests = scan_xml(raw)
            by_suffix = {test.rsplit(":", 1)[-1]: test for _, test in tests}
            checksum = sha256(raw).hexdigest()
            for definition in doc["ids"]["definitions"]:
                suffix = definition.rsplit(":", 1)[-1]
                jobs.append((
                    args.converter, schema, schema_commit, args.source_pin, path, checksum, definition,
                    by_suffix[suffix], output_root / suffix, authored.pop((path, suffix), None),
                ))
        if authored:
            raise SystemExit("missing XML for authored YAML boundary Tests")
        try:
            with ThreadPoolExecutor(max_workers=args.jobs) as pool:
                records = list(pool.map(lambda job: convert(*job), jobs))
        except (ValueError, ValidationError) as error:
            raise SystemExit(str(error)) from error
    report = {"source_pin": args.source_pin, "schema_pin": schema_commit,
              "converter": version, "definitions": records}
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.check:
        if args.receipt.read_text(encoding="utf-8") != rendered:
            raise SystemExit(f"stale conversion receipt: {args.receipt}")
    print(rendered, end="")


if __name__ == "__main__":
    main()
