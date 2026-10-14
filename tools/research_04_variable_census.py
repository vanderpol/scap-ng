#!/usr/bin/env python3
"""Research-only 0.4 census of the RELEASED six-STIG 0.3 authoring ZIP.

Counts unique assessment definitions and per-benchmark use separately.
When supplied split roots, pairs each selected native file with its complete
standalone original OVAL definition closure (not an edited XML excerpt).
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import copy
import csv
import hashlib
import json
from pathlib import Path
import re
import shutil
import zipfile

import yaml
from measure_post_modernization_variable_patterns import analyze_remaining_variables, exact_variable_refs

BENCHMARKS = {
    "rhel_9": "RHEL 9",
    "oracle_linux_9": "Oracle Linux 9",
    "ms_windows_11": "Windows 11",
    "ms_windows_server_2025": "Windows Server 2025",
    "ms_windows_server_dns": "Windows Server DNS",
    "apache_server_2-4_unix_server": "Apache UNIX Server",
}
PIN = "8c8e5dff860af6b1290ee9273a282db24278f8d5"
RELEASE = "v0.3.0-six-stig-typed-operators-5796d016b12f"
FAVORITES = {
    "rhel_9": ["SV-258013", "SV-258020", "SV-257889"],
    "oracle_linux_9": [],
    "ms_windows_11": [],
    "ms_windows_server_2025": ["SV-278043", "SV-278028"],
    "ms_windows_server_dns": ["SV-259350", "SV-259374"],
    "apache_server_2-4_unix_server": ["SV-214228", "SV-214268"],
}

def dynamic_sources(expression):
    """Distinct runtime data producers in an expression (not mere function calls)."""
    found = set()
    def walk(node):
        if isinstance(node, list):
            for child in node:
                walk(child)
        elif isinstance(node, dict):
            if isinstance(node.get("variable"), str):
                found.add(("variable", node["variable"]))
            if isinstance(node.get("object"), str):
                found.add(("object", node["object"]))
            if "object_values" in node:
                found.add(("object_values", repr(node["object_values"])))
            for child in node.values():
                walk(child)
    walk(expression)
    return found

def classify(v, original):
    if original.get("kind") == "external":
        return "retain_external_input"
    n = v["consumer_count"]
    contexts = v["consumer_contexts"]
    if n == 0:
        return "audit_unreferenced_provenance"
    if n > 1:
        return "retain_shared"
    if contexts.get("variable"):
        return "retain_chained"
    if v["compile_time_static"]:
        return "candidate_static_folding"
    if original.get("kind") != "local":
        return "retain_nonlocal"
    if contexts.get("object") == 1:
        expr = original.get("expression") or {}
        funcs = v["function_counts"]
        if v["kind"] == "direct_object_projection":
            return "candidate_projection"
        sources = dynamic_sources(expr)
        if funcs.get("concat") == 1 and len(funcs) <= 2:
            return ("candidate_unary_concat_review" if len(sources) == 1
                    else "retain_multi_source_concat")
        if len(funcs) <= 2 and len(sources) == 1:
            return "candidate_other_unary_review"
        return "retain_complex_object_input"
    if contexts.get("state") == 1:
        return "candidate_expected_value_review"
    return "retain_other_runtime"

def variable_rows(doc):
    a = doc["assessment"]
    analyzed = analyze_remaining_variables(a, {})
    vars = a.get("variables") or {}
    for row in analyzed["rows"]:
        v = vars[row["variable_id"]]
        row = {**row, "category": classify(row, v)}
        row["disposition"] = "candidate_research" if row["category"].startswith("candidate_") else ("audit" if row["category"].startswith("audit_") else "retain")
        yield row

def object_references(value, object_id, path=()):
    """Direct named Object references, including foreach source bindings."""
    if isinstance(value, list):
        for index, child in enumerate(value):
            yield from object_references(child, object_id, path + (str(index),))
    elif isinstance(value, dict):
        for key, child in value.items():
            if key == "object" and child == object_id:
                yield path + (key,)
            elif key == "in" and child == object_id and path and path[-1] == "for_each":
                yield path + (key,)
            else:
                yield from object_references(child, object_id, path + (key,))

def named_object_rows(doc):
    assessment = doc["assessment"]
    registry = {}
    for section in ("objects", "shared_objects"):
        for oid, payload in (assessment.get(section) or {}).items():
            if oid in registry:
                raise ValueError(f"Duplicate named Object: {oid}")
            registry[oid] = (section, payload)
    for oid, (section, payload) in sorted(registry.items()):
        refs = list(object_references(assessment, oid))
        if not refs:
            category = "audit_unreferenced_named_object"
        elif len(refs) > 1:
            category = "retain_shared_named_object"
        elif refs[0][0] == "variables":
            category = "candidate_variable_private_source_nesting"
        elif "for_each" in refs[0]:
            category = "candidate_nested_foreach_source"
        elif refs[0][0] in {"objects", "shared_objects"}:
            category = "candidate_nested_object_dependency"
        elif refs[0][0] == "tests":
            category = "already_test_locality_0_3"
        else:
            category = "retain_other_named_object"
        yield dict(object_id=oid, section=section, category=category,
                   consumer_count=len(refs), consumer_paths=[".".join(path) for path in refs])

def fetch_oval(split, key, rid):
    manifest = json.loads((split / key / "manifest.json").read_text())
    matches = [row for row in manifest["rules"]
               if row.get("path") and re.search(r"(?<![0-9])" + re.escape(rid) + r"(?![0-9])", row.get("rule_id", ""))]
    if len(matches) != 1:
        raise ValueError(f"OVAL split closure not unique for {key} {rid}: {len(matches)}")
    oval = split / key / matches[0]["path"]
    if not oval.is_file():
        raise ValueError(f"OVAL split closure absent: {oval}")
    if matches[0].get("status") not in {"split_valid", "schema_valid"}:
        raise ValueError(f"OVAL closure invalid for {rid}: {matches[0].get('status')}")
    if hashlib.sha256(oval.read_bytes()).hexdigest() != matches[0]["sha256"]:
        raise ValueError(f"OVAL split checksum failed: {oval}")
    return oval, matches[0]

def run(args):
    out = args.output
    out.mkdir(parents=True, exist_ok=True)
    work = out / "_source"
    with zipfile.ZipFile(args.authoring_zip) as z:
        if z.testzip() is not None:
            raise ValueError("Authoring ZIP failed CRC")
        names = [n for n in z.namelist() if n.startswith("authoring/") and n.endswith(".yaml")]
        if not names:
            raise ValueError("No source YAML under authoring/")
        for name in names:
            target = work / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(z.read(name))
    root = work / "authoring"
    all_docs = {}
    by_id = defaultdict(list)
    by_key_id = defaultdict(lambda: defaultdict(list))
    rules = defaultdict(list)
    for path in sorted(root.rglob("*.yaml")):
        rel = path.relative_to(root).as_posix()
        doc = yaml.safe_load(path.read_text())
        all_docs[rel] = doc
        parts = Path(rel).parts
        if "assessment" in doc:
            aid = doc["assessment"]["id"]
            if parts[0] == "shared":
                by_id[aid].append(rel)
            elif parts[0] in BENCHMARKS:
                by_key_id[parts[0]][aid].append(rel)
        elif "rule" in doc and parts[0] in BENCHMARKS:
            rules[parts[0]].append(doc["rule"])
    reachable = defaultdict(lambda: defaultdict(set))
    for key in BENCHMARKS:
        if not rules[key]:
            raise ValueError(f"No rules: {key}")
        for rule in rules[key]:
            for choice in (rule.get("assessment_choices") or {}).values():
                if not isinstance(choice, dict):
                    continue
                aid = choice.get("assessment")
                matches = by_key_id[key].get(aid, []) + by_id.get(aid, [])
                if len(matches) != 1:
                    raise ValueError(f"Ambiguous/missing {key} {rule['id']} -> {aid}: {matches}")
                reachable[key][matches[0]].add(rule["id"])
    rows = []
    object_rows = []
    summary = {}
    for key in BENCHMARKS:
        c = Counter()
        c["rules"] = len(rules[key])
        c["reachable_assessment_files"] = len(reachable[key])
        for rel, rids in reachable[key].items():
            a = all_docs[rel].get("assessment") or {}
            if a.get("mode") != "automated":
                continue
            c["automated_assessments"] += 1
            for item in variable_rows(all_docs[rel]):
                item.update(benchmark=key, source_path=rel, assessment_id=a["id"], rule_ids=sorted(rids))
                rows.append(item)
                c[item["category"]] += 1
                c[item["disposition"]] += 1
                c["variables"] += 1
            for item in named_object_rows(all_docs[rel]):
                item.update(benchmark=key, source_path=rel, assessment_id=a["id"], rule_ids=sorted(rids))
                object_rows.append(item)
                c["named_objects"] += 1
                c[item["category"]] += 1
        summary[key] = dict(c)
    unique = {(r["source_path"], r["variable_id"]): r for r in rows}
    unique_counts = dict(Counter(r["category"] for r in unique.values()))
    use_counts = dict(Counter(r["category"] for r in rows))
    unique_objects = {(r["source_path"], r["object_id"]): r for r in object_rows}
    object_counts = dict(Counter(r["category"] for r in object_rows))
    report = {
        "status": "research_only_candidates_not_proven",
        "source_release": RELEASE,
        "source_zip_sha256": hashlib.sha256(args.authoring_zip.read_bytes()).hexdigest(),
        "niwc_pin": PIN, "six_benchmark_use_counts": summary,
        "six_benchmark_category_counts": use_counts,
        "unique_variable_definitions": len(unique),
        "unique_category_counts": unique_counts,
        "benchmark_usage_count": len(rows),
        "named_object_benchmark_uses": len(object_rows),
        "named_object_unique_definitions": len(unique_objects),
        "named_object_category_counts": object_counts,
        "notes": [
            "A reused shared assessment contributes to each benchmark using it, but counts only once in unique definitions.",
            "A candidate is a research hypothesis, not proof of safe conversion.",
            "Full original OVAL closure is sourced from pinned NIWC content via the existing splitter.",
        ],
    }
    with (out / "ALL-VARIABLES.csv").open("w", newline="") as stream:
        fields = ["benchmark", "source_path", "assessment_id", "rule_ids", "variable_id",
                  "kind", "datatype", "consumer_count", "consumer_contexts",
                  "function_counts", "compile_time_static", "category", "disposition"]
        writer = csv.writer(stream)
        writer.writerow(fields)
        for item in sorted(rows, key=lambda r:(r["benchmark"],r["source_path"],r["variable_id"])):
            writer.writerow([json.dumps(item.get(f), sort_keys=True) if isinstance(item.get(f),(dict,list))
                             else item.get(f) for f in fields])

    with (out / "NAMED-OBJECTS.csv").open("w", newline="") as stream:
        fields = ["benchmark", "source_path", "assessment_id", "rule_ids",
                  "object_id", "section", "consumer_count", "consumer_paths", "category"]
        writer = csv.writer(stream)
        writer.writerow(fields)
        for item in sorted(object_rows, key=lambda r:(r["benchmark"],r["source_path"],r["object_id"])):
            writer.writerow([json.dumps(item.get(f), sort_keys=True) if isinstance(item.get(f),(dict,list))
                             else item.get(f) for f in fields])

    # Portfolio: in every STIG include one candidate and one retained example;
    # then add categories not yet represented, balancing benchmark coverage.
    chosen = []
    used = set()
    by_benchmark_selected = Counter()
    category_benchmark_selected = Counter()
    def rank(row):
        return (not any(r in FAVORITES[row["benchmark"]] for r in row["rule_ids"]),
                row["consumer_count"], row["source_path"])
    ordered = sorted(rows, key=rank)
    def take(row):
        chosen.append(row)
        used.add(row["source_path"])
        by_benchmark_selected[row["benchmark"]] += 1
        category_benchmark_selected[(row["benchmark"],row["category"])] += 1
    for key in BENCHMARKS:
        for disposition in ("candidate_research", "retain"):
            options = [r for r in ordered if r["benchmark"] == key and
                       r["disposition"] == disposition and r["source_path"] not in used]
            if options:
                take(options[0])
    for category in sorted({r["category"] for r in rows}):
        if len(chosen) >= args.max_examples: break
        if any(r["category"] == category for r in chosen): continue
        options = [r for r in rows if r["category"] == category and r["source_path"] not in used]
        options.sort(key=lambda r:(by_benchmark_selected[r["benchmark"]], rank(r)))
        if options and by_benchmark_selected[options[0]["benchmark"]] < 4:
            take(options[0])
    # Fill remaining spots with diverse examples, avoiding four near-identical
    # Apache concat samples when other platforms or mechanisms are available.
    while len(chosen) < args.max_examples:
        options = [r for r in rows if r["source_path"] not in used and
                   by_benchmark_selected[r["benchmark"]] < 4]
        if not options:
            break
        options.sort(key=lambda r:(
            by_benchmark_selected[r["benchmark"]],
            category_benchmark_selected[(r["benchmark"],r["category"])],
            sum(x["category"] == r["category"] for x in chosen),
            rank(r)))
        take(options[0])
    cases = []
    for item in chosen:
        key = item["benchmark"]
        rids = item["rule_ids"]
        rid = next((r for r in FAVORITES[key] if r in rids), rids[0])
        folder = out / "examples" / key / (rid + "--" + item["category"])
        folder.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / item["source_path"], folder / "current-0.3.assessment.yaml")
        oval, provenance = fetch_oval(args.split_root, key, rid)
        shutil.copyfile(oval, folder / "original-1.4.oval.xml")
        doc = copy.deepcopy(all_docs[item["source_path"]])
        variables = doc["assessment"].get("variables") or {}
        target = variables.get(item["variable_id"])
        uses = list(exact_variable_refs({k:v for k,v in doc["assessment"].items() if k != "variables"}, item["variable_id"]))
        proposal = False
        if item["disposition"] == "candidate_research" and len(uses) == 1 and target:
            path = uses[0]
            parent = doc["assessment"]
            for p in path[:-1]:
                parent = parent[int(p)] if isinstance(parent, list) else parent[p]
            last = int(path[-1]) if isinstance(parent, list) else path[-1]
            if parent[last] == {"variable": item["variable_id"]}:
                parent[last] = {"expression": copy.deepcopy(target.get("expression")),
                                "research_inline_source_variable": item["variable_id"]}
                variables.pop(item["variable_id"])
                if not variables:
                    doc["assessment"].pop("variables", None)
                (folder / "proposed-0.4.RESEARCH.yaml").write_text(
                    "# NOT a valid 0.3 or approved 0.4 file; this is speculative authoring sugar.\n"
                    + yaml.safe_dump(doc, sort_keys=False))
                proposal = True
        (folder / "README.md").write_text(
            f"# {rid} — {item['category']}\n\n"
            + f"Benchmark: {BENCHMARKS[key]}\n\n"
            + f"Variable: `{item['variable_id']}` ({item['consumer_count']} consumer references)\n\n"
            + f"Released assessment source: `{item['source_path']}`\n\n"
            + f"Associated Rule IDs: {', '.join(rids)}\n\n"
            + "- `original-1.4.oval.xml`: verbatim standalone OVAL closure generated from pinned NIWC SCAP 1.4.\n"
            + "- `current-0.3.assessment.yaml`: exact released authoring Assessment.\n"
            + ("- `proposed-0.4.RESEARCH.yaml`: complete but **non-normative** hypothetical inline form.\n" if proposal else
               "- No proposed rewrite: this is a deliberate retained/complex counterexample.\n")
            + "\nNo runtime semantic or OVAL equivalence claim is made by this research sketch.\n")
        cases.append(dict(benchmark=key, rule_id=rid, category=item["category"],
                          folder=folder.relative_to(out).as_posix(), proposed_sketch=proposal,
                          oval_sha256=provenance["sha256"]))
    report["examples"] = cases
    (out / "STATS.json").write_text(json.dumps(report, sort_keys=True, indent=2) + "\n")
    lines = ["# SCAP-NG 0.4: Variable and nested-Object research", "",
             "**Research only. 0.3 normative source and release assets are unchanged.**", "",
             f"Measured [the released six-STIG authoring archive](https://github.com/vanderpol/scap-ng/releases/tag/{RELEASE})",
             f"against pinned NIWC source revision `{PIN}`.", "",
             "### Six STIG variable classifications", "",
             "| STIG | Variable uses | Candidate research | Retain named | Unreferenced audit |",
             "|---|---:|---:|---:|---:|"]
    for key, title in BENCHMARKS.items():
        c = summary[key]
        lines.append(f"| {title} | {c.get('variables',0)} | {c.get('candidate_research',0)} | {c.get('retain',0)} | {c.get('audit',0)} |")
    lines += ["",
              f"Total benchmark-variable uses: **{len(rows)}** (candidates: **{sum(r['disposition']=='candidate_research' for r in rows)}**, retain: **{sum(r['disposition']=='retain' for r in rows)}**, unreferenced audit: **{sum(r['disposition']=='audit' for r in rows)}**).",
              f"Unique Variable definitions across all six (deduplicate shared Assessments): **{len(unique)}**.",
              "",
              "Breakdown by reason is in `STATS.json`; every classified Variable is in `ALL-VARIABLES.csv`.",
              f"Named Objects: **{len(object_rows)} benchmark uses**, **{len(unique_objects)} unique definitions**, including **{sum(v for k,v in object_counts.items() if k.startswith('candidate_'))} private-source nesting research candidates**.",
              "See `NAMED-OBJECTS.csv` for the direct references and disposition of each named Object.",
              "A candidate is not a promise of equivalence or a proposal to remove every surviving Variable.",
              "", "### Side-by-side original and proposed examples", "",
              "| Rule | Pattern | Directory |", "|---|---|---|"]
    for c in cases:
        lines.append(f"| {BENCHMARKS[c['benchmark']]} {c['rule_id']} | {c['category']} | [{c['folder']}]({c['folder']}/README.md) |")
    lines += ["", "Every directory contains **original-1.4.oval.xml** directly beside **current-0.3.assessment.yaml**.",
              "The optional `proposed-0.4.RESEARCH.yaml` is deliberately not a schema-valid 0.3 Assessment.",
              "Source OVAL includes each Rule's full referenced Definitions/Tests/Objects/States/Variables.",
              "For shared native Assessments the original OVAL is the representative Rule closure, not a claim of one-to-one file identity.", ""]
    (out / "README.md").write_text("\n".join(lines))
    shutil.rmtree(work)
    print("CENSUS_STATS_BEGIN")
    print(json.dumps({"by_benchmark": summary, "unique_variables": len(unique),
                      "variable_uses": len(rows), "named_object_uses": len(object_rows),
                      "named_object_categories": object_counts, "examples": cases}, sort_keys=True))
    print("CENSUS_STATS_END")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--authoring-zip", type=Path, required=True)
    parser.add_argument("--split-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-examples", type=int, default=18)
    run(parser.parse_args())

if __name__ == "__main__":
    main()
