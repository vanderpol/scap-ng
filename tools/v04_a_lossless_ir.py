#!/usr/bin/env python3
"""#240 / #232: lossless, non-executable 0.4-A research compiler envelope.

A typed *index* over full canonical base-authoring ASTs, not a replacement
language or an interpreter. No Test result, OVAL six-state truth, collection,
or signed .scapng semantics are inferred. A validator-accepted extension is
retained in the complete AST; a broken identity/reference fails closed.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath

from v04_a_authoring_graph_index import canonical_json, graph_index
from v04_a_benchmark_choice_version_closure import inspect_edges
from v04_a_dataflow_index import index_assessment_dataflow

IR_FORMAT = "scap-ng-0.4-a-lossless-source-envelope/0.2"
IR_STATUS = "RESEARCH_NOT_EXECUTABLE"


def _source_name(name):
    """Normalize source-format spelling, without discarding its logical path."""
    if not isinstance(name, str) or not name.startswith("authoring/"):
        raise ValueError(f"unsafe or unsupported authoring path: {name!r}")
    parts = PurePosixPath(name).parts
    if any(part in (".", "..", "") for part in parts) or len(parts) < 3:
        raise ValueError(f"unsafe authoring path: {name!r}")
    for suffix in (".json", ".yaml", ".yml"):
        if name.endswith(suffix):
            return name[:-len(suffix)] + ".json"
    raise ValueError(f"unsupported authoring filename: {name!r}")


def _collection_ref_hints(test):
    """Index source references only; these are NOT executable dependencies.

    In particular a Test-level Variable reference cannot be silently
    promoted to an Assessment-level truth dependency.
    """
    found = []

    def walk(value, path):
        if isinstance(value, dict):
            for key, child in sorted(value.items()):
                current = path + [key]
                if key == "variable" and isinstance(child, str):
                    found.append({"type": "variable", "path": current, "target": child})
                walk(child, current)
        elif isinstance(value, list):
            for i, child in enumerate(value):
                walk(child, path + [i])

    if isinstance(test.get("object"), str):
        found.append({"type": "shared_object", "path": ["object"],
                      "target": test["object"]})
    walk(test, [])
    return found


def _check_assessment_dependency_targets(documents):
    """Resolve truth-dependency targets without running or changing them.

    Collection/Variable references are intentionally excluded; this is a
    separate Assessment dependency graph with exact declared versions.
    """
    sources = {
        doc["assessment"]["id"]: (path, doc["assessment"])
        for path, doc in documents.items() if "assessment" in doc
    }
    links = {}
    for path, doc in sorted(documents.items()):
        assessment = doc.get("assessment")
        if not isinstance(assessment, dict):
            continue
        source_id = assessment["id"]
        declared = assessment.get("dependencies", {})
        if not isinstance(declared, dict):
            raise ValueError(f"{path}: invalid Assessment dependency mapping")
        links[source_id] = []
        for alias, dep in sorted(declared.items()):
            if not isinstance(alias, str) or not alias or not isinstance(dep, dict):
                raise ValueError(f"{path}: malformed Assessment dependency {alias!r}")
            target_id = dep.get("assessment")
            target = sources.get(target_id) if isinstance(target_id, str) else None
            if target is None:
                raise ValueError(f"{path}: unresolved Assessment dependency {alias}: {target_id!r}")
            target_path, target_assessment = target
            if dep.get("expected_id", target_id) != target_id:
                raise ValueError(f"{path}: Assessment dependency {alias} expected_id mismatch")
            if (type(dep.get("expected_version")) is not type(target_assessment.get("version"))
                    or dep.get("expected_version") != target_assessment.get("version")):
                raise ValueError(f"{path}: Assessment dependency {alias} version mismatch")
            # Usage belongs to the consumer's typed invocation, not the target
            # Assessment. No intrinsic purpose is inferred from class or mode.
            from_folder = PurePosixPath(path).parts[1]
            to_folder = PurePosixPath(target_path).parts[1]
            if to_folder not in ("shared", from_folder):
                raise ValueError(f"{path}: cross-Benchmark private Assessment dependency {alias}")
            links[source_id].append(target_id)

    # Assessment-truth references form a directed graph; cycles are unsafe to
    # schedule even though this source-preservation stage never executes them.
    done, visiting = set(), set()
    for start in links:
        if start in done:
            continue
        stack = [(start, False)]
        while stack:
            node, leaving = stack.pop()
            if leaving:
                visiting.remove(node)
                done.add(node)
                continue
            if node in done:
                continue
            if node in visiting:
                raise ValueError(f"cyclic Assessment dependency through {node}")
            visiting.add(node)
            stack.append((node, True))
            for target in reversed(links[node]):
                stack.append((target, False))
    return sum(map(len, links.values()))


def normalize_documents(documents):
    """Build deterministic lossless envelopes from validated *base* documents.

    This operation checks the complete reference graph and per-Benchmark
    Rule choice closure. Strict 0.4 base/capability schema validation is done
    by the independently maintained pipeline, and again by the CLI's archive
    entrypoint. Do not pass unvalidated authoring to claim semantic validity.
    """
    if not isinstance(documents, dict) or not documents:
        raise ValueError("no base-authoring documents")
    canonical = {}
    for original, document in documents.items():
        path = _source_name(original)
        if path in canonical:
            raise ValueError(f"duplicate normalized authoring path: {path}")
        canonical[path] = document
    graph = graph_index(canonical)
    edges = inspect_edges(canonical)
    if edges["incompatible_edge_count"]:
        raise ValueError("mixed Benchmark/Assessment specification versions")
    _check_assessment_dependency_targets(canonical)

    entries = []
    tests_total = 0
    automated = 0
    for path, document in sorted(canonical.items()):
        kind, body = next(iter(document.items()))
        entry = {
            "kind": kind,
            "id": body["id"],
            "source_path": path,
            "source_sha256": sha256(canonical_json(document)).hexdigest(),
            "source_ast": document,
        }
        if kind == "assessment":
            mode = body.get("mode")
            if mode not in ("manual", "automated"):
                raise ValueError(f"{path}: unknown Assessment mode")
            index = {"mode": mode, "assessment_dependencies": [],
                     "tests": []}
            deps = body.get("dependencies") or {}
            if not isinstance(deps, dict):
                raise ValueError(f"{path}: dependencies must be a mapping")
            for alias, dep in sorted(deps.items()):
                if not isinstance(dep, dict) or not isinstance(dep.get("assessment"), str):
                    raise ValueError(f"{path}: invalid Assessment dependency {alias!r}")
                index["assessment_dependencies"].append({
                    "alias": alias, "target": dep["assessment"],
                    "expected_version": dep.get("expected_version"),
                    "purpose": dep.get("purpose"),
                })
            if mode == "automated":
                automated += 1
                spec = body.get("specification")
                if (not isinstance(spec, dict) or not isinstance(spec.get("id"), str)
                        or not isinstance(spec.get("version"), str)):
                    raise ValueError(f"{path}: missing explicit specification id/version")
                tests = body.get("tests")
                if not isinstance(tests, dict) or not tests:
                    raise ValueError(f"{path}: no named automated Tests")
                if "evaluate" not in body:
                    raise ValueError(f"{path}: missing evaluate expression")
                index["specification"] = spec
                index["source_dataflow"] = index_assessment_dataflow(body)
                for name, test in sorted(tests.items()):
                    if not isinstance(test, dict):
                        raise ValueError(f"{path}: invalid Test {name!r}")
                    capability = test.get("capability")
                    requirement = test.get("require")
                    if not isinstance(capability, str) or not capability:
                        raise ValueError(f"{path}: Test {name} lacks capability")
                    if not isinstance(requirement, str) or not requirement:
                        raise ValueError(f"{path}: Test {name} lacks explicit Item require")
                    if ("collected_items_require" in test
                            or "state_fields_require" in test):
                        raise ValueError(f"{path}: Test {name} retains scoped-only grammar")
                    index["tests"].append({
                        "id": name, "capability": capability,
                        "item_requirement": requirement,
                        "source_sha256": sha256(canonical_json(test)).hexdigest(),
                        "collection_reference_hints": _collection_ref_hints(test),
                    })
                    tests_total += 1
            entry["assessment_index"] = index
        entries.append(entry)
    return {
        "format": IR_FORMAT,
        "status": IR_STATUS,
        "source_graph_sha256": graph["graph_sha256"],
        "version_inventory": graph["version_inventory"],
        "document_count": len(entries),
        "automated_assessment_count": automated,
        "automated_test_count": tests_total,
        "rule_choice_link_count": edges["counts"]["choice_links"],
        "documents": entries,
        "not_proven": [
            "runtime Test/State/Variable or collection evaluation",
            "unknown/error/not_applicable six-state equivalence",
            "scanner execution, signatures or executable bundle packaging",
            "owner approval of scoped shorthand and version migration",
        ],
    }


def decode_and_verify(ir):
    """Independently rederive every index and hash; no lossy reverse mapping."""
    if not isinstance(ir, dict) or ir.get("format") != IR_FORMAT or ir.get("status") != IR_STATUS:
        raise ValueError("unexpected or executable-looking research IR")
    entries = ir.get("documents")
    if not isinstance(entries, list) or not entries:
        raise ValueError("missing IR documents")
    docs = {}
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("invalid IR envelope")
        path = entry.get("source_path")
        if not isinstance(path, str) or _source_name(path) != path or path in docs:
            raise ValueError("duplicate or uncanonical IR source path")
        doc = entry.get("source_ast")
        if not isinstance(doc, dict):
            raise ValueError(f"{path}: missing full source AST")
        if sha256(canonical_json(doc)).hexdigest() != entry.get("source_sha256"):
            raise ValueError(f"{path}: source AST digest mismatch")
        docs[path] = doc
    expected = normalize_documents(docs)
    if canonical_json(ir) != canonical_json(expected):
        raise ValueError("IR typed index, order, identity, or version checksum mismatch")
    return docs


def _validated_from_base_archive(path):
    """Import only independently verified research ZIPs, never a signed bundle."""
    from v04_a_deterministic_research_container import verify_research_container
    from v04_a_end_to_end_base_authoring import (
        _extract_docs, validate_native_capability_tests,
    )
    from validate_native_json_schemas import build_validators
    raw = Path(path).read_bytes()
    verified = verify_research_container(raw)
    docs, _ = _extract_docs(raw)
    if verified["member_count"] != len(docs):
        raise ValueError("verified archive document count differs")
    root = Path(__file__).resolve().parents[1]
    schema = build_validators(root / "schema/v0.4.0")["assessment.schema.json"]
    for source, doc in sorted(docs.items()):
        assessment = doc.get("assessment")
        if isinstance(assessment, dict) and assessment.get("mode") == "automated":
            errors = list(schema.iter_errors(doc))
            if errors:
                err = sorted(errors, key=lambda e: (list(map(str, e.absolute_path)),
                                                    e.message))[0]
                raise ValueError(f"{source}: invalid base Assessment: {err.message}")
    validate_native_capability_tests(docs)
    return docs


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-zip", type=Path, required=True,
                        help="independently verified 0.4-A unsigned base authoring research ZIP")
    parser.add_argument("--out", type=Path, required=True,
                        help="canonical lossless typed research envelope JSON")
    parser.add_argument("--assert-six", action="store_true")
    args = parser.parse_args(argv)
    ir = normalize_documents(_validated_from_base_archive(args.base_zip))
    decoded = decode_and_verify(ir)
    from jsonschema import Draft202012Validator
    schema_path = (Path(__file__).resolve().parents[1] /
                   "research/assessment-simplification/compact-authoring-04/"
                   "lossless-ir-envelope.schema.json")
    research_schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(research_schema)
    Draft202012Validator(research_schema).validate(ir)
    if args.assert_six and (
        ir["document_count"] != 4001 or
        ir["automated_assessment_count"] != 872 or
        ir["automated_test_count"] != 1375 or
        ir["rule_choice_link_count"] != 2958
    ):
        raise ValueError("pinned six-STIG IR totals differ")
    data = canonical_json(ir) + b"\n"
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(data)
    print(json.dumps({
        "status": ir["status"], "format": ir["format"],
        "source_graph_sha256": ir["source_graph_sha256"],
        "ir_sha256": sha256(data).hexdigest(),
        "document_count": len(decoded),
        "automated_assessments": ir["automated_assessment_count"],
        "automated_tests": ir["automated_test_count"],
        "rule_choice_links": ir["rule_choice_link_count"],
        "roundtrip": "PASS",
        "source_dataflow_edges": sum(r.get("assessment_index", {}).get(
            "source_dataflow", {}).get("edge_count", 0) for r in ir["documents"]),
        "source_dataflow_sites": sum(len(r.get("assessment_index", {}).get(
            "source_dataflow", {}).get("sites", [])) for r in ir["documents"]),
        "assessment_truth_dependencies": sum(len(r.get("assessment_index", {}).get(
            "assessment_dependencies", [])) for r in ir["documents"]),
        "research_ir_schema": "PASS",
        "scanner_executable": False,
    }, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
