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
    source=json.loads((study/"BUILD-TIME-IMPORT/RESULTS.json").read_text())
    debugging=json.loads((study/"VARIABLE-DEBUG-STATS.json").read_text())
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
        "- Earlier legacy-layout Apache research found a four-Object/11-Variable graph. The **published 0.3 release localizes the source Objects**; do not revive that old layout in a proposed standard.",
        "",
        "### New build-time compilation proof using published 0.3 content",
        "",
        f"- **{source['safe_exact_roundtrip_consumers']} of {source['identical_graph_candidates']}** Apache Assessment consumers independently expand a single **{source['module_variables']}-Variable source module** back to exactly the same parsed 0.3 assessment; **{len(source['refusals'])} rejected**.",
        f"- This replaces **{source['original_named_definitions_across_consumers']}** duplicated declarations with **{source['authoring_definitions_with_import_module']}** shared declarations plus explicit imports—a research reduction of **{source['duplicate_declarations_eliminated_from_authoring']}** duplicate Variable declarations.",
        f"- Public typed outputs: **{', '.join(source['public_exports'])}**. Required Object sources remain local to each Assessment: **{', '.join(source['required_assessment_local_object_sources']) or 'none'}**.",
        "- Every sample in `BUILD-TIME-IMPORT/consumer-samples/` includes the complete original standalone OVAL XML, released 0.3 YAML, research import, and expanded 0.3 YAML.",
        "- **Compiler-only sharing does not share scan results or collected Items**, and it adds no runtime status/evidence mechanism.",
        "",
        "### Make complex Variable chains diagnosable",
        "",
        f"- The study generated **{debugging['paired_diagnostic_plans']}** static diagnostic stage plans covering **{debugging['paired_stage_occurrences']}** stage occurrences; no scanner was run.",
        "- Each plan records the ordered Variable DAG, operations, inputs, consumer checks, datatypes, and risky multi-source or regex transformations.",
        "- A future scanner MAY offer optional, bounded **per-stage debugging**: input/output counts, status/completeness/error, source lineage and redacted samples. Keep ordinary assessment results small.",
        "- Trace details must **never** change scan truth, infer completion from a sample, or leak sensitive values.",
        "",
        "## Approaches worth comparing (not all need a language change)",
        "",
        "| Approach | Benefit | Risk / implementation cost | Working priority |",
        "|---|---|---|---|",
        "| **Generated dependency map + optional Variable trace** | Explain input → stage → consumer; surface first incomplete/error stage | Scan-time diagnostics need privacy, result contract and capped evidence | **First; separate normative trace later** |",
        "| **Build-time shared graph import** | Proven on 15 Apache 0.3 Assessments; exact compiler expansion and typed outputs | Need general namespace/import-cycle/schema contract and independent content-validation gating | **Best scoped 0.4 candidate** |",
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
        "A concrete Apache source-only import now compiles **15/15** Assessments",
        "back to the exact same parsed 0.3 content; develop its general namespace,",
        "dependency, typing, validation and import-cycle contract before normative use.",
        "Do not infer that shared authoring implies shared runtime collection or results.",
        "Explore a compact pipeline syntax only if representative real chains become",
        "meaningfully easier to read and lower exactly. Keep explicit Variables valid.",
        "",
        "## Board engagement",
        "",
        "Read `BOARD-DESIGN-OPTIONS.md` in this same ZIP for the scoped import syntax, exact lowering guardrails, debugging design and suggested questions.",
        "",
        "This is suitable as an **informational research preview** after the owner reviews",
        "its examples; it is **not** a specification ratification request.",
        "For discussion, ask whether the Board prefers (1) source-only compiler imports",
        "to remain non-normative authoring tooling, or (2) a shared normative authoring",
        "contract with exact lowering; and what debug stage evidence is worth standardizing.",
        "A later",
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
