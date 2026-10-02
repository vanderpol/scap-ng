# Iteration 003 status and current entry points

This directory contains both active records and older experiments. It is not one uniformly current source tree.

| Area | Current interpretation |
| --- | --- |
| `design/CURRENT-DESIGN.md` | Authoritative working-design checkpoint; latest owner corrections take precedence |
| `design/` | Current decision and semantic records; historical terminology within older notes needs reconciliation |
| `review/rhel9-current-full/` | Generated full RHEL 9 review candidate; [maintained guide](../../../docs/rhel9-review.md) |
| `review/windows11-current-full/` | Generated full Windows 11 review candidate; [guide](review/windows11-current-full/README.md) |
| `review/full-current-native-normalized/` | Latest pinned-corpus normalization review snapshot; provenance and handled errors are separate |
| Other `review/` slices | Dated focused evidence, not automatic latest-grammar approval |
| `source/`, `packages/` | Historical generated baseline and superseded Policy experiments |
| `examples/`, `results/` | Focused working demonstrations; validate their individual grammar/status |
| `evidence/` | Dated evidence valid only for its recorded source/commit and gate |
| `board-review/` | Original questions, reconciled into [individual yes/no proposals](../../../board/proposals/README.md) |

Use the [maintained tools](../../../tools/README.md). Historical generation workflows require explicit opt-in; held publishing jobs stay held. [Lossless rebaseline](../../../docs/lossless-rebaseline.md).

## Preserved original iteration plan

The following original plan is historical. Its directions toward `source/split-rule-assessment/` and earlier terminology are superseded by the status table above and CURRENT-DESIGN.

# SCAP-NG Research Iteration 003

**Status:** active clean-room conversion redesign  
**Audience:** project contributors, external reviewers, and potential OVAL Board review

Current review entry point: [full RHEL9 current-design review](review/rhel9-current-full/README.md). It is generated from the pinned original package using `tools/scap_upconvert_v003/convert_full_review.py`; older `source/` trees remain historical baselines. Read [CURRENT-DESIGN.md](design/CURRENT-DESIGN.md) before selecting a generator.

Iteration 003 is organized so a reviewer can understand it without knowing
iteration 001 or 002.

Its purpose is to demonstrate a clean, semantically lossless SCAP 1.4 ->
SCAP-NG conversion approach using the current native design.

## Directory map

    003/
      README.md
      design/
      source/
        split-rule-assessment/
      examples/
      results/
      evidence/
      tooling-notes/

### design/

Human-readable architecture and conversion decisions for this iteration.

Start here after reading this README.

### source/

Native SCAP-NG source examples.

Each independently reviewable SCAP-NG architecture gets its own directory.
Iteration 003 currently implements only:

    source/split-rule-assessment/

Other architectures SHALL NOT be mixed into that tree.

### examples/

Small focused examples used to explain individual semantics, edge cases, and
conversion behavior. These are teaching/review artifacts, not complete
benchmark source trees.

### results/

Sample SCAP-NG result artifacts and result-format demonstrations.

Source and results are deliberately separated so reviewers never have to guess
whether a file is input content or scanner output.

### evidence/

Conversion provenance, equivalence reports, source accounting, migration
diagnostics, hashes, and other proof material.

Legacy SCAP 1.4 identifiers, namespaces, hrefs, and XML-derived lineage MAY
appear here when needed for traceability. They SHALL NOT appear in native NG
source.

### tooling-notes/

Iteration-specific implementation notes and converter-development observations.
Reusable converter code remains under repository-level tools/.

## Current architecture under review

Iteration 003 currently covers only the split Rule/Assessment architecture:

    Benchmark -> Rule -> selected check -> Assessment

All native source for that model belongs under:

    source/split-rule-assessment/

A future architecture experiment MUST use a separate sibling directory rather
than adding alternate semantics into this tree.

## Review order

For an external reviewer, the intended path is:

1. README.md
2. design/conversion-contract.md
3. design/native-source-layout.md
4. design/applicability-registry.md
5. source/split-rule-assessment/
6. examples/
7. results/
8. evidence/

## Clean-source rule

Native SCAP-NG source SHALL NOT contain XCCDF, OVAL, OCIL, or CPE
Applicability Language IDs, namespaces, hrefs, XML-shaped structures, or other
legacy serialization residue.

Legacy lineage belongs only in evidence/provenance.

If preserving such a reference appears necessary to retain semantics, the
conversion path stops for design review rather than leaking the legacy
construct into NG source.
