#!/usr/bin/env python3
"""Canonical 0.4.0 source guards; legacy research import is a separate phase.

The version-local schema still accepts certain old imported source shapes used
by earlier research pipelines. The *canonical generated archive* must not.
This guards syntax, not OVAL execution/results or native bundle compilation.

Refs #239 #232.
"""
import argparse
import json
from pathlib import Path
import zipfile

import yaml

from build_v04_canonical_six_stigs import promote


def check_test(test, origin):
    if not isinstance(test, dict):
        raise ValueError(f"{origin}: Test must be an object")
    if "collected_items_require" in test:
        raise ValueError(f"{origin}: obsolete collected_items_require alias")
    source = test.get("object")
    if isinstance(source, dict) and "capability" in source:
        raise ValueError(f"{origin}: inline Object capability must be inherited")
    req = test.get("require")
    if isinstance(req, dict):
        if "states" in test:
            raise ValueError(f"{origin}: structured require cannot coexist with legacy states")
        if set(req) == {"items"} and "states_match" in test:
            raise ValueError(f"{origin}: existence-only Test cannot have states_match")
    return True


def check_archive(archive_path):
    documents = tests = 0
    with zipfile.ZipFile(archive_path) as z:
        if z.testzip() is not None:
            raise ValueError("Corrupted archive")
        paths = sorted(x for x in z.namelist()
                       if x.startswith("authoring/") and x.endswith((".yaml", ".json")))
        for path in paths:
            doc = yaml.safe_load(z.read(path)) if path.endswith(".yaml") else json.loads(z.read(path))
            documents += 1
            a = doc.get("assessment") if isinstance(doc, dict) else None
            if not isinstance(a, dict) or a.get("mode") != "automated":
                continue
            for test_id, test in (a.get("tests") or {}).items():
                check_test(test, f"{path} / {test_id}")
                tests += 1
    if documents != 4012:
        raise ValueError(f"Expected 4,001 documents, got {documents}")
    if tests != 1390:
        raise ValueError(f"Expected 1,375 distinct Tests, got {tests}")
    print(f"PASS canonical 0.4 source guards: {documents} documents; {tests} Tests; {archive_path}")


def self_test():
    base = {"capability": "unix.file", "object": {"select": {"filepath": {"equals": "/tmp/test"}}},
            "require": {"items": "one_or_more"}}
    assert check_test(base, "valid")
    invalid = [
        ({**base, "object": {"capability": "unix.file"}}, "inline Object capability"),
        ({**base, "object": {"capability": "windows.registry"}}, "inline Object capability"),
        ({**base, "collected_items_require": "at_least_one_exists"}, "obsolete"),
        ({**base, "states": []}, "legacy states"),
        ({**base, "states_match": "all"}, "states_match"),
        ({**base, "require": "at_least_one_exists",
          "collected_items_require": "at_least_one_exists"}, "obsolete"),
    ]
    for test, expected in invalid:
        try:
            check_test(test, "negative")
        except ValueError as exc:
            if expected not in str(exc):
                raise AssertionError(f"Wrong rejection: {exc}") from exc
        else:
            raise AssertionError(f"Invalid Test accepted: {test}")
    source = {"assessment": {"mode": "automated", "tests": {
        "example-test": {"capability": "unix.file", "object": {"capability": "unix.file"},
                         "require": "at_least_one_exists"}}}}
    candidate, _ = promote(source)
    assert candidate["assessment"]["tests"]["example-test"]["require"] == {"items": "one_or_more"}
    assert check_test(candidate["assessment"]["tests"]["example-test"], "promoted")
    for changes in (
        {"object": {"capability": "windows.registry"}},
        {"collected_items_require": "none_exist"},
    ):
        bad = json.loads(json.dumps(source))
        bad["assessment"]["tests"]["example-test"].update(changes)
        try:
            promote(bad)
        except ValueError:
            pass
        else:
            raise AssertionError(f"Conflicting imported requirement/capability accepted: {changes}")
    print(f"PASS canonical 0.4 rejection fixtures: {len(invalid)} negative; importer conflicts")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--archive", type=Path)
    args = p.parse_args()
    self_test()
    if args.archive:
        check_archive(args.archive)
