#!/usr/bin/env python3
"""Refs #245. General original-OVAL fixed-State-value C authoring probe.

This is a research authoring projection over the *existing* typed A source
graph, NOT a native C full-Definition conversion or scanner-result proof.
Only a single-consumer string constant can move into the editable author
surface. Every other Variable (including dynamic collection inputs and
derived runtime steps) remains in the explicitly typed compatibility graph.
The independent compiler receives authored values + a source-identity sidecar,
never the original Assessment at compile time.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import re
from hashlib import sha256

from research_c_source_identity_contract import source_digest

STAGE = "C_RESEARCH_SOURCE_FIXED_STATE_EXPECTATIONS"
SENTINEL = "c_inline_expected"
CHECKS = {"all", "at least one", "only one", "none satisfy"}
OPS = {"equals", "pattern match"}
ALIAS = re.compile(r"expected_[a-z0-9_]{1,60}\Z")


def _paths(value, vid, path=()):
    if isinstance(value, dict):
        if value == {"variable": vid}:
            yield path
        for key, member in value.items():
            yield from _paths(member, vid, path + (key,))
    elif isinstance(value, list):
        for i, member in enumerate(value):
            yield from _paths(member, vid, path + (i,))


def _at(graph, path):
    node = graph
    for segment in path:
        node = node[segment]
    return node


def present_fixed_state_expectations(original):
    """Return an author value surface and reversible source compatibility data.

    Only one consumer, known State value location, type and explicit
    variable_check qualify. No constants feeding collectors or DAG nodes.
    """
    if not isinstance(original, dict) or original.get("mode") != "automated":
        raise ValueError("source must be an automated typed Assessment")
    vars_ = original.get("variables", {})
    if not isinstance(vars_, dict) or not vars_:
        raise ValueError("typed source Variables required")
    graph = deepcopy(original)
    author = {"stage": STAGE, "expected_values": {}}
    bindings = {}
    outside = {k: v for k, v in original.items() if k != "variables"}
    used_aliases = set()
    for vid, var in sorted(vars_.items()):
        if (not isinstance(var, dict) or
            var.get("kind") != "constant" or var.get("datatype") != "string" or
            not isinstance(var.get("expression"), dict) or
            set(var["expression"]) != {"literal"}):
            continue
        value = var["expression"]["literal"]
        if not (type(value) is str or isinstance(value, list) and
                1 <= len(value) <= 256 and
                all(type(item) is str for item in value)):
            continue
        if isinstance(value, list) and any(len(x) > 4096 for x in value):
            continue
        if type(value) is str and len(value) > 4096:
            continue
        usages = list(_paths(outside, vid))
        dependencies = list(_paths(vars_, vid))
        if dependencies or len(usages) != 1:
            continue
        path = usages[0]
        if (len(path) < 4 or path[0] != "states" or
            path[-1] != "value"):
            continue
        entity = _at(original, path[:-1])
        if (not isinstance(entity, dict) or
            entity.get("datatype") != "string" or
            entity.get("operation") not in OPS or
            entity.get("variable_check") not in CHECKS or
            entity.get("field") is None):
            continue
        field = entity["field"]
        if type(field) is not str:
            continue
        base = "expected_" + re.sub(r"[^a-z0-9_]+", "_", field.lower()).strip("_")
        if not ALIAS.fullmatch(base):
            continue
        alias = base
        n = 2
        while alias in used_aliases:
            alias = f"{base[:55]}_{n}"
            n += 1
            if not ALIAS.fullmatch(alias):
                raise ValueError("duplicate expected field cannot be named")
        used_aliases.add(alias)
        author["expected_values"][alias] = {
            "field": field, "operation": entity["operation"],
            "value_match": entity["variable_check"],
            "value": deepcopy(value),
        }
        bindings[alias] = {
            "source_variable_id": vid, "source_variable": deepcopy(var),
            "path": list(path), "source_field": field,
            "source_operation": entity["operation"],
            "source_value_match": entity["variable_check"],
        }
        _at(graph, path[:-1])["value"] = {SENTINEL: alias}
        graph["variables"].pop(vid)
    if not bindings:
        raise ValueError("no source-proven single-consumer State constants")
    sidecar = {
        "stage": STAGE, "source_sha256": source_digest(original),
        "source_graph_without_inlined_constants": graph,
        "bindings": bindings,
    }
    return author, sidecar


def compile_fixed_state_expectations(author, sidecar):
    if (not isinstance(author, dict) or set(author) != {"stage", "expected_values"}
        or author["stage"] != STAGE or not isinstance(sidecar, dict)
        or set(sidecar) != {
            "stage", "source_sha256",
            "source_graph_without_inlined_constants", "bindings"}
        or sidecar["stage"] != STAGE):
        raise ValueError("unrecognized C fixed expected-value source contract")
    expected, bindings = author["expected_values"], sidecar["bindings"]
    if (not isinstance(expected, dict) or not isinstance(bindings, dict)
        or not 1 <= len(expected) <= 256 or set(expected) != set(bindings)):
        raise ValueError("missing/extra expected value or source binding")
    result = deepcopy(sidecar["source_graph_without_inlined_constants"])
    if not isinstance(result.get("variables"), dict):
        raise ValueError("untrusted source Variables graph")
    seen_ids = set(result["variables"])
    seen_paths = set()
    for alias, entry in expected.items():
        binding = bindings[alias]
        if (type(alias) is not str or not ALIAS.fullmatch(alias) or
            not isinstance(entry, dict) or
            set(entry) != {"field", "operation", "value_match", "value"} or
            not isinstance(binding, dict) or
            set(binding) != {"source_variable_id", "source_variable",
                             "path", "source_field", "source_operation",
                             "source_value_match"}):
            raise ValueError("unrecognized fixed expectation or source binding")
        vid, var, path = (binding["source_variable_id"],
                          binding["source_variable"], binding["path"])
        if (type(vid) is not str or not vid or vid in seen_ids or
            not isinstance(path, list) or len(path) < 4 or
            path[0] != "states" or path[-1] != "value"):
            raise ValueError("duplicate or invalid source Variable identity")
        key = tuple(path)
        if key in seen_paths:
            raise ValueError("two authored values share one source entity")
        seen_ids.add(vid)
        seen_paths.add(key)
        field, operation, mode = (binding["source_field"],
                                   binding["source_operation"],
                                   binding["source_value_match"])
        if (entry["field"], entry["operation"], entry["value_match"]) != (
                field, operation, mode):
            raise ValueError("source field/operator/value_match changed")
        value = entry["value"]
        if not (type(value) is str and len(value) <= 4096 or
                isinstance(value, list) and 1 <= len(value) <= 256 and
                all(type(v) is str and len(v) <= 4096 for v in value)):
            raise ValueError("invalid source-typed constant or cardinality")
        if (var.get("kind") != "constant" or
            var.get("datatype") != "string" or
            not isinstance(var.get("expression"), dict) or
            set(var["expression"]) != {"literal"}):
            raise ValueError("original Variable source semantics not pinned")
        try:
            entity = _at(result, path[:-1])
        except (KeyError, IndexError, TypeError) as exc:
            raise ValueError("original State entity reference missing") from exc
        if (entity.get("value") != {SENTINEL: alias} or
            entity.get("field") != field or
            entity.get("operation") != operation or
            entity.get("variable_check") != mode or
            entity.get("datatype") != "string"):
            raise ValueError("source State context was modified or rebound")
        var = deepcopy(var)
        var["expression"]["literal"] = deepcopy(value)
        result["variables"][vid] = var
        entity["value"] = {"variable": vid}
    return result


def prove_fixed_state_source(original, author, sidecar):
    rebuilt = compile_fixed_state_expectations(author, sidecar)
    if (rebuilt != original or source_digest(rebuilt) != sidecar["source_sha256"]):
        raise ValueError("C authoring changed original source typed graph")
    return {"recreated_complete_typed_A_graph": True,
            "inlined_source_constants": len(author["expected_values"]),
            "OVAL_scanner_parity_proven": False,
            "full_native_C_compilation_proven": False}


def census(review_dir, manifest, *, examples_dir=None):
    m = manifest
    if m.get("stage") != "SOURCE_BACKED_NATIVE_C_SUBSET_NOT_SCANNER_PARITY":
        raise ValueError("expected verified native C disposition manifest")
    target = {(r["file"], r["definition_id"]) for r in m["unsupported"]
              if r["reason"].startswith("VARIABLE_SOURCE_GRAPH_NEEDS_COMPATIBILITY")}
    sources = {}
    for path in Path(review_dir).glob("*.review.json"):
        row = json.loads(path.read_text(encoding="utf-8"))
        key = (row.get("source", {}).get("file"),
               row.get("source", {}).get("definition_id"))
        if key in target:
            if key in sources:
                raise ValueError("duplicate source-Definition identity")
            sources[key] = row["A_source_compatibility_fallback"]
    if set(sources) != target:
        raise ValueError("original Variable-blocked source review incomplete")
    proof_rows = []
    if examples_dir is not None:
        examples_dir = Path(examples_dir)
        examples_dir.mkdir(parents=True, exist_ok=True)
    for key, source in sorted(sources.items()):
        try:
            author, sidecar = present_fixed_state_expectations(source)
        except ValueError as exc:
            if str(exc) != "no source-proven single-consumer State constants":
                raise
            continue
        proof = prove_fixed_state_source(source, author, sidecar)
        row={"source_file": key[0], "definition_id": key[1],
             "inlined_constants": proof["inlined_source_constants"]}
        if examples_dir is not None:
            import yaml
            basename=sha256((key[0]+"|"+key[1]).encode("utf-8")).hexdigest()[:24]
            author_file=basename+".author.research.yaml"
            sidecar_file=basename+".source-provenance.research.json"
            # Authoring is purpose-oriented; source IDs and complete A graph
            # reside in the mandatory provenance file, never in the editable
            # expected-value declarations.
            note=("# 0.4-C research only; NOT a full native C Assessment or scanner result.\n"
                  +"# Original OVAL: "+key[0]+"\n"
                  +"# Definition: "+key[1]+"\n")
            (examples_dir/author_file).write_text(
                note+yaml.safe_dump(author,sort_keys=False,allow_unicode=True),
                encoding="utf-8")
            (examples_dir/sidecar_file).write_text(
                json.dumps(sidecar,sort_keys=True,indent=2)+"\n",encoding="utf-8")
            # Actually reload the emitted files, not just in-memory copies.
            loaded_author=yaml.safe_load((examples_dir/author_file).read_text(
                encoding="utf-8"))
            loaded_sidecar=json.loads((examples_dir/sidecar_file).read_text(
                encoding="utf-8"))
            if compile_fixed_state_expectations(loaded_author,loaded_sidecar)!=source:
                raise ValueError("serialized C/provenance source graph drift")
            row.update({"author_file":author_file,"sidecar_file":sidecar_file,
                        "source_sha256":sidecar["source_sha256"]})
        proof_rows.append(row)
    if examples_dir is not None:
        (examples_dir/"index.json").write_text(
            json.dumps({"stage":STAGE,"source_definitions":proof_rows,
                        "scanner_parity_proven":False,
                        "full_native_C_compilation_proven":False},
                       sort_keys=True,indent=2)+"\n",encoding="utf-8")
    return {
        "variable_blocked_definitions": len(target),
        "hybrid_source_graph_proven_definitions": len(proof_rows),
        "moved_constant_variables": sum(r["inlined_constants"] for r in proof_rows),
        "still_native_C_converted_definitions": m["native_C_Definitions"],
        "scanner_parity_proven": False, "full_native_C_compilation_proven": False,
        "examples": proof_rows,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--review", type=Path, required=True)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--examples-dir", type=Path)
    args = p.parse_args()
    summary = census(args.review,
                     json.loads(args.manifest.read_text(encoding="utf-8")),
                     examples_dir=args.examples_dir)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2, sort_keys=True)+"\n",
                        encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k != "examples"},
                     sort_keys=True))


if __name__ == "__main__":
    main()
