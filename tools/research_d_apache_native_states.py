#!/usr/bin/env python3
"""Refs #246 — 0.4-D Apache lossless authoring experiment.

Keep A-like test and field requirements paired, preserving State boundaries
and states_match: all. Reuse only C's proven provenance/derived-value bridge.
No changes to A schemas, converters, scanner or normative vocabulary.
This is a source-scoped Apache SV-214268 study, not a generic D compiler.
"""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import argparse
import json
import yaml

from research_c_apache_provenance_split import (
    present_apache_provenance_split, compile_apache_split)

D_STAGE = "D_RESEARCH_APACHE_NATIVE_STATE_GROUPS_LOSSLESS"
D_KEYS = {"stage", "assessment", "observations", "derived_values", "checks", "require"}
# Restrict this first native projection to source-proven Apache combinations;
# a compiler may not silently invent a field/existence default.
ITEM_TO_D = {("one_or_more", "every"): "at_least_one_exists_and_all_match"}
FIELD_TO_D = {
    ("optional", "every"): "may_be_absent_and_all_match",
    ("one_or_more", "every"): "at_least_one_exists_and_all_match",
    ("one_or_more", "some"): "at_least_one_exists_and_some_match",
}
ITEM_FROM_D = {v: k for k, v in ITEM_TO_D.items()}
FIELD_FROM_D = {v: k for k, v in FIELD_TO_D.items()}
OPS = {"matches_regex", "equals"}


def _fail(message):
    raise ValueError("0.4-D Apache source-bound pilot: " + message)


def _native_check_to_d(check):
    if not isinstance(check, dict) or set(check) != {"description", "from", "must"}:
        _fail("unexpected C source check")
    must = check["must"]
    if not isinstance(must, dict) or set(must) not in (
        {"items_exist", "items_match", "fields"},
        {"items_exist", "items_match", "fields", "fields_join"},
    ):
        _fail("unsupported source requirement shape")
    pair = (must["items_exist"], must["items_match"])
    if pair not in ITEM_TO_D:
        _fail("unproven Test existence and matching combination")
    fields = must["fields"]
    if not isinstance(fields, list) or not 1 <= len(fields) <= 64:
        _fail("one or more field predicates required")
    if len(fields) > 1 and (must.get("fields_join") != "and"):
        _fail("source multiple-State join is not proven all")
    if len(fields) == 1 and "fields_join" in must:
        _fail("singleton join should not be present")
    result = {
        "description": deepcopy(check["description"]),
        "from": deepcopy(check["from"]),
        "require": ITEM_TO_D[pair],
        "states": [],
    }
    for field in fields:
        if not isinstance(field, dict) or set(field) not in (
            {"field", "exists", "matches", "matches_regex"},
            {"field", "exists", "matches", "equals"},
        ):
            _fail("unsupported source State predicate")
        pair = (field["exists"], field["matches"])
        if pair not in FIELD_TO_D:
            _fail("unsupported State existence and matching combination")
        name = field["field"]
        op = "matches_regex" if "matches_regex" in field else "equals"
        if not isinstance(name, str) or not name:
            _fail("empty source field identity")
        result["states"].append({
            name: {"require": FIELD_TO_D[pair], op: deepcopy(field[op])}
        })
    if len(fields) > 1:
        result["states_match"] = "all"
    return result


def _d_check_to_native(check):
    if not isinstance(check, dict) or set(check) not in (
        {"description", "from", "require", "states"},
        {"description", "from", "require", "states", "states_match"},
    ):
        _fail("expected description/from/require/states and optional states_match")
    if check["require"] not in ITEM_FROM_D:
        _fail("unsupported Test requirement; no silent cardinality fallback")
    states = check["states"]
    if not isinstance(states, list) or not 1 <= len(states) <= 64:
        _fail("source States must be nonempty")
    if len(states) > 1 and check.get("states_match") != "all":
        _fail("two or more States must explicitly match all on same Item")
    if len(states) == 1 and "states_match" in check:
        _fail("single State has no states_match in this source fixture")
    items_exist, items_match = ITEM_FROM_D[check["require"]]
    fields = []
    for state in states:
        if not isinstance(state, dict) or len(state) != 1:
            _fail("one field name per State, no implicit field grouping")
        name, predicate = next(iter(state.items()))
        if not isinstance(name, str) or not name or not isinstance(predicate, dict):
            _fail("State field and predicate required")
        if set(predicate) not in ({"require", "matches_regex"}, {"require", "equals"}):
            _fail("require and one supported comparison required per State")
        if predicate["require"] not in FIELD_FROM_D:
            _fail("unsupported State requirement; no hidden existence default")
        op = "matches_regex" if "matches_regex" in predicate else "equals"
        ex, ma = FIELD_FROM_D[predicate["require"]]
        if not isinstance(predicate[op], str):
            _fail("Apache shellcommand State comparator must be string")
        fields.append({
            "field": name, "exists": ex, "matches": ma,
            op: deepcopy(predicate[op]),
        })
    must = {"items_exist": items_exist, "items_match": items_match, "fields": fields}
    if len(fields) > 1:
        must["fields_join"] = "and"
    return {
        "description": deepcopy(check["description"]),
        "from": deepcopy(check["from"]),
        "must": must,
    }


