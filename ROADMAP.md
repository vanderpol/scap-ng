# SCAP-NG development roadmap

Updated: 2026-10-04.

SCAP-NG 0.2.0 is technically frozen for bounded human/OVAL Board review. The roadmap now prioritizes conformance evidence and review over further unbounded schema expansion.

## Current phase — 0.2.0 review and conformance

Immediate goals:

1. Human-review the six converter-produced Board examples and resolve only demonstrated defects.
2. Turn accepted examples into the seed conformance corpus.
3. Close known converter gaps, especially direct Variable Tests and additional valid Object/Variable/Set/Filter/function patterns.
4. Expand representative conversion coverage only after the small review gate.
5. Add stronger independent/runtime evidence, including live collector and differential execution where practical.

## Next phase — authoring and reference implementation

After the language/conformance surface is stable enough:

- build the content editor from accepted native content rather than letting UI design determine semantics;
- build a minimal reference evaluator/scanner focused on normative correctness and conformance;
- continue concise capability/reference documentation generated from reviewed semantic sources where practical;
- improve diagnostics and Windows/local converter usability.

## Packaging, results, and scale

Continue hardening without changing Assessment truth semantics:

- deterministic manifest-based `.scapng` bundles;
- signing/trust profiles and verification policy;
- compact Results with evidence completeness, privacy/redaction, and JSONL/SIEM projection;
- enterprise/offline performance and 100k+ host assumptions;
- reusable/shared Assessment optimization only where semantic equivalence is proven.

## Standards/community path

When semantics and conformance evidence are mature:

- consolidate normative requirements, terminology, SCAP 1.4/OVAL crosswalks, and Board decisions;
- resolve remaining OVAL Board questions and versioned votes;
- prepare material suitable for broader SCAP/NIST standards discussion;
- plan any eventual OVAL Community transition only with explicit owner and receiving-organization approval.

## Design boundaries

- Current architecture is **Benchmark → Rule → Assessment**; there is no separate Policy object.
- OVAL 5.12.3 is the current migration semantic baseline, with later corrections/reinstatements handled explicitly.
- Used, non-deprecated semantics are preserved unless an explicit reviewed disposition replaces/removes them.
- Deprecated Tests are migration blockers unless authoritatively reinstated.
- Source defects are reported, not silently repaired during equivalence conversion.
- Migration provenance stays outside executable native content.
- ESX/VMware expansion and the two Kubernetes OVAL 6-only Tests remain deferred as recorded in the 0.2.0 checkpoint.

## Validation strategy

- **Focused tests:** normal development loop.
- **Fast five-benchmark regression:** normal integration gate for converter/schema changes.
- **Full NIWC corpus:** intentional milestones/freezes/Board deliverables, not the routine edit loop.
- Human acceptance, Board ratification, schema validity, migration equivalence, collector conformance, and live-target validation remain distinct statuses.

[Open issues](https://github.com/vanderpol/scap-ng/issues?q=is%3Aissue+is%3Aopen) · [Board review](board/README.md) · [Current design](research/iterations/003/design/CURRENT-DESIGN.md) · [Tools](tools/HUMAN-RUNNABLE-SCRIPTS.md)
