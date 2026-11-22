#!/usr/bin/env python3
"""Generate the schema-derived 0.4.1 conformance inventory and portable vectors.

This generator reads only the checked-out flat ``schema/`` tree.  It deliberately
never copies a hand-maintained capability list: mappings, JSON-Schema properties,
enums and constraints are extracted at generation time.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any

import yaml

HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]
SCHEMA = ROOT / "schema"
OUT = ROOT / "conformance"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def order_assessment_tests(document: dict[str, Any]) -> dict[str, Any]:
    """Apply Issue #95 presentation order without changing schema semantics."""
    assessment = document.get("assessment")
    tests = assessment.get("tests") if isinstance(assessment, dict) else None
    if not isinstance(tests, dict):
        return document
    for name, test in list(tests.items()):
        if not isinstance(test, dict) or "object" not in test or "require" not in test:
            continue
        ordered: dict[str, Any] = {}
        for key, value in test.items():
            if key == "require":
                continue
            ordered[key] = value
            if key == "object":
                ordered["require"] = test["require"]
        tests[name] = ordered
    return document


def digest(paths: list[Path]) -> str:
    h = hashlib.sha256()
    for path in sorted(paths):
        h.update(path.relative_to(SCHEMA).as_posix().encode() + b"\0")
        h.update(path.read_bytes())
    return h.hexdigest()


def git_sha() -> str:
    """Return the canonical schema source pin, never this implementation commit."""
    requested = os.environ.get("SCAP_NG_SCHEMA_COMMIT")
    if requested:
        return requested
    current = digest(sorted((*SCHEMA.glob("*.json"), *(SCHEMA / "capability-mappings").rglob("*.json"))))
    existing = OUT / "manifest.json"
    if existing.is_file():
        prior = load(existing)
        if prior.get("schema_family_sha256") == current and prior.get("schema_commit"):
            return prior["schema_commit"]
        raise SystemExit("schema resources changed; regenerate with SCAP_NG_SCHEMA_COMMIT=<reviewed exact source commit>")
    try:
        return subprocess.check_output(["git", "rev-parse", "origin/main"], cwd=ROOT, text=True).strip()
    except subprocess.CalledProcessError:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def pointer(path: str, key: str) -> str:
    return path + "/" + key.replace("~", "~0").replace("/", "~1")


def walk_schema(value: Any, path: str = ""):
    if isinstance(value, dict):
        yield path, value
        for key, child in value.items():
            yield from walk_schema(child, pointer(path, key))
    elif isinstance(value, list):
        for i, child in enumerate(value):
            yield from walk_schema(child, f"{path}/{i}")


def constraint_value(value: Any) -> Any:
    """Keep the inventory reviewable while retaining an exact value digest.

    Scalar constraints remain directly readable. Nested schema branches are
    represented by shape, keys, and a canonical JSON digest; the source schema
    and pointer remain the authoritative full value.
    """
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    if isinstance(value, dict):
        return {"kind": "object", "keys": list(value), "sha256": hashlib.sha256(encoded).hexdigest()}
    return {"kind": "array", "length": len(value), "sha256": hashlib.sha256(encoded).hexdigest()}


