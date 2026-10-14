#!/usr/bin/env python3
"""Enrich six-STIG 0.4 study with independently lowerable research prototypes.

Reads the precise released 0.3 authoring ZIP and the existing signed-source-
paired study. Does not change source authoring, schemas, or scanner bundles.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import re
import shutil
import zipfile
import yaml
from research_04_self_contained_inline import (
    inline_variable, inline_object, lower_inline, metrics, analyze_chain,
)
from research_04_variable_census import fetch_oval

def measured(before, after):
    original, updated = metrics(before), metrics(after)
    return {
        "before": original, "after": updated,
        "line_delta": updated["lines"] - original["lines"],
        "byte_delta": updated["bytes"] - original["bytes"],
        "depth_delta": updated["max_nesting"] - original["max_nesting"],
    }

def dump_inline(path, doc, *, is_object=False):
    note = ("nested Object" if is_object else "inline Variable")
    path.write_text(
        "# Experimental 0.4 " + note +
        ": exact self-contained lowering to original 0.3 proven.\n"
        "# NOT adopted syntax; no scanner/OVAL runtime equivalence claimed.\n"
        + yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")

def run(zip_path, out, split_root):
    stats_path = out / "STATS.json"
    stats = json.loads(stats_path.read_text(encoding="utf-8"))
    with zipfile.ZipFile(zip_path) as z:
        def read_doc(relative):
            path = "authoring/" + relative
            return yaml.safe_load(z.read(path).decode("utf-8"))
        docs = {}
        def doc(relative):
            if relative not in docs:
                docs[relative] = read_doc(relative)
            return docs[relative]

        def read_csv(name):
            with (out / name).open(newline="", encoding="utf-8") as stream:
                return list(csv.DictReader(stream))
        vrows = read_csv("ALL-VARIABLES.csv")
        orows = read_csv("NAMED-OBJECTS.csv")
        outcomes = []
        chains = defaultdict(Counter)
        keys = set(r["benchmark"] for r in vrows + orows)
        scoped = defaultdict(set)
        for row in vrows + orows:
            scoped[row["benchmark"]].add(row["source_path"])
        for key, paths in scoped.items():
            for path in paths:
                chains[key].update(analyze_chain(doc(path)["assessment"]))

        for row in vrows:
            if row["disposition"] != "candidate_research":
                continue
            original = doc(row["source_path"])
            record = {k: row[k] for k in ("benchmark", "source_path", "assessment_id", "variable_id", "category")}
            record["kind"] = "variable"
            try:
                revised, proof = inline_variable(original, row["variable_id"])
                if lower_inline(revised) != original:
                    raise ValueError("roundtrip unequal")
                record.update(status="exact_structural_proof", **measured(original, revised))
            except ValueError as error:
                record.update(status="refused", reason=str(error))
            outcomes.append(record)
        for row in orows:
            if not row["category"].startswith("candidate_"):
                continue
            original = doc(row["source_path"])
            record = {k: row[k] for k in ("benchmark", "source_path", "assessment_id", "object_id", "category")}
            record["kind"] = "object"
            try:
                revised, proof = inline_object(original, row["object_id"])
                if lower_inline(revised) != original:
                    raise ValueError("roundtrip unequal")
                record.update(status="exact_structural_proof", **measured(original, revised))
            except ValueError as error:
                record.update(status="refused", reason=str(error))
            outcomes.append(record)

        # Add a self-contained proposal alongside each appropriate existing
        # original OVAL + released native pair.
        for entry in stats["examples"]:
            folder = out / entry["folder"]
            source = yaml.safe_load((folder / "current-0.3.assessment.yaml").read_text(encoding="utf-8"))
            if entry["category"].startswith("candidate_"):
                variable_line = next(
                    (line for line in (folder / "README.md").read_text().splitlines()
                     if line.startswith("Variable: ")), "")
                quoted_parts = variable_line.split(chr(96))
                if len(quoted_parts) >= 3:
                    try:
                        changed, info = inline_variable(source, quoted_parts[1])
                        if lower_inline(changed) != source:
                            raise ValueError("roundtrip unequal")
                        dump_inline(folder / "proposed-0.4.SELF-CONTAINED.RESEARCH.yaml", changed)
                        entry["self_contained_verified"] = True
                    except ValueError:
                        entry["self_contained_verified"] = False

        # Deliberately include a source-paired case for Object nesting, one in
        # RHEL9 and one in Oracle Linux 9; this is a *different* investigation
        # from the earlier 18 Variable examples.
        new_object_cases = 0
        for key in ("rhel_9", "oracle_linux_9"):
            options = [r for r in orows if r["benchmark"] == key and
                       r["category"] == "candidate_nested_foreach_source"]
            options.sort(key=lambda r:(r["source_path"],r["object_id"]))
            for item in options:
                original = doc(item["source_path"])
                try:
                    changed, _ = inline_object(original, item["object_id"])
                    if lower_inline(changed) != original:
                        continue
                except ValueError:
                    continue
                ids = json.loads(item["rule_ids"])
                if not ids:
                    continue
                rid = ids[0]
                folder = out / "examples" / key / (rid + "--nested-object-source")
                folder.mkdir(parents=True, exist_ok=True)
                with zipfile.ZipFile(zip_path) as source_zip:
                    (folder / "current-0.3.assessment.yaml").write_bytes(
                        source_zip.read("authoring/" + item["source_path"]))
                oval, provenance = fetch_oval(split_root, key, rid)
                shutil.copyfile(oval, folder / "original-1.4.oval.xml")
                dump_inline(folder / "proposed-0.4.SELF-CONTAINED.RESEARCH.yaml",
                            changed, is_object=True)
                (folder / "README.md").write_text(
                    "# " + rid + " — nested source Object\n\n"
                    + "OVAL complete source closure / unchanged 0.3 / experimental 0.4\n\n"
                    + "Object: " + item["object_id"] + "\n\n"
                    + "Exact independent 0.3 lowering verified; scanner runtime equivalence "
                      "and author readability are separate research gates.\n")
                stats["examples"].append(dict(
                    benchmark=key, rule_id=rid, category=item["category"],
                    folder=folder.relative_to(out).as_posix(),
                    proposed_sketch=False, self_contained_verified=True,
                    oval_sha256=provenance["sha256"]))
                new_object_cases += 1
                break

    with (out / "SELF-CONTAINED-PROOFS.csv").open("w", newline="", encoding="utf-8") as stream:
        fields=["benchmark","source_path","assessment_id","kind","variable_id","object_id",
                "category","status","reason","line_delta","byte_delta","depth_delta"]
        writer=csv.writer(stream)
        writer.writerow(fields)
        for row in outcomes:
            writer.writerow([row.get(k, "") for k in fields])
    passed=[r for r in outcomes if r["status"]=="exact_structural_proof"]
    rejected=[r for r in outcomes if r["status"]=="refused"]
    summary={
        "status":"research_syntax_only_not_runtime_parity",
        "source_release":stats["source_release"],
        "candidate_attempts":len(outcomes),
        "structural_proofs":len(passed),
        "refusals":len(rejected),
        "proofs_by_type":dict(Counter(r["kind"] for r in passed)),
        "refusals_by_reason":dict(Counter(r["reason"] for r in rejected)),
        "proofs_by_benchmark":dict(Counter(r["benchmark"] for r in passed)),
        "proofs_by_category":dict(Counter(r["category"] for r in passed)),
        "metric_deltas": {
            "sum_lines":sum(r["line_delta"] for r in passed),
            "sum_bytes":sum(r["byte_delta"] for r in passed),
            "median_line_delta":sorted(r["line_delta"] for r in passed)[len(passed)//2] if passed else None,
            "max_nesting_increase":max([r["depth_delta"] for r in passed] or [0]),
            "cases_with_more_lines":sum(r["line_delta"]>0 for r in passed),
            "cases_with_deeper_nesting":sum(r["depth_delta"]>0 for r in passed),
        },
        "chain_census_by_benchmark":{k:dict(v) for k,v in chains.items()},
        "object_source_examples":new_object_cases,
        "proved_only":"Independent exact structural 0.3 lowering, never OVAL/scanner execution",
    }
    (out / "SELF-CONTAINED-STATS.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    stats["examples"] = stats["examples"]
    stats["self_contained_study"] = summary
    stats_path.write_text(json.dumps(stats,indent=2,sort_keys=True)+"\n")
    readme=out/"README.md"
    with readme.open("a",encoding="utf-8") as stream:
        stream.write("\n## Self-contained authoring experiment\n\n")
        stream.write(
            f"- {len(passed)} exact independent structural relocation proofs "
            f"({summary['proofs_by_type'].get('variable',0)} Variables; "
            f"{summary['proofs_by_type'].get('object',0)} Objects); "
            f"{len(rejected)} refusals.\n")
        stream.write(
            f"- Total lines delta summed across individually attempted cases: "
            f"{summary['metric_deltas']['sum_lines']}; nested YAML depth increased "
            f"in {summary['metric_deltas']['cases_with_deeper_nesting']} cases.\n")
        stream.write(
            "- Full metrics: SELF-CONTAINED-PROOFS.csv and SELF-CONTAINED-STATS.json.\n"
            "- Unlike the older inline sketches, files named "
            "proposed-0.4.SELF-CONTAINED.RESEARCH.yaml carry complete local definitions "
            "and independently lower exactly into the released 0.3 source.\n"
            "- Original standalone OVAL files accompany the two new Object examples "
            "as well as the earlier Variable cases.\n"
            "- Structural exactness does NOT prove OVAL 5.12.3 result equivalence, "
            "runtime status/error propagation, or human readability superiority.\n")
    print(json.dumps(summary,indent=2,sort_keys=True))
    return summary

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--authoring-zip",type=Path,required=True)
    p.add_argument("--study",type=Path,required=True)
    p.add_argument("--split-root",type=Path,required=True)
    a=p.parse_args()
    run(a.authoring_zip,a.study,a.split_root)

if __name__=="__main__":
    main()
