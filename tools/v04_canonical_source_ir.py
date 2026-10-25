#!/usr/bin/env python3
"""Canonical SCAP-NG 0.4.0 typed source-IR preflight (#232, #239).

Consumes *regenerated* canonical YAML and JSON authoring, never the older
research 0.4-A syntax. Normalizes independently parsed source and retains
the full approved AST, including unusual nested Test requirements. This is a
lossless compilation FRONT END, not executable scanner IR or a .scapng bundle.

The benchmark version mismatch is reported and blocks executable promotion;
the input declaration is never rewritten.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
from functools import lru_cache
import json
from pathlib import Path

from v04_field_requirement import field_scopes, validate_test

from v04_a_authoring_graph_index import (
    canonical_json, graph_index, read_authoring_archive,
)
from v04_a_benchmark_choice_version_closure import inspect_edges
from v04_a_lossless_ir import _check_assessment_dependency_targets
from v04_a_dataflow_index import index_assessment_dataflow


FORMAT = "scap-ng-0.4.0-canonical-typed-source-ir/0.1"
STATUS = "SOURCE_IR_VERIFIED_NOT_EXECUTABLE"


def _logical_source(path):
    for suffix in (".json", ".yaml"):
        if path.endswith(suffix) and path.startswith("authoring/"):
            return path[:-len(suffix)] + ".json"
    raise ValueError(f"not a canonical authoring source: {path!r}")


def normalize_documents(documents):
    """Preserve each AST while indexing explicitly authored Test requirements."""
    source = {}
    for path, doc in documents.items():
        logical = _logical_source(path)
        if logical in source:
            raise ValueError(f"duplicate source path across formats: {logical}")
        source[logical] = doc
    graph = graph_index(source)  # IDs, Rule choices, Test/Object/Variable refs.
    edges = inspect_edges(source)  # Benchmark-local specifications and choices.
    truth_dependency_count = _check_assessment_dependency_targets(source)
    dataflow_counts = Counter()
    records = []
    totals = Counter()
    for path, doc in sorted(source.items()):
        kind, body = next(iter(doc.items()))
        indexed = []
        if kind == "assessment" and body.get("mode") == "automated":
            specification = body.get("specification")
            if (not isinstance(specification, dict)
                    or specification.get("version") != "0.4.0"):
                raise ValueError(f"{path}: automated Assessment lacks 0.4.0 specification")
            for test_id, test in sorted((body.get("tests") or {}).items()):
                if not isinstance(test, dict):
                    raise ValueError(f"{path}: invalid Test {test_id}")
                if "collected_items_require" in test:
                    raise ValueError(f"{path}: legacy source requirement alias in {test_id}")
                obj = test.get("object")
                if isinstance(obj, dict) and "capability" in obj:
                    raise ValueError(f"{path}: redundant inline Object capability in {test_id}")
                cap = test.get("capability")
                if not isinstance(cap, str) or not cap:
                    raise ValueError(f"{path}: missing Test capability {test_id}")
                validate_test(test)
                requirement = test.get("require")
                shape = ('presence' if set(requirement) == {'items_found'}
                         else 'item_condition')
                indexed.append({
                    "id": test_id, "capability": cap, "requirement_shape": shape,
                    "requirement": requirement, "test_sha256": sha256(canonical_json(test)).hexdigest(),
                    "field_requirements": field_scopes(requirement),
                    "fallback_diagnostic": None,
                })
                totals[shape] += 1
        dataflow = None
        if kind == "assessment" and body.get("mode") == "automated":
            # Static dependency index only; never schedule collection or evaluate
            # a result while constructing a source IR.
            dataflow = index_assessment_dataflow(body)
            dataflow_counts["objects_variables_tests"] += len(dataflow["nodes"])
            dataflow_counts["edges"] += dataflow["edge_count"]
            dataflow_counts["source_sites"] += len(dataflow["sites"])
        record = {
            "path": path, "kind": kind, "id": body["id"],
            "source_sha256": sha256(canonical_json(doc)).hexdigest(),
            "source_ast": doc, "typed_tests": indexed,
            "source_dataflow": dataflow,
        }
        records.append(record)
        totals["documents"] += 1
        totals[kind] += 1
    return {
        "format": FORMAT, "status": STATUS,
        "source_graph_sha256": graph["graph_sha256"],
        "version_inventory": graph["version_inventory"],
        "benchmark_version_conflicts": edges["incompatible_edge_count"],
        "benchmark_version_conflict_samples": edges["incompatible_edge_samples"],
        "rule_choice_links": edges["counts"]["choice_links"],
        "assessment_truth_dependencies": truth_dependency_count,
        "source_dataflow": dict(sorted(dataflow_counts.items())),
        "totals": dict(sorted(totals.items())),
        "records": records,
        "executable_compiler_complete": False,
        "version_policy_approved": False,
        "signed_bundle": False,
        "scanner_semantics_verified": False,
    }


def decode_and_verify(ir):
    """Reject forged indexes, altered source, dropped States and stale counts."""
    if not isinstance(ir, dict) or ir.get("format") != FORMAT or ir.get("status") != STATUS:
        raise ValueError("unexpected or executable-looking IR")
    records = ir.get("records")
    if not isinstance(records, list) or not records:
        raise ValueError("no source records")
    docs = {}
    for row in records:
        path = row.get("path")
        if not isinstance(path, str) or _logical_source(path) != path or path in docs:
            raise ValueError("unsafe or duplicate normalized source path")
        doc = row.get("source_ast")
        if not isinstance(doc, dict) or sha256(canonical_json(doc)).hexdigest() != row.get("source_sha256"):
            raise ValueError(f"{path}: source AST checksum mismatch")
        docs[path] = doc
    expected = normalize_documents(docs)
    if canonical_json(expected) != canonical_json(ir):
        raise ValueError("typed index, source dependency, count or graph identity mismatch")
    return docs


def _schema_validators(schema_dir):
    from jsonschema import Draft202012Validator
    from referencing import Registry, Resource
    store = {}
    for path in sorted(schema_dir.rglob("*.json")):
        try:
            schema = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if not isinstance(schema, dict) or "$schema" not in schema:
            continue
        store[path.name] = schema
        if "$id" in schema:
            store[schema["$id"]] = schema
        store["https://scap-ng.dev/schema/v0.4.0/" + path.relative_to(schema_dir).as_posix()] = schema
    # The deprecated RefResolver can incorrectly resolve a nested local $ref
    # in assessment-language.schema.json against assessment.schema.json.
    # Preserve the referenced document's own $id/scope with a modern registry.
    registry = Registry().with_resources(
        (uri, Resource.from_contents(schema))
        for uri, schema in store.items() if uri.startswith("https://")
    )
    return {
        kind: Draft202012Validator(store[kind + ".schema.json"], registry=registry)
        for kind in ("assessment", "rule", "benchmark", "applicability")
    }


@lru_cache(maxsize=1)
def _supported_capabilities():
    """Accept only the version-pinned 0.4 native capability vocabulary.

    This is a closed catalog identity check, not a claim that the scanner
    implements a collector or that generated per-capability semantics passed.
    """
    root = Path(__file__).resolve().parents[1] / (
        "schema/v0.4.0/capability-mappings/supported")
    paths = sorted(root.glob("*.json"))
    if len(paths) != 100:
        raise ValueError("native 0.4 capability mapping census changed")
    caps = set()
    for path in paths:
        mapping = json.loads(path.read_text(encoding="utf-8"))
        cap = mapping.get("capability")
        if (not isinstance(cap, str) or cap != path.stem or
                mapping.get("specification_version") != "0.4.0" or
                cap in caps):
            raise ValueError(f"invalid or duplicated native 0.4 capability mapping: {path}")
        caps.add(cap)
    return frozenset(caps)


def _validate_capability_identities(documents):
    """Reject unknown Test and named Object capabilities before packaging."""
    supported = _supported_capabilities()
    for path, doc in sorted(documents.items()):
        assessment = doc.get("assessment")
        if not isinstance(assessment, dict) or assessment.get("mode") != "automated":
            continue
        for section in ("tests", "objects", "shared_objects"):
            entries = assessment.get(section) or {}
            if not isinstance(entries, dict):
                raise ValueError(f"{path}: invalid {section} declarations")
            for ident, node in entries.items():
                if not isinstance(node, dict):
                    continue  # Native structural schema reports this defect.
                cap = node.get("capability")
                if section == "tests" or cap is not None:
                    if not isinstance(cap, str) or cap not in supported:
                        raise ValueError(
                            f"{path}: unknown native 0.4 capability {cap!r} "
                            f"in {section}.{ident}")


def validate_docs(documents, validators):
    # Generic Assessment Schema cannot select a generated capability contract
    # from a string token. The native compiler must not silently accept Test
    # capabilities that have no reviewed version-local mapping.
    _validate_capability_identities(documents)
    from v04_object_contract import object_errors
    for path, doc in sorted(documents.items()):
        failures = list(object_errors(doc))
        if failures:
            first = failures[0]
            raise ValueError(f"{path}: native 0.4.0 Object schema failure: {first.message}")
    for path, doc in sorted(documents.items()):
        kind = next(iter(doc))
        failures = list(validators[kind].iter_errors(doc))
        if failures:
            first = sorted(failures, key=lambda e: (len(e.absolute_path), str(e.absolute_path)))[0]
            raise ValueError(f"{path}: native 0.4.0 schema failure at "
                             f"{list(first.absolute_path)}: {first.message[:280]}")


def compile_pair(json_archive, yaml_archive, *, validate_schema=True, legacy_review=False, legacy_original_03=None):
    if legacy_original_03 is not None and not legacy_review:
        raise ValueError("original 0.3 dependencies require an explicit legacy review view")
    json_docs = read_authoring_archive(json_archive, "json")
    yaml_docs = read_authoring_archive(yaml_archive, "yaml")
    if legacy_review:
        # Explicitly selected historical review inputs retain their original
        # archives/inverse ledgers. Validate and compile the canonical view,
        # using the same source-invertible generator as current authoring.
        from validate_v04_fields_condition_preview import native_schema_projection
        if ({_logical_source(path): doc for path, doc in json_docs.items()} !=
                {_logical_source(path): doc for path, doc in yaml_docs.items()}):
            raise ValueError("legacy review JSON/YAML source mismatch")
        closure = None
        if legacy_original_03 is not None:
            from v04_restore_missing_applicability import restore_legacy_view_documents
            original_paths = set(json_docs)
            json_docs, closure = restore_legacy_view_documents(json_docs, legacy_original_03)
            yaml_docs = {**yaml_docs, **{
                path.removesuffix('.json') + '.yaml': doc for path, doc in json_docs.items()
                if path not in original_paths}}
        json_docs = native_schema_projection(json_docs)
        yaml_docs = native_schema_projection(yaml_docs)
    if validate_schema:
        schema_dir = Path(__file__).resolve().parents[1] / "schema/v0.4.0"
        validators = _schema_validators(schema_dir)
        validate_docs(json_docs, validators)
        validate_docs(yaml_docs, validators)
    j_ir = normalize_documents(json_docs)
    y_ir = normalize_documents(yaml_docs)
    if canonical_json(j_ir) != canonical_json(y_ir):
        raise ValueError("independent canonical YAML/JSON typed source IR mismatch")
    if decode_and_verify(j_ir) != {
        _logical_source(path): doc for path, doc in json_docs.items()
    }:
        raise ValueError("JSON typed source IR reconstruction mismatch")
    if decode_and_verify(y_ir) != {
        _logical_source(path): doc for path, doc in yaml_docs.items()
    }:
        raise ValueError("YAML typed source IR reconstruction mismatch")
    data = canonical_json(j_ir) + b"\n"
    report = {
        "status": STATUS,
        "documents": j_ir["totals"]["documents"],
        "tests": sum(j_ir["totals"].get(key, 0) for key in
                     ("presence", "item_condition")),
        "requirement_shapes": {key: j_ir["totals"].get(key, 0) for key in
                               ("presence", "item_condition")},
        "rule_choice_links": j_ir["rule_choice_links"],
        "assessment_truth_dependencies": j_ir["assessment_truth_dependencies"],
        "source_dataflow": j_ir["source_dataflow"],
        "version_conflicting_choice_links": j_ir["benchmark_version_conflicts"],
        "version_policy_status": "BLOCKED_UNAPPROVED_SOURCE_MIGRATION"
                                 if j_ir["benchmark_version_conflicts"] else "DECLARED_COMPATIBLE",
        "canonical_ir_sha256": sha256(data).hexdigest(),
        "source_graph_sha256": j_ir["source_graph_sha256"],
        "source_reconstruction": "PASS",
        "yaml_json_byte_parity": "PASS",
        "native_source_schema": "PASS" if validate_schema else "NOT_TESTED_FIXTURE",
        **({"schema_validation_view": "CANONICAL_PROJECTION_OF_LEGACY_REVIEW_INPUT",
            "legacy_source_inverse": "PASS",
            **({"legacy_dependency_restoration": closure} if closure else {})}
           if legacy_review else {}),
        "native_executable_compiler_complete": False,
        "signed_bundle": False,
        "scanner_parity": False,
    }
    return data, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-archive", type=Path, required=True)
    parser.add_argument("--yaml-archive", type=Path, required=True)
    parser.add_argument("--out-ir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--assert-six", action="store_true")
    args = parser.parse_args()
    data, report = compile_pair(args.json_archive, args.yaml_archive)
    if args.assert_six and (
        report["documents"], report["tests"], report["rule_choice_links"],
        report["requirement_shapes"]
    ) != (4012, 1390, 2958,
          {"presence": 399, "item_condition": 991}):
        raise ValueError("canonical six-STIG source IR regression counts changed")
    args.out_ir.parent.mkdir(parents=True, exist_ok=True)
    args.out_ir.write_bytes(data)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n",
                           encoding="utf-8")
    print(json.dumps(report, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
