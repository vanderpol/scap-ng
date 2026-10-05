# OVAL Board review of SCAP-NG

**Status:** SCAP-NG 0.2.0 is a frozen pre-alpha working design for human/OVAL Board review. Nothing is Board-approved merely because code, schema, examples, or CI are green.

## Start here

1. Read **[SCAP 1.4 → SCAP-NG: key changes](SCAP-1.4-TO-SCAP-NG-KEY-CHANGES.md)**, including the new **Results: less volume, more useful information** section covering Benchmark summaries, Rule messages/reasons, bounded evidence, maximum returned samples, and explicit completeness.
2. Open the **[SCAP-NG 0.2.0 schema](../schema/v0.2.0/README.md)** — the frozen schema set, capability mappings, validation commands, and newcomer guide are all there.
3. Review the **[0.2.0 Board review content](review-content/0.2.0/README.md)** — this now includes the six source-to-NG converter pilot cases, frequency-oriented examples, focused New NG feature samples, and supporting/stress examples. For a feature-by-feature inventory, use **[FEATURE-SAMPLES.md](review-content/0.2.0/FEATURE-SAMPLES.md)**.
4. Review the **[OVAL 5.12.3 → SCAP-NG capability crosswalk](../specification/migration/oval-5.12.3-capability-crosswalk.md)** — this is the direct Test-type/capability mapping and a critical part of the Board review.
5. Review the **full NIWC Current conversion evidence** described below. A replacement full-corpus artifact is being regenerated from the current 0.2.0 hidden-behavior-safe baseline; do not treat the older 65/65 artifact as the current Board deliverable.
6. Review the **[Board proposals and votes](VOTES.md)** — one maintained index for proposal records, Discussion vote links, and the small set of current design decisions that still need new proposals.
7. Try the **[human-runnable SCAP 1.4 → NG conversion tools](../tools/HUMAN-RUNNABLE-SCRIPTS.md)**. The normal one-package entry point is **[`generate_niwc_current_review.py`](../tools/generate_niwc_current_review.py)**, which runs the checked-in rule splitter and current converter from an original pinned SCAP 1.4 ZIP. The exact-deduplication step is **[`scap_ng_repo_normalizer.py`](../tools/scap_ng_repo_normalizer.py)**.

## Current working direction

- Benchmark → Rule → Assessment; no separate Policy object.
- Preserve used, non-deprecated OVAL semantics without reproducing OVAL XML structure.
- Keep Test, Object, State, Variable, and Item concepts where their semantics remain useful.
- Keep applicability explicit and authored.
- Keep manual assessment first-class.
- Keep migration provenance separate from executable native content.
- Produce smaller, explainable Results with bounded evidence and explicit completeness.
- Use a self-contained manifest-based package for compiled content.

## Review boundary

SCAP-NG remains versioned as **0.2.0** for this Board review, but the current 0.2.0 baseline includes post-freeze corrective changes that made previously implicit/defaulted semantics explicit. Reviewers SHALL use the current `schema/v0.2.0/` content on `main` together with its regression evidence rather than treating the earlier six-case publication SHA as the final technical schema baseline.

The six converter-produced Board cases remain **pending human acceptance**, but they are no longer the whole review surface. The 0.2.0 Board corpus now also includes frequency-oriented examples from the pinned Self-Assertion source, supporting/stress examples for non-trivial Variable/Set/filter/dependency logic, and focused samples for newer or newly explicit NG concepts such as conditional evaluation, a candidate Assessment-result dependency analog for OVAL `extend_definition`, intrinsic and standalone applicability, explicit `not_applicable`, reporting projection, redaction, Organizational Input, manual Assessment, and the collected-Item reuse proposal.

The maintained entry point for that corpus is [`review-content/0.2.0/README.md`](review-content/0.2.0/README.md); the authoritative feature inventory is [`FEATURE-SAMPLES.md`](review-content/0.2.0/FEATURE-SAMPLES.md). The sample corpus is intentionally broader than the six converter-pilot cases, while keeping converter-fidelity evidence separate from native feature-demonstration content.

These checks establish structural, conversion, schema/semantic, and known-result evidence. They do **not** establish independent scanner equivalence, complete collector coverage, or live-target conformance. ESX/VMware and Kubernetes semantics that still need upstream guidance remain deferred rather than being guessed into the frozen design.

## Full NIWC Current conversion build

The exhaustive Board build accounts for all **65 pinned NIWC Current SCAP 1.4 source packages**. The current conversion contract intentionally distinguishes supported standard content from four known NIWC/SCC publisher-extension packages that use `independent.sqlext`:

- **61 packages** are expected to produce native SCAP-NG source trees and compiled packages;
- **4 SQL Server packages** are expected to stop with the explicit blocker `nonstandard source capability independent.sqlext`;
- **0 unexpected blockers** are permitted.

The four expected blockers are the SQL Server 2016 Database/Instance and SQL Server 2022 Database/Instance packages. `sqlext` is NIWC/SCC experimental publisher-extension content and is **not** being promoted into the SCAP-NG native capability registry merely to make the corpus appear 65/65 convertible.

A replacement full-corpus Board artifact is currently being regenerated from the hidden-behavior-safe 0.2.0 baseline. The older artifact from run `37247949326` predates the explicit-default/hidden-behavior fixes and SHALL NOT be treated as the current Board deliverable. This page should be updated with the new run/artifact link and digest only after the current build completes all schema, Assessment-semantic, package-graph, normalization, compilation, and evidence gates.

The full build preserves the fresh source-derived NG trees for supported packages, exact-semantics normalized trees, compiled `.scapng` packages, conversion/blocker status for every one of the 65 source packages, and before/after validation evidence. Normalization may replace exact duplicate Assessment definitions with one shared Assessment only when semantic equivalence is proven; Rule/check bindings and source provenance remain represented.

## Reproduce the conversion

The review builds are generated from checked-in tools and pinned source packages; they are not hand-edited exports. A reviewer can run the same pipeline locally:

- **Convert one pinned SCAP 1.4 package:** [`tools/generate_niwc_current_review.py`](../tools/generate_niwc_current_review.py)
- **See complete commands and prerequisites:** [Human-runnable SCAP-NG tools](../tools/HUMAN-RUNNABLE-SCRIPTS.md)
- **Normalize only proven exact duplicate Assessments:** [`tools/scap_ng_repo_normalizer.py`](../tools/scap_ng_repo_normalizer.py)
- **Inspect the exhaustive 65-package CI pipeline:** [`.github/workflows/scap-ng-full-current-native-normalize-compile.yml`](../.github/workflows/scap-ng-full-current-native-normalize-compile.yml)

The conversion goal is **semantic losslessness for supported SCAP 1.4 paths, with a normalized native representation**. Exact duplicate Assessment definitions may be replaced by one shared Assessment only when semantic equivalence is proven; Rule/check bindings and source provenance remain represented. Similar or near-duplicate Assessments are not merged automatically.

## Open design discussions

- **[Native representation of OVAL `extend_definition`](discussions/EXTEND-DEFINITION-NATIVE-MODEL.md)** — current conversion preserves the semantic by recursive inlining; the Board still needs to decide whether native NG should preserve an explicit Assessment-result reference and, if so, where that binding belongs.

## Voting

See **[Board proposals and votes](VOTES.md)** for the complete maintained proposal index, individual immutable proposal records, Discussion vote links, current proposal gaps, and voting-governance caveats.
