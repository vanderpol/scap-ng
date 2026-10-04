# OVAL Board review of SCAP-NG

**Status:** SCAP-NG 0.2.0 is a frozen pre-alpha working design for human/OVAL Board review. Nothing is Board-approved merely because code, schema, examples, or CI are green.

## Start here

1. Read **[SCAP 1.4 → SCAP-NG: key changes](SCAP-1.4-TO-SCAP-NG-KEY-CHANGES.md)**.
2. Open the **[SCAP-NG 0.2.0 schema](../schema/v0.2.0/README.md)** — the frozen schema set, capability mappings, validation commands, and newcomer guide are all there.
3. Review the six small **[0.2.0 source-to-NG examples](review-content/0.2.0/README.md)**.
4. Use the **[0.2.0 review checkpoint](SCAP-NG-0.2.0-REVIEW-CHECKPOINT.md)** for scope, evidence, and open Board questions.
5. Consult the detailed **[OVAL-to-NG capability crosswalk](../specification/migration/oval-5.12.3-capability-crosswalk.md)** only when deeper mapping detail is needed.
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

The six converter-produced Board cases are present and validated, but still **pending human acceptance**. Schema/round-trip tests do not prove independent scanner or live-target equivalence.

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
