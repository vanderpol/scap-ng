#!/usr/bin/env python3
"""Compile canonical 0.4.0 Assessments into manifest-linked .scapng packages.

This is the 0.4 native equivalent of the 0.2/0.3 content compiler: a
deterministic, manifest-authoritative content graph with separately compiled
Test dispatch and six-state result programs. The Test programs preserve exact
0.4 source operands; collection and live scanner execution are NOT claimed.

Inputs may be a previously verified 0.4 source-preview ZIP (fast development),
an independently parsed YAML-only or JSON-only canonical authoring archive,
or both formats with byte-identical compiled-bundle parity (release).
Refs #232 #229.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from hashlib import sha256
import io
import json
from pathlib import Path
import re
import zipfile
from functools import lru_cache

from v04_a_authoring_graph_index import (
    canonical_json, graph_index, read_authoring_archive,
)
from v04_a_benchmark_choice_version_closure import inspect_edges
from v04_canonical_result_plan import compile_canonical_result_plan
from v04_canonical_source_ir import (
    compile_pair, decode_and_verify, normalize_documents, validate_docs,
)
from v04_canonical_unsigned_package import (
    _manifest_schema, _package_validators, _strict_json,
    _verify_exact_rule_inventory, _write_member, partition_documents,
    verify_package as verify_source_package,
)
from v04_field_requirement import validate_test
from v04_a_dataflow_index import index_assessment_dataflow


FORMAT_VERSION = "0.4.0"
PROGRAM_FORMAT = "scap-ng-0.4.0-native-assessment-program/0.1"
STAGE = "compiled-native-0.4.0-program-not-scanner-validated/0.1"
MANIFEST_MEMBER = "META-INF/manifest.json"
DOCUMENT_KINDS = {"benchmark": "benchmark", "rule": "rule",
                  "assessment": "assessment", "applicability": "applicability_catalog"}


def _read_archive(raw):
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)) or archive.testzip() is not None:
            raise ValueError("duplicate or damaged ZIP members")
        return {name: archive.read(name) for name in names}


def _safe_path(kind, identity):
    if kind not in DOCUMENT_KINDS or not isinstance(identity, str) or not identity:
        raise ValueError("invalid native document identity")
    if kind == "benchmark":
        return "benchmark.json"
    if kind == "applicability":
        return "applicability.json"
    category = "rules" if kind == "rule" else "assessments"
    stem = re.sub(r"[^a-zA-Z0-9._-]+", "_", identity).strip("._-") or kind
    # Keep meaningful IDs visible while ensuring injectivity and path budgets.
    suffix = sha256((kind + "\0" + identity).encode()).hexdigest()[:12]
    budget = 160 - len(category) - len(suffix) - len("/-.json")
    return f"{category}/{stem[:budget]}-{suffix}.json"


def _program_path(assessment_id):
    digest = sha256(assessment_id.encode("utf-8")).hexdigest()
    return f"programs/{digest}.json"


def compile_test_instruction(test_id, test):
    """Preserve the complete approved requirement as a typed dispatch operand.

    Population and satisfaction counts remain independent, including nested
    field/record counts. Legacy State fallback is rejected by the same schema.
    """
    if not isinstance(test_id, str) or not isinstance(test, dict):
        raise ValueError("invalid Test instruction")
    validate_test(test)
    if not isinstance(test.get("capability"), str) or not test["capability"]:
        raise ValueError(f"Test {test_id}: missing collector capability")
    if test['capability'] not in _compiler_capabilities():
        raise ValueError('unknown native 0.4 capability ' + repr(test['capability']))
    if "collected_items_require" in test:
        raise ValueError("legacy collected_items_require is not canonical 0.4")
    if isinstance(test.get("object"), dict) and "capability" in test["object"]:
        raise ValueError("inline Object capability is redundant in 0.4")
    requirement = test['require']
    opcode = ('CHECK_COLLECTION_PRESENCE' if set(requirement) == {'items_found'}
              else 'CHECK_ITEM_CONDITION')
    return {
        "opcode": opcode,
        "test_id": test_id,
        "capability": test["capability"],
        "source_test_sha256": sha256(canonical_json(test)).hexdigest(),
        "operands": deepcopy(test),
    }


@lru_cache(maxsize=1)
def _compiler_capabilities():
    from v04_canonical_source_ir import _supported_capabilities
    return _supported_capabilities()


def compile_assessment_program(assessment):
    if not isinstance(assessment, dict) or assessment.get("mode") != "automated":
        raise ValueError("native program requires automated Assessment")
    tests = assessment.get("tests") or {}
    if not isinstance(tests, dict):
        raise ValueError("invalid Assessment Tests")
    index_assessment_dataflow(assessment)  # Resolve source DAGs and for_each lineage.
    for test_id, test in tests.items():
        obj = test.get('object')
        if isinstance(obj, str):
            shared = assessment.get('shared_objects') or {}
            if obj not in shared:
                raise ValueError(f'Test {test_id}: unresolved Object {obj}')
            if shared[obj].get('capability') != test.get('capability'):
                raise ValueError(f'Test {test_id}: referenced Object capability conflicts with Test')
    instructions = [compile_test_instruction(k, t) for k, t in sorted(tests.items())]
    result = compile_canonical_result_plan(assessment)
    required = set(result["requires"]["tests"])
    missing = sorted(required - set(tests))
    if missing:
        raise ValueError("result program references missing Test: " + ", ".join(missing))
    return {
        "format": PROGRAM_FORMAT,
        "assessment_id": assessment["id"],
        "assessment_source_sha256": sha256(canonical_json(assessment)).hexdigest(),
        "test_instructions": instructions,
        "result_instructions": result["instructions"],
        "result_requires": result["requires"],
        "result_expression_sha256": result["source_sha256"],
        "scanner_evaluated": False,
    }


def build_bundle(documents, *, validate_schema=True):
    """Compile one complete Benchmark with a program for every automated Assessment."""
    if not isinstance(documents, dict) or not documents:
        raise ValueError("no native documents")
    if validate_schema:
        validate_docs(documents, _package_validators())
    graph = graph_index(documents)
    edges = inspect_edges(documents)
    if edges["incompatible_edge_count"] or len(edges["benchmarks"]) != 1:
        raise ValueError("expected one closed 0.4 Benchmark Assessment graph")
    benchmark = next(doc["benchmark"] for doc in documents.values() if "benchmark" in doc)
    _verify_exact_rule_inventory(documents, benchmark)
    object_index = {}
    program_index = {}
    members = {}
    seen_paths = set()
    for _path, doc in sorted(documents.items()):
        kind, body = next(iter(doc.items()))
        ident = body["id"]
        path = _safe_path(kind, ident)
        if ident in object_index or path in seen_paths:
            raise ValueError(f"duplicate native document identity or member {ident}")
        seen_paths.add(path)
        serialized = canonical_json(doc)
        members[path] = serialized
        object_index[ident] = {"type": DOCUMENT_KINDS[kind],
                               "version": body.get("version"),
                               "path": path, "sha256": sha256(serialized).hexdigest(),
                               "size": len(serialized)}
        if kind == "assessment" and body.get("mode") == "automated":
            compiled = canonical_json(compile_assessment_program(body))
            program_path = _program_path(ident)
            if program_path in members:
                raise ValueError("duplicate program identity")
            members[program_path] = compiled
            program_index[ident] = {"path": program_path,
                                    "sha256": sha256(compiled).hexdigest(),
                                    "size": len(compiled)}
    manifest = {
        "format": "scap-ng-package-manifest",
        "format_version": FORMAT_VERSION,
        "benchmark_id": benchmark["id"],
        "benchmark_version": benchmark.get("version"),
        "entrypoint": benchmark["id"],
        "objects": dict(sorted(object_index.items())),
        "integrity": {"algorithm": "sha-256", "unexpected_members": "reject"},
        "build_provenance": {
            "stage": STAGE,
            "source_graph_sha256": graph["graph_sha256"],
            "rule_choice_links": edges["counts"]["choice_links"],
            "source_documents": len(documents),
            "compiled_programs": dict(sorted(program_index.items())),
            "scanner_evaluation_verified": False,
            "publisher_signature_verified": False,
        },
        "signature": {"format": None, "path": None,
                      "certificate_path": None, "trust": None},
    }
    _manifest_schema().validate(manifest)
    members[MANIFEST_MEMBER] = canonical_json(manifest)
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w") as archive:
        for name, content in sorted(members.items()):
            _write_member(archive, name, content)
    return out.getvalue(), manifest


def verify_bundle(raw, *, validate_schema=True):
    """Recompile all programs from independently decoded documents and compare."""
    members = _read_archive(raw)
    if MANIFEST_MEMBER not in members:
        raise ValueError("missing compiled manifest")
    manifest_bytes = members[MANIFEST_MEMBER]
    manifest = _strict_json(manifest_bytes)
    if canonical_json(manifest) != manifest_bytes:
        raise ValueError("noncanonical manifest")
    _manifest_schema().validate(manifest)
    provenance = manifest["build_provenance"]
    if (manifest["format_version"] != FORMAT_VERSION or
            not isinstance(provenance, dict) or
            provenance.get("stage") != STAGE or
            provenance.get("scanner_evaluation_verified") is not False or
            provenance.get("publisher_signature_verified") is not False):
        raise ValueError("not a supported compiled native 0.4 bundle")
    if any(x is not None for x in manifest["signature"].values()):
        raise ValueError("unsigned compiler cannot claim a signature")
    expected = {MANIFEST_MEMBER}
    documents = {}
    assessment_payloads = {}
    for ident, info in manifest["objects"].items():
        kind = next((kind for kind, out in DOCUMENT_KINDS.items()
                     if out == info["type"]), None)
        if kind is None or info["path"] != _safe_path(kind, ident):
            raise ValueError("incorrect logical ID/member path")
        name = info["path"]
        if name in expected or name not in members:
            raise ValueError("missing or duplicate document member")
        expected.add(name)
        data = members[name]
        if len(data) != info["size"] or sha256(data).hexdigest() != info["sha256"]:
            raise ValueError("compiled document digest mismatch")
        document = _strict_json(data)
        if (canonical_json(document) != data or list(document) != [kind] or
                document[kind].get("id") != ident or
                document[kind].get("version") != info["version"]):
            raise ValueError("compiled document content/identity mismatch")
        documents[f"authoring/compiled/{kind}/{ident}.json"] = document
        if kind == "assessment" and document[kind].get("mode") == "automated":
            assessment_payloads[ident] = document[kind]
    benchmark = next((x["benchmark"] for x in documents.values() if "benchmark" in x), None)
    if (not benchmark or benchmark["id"] != manifest["benchmark_id"] or
            manifest["entrypoint"] != benchmark["id"] or
            manifest["benchmark_version"] != benchmark.get("version")):
        raise ValueError("compiled Benchmark entrypoint mismatch")
    _verify_exact_rule_inventory(documents, benchmark)
    programs = provenance.get("compiled_programs")
    if not isinstance(programs, dict) or set(programs) != set(assessment_payloads):
        raise ValueError("incomplete automated Assessment program inventory")
    for ident, info in programs.items():
        path = _program_path(ident)
        if info.get("path") != path or path in expected or path not in members:
            raise ValueError("missing or duplicate compiled program")
        expected.add(path)
        data = members[path]
        if len(data) != info.get("size") or sha256(data).hexdigest() != info.get("sha256"):
            raise ValueError("compiled program digest mismatch")
        if data != canonical_json(compile_assessment_program(assessment_payloads[ident])):
            raise ValueError("compiled program is stale or has altered Test semantics")
    if set(members) != expected:
        raise ValueError("extra or unlisted compiled package member")
    if validate_schema:
        validate_docs(documents, _package_validators())
    graph = graph_index(documents)
    edges = inspect_edges(documents)
    if (edges["incompatible_edge_count"] or len(edges["benchmarks"]) != 1 or
            graph["graph_sha256"] != provenance["source_graph_sha256"] or
            len(documents) != provenance["source_documents"] or
            edges["counts"]["choice_links"] != provenance["rule_choice_links"]):
        raise ValueError("compiled logical graph mismatch")
    return {"status": "NATIVE_040_COMPILED_CONTENT_BUNDLE_NOT_SCANNER_TESTED",
            "benchmark": benchmark["id"], "documents": len(documents),
            "programs": len(programs),
            "tests": sum(len(p.get("tests") or {}) for p in assessment_payloads.values()),
            "source_graph_sha256": graph["graph_sha256"],
            "scanner_evaluated": False, "signature_verified": False}


def compile_from_source_package(raw, *, validate_schema=True):
    """One-STIG development path; source integrity is checked before compiling."""
    verify_source_package(raw, validate_schema=validate_schema)
    members = _read_archive(raw)
    manifest = _strict_json(members[MANIFEST_MEMBER])
    documents = {}
    for logical_id, info in manifest["objects"].items():
        doc = _strict_json(members[info["path"]])
        documents[f"authoring/verified/{logical_id}.json"] = doc
    compiled, _ = build_bundle(documents, validate_schema=False)
    return compiled, verify_bundle(compiled, validate_schema=validate_schema)


def _build_partitioned_bundles(documents):
    """Compile each closed Benchmark graph without depending on file suffixes."""
    partitions = partition_documents(documents)
    bundles = {}
    for folder, subset in sorted(partitions.items()):
        bundles[folder], _ = build_bundle(subset, validate_schema=False)
    return bundles


def _verify_partitioned_bundles(bundles, *, validate_schema):
    return {name: verify_bundle(raw, validate_schema=validate_schema)
            for name, raw in sorted(bundles.items())}


def compile_from_archive(archive, source_format, *, validate_schema=True):
    """Compile a JSON-only or YAML-only authoring archive independently.

    A single source format remains subject to the same full typed-source,
    graph, version-closure, capability and bundle-verification gates. No
    alternate parser or sibling serialization is used as a fallback.
    """
    documents = read_authoring_archive(archive, source_format)
    if validate_schema:
        validate_docs(documents, _package_validators())
    ir = normalize_documents(documents)
    if ir["benchmark_version_conflicts"]:
        raise ValueError("native authoring versions are incompatible")
    recovered = decode_and_verify(ir)
    bundles = _build_partitioned_bundles(recovered)
    return bundles, _verify_partitioned_bundles(
        bundles, validate_schema=validate_schema)


def compile_from_pair(json_zip, yaml_zip, *, validate_schema=True):
    """Release path: independently parse AND compile both serializations."""
    _, validation = compile_pair(json_zip, yaml_zip, validate_schema=validate_schema)
    if validation["version_conflicting_choice_links"]:
        raise ValueError("native authoring versions are incompatible")
    json_docs = read_authoring_archive(json_zip, "json")
    yaml_docs = read_authoring_archive(yaml_zip, "yaml")
    json_bundles = _build_partitioned_bundles(json_docs)
    yaml_bundles = _build_partitioned_bundles(yaml_docs)
    if json_bundles != yaml_bundles:
        raise ValueError("independent YAML/JSON compiled bundle mismatch")
    # The paired front end already proved typed source-IR reconstruction and
    # exact YAML/JSON source parity. Verify the identical compiled bytes once.
    return json_bundles, _verify_partitioned_bundles(
        json_bundles, validate_schema=validate_schema)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-package", type=Path)
    parser.add_argument("--json-archive", type=Path)
    parser.add_argument("--yaml-archive", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    if args.source_package and (args.json_archive or args.yaml_archive):
        parser.error("--source-package cannot accompany authoring archives")
    if not (args.source_package or args.json_archive or args.yaml_archive):
        parser.error("provide a source package or at least one authoring archive")
    if args.source_package:
        name = args.source_package.name.removesuffix(".source-preview.zip")
        bundle, check = compile_from_source_package(args.source_package.read_bytes())
        bundles, results = {name: bundle}, {name: check}
    elif args.json_archive and args.yaml_archive:
        bundles, results = compile_from_pair(args.json_archive, args.yaml_archive)
    else:
        archive = args.json_archive or args.yaml_archive
        source_format = "json" if args.json_archive else "yaml"
        bundles, results = compile_from_archive(archive, source_format)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, data in sorted(bundles.items()):
        (args.output_dir / f"{name}.scapng").write_bytes(data)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
