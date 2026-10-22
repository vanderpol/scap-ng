#!/usr/bin/env python3
"""Compile canonical 0.4.0 Assessments into manifest-linked .scapng packages.

This is the 0.4 native equivalent of the 0.2/0.3 content compiler: a
deterministic, manifest-authoritative content graph with separately compiled
Test dispatch and six-state result programs. The Test programs preserve exact
0.4 source operands; collection and live scanner execution are NOT claimed.

Inputs may be a previously verified 0.4 source-preview ZIP (fast development)
or independently parsed YAML and JSON canonical authoring archives (release).
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

from v04_a_authoring_graph_index import canonical_json, graph_index
from v04_a_benchmark_choice_version_closure import inspect_edges
from v04_canonical_result_plan import compile_canonical_result_plan
from v04_canonical_source_ir import (
    compile_pair, decode_and_verify, validate_docs,
)
from v04_canonical_unsigned_package import (
    _manifest_schema, _package_validators, _strict_json,
    _verify_exact_rule_inventory, _write_member, partition_documents,
    verify_package as verify_source_package,
)
from v04_field_requirement import validate_test


FORMAT_VERSION = "0.4.0"
PROGRAM_FORMAT = "scap-ng-0.4.0-native-assessment-program/0.1"
STAGE = "compiled-native-0.4.0-program-not-scanner-validated/0.1"
MANIFEST_MEMBER = "META-INF/manifest.json"
DOCUMENT_KINDS = {"benchmark": "benchmark", "rule": "rule",
                  "assessment": "assessment", "applicability": "applicability_catalog"}
REQUIREMENT_SHAPES = {"one_or_more", "none", "exactly_one", "all", "may_be_absent"}


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
    """Emit a typed Test dispatch instruction without erasing uncommon OVAL checks.

    The two accepted structured requirement shapes have explicit native opcodes.
    A legacy source-exact check has its own opcode and full State operands, not
    a guessed equivalent of all_items_must. Scanner support is a separate gate.
    """
    if not isinstance(test_id, str) or not isinstance(test, dict):
        raise ValueError("invalid Test instruction")
    validate_test(test)
    if not isinstance(test.get("capability"), str) or not test["capability"]:
        raise ValueError(f"Test {test_id}: missing collector capability")
    if "collected_items_require" in test:
        raise ValueError("legacy collected_items_require is not canonical 0.4")
    if isinstance(test.get("object"), dict) and "capability" in test["object"]:
        raise ValueError("inline Object capability is redundant in 0.4")
    requirement = test.get("require")
    if isinstance(requirement, dict):
        items = requirement.get("items")
        if items not in REQUIREMENT_SHAPES:
            raise ValueError(f"Test {test_id}: unsupported Items requirement")
        if set(requirement) == {"items"}:
            if "states" in test or "states_match" in test:
                raise ValueError(f"Test {test_id}: presence-only Test has States")
            opcode = "CHECK_COLLECTION_PRESENCE"
        elif (set(requirement) <= {"items", "all_items_must", "field_requirement"}
              and "all_items_must" in requirement
              and items in {"one_or_more", "may_be_absent"}
              and isinstance(requirement["all_items_must"], list)
              and requirement["all_items_must"]
              and "states" not in test):
            opcode = "CHECK_EACH_ITEM_REQUIREMENT"
        else:
            raise ValueError(f"Test {test_id}: ambiguous canonical Items requirement")
    elif (isinstance(requirement, str) and requirement
          and isinstance(test.get("states"), list) and test["states"]):
        # The original check/existence/State boundaries remain explicit; no
        # blanket conversion to ALL, OR or an invented result default.
        opcode = "CHECK_SOURCE_EXACT_STATES"
    else:
        raise ValueError(f"Test {test_id}: unsupported Test requirement")
    return {
        "opcode": opcode,
        "test_id": test_id,
        "capability": test["capability"],
        "source_test_sha256": sha256(canonical_json(test)).hexdigest(),
        "operands": deepcopy(test),
    }


def compile_assessment_program(assessment):
    if not isinstance(assessment, dict) or assessment.get("mode") != "automated":
        raise ValueError("native program requires automated Assessment")
    tests = assessment.get("tests") or {}
    if not isinstance(tests, dict):
        raise ValueError("invalid Assessment Tests")
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


def compile_from_pair(json_zip, yaml_zip, *, validate_schema=True):
    """Release path: independently parse both serializations before emission."""
    ir_bytes, validation = compile_pair(json_zip, yaml_zip, validate_schema=validate_schema)
    if validation["version_conflicting_choice_links"]:
        raise ValueError("native authoring versions are incompatible")
    docs = decode_and_verify(_strict_json(ir_bytes))
    partitions = partition_documents(docs)
    bundles, results = {}, {}
    for folder, subset in sorted(partitions.items()):
        archive, _ = build_bundle(subset, validate_schema=False)
        bundles[folder] = archive
        results[folder] = verify_bundle(archive, validate_schema=validate_schema)
    return bundles, results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--source-package", type=Path)
    group.add_argument("--json-archive", type=Path)
    parser.add_argument("--yaml-archive", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    if args.source_package:
        if args.yaml_archive:
            parser.error("--yaml-archive cannot accompany --source-package")
        name = args.source_package.name.removesuffix(".source-preview.zip")
        bundle, check = compile_from_source_package(args.source_package.read_bytes())
        bundles, results = {name: bundle}, {name: check}
    else:
        if not args.yaml_archive:
            parser.error("--json-archive requires --yaml-archive")
        bundles, results = compile_from_pair(args.json_archive, args.yaml_archive)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, data in sorted(bundles.items()):
        (args.output_dir / f"{name}.scapng").write_bytes(data)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
