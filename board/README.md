# OVAL Board review of SCAP-NG

**Status:** SCAP-NG 0.2.0 is a frozen pre-alpha working design for human/OVAL Board review. Nothing is Board-approved merely because code, schema, examples, or CI are green.

## Start here

1. Read **[SCAP 1.4 → SCAP-NG: key changes](SCAP-1.4-TO-SCAP-NG-KEY-CHANGES.md)**.
2. Open the **[SCAP-NG 0.2.0 schema](../schema/v0.2.0/README.md)** — the frozen schema set, capability mappings, validation commands, and newcomer guide are all there.
3. Review the six small **[0.2.0 source-to-NG examples](review-content/0.2.0/README.md)**.
4. Review the **[OVAL 5.12.3 → SCAP-NG capability crosswalk](../specification/migration/oval-5.12.3-capability-crosswalk.md)** — this is the direct Test-type/capability mapping and a critical part of the Board review.
5. Download the **[current normalized 65-package SCAP 1.4 → SCAP-NG review artifact](https://github.com/vanderpol/scap-ng/actions/runs/37242380664/artifacts/11318411057)** (`niwc-current-full-review`). It contains the source-derived trees, exact-semantics normalized trees, compiled packages, and validation evidence for all 65 pinned NIWC Current source packages.
6. Review the **[proposal coverage audit](PROPOSAL-COVERAGE-AUDIT.md)** for current-design gaps and stale voting questions.
7. Try the **[human-runnable SCAP 1.4 → NG conversion tools](../tools/HUMAN-RUNNABLE-SCRIPTS.md)**. The normal one-package entry point is **[`generate_niwc_current_review.py`](../tools/generate_niwc_current_review.py)**, which runs the checked-in rule splitter and current converter from an original pinned SCAP 1.4 ZIP. The exact-deduplication step is **[`scap_ng_repo_normalizer.py`](../tools/scap_ng_repo_normalizer.py)**.
8. Review or vote on individual **[Board proposals](proposals/README.md)** through the published **[Discussion links](VOTES.md)**.

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

The technical schema baseline is `7cd8b1242d7fb4a2eb9b5f49c7ec3f48b2dd622d`. Later commits may add Board samples, documentation, CI, or maintenance without changing that frozen schema meaning.

The six converter-produced Board cases are present and validated, but still **pending human acceptance**. The six-case publication commit is `8262e7e03418c229b85db6fe5cab600c9b92b8e9`; its repository-boundary, rebaseline-smoke, current-design-regression, and fast-five conversion workflows completed successfully. The frozen 0.2.0 baseline also passed broader Self-Assertion and full-corpus validation gates.

These checks establish structural, conversion, and known-result evidence. They do **not** establish independent scanner equivalence, complete collector coverage, or live-target conformance. ESX/VMware and Kubernetes semantics that still need upstream guidance remain deferred rather than being guessed into the frozen design.

## Full 65-package conversion build

A fresh conversion of all **65 pinned NIWC Current SCAP 1.4 packages** completed successfully using the checked-in converter and exact-semantics normalizer pipeline for Board review:

- **[Download the normalized 65-package review artifact](https://github.com/vanderpol/scap-ng/actions/runs/37242380664/artifacts/11318411057)** — `niwc-current-full-review`
- **[GitHub Actions run 37242380664](https://github.com/vanderpol/scap-ng/actions/runs/37242380664)** — build provenance, logs, and all generated artifacts
- Artifact SHA-256: `fbad06c83a057c20a3348d29590cc3269a431518e44af406bc452a3a92869cd6`

The build preserves the fresh source-derived NG trees, exact-semantics normalized trees, compiled `.scapng` packages, conversion/blocker status for every source package, and before/after validation evidence. Normalization may replace exact duplicate Assessment definitions with one shared Assessment only when semantic equivalence is proven; Rule/check bindings and source provenance remain represented.

## Reproduce the conversion

The published review builds are generated from checked-in tools and pinned source packages; they are not hand-edited exports. A reviewer can run the same pipeline locally:

- **Convert one pinned SCAP 1.4 package:** [`tools/generate_niwc_current_review.py`](../tools/generate_niwc_current_review.py)
- **See complete commands and prerequisites:** [Human-runnable SCAP-NG tools](../tools/HUMAN-RUNNABLE-SCRIPTS.md)
- **Normalize only proven exact duplicate Assessments:** [`tools/scap_ng_repo_normalizer.py`](../tools/scap_ng_repo_normalizer.py)
- **Inspect the exhaustive 65-package CI pipeline:** [`.github/workflows/scap-ng-full-current-native-normalize-compile.yml`](../.github/workflows/scap-ng-full-current-native-normalize-compile.yml)

The conversion goal is **semantic losslessness for supported SCAP 1.4 paths, with a normalized native representation**. Exact duplicate Assessment definitions may be replaced by one shared Assessment only when semantic equivalence is proven; Rule/check bindings and source provenance remain represented. Similar or near-duplicate Assessments are not merged automatically.

## Voting

Published proposal text is versioned. React to the opening Discussion post with 👍 Yes or 👎 No; comments explain a vote. A substantive change requires a new proposal version rather than silently editing the voted text.

Eligibility, quorum, voting duration, abstention/conflict handling, and official disposition still require Board agreement before reactions are binding.
