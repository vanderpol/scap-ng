#!/usr/bin/env python3
"""Public subprocess CLI smoke using schema-valid miniature 0.4 authoring.

This exercises the *existing* compiler CLI on fully validated input, rather
than relying on historical prototype unit fixtures that bypass schema checks.
It does not imply OVAL-to-Benchmark authorship or live scanner conformance.
Refs #232 #248.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

import yaml

from v04_a_authoring_graph_index import canonical_json
from v04_canonical_unsigned_package import build_package
from v04_native_bundle_compiler import verify_bundle


COMPILER = Path(__file__).with_name("v04_native_bundle_compiler.py")


def schema_valid_docs():
    docs = {
        "authoring/demo/benchmark.demo.json": {"benchmark": {
            "id": "demo", "version": {"value": "1"},
            "assessment_specifications": [{
                "id": "scap-ng.pre-alpha.assessment", "version": "0.4.0"}],
            "rules": ["r1"],
        }},
        "authoring/demo/rules/r1.json": {"rule": {
            "id": "r1",
            "assessment_choices": {"automated": {"assessment": "assessment-1"}},
            "default_assessment_choice": "automated",
        }},
        "authoring/demo/assessments/a1.json": {"assessment": {
            "id": "assessment-1", "mode": "automated",
            "specification": {"id": "scap-ng.pre-alpha.assessment",
                              "version": "0.4.0"},
            "evaluate": {"test": "file-mode-test"},
            "tests": {"file-mode-test": {
                "test_title": "File mode is compliant", "capability": "unix.file",
                "object": {"filepath": "/etc/example"},
                "require": {"items_found": "one_or_more", "items_satisfying": "every",
                            "fields": {"mode": {"equals": "0600",
                                "values_found": "one_or_more", "values_matching": "every"}}},
                "reported_elements": "all",
            }},
        }},
    }
    benchmark = docs["authoring/demo/benchmark.demo.json"]["benchmark"]
    benchmark.update({
        "ng_schema_version": "0.4.0", "use_case": "compliance",
        "title": [{"text": "Portable 0.4 compiler smoke", "language": "en"}],
        "description": [{"text": "Small complete authoring graph", "language": "en"}],
        "language": "en", "status": [], "metadata": {}, "notices": [],
        "front_matter": [], "rear_matter": [], "references": [], "text_blocks": [],
        "platform": {"id": "demo-platform", "title": "Demonstration",
                     "applicability": {}},
        "applicability_catalog": "demo-applicability",
        "scoring": [], "parameters": [], "default_selection": True,
        "groups": [], "profiles": [],
    })
    rule = docs["authoring/demo/rules/r1.json"]["rule"]
    rule.update({
        "version": "1", "title": "Demonstration Rule",
        "severity": "medium", "role": "full", "weight": 1.0,
        "discussion": "Verify a file permission", "rationale": None,
        "extensions": {}, "warnings": [], "identifiers": [], "references": [],
        "requires": [], "conflicts": [], "applicability": [],
        "parameters": {}, "remediation": {},
        "organizational_input_requirements": {},
    })
    assessment = docs["authoring/demo/assessments/a1.json"]["assessment"]
    assessment.update({
        "version": 1, "assessment_title": "File permission inspection",
        "class": "compliance", "purpose": "assessment",
    })
    return docs


def authoring_archives(docs, directory):
    archives = []
    for suffix in ("json", "yaml"):
        archive = directory / (suffix + ".zip")
        with zipfile.ZipFile(archive, "w") as zf:
            for path, doc in sorted(docs.items()):
                payload = (canonical_json(doc) if suffix == "json" else
                           yaml.safe_dump(doc).encode("utf-8"))
                zf.writestr(path.removesuffix(".json") + "." + suffix,
                            payload)
        archives.append(archive)
    return archives


def run_cli(*args):
    return subprocess.run([sys.executable, str(COMPILER), *map(str, args)],
                          capture_output=True, text=True, check=True)


class PublicNativeCLIRegression(unittest.TestCase):
    def test_schema_valid_source_package_and_dual_archive_cli(self):
        documents = schema_valid_docs()
        raw, _ = build_package(documents, validate_schema=True)
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            source = work / "demo.source-preview.zip"
            source.write_bytes(raw)
            paired_json, paired_yaml = authoring_archives(documents, work)
            report1 = work / "source-report.json"
            report2 = work / "paired-report.json"
            output1 = work / "out-source"
            output2 = work / "out-paired"
            run_cli("--source-package", source, "--output-dir", output1,
                    "--report", report1)
            run_cli("--json-archive", paired_json, "--yaml-archive", paired_yaml,
                    "--output-dir", output2, "--report", report2)
            native1 = (output1 / "demo.scapng").read_bytes()
            native2 = (output2 / "demo.scapng").read_bytes()
            self.assertEqual(native1, native2)
            self.assertEqual(json.loads(report1.read_text()),
                             json.loads(report2.read_text()))
            result = verify_bundle(native1, validate_schema=True)
            self.assertEqual((result["documents"], result["tests"]), (3, 1))
            self.assertFalse(result["scanner_evaluated"])


if __name__ == "__main__":
    unittest.main()
