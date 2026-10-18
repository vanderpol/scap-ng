#!/usr/bin/env python3
"""#239: fail-closed 0.4-A draft vs scoped-research authoring boundary.

Not a schema replacement or an OVAL evaluator. This guard prevents accidental
mixed Test-level dialects while the scoped research candidate is unapproved.
Run full version-local and capability-specific JSON Schema validation separately.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSESSMENT_SCHEMA = ROOT / "schema/v0.4.0/assessment.schema.json"
LANGUAGE_SCHEMA = ROOT / "schema/v0.4.0/assessment-language.schema.json"
DRAFT_TEST_REQUIRE = "require"
RESEARCH_TEST_REQUIRE = "collected_items_require"
RESEARCH_FIELD_INHERIT = "state_fields_require"
DRAFT_GROUPS = frozenset(("all", "any", "one", "odd"))
RESEARCH_GROUPS = frozenset(("and", "or"))


class GrammarBoundaryError(ValueError):
    pass


def boundary_schema_report():
    assessment = json.loads(ASSESSMENT_SCHEMA.read_text(encoding="utf-8"))
    language = json.loads(LANGUAGE_SCHEMA.read_text(encoding="utf-8"))
    root_test = assessment["properties"]["assessment"]["properties"]["tests"]["additionalProperties"]
    lang_test = language["$defs"]["test"]
    if assessment.get("x-scap-ng-version") != "0.4.0":
        raise GrammarBoundaryError("unexpected Assessment schema version")
    if language.get("x-scap-ng-version") != "0.4.0":
        raise GrammarBoundaryError("unexpected language schema version")
    if DRAFT_TEST_REQUIRE not in root_test["required"] or DRAFT_TEST_REQUIRE not in lang_test["required"]:
        raise GrammarBoundaryError("base Test-level required vocabulary changed; owner review needed")
    if DRAFT_TEST_REQUIRE not in root_test["properties"] or DRAFT_TEST_REQUIRE not in lang_test["properties"]:
        raise GrammarBoundaryError("base Test requirement key removed")
    if RESEARCH_TEST_REQUIRE in root_test["properties"] or RESEARCH_TEST_REQUIRE in lang_test["properties"]:
        raise GrammarBoundaryError("unapproved scoped Test requirement promoted into draft schema")
    if RESEARCH_FIELD_INHERIT in root_test["properties"] or RESEARCH_FIELD_INHERIT in lang_test["properties"]:
        raise GrammarBoundaryError("unapproved scoped State inheritance promoted into draft schema")
    if lang_test["properties"].get("states_match", {}).get("enum") != ["all", "any", "one", "odd"]:
        raise GrammarBoundaryError("baseline states_match changed")
    scalar = language["$defs"]["scalar_field_predicate"]
    if DRAFT_TEST_REQUIRE not in scalar["required"]:
        raise GrammarBoundaryError("baseline scalar field requirement changed")
    return {
        "status": "DRAFT_BOUNDARY_INTACT",
        "draft_test_key": DRAFT_TEST_REQUIRE,
        "unapproved_research_test_key": RESEARCH_TEST_REQUIRE,
        "unapproved_field_scope_key": RESEARCH_FIELD_INHERIT,
        "base_test_additional_properties": root_test.get("additionalProperties"),
        "warning": ("Base Test additionalProperties is permissive; call "
                    "validate_draft_boundaries before accepting authored Tests"),
        "not_proven": ["native 0.4 compilation", "source OVAL runtime parity",
                       "scoped research owner acceptance", "scanner execution"],
    }


def _require(condition, message):
    if not condition:
        raise GrammarBoundaryError(message)


def _state_entries(entries, path):
    _require(isinstance(entries, list) and bool(entries), f"{path}: expected nonempty State list")
    for idx, node in enumerate(entries):
        where = f"{path}[{idx}]"
        _require(isinstance(node, dict), f"{where}: invalid State expression")
        if RESEARCH_FIELD_INHERIT in node:
            raise GrammarBoundaryError(f"{where}: state_fields_require is scoped research-only")
        # A literal observed field named 'and'/'or' is a dictionary, not a group.
        for key in RESEARCH_GROUPS:
            if isinstance(node.get(key), list):
                raise GrammarBoundaryError(f"{where}: research-only logical group '{key}'")
        groups = [key for key in DRAFT_GROUPS if isinstance(node.get(key), list)]
        if groups:
            _require(len(groups) == 1 and len(node) == 1,
                     f"{where}: ambiguous draft logical group")
            _state_entries(node[groups[0]], f"{where}.{groups[0]}")
            continue
        _require(len(node) == 1, f"{where}: expected exactly one named field")
        field, predicate = next(iter(node.items()))
        _require(isinstance(predicate, dict), f"{where}.{field}: expected typed predicate")
        # These are legacy scalar wrappers, not the field name 'value'.
        if "operation" in predicate and "value" in predicate:
            raise GrammarBoundaryError(f"{where}.{field}: legacy comparator wrapper is not 0.4-A")
        if "existence" in predicate or "match" in predicate:
            raise GrammarBoundaryError(f"{where}.{field}: legacy cardinality pair is not 0.4-A")
        if "record" not in predicate:
            _require("require" in predicate,
                     f"{where}.{field}: scalar field requires explicit draft 'require'")
        # Nested records have their own requirements; this guard intentionally
        # does not infer scalar scope into record/record-field multiplicities.


def validate_draft_boundaries(document):
    """Reject mixed dialects before the separate strict full schema validator.

    No semantic verification; only the narrow shape boundary reviewed in #239.
    """
    boundary_schema_report()
    _require(isinstance(document, dict) and isinstance(document.get("assessment"), dict),
             "missing Assessment document")
    a = document["assessment"]
    tests = a.get("tests")
    _require(isinstance(tests, dict) and bool(tests), "no draft automated Tests")
    for name, test in tests.items():
        where = f"assessment.tests.{name}"
        _require(isinstance(test, dict), f"{where}: invalid Test")
        _require(DRAFT_TEST_REQUIRE in test, f"{where}: draft Test 'require' missing")
        for key in (RESEARCH_TEST_REQUIRE, RESEARCH_FIELD_INHERIT,
                    "existence", "match"):
            if key in test:
                raise GrammarBoundaryError(f"{where}: '{key}' is not allowed in base 0.4-A")
        if "states" in test and test["states"] is not None:
            _state_entries(test["states"], f"{where}.states")
    return {"status": "DRAFT_BOUNDARY_PASS", "tested": len(tests),
            "scope": "authoring syntax boundary only; independent schema/compiler/runtime proof needed"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assessment-json", type=Path)
    args = parser.parse_args()
    report = boundary_schema_report()
    if args.assessment_json:
        report["assessment"] = validate_draft_boundaries(
            json.loads(args.assessment_json.read_text(encoding="utf-8")))
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
