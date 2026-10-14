#!/usr/bin/env python3
"""Generate a short evidence-backed 0.4 OVAL Board FYI packet, not a vote."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

LABELS={
    "rhel_9":"RHEL 9",
    "oracle_linux_9":"Oracle Linux 9",
    "ms_windows_11":"Windows 11",
    "ms_windows_server_2025":"Windows Server 2025",
    "ms_windows_server_dns":"Windows Server DNS",
    "apache_server_2-4_unix_server":"Apache 2.4 UNIX",
}
def make(study):
    s=json.loads((study/"STATS.json").read_text())
    p=json.loads((study/"SELF-CONTAINED-STATS.json").read_text())
    a=json.loads((study/"APACHE-DATAFLOW-PATTERNS.json").read_text())
    candidates=sum(x.get("candidate_research",0) for x in s["six_benchmark_use_counts"].values())
    retain=sum(x.get("retain",0) for x in s["six_benchmark_use_counts"].values())
    audit=sum(x.get("audit",0) for x in s["six_benchmark_use_counts"].values())
    rows=["# SCAP-NG 0.4 — improving complex derived data",
          "",
          "**OVAL Board research preview, NOT a vote or proposed change to the frozen 0.3 specification.**",
          "",
          "## Question",
          "",
          "How can authors understand a multi-step Variable calculation without needing to chase",
          "many separate references—and without turning the assessment into an opaque program?",
          "",
          "## Findings from six complete STIG conversions",
          "",
          "| STIG | Variable uses | Simplification candidates | Retain for now | Unreferenced audit |",
          "|---|---:|---:|---:|---:|"]
    for key, title in LABELS.items():
        c=s["six_benchmark_use_counts"][key]
        rows.append(f"| {title} | {c.get('variables',0)} | {c.get('candidate_research',0)} | {c.get('retain',0)} | {c.get('audit',0)} |")
    rows += [
        f"| **Total** | **{s['benchmark_usage_count']}** | **{candidates}** | **{retain}** | **{audit}** |",
        "",
        f"Shared Assessments deduplicate to **{s['unique_variable_definitions']} unique named Variables**.",
        f"Among **{s['named_object_benchmark_uses']} named Object uses**, only **14** are private nested-source candidates.",
        "",
        "### What exact compilation shows",
        "",
        f"- **{p['structural_proofs']}/{p['candidate_attempts']}** self-contained research forms independently lower to the **same parsed 0.3 Assessment structure**; this is **only a syntax/dataflow identity check**.",
        f"- **{p['metric_deltas']['cases_with_more_lines']}** of those forms increase YAML lines; **{p['metric_deltas']['cases_with_deeper_nesting']}** increase nesting depth.",
        f"- Combined delta over **separate** one-component-at-a-time proofs: **{p['metric_deltas']['sum_lines']:+d} YAML lines**, **{p['metric_deltas']['sum_bytes']:+d} bytes**. These deltas must NOT be extrapolated to a single simultaneous rewrite of every file.",
        "- Simply embedding full Objects or Variables is technically possible but often **harder to read**; fewer names is not the same as less complexity.",
        "",
        "### Apache is the most revealing case",
        "",
        f"- **{a['apache_assessments_with_variable_dataflow']}** Apache automated Assessments with Variable graphs and **{a['apache_variable_occurrences']}** Variable uses.",
        f"- **{a['apache_exact_named_payload_duplicate_groups']}** exact-named-definition repeat groups span **{a['apache_exact_named_payload_duplicate_occurrences']}** Variable occurrences.",
        f"- A stricter transitive comparison that includes referenced Variables **and source Objects** identifies **{a['apache_complete_closed_graph_duplicate_groups']}** repeated, complete dependency-graph groups across **{a['apache_complete_closed_graph_duplicate_occurrences']}** Variable occurrences; unresolved authoring dependencies: **{sum(a['apache_incomplete_closed_graph_reasons'].values())}**.",

        f"- **{a['apache_expression_duplicate_groups']}** repeated expression signatures spanning Assessments. Identical graphs suggest a reuse opportunity, **not** a proven shared runtime acquisition plan.",
        "- Earlier Apache Observation research separately proved **15 consumers** sharing an exact **4-Object + 11-Variable** discovery subgraph with two public outputs. Its runtime status/provenance contract is still deferred.",
        "",
        "## Approaches worth comparing (not all need a language change)",
        "",
        "| Approach | Benefit | Risk / implementation cost | Working priority |",
        "|---|---|---|---|",
        "| **Generated dependency map** from existing content | Authors see input → calculation → consumers; zero schema impact | Explain only; no source reduction | **First** |",
        "| **Build-time shared graph import** | Author discovery once; compiler expands the exact existing 0.3 graph per Assessment | Add explicit typed exports, acyclic namespaces, provenance and compiler validation; **no new runtime behavior** | **High priority to prototype** |",
        "| **Shared runtime producer / Observation** | Scanner may collect once and reuse typed evidence across Rules | Requires new artifact identity, scheduling, target scope, status/completeness, provenance and caching contract | **Separate future decision** |",
        "| **Small named transformation stages** | A linear left-to-right path may read more naturally than many independent Variables | Must preserve multi-value/cardinality and six-state status; no implicit map/flatten/cartesian | **Prototype only** |",
        "| **Bounded inline expressions** | Reduce boilerplate for single-source, single-consumer expressions | Full-metadata nesting currently adds YAML; readability unknown | **Selective** |",
        "| **Generic script / JSONata / CEL / jq engine** | Familiar concise functional operators | Silent changes to empty sequences, errors, correlation, control flow and scanner attack surface | **Do not adopt without independent semantics** |",
        "",
        "JSONata's function chaining is a good **presentation** idea; its sequence flattening is",
        "not automatically equivalent to OVAL's multi-valued Variable and error model.",
        "CEL's list operations also have their own error/Boolean rules; neither is a drop-in scanner evaluator.",
        "",
        "## Read original OVAL beside the alternatives",
        "",
        "Each linked example folder includes exact standalone SCAP 1.4 OVAL XML, current native",
        "0.3 YAML, and research 0.4 examples where appropriate. Some include a derived-value",
        "flow explanation that makes the original Variable dependency graph visible.",
        "",
        "| Family | Example / purpose | Evidence |",
        "|---|---|---|"]
    def find(k,rule_or_substr):
        return next((x for x in s["examples"] if x["benchmark"]==k and
                     (x["rule_id"]==rule_or_substr or rule_or_substr in x["category"])),None)
    examples=[
        ("rhel_9","SV-258020","dconf source/path derivation"),
        ("rhel_9","candidate_nested_foreach_source","private source Object"),
        ("oracle_linux_9","candidate_nested_foreach_source","nested source Object"),
        ("ms_windows_server_2025","SV-278043","multi-source event-log case **retained**"),
        ("ms_windows_server_dns","SV-259374","derived dynamic path"),
        ("apache_server_2-4_unix_server","SV-214228","long discovery/derived configuration path"),
        ("apache_server_2-4_unix_server","SV-214268","shared or chained dataflow **retained**"),
    ]
    for key,rid,label in examples:
        item=find(key,rid)
        if item:
            folder=item["folder"]
            rows.append(f"| {LABELS[key]} | {label} ({item['rule_id']}) | [{folder}]({folder}/README.md) |")
    rows += [
        "",
        "## Strict proof limits",
        "",
        "- No live OVAL engine comparison, six-state differential testing, or scanner collection/evidence verification was performed in this research.",
        "- The exact lowering proof is structural identity of parsed Assessment data, not proof that a proposed expression language has identical execution semantics.",
        "- Multi-source concatenations, correlated collection and OVAL empty/missing/error behavior remain explicit and untouched.",
        "- Reuse must not change acquisition order, independent status/completeness, input scope, evidence lineage or result signing.",
        "- **18 original Variable cases plus 2 new Object cases** are illustrative, not comprehensive coverage of every transformation family.",
        "",
        "## Provisional recommendation",
        "",
        "**Do not add universal Object nesting or a generic pipeline evaluator to 0.4 now.**",
        "First use generated, inspectable **value/dataflow views**.",
        "Next prototype a **source-only import** of reusable typed Objects/Variables that",
        "the compiler expands into each consuming Assessment's canonical 0.3 graph.",
        "Do not infer that shared authoring implies shared runtime collection or results.",
        "Explore a compact pipeline syntax only if representative real chains become",
        "meaningfully easier to read and lower exactly. Keep explicit Variables valid.",
        "",
        "## Board engagement",
        "",
        "This is suitable as an **informational research preview** after the owner reviews",
        "its examples; it is **not** a specification ratification request. A later",
        "proposal should contain a single precise grammar alternative, its lossless",
        "lowering rules, adversarial test fixtures and quantified benefits.",
        "",
        f"Reproduction: [issue #223](https://github.com/vanderpol/scap-ng/issues/223),",
        "source ZIP provenance and every classified Variable/Object in the other files of this archive.",
    ]
    (study/"BOARD-RESEARCH-PREVIEW.md").write_text("\n".join(rows)+"\n")
    return dict(preview="BOARD-RESEARCH-PREVIEW.md",variable_uses=s["benchmark_usage_count"],
                apache_repeated=a["apache_exact_named_payload_duplicate_groups"])

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--study",required=True,type=Path)
    args=ap.parse_args()
    print(json.dumps(make(args.study),indent=2))
if __name__=="__main__":main()
