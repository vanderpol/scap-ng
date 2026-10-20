#!/usr/bin/env python3
"""Refs #246: fully source-pinned 0.4-D seven-Test UNIX nested Set/Filter case.

An independent D Test requirement view over C's proven native typed OVAL Set
and literal-expectation bridge. Source IDs live in an explicit provenance
sidecar; original Sets/Filters are not reinterpreted. No scanner parity claim.
"""
from __future__ import annotations
import argparse
from copy import deepcopy
import json
from pathlib import Path
import yaml

from research_c_oval_hybrid_provenance import (
    present_oval_set_provenance,
    compile_oval_set_provenance,
    prove_oval_set_provenance,
    STAGE as C_STAGE,
)

D_STAGE = "D_RESEARCH_NATIVE_TEST_REQUIREMENTS_ORIGINAL_OVAL_SETS"
D_KEYS = {"stage", "assessment", "collections", "expected_values", "tests", "evaluate"}
# Only the actual original-source existential combinations are admitted.
# Source check=all for each of the seven Tests; no implicit quantifier.
SOURCE_PAIRS = {
    ("exactly_one", "every", True): "only_one_exists_and_matches",
    ("one_or_more", "every", True): "at_least_one_exists_and_all_match",
    ("none", "every", False): "none_exist",
}
INVERSE_PAIRS = {v: k for k, v in SOURCE_PAIRS.items()}


def _fail(message):
    raise ValueError("D original UNIX Set source contract: " + message)


def _tree(tree, forward, depth=0):
    if depth > 64 or not isinstance(tree, dict) or len(tree) != 1:
        _fail("criteria must be a bounded single-key expression")
    key, parts = next(iter(tree.items()))
    if key == ("check" if forward else "test"):
        if type(parts) is not str or not parts:
            _fail("empty Test identity")
        return {("test" if forward else "check"): parts}
    mapping = {"and": "all", "or": "any"} if forward else {
        "all": "and", "any": "or"}
    if key not in mapping or not isinstance(parts, list) or not parts:
        _fail("only source-backed all/any criteria supported")
    return {mapping[key]: [_tree(node, forward, depth + 1) for node in parts]}


def _to_d_test(check):
    if not isinstance(check, dict) or set(check) != {
        "description", "observation", "capability", "must"}:
        _fail("unexpected original Set check")
    must = check["must"]
    if not isinstance(must, dict) or set(must) not in (
        {"items_exist", "items_match"},
        {"items_exist", "items_match", "states"},
    ):
        _fail("unsupported original Test cardinality")
    states = must.get("states", [])
    if not isinstance(states, list) or len(set(states)) != len(states):
        _fail("source State list invalid")
    pair = (must["items_exist"], must["items_match"], bool(states))
    if pair not in SOURCE_PAIRS:
        _fail("original Test cardinality not proven for D")
    test = {
        "description": deepcopy(check["description"]),
        "collection": check["observation"],
        "capability": check["capability"],
        "require": SOURCE_PAIRS[pair],
    }
    if states:
        test["states"] = deepcopy(states)
        if len(states) > 1:
            # Preserve scope: original OVAL source family has <=1 State each.
            _fail("multi-State logical composition requires separate source proof")
    return test


def _from_d_test(test):
    if not isinstance(test, dict) or set(test) not in (
        {"description", "collection", "capability", "require"},
        {"description", "collection", "capability", "require", "states"},
    ):
        _fail("expected source Test fields are missing or ambiguous")
    token = test["require"]
    if token not in INVERSE_PAIRS:
        _fail("unsupported paired requirement")
    exist, match, has_states = INVERSE_PAIRS[token]
    states = test.get("states", [])
    if type(test["description"]) is not str or not test["description"].strip():
        _fail("required Test description missing")
    if type(test["collection"]) is not str or not test["collection"]:
        _fail("collection identity required")
    if type(test["capability"]) is not str or not test["capability"]:
        _fail("typed capability required")
    if not isinstance(states, list) or bool(states) != has_states:
        _fail("States/existence requirement mismatch")
    if len(states) > 1 or len(set(states)) != len(states):
        _fail("unsupported multiple/duplicate State references")
    must = {"items_exist": exist, "items_match": match}
    if states:
        must["states"] = deepcopy(states)
    return {
        "description": deepcopy(test["description"]),
        "observation": test["collection"],
        "capability": test["capability"],
        "must": must,
    }


