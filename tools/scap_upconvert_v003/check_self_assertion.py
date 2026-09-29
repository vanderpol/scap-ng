#!/usr/bin/env python3
"""Conformance gate for SCAP-NG v003 variable/expression lowering.

This intentionally uses the SCAP 1.4 Self-Assertion corpus as an external
language-semantics test suite. The goal is not to reproduce OVAL serialization;
it is to prove that native SCAP-NG can represent the source semantics without
silently dropping unsupported variable/function behavior.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys
import urllib.request
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from scap_upconvert_v003.build_rhel9_review_slice import (
    local,
    lower_definition,
    semantic_id,
    unsupported_definition_features,
)
from scap_upconvert_v003.cleanliness import assert_native_clean

BASE = (
    "https://raw.githubusercontent.com/OVAL-Community/SCAP-Self-Assertion/"
    "main/SCAP_1.4/OVAL_Test_Content/agnostic/"
)

FILES = [
    "ind-def_variable_test.xml",
    "oval-def_arithmetic_function.xml",
    "oval-def_begin_function.xml",
    "oval-def_concat_function.xml",
    "oval-def_constant_variable.xml",
    "oval-def_end_function.xml",
    "oval-def_escape_regex_function.xml",
    "oval-def_literal_component.xml",
    "oval-def_local_variable.xml",
    "oval-def_merge.xml",
    "oval-def_object_component.xml",
    "oval-def_regex_capture_function.xml",
    "oval-def_split_function.xml",
    "oval-def_substring_function.xml",
    "oval-def_time_difference_function.xml",
    "oval-def_variable_component.xml",
    "oval_check_enumeration_variable_values.xml",
]

def fetch_xml(name: str) -> ET.Element:
    request = urllib.request.Request(
        BASE + name,
        headers={"User-Agent": "scap-ng-v003-self-assertion"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return ET.fromstring(response.read())

def definition_nodes(root: ET.Element):
    return [
        node
        for node in root.iter()
        if local(node.tag) == "definition" and node.get("id")
    ]

def main() -> int:
    failures = []
    converted = 0
    per_file = []

    for name in FILES:
        root = fetch_xml(name)
        definitions = definition_nodes(root)
        file_failures = 0

        for definition in definitions:
            definition_id = definition.get("id")
            unsupported = unsupported_definition_features(root, definition_id)
            assessment_id = "self-assertion." + semantic_id(definition_id, "definition")
            assessment, error = lower_definition(root, definition_id, assessment_id)

            problems = []
            if unsupported:
                problems.append({"unsupported_features": unsupported})
            if assessment is None:
                problems.append({"lowering_error": error})

            if assessment is not None:
                try:
                    assert_native_clean(assessment)
                except Exception as exc:
                    problems.append({"cleanliness_error": str(exc)})

            if problems:
                file_failures += 1
                failures.append(
                    {
                        "file": name,
                        "definition_id": definition_id,
                        "problems": problems,
                    }
                )
            else:
                converted += 1

        per_file.append(
            {
                "file": name,
                "definitions": len(definitions),
                "failures": file_failures,
            }
        )

    report = {
        "files": len(FILES),
        "definitions_converted": converted,
        "failures": len(failures),
        "per_file": per_file,
        "failure_details": failures,
    }
    print(json.dumps(report, indent=2, sort_keys=True))

    if failures:
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