def enums_and_constraints(doc: Any, source: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    enums: list[dict[str, Any]] = []
    constraints: list[dict[str, Any]] = []
    properties: list[dict[str, Any]] = []
    keywords = {
        "type", "required", "additionalProperties", "minProperties", "maxProperties",
        "minItems", "maxItems", "minLength", "maxLength", "pattern", "format",
        "const", "oneOf", "anyOf", "allOf", "not", "if", "then", "else",
        "dependentSchemas", "propertyNames", "uniqueItems", "contains",
        "unevaluatedProperties", "dependentRequired", "multipleOf", "minimum", "maximum",
        "exclusiveMinimum", "exclusiveMaximum",
    }
    for path, node in walk_schema(doc):
        if not isinstance(node, dict):
            continue
        if "enum" in node:
            enums.append({"pointer": path or "/", "values": node["enum"]})
        for key in sorted(set(node) & keywords):
            constraints.append({"pointer": path or "/", "keyword": key, "value": constraint_value(node[key])})
        if isinstance(node.get("properties"), dict):
            properties.append({
                "pointer": path or "/",
                "names": list(node["properties"]),
                "required": list(node.get("required", [])),
                "additional_properties": node.get("additionalProperties", True),
            })
    return enums, constraints, properties


def all_enums(node: Any) -> list[Any]:
    result: list[Any] = []
    for _, child in walk_schema(node):
        if isinstance(child, dict) and "enum" in child:
            result.extend(child["enum"])
    return result


def sample_for(datatype: str | None, *, ordinal: int = 0) -> Any:
    values = {
        "string": "fixture-value",
        "boolean": True,
        "integer": 7,
        "float": 7.5,
        "binary": "ZmFjdHVyZQ==",
        "version": "1.2.3",
        "ipv4": "192.0.2.7",
        "ipv6": "2001:db8::7",
        "rpm_evr": "1:1.2.3-7",
        "debian_evr": "1:1.2.3-7",
        "fileset_revision": "1.2.3",
        "ios_version": "1.2.3",
        "record": {"fixture_field": "fixture-value"},
    }
    value = values.get(datatype or "string", "fixture-value")
    if ordinal and isinstance(value, str):
        return f"{value}-{ordinal}"
    return value


def slug(name: str) -> str:
    return name.replace(".", "-").replace("_", "-")


def selector_sample(capability: str, field: str, mapping: dict[str, Any], selector_contracts: dict[str, Any]) -> Any:
    # Prefer canonical enum values exposed by the generated selector schema.
    native_selector = selector_contracts.get("resolved", {}).get(capability, {}).get("selectors", {}).get(field, {})
    source = native_selector.get("enum_source")
    if source:
        # enum_source is a vocabulary name, not necessarily a JSON pointer. The
        # selector schema remains authoritative for actual values.
        pass
    defs = selector_contracts.get("_selector_defs", {})
    for key in (f"{slug(capability)}_{field}_selector", f"{capability.replace('.', '_')}_{field}_selector"):
        if key in defs:
            definition = defs[key]
            # propertyNames enums describe allowed keys; only the operation
            # value enum is a selector vocabulary. Definitions use allOf, so
            # search each subschema for the equals property.
            for _, node in walk_schema(definition):
                if not isinstance(node, dict) or "equals" not in node.get("properties", {}):
                    continue
                enums = [v for v in all_enums(node["properties"]["equals"])
                         if isinstance(v, str) and v not in {"datatype", "equals"}]
                if enums:
                    return enums[0]
    datatypes = mapping.get("native", {}).get("field_datatypes", {})
    types = datatypes.get(field, ["string"])
    return sample_for(types[0] if types else "string")


def different_value(value: Any, datatype: str | None = None) -> Any:
    """Create a deterministic mismatch without changing the declared datatype."""
    if datatype == "boolean":
        return not value
    if datatype == "integer":
        return value + 1
    if datatype == "float":
        return value + 1.0
    if datatype == "record" and isinstance(value, dict):
        return {**value, "fixture_field": "not-the-expected-value"}
    if isinstance(value, list):
        return value + ["not-the-expected-value"]
    return "not-the-expected-value"


def predicate(value: Any, datatype: str | None = None) -> dict[str, Any]:
    if datatype == "record":
        return {"record": {"records_found": "one_or_more", "records_matching": "every", "fields": {
            "fixture_field": {"values_found": "one_or_more", "values_matching": "every", "equals": "fixture-value"}
        }}}
    return {"equals": value}


def build_assessment(mapping: dict[str, Any], selector_contracts: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    capability = mapping["capability"]
    s = slug(capability)
    native = mapping.get("native", {})
    datatypes = native.get("field_datatypes", {})
    selector_names: list[str] = []
    for alternative in native.get("object_selector_alternatives", []):
        if alternative:
            selector_names = list(alternative)
            break
    if not selector_names:
        selector_names = list(native.get("selector_map", {}))
    selector_values = {name: selector_sample(capability, name, mapping, selector_contracts) for name in selector_names}
    object_fields = {name: predicate(selector_values[name]) for name in selector_names}
    state_fields = list(native.get("state_field_map", {}))
    field_types = {field: (datatypes.get(field) or ["string"])[0] for field in state_fields}
    field_values = {field: selector_values[field] if field in selector_values else sample_for(field_types[field]) for field in state_fields}
    test_name = f"{s}-test"[:64]
    body: dict[str, Any] = {
        "assessment": {
            "id": f"conformance-{s}"[:64],
            "version": 1,
            "assessment_title": f"SCAP-NG 0.4.1 conformance: {capability} positive and status vectors",
            "mode": "automated",
            "class": "miscellaneous",
            "specification": {"id": "scap-ng.pre-alpha.assessment", "version": "0.4.1"},
            "tests": {},
            "evaluate": {"test": test_name},
        }
    }
    test: dict[str, Any] = {
        "test_title": f"Collect and match every declared {capability} field",
        "capability": capability,
    }
    source_kind = native.get("test_source", {}).get("kind")
    if source_kind == "variable":
        variable_name = f"{s}-variable"
        body["assessment"]["variables"] = {
            variable_name: {"kind": "constant", "expression": {"literal": {"datatype": "string", "value": "fixture-value"}}}
        }
        test["variable"] = variable_name
    elif source_kind != "none":
        test["object"] = {"capability": capability, **object_fields}
    test["require"] = {"item_requirement": {"items_found": "one_or_more"}}
    if state_fields:
        test["require"]["item_requirement"]["items_satisfying"] = "every"
        test["require"]["field_requirement"] = {"values_found": "one_or_more", "values_matching": "every"}
        test["require"]["fields"] = {field: predicate(value, field_types[field]) for field, value in field_values.items()}
    if capability != "independent.unknown":
        test["reported_elements"] = "all"
    body["assessment"]["tests"][test_name] = test
    # The evidence fixture is intentionally separate from the source assessment.
    fields = {
        field: {"datatype": field_types[field], "value": value, "status": "collected"}
        for field, value in field_values.items()
    }
    item = {"id": f"{s}-item", "capability": capability, "fields": fields, "status": "collected"}
    comparison_fields = [field for field in state_fields if field not in selector_names]
    if comparison_fields:
        negative_field = comparison_fields[0]
        negative_value = different_value(fields[negative_field]["value"], fields[negative_field]["datatype"])
        negative_items = [{**item, "fields": {**fields, negative_field: {**fields[negative_field], "value": negative_value}}}]
        negative_strategy = "field-mismatch"
    else:
        negative_field = None
        negative_items = []
        negative_value = None
        negative_strategy = "empty-collected-population"
    fixture = {
        "format": "scap-ng-conformance-evidence-0.1",
        "schema_version": "0.4.1",
        "case_id": capability,
        "clock": {"now_utc": "2026-01-01T00:00:00Z", "timezone": "UTC", "locale": "C", "ordering": "document"},
        "items": [item],
        "semantic_contract": {"selector_fields": selector_names, "negative_strategy": negative_strategy, "negative_field": negative_field, "negative_value": negative_value},
        "variants": {
            "positive": {"items": [item], "acquisition": "collected"},
            "negative": {"items": negative_items, "acquisition": "collected", "selector_fields_preserved": negative_strategy == "field-mismatch"},
            "multi-item": {"items": [{**item, "id": f"{s}-item-1"}, {**item, "id": f"{s}-item-2"}], "acquisition": "collected", "population": "two matching Items"},
            "boundary": {"items": [item], "acquisition": "collected", "boundary": "minimum one Item and one value per required field"},
            "empty": {"items": [], "acquisition": "not_collected"},
            "permission-denied": {"items": [], "acquisition": "denied"},
            "error": {"items": [], "acquisition": "error"},
            "not-applicable": {"items": [], "acquisition": "not_applicable"},
        },
    }
    if capability == "independent.unknown":
        fixture["semantic_witnesses"] = [{"rule": "independent.unknown.fixed_result", "positive_variant": "positive", "negative_variant": "negative", "expected": "unknown", "reason": "The mapping declares a fixed UNKNOWN source with no Object, State, existence, or runtime result control; distinct collected and empty evidence cannot turn that source into TRUE or FALSE."}]
    return body, fixture


def operator_operand(operator: str) -> tuple[str, Any, Any, str]:
    """Return datatype, observed value, comparison operand, and justification."""
    if operator.startswith("float_"):
        datatype, observed = "float", 2.5
    elif operator.startswith("binary_"):
        datatype, observed = "binary", "Zm9v"
    elif operator.startswith("version_"):
        datatype, observed = "version", "1.2.3"
    elif operator.startswith("ipv4_"):
        datatype, observed = "ipv4", "192.0.2.7"
    elif operator.startswith("ipv6_"):
        datatype, observed = "ipv6", "2001:db8::7"
    elif operator.startswith("rpm_evr_"):
        datatype, observed = "rpm_evr", "1:1.2.3-7"
    elif operator.startswith("debian_evr_"):
        datatype, observed = "debian_evr", "1:1.2.3-7"
    elif operator.startswith("fileset_revision_"):
        datatype, observed = "fileset_revision", "1.2.3"
    elif operator.startswith("ios_version_"):
        datatype, observed = "ios_version", "1.2.3"
    elif operator in {"bitwise_and", "bitwise_or"}:
        datatype, observed = "integer", 3
    elif operator in {"subset_of", "superset_of"}:
        datatype, observed = "string", ["alpha", "beta"]
    else:
        datatype, observed = "string", "fixture-value"
    if operator in {"not_equal", "case_insensitive_not_equal", "float_not_equal", "binary_not_equal", "version_not_equal", "ipv4_not_equal", "ipv6_not_equal", "rpm_evr_not_equal", "debian_evr_not_equal", "fileset_revision_not_equal", "ios_version_not_equal"}:
        operand = different_value(observed, datatype)
        reason = "The operand is a deterministic different value, so not-equal is TRUE."
    elif operator in {"greater_than", "greater_than_or_equal", "less_than", "less_than_or_equal"} or operator.endswith(("_greater_than", "_greater_than_or_equal", "_less_than", "_less_than_or_equal")):
        if operator.endswith("greater_than"):
            operand = "1.0" if datatype in {"version", "ios_version", "fileset_revision"} else (1 if datatype not in {"float"} else 1.5)
            if datatype == "string": operand = "a"
            if datatype in {"ipv4", "ipv6"}: operand = "192.0.2.1" if datatype == "ipv4" else "2001:db8::1"
        elif operator.endswith("greater_than_or_equal"):
            operand = observed
        elif operator.endswith("less_than"):
            operand = "9.9.9" if datatype in {"version", "ios_version", "fileset_revision"} else (9 if datatype not in {"float"} else 9.5)
            if datatype == "string": operand = "zzzz"
            if datatype in {"ipv4", "ipv6"}: operand = "192.0.2.9" if datatype == "ipv4" else "2001:db8::9"
        else:
            operand = observed
        reason = "The typed observed value and operand satisfy the named ordering relation."
    elif operator in {"bitwise_and", "bitwise_or"}:
        operand = 1 if operator == "bitwise_and" else 3
        reason = "The integer bit mask satisfies the named bitwise relation."
    elif operator == "matches_regex":
        operand = "^fixture-value$"
        reason = "The deterministic lexical value matches the anchored regular expression."
    elif operator in {"subset_of", "superset_of"}:
        operand = ["alpha", "beta", "gamma"] if operator == "subset_of" else ["alpha"]
        reason = "The ordered observed collection satisfies the named set relation."
    elif operator in {"case_insensitive_equals"}:
        operand = "FIXTURE-VALUE"
        reason = "The operand differs only in case."
    elif operator in {"ipv4_subset_of", "ipv4_superset_of", "ipv6_subset_of", "ipv6_superset_of"}:
        operand = observed
        reason = "The identical typed network value satisfies the reflexive set relation."
    else:
        operand = observed
        reason = "The typed operand is equal to the observed value."
    return datatype, observed, operand, reason


def build_selector_alternative_suite(mappings: list[dict[str, Any]], selector_contracts: dict[str, Any]) -> dict[str, Any]:
    tests: dict[str, Any] = {}
    expected: dict[str, Any] = {}
    test_outcomes: dict[str, str] = {}
    witness: dict[str, Any] = {}
    for mapping in mappings:
        capability = mapping["capability"]
        native = mapping.get("native", {})
        alternatives = native.get("object_selector_alternatives", [])
        for index, alternative in enumerate(alternatives, 1):
            if native.get("test_source", {}).get("kind") in {"none", "variable"}:
                continue
            test_name = f"selector-{slug(capability)}-{index}-test"[:64]
            values = {field: selector_sample(capability, field, mapping, selector_contracts) for field in alternative}
            tests[test_name] = {"test_title": f"{capability} selector alternative {index}", "capability": capability, "reported_elements": "all", "object": {"capability": capability, **{field: predicate(value) for field, value in values.items()}}, "require": {"item_requirement": {"items_found": "one_or_more"}}}
            test_outcomes[test_name] = "true"
            expected[f"{capability}#{index}"] = {"outcome": "true", "selectors": values, "reason": "The complete declared selector alternative is present and independently witnessed."}
            witness[test_name] = {"capability": capability, "selectors": values, "items": [{"id": f"{slug(capability)}-selector-{index}-item", "capability": capability, "fields": {}, "status": "collected"}]}
    assessment = {"assessment": {"id": "conformance-core-selector-alternatives", "version": 1, "assessment_title": "SCAP-NG 0.4.1 selector alternatives", "mode": "automated", "class": "miscellaneous", "specification": {"id": "scap-ng.pre-alpha.assessment", "version": "0.4.1"}, "tests": tests, "evaluate": {"and": [{"test": name} for name in tests]}}}
    fixture = {"format": "scap-ng-conformance-evidence-0.1", "schema_version": "0.4.1", "case_id": "core-selector-alternatives", "clock": {"now_utc": "2026-01-01T00:00:00Z", "timezone": "UTC", "locale": "C", "ordering": "document"}, "test_outcomes": test_outcomes, "selector_witnesses": witness}
    return {"assessment": assessment, "fixture": fixture, "expected": {"format": "scap-ng-conformance-expected-0.1", "schema_version": "0.4.1", "case_id": "core-selector-alternatives", "alternatives": expected, "reason": "Every mapping-declared selector alternative is represented; enum boundary and collector execution remain separate gates."}}


def build_operator_suite(comparison_operators: list[str]) -> dict[str, Any]:
    tests: dict[str, Any] = {}
    variables: dict[str, Any] = {}
    expected: dict[str, Any] = {}
    outcomes = {}
    for operator in comparison_operators:
        name = f"operator-{slug(operator)}"
        variable = f"{name}-variable"
        datatype, observed, operand, reason = operator_operand(operator)
        variables[variable] = {"kind": "constant", "expression": {"literal": {"datatype": datatype, "value": observed}}}
        field_predicate = {operator: operand}
        if isinstance(operand, list):
            field_predicate = {"value_match": "every", **field_predicate}
        tests[f"{name}-test"] = {
            "test_title": f"Comparison operator {operator} has a TRUE witness",
            "capability": "variable.value", "variable": variable, "reported_elements": "all",
            "require": {"item_requirement": {"items_found": "one_or_more", "items_satisfying": "every"}, "field_requirement": {"values_found": "one_or_more", "values_matching": "every"}, "fields": {"value": field_predicate}},
        }
        outcomes[f"{name}-test"] = "true"
        expected[operator] = {"outcome": "true", "datatype": datatype, "observed": observed, "operand": operand, "reason": reason}
    test_names = list(outcomes)
    assessment = {"assessment": {"id": "conformance-core-comparison-operators", "version": 1, "assessment_title": "SCAP-NG 0.4.1 comparison operator witnesses", "mode": "automated", "class": "miscellaneous", "specification": {"id": "scap-ng.pre-alpha.assessment", "version": "0.4.1"}, "variables": variables, "tests": tests, "evaluate": {"and": [{"test": name} for name in test_names]}}}
    fixture = {"format": "scap-ng-conformance-evidence-0.1", "schema_version": "0.4.1", "case_id": "core-comparison-operators", "clock": {"now_utc": "2026-01-01T00:00:00Z", "timezone": "UTC", "locale": "C", "ordering": "document"}, "test_outcomes": outcomes}
    return {"assessment": assessment, "fixture": fixture, "expected": {"format": "scap-ng-conformance-expected-0.1", "schema_version": "0.4.1", "case_id": "core-comparison-operators", "operators": expected, "reason": "Each operator has a typed operand chosen to make the named relation TRUE; this is a semantic witness, not RI execution proof."}}


def build_enum_boundary_suite(mappings: list[dict[str, Any]]) -> dict[str, Any]:
    enum_values = ["classes_root", "current_config", "current_user", "current_user_local_settings", "local_machine", "users"]
    tests: dict[str, Any] = {}; outcomes: dict[str, str] = {}; expected: dict[str, Any] = {}
    for mapping in mappings:
        capability = mapping["capability"]
        if capability not in {"windows.registry", "windows.regkeyeffectiverights"}: continue
        native = mapping.get("native", {}); selectors = list(native.get("object_selector_alternatives", [[]])[0])
        for index, value in enumerate(enum_values, 1):
            name = f"enum-{slug(capability)}-{index}-test"[:64]
            obj = {"capability": capability, **{selector: {"equals": value if selector == "hive" else "fixture-value"} for selector in selectors}}
            tests[name] = {"test_title": f"{capability} hive enum boundary {value}", "capability": capability, "reported_elements": "all", "object": obj, "require": {"item_requirement": {"items_found": "one_or_more"}}}
            outcomes[name] = "true"; expected[f"{capability}#{value}"] = {"outcome": "true", "reason": "Every schema-admitted hive enum value has a distinct selector witness."}
    assessment = {"assessment": {"id": "conformance-core-enum-boundaries", "version": 1, "assessment_title": "SCAP-NG 0.4.1 native selector enum boundaries", "mode": "automated", "class": "miscellaneous", "specification": {"id": "scap-ng.pre-alpha.assessment", "version": "0.4.1"}, "tests": tests, "evaluate": {"and": [{"test": name} for name in tests]}}}
    fixture = {"format": "scap-ng-conformance-evidence-0.1", "schema_version": "0.4.1", "case_id": "core-enum-boundaries", "clock": {"now_utc": "2026-01-01T00:00:00Z", "timezone": "UTC", "locale": "C", "ordering": "document"}, "test_outcomes": outcomes}
    return {"assessment": assessment, "fixture": fixture, "expected": {"format": "scap-ng-conformance-expected-0.1", "schema_version": "0.4.1", "case_id": "core-enum-boundaries", "enum_values": expected, "reason": "Native selector enum values are schema-valid witnesses; invalid sentinel rejection remains a separate negative gate."}}


def build_multi_value_suite(mappings: list[dict[str, Any]], selector_contracts: dict[str, Any]) -> dict[str, Any]:
    tests: dict[str, Any] = {}; variables: dict[str, Any] = {}; outcomes: dict[str, str] = {}; expected: dict[str, Any] = {}
    for mapping in mappings:
        capability = mapping["capability"]; native = mapping.get("native", {}); datatypes = native.get("field_datatypes", {})
        state_fields = list(native.get("state_field_map", {})); field = next((f for f in state_fields if (datatypes.get(f) or ["string"])[0] != "record"), None)
        if field is None: continue
        datatype = (datatypes.get(field) or ["string"])[0]; value = selector_sample(capability, field, mapping, selector_contracts) if field in native.get("selector_map", {}) else sample_for(datatype)
        test_name = f"multi-value-{slug(capability)}-test"[:64]
        test = {"test_title": f"{capability} value_match every multi-value witness", "capability": capability, "require": {"item_requirement": {"items_found": "one_or_more", "items_satisfying": "every"}, "field_requirement": {"values_found": "one_or_more", "values_matching": "every"}, "fields": {field: {"value_match": "every", "equals": [value, value]}}}}
        if capability != "independent.unknown": test["reported_elements"] = "all"
        if native.get("test_source", {}).get("kind") == "variable":
            var = f"multi-value-{slug(capability)}-variable"[:64]; variables[var] = {"kind": "constant", "expression": {"literal": {"datatype": datatype, "value": [value, value]}}}; test["variable"] = var
        elif native.get("test_source", {}).get("kind") != "none":
            selector_names = list(native.get("object_selector_alternatives", [[]])[0]) if native.get("object_selector_alternatives") else list(native.get("selector_map", {})); test["object"] = {"capability": capability, **{name: predicate(selector_sample(capability, name, mapping, selector_contracts)) for name in selector_names}}
        tests[test_name] = test; outcomes[test_name] = "true"; expected[capability] = {"outcome": "true", "field": field, "datatype": datatype, "values": [value, value], "reason": "Both deterministic values satisfy value_match: every."}
    assessment = {"assessment": {"id": "conformance-core-multi-values", "version": 1, "assessment_title": "SCAP-NG 0.4.1 multi-value field matching", "mode": "automated", "class": "miscellaneous", "specification": {"id": "scap-ng.pre-alpha.assessment", "version": "0.4.1"}, "variables": variables, "tests": tests, "evaluate": {"and": [{"test": name} for name in tests]}}}
    fixture = {"format": "scap-ng-conformance-evidence-0.1", "schema_version": "0.4.1", "case_id": "core-multi-values", "clock": {"now_utc": "2026-01-01T00:00:00Z", "timezone": "UTC", "locale": "C", "ordering": "document"}, "test_outcomes": outcomes}
    return {"assessment": assessment, "fixture": fixture, "expected": {"format": "scap-ng-conformance-expected-0.1", "schema_version": "0.4.1", "case_id": "core-multi-values", "capabilities": expected, "reason": "Each applicable scalar field has a schema-valid value_match: every witness; record-only and no-field capabilities are explicitly omitted."}}


def build_cardinality_suite() -> dict[str, Any]:
    cases = [
        ("item-exactly-one", "independent.unknown", {"item_requirement": {"items_found": "exactly_one"}}, "Exactly one collected Item satisfies exactly_one."),
        ("item-none", "independent.unknown", {"item_requirement": {"items_found": "none"}}, "A collected empty population satisfies none."),
        ("item-zero-or-more", "independent.unknown", {"item_requirement": {"items_found": "zero_or_more"}}, "An empty collected population satisfies zero_or_more."),
        ("field-exactly-one", "variable.value", {"item_requirement": {"items_found": "one_or_more", "items_satisfying": "every"}, "field_requirement": {"values_found": "one_or_more", "values_matching": "every"}, "fields": {"value": {"values_found": "exactly_one", "values_matching": "every", "equals": "fixture-value"}}}, "One observed value satisfies exactly_one."),
        ("field-none", "variable.value", {"item_requirement": {"items_found": "one_or_more", "items_satisfying": "every"}, "field_requirement": {"values_found": "one_or_more", "values_matching": "every"}, "fields": {"value": {"values_found": "none"}}}, "Confirmed field absence satisfies none without a comparator."),
        ("field-zero-or-more", "variable.value", {"item_requirement": {"items_found": "one_or_more", "items_satisfying": "every"}, "field_requirement": {"values_found": "one_or_more", "values_matching": "every"}, "fields": {"value": {"values_found": "zero_or_more", "values_matching": "every", "equals": "fixture-value"}}}, "Zero or more observed values is a valid independent cardinality."),
    ]
    tests = {}; variables = {}; outcomes = {}; expected = {}
    for name, capability, require, reason in cases:
        test_name = f"cardinality-{name}-test"
        test = {"test_title": f"Cardinality witness: {name}", "capability": capability, "require": require}
        if capability == "variable.value":
            variable = f"{test_name}-variable"
            variables[variable] = {"kind": "constant", "expression": {"literal": {"datatype": "string", "value": "fixture-value"}}}
            test["variable"] = variable; test["reported_elements"] = "all"
        tests[test_name] = test; outcomes[test_name] = "true"; expected[name] = {"outcome": "true", "reason": reason}
    assessment = {"assessment": {"id": "conformance-core-cardinalities", "version": 1, "assessment_title": "SCAP-NG 0.4.1 remaining Item and field cardinalities", "mode": "automated", "class": "miscellaneous", "specification": {"id": "scap-ng.pre-alpha.assessment", "version": "0.4.1"}, "variables": variables, "tests": tests, "evaluate": {"and": [{"test": name} for name in tests]}}}
    fixture = {"format": "scap-ng-conformance-evidence-0.1", "schema_version": "0.4.1", "case_id": "core-cardinalities", "clock": {"now_utc": "2026-01-01T00:00:00Z", "timezone": "UTC", "locale": "C", "ordering": "document"}, "test_outcomes": outcomes}
    return {"assessment": assessment, "fixture": fixture, "expected": {"format": "scap-ng-conformance-expected-0.1", "schema_version": "0.4.1", "case_id": "core-cardinalities", "cardinalities": expected, "reason": "Each remaining cardinality has a dedicated schema-valid witness; execution receipts remain separate."}}


def build_variable_interaction_suite() -> dict[str, Any]:
    """Exercise a canonical Variable -> Require -> Evaluate chain.

    The second Test is deliberately FALSE because two observed values cannot
    satisfy ``values_found: exactly_one``.  ``not`` keeps the enclosing
    Assessment TRUE without hiding the decisive FALSE leaf.
    """
    variables = {
        "source-values-variable": {"kind": "constant", "expression": {"literal": {"datatype": "string", "value": ["alpha", "beta"]}}},
        "alias-values-variable": {"kind": "local", "expression": {"variable": "source-values-variable"}},
        "expected-values-variable": {"kind": "constant", "expression": {"literal": {"datatype": "string", "value": ["alpha", "beta"]}}},
    }
    common = {"item_requirement": {"items_found": "exactly_one", "items_satisfying": "every"}, "field_requirement": {"values_found": "one_or_more", "values_matching": "every"}}
    every_require = {**common, "fields": {"value": {"value_match": "every", "values_found": "one_or_more", "values_matching": "every", "equals": {"variable": "expected-values-variable"}}}}
    exact_require = {**common, "fields": {"value": {"value_match": "every", "values_found": "exactly_one", "values_matching": "every", "equals": {"variable": "expected-values-variable"}}}}
    tests = {
        "variable-alias-every-test": {"test_title": "Variable alias preserves ordered values", "capability": "variable.value", "reported_elements": "all", "variable": "alias-values-variable", "require": every_require},
        "variable-alias-exactly-one-test": {"test_title": "Variable alias exposes field cardinality failure", "capability": "variable.value", "reported_elements": "all", "variable": "alias-values-variable", "require": exact_require},
    }
    assessment = {"assessment": {"id": "conformance-core-variable-interactions", "version": 1, "assessment_title": "SCAP-NG 0.4.1 Variable, Require and Evaluate interactions", "mode": "automated", "class": "miscellaneous", "specification": {"id": "scap-ng.pre-alpha.assessment", "version": "0.4.1"}, "variables": variables, "tests": tests, "evaluate": {"and": [{"test": "variable-alias-every-test"}, {"not": {"test": "variable-alias-exactly-one-test"}}]}}}
    fixture = {"format": "scap-ng-conformance-evidence-0.1", "schema_version": "0.4.1", "case_id": "core-variable-interactions", "clock": {"now_utc": "2026-01-01T00:00:00Z", "timezone": "UTC", "locale": "C", "ordering": "document"}, "variables": {"source-values-variable": ["alpha", "beta"], "alias-values-variable": ["alpha", "beta"], "expected-values-variable": ["alpha", "beta"]}, "test_outcomes": {"variable-alias-every-test": "true", "variable-alias-exactly-one-test": "false"}}
    expected = {"format": "scap-ng-conformance-expected-0.1", "schema_version": "0.4.1", "case_id": "core-variable-interactions", "assertions": {"variable-alias-every-test": {"outcome": "true", "items_found": 1, "items_satisfying": 1, "values_found": 2, "values_matching": 2, "reason": "The local alias preserves the two ordered source values; every observed value matches the expected Variable."}, "variable-alias-exactly-one-test": {"outcome": "false", "items_found": 1, "items_satisfying": 0, "values_found": 2, "values_matching": 2, "reason": "The same two-value alias fails values_found: exactly_one; the FALSE leaf remains visible."}}, "enclosing_outcome": "true", "reason": "Variable alias resolution, field cardinality, and canonical not are independently asserted; the enclosing AND is TRUE without negating the FALSE leaf."}
    return {"assessment": assessment, "fixture": fixture, "expected": expected}


def build_set_filter_suite() -> dict[str, Any]:
    """Schema-valid witnesses for shared Set composition and filter actions."""
    shared_objects = {
        "left-object": {"object_title": "Left package population", "capability": "linux.dpkginfo", "name": {"equals": "left"}},
        "right-object": {"object_title": "Right package population", "capability": "linux.dpkginfo", "name": {"equals": "right"}},
    }

    def filter_entry(action: str, value: str) -> dict[str, Any]:
        return {action: {"arch": {"values_found": "one_or_more", "values_matching": "every", "equals": value}}}

    def set_expression(operator: str) -> dict[str, Any]:
        operands = [
            {"object": "left-object", "filters": [filter_entry("include", "amd64")]},
            {"object": "right-object", "filters": [filter_entry("exclude", "arm64")]},
        ]
        return {"operator": operator, "operands": operands}

    tests = {}
    for name, operator, title in [
        ("union", "union", "Union applies include/exclude filters to both operands"),
        ("intersection", "intersection", "Intersection retains only shared Items"),
        ("difference", "difference", "Difference removes right-operand Items"),
    ]:
        tests[f"set-{name}-test"] = {
            "test_title": title,
            "capability": "linux.dpkginfo",
            "reported_elements": "all",
            "object": {"capability": "linux.dpkginfo", "set": set_expression(operator)},
            "require": {"item_requirement": {"items_found": "one_or_more"}},
        }
    assessment = {"assessment": {"id": "conformance-core-set-filters", "version": 1, "assessment_title": "SCAP-NG 0.4.1 Set and Filter semantics", "mode": "automated", "class": "miscellaneous", "specification": {"id": "scap-ng.pre-alpha.assessment", "version": "0.4.1"}, "shared_objects": shared_objects, "tests": tests, "evaluate": {"and": [{"test": "set-union-test"}, {"test": "set-intersection-test"}, {"test": "set-difference-test"}]}}}
    fixture = {"format": "scap-ng-conformance-evidence-0.1", "schema_version": "0.4.1", "case_id": "core-set-filters", "clock": {"now_utc": "2026-01-01T00:00:00Z", "timezone": "UTC", "locale": "C", "ordering": "document"}, "populations": {"left": [{"id": "left-a", "arch": "amd64", "status": "collected"}, {"id": "shared", "arch": "amd64", "status": "collected"}], "right": [{"id": "shared", "arch": "amd64", "status": "collected"}, {"id": "right-b", "arch": "amd64", "status": "collected"}]}, "test_outcomes": {"set-union-test": "true", "set-intersection-test": "true", "set-difference-test": "true"}}
    expected = {"format": "scap-ng-conformance-expected-0.1", "schema_version": "0.4.1", "case_id": "core-set-filters", "operations": {"union": {"outcome": "true", "items_found": 3, "items_satisfying": 3, "values": ["left-a", "shared", "right-b"], "reason": "Include/exclude filters are applied before union; the duplicate shared Item is retained once."}, "intersection": {"outcome": "true", "items_found": 1, "items_satisfying": 1, "values": ["shared"], "reason": "Both filtered operand populations contain the shared Item."}, "difference": {"outcome": "true", "items_found": 1, "items_satisfying": 1, "values": ["left-a"], "reason": "The right filtered population is removed from the left population."}}, "filter_actions": ["include", "exclude"], "set_operators": ["union", "intersection", "difference"], "reason": "The abstract deterministic populations independently justify Set cardinalities; collector execution and capability-specific filter semantics remain separate."}
    return {"assessment": assessment, "fixture": fixture, "expected": expected}


def build_semantic_boundary_suite() -> dict[str, Any]:
    """Witness shared file-selection semantic boundaries with paired cases.

    These combinations are deliberately schema-valid but semantically distinct:
    traversal is valid for an ordinary selector, while full-path or patterned
    directory selection with traversal is rejected by the mapping rule.  A
    literal Windows filename with a reserved character is rejected; the same
    character in a match expression is explicitly permitted.
    """
    tests: dict[str, Any] = {}
    outcomes: dict[str, str] = {}
    assertions: dict[str, Any] = {}
    witnesses: list[dict[str, Any]] = []
    evidence: dict[str, Any] = {}

    cases = [
        (
            "unix-full-path-safe-test", "unix.file", {
                "capability": "unix.file", "filepath": {"equals": "/etc/hosts"},
            }, {"filepath": {"equals": "/etc/hosts"}}, "true", [],
            "An equality full_path selection has no traversal and is semantically valid.",
        ),
        (
            "unix-full-path-traversal-test", "unix.file", {
                "capability": "unix.file", "filepath": {"matches_regex": "^/etc/.*"}, "traversal": {"max_depth": "unlimited", "recurse": "directories"},
            }, {"filepath": {"matches_regex": "^/etc/.*"}}, "error", ["unix.file.full_path_no_traversal"],
            "The schema admits the shape, but the semantic rule rejects traversal with full_path selection.",
        ),
        (
            "unix-pattern-directory-traversal-test", "unix.file", {
                "capability": "unix.file", "path": {"matches_regex": "^/var/log/.*"}, "traversal": {"max_depth": "unlimited", "recurse": "directories"},
            }, {"path": {"matches_regex": "^/var/log/.*"}}, "error", ["unix.file.pattern_directory_no_traversal"],
            "The schema admits the shape, but a patterned directory selection cannot request traversal.",
        ),
        (
            "windows-full-path-traversal-test", "windows.file", {
                "capability": "windows.file", "filepath": {"matches_regex": "^C:[\\\\]Windows[\\\\].*"}, "traversal": {"max_depth": "unlimited", "recurse": "directories"},
            }, {"filepath": {"matches_regex": "^C:[\\\\]Windows[\\\\].*"}}, "error", ["windows.file.full_path_no_traversal"],
            "The Windows full_path traversal combination is schema-valid but semantically rejected.",
        ),
        (
            "windows-pattern-directory-traversal-test", "windows.file", {
                "capability": "windows.file", "path": {"matches_regex": "^C:[\\\\]Logs[\\\\].*"}, "traversal": {"max_depth": "unlimited", "recurse": "directories"},
            }, {"path": {"matches_regex": "^C:[\\\\]Logs[\\\\].*"}}, "error", ["windows.file.pattern_directory_no_traversal"],
            "The Windows patterned directory traversal combination is semantically rejected.",
        ),
        (
            "windows-literal-reserved-name-test", "windows.file", {
                "capability": "windows.file", "path": {"equals": "C:\\Windows"}, "filename": {"equals": "bad:name"},
            }, {"path": {"equals": "C:\\Windows"}, "filename": {"equals": "bad:name"}}, "error", ["windows.file.literal_name_characters"],
            "A literal Windows filename cannot contain a reserved character; this is a semantic error, not a schema error.",
        ),
        (
            "windows-pattern-reserved-name-test", "windows.file", {
                "capability": "windows.file", "path": {"equals": "C:\\Windows"}, "filename": {"matches_regex": "^bad:name$"},
            }, {"path": {"equals": "C:\\Windows"}, "filename": {"matches_regex": "^bad:name$"}}, "true", ["windows.file.literal_name_characters"],
            "Reserved characters in a match expression are allowed; the literal-name rule is not applied to regex syntax.",
        ),
    ]
    # The same constraints recur on other file-content/resource capabilities.
    # Keep paired witnesses per occurrence rather than claiming transitive
    # coverage from the Unix and Windows examples.
    family_specs = [
        ("file.hash", "file.hash.full_path_no_traversal", "file.hash.pattern_directory_no_traversal", "unix", "directories"),
        ("independent.textfilecontent", "independent.textfilecontent.full_path_no_traversal", "independent.textfilecontent.pattern_directory_no_traversal", "unix", "directories"),
        ("independent.xmlfilecontent", "independent.xmlfilecontent.full_path_no_traversal", "independent.xmlfilecontent.pattern_directory_no_traversal", "unix", "directories"),
        ("windows.fileeffectiverights", "windows.fileeffectiverights.full_path_no_traversal", "windows.fileeffectiverights.pattern_directory_no_traversal", "windows", "directories"),
        ("linux.selinuxsecuritycontext", "linux.selinuxsecuritycontext.full_path_no_traversal", "linux.selinuxsecuritycontext.pattern_directory_no_traversal", "unix", "directories"),
    ]
    for index, (capability, full_rule, pattern_rule, platform, recurse) in enumerate(family_specs):
        prefix = "C:\\Windows" if platform == "windows" else "/etc"
        log_prefix = "C:\\Logs" if platform == "windows" else "/var/log"
        full_path = f"{prefix}/fixture" if platform == "unix" else f"{prefix}\\fixture.txt"
        full_pattern = f"^{prefix.replace('\\', '[\\\\]')}/.*"
        directory_pattern = f"^{log_prefix.replace('\\', '[\\\\]')}/.*"
        traversal = {"max_depth": "unlimited", "recurse": recurse}
        cases.extend([
            (f"semantic-{index}-full-safe-test", capability, {"capability": capability, "filepath": {"equals": full_path}}, {"filepath": {"equals": full_path}}, "true", [full_rule], "Equality full_path selection is valid without traversal."),
            (f"semantic-{index}-full-traversal-test", capability, {"capability": capability, "filepath": {"matches_regex": full_pattern}, "traversal": traversal}, {"filepath": {"matches_regex": full_pattern}}, "error", [full_rule], "Traversal is rejected when this capability selects full_path."),
            (f"semantic-{index}-pattern-safe-test", capability, {"capability": capability, "path": {"equals": log_prefix}}, {"path": {"equals": log_prefix}}, "true", [pattern_rule], "Equality directory selection is valid without traversal."),
            (f"semantic-{index}-pattern-traversal-test", capability, {"capability": capability, "path": {"matches_regex": directory_pattern}, "traversal": traversal}, {"path": {"matches_regex": directory_pattern}}, "error", [pattern_rule], "Traversal is rejected when this capability selects a patterned directory."),
        ])
    cases.extend([
        ("yaml-inline-content-safe-test", "independent.yamlfilecontent", {"capability": "independent.yamlfilecontent", "content": {"equals": "fixture-content"}}, {"content": {"equals": "fixture-content"}}, "true", ["independent.yamlfilecontent.inline_content_no_traversal"], "Inline content selection is valid without file traversal."),
        ("yaml-inline-content-traversal-test", "independent.yamlfilecontent", {"capability": "independent.yamlfilecontent", "content": {"equals": "fixture-content"}, "traversal": {"max_depth": "unlimited", "recurse": "directories"}}, {"content": {"equals": "fixture-content"}}, "error", ["independent.yamlfilecontent.inline_content_no_traversal"], "Traversal is not applicable when inline YAML content is supplied."),
    ])
    cases.extend([
        ("family-vocabulary-safe-test", "independent.family", None, {"family": {"equals": "unix"}}, "true", ["independent.family.literal_vocabulary"], "The literal family value unix is in the source vocabulary."),
        ("family-vocabulary-invalid-test", "independent.family", None, {"family": {"equals": ""}}, "error", ["independent.family.literal_vocabulary"], "An empty literal family is reserved for variable serialization and is semantically invalid."),
        ("interface-type-safe-test", "unix.interface", {"capability": "unix.interface", "name": {"equals": "eth0"}}, {"type": {"equals": "ARPHRD_ETHER"}}, "true", ["unix.interface.type_literal"], "ARPHRD_ETHER is a source OVAL interface-type literal."),
        ("interface-type-invalid-test", "unix.interface", {"capability": "unix.interface", "name": {"equals": "eth0"}}, {"type": {"equals": ""}}, "error", ["unix.interface.type_literal"], "The empty interface type is not a native literal; it is reserved for variable serialization."),
        ("lockout-time-safe-test", "windows.lockoutpolicy", None, {"force_logoff": {"equals": 0}}, "true", ["windows.lockoutpolicy.nonnegative_time_values"], "Zero is the inclusive lower bound for a non-negative lockout time."),
        ("lockout-time-invalid-test", "windows.lockoutpolicy", None, {"force_logoff": {"equals": -1}}, "error", ["windows.lockoutpolicy.nonnegative_time_values"], "A negative literal lockout time violates the non-negative source constraint."),
        ("listening-protocol-safe-test", "linux.inetlisteningservers", {"capability": "linux.inetlisteningservers", "protocol": {"equals": "tcp"}}, {"protocol": {"equals": "tcp"}}, "true", ["linux.inetlisteningservers.protocol"], "Collected transport protocol tcp uses the required lower-case form."),
        ("listening-protocol-invalid-test", "linux.inetlisteningservers", {"capability": "linux.inetlisteningservers", "protocol": {"equals": "TCP"}}, {"protocol": {"equals": "TCP"}}, "error", ["linux.inetlisteningservers.protocol"], "Upper-case TCP is not the canonical lower-case collected protocol form."),
    ])
    cases.extend([
        ("registry-key-null-safe-test", "windows.registry", {"capability": "windows.registry", "hive": {"equals": "classes_root"}}, {}, "true", ["windows.registry.key_null_requires_name_null"], "A null key selects the hive itself and therefore requires a null value name."),
        ("registry-key-null-invalid-test", "windows.registry", {"capability": "windows.registry", "hive": {"equals": "classes_root"}, "name": {"equals": "fixture-value"}}, {}, "error", ["windows.registry.key_null_requires_name_null"], "A non-null value name cannot be evaluated when the containing registry key is null."),
        ("registry-value-type-safe-test", "windows.registry", {"capability": "windows.registry", "hive": {"equals": "classes_root"}, "key": {"equals": "Software"}, "name": {"equals": "Count"}}, {"type": {"equals": "dword"}, "value": {"datatype": "integer", "equals": 7}}, "true", ["windows.registry.value_type_datatype"], "A dword registry type and integer value predicate use compatible native datatypes."),
        ("registry-value-type-invalid-test", "windows.registry", {"capability": "windows.registry", "hive": {"equals": "classes_root"}, "key": {"equals": "Software"}, "name": {"equals": "Count"}}, {"type": {"equals": "dword"}, "value": {"datatype": "string", "equals": "7"}}, "error", ["windows.registry.value_type_datatype"], "A dword registry type cannot be compared as a string when both type and value datatype are asserted."),
        ("text-pattern-operation-safe-test", "independent.textfilecontent", {"capability": "independent.textfilecontent", "pattern": {"matches_regex": "^needle$"}}, {"pattern": {"equals": "^needle$"}}, "true", ["independent.textfilecontent.pattern_operation"], "The text-file Object pattern uses the canonical match operation."),
        ("text-pattern-operation-invalid-test", "independent.textfilecontent", {"capability": "independent.textfilecontent", "pattern": {"equals": "^needle$"}}, {"pattern": {"equals": "^needle$"}}, "error", ["independent.textfilecontent.pattern_operation"], "An equality selector is not the required pattern operation for text-file collection."),
        ("xml-xpath-operation-safe-test", "independent.xmlfilecontent", {"capability": "independent.xmlfilecontent", "full_path": {"equals": "/etc/config.xml"}, "xpath": {"equals": "/config/value"}}, {"xpath": {"equals": "/config/value"}}, "true", ["independent.xmlfilecontent.xpath_equal"], "The XML Object XPath selector is an equality predicate for an XPath 1.0 expression."),
        ("xml-xpath-operation-invalid-test", "independent.xmlfilecontent", {"capability": "independent.xmlfilecontent", "full_path": {"equals": "/etc/config.xml"}, "xpath": {"matches_regex": "/config/.*"}}, {"xpath": {"equals": "/config/.*"}}, "error", ["independent.xmlfilecontent.xpath_equal"], "Pattern matching is not the canonical equality selector for an XML XPath."),
        ("yaml-content-operation-safe-test", "independent.yamlfilecontent", {"capability": "independent.yamlfilecontent", "content": {"equals": "fixture-content"}}, {"content": {"equals": "fixture-content"}}, "true", ["independent.yamlfilecontent.content_equal"], "Inline YAML content selection uses equality semantics."),
        ("yaml-content-operation-invalid-test", "independent.yamlfilecontent", {"capability": "independent.yamlfilecontent", "content": {"matches_regex": "fixture-.*"}}, {"content": {"equals": "fixture-content"}}, "error", ["independent.yamlfilecontent.content_equal"], "Inline YAML content is a complete value and cannot use a pattern selector."),
        ("plist-path-operation-safe-test", "macos.plist", {"capability": "macos.plist", "filepath": {"equals": "/Library/Preferences/example.plist"}}, {"filepath": {"equals": "/Library/Preferences/example.plist"}}, "true", ["macos.plist.filepath_equal"], "The plist filepath Object selector uses equality semantics."),
        ("plist-path-operation-invalid-test", "macos.plist", {"capability": "macos.plist", "filepath": {"matches_regex": "/Library/Preferences/.*\\.plist"}}, {"filepath": {"equals": "/Library/Preferences/example.plist"}}, "error", ["macos.plist.filepath_equal"], "A pattern selector is not the canonical equality operation for plist filepath."),
        ("panos-xpath-operation-safe-test", "panos.config", {"capability": "panos.config", "xpath": {"equals": "/config/devices"}}, {"xpath": {"equals": "/config/devices"}}, "true", ["panos.config.xpath_equal"], "PAN-OS XPath selection uses equality semantics."),
        ("panos-xpath-operation-invalid-test", "panos.config", {"capability": "panos.config", "xpath": {"matches_regex": "/config/.*"}}, {"xpath": {"equals": "/config/devices"}}, "error", ["panos.config.xpath_equal"], "A pattern selector is not the canonical equality operation for PAN-OS XPath."),
    ])
    cases.extend([
        ("pwpolicy-auth-pair-safe-test", "macos.pwpolicy", {"capability": "macos.pwpolicy", "username": {"equals": "fixture-user"}}, {"username": {"equals": "fixture-user"}}, "true", ["macos.pwpolicy.auth_pair"], "Omitting both optional authenticator members preserves the unauthenticated policy form."),
        ("pwpolicy-auth-pair-invalid-test", "macos.pwpolicy", {"capability": "macos.pwpolicy", "username": {"equals": "fixture-user"}, "authenticator_password": {"equals": "secret"}}, {"username": {"equals": "fixture-user"}}, "error", ["macos.pwpolicy.auth_pair"], "An authenticator password without its paired authenticator violates the native pair constraint."),
        ("pwpolicy-password-equal-safe-test", "macos.pwpolicy", {"capability": "macos.pwpolicy", "authenticator": {"equals": "Directory"}, "authenticator_password": {"equals": "secret"}}, {"authenticator_password": {"equals": "secret"}}, "true", ["macos.pwpolicy.password_equal"], "The authenticator password selector uses equality semantics."),
        ("pwpolicy-password-equal-invalid-test", "macos.pwpolicy", {"capability": "macos.pwpolicy", "authenticator": {"equals": "Directory"}, "authenticator_password": {"matches_regex": "sec.*"}}, {"authenticator_password": {"equals": "secret"}}, "error", ["macos.pwpolicy.password_equal"], "A pattern operation is not the native equality operation for authenticator_password."),
        ("pwpolicy-directory-equal-safe-test", "macos.pwpolicy", {"capability": "macos.pwpolicy", "directory_node": {"equals": "/Local/Default"}}, {"directory_node": {"equals": "/Local/Default"}}, "true", ["macos.pwpolicy.directory_node_equal"], "The directory_node selector uses equality semantics."),
        ("pwpolicy-directory-equal-invalid-test", "macos.pwpolicy", {"capability": "macos.pwpolicy", "directory_node": {"matches_regex": "/Local/.*"}}, {"directory_node": {"equals": "/Local/Default"}}, "error", ["macos.pwpolicy.directory_node_equal"], "A pattern operation is not the native equality operation for directory_node."),
        ("pwpolicy-xpath-equal-safe-test", "macos.pwpolicy", {"capability": "macos.pwpolicy", "xpath": {"equals": "/policy/value"}}, {"xpath": {"equals": "/policy/value"}}, "true", ["macos.pwpolicy.xpath_equal"], "The policy XPath selector uses equality semantics."),
        ("pwpolicy-xpath-equal-invalid-test", "macos.pwpolicy", {"capability": "macos.pwpolicy", "xpath": {"matches_regex": "/policy/.*"}}, {"xpath": {"equals": "/policy/value"}}, "error", ["macos.pwpolicy.xpath_equal"], "A pattern operation is not the native equality operation for policy XPath."),
        ("cmdlet-module-guid-safe-test", "windows.cmdlet", {"capability": "windows.cmdlet", "module_id": {"equals": "12345678-1234-1234-1234-1234567890ab"}}, {"module_id": {"equals": "12345678-1234-1234-1234-1234567890ab"}}, "true", ["windows.cmdlet.module_guid"], "The literal module_id is a canonical Windows GUID."),
        ("cmdlet-module-guid-invalid-test", "windows.cmdlet", {"capability": "windows.cmdlet", "module_id": {"equals": "not-a-guid"}}, {"module_id": {"equals": "not-a-guid"}}, "error", ["windows.cmdlet.module_guid"], "A non-null literal module_id that is not a GUID is a semantic error."),
        ("dpkg-debian-evr-safe-test", "linux.dpkginfo", {"capability": "linux.dpkginfo", "name": {"equals": "fixture-package"}}, {"evr": {"datatype": "debian_evr", "equals": "1:2.3-4"}}, "true", ["linux.dpkginfo.debian_evr"], "A Debian package EVR is compared with the preferred debian_evr datatype."),
    ])
    cases.extend([
        ("sid-defaults-safe-test", "windows.sid", {"capability": "windows.sid", "trustee_name": {"equals": "Administrators"}, "include_group": True, "resolve_group": False}, {"trustee_name": {"equals": "Administrators"}}, "true", ["windows.sid.materialized_behaviors"], "The direct SID Object materializes both group behavior parameters."),
        ("sid-defaults-invalid-test", "windows.sid", {"capability": "windows.sid", "trustee_name": {"equals": "Administrators"}}, {"trustee_name": {"equals": "Administrators"}}, "error", ["windows.sid.materialized_behaviors"], "A direct SID Object omitting imported group behavior defaults is semantically incomplete."),
        ("sid-sid-defaults-safe-test", "windows.sid_sid", {"capability": "windows.sid_sid", "trustee_sid": {"equals": "S-1-5-32-544"}, "include_group": True, "resolve_group": False}, {"trustee_sid": {"equals": "S-1-5-32-544"}}, "true", ["windows.sid_sid.materialized_behaviors"], "The SID-targeted Object materializes both group behavior parameters."),
        ("sid-sid-defaults-invalid-test", "windows.sid_sid", {"capability": "windows.sid_sid", "trustee_sid": {"equals": "S-1-5-32-544"}}, {"trustee_sid": {"equals": "S-1-5-32-544"}}, "error", ["windows.sid_sid.materialized_behaviors"], "A direct SID-targeted Object omitting imported group behavior defaults is semantically incomplete."),
        ("ntuser-value-type-safe-test", "windows.ntuser", {"capability": "windows.ntuser", "key": {"equals": "Software"}, "name": {"equals": "Count"}}, {"type": {"equals": "dword"}, "value": {"datatype": "integer", "equals": 7}}, "true", ["windows.ntuser.value_type_datatype"], "A registry dword type and integer NT-user value predicate use compatible datatypes."),
        ("ntuser-value-type-invalid-test", "windows.ntuser", {"capability": "windows.ntuser", "key": {"equals": "Software"}, "name": {"equals": "Count"}}, {"type": {"equals": "dword"}, "value": {"datatype": "string", "equals": "7"}}, "error", ["windows.ntuser.value_type_datatype"], "A registry dword type cannot be compared as a string when both type and value datatype are asserted."),
        ("password-range-safe-test", "windows.passwordpolicy", None, {"min_passwd_age": {"equals": 0}}, "true", ["windows.passwordpolicy.source_ranges"], "Zero is the inclusive lower bound for a non-negative password-policy age."),
        ("password-range-invalid-test", "windows.passwordpolicy", None, {"min_passwd_age": {"equals": -1}}, "error", ["windows.passwordpolicy.source_ranges"], "A negative literal password-policy age violates the source range constraint."),
    ])
    cases.extend([
        ("plist-xpath-operation-safe-test", "macos.plist", {"capability": "macos.plist", "app_id": {"equals": "com.example"}, "xpath": {"equals": "/dict/key"}}, {"xpath": {"equals": "/dict/key"}}, "true", ["macos.plist.xpath_equal"], "The plist XPath selector uses equality semantics."),
        ("plist-xpath-operation-invalid-test", "macos.plist", {"capability": "macos.plist", "app_id": {"equals": "com.example"}, "xpath": {"matches_regex": "/dict/.*"}}, {"xpath": {"equals": "/dict/key"}}, "error", ["macos.plist.xpath_equal"], "A pattern selector is not the canonical equality operation for plist XPath."),
        ("systemprofiler-xpath-operation-safe-test", "macos.systemprofiler", {"capability": "macos.systemprofiler", "data_type": {"equals": "SPHardwareDataType"}, "xpath": {"equals": "/hardware"}}, {"xpath": {"equals": "/hardware"}}, "true", ["macos.systemprofiler.xpath_equal"], "The system_profiler XPath selector uses equality semantics."),
        ("systemprofiler-xpath-operation-invalid-test", "macos.systemprofiler", {"capability": "macos.systemprofiler", "data_type": {"equals": "SPHardwareDataType"}, "xpath": {"matches_regex": "/hardware/.*"}}, {"xpath": {"equals": "/hardware"}}, "error", ["macos.systemprofiler.xpath_equal"], "A pattern selector is not the canonical equality operation for system_profiler XPath."),
        ("shadow-encrypt-safe-test", "unix.shadow", {"capability": "unix.shadow", "username": {"equals": "fixture-user"}}, {"encrypt_method": {"equals": "SHA-512"}}, "true", ["unix.shadow.encrypt_method_literal"], "SHA-512 is an admitted OVAL encryption-method literal."),
        ("shadow-encrypt-invalid-test", "unix.shadow", {"capability": "unix.shadow", "username": {"equals": "fixture-user"}}, {"encrypt_method": {"equals": ""}}, "error", ["unix.shadow.encrypt_method_literal"], "An empty encryption method is reserved for variable serialization and is not a native literal."),
        ("yaml-yamlpath-safe-test", "independent.yamlfilecontent", {"capability": "independent.yamlfilecontent", "yamlpath": {"equals": "$.metadata.name"}}, {"yamlpath": {"equals": "$.metadata.name"}}, "true", ["independent.yamlfilecontent.yamlpath_equal"], "The YAMLPath selector uses equality semantics."),
        ("yaml-yamlpath-invalid-test", "independent.yamlfilecontent", {"capability": "independent.yamlfilecontent", "yamlpath": {"matches_regex": "\\$\\..*"}}, {"yamlpath": {"equals": "$.metadata.name"}}, "error", ["independent.yamlfilecontent.yamlpath_equal"], "A pattern selector is not the canonical equality operation for YAMLPath."),
        ("yaml-full-path-traversal-test", "independent.yamlfilecontent", {"capability": "independent.yamlfilecontent", "full_path": {"matches_regex": "^/etc/.*"}, "traversal": {"max_depth": "unlimited", "recurse": "directories"}}, {"filepath": {"matches_regex": "^/etc/.*"}}, "error", ["independent.yamlfilecontent.full_path_no_traversal"], "Traversal is rejected when YAML content selects full_path."),
        ("shadow-encrypt-boundary-test", "unix.shadow", {"capability": "unix.shadow", "username": {"equals": "fixture-user"}}, {"encrypt_method": {"equals": "DES"}}, "true", ["unix.shadow.encrypt_method_literal"], "DES is the lower lexical boundary of the admitted encryption-method vocabulary."),
    ])
    cases.extend([
        ("xml-item-creation-safe-test", "independent.xmlfilecontent", {"capability": "independent.xmlfilecontent", "full_path": {"equals": "/etc/config.xml"}, "xpath": {"equals": "/config/value"}, "item_creation": "all_object_elements_fullfilled"}, {"xpath": {"equals": "/config/value"}}, "true", ["independent.xmlfilecontent.materialized_item_creation"], "The XML Object explicitly materializes the imported all-object-elements item-creation default."),
        ("xml-item-creation-invalid-test", "independent.xmlfilecontent", {"capability": "independent.xmlfilecontent", "full_path": {"equals": "/etc/config.xml"}, "xpath": {"equals": "/config/value"}}, {"xpath": {"equals": "/config/value"}}, "error", ["independent.xmlfilecontent.materialized_item_creation"], "A direct XML Object omitting the materialized item-creation behavior is semantically incomplete."),
        ("rpm-package-defaults-safe-test", "linux.rpmverifypackage", {"capability": "linux.rpmverifypackage", "name": {"equals": "fixture-package"}, "skip_dependencies": False, "skip_scripts": False}, {"name": {"equals": "fixture-package"}}, "true", ["linux.rpmverifypackage.materialized_behaviors"], "The RPM package Object explicitly materializes both verification switches."),
        ("rpm-package-defaults-invalid-test", "linux.rpmverifypackage", {"capability": "linux.rpmverifypackage", "name": {"equals": "fixture-package"}}, {"name": {"equals": "fixture-package"}}, "error", ["linux.rpmverifypackage.materialized_behaviors"], "A direct RPM package Object omitting imported verification switches is semantically incomplete."),
        ("rpm-file-defaults-safe-test", "linux.rpmverifyfile", {"capability": "linux.rpmverifyfile", "name": {"equals": "fixture-file"}, "epoch": {"equals": "0"}, "version": {"equals": "1.0"}, "release": {"equals": "1"}, "arch": {"equals": "x86_64"}, "filepath": {"equals": "/usr/bin/fixture"}, "skip_link_target": False, "skip_size": False, "skip_owner": False, "skip_group": False, "skip_mtime": False, "skip_mode": False, "skip_rdev": False, "skip_config_files": False, "skip_ghost_files": False, "skip_file_digest": False, "skip_capabilities": False}, {"name": {"equals": "fixture-file"}}, "true", ["linux.rpmverifyfile.materialized_behaviors"], "The RPM file Object explicitly materializes every non-deprecated verification switch."),
        ("rpm-file-defaults-invalid-test", "linux.rpmverifyfile", {"capability": "linux.rpmverifyfile", "name": {"equals": "fixture-file"}, "epoch": {"equals": "0"}, "version": {"equals": "1.0"}, "release": {"equals": "1"}, "arch": {"equals": "x86_64"}, "filepath": {"equals": "/usr/bin/fixture"}}, {"name": {"equals": "fixture-file"}}, "error", ["linux.rpmverifyfile.materialized_behaviors"], "A direct RPM file Object omitting imported verification switches is semantically incomplete."),
    ])
    cases.extend([
        ("file-rights-literal-safe-test", "windows.fileeffectiverights", {"capability": "windows.fileeffectiverights", "path": {"equals": "C:\\Windows"}, "filename": {"matches_regex": "^bad:name$"}, "trustee_sid": {"equals": "S-1-5-32-544"}}, {"filename": {"matches_regex": "^bad:name$"}}, "true", ["windows.fileeffectiverights.literal_name_characters"], "Reserved characters are permitted inside a filename match expression."),
        ("file-rights-literal-invalid-test", "windows.fileeffectiverights", {"capability": "windows.fileeffectiverights", "path": {"equals": "C:\\Windows"}, "filename": {"equals": "bad:name"}, "trustee_sid": {"equals": "S-1-5-32-544"}}, {"filename": {"equals": "bad:name"}}, "error", ["windows.fileeffectiverights.literal_name_characters"], "A literal Windows filename cannot contain reserved characters."),
        ("file-rights-trustee-sid-safe-test", "windows.fileeffectiverights", {"capability": "windows.fileeffectiverights", "filepath": {"equals": "C:\\Windows\\fixture.txt"}, "trustee_sid": {"equals": "S-1-5-32-544"}}, {"trustee_sid": {"equals": "S-1-5-32-544"}}, "true", ["windows.fileeffectiverights.trustee_sid"], "File effective-rights identifies the trustee by SID."),
    ])
    cases.extend([
        ("wu-defaults-safe-test", "windows.wuaupdatesearcher", {"capability": "windows.wuaupdatesearcher", "search_criteria": {"equals": "IsInstalled=1"}, "include_superseded_updates": True}, {"search_criteria": {"equals": "IsInstalled=1"}}, "true", ["windows.wuaupdatesearcher.materialized_superseded_default"], "The direct Object explicitly materializes include_superseded_updates."),
        ("wu-defaults-invalid-test", "windows.wuaupdatesearcher", {"capability": "windows.wuaupdatesearcher", "search_criteria": {"equals": "IsInstalled=1"}}, {"search_criteria": {"equals": "IsInstalled=1"}}, "error", ["windows.wuaupdatesearcher.materialized_superseded_default"], "A direct Object omitting the required materialized superseded-update default is semantically incomplete."),
        ("ntuser-defaults-safe-test", "windows.ntuser", {"capability": "windows.ntuser", "key": {"equals": "Software"}, "name": {"equals": "Example"}, "include_default": False, "item_creation": "key_and_name_exist"}, {"key": {"equals": "Software"}, "name": {"equals": "Example"}}, "true", ["windows.ntuser.materialized_collection_defaults"], "The direct NT-user Object explicitly carries both imported collection defaults."),
        ("ntuser-defaults-invalid-test", "windows.ntuser", {"capability": "windows.ntuser", "key": {"equals": "Software"}, "name": {"equals": "Example"}}, {"key": {"equals": "Software"}, "name": {"equals": "Example"}}, "error", ["windows.ntuser.materialized_collection_defaults"], "An NT-user Object omitting materialized include_default and item_creation is semantically incomplete."),
    ])
    for name, capability, obj, fields, outcome, rule_ids, reason in cases:
        require = {"item_requirement": {"items_found": "one_or_more"}}
        if fields:
            require["item_requirement"]["items_satisfying"] = "every"
            require.update({"field_requirement": {"values_found": "one_or_more", "values_matching": "every"}, "fields": fields})
        tests[name] = {
            "test_title": f"Semantic boundary witness: {name.removesuffix('-test')}",
            "capability": capability,
            "require": require,
            "reported_elements": "all",
        }
        if obj is not None:
            tests[name]["object"] = obj
        outcomes[name] = outcome
        item_count = 1 if outcome == "true" else 0
        assertion = {"outcome": outcome, "items_found": item_count, "items_satisfying": item_count, "reason": reason}
        assertions[name] = assertion
        if outcome == "true":
            typed_fields = {}
            for field, predicate in fields.items():
                operator, value = next(iter(predicate.items()))
                if operator == "matches_regex":
                    value = {
                        "^/etc/.*": "/etc/hosts",
                        "^/var/log/.*": "/var/log/app.log",
                        "^C:[\\]Windows[\\].*": "C:\\Windows\\fixture.txt",
                        "^C:[\\]Logs[\\].*": "C:\\Logs\\fixture.txt",
                        "^bad:name$": "bad:name",
                    }.get(value, value)
                datatype = "boolean" if isinstance(value, bool) else "integer" if isinstance(value, int) and not isinstance(value, bool) else "string"
                typed_fields[field] = {"datatype": datatype, "value": value, "status": "collected"}
            evidence[name] = {"status": "collected", "items_found": 1, "items_satisfying": 1, "items": [{"id": f"{name}-item", "capability": capability, "fields": typed_fields}]}
        else:
            evidence[name] = {"status": "not_run", "items_found": 0, "items_satisfying": 0, "items": [], "reason": "Semantic validation fails before collection."}
        if rule_ids:
            witnesses.append({"test": name, "rules": rule_ids, "expected": outcome, "reason": reason})
    assessment = {"assessment": {"id": "conformance-core-semantic-boundaries", "version": 1, "assessment_title": "SCAP-NG 0.4.1 shared file-selection semantic boundaries", "mode": "automated", "class": "miscellaneous", "specification": {"id": "scap-ng.pre-alpha.assessment", "version": "0.4.1"}, "tests": tests, "evaluate": {"and": [{"test": name} for name in tests]}}}
    fixture = {"format": "scap-ng-conformance-evidence-0.1", "schema_version": "0.4.1", "case_id": "core-semantic-boundaries", "clock": {"now_utc": "2026-01-01T00:00:00Z", "timezone": "UTC", "locale": "C", "ordering": "document"}, "test_outcomes": outcomes, "evidence": evidence, "semantic_witnesses": witnesses}
    expected = {"format": "scap-ng-conformance-expected-0.1", "schema_version": "0.4.1", "case_id": "core-semantic-boundaries", "assertions": assertions, "rules": sorted({rule for witness in witnesses for rule in witness["rules"]}), "reason": "Each invalid combination remains schema-valid but has an independently justified semantic ERROR; positive cases demonstrate the allowed boundary and regex exemption. Scanner execution is not claimed."}
    return {"assessment": assessment, "fixture": fixture, "expected": expected}

def build_variable_function_suite() -> dict[str, Any]:
    """Schema-valid witnesses for ordered Variable functions and aliases."""
    variables = {
        "source-values-variable": {"kind": "constant", "expression": {"literal": {"datatype": "string", "value": ["a", "a", "b"]}}},
        "unique-values-variable": {"kind": "local", "expression": {"unique": {"variable": "source-values-variable"}}},
        "count-values-variable": {"kind": "local", "expression": {"count": {"variable": "source-values-variable"}}},
        "concat-values-variable": {"kind": "local", "expression": {"concat": [{"literal": "prefix-"}, {"variable": "unique-values-variable"}]}},
        "merge-values-variable": {"kind": "local", "expression": {"merge": {"delimiter": ",", "sort": "lexical", "order": "ascending", "values": {"variable": "unique-values-variable"}}}},
        "expected-unique-variable": {"kind": "constant", "expression": {"literal": {"datatype": "string", "value": ["a", "b"]}}},
        "expected-count-variable": {"kind": "constant", "expression": {"literal": {"datatype": "integer", "value": 3}}},
        "expected-concat-variable": {"kind": "constant", "expression": {"literal": {"datatype": "string", "value": ["prefix-a", "prefix-b"]}}},
        "expected-merge-variable": {"kind": "constant", "expression": {"literal": {"datatype": "string", "value": "a,b"}}},
    }
    def test(name: str, variable: str, expected: str, title: str, value_match: str = "every") -> dict[str, Any]:
        return {"test_title": title, "capability": "variable.value", "reported_elements": "all", "variable": variable, "require": {"item_requirement": {"items_found": "one_or_more", "items_satisfying": "every"}, "field_requirement": {"values_found": "one_or_more", "values_matching": "every"}, "fields": {"value": {"value_match": value_match, "values_found": "one_or_more", "values_matching": "every", "equals": {"variable": expected}}}}}
    tests = {
        "function-unique-test": test("unique", "unique-values-variable", "expected-unique-variable", "Unique removes duplicate values preserving first occurrence"),
        "function-count-test": test("count", "count-values-variable", "expected-count-variable", "Count counts duplicate values", "one_or_more"),
        "function-concat-test": test("concat", "concat-values-variable", "expected-concat-variable", "Concat preserves ordered Cartesian values"),
        "function-merge-test": test("merge", "merge-values-variable", "expected-merge-variable", "Merge sorts and joins values"),
    }
    assessment = {"assessment": {"id": "conformance-core-variable-functions", "version": 1, "assessment_title": "SCAP-NG 0.4.1 Variable function semantics", "mode": "automated", "class": "miscellaneous", "specification": {"id": "scap-ng.pre-alpha.assessment", "version": "0.4.1"}, "variables": variables, "tests": tests, "evaluate": {"and": [{"test": name} for name in tests]}}}
    fixture = {"format": "scap-ng-conformance-evidence-0.1", "schema_version": "0.4.1", "case_id": "core-variable-functions", "clock": {"now_utc": "2026-01-01T00:00:00Z", "timezone": "UTC", "locale": "C", "ordering": "document"}, "variables": {"source-values-variable": ["a", "a", "b"], "unique-values-variable": ["a", "b"], "count-values-variable": [3], "concat-values-variable": ["prefix-a", "prefix-b"], "merge-values-variable": ["a,b"]}, "test_outcomes": {name: "true" for name in tests}}
    expected = {"format": "scap-ng-conformance-expected-0.1", "schema_version": "0.4.1", "case_id": "core-variable-functions", "functions": {"unique": {"outcome": "true", "values_found": 2, "values": ["a", "b"], "reason": "Unique removes the second a and preserves first occurrence order."}, "count": {"outcome": "true", "values_found": 1, "values": [3], "reason": "Count returns one integer equal to the source population length three, including duplicates."}, "concat": {"outcome": "true", "values_found": 2, "values": ["prefix-a", "prefix-b"], "reason": "Concat combines the literal prefix with each unique value in document order."}, "merge": {"outcome": "true", "values_found": 1, "values": ["a,b"], "reason": "Lexical ascending merge joins the unique values with the explicit comma delimiter."}}, "function_names": ["unique", "count", "concat", "merge"], "reason": "Expected values are independently derived from ordered literal populations; status/error propagation and runtime execution remain separate."}
    return {"assessment": assessment, "fixture": fixture, "expected": expected}


def build_input_guard_suite() -> dict[str, Any]:
    """Exercise presence guards without collapsing absent and empty bindings."""
    assessment = {"assessment": {"id": "conformance-core-input-guards", "version": 1, "assessment_title": "SCAP-NG 0.4.1 Input presence and cardinality guards", "mode": "automated", "class": "compliance", "specification": {"id": "scap-ng.pre-alpha.assessment", "version": "0.4.1"}, "inputs": {"expected-value-input": {"datatype": "integer", "cardinality": "exactly_one", "required": False, "constraints": {"predicate": {"and": [{"greater_than_or_equal": 1}, {"less_than_or_equal": 10}]}}}}, "tests": {"input-guarded-test": {"test_title": "Input-bound registry comparison", "capability": "windows.registry", "reported_elements": "all", "object": {"hive": {"equals": "local_machine"}, "key": {"equals": "SOFTWARE\\Policies\\Example"}, "name": {"equals": "ExampleValue"}}, "require": {"item_requirement": {"items_found": "one_or_more", "items_satisfying": "every"}, "field_requirement": {"values_found": "one_or_more", "values_matching": "every"}, "fields": {"type": {"equals": "dword"}, "value": {"equals": {"input": "expected-value-input"}, "value_match": "every"}}}}}, "evaluate": {"if": {"input_provided": "expected-value-input"}, "then": {"test": "input-guarded-test"}, "else": {"not_evaluated": {"reason": "Expected organization input was not supplied", "follow_up": "Obtain an authorized value before evaluation"}}}}}
    fixture = {"format": "scap-ng-conformance-evidence-0.1", "schema_version": "0.4.1", "case_id": "core-input-guards", "clock": {"now_utc": "2026-01-01T00:00:00Z", "timezone": "UTC", "locale": "C", "ordering": "document"}, "bindings": {"provided": [7], "absent": None, "explicit-empty": [], "too-many": [7, 8], "out-of-range": [0]}, "test_outcomes": {"provided": "true", "absent": "not_evaluated", "explicit-empty": "error", "too-many": "error", "out-of-range": "error"}}
    expected = {"format": "scap-ng-conformance-expected-0.1", "schema_version": "0.4.1", "case_id": "core-input-guards", "variants": {"provided": {"assessment_outcome": "true", "reason": "Presence guard takes the then branch; one supplied integer satisfies the bounded Input predicate."}, "absent": {"assessment_outcome": "not_evaluated", "reason": "Absent optional Input takes the explicit else branch; it is not treated as an empty or default value."}, "explicit-empty": {"assessment_outcome": "error", "reason": "A supplied empty population is distinct from absence and violates exactly_one."}, "too-many": {"assessment_outcome": "error", "reason": "Two supplied values violate exactly_one; cardinality is not silently truncated."}, "out-of-range": {"assessment_outcome": "error", "reason": "The supplied value violates the explicit 1..10 predicate; it is not coerced or defaulted."}}, "guard": "input_provided", "input_cardinality": "exactly_one", "independently_justified": True, "reason": "Input presence, supplied population cardinality, and value constraints are separate dimensions; runtime binding receipts remain RI-owned."}
    return {"assessment": assessment, "fixture": fixture, "expected": expected}


def build_applicability_suite() -> dict[str, Any]:
    """Exercise Assessment dependency identity and applicability inheritance shape."""
    assessment = {"assessment": {"id": "conformance-core-applicability", "version": 1, "assessment_title": "SCAP-NG 0.4.1 shared Assessment applicability", "mode": "automated", "class": "compliance", "specification": {"id": "scap-ng.pre-alpha.assessment", "version": "0.4.1"}, "dependencies": {"shared-applicability": {"assessment": "shared-applicability-assessment", "expected_version": 1, "purpose": "applicability"}}, "applicability": {"and": [{"assessment": "shared-applicability-assessment"}, {"not": {"not_applicable": {"reason": "Target is excluded by the shared applicability Assessment."}}}]}, "tests": {"applicable-test": {"test_title": "Applicable shared Assessment branch", "capability": "independent.unknown", "require": {"item_requirement": {"items_found": "one_or_more"}}}}, "evaluate": {"test": "applicable-test"}}}
    fixture = {"format": "scap-ng-conformance-evidence-0.1", "schema_version": "0.4.1", "case_id": "core-applicability", "clock": {"now_utc": "2026-01-01T00:00:00Z", "timezone": "UTC", "locale": "C", "ordering": "document"}, "dependency_outcomes": {"applicable": "true", "not-applicable": "not_applicable", "deferred": "not_evaluated"}, "test_outcome": "true"}
    expected = {"format": "scap-ng-conformance-expected-0.1", "schema_version": "0.4.1", "case_id": "core-applicability", "dependency": "shared-applicability-assessment", "purpose": "applicability", "variants": {"applicable": {"inherited_applicability": "true", "assessment_outcome": "true", "reason": "The shared dependency is applicable and the local applicability expression admits the target."}, "not-applicable": {"inherited_applicability": "not_applicable", "assessment_outcome": "not_applicable", "reason": "NOT_APPLICABLE from the shared applicability dependency is preserved, not converted to FALSE."}, "deferred": {"inherited_applicability": "not_evaluated", "assessment_outcome": "not_evaluated", "reason": "An indeterminate shared applicability dependency remains NOT_EVALUATED and does not fall through to the local Test."}}, "independently_justified": True, "runtime_qualification": False, "reason": "Dependency identity, purpose, and applicability status handoff are authored separately from scanner execution."}
    return {"assessment": assessment, "fixture": fixture, "expected": expected}


def build_authoring_enum_cases() -> list[tuple[str, dict[str, Any], dict[str, Any]]]:
    """Generate witnesses for every active Assessment authoring enum branch.

    These are authoring/schema cases, not runtime outcomes.  In particular the
    explicit reported-elements array is included because it is a distinct
    oneOf branch from the two scalar enum values.
    """
    classes = ["compliance", "vulnerability", "patch", "inventory", "miscellaneous"]
    outcomes = ["true", "false", "error", "unknown", "not_evaluated", "not_applicable"]
    reported_elements = [("all", "scalar-all"), ("compared", "scalar-compared"), (["value"], "explicit-list")]
    cases = []
    for assessment_class in classes:
        for reported, label in reported_elements:
            case_id = f"authoring-automated-{assessment_class}-{label}"
            body = {"assessment": {"id": case_id, "version": 1, "assessment_title": f"Authoring enum witness automated/{assessment_class}/{label}", "mode": "automated", "class": assessment_class, "specification": {"id": "scap-ng.pre-alpha.assessment", "version": "0.4.1"}, "tests": {"enum-test": {"test_title": "reported-elements enum/oneOf witness", "capability": "independent.unknown", "reported_elements": reported, "require": {"item_requirement": {"items_found": "one_or_more"}}}}, "evaluate": {"test": "enum-test"}}}
            expected = {"format": "scap-ng-conformance-expected-0.1", "schema_version": "0.4.1", "case_id": case_id, "mode": "automated", "class": assessment_class, "reported_elements": label, "reason": "Schema-admitted automated class and reported_elements branch; no scanner outcome is inferred."}
            cases.append((case_id, body, expected))
        case_id = f"authoring-manual-{assessment_class}"
        body = {"assessment": {"id": case_id, "version": 1, "assessment_title": f"Authoring enum witness manual/{assessment_class}", "mode": "manual", "class": assessment_class, "procedure": "Review the deterministic authoring enum witness.", "response": {"type": "technical-outcome", "choices": [{"value": outcome, "outcome": outcome} for outcome in outcomes], "allow_comment": True, "allow_evidence": True}}}
        expected = {"format": "scap-ng-conformance-expected-0.1", "schema_version": "0.4.1", "case_id": case_id, "mode": "manual", "class": assessment_class, "response_outcomes": outcomes, "reason": "Schema-admitted manual class and every technical outcome enum value; no response is selected."}
        cases.append((case_id, body, expected))
    return cases


def build_status_and_policy_cases() -> dict[str, Any]:
    base = {"version": 1, "assessment_title": "SCAP-NG 0.4.1 typed status witness", "mode": "automated", "class": "miscellaneous", "specification": {"id": "scap-ng.pre-alpha.assessment", "version": "0.4.1"}, "tests": {"status-test": {"test_title": "Typed status propagation witness", "capability": "independent.unknown", "require": {"item_requirement": {"items_found": "one_or_more"}}}}}
    status = []
    for name, expression, outcome, reason in [
        ("not-evaluated", {"not_evaluated": {"reason": "Evidence-backed authoring deferral", "follow_up": "Collect the required evidence."}}, "not_evaluated", "Author-declared deferral remains NOT_EVALUATED."),
        ("not-applicable", {"not_applicable": {"reason": "Applicability predicate excludes this target."}}, "not_applicable", "Applicability remains NOT_APPLICABLE and is not Boolean false."),
    ]:
        document = {"assessment": {**base, "id": f"conformance-status-{name}", "evaluate": expression}}
        status.append((name, document, {"format": "scap-ng-conformance-expected-0.1", "schema_version": "0.4.1", "case_id": f"status-{name}", "assessment_outcome": outcome, "reason": reason}))
    tailoring = {"tailoring": {"id": "conformance-disabled-profile-tailoring", "version": 1, "purpose": "Exercise profile disablement without changing Assessment truth.", "benchmark": {"id": "conformance-benchmark", "version": 1}, "profile": "baseline", "extends": None, "enabled_rules": ["rule-enabled"], "disabled_rules": ["rule-disabled"], "group_operations": [], "check_selectors": {}, "provenance": {"organization": "SCAP-NG", "created_by": "conformance", "created_at": None, "modified_by": "conformance", "modified_at": None, "authorized_by": "owner", "authorized_at": None, "authorization_reference": "issue-87", "authorization_status": "review"}}}
    benchmark = {"benchmark": {"id": "conformance-benchmark", "ng_schema_version": "0.4.1", "use_case": "conformance", "assessment_specifications": [], "title": [{"text": "Conformance benchmark", "language": "en"}], "description": [{"text": "Deterministic profile witness", "language": "en"}], "language": "en", "status": [], "version": {}, "metadata": {}, "notices": [], "front_matter": [], "rear_matter": [], "references": [], "text_blocks": [], "platform": {"id": "all", "title": "All targets"}, "applicability_catalog": "catalog", "scoring": [], "parameters": [], "default_selection": True, "groups": [], "profiles": [{"id": "baseline", "title": "Baseline", "description": "Disables one rule", "disabled_rules": ["rule-disabled"]}], "rules": ["rule-enabled", "rule-disabled"]}}
    policy_expected = {"format": "scap-ng-conformance-expected-0.1", "schema_version": "0.4.1", "case_id": "disabled-profile", "profile": "baseline", "disabled_rules": ["rule-disabled"], "enabled_rules": ["rule-enabled"], "reason": "Profile resolution disables the named Rule; it does not fabricate a technical Assessment outcome."}
    return {"status": status, "tailoring": tailoring, "benchmark": benchmark, "policy_expected": policy_expected}


def build_core() -> dict[str, Any]:
    tests = {}
    for name, title in [
        ("true-test", "A supplied TRUE leaf"), ("false-test", "A supplied FALSE leaf"),
        ("unknown-test", "A supplied UNKNOWN leaf"), ("error-test", "A supplied ERROR leaf"),
        ("na-test", "A supplied NOT_APPLICABLE leaf"),
    ]:
        tests[name] = {"test_title": title, "capability": "independent.unknown", "require": {"item_requirement": {"items_found": "one_or_more"}}}
    assessment = {
        "assessment": {
            "id": "conformance-core-evaluate-not",
            "version": 1,
            "assessment_title": "SCAP-NG 0.4.1 core Evaluate, Require and not semantics",
            "mode": "automated", "class": "miscellaneous",
            "specification": {"id": "scap-ng.pre-alpha.assessment", "version": "0.4.1"},
            "tests": tests,
            "evaluate": {"and": [
                {"test": "true-test"}, {"not": {"test": "false-test"}},
                {"not": {"not": {"test": "true-test"}}},
                {"one": [{"test": "true-test"}, {"test": "false-test"}]},
                {"xor": [{"test": "true-test"}, {"test": "false-test"}]},
                {"or": [{"test": "false-test"}, {"test": "true-test"}]},
            ]},
        }
    }
    fixture = {
        "format": "scap-ng-conformance-evidence-0.1", "schema_version": "0.4.1",
        "case_id": "core-evaluate-not", "clock": {"now_utc": "2026-01-01T00:00:00Z", "timezone": "UTC", "locale": "C", "ordering": "document"},
        "test_outcomes": {"true-test": "true", "false-test": "false", "unknown-test": "unknown", "error-test": "error", "na-test": "not_applicable"},
        "variants": {"normal": {"test_outcomes": {"true-test": "true", "false-test": "false"}, "assessment_outcome": "true"},
                     "unknown": {"test_outcomes": {"true-test": "true", "false-test": "unknown"}, "assessment_outcome": "unknown"},
                     "error": {"test_outcomes": {"true-test": "true", "false-test": "error"}, "assessment_outcome": "error"},
                     "not-applicable": {"test_outcomes": {"true-test": "true", "false-test": "not_applicable"}, "assessment_outcome": "not_applicable"}},
    }
    return {"assessment": assessment, "fixture": fixture}


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def inventory() -> dict[str, Any]:
    paths = sorted(SCHEMA.glob("*.json")) + sorted((SCHEMA / "capability-mappings").rglob("*.json"))
    schema_docs = []
    enums = []
    constraints = []
    property_groups = []
    refs = []
    for path in paths:
        doc = load(path)
        rel = path.relative_to(ROOT).as_posix()
        e, c, p = enums_and_constraints(doc, rel)
        schema_docs.append({"path": rel, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "kind": "root" if path.parent == SCHEMA else "mapping"})
        enums.extend(e); constraints.extend(c); property_groups.extend(p)
        for pointer_path, node in walk_schema(doc):
            if isinstance(node, dict) and "$ref" in node:
                refs.append({"path": pointer_path or "/", "ref": node["$ref"], "source": rel})
    selector_contracts = load(SCHEMA / "native-selector-contracts.json")
    selector_contracts["_selector_defs"] = load(SCHEMA / "native-selector.schema.json").get("$defs", {})
    mappings = []
    for path in sorted((SCHEMA / "capability-mappings").rglob("*.json")):
        if path.name == "README.json":
            continue
        m = load(path); n = m.get("native", {})
        mappings.append({
            "capability": m["capability"], "status": path.parent.name,
            "source_path": path.relative_to(ROOT).as_posix(),
            "object_selectors": list(n.get("selector_map", {})),
            "selector_alternatives": n.get("object_selector_alternatives", []),
            "fields": list(n.get("state_field_map", {})),
            "field_datatypes": n.get("field_datatypes", {}),
            "test_source": n.get("test_source", {"kind": "object"}),
            "semantic_validator_rules": [r.get("id") for r in m.get("semantic_validator_rules", [])],
            "vector_policy": {
                "positive": "capability vector fixture",
                "negative": "capability vector fixture",
                "boundary": "capability vector fixture",
                "unknown": "portable status vector; scanner must preserve status",
                "error": "portable status vector; scanner must preserve status",
                "not_applicable": "portable applicability vector; scanner must preserve status",
                "invalid_authoring": "shared schema rejection vector",
            },
        })
    ops = set()
    for e in enums:
        if "operator" in e["pointer"] or "operation" in e["pointer"]:
            ops.update(v for v in e["values"] if isinstance(v, str))
    # Include every canonical operation from the schema definition, even if the
    # definition's pointer is not named operator.
    common = load(SCHEMA / "capability-common.schema.json")
    for _, node in walk_schema(common):
        if isinstance(node, dict) and node.get("title") in {"Comparison operation", "Logical operator"}:
            ops.update(node.get("enum", []))
    # Keep categories separate so an editor or adapter cannot mistake a
    # field-comparison token for a Boolean Evaluate operator.
    operator_inventory = {"comparison": [], "logical": [], "set": [], "functions": [], "field_predicate_properties": []}
    for file_name, definition_name, category in [
        ("capability-common.schema.json", "comparison_operation", "comparison"),
        ("capability-common.schema.json", "logical_operator", "logical"),
        ("capability-common.schema.json", "set_expression", "set"),
        ("variable-function-expression.schema.json", "function_call", "functions"),
    ]:
        doc = load(SCHEMA / file_name)
        definition = doc.get("$defs", {}).get(definition_name, {})
        values = []
        for _, node in walk_schema(definition):
            if isinstance(node, dict) and isinstance(node.get("enum"), list):
                values.extend(node["enum"])
        if category == "functions":
            operator_inventory[category] = sorted(set(values))
        else:
            operator_inventory[category] = sorted(set(values))
    language = load(SCHEMA / "assessment-language.schema.json")
    for name in ("scalar_field_predicate", "record_field_predicate", "object_selector_predicate"):
        operator_inventory["field_predicate_properties"].extend(
            k for k in language.get("$defs", {}).get(name, {}).get("properties", {})
            if k not in {"values_found", "values_matching", "datatype", "value_match", "redact_result", "selection_match"}
        )
    operator_inventory["field_predicate_properties"] = sorted(set(operator_inventory["field_predicate_properties"]))
    fields = []
    for row in mappings:
        for field in row["fields"]:
            fields.append({"capability": row["capability"], "field": field, "datatypes": row["field_datatypes"].get(field, []), "role": "selector" if field in row["object_selectors"] else "state"})
    definitions = []
    for path in sorted(SCHEMA.glob("*.json")):
        doc = load(path)
        for name, value in doc.get("$defs", {}).items():
            definitions.append({"schema": path.relative_to(ROOT).as_posix(), "name": name, "title": value.get("title"), "description": value.get("description")})
    return {
        "format": "scap-ng-schema-feature-inventory-0.1",
        "schema_version": "0.4.1",
        "schema_commit": git_sha(),
        "schema_family_sha256": digest(paths),
        "source": "vanderpol/scap-ng flat schema/ at exact Git commit",
        "generated_by": "conformance/tools/generate.py",
        "counts": {
            "schema_documents": len(schema_docs), "root_schemas": sum(d["kind"] == "root" and d["path"].endswith(".schema.json") for d in schema_docs),
            "capability_mappings": len(mappings), "supported_capabilities": sum(m["status"] == "supported" for m in mappings),
            "experimental_capabilities": sum(m["status"] == "experimental" for m in mappings),
            "schema_property_groups": len(property_groups), "schema_enums": len(enums),
            "schema_constraints": len(constraints), "schema_references": len(refs),
            "comparison_operations": len(ops),
        },
        "schema_documents": schema_docs,
        "capabilities": mappings,
        "operations": sorted(ops),
        "operator_inventory": operator_inventory,
        "fields": fields,
        "definitions": definitions,
        "enums": enums,
        "constraints": constraints,
        "property_groups": property_groups,
        "references": refs,
        "coverage_policy": {
            "required_vectors": ["positive", "negative", "boundary", "unknown", "error", "not_applicable", "invalid_authoring"],
            "status_semantics": "Expected statuses are typed oracle values, not Booleanized PASS/FAIL. Negation is only the canonical not expression.",
            "unsupported": "A capability without an independently qualified collector remains schema-covered but execution-unqualified.",
        },
        "schema_branch_tracking": {
            "capability_mappings": "vector-covered by one independent Assessment per mapping",
            "evaluate_require_variable_core": "vector-covered by cases/core/evaluate-not.assessment.yaml",
            "schema_properties_enums_constraints": "exhaustively inventoried; occurrence-specific executable vectors are not claimed by this increment",
            "untested_branches": [
                "All schema property/enum/constraint occurrences not reachable through the portable Assessment vectors; see properties, enums, and constraints arrays.",
                "Platform collector acquisition and native selector execution; requires an adapter receipt and is not inferred from schema validity.",
                "Scale/concurrency (100K/1M Items), real-host permissions, and cross-scanner equivalence; tracked outside this source oracle.",
            ],
        },
    }


def main() -> None:
    inv = inventory()
    write_json(OUT / "schema-coverage.json", inv)
    selector_contracts = load(SCHEMA / "native-selector-contracts.json")
    selector_contracts["_selector_defs"] = load(SCHEMA / "native-selector.schema.json").get("$defs", {})
    rows = []
    selector_mappings = []
    for path in sorted((SCHEMA / "capability-mappings").rglob("*.json")):
        if path.name != "README.json":
            selector_mappings.append(load(path))
    for path in sorted((SCHEMA / "capability-mappings").rglob("*.json")):
        if path.name == "README.json": continue
        mapping = load(path)
        body, fixture = build_assessment(mapping, selector_contracts)
        capability = mapping["capability"]; s = slug(capability)
        assessment_path = OUT / "cases" / "capabilities" / f"{s}.assessment.yaml"
        fixture_path = OUT / "fixtures" / f"{s}.json"
        expected_path = OUT / "expected" / f"{s}.json"
        assessment_path.parent.mkdir(parents=True, exist_ok=True)
        assessment_path.write_text(yaml.safe_dump(order_assessment_tests(body), sort_keys=False, allow_unicode=False), encoding="utf-8")
        write_json(fixture_path, fixture)
        field_count = len(mapping.get("native", {}).get("state_field_map", {}))
        state_field_names = list(mapping.get("native", {}).get("state_field_map", {}))
        has_fields = bool(state_field_names)
        negative_strategy = fixture["semantic_contract"]["negative_strategy"]
        negative_field = fixture["semantic_contract"]["negative_field"]
        positive_assertion = {"assessment_outcome": "true", "test_outcome": "true", "items_found": 1, "reason": "All declared fields match the collected Item."}
        negative_assertion = {"assessment_outcome": "false", "test_outcome": "false", "items_found": 0 if negative_strategy == "empty-collected-population" else 1, "reason": (f"Collected field {negative_field} is changed while selector fields remain identical; the mismatch is decisive." if negative_strategy == "field-mismatch" else "A collected empty population violates items_found: one_or_more; no selector is changed.")}
        if capability == "independent.unknown":
            # This capability is a fixed-result semantic source.  Collection
            # evidence is intentionally varied, but neither populated nor
            # empty evidence may manufacture TRUE/FALSE for a Test whose
            # canonical result is UNKNOWN.
            positive_assertion = {"assessment_outcome": "unknown", "test_outcome": "unknown", "items_found": 1, "reason": "The fixed-result capability is UNKNOWN regardless of collected evidence; the positive Item does not override its source contract."}
            negative_assertion = {"assessment_outcome": "unknown", "test_outcome": "unknown", "items_found": 0, "reason": "The fixed-result capability remains UNKNOWN with a distinct collected-empty evidence variant; this is not a FALSE Require witness."}
        elif has_fields:
            positive_assertion["items_satisfying"] = 1
            negative_assertion["items_satisfying"] = 0
        expected = {"format": "scap-ng-conformance-expected-0.1", "schema_version": "0.4.1", "case_id": capability, "variants": {
            "positive": positive_assertion,
            "negative": negative_assertion,
            "multi-item": {"assessment_outcome": "true", "test_outcome": "true", "items_found": 2, **({"items_satisfying": 2} if has_fields else {}), "reason": "Two distinct matching Items both satisfy the complete Require condition."},
            "boundary": {"assessment_outcome": "true", "test_outcome": "true", "items_found": 1, **({"items_satisfying": 1} if has_fields else {}), "reason": "Minimum permitted non-empty Item and field cardinality."},
            "empty": {"assessment_outcome": "unknown", "test_outcome": "unknown", "items_found": 0, "items_satisfying": 0, "reason": "No evidence was collected; absence is not a passing result."},
            "permission-denied": {"assessment_outcome": "unknown", "test_outcome": "unknown", "items_found": 0, "items_satisfying": 0, "reason": "Permission denied is preserved as UNKNOWN."},
            "error": {"assessment_outcome": "error", "test_outcome": "error", "items_found": 0, "items_satisfying": 0, "reason": "Collector ERROR is not converted to FALSE or TRUE."},
            "not-applicable": {"assessment_outcome": "not_applicable", "test_outcome": "not_applicable", "items_found": 0, "items_satisfying": 0, "reason": "Applicability is a typed outcome, not a Boolean false."},
        }}
        if capability == "independent.unknown":
            for variant_name, assertion in expected["variants"].items():
                assertion["assessment_outcome"] = "unknown"
                assertion["test_outcome"] = "unknown"
                assertion["reason"] = "The fixed-result capability is UNKNOWN for the distinct evidence variant; collection status does not manufacture a Boolean result."
            expected["semantic_rules"] = [{"id": "independent.unknown.fixed_result", "expected": "unknown", "reason": "Fixed-result source semantics dominate every distinct evidence variant; this is explicitly not a FALSE negative."}]
        write_json(expected_path, expected)
        def file_sha256(file_path: Path) -> str:
            return hashlib.sha256(file_path.read_bytes()).hexdigest()
        rows.append({"capability": capability, "status": path.parent.name,
                     "assessment": assessment_path.relative_to(OUT).as_posix(),
                     "fixture": fixture_path.relative_to(OUT).as_posix(),
                     "expected": expected_path.relative_to(OUT).as_posix(),
                     "sha256": {"assessment": file_sha256(assessment_path),
                                "fixture": file_sha256(fixture_path),
                                "expected": file_sha256(expected_path)},
                     "field_count": field_count, "vectors": list(expected["variants"])})
    core = build_core()
    core_assessment = OUT / "cases/core/evaluate-not.assessment.yaml"
    core_assessment.write_text(yaml.safe_dump(order_assessment_tests(core["assessment"]), sort_keys=False), encoding="utf-8")
    write_json(OUT / "fixtures/core-evaluate-not.json", core["fixture"])
    write_json(OUT / "expected/core-evaluate-not.json", {"format": "scap-ng-conformance-expected-0.1", "schema_version": "0.4.1", "case_id": "core-evaluate-not", "underlying": {"true-test": "true", "false-test": "false"}, "assertions": {"not(false)": "true", "not(not(true))": "true", "one(true,false)": "true", "xor(true,false)": "true", "and": "true", "unknown": "unknown", "error": "error", "not_applicable": "not_applicable"}, "reason": "The FALSE leaf remains explicitly FALSE; not is tested only as an enclosing expression."})
    operators = build_operator_suite(sorted(inv["operator_inventory"]["field_predicate_properties"]))
    op_assessment = OUT / "cases/core/comparison-operators.assessment.yaml"
    op_assessment.write_text(yaml.safe_dump(order_assessment_tests(operators["assessment"]), sort_keys=False), encoding="utf-8")
    write_json(OUT / "fixtures/core-comparison-operators.json", operators["fixture"])
    write_json(OUT / "expected/core-comparison-operators.json", operators["expected"])
    selectors = build_selector_alternative_suite(selector_mappings, selector_contracts)
    selector_assessment = OUT / "cases/core/selector-alternatives.assessment.yaml"
    selector_assessment.write_text(yaml.safe_dump(order_assessment_tests(selectors["assessment"]), sort_keys=False), encoding="utf-8")
    write_json(OUT / "fixtures/core-selector-alternatives.json", selectors["fixture"])
    write_json(OUT / "expected/core-selector-alternatives.json", selectors["expected"])
    multi_values = build_multi_value_suite(selector_mappings, selector_contracts)
    multi_value_assessment = OUT / "cases/core/multi-values.assessment.yaml"
    multi_value_assessment.write_text(yaml.safe_dump(order_assessment_tests(multi_values["assessment"]), sort_keys=False), encoding="utf-8")
    write_json(OUT / "fixtures/core-multi-values.json", multi_values["fixture"])
    write_json(OUT / "expected/core-multi-values.json", multi_values["expected"])
    enum_boundaries = build_enum_boundary_suite(selector_mappings)
    enum_assessment = OUT / "cases/core/enum-boundaries.assessment.yaml"
    enum_assessment.write_text(yaml.safe_dump(order_assessment_tests(enum_boundaries["assessment"]), sort_keys=False), encoding="utf-8")
    write_json(OUT / "fixtures/core-enum-boundaries.json", enum_boundaries["fixture"])
    write_json(OUT / "expected/core-enum-boundaries.json", enum_boundaries["expected"])
    cardinalities = build_cardinality_suite()
    cardinality_assessment = OUT / "cases/core/cardinalities.assessment.yaml"
    cardinality_assessment.write_text(yaml.safe_dump(order_assessment_tests(cardinalities["assessment"]), sort_keys=False), encoding="utf-8")
    write_json(OUT / "fixtures/core-cardinalities.json", cardinalities["fixture"])
    write_json(OUT / "expected/core-cardinalities.json", cardinalities["expected"])
    variable_interactions = build_variable_interaction_suite()
    variable_assessment = OUT / "cases/core/variable-interactions.assessment.yaml"
    variable_assessment.write_text(yaml.safe_dump(order_assessment_tests(variable_interactions["assessment"]), sort_keys=False), encoding="utf-8")
    write_json(OUT / "fixtures/core-variable-interactions.json", variable_interactions["fixture"])
    write_json(OUT / "expected/core-variable-interactions.json", variable_interactions["expected"])
    set_filters = build_set_filter_suite()
    set_assessment = OUT / "cases/core/set-filters.assessment.yaml"
    set_assessment.write_text(yaml.safe_dump(order_assessment_tests(set_filters["assessment"]), sort_keys=False), encoding="utf-8")
    write_json(OUT / "fixtures/core-set-filters.json", set_filters["fixture"])
    write_json(OUT / "expected/core-set-filters.json", set_filters["expected"])
    semantic_boundaries = build_semantic_boundary_suite()
    semantic_assessment = OUT / "cases/core/semantic-boundaries.assessment.yaml"
    semantic_assessment.write_text(yaml.safe_dump(order_assessment_tests(semantic_boundaries["assessment"]), sort_keys=False), encoding="utf-8")
    write_json(OUT / "fixtures/core-semantic-boundaries.json", semantic_boundaries["fixture"])
    write_json(OUT / "expected/core-semantic-boundaries.json", semantic_boundaries["expected"])
    variable_functions = build_variable_function_suite()
    function_assessment = OUT / "cases/core/variable-functions.assessment.yaml"
    function_assessment.write_text(yaml.safe_dump(order_assessment_tests(variable_functions["assessment"]), sort_keys=False), encoding="utf-8")
    write_json(OUT / "fixtures/core-variable-functions.json", variable_functions["fixture"])
    write_json(OUT / "expected/core-variable-functions.json", variable_functions["expected"])
    input_guards = build_input_guard_suite()
    input_assessment = OUT / "cases/core/input-guards.assessment.yaml"
    input_assessment.write_text(yaml.safe_dump(order_assessment_tests(input_guards["assessment"]), sort_keys=False), encoding="utf-8")
    write_json(OUT / "fixtures/core-input-guards.json", input_guards["fixture"])
    write_json(OUT / "expected/core-input-guards.json", input_guards["expected"])
    applicability = build_applicability_suite()
    applicability_assessment = OUT / "cases/core/applicability.assessment.yaml"
    applicability_assessment.write_text(yaml.safe_dump(order_assessment_tests(applicability["assessment"]), sort_keys=False), encoding="utf-8")
    write_json(OUT / "fixtures/core-applicability.json", applicability["fixture"])
    write_json(OUT / "expected/core-applicability.json", applicability["expected"])
    status_cases = build_status_and_policy_cases()
    status_rows = []
    for name, document, expected in status_cases["status"]:
        assessment_path = OUT / f"cases/core/status-{name}.assessment.yaml"
        assessment_path.write_text(yaml.safe_dump(order_assessment_tests(document), sort_keys=False), encoding="utf-8")
        fixture_path = OUT / f"fixtures/status-{name}.json"
        write_json(fixture_path, {"format": "scap-ng-conformance-evidence-0.1", "schema_version": "0.4.1", "case_id": f"status-{name}", "clock": {"now_utc": "2026-01-01T00:00:00Z", "timezone": "UTC", "locale": "C", "ordering": "document"}, "test_outcomes": {"status-test": expected["assessment_outcome"]}})
        expected_path = OUT / f"expected/status-{name}.json"; write_json(expected_path, expected)
        status_rows.append({"id": f"status-{name}", "schema": "assessment.schema.json", "assessment": assessment_path.relative_to(OUT).as_posix(), "fixture": fixture_path.relative_to(OUT).as_posix(), "expected": expected_path.relative_to(OUT).as_posix()})
    tailoring_path = OUT / "cases/policy/disabled-profile-tailoring.json"; write_json(tailoring_path, status_cases["tailoring"])
    benchmark_path = OUT / "cases/policy/disabled-profile-benchmark.json"; write_json(benchmark_path, status_cases["benchmark"])
    policy_expected_path = OUT / "expected/disabled-profile.json"; write_json(policy_expected_path, status_cases["policy_expected"])
    authoring_rows = []
    for case_id, document, expected in build_authoring_enum_cases():
        assessment_path = OUT / f"cases/core/{case_id}.assessment.yaml"; assessment_path.write_text(yaml.safe_dump(order_assessment_tests(document), sort_keys=False), encoding="utf-8")
        expected_path = OUT / f"expected/{case_id}.json"; write_json(expected_path, expected)
        authoring_rows.append({"id": case_id, "schema": "assessment.schema.json", "assessment": assessment_path.relative_to(OUT).as_posix(), "expected": expected_path.relative_to(OUT).as_posix()})
    invalid = {
        "assessment": {"id": "invalid-negate", "version": 1, "assessment_title": "invalid", "mode": "automated", "class": "miscellaneous", "specification": {"id": "scap-ng.pre-alpha.assessment", "version": "0.4.1"}, "tests": {"invalid-test": {"capability": "independent.unknown", "require": {"item_requirement": {"items_found": "one_or_more"}}, "negate": True}}}
    }
    (OUT / "cases/invalid/negate.assessment.yaml").write_text(yaml.safe_dump(invalid, sort_keys=False), encoding="utf-8")
    invalid_enum_cases = {
        "invalid-class": {"assessment": {"id": "invalid-class", "version": 1, "assessment_title": "invalid", "mode": "manual", "class": "not-a-class", "procedure": "invalid", "response": {"type": "technical-outcome", "choices": [{"value": "x", "outcome": "true"}], "allow_comment": False, "allow_evidence": False}}},
        "invalid-reported-elements": {"assessment": {"id": "invalid-reported-elements", "version": 1, "assessment_title": "invalid", "mode": "automated", "class": "miscellaneous", "specification": {"id": "scap-ng.pre-alpha.assessment", "version": "0.4.1"}, "tests": {"invalid-test": {"capability": "independent.unknown", "reported_elements": "not-an-option", "require": {"item_requirement": {"items_found": "one_or_more"}}}}, "evaluate": {"test": "invalid-test"}}},
        "invalid-manual-outcome": {"assessment": {"id": "invalid-manual-outcome", "version": 1, "assessment_title": "invalid", "mode": "manual", "class": "miscellaneous", "procedure": "invalid", "response": {"type": "technical-outcome", "choices": [{"value": "x", "outcome": "not-a-status"}], "allow_comment": False, "allow_evidence": False}}},
        "invalid-mode": {"assessment": {"id": "invalid-mode", "version": 1, "assessment_title": "invalid", "mode": "semi", "class": "miscellaneous"}},
        "invalid-variable-kind": {"assessment": {"id": "invalid-variable-kind", "version": 1, "assessment_title": "invalid", "mode": "automated", "class": "miscellaneous", "specification": {"id": "scap-ng.pre-alpha.assessment", "version": "0.4.1"}, "variables": {"bad-variable": {"kind": "external", "expression": {"literal": "x"}}}, "tests": {"invalid-test": {"capability": "independent.unknown", "require": {"item_requirement": {"items_found": "one_or_more"}}}}, "evaluate": {"test": "invalid-test"}}},
        "invalid-cardinality": {"assessment": {"id": "invalid-cardinality", "version": 1, "assessment_title": "invalid", "mode": "automated", "class": "miscellaneous", "specification": {"id": "scap-ng.pre-alpha.assessment", "version": "0.4.1"}, "tests": {"invalid-test": {"capability": "independent.unknown", "require": {"item_requirement": {"items_found": "sometimes"}}}}, "evaluate": {"test": "invalid-test"}}},
        "invalid-specification-version": {"assessment": {"id": "invalid-specification-version", "version": 1, "assessment_title": "invalid", "mode": "automated", "class": "miscellaneous", "specification": {"id": "scap-ng.pre-alpha.assessment", "version": "0.4.0"}, "tests": {"invalid-test": {"capability": "independent.unknown", "require": {"item_requirement": {"items_found": "one_or_more"}}}}, "evaluate": {"test": "invalid-test"}}},
        "invalid-reported-elements-duplicate": {"assessment": {"id": "invalid-reported-elements-duplicate", "version": 1, "assessment_title": "invalid", "mode": "automated", "class": "miscellaneous", "specification": {"id": "scap-ng.pre-alpha.assessment", "version": "0.4.1"}, "tests": {"invalid-test": {"capability": "independent.unknown", "reported_elements": ["value", "value"], "require": {"item_requirement": {"items_found": "one_or_more"}}}}, "evaluate": {"test": "invalid-test"}}},
        "invalid-empty-procedure": {"assessment": {"id": "invalid-empty-procedure", "version": 1, "assessment_title": "invalid", "mode": "manual", "class": "miscellaneous", "procedure": "", "response": {"type": "technical-outcome", "choices": [{"value": "x", "outcome": "true"}], "allow_comment": False, "allow_evidence": False}}},
        "invalid-id-pattern": {"assessment": {"id": "INVALID_ID", "version": 1, "assessment_title": "invalid", "mode": "manual", "class": "miscellaneous", "procedure": "invalid", "response": {"type": "technical-outcome", "choices": [{"value": "x", "outcome": "true"}], "allow_comment": False, "allow_evidence": False}}},
    }
    invalid_enum_cases["invalid-set-difference-cardinality"] = {
        "assessment": {
            "id": "invalid-set-difference-cardinality", "version": 1,
            "assessment_title": "invalid", "mode": "automated", "class": "miscellaneous",
            "specification": {"id": "scap-ng.pre-alpha.assessment", "version": "0.4.1"},
            "tests": {"invalid-test": {
                "test_title": "invalid Set difference", "capability": "linux.dpkginfo", "reported_elements": "all",
                "object": {"capability": "linux.dpkginfo", "set": {"operator": "difference", "operands": [
                    {"object": "left-object", "filters": [{"include": {"arch": {"values_found": "one_or_more", "values_matching": "every", "equals": "amd64"}}}]},
                    {"object": "right-object", "filters": [{"exclude": {"arch": {"values_found": "one_or_more", "values_matching": "every", "equals": "arm64"}}}]},
                    {"object": "third-object", "filters": [{"include": {"arch": {"values_found": "one_or_more", "values_matching": "every", "equals": "amd64"}}}]}
                ]}},
                "require": {"item_requirement": {"items_found": "one_or_more"}}
            }},
            "evaluate": {"test": "invalid-test"}
        }
    }
    for name, document in invalid_enum_cases.items():
        (OUT / f"cases/invalid/{name}.assessment.yaml").write_text(yaml.safe_dump(order_assessment_tests(document), sort_keys=False), encoding="utf-8")
    manifest = {
        "format": "scap-ng-native-conformance-manifest-0.1", "schema_version": "0.4.1", "schema_commit": inv["schema_commit"], "schema_family_sha256": inv["schema_family_sha256"],
        "source": "vanderpol/scap-ng", "issue": 87, "runner_contract": "conformance/CONTRACT.md", "schema_inventory": "conformance/schema-coverage.json", "coverage_audit": "conformance/coverage-audit.json", "capability_case_count": len(rows), "capabilities": rows,
        "authoring_cases": authoring_rows,
        "status_cases": status_rows + [{"id": "disabled-profile-tailoring", "schema": "tailoring.schema.json", "case": "cases/policy/disabled-profile-tailoring.json", "expected": "expected/disabled-profile.json"}, {"id": "disabled-profile-benchmark", "schema": "benchmark.schema.json", "case": "cases/policy/disabled-profile-benchmark.json", "expected": "expected/disabled-profile.json"}],
        "core_cases": [{"id": "core-evaluate-not", "assessment": "cases/core/evaluate-not.assessment.yaml", "fixture": "fixtures/core-evaluate-not.json", "expected": "expected/core-evaluate-not.json", "vectors": ["evaluate", "not", "double-not", "and", "or", "one", "xor", "unknown", "error", "not_applicable"]}, {"id": "core-variable-interactions", "assessment": "cases/core/variable-interactions.assessment.yaml", "fixture": "fixtures/core-variable-interactions.json", "expected": "expected/core-variable-interactions.json", "vectors": ["local-alias", "values-found-exactly-one", "false-leaf", "not-false"]}, {"id": "core-set-filters", "assessment": "cases/core/set-filters.assessment.yaml", "fixture": "fixtures/core-set-filters.json", "expected": "expected/core-set-filters.json", "vectors": ["include", "exclude", "union", "intersection", "difference"]}, {"id": "core-semantic-boundaries", "assessment": "cases/core/semantic-boundaries.assessment.yaml", "fixture": "fixtures/core-semantic-boundaries.json", "expected": "expected/core-semantic-boundaries.json", "vectors": ["file-selection-traversal", "windows-literal-name"]}, {"id": "core-variable-functions", "assessment": "cases/core/variable-functions.assessment.yaml", "fixture": "fixtures/core-variable-functions.json", "expected": "expected/core-variable-functions.json", "vectors": ["unique", "count", "concat", "merge"]}, {"id": "core-input-guards", "assessment": "cases/core/input-guards.assessment.yaml", "fixture": "fixtures/core-input-guards.json", "expected": "expected/core-input-guards.json", "vectors": ["provided", "absent", "explicit-empty", "too-many", "out-of-range"]}, {"id": "core-applicability", "assessment": "cases/core/applicability.assessment.yaml", "fixture": "fixtures/core-applicability.json", "expected": "expected/core-applicability.json", "vectors": ["applicable", "not-applicable", "deferred"]}, {"id": "core-comparison-operators", "assessment": "cases/core/comparison-operators.assessment.yaml", "fixture": "fixtures/core-comparison-operators.json", "expected": "expected/core-comparison-operators.json", "vectors": sorted(inv["operator_inventory"]["field_predicate_properties"])}, {"id": "core-selector-alternatives", "assessment": "cases/core/selector-alternatives.assessment.yaml", "fixture": "fixtures/core-selector-alternatives.json", "expected": "expected/core-selector-alternatives.json", "vectors": ["every-valid-selector-alternative"]}, {"id": "core-multi-values", "assessment": "cases/core/multi-values.assessment.yaml", "fixture": "fixtures/core-multi-values.json", "expected": "expected/core-multi-values.json", "vectors": ["applicable-capability-fields"]}, {"id": "core-enum-boundaries", "assessment": "cases/core/enum-boundaries.assessment.yaml", "fixture": "fixtures/core-enum-boundaries.json", "expected": "expected/core-enum-boundaries.json", "vectors": ["schema-admitted-selector-enums"]}, {"id": "core-cardinalities", "assessment": "cases/core/cardinalities.assessment.yaml", "fixture": "fixtures/core-cardinalities.json", "expected": "expected/core-cardinalities.json", "vectors": ["remaining-cardinalities"]}],
        "invalid_cases": [
            {"id": "invalid-negate", "assessment": "cases/invalid/negate.assessment.yaml", "expected": "schema-invalid", "reason": "negate is not canonical; not is the sole negation operator."},
            {"id": "invalid-variable-datatype", "assessment": "cases/invalid/variable-datatype.assessment.yaml", "expected": "schema-invalid", "reason": "Variables infer datatype from typed expressions; declaration datatype is not canonical."},
            {"id": "invalid-legacy-states", "assessment": "cases/invalid/legacy-states.assessment.yaml", "expected": "schema-invalid", "reason": "Legacy State wrappers are not part of the 0.4.1 language."},
            {"id": "invalid-class", "assessment": "cases/invalid/invalid-class.assessment.yaml", "expected": "schema-invalid", "reason": "Assessment class is a closed canonical enum."},
            {"id": "invalid-reported-elements", "assessment": "cases/invalid/invalid-reported-elements.assessment.yaml", "expected": "schema-invalid", "reason": "reported_elements admits only all, compared, or a valid explicit field list."},
            {"id": "invalid-manual-outcome", "assessment": "cases/invalid/invalid-manual-outcome.assessment.yaml", "expected": "schema-invalid", "reason": "Manual response outcomes are the six canonical technical statuses."},
            {"id": "invalid-mode", "assessment": "cases/invalid/invalid-mode.assessment.yaml", "expected": "schema-invalid", "reason": "Assessment mode is a closed manual/automated enum."},
            {"id": "invalid-variable-kind", "assessment": "cases/invalid/invalid-variable-kind.assessment.yaml", "expected": "schema-invalid", "reason": "Variable kind is limited to local and constant; no external declaration kind is canonical."},
            {"id": "invalid-cardinality", "assessment": "cases/invalid/invalid-cardinality.assessment.yaml", "expected": "schema-invalid", "reason": "Require cardinality is a closed canonical enum."},
            {"id": "invalid-specification-version", "assessment": "cases/invalid/invalid-specification-version.assessment.yaml", "expected": "schema-invalid", "reason": "Active Assessment authoring is pinned to specification version 0.4.1."},
            {"id": "invalid-reported-elements-duplicate", "assessment": "cases/invalid/invalid-reported-elements-duplicate.assessment.yaml", "expected": "schema-invalid", "reason": "Explicit reported element lists require unique field names."},
            {"id": "invalid-empty-procedure", "assessment": "cases/invalid/invalid-empty-procedure.assessment.yaml", "expected": "schema-invalid", "reason": "Manual procedure is required and cannot be empty."},
            {"id": "invalid-id-pattern", "assessment": "cases/invalid/invalid-id-pattern.assessment.yaml", "expected": "schema-invalid", "reason": "Native identifiers use the canonical lower-kebab pattern."},
            {"id": "invalid-set-difference-cardinality", "assessment": "cases/invalid/invalid-set-difference-cardinality.assessment.yaml", "expected": "schema-invalid", "reason": "Set difference admits at most two operands."},
        ],
        "execution_boundary": "Schema validation and oracle comparison are independent of RI execution. RI adapter coordination is RI issue #196.",
        "coverage_claim": "Inventory and vector presence are exhaustive for the pinned mappings; scanner execution remains unqualified until an independent adapter supplies receipts.",
    }
    write_json(OUT / "manifest.json", manifest)


if __name__ == "__main__":
    main()
