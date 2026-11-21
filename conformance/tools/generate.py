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
        "require": {"item_requirement": {"items_found": "one_or_more"}},
    }
    if state_fields:
        test["require"]["item_requirement"]["items_satisfying"] = "every"
        test["require"]["field_requirement"] = {"values_found": "one_or_more", "values_matching": "every"}
        test["require"]["fields"] = {field: predicate(value, field_types[field]) for field, value in field_values.items()}
    if capability != "independent.unknown":
        test["reported_elements"] = "all"
    if native.get("test_source", {}).get("kind") == "none":
        # Singleton sources intentionally have no Object.
        pass
    elif native.get("test_source", {}).get("kind") == "variable":
        variable_name = f"{s}-variable"[:64]
        body["assessment"]["variables"] = {
            variable_name: {"kind": "constant", "expression": {"literal": {"datatype": "string", "value": "fixture-value"}}}
        }
        test["variable"] = variable_name
    else:
        test["object"] = {"capability": capability, **object_fields}
    body["assessment"]["tests"][test_name] = test
    # The evidence fixture is intentionally separate from the source assessment.
    fields = {
        field: {"datatype": field_types[field], "value": value, "status": "collected"}
        for field, value in field_values.items()
    }
    item = {"id": f"{s}-item", "capability": capability, "fields": fields, "status": "collected"}
    fixture = {
        "format": "scap-ng-conformance-evidence-0.1",
        "schema_version": "0.4.1",
        "case_id": capability,
        "clock": {"now_utc": "2026-01-01T00:00:00Z", "timezone": "UTC", "locale": "C", "ordering": "document"},
        "items": [item],
        "variants": {
            "positive": {"items": [item], "acquisition": "collected"},
            "negative": {"items": [{**item, "fields": {**fields, **({next(iter(fields)): {**fields[next(iter(fields))], "value": different_value(fields[next(iter(fields))]["value"], fields[next(iter(fields))]["datatype"])} } if fields else {})}}], "acquisition": "collected"},
            "boundary": {"items": [item], "acquisition": "collected", "boundary": "minimum one Item and one value per required field"},
            "empty": {"items": [], "acquisition": "not_collected"},
            "permission-denied": {"items": [], "acquisition": "denied"},
            "error": {"items": [], "acquisition": "error"},
            "not-applicable": {"items": [], "acquisition": "not_applicable"},
        },
    }
    return body, fixture


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
    for path in sorted((SCHEMA / "capability-mappings").rglob("*.json")):
        if path.name == "README.json": continue
        mapping = load(path)
        body, fixture = build_assessment(mapping, selector_contracts)
        capability = mapping["capability"]; s = slug(capability)
        assessment_path = OUT / "cases" / "capabilities" / f"{s}.assessment.yaml"
        fixture_path = OUT / "fixtures" / f"{s}.json"
        expected_path = OUT / "expected" / f"{s}.json"
        assessment_path.parent.mkdir(parents=True, exist_ok=True)
        assessment_path.write_text(yaml.safe_dump(body, sort_keys=False, allow_unicode=False), encoding="utf-8")
        write_json(fixture_path, fixture)
        field_count = len(mapping.get("native", {}).get("state_field_map", {}))
        expected = {"format": "scap-ng-conformance-expected-0.1", "schema_version": "0.4.1", "case_id": capability, "variants": {
            "positive": {"assessment_outcome": "true", "test_outcome": "true", "items_found": 1, "items_satisfying": 1, "reason": "All declared fields match the collected Item."},
            "negative": {"assessment_outcome": "false", "test_outcome": "false", "items_found": 1, "items_satisfying": 0, "reason": "A deterministic field mismatch is decisive; no negation hides it."},
            "boundary": {"assessment_outcome": "true", "test_outcome": "true", "items_found": 1, "items_satisfying": 1, "reason": "Minimum permitted non-empty Item and field cardinality."},
            "empty": {"assessment_outcome": "unknown", "test_outcome": "unknown", "items_found": 0, "items_satisfying": 0, "reason": "No evidence was collected; absence is not a passing result."},
            "permission-denied": {"assessment_outcome": "unknown", "test_outcome": "unknown", "items_found": 0, "items_satisfying": 0, "reason": "Permission denied is preserved as UNKNOWN."},
            "error": {"assessment_outcome": "error", "test_outcome": "error", "items_found": 0, "items_satisfying": 0, "reason": "Collector ERROR is not converted to FALSE or TRUE."},
            "not-applicable": {"assessment_outcome": "not_applicable", "test_outcome": "not_applicable", "items_found": 0, "items_satisfying": 0, "reason": "Applicability is a typed outcome, not a Boolean false."},
        }}
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
    core_assessment.write_text(yaml.safe_dump(core["assessment"], sort_keys=False), encoding="utf-8")
    write_json(OUT / "fixtures/core-evaluate-not.json", core["fixture"])
    write_json(OUT / "expected/core-evaluate-not.json", {"format": "scap-ng-conformance-expected-0.1", "schema_version": "0.4.1", "case_id": "core-evaluate-not", "underlying": {"true-test": "true", "false-test": "false"}, "assertions": {"not(false)": "true", "not(not(true))": "true", "one(true,false)": "true", "xor(true,false)": "true", "and": "true", "unknown": "unknown", "error": "error", "not_applicable": "not_applicable"}, "reason": "The FALSE leaf remains explicitly FALSE; not is tested only as an enclosing expression."})
    invalid = {
        "assessment": {"id": "invalid-negate", "version": 1, "assessment_title": "invalid", "mode": "automated", "class": "miscellaneous", "specification": {"id": "scap-ng.pre-alpha.assessment", "version": "0.4.1"}, "tests": {"invalid-test": {"capability": "independent.unknown", "require": {"item_requirement": {"items_found": "one_or_more"}}, "negate": True}}}
    }
    (OUT / "cases/invalid/negate.assessment.yaml").write_text(yaml.safe_dump(invalid, sort_keys=False), encoding="utf-8")
    manifest = {
        "format": "scap-ng-native-conformance-manifest-0.1", "schema_version": "0.4.1", "schema_commit": inv["schema_commit"], "schema_family_sha256": inv["schema_family_sha256"],
        "source": "vanderpol/scap-ng", "issue": 87, "runner_contract": "conformance/CONTRACT.md", "schema_inventory": "conformance/schema-coverage.json", "capability_case_count": len(rows), "capabilities": rows,
        "core_cases": [{"id": "core-evaluate-not", "assessment": "cases/core/evaluate-not.assessment.yaml", "fixture": "fixtures/core-evaluate-not.json", "expected": "expected/core-evaluate-not.json", "vectors": ["evaluate", "not", "double-not", "and", "or", "one", "xor", "unknown", "error", "not_applicable"]}],
        "invalid_cases": [
            {"id": "invalid-negate", "assessment": "cases/invalid/negate.assessment.yaml", "expected": "schema-invalid", "reason": "negate is not canonical; not is the sole negation operator."},
            {"id": "invalid-variable-datatype", "assessment": "cases/invalid/variable-datatype.assessment.yaml", "expected": "schema-invalid", "reason": "Variables infer datatype from typed expressions; declaration datatype is not canonical."},
            {"id": "invalid-legacy-states", "assessment": "cases/invalid/legacy-states.assessment.yaml", "expected": "schema-invalid", "reason": "Legacy State wrappers are not part of the 0.4.1 language."},
        ],
        "execution_boundary": "Schema validation and oracle comparison are independent of RI execution. RI adapter coordination is RI issue #196.",
        "coverage_claim": "Inventory and vector presence are exhaustive for the pinned mappings; scanner execution remains unqualified until an independent adapter supplies receipts.",
    }
    write_json(OUT / "manifest.json", manifest)


if __name__ == "__main__":
    main()