def present_d_apache(original_assessment):
    """For presentation only, convert the pinned existing source to D."""
    c_author, sidecar = present_apache_provenance_split(original_assessment)
    d_author = deepcopy(c_author)
    d_author["stage"] = D_STAGE
    d_author["checks"] = {
        key: _native_check_to_d(check)
        for key, check in c_author["checks"].items()
    }
    return d_author, sidecar


def compile_d_apache(author, sidecar, *, require_original_source=True):
    """Compile D input through existing pinned C/A source-compatible bridge.

    The original source Assessment is NOT an input to this compiler.
    Source equality uses the sidecar's original C authoring digest and
    original Variables / shared-Object digests. Explicit edit mode can
    change content but never claims parity with original source.
    """
    if not isinstance(author, dict) or set(author) != D_KEYS or (
        author.get("stage") != D_STAGE
    ):
        _fail("one complete D Apache authoring document required")
    if not isinstance(author["checks"], dict) or len(author["checks"]) != 5:
        _fail("exactly five original Apache Tests required")
    c_author = deepcopy(author)
    c_author["stage"] = "C_RESEARCH_APACHE_AUTHORING_WITH_REQUIRED_PROVENANCE_SIDECAR"
    c_author["checks"] = {
        key: _d_check_to_native(check)
        for key, check in author["checks"].items()
    }
    return compile_apache_split(
        c_author, sidecar, require_original_source=require_original_source)


def source_fixture():
    path = (Path(__file__).resolve().parents[1] /
        "research/requirements-first-language/contract-candidate/corpus/" /
        "source-specimens/independent-shellcommand-1-3d964d126ca8.source.yaml")
    return yaml.safe_load(path.read_text(encoding="utf-8"))["assessment"]


def export_review(outdir):
    source = source_fixture()
    author, sidecar = present_d_apache(source)
    native = compile_d_apache(
        yaml.safe_load(yaml.safe_dump(author)),
        yaml.safe_load(yaml.safe_dump(sidecar)))
    if native != source:
        _fail("D reconstructed native Assessment differs from source")
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    author_text = yaml.safe_dump(author, sort_keys=False, allow_unicode=True)
    provenance_text = yaml.safe_dump(sidecar, sort_keys=False, allow_unicode=True)
    (out / "apache-sv214268.0.4-D-author.yaml").write_text(
        "# 0.4-D lossless Apache authoring prototype; research only.\n"
        "# Source-equivalent reconstruction of all 5 Tests and 19 Variables.\n"
        + author_text, encoding="utf-8")
    (out / "apache-sv214268.0.4-D-provenance.yaml").write_text(
        "# Required conversion-side provenance; not author-edited.\n"
        + provenance_text, encoding="utf-8")
    metrics = {
        "source_id": source["id"],
        "tests": len(native["tests"]),
        "variables": len(native["variables"]),
        "shared_objects": len(native["shared_objects"]),
        "d_author_lines": len(author_text.splitlines()),
        "d_author_bytes": len(author_text.encode("utf-8")),
        "provenance_lines": len(provenance_text.splitlines()),
        "provenance_bytes": len(provenance_text.encode("utf-8")),
        "original_source_structural_equality": True,
        "source_scanner_runtime_parity": False,
        "a_schema_modified": False,
        "scope": "pinned Apache SV-214268; no generalized compiler claim",
    }
    (out / "proof.json").write_text(
        json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return metrics


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    print(json.dumps(export_review(args.out), indent=2, sort_keys=True))
