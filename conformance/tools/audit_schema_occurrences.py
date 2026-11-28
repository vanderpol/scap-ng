#!/usr/bin/env python3
"""Record enum, const, property and boundary evidence at canonical schema locations."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json

from jsonschema import Draft202012Validator, validators
from referencing import Registry
from referencing.jsonschema import DRAFT202012

from runner import CONFORMANCE, ROOT, load, schema_validator
from specification import ENTRY_POINTS, reachable_schema_locations, walk
from schema_documentation import SchemaStore

REPORT = CONFORMANCE / "qualification/schema-value-occurrences.json"
SHAPE_REPORT = CONFORMANCE / "qualification/schema-shape-occurrences.json"
BOUNDS = {
    "minimum": "number", "maximum": "number",
    "minLength": "string", "maxLength": "string",
    "minItems": "array", "maxItems": "array",
    "minProperties": "object", "maxProperties": "object",
}


def encode(data):
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def source_schema(inventory):
    schemas = {}
    for row in inventory["schema_documents"]:
        if row["kind"] != "root" or not row["path"].endswith(".schema.json"):
            continue
        path = ROOT / row["path"]
        raw = path.read_bytes()
        if sha256(raw).hexdigest() != row["sha256"]:
            raise ValueError(f"Pinned schema bytes changed for {row['path']}")
        schemas[row["path"]] = json.loads(raw)
    return schemas


def schema_locations(schemas):
    store = SchemaStore({document["$id"]: document for document in schemas.values()})
    reached = defaultdict(list)
    for cohort, names in ENTRY_POINTS.items():
        for name in names:
            schema = schemas[f"schema/{name}.schema.json"]
            for location in reachable_schema_locations(store, schema["$id"]):
                reached[location].append({"entry_point": name, "kind": cohort})

    occurrences = {}
    by_node = {}
    shapes = {"properties": {}, "bounds": {}}
    for source, document in schemas.items():
        for pointer, node, *_ in walk(document):
            if not isinstance(node, dict):
                continue
            scope = reached.get(document["$id"] + "#" + pointer, [])
            entry_names = [row["entry_point"] for row in scope]
            property_rows = {}
            for name in node.get("properties", {}):
                escaped = name.replace("~", "~0").replace("/", "~1")
                key = f"{source}#{pointer}/properties/{escaped}"
                row = {"entry_points": entry_names, "witnesses": {}}
                shapes["properties"][key] = row
                property_rows[name] = row
            if property_rows:
                by_node[(id(node), "properties")] = property_rows
            for keyword in BOUNDS.keys() & node.keys():
                key = f"{source}#{pointer}/{keyword}"
                row = {"entry_points": entry_names, "value": node[keyword], "witnesses": {}}
                shapes["bounds"][key] = row
                by_node[(id(node), keyword)] = row
            for keyword in ("enum", "const"):
                if keyword not in node:
                    continue
                values = node[keyword] if keyword == "enum" else [node[keyword]]
                key = f"{source}#{pointer}/{keyword}"
                occurrences[key] = {
                    "entry_points": scope,
                    "values": [{"value": value, "matches": {}} for value in values],
                    "rejections": {},
                }
                by_node[(id(node), keyword)] = key
    return occurrences, by_node, shapes


def case_sources(experimental_capabilities):
    manifest = load(CONFORMANCE / "manifest.json")
    supplemental = load(CONFORMANCE / "supplemental-manifest.json")
    declared = {}

    def register(path, schema, valid, scope="active"):
        details = (schema, valid, scope)
        if path in declared and declared[path] != details:
            raise ValueError(f"Conflicting schema dispositions for {path}")
        declared[path] = details

    assessment = "assessment.schema.json"
    for family in ("capabilities", "core_cases", "authoring_cases", "status_cases", "invalid_cases"):
        for row in manifest[family]:
            register(row.get("assessment", row.get("case")), row.get("schema", assessment), family != "invalid_cases")
    for row in supplemental["cases"]:
        register(row["source"], row["schema"], row["valid"])

    register("exact-equality/exact-equality.assessment.yaml", assessment, True)
    functions = load(CONFORMANCE / "function-boundaries/expected.json")
    register("function-boundaries/" + functions["source"], assessment, True)
    register("function-boundaries/" + functions["exceptional_expression"]["source"], assessment, True)
    input_policy = load(CONFORMANCE / "input-policy/expected.json")
    register("input-policy/" + input_policy["source"], assessment, True)
    register("input-policy/" + input_policy["predicate_limits"]["string_source"], assessment, True)
    register("logical-cardinality/one-xor.assessment.yaml", assessment, True)
    register("conditional-replay/mixed-guards.assessment.yaml", assessment, True)
    register("empty-projection/empty-collection.assessment.yaml", assessment, True)
    for source in ("content-package/sources.json", "manual-lifecycle/sources.json"):
        for member in load(CONFORMANCE / source)["members"]:
            register(member["source"], f'{member["kind"]}.schema.json', True)

    boundaries = "oval-self-assertion/yaml-boundaries"
    for platform in load(CONFORMANCE / boundaries / "expected.json")["platforms"].values():
        register(f'{boundaries}/{platform["native"]}', assessment, True)

    manual = load(CONFORMANCE / "manual-lifecycle/expected.json")
    for path in manual["standalone_results"].values():
        register(path, "manual-assessment-result.schema.json", True)

    metadata = load(CONFORMANCE / "file-metadata/expected.json")
    register("file-metadata/" + metadata["source"], assessment, True)

    result_evidence = load(CONFORMANCE / "result-evidence/expected.json")
    register("result-evidence/" + result_evidence["source"], assessment, True)
    for name, schema in result_evidence["documents"].items():
        register("result-evidence/" + name, schema, True)

    result_package = load(CONFORMANCE / "result-package/manifest.json")
    register("result-package/manifest.json", "result-package-manifest.schema.json", True, "draft-transport")
    for member in result_package["members"]:
        register("result-package/" + member["path"], member["kind"].replace("_", "-") + ".schema.json", True, "draft-transport")

    experiment = load(CONFORMANCE / "suite-index.json")
    for suite in experiment["suites"]:
        if suite["adoption"] == "experimental":
            for path in suite["artifact_sha256"]:
                if path.endswith(".assessment.yaml"):
                    register(path, assessment, True, "experimental")

    for path, (schema, valid, scope) in sorted(declared.items()):
        source = CONFORMANCE / path
        instance = load(source)
        capabilities = {row.get("capability") for row in instance.get("assessment", {}).get("tests", {}).values()
                        if isinstance(row, dict)}
        if capabilities & experimental_capabilities:
            scope = "experimental"
        yield path, schema, valid, scope, instance, sha256(source.read_bytes()).hexdigest()


def validator_class(schemas, by_node, occurrences, context):
    const = Draft202012Validator.VALIDATORS["const"]

    def track(keyword):
        original = Draft202012Validator.VALIDATORS[keyword]

        def wrapped(validator, expected, instance, schema):
            row = occurrences[by_node[(id(schema), keyword)]]
            path = context["path"]
            scope = context["scope"]
            error = next(original(validator, expected, instance, schema), None)
            if error is not None:
                if not context["valid"]:
                    row["rejections"].setdefault(scope, path)
                yield error
            elif context["valid"]:
                match = next(entry for entry in row["values"]
                             if next(const(validator, entry["value"], instance, schema), None) is None)
                match["matches"].setdefault(scope, path)

        return wrapped

    def properties(validator, expected, instance, schema):
        if context["valid"] and validator.is_type(instance, "object"):
            names = expected.keys() & instance.keys()
            if names:
                rows = by_node[(id(schema), "properties")]
                for name in names:
                    rows[name]["witnesses"].setdefault(context["scope"], context["path"])
        yield from Draft202012Validator.VALIDATORS["properties"](validator, expected, instance, schema)

    def bound(keyword, datatype):
        original = Draft202012Validator.VALIDATORS[keyword]

        def wrapped(validator, expected, instance, schema):
            error = next(original(validator, expected, instance, schema), None)
            applicable = validator.is_type(instance, datatype)
            if applicable:
                valid_document = context["valid"]
                if (error is None) == valid_document:
                    observed = instance if datatype == "number" else len(instance)
                    kind = ("boundary" if observed == expected else "interior") if valid_document else "rejected"
                    scope = context["scope"]
                    row = by_node[(id(schema), keyword)]
                    row["witnesses"].setdefault(scope, {}).setdefault(kind, context["path"])
            if error is not None:
                yield error
        return wrapped

    traced_validator = validators.extend(Draft202012Validator, {
        "enum": track("enum"), "const": track("const"), "properties": properties,
        **{name: bound(name, datatype) for name, datatype in BOUNDS.items()},
    })
    # Pin the dialect directly for every resource so referenced roots retain
    # the same instrumented validator when a reference is resolved.
    resources = {}
    for document in schemas.values():
        if document.pop("$schema") != "https://json-schema.org/draft/2020-12/schema":
            raise ValueError(f"Unexpected JSON Schema dialect {document['$id']}")
        resources[document["$id"]] = DRAFT202012.create_resource(document)
    return traced_validator, Registry().with_resources(resources.items())


def audit():
    inventory = load(CONFORMANCE / "schema-coverage.json")
    experimental = {row["capability"] for row in inventory["capabilities"] if row["status"] == "experimental"}
    schemas = source_schema(inventory)
    occurrences, by_node, shapes = schema_locations(schemas)
    context = {}
    traced_validator, registry = validator_class(schemas, by_node, occurrences, context)
    traced = {}
    plain = {}
    cases = {}
    for path, schema, valid, scope, instance, digest in case_sources(experimental):
        context.update(path=path, valid=valid, scope=scope)
        if schema not in traced:
            traced[schema] = traced_validator(schemas[f"schema/{schema}"], registry=registry)
            plain[schema] = schema_validator(schema)
        if plain[schema].is_valid(instance) != valid or traced[schema].is_valid(instance) != valid:
            raise ValueError(f"{path} disagrees with its expected schema disposition")
        cases[path] = {"schema": schema, "valid": valid, "scope": scope, "sha256": digest}

    counts = Counter()
    for row in occurrences.values():
        reachable = bool(row["entry_points"])
        counts["reachable_occurrences" if reachable else "unreachable_occurrences"] += 1
        for value in row["values"]:
            counts["declared_values"] += 1
            if reachable:
                counts["reachable_values"] += 1
                for scope in value["matches"]:
                    counts[f"matched_by_{scope}"] += 1
                if not value["matches"]:
                    counts["without_match"] += 1
    enum_report = {
        "format": "scap-ng-schema-value-occurrences-1",
        "schema_commit": inventory["schema_commit"], "schema_family_sha256": inventory["schema_family_sha256"],
        "interpretation": "Each match is a successful enum or const comparison while checking a schema-valid document. "
                          "The containing branch can still fail another constraint. "
                          "Rejections are individual comparisons reached in schema-invalid cases. "
                          "The corpus paths are published static native documents. "
                          "Runtime mutants, source XML and scanner semantics are measured in separate receipts.",
        "coverage": dict(counts), "cases": cases, "occurrences": occurrences,
    }


    shape_counts = {}
    for kind, rows in shapes.items():
        totals = Counter()
        for row in rows.values():
            if row["entry_points"]:
                totals["reachable"] += 1
                if not row["witnesses"]:
                    totals["without_witness"] += 1
                for scope, witness in row["witnesses"].items():
                    totals[f"witnessed_by_{scope}"] += 1
                    if kind == "bounds":
                        for disposition in witness:
                            totals[f"{disposition}_by_{scope}"] += 1
            else:
                totals["unreachable"] += 1
        shape_counts[kind] = dict(totals)
    return enum_report, {
        "format": "scap-ng-schema-shape-occurrences-1",
        "schema_commit": inventory["schema_commit"],
        "schema_family_sha256": inventory["schema_family_sha256"],
        "interpretation": "Property rows identify a member present during validation of a schema-valid "
                          "document. Bound rows identify an applicable comparison at the exact bound, "
                          "inside it, or rejected in an invalid document. Individual comparisons can "
                          "occur in a sibling branch that fails another constraint. Mutations run in "
                          "separate local tests and do not enter these static-document counts.",
        "coverage": shape_counts,
        "documents": cases,
        **shapes,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    for path, report in zip((REPORT, SHAPE_REPORT), audit(), strict=True):
        rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != rendered:
                raise SystemExit(f"Schema occurrence receipt is stale: {path.name}")
        else:
            path.write_text(rendered, encoding="utf-8")
        print(encode(report["coverage"]))
