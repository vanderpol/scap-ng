#!/usr/bin/env python3
"""Restore 11 proven shared Applicability Assessments omitted from pinned r3.

The October 15 research exporter selected shared Rule choices but omitted
shared Assessments reachable only through Applicability catalogs. Repair from
the immutable 0.3 source, preserving full source logic and verifying inverse
conversion. This is a *source archive repair*, not an executable compiler.

Refs #232 #239.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import zipfile

import yaml

from migrate_v04_enum_selectors import migrate, restore
from research_04_native_deep_content_census import SUPPORTED_MAPPING_DATA
from research_04_one_grammar_proof import (
    check_no_parallel_comparison_or_cardinality_grammar,
    lower_single, make_single, normalize_inert_source_checks,
)
from research_04_scoped_state_require import compact, expand
from test_v04_review_reference_graph import scan
from v04_a_authoring_graph_index import read_authoring_archive


PINS = {
    "historical_json": "a1837c03133021f4d13814516a91b372f83b03771519f8361398ff1663056fea",
    "historical_yaml": "03d64157ee295b81defe6f96cf7a3123410010ef4422d76bf5b7bb3ddbf30c9d",
    "original_03": "9b8d6e3528d52a7babc9d3fd0bdcad03664edfa9a754c65d49df5765f2b7473f",
}


def _logical(name):
    if name.endswith((".json", ".yaml")):
        return name.rsplit(".", 1)[0]
    raise ValueError("not a native authoring document: " + name)


def _missing(documents):
    _, problems = scan(documents)
    if not problems:
        raise ValueError("historical corpus no longer has the expected omissions")
    if any(len(row) != 4 or row[1] != "unresolved Applicability Assessment"
           for row in problems):
        raise ValueError("unexpected historical source graph defects: " + repr(problems[:8]))
    counts = Counter(row[3] for row in problems)
    # The original source contained 11 distinct Checks reused by two Linux
    # benchmarks. Do not tolerate a new missing link or a third occurrence.
    if len(problems) != 22 or len(counts) != 11 or any(n != 2 for n in counts.values()):
        raise ValueError("historical Applicability omission census changed: " + repr(counts))
    paths = {row[0] for row in problems}
    if paths != {"authoring/rhel_9/applicability.json",
                 "authoring/oracle_linux_9/applicability.json"}:
        raise ValueError("unexpected missing Applicability source paths: " + repr(paths))
    return set(counts)


def _restore_from_03(original):
    """Perform the same exact-inverse r3 conversion, without obsolete schema imports."""
    one, _, notes = make_single(original)
    check_no_parallel_comparison_or_cardinality_grammar(one)
    if lower_single(one) != normalize_inert_source_checks(original, notes):
        raise ValueError("original 0.3 Assessment one-grammar reconstruction failed")
    modern, migrations = migrate(one, SUPPORTED_MAPPING_DATA)
    if restore(modern, migrations) != one:
        raise ValueError("original 0.3 selector conversion is not invertible")
    scoped, _ = compact(modern)
    if expand(scoped) != modern:
        raise ValueError("original 0.3 scoped-field conversion is not invertible")
    spec = scoped["assessment"].get("specification")
    if not isinstance(spec, dict) or spec.get("version") != "0.3.0":
        raise ValueError("unexpected source specification version")
    spec["version"] = "0.4.0"
    for test in (scoped["assessment"].get("tests") or {}).values():
        if "collected_items_require" in test or "require" not in test:
            raise ValueError("unexpected historical Test requirement spelling")
        test["collected_items_require"] = test.pop("require")
    # Undo only the pinned r3 spelling/version edits, then prove the native
    # 0.3 representation recovers exactly. This is *not* a semantic guess.
    back = deepcopy(scoped)
    back["assessment"]["specification"]["version"] = "0.3.0"
    for test in (back["assessment"].get("tests") or {}).values():
        test["require"] = test.pop("collected_items_require")
    if expand(back) != modern:
        raise ValueError("recovered 0.4 preview did not preserve original source")
    return scoped


def restore_archive_pair(historical_json, historical_yaml, original_03,
                         out_json, out_yaml, *, check_pins=True):
    sources = {"historical_json": Path(historical_json),
               "historical_yaml": Path(historical_yaml),
               "original_03": Path(original_03)}
    digests = {name: sha256(path.read_bytes()).hexdigest()
               for name, path in sources.items()}
    if check_pins and digests != PINS:
        raise ValueError("original immutable source digest mismatch: " + repr(digests))

    jdocs = read_authoring_archive(historical_json, "json")
    ydocs = read_authoring_archive(historical_yaml, "yaml")
    if {_logical(p): doc for p, doc in jdocs.items()} != {
        _logical(p): doc for p, doc in ydocs.items()
    }:
        raise ValueError("pinned historical YAML/JSON sources differ before restoration")
    missing = _missing(jdocs)
    if missing != _missing({_logical(p) + ".json": doc for p, doc in ydocs.items()}):
        raise ValueError("historical missing-reference inventory differs by format")

    restored = {}
    provenance = {}
    with zipfile.ZipFile(original_03) as archive:
        if archive.testzip() is not None:
            raise ValueError("corrupt original 0.3 source ZIP")
        for path in archive.namelist():
            if not (path.startswith("authoring/shared/assessments/")
                    and path.endswith(".yaml")):
                continue
            raw = archive.read(path)
            doc = yaml.safe_load(raw)
            assessment = doc.get("assessment") if isinstance(doc, dict) else None
            ident = assessment.get("id") if isinstance(assessment, dict) else None
            if ident not in missing:
                continue
            if ident in restored:
                raise ValueError("ambiguous original shared Assessment ID: " + ident)
            converted = _restore_from_03(doc)
            if converted["assessment"]["id"] != ident:
                raise ValueError("shared Assessment ID changed during source restoration")
            restored[ident] = (path, converted)
            provenance[ident] = {"original_path": path, "sha256": sha256(raw).hexdigest(),
                                 "tests": len(converted["assessment"].get("tests") or {})}
    if set(restored) != missing:
        raise ValueError("pinned 0.3 source does not close historical omissions: "
                         + repr(sorted(missing - set(restored))))

    added_json = {path.removesuffix(".yaml") + ".json": {"assessment": data["assessment"]}
                  for path, data in restored.values()}
    added_yaml = {path: {"assessment": data["assessment"]}
                  for path, data in restored.values()}
    for kind, original_docs, additions in (
        ("json", jdocs, added_json), ("yaml", ydocs, added_yaml),
    ):
        if set(original_docs) & set(additions):
            raise ValueError("restoration overwrote original source")
        complete = {**original_docs, **additions}
        _, problems = scan(complete)
        if problems:
            raise ValueError("repaired source still has unresolved references: "
                             + repr(problems[:10]))
        dest = Path(out_json if kind == "json" else out_yaml)
        with zipfile.ZipFile(sources["historical_" + kind]) as old, zipfile.ZipFile(
            dest, "w", zipfile.ZIP_DEFLATED, compresslevel=8
        ) as new:
            if old.testzip() is not None:
                raise ValueError("corrupt pinned historical source ZIP")
            old_names = old.namelist()
            if len(old_names) != len(set(old_names)):
                raise ValueError("duplicate historical ZIP members")
            for name in sorted(set(old_names) | set(additions)):
                if name in additions:
                    body = (json.dumps(additions[name], ensure_ascii=False, indent=2) + "\n"
                            if kind == "json" else yaml.safe_dump(
                                additions[name], sort_keys=False, allow_unicode=True, width=112))
                    new.writestr(name, body.encode("utf-8"))
                else:
                    new.writestr(name, old.read(name))
        parsed_again = read_authoring_archive(dest, kind)
        if parsed_again != complete:
            raise ValueError("repaired archive failed independent native source roundtrip")
    if {_logical(p): doc for p, doc in read_authoring_archive(out_json, "json").items()} != {
        _logical(p): doc for p, doc in read_authoring_archive(out_yaml, "yaml").items()
    }:
        raise ValueError("restored YAML/JSON logical source graph mismatch")
    return {"status": "HISTORICAL_APPLICABILITY_SOURCE_RESTORED_NOT_COMPILED",
            "source_sha256": digests, "restored_assessments": len(restored),
            "resolved_links": 22, "documents": len(jdocs) + len(restored),
            "restored_tests": sum(item["tests"] for item in provenance.values()),
            "provenance": dict(sorted(provenance.items())),
            "output_sha256": {
                "json": sha256(Path(out_json).read_bytes()).hexdigest(),
                "yaml": sha256(Path(out_yaml).read_bytes()).hexdigest(),
            }}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--historical-json", required=True, type=Path)
    p.add_argument("--historical-yaml", required=True, type=Path)
    p.add_argument("--original-03", required=True, type=Path)
    p.add_argument("--out-json", required=True, type=Path)
    p.add_argument("--out-yaml", required=True, type=Path)
    p.add_argument("--report", required=True, type=Path)
    args = p.parse_args()
    result = restore_archive_pair(args.historical_json, args.historical_yaml,
                                  args.original_03, args.out_json, args.out_yaml)
    args.report.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                           encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "provenance"},
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
