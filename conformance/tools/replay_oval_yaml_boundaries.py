#!/usr/bin/env python3
"""Collect the pinned UNIX YAML boundary cases with an unprivileged OpenSCAP."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import subprocess
from tempfile import TemporaryDirectory
import xml.etree.ElementTree as ET

from qualify_merge_fixture import require_equal
from runner import CONFORMANCE, load

CORPUS = CONFORMANCE / "oval-self-assertion"
BOUNDARIES = CORPUS / "yaml-boundaries"
RESULT = "{http://oval.mitre.org/XMLSchema/oval-results-5}"
SYSC = "{http://oval.mitre.org/XMLSchema/oval-system-characteristics-5}"
PREFIX = "oval:org.scapng.conformance"


def observed_result(result, number):
    tree = ET.parse(result)
    definition_id = f"{PREFIX}:def:{number}"
    test_id = f"{PREFIX}:tst:{number}"
    object_id = f"{PREFIX}:obj:{number}"
    definition, = tree.findall(f".//{RESULT}definition[@definition_id='{definition_id}']")
    test, = tree.findall(f".//{RESULT}test[@test_id='{test_id}']")
    obj, = tree.findall(f".//{SYSC}object[@id='{object_id}']")
    return {
        "definition": definition_id, "test": test_id, "object": object_id,
        "definition_outcome": definition.attrib["result"],
        "test_outcome": test.attrib["result"],
        "object_flag": obj.attrib["flag"],
        "items": len(obj.findall(SYSC + "reference")),
    }


def replay(oscap):
    if os.geteuid() == 0:
        raise ValueError("Run the read-permission witness as an unprivileged user")
    expected = load(BOUNDARIES / "expected.json")
    platform = expected["platforms"]["unix"]
    source = BOUNDARIES / platform["xml"]
    fixture_root = Path(platform["fixture_root"])
    version = subprocess.check_output([oscap, "--version"], text=True, timeout=10)
    scanner = re.search(r"OpenSCAP command line tool \(oscap\) (\S+)", version).group(1)
    advertised_oval = re.search(r"OVAL Version: (\S+)", version).group(1)
    observed = {}
    fixture_root.mkdir(mode=0o700)
    copied = []
    try:
        for name, row in expected["cases"].items():
            path = fixture_root / row["destination"]
            raw = (CORPUS / row["source_fixture"]).read_bytes()
            path.write_bytes(raw)
            copied.append(path)
            path.chmod(0o000 if name == "unreadable" else 0o600)
            if name == "unreadable":
                try:
                    path.read_bytes()
                except PermissionError:
                    pass
                else:
                    raise ValueError("OS bypassed the fixture file permissions")
        with TemporaryDirectory(prefix="scap-ng-yaml-boundary-results-") as output:
            for name, row in expected["cases"].items():
                number = row["source_ids"][0]
                filename = f"{output}/{name}.xml"
                command = [oscap, "oval", "eval", "--skip-validation", "--id", f"{PREFIX}:def:{number}",
                           "--results", filename, str(source)]
                run = subprocess.run(command, text=True, capture_output=True, timeout=20)
                if run.returncode not in (0, 2):
                    raise ValueError(f"{name}: collector failed: {run.stderr.strip()}")
                record = observed_result(filename, number)
                outcome = expected["outcomes_by_source_collection_flag"][record["object_flag"]]
                require_equal(record["test_outcome"], outcome, name)
                require_equal(record["definition_outcome"], outcome, name)
                if "complete_expectation" in row:
                    require_equal(outcome, row["complete_expectation"], name)
                path = fixture_root / row["destination"]
                record.update(
                    fixture_sha256=sha256((CORPUS / row["source_fixture"]).read_bytes()).hexdigest(),
                    fixture_mode=f"{path.stat().st_mode & 0o777:04o}",
                )
                observed[name] = record
    finally:
        for path in copied:
            path.unlink()
        fixture_root.rmdir()

    return {
        "format": "scap-ng-oval-yaml-boundary-observation-1",
        "scanner": "OpenSCAP", "scanner_version": scanner, "advertised_oval_version": advertised_oval,
        "source": source.relative_to(CONFORMANCE).as_posix(),
        "source_sha256": sha256(source.read_bytes()).hexdigest(),
        "source_schema_pin": expected["source_schema_pin"], "observations": observed,
        "qualification": "Real UNIX file collection. The pinned 5.12.3 XSD and Schematron are checked separately.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--oscap", default="oscap")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    output = json.dumps(replay(args.oscap), indent=2, sort_keys=True) + "\n"
    if args.check and (BOUNDARIES / "openscap-unix.json").read_text(encoding="utf-8") != output:
        raise SystemExit("OpenSCAP boundary receipt differs from observed outcomes")
    print(output, end="")
