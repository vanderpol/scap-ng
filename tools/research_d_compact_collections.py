#!/usr/bin/env python3
"""Refs #246: 0.4-D authoring-only removal of redundant typed leaf selectors.

A narrow, exact-source UNIX OVAL 5.12.3 Set/Filter pilot:
- source Object titles/identity remain in a required managed sidecar,
- select.path's proven literal string equals has no redundant operation/type,
- select.filename's source-specific nil remains explicit,
- identical nested Set subtrees become compiler-expanded source references.
Native Object/Set/Filter/State/Test/Variable AST is exactly reconstructed.
Not a general unix.file syntax approval or a scanner parity claim.
"""
from __future__ import annotations
from copy import deepcopy
import argparse
import json
from pathlib import Path
import yaml

from research_d_set_factoring import (
    present_factored_sets, compile_factored_sets, prove_factored_sets,
    _count_reuse, STAGE as FACTORED_STAGE)

STAGE = "D_RESEARCH_SOURCE_COMPAT_COMPACT_UNIX_SET_COLLECTIONS"
SIDECAR_STAGE = "D_RESEARCH_TYPED_SET_SELECTION_METADATA_BOUND"
AUTHOR_KEYS = {"stage", "assessment", "collections", "expected_values",
               "tests", "evaluate"}
SIDECAR_KEYS = {"stage", "source_provenance", "object_titles"}


def _fail(message):
    raise ValueError("D compact UNIX Set authoring: " + message)


def _compact_leaf(selection):
    if not isinstance(selection, dict) or set(selection) != {"path", "filename"}:
        _fail("only original two-field UNIX filename/path selector supported")
    path, filename = selection["path"], selection["filename"]
    if (not isinstance(path, dict) or set(path) != {
            "datatype", "operation", "value"} or
        path["datatype"] != "string" or path["operation"] != "equals" or
        type(path["value"]) is not str or
        not isinstance(filename, dict) or set(filename) != {
            "datatype", "nil", "operation", "value"} or
        filename != {"datatype": "string", "nil": True,
                     "operation": "equals", "value": ""}):
        _fail("unproven typed filename/path selector; retain native A")
    return {"path": path["value"], "filename": {"nil": True}}


def _restore_leaf(selection):
    if not isinstance(selection, dict) or set(selection) != {
            "path", "filename"} or type(selection["path"]) is not str or (
            selection["filename"] != {"nil": True}):
        _fail("original literal path and explicit filename:nil are mandatory")
    return {
        "filename": {
            "datatype": "string", "nil": True,
            "operation": "equals", "value": "",
        },
        "path": {
            "datatype": "string", "operation": "equals",
            "value": selection["path"],
        },
    }


def present_compact_collections(source):
    factored, c_provenance, reuse_count = present_factored_sets(source)
    author = deepcopy(factored)
    author["stage"] = STAGE
    titles = {}
    counts = {"compact_literal_path_selectors": 0, "exact_set_reuses": reuse_count}
    for alias, ob in author["collections"].items():
        if not isinstance(ob, dict) or (
                set(ob) not in (
                    {"capability", "object_title", "select", "behaviors"},
                    {"capability", "object_title", "set"})):
            _fail("source Object shape does not match pilot")
        if ob["capability"] != "unix.file":
            _fail("not an OVAL unix.file Object")
        title = ob.pop("object_title")
        if type(title) is not str or not title.strip():
            _fail("source description missing")
        titles[alias] = title
        if "select" in ob:
            ob["select"] = _compact_leaf(ob["select"])
            counts["compact_literal_path_selectors"] += 1
    if counts["compact_literal_path_selectors"] != 4 or len(titles) != 11:
        _fail("source selection and Object population changed")
    sidecar = {"stage": SIDECAR_STAGE,
               "source_provenance": deepcopy(c_provenance),
               "object_titles": titles}
    return author, sidecar, counts


def compile_compact_collections(author, sidecar):
    if not isinstance(author, dict) or set(author) != AUTHOR_KEYS or (
            author["stage"] != STAGE):
        _fail("complete compact D authoring required")
    if not isinstance(sidecar, dict) or set(sidecar) != SIDECAR_KEYS or (
            sidecar["stage"] != SIDECAR_STAGE):
        _fail("complete managed source description/provenance required")
    titles = sidecar["object_titles"]
    cols = author["collections"]
    if not isinstance(titles, dict) or not isinstance(cols, dict) or (
            set(titles) != set(cols)):
        _fail("every named source Object needs a unique managed description")
    rebuilt = deepcopy(author)
    rebuilt["stage"] = FACTORED_STAGE
    for alias, ob in rebuilt["collections"].items():
        if type(titles[alias]) is not str or not titles[alias].strip():
            _fail("empty or invalid source title")
        if "object_title" in ob or "capability" not in ob:
            _fail("redundant or missing managed Object fields")
        ob["object_title"] = titles[alias]
        if "select" in ob:
            if ob["capability"] != "unix.file":
                _fail("unsupported shorthand capability")
            ob["select"] = _restore_leaf(ob["select"])
    return compile_factored_sets(rebuilt, sidecar["source_provenance"])


def prove_compact_collections(source, author, sidecar):
    result = compile_compact_collections(author, sidecar)
    if result != source:
        _fail("compact D Assessment has diverged from original OVAL source")
    factored = deepcopy(author)
    factored["stage"] = FACTORED_STAGE
    for alias, ob in factored["collections"].items():
        ob["object_title"] = sidecar["object_titles"][alias]
        if "select" in ob:
            ob["select"] = _restore_leaf(ob["select"])
    complete = prove_factored_sets(
        source, factored, sidecar["source_provenance"])
    return {**complete,
            "managed_source_object_titles": len(sidecar["object_titles"]),
            "authored_redundant_source_titles": 0,
            "short_literal_unix_file_selectors": sum(
                "select" in x for x in author["collections"].values())}


def export_compact_collections(source, out):
    author, sidecar, counts = present_compact_collections(source)
    proof = prove_compact_collections(source, author, sidecar)
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    core = yaml.safe_dump(author, sort_keys=False, allow_unicode=True)
    managed = yaml.safe_dump(sidecar, sort_keys=False, allow_unicode=True)
    (out / "unix-set-seven-tests.0.4-D-compact-author.yaml").write_text(
        "# 0.4-D source-preserving compact authoring, original OVAL Set #276.\n"
        "# Immutable conversion metadata is kept separately from editable logic.\n"
        + core, encoding="utf-8")
    (out / "unix-set-seven-tests.0.4-D-compact-provenance.yaml").write_text(
        "# Required managed original source titles, OVAL IDs and value bindings.\n"
        + managed, encoding="utf-8")
    report = {**proof, **counts,
        "compact_editable_lines": len(core.splitlines()),
        "compact_editable_bytes": len(core.encode("utf-8")),
        "managed_lines": len(managed.splitlines()),
        "managed_bytes": len(managed.encode("utf-8"))}
    (out / "compact-proof.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    source = json.loads(args.source.read_text(encoding="utf-8"))
    print(json.dumps(export_compact_collections(source, args.out), indent=2))