def present_d_oval_sets(native):
    c, provenance = present_oval_set_provenance(native)
    checks = {alias: _to_d_test(test)
              for alias, test in c["checks"].items()}
    out = {
        "stage": D_STAGE,
        "assessment": deepcopy(c["assessment"]),
        "collections": deepcopy(c["observations"]),
        "expected_values": deepcopy(c["expected_values"]),
        "tests": checks,
        "evaluate": _tree(c["require"], True),
    }
    if len(checks) != 7 or len(out["collections"]) != 11:
        _fail("pinned original seven Tests / eleven Objects changed")
    return out, provenance


def _to_c(d):
    if not isinstance(d, dict) or set(d) != D_KEYS or d.get("stage") != D_STAGE:
        _fail("one complete D UNIX source Assessment required")
    if not isinstance(d["tests"], dict) or len(d["tests"]) != 7:
        _fail("all seven original Tests are required")
    if not isinstance(d["collections"], dict) or len(d["collections"]) != 11:
        _fail("all eleven original Objects, including seven Sets, required")
    if not isinstance(d["expected_values"], dict) or len(d["expected_values"]) != 4:
        _fail("all four State expectations required")
    checks = {name: _from_d_test(test) for name, test in d["tests"].items()}
    return {
        "stage": C_STAGE,
        "assessment": deepcopy(d["assessment"]),
        "observations": deepcopy(d["collections"]),
        "expected_values": deepcopy(d["expected_values"]),
        "checks": checks,
        "require": _tree(d["evaluate"], False),
    }


def compile_d_oval_sets(author, provenance):
    """From D authoring and pinned source bindings, reconstruct native source."""
    return compile_oval_set_provenance(_to_c(author), provenance)


def prove_d_oval_sets(original, author, provenance):
    reconstructed = compile_d_oval_sets(author, provenance)
    if reconstructed != original:
        _fail("OVAL Set/Filter/Variable/Test graph differs from original source")
    source_proof = prove_oval_set_provenance(original, _to_c(author), provenance)
    if not source_proof["exact_typed_OVAL_graph_reproduced"]:
        _fail("source graph proof not established")
    return {
        "native_source_graph_identical": True,
        "source_test_count": len(reconstructed["tests"]),
        "source_object_count": len(reconstructed["objects"]),
        "source_set_count": sum("set" in ob for ob in reconstructed["objects"].values()),
        "source_state_count": len(reconstructed["states"]),
        "source_variable_count": len(reconstructed["variables"]),
        "authored_constant_variable_declarations": 0,
        "runtime_oval_scanner_parity_proven": False,
        "normative_04a_schema_validated": False,
    }


def export_d_oval_sets(source, output):
    author, provenance = present_d_oval_sets(source)
    proof = prove_d_oval_sets(source, author, provenance)
    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)
    author_text = yaml.safe_dump(author, allow_unicode=True, sort_keys=False)
    provenance_text = yaml.safe_dump(provenance, allow_unicode=True, sort_keys=False)
    (out / "unix-set-seven-tests.0.4-D-author.yaml").write_text(
        "# 0.4-D lossless original OVAL 5.12.3 seven-Test Set/Filter research.\n"
        "# Source: OVAL-Community/SCAP-Self-Assertion@e3538595c5083b9c34d937a81d319234df9bbfaa\n"
        "# SCAP_1.4/OVAL_Test_Content/unix/oval-def_set-unix.xml:definition 276\n"
        + author_text, encoding="utf-8")
    (out / "unix-set-seven-tests.0.4-D-provenance.yaml").write_text(
        "# Managed provenance; not edited as normative authoring.\n"
        + provenance_text, encoding="utf-8")
    result = {**proof,
        "D_authored_lines": len(author_text.splitlines()),
        "D_authored_bytes": len(author_text.encode("utf-8")),
        "D_provenance_lines": len(provenance_text.splitlines()),
        "D_provenance_bytes": len(provenance_text.encode("utf-8")),
    }
    (out / "proof.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path,
                        help="One pinned native A-compatible JSON Assessment")
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    source = json.loads(args.source.read_text(encoding="utf-8"))
    print(json.dumps(export_d_oval_sets(source, args.out), sort_keys=True))
