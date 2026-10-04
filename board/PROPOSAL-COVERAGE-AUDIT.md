# OVAL Board proposal coverage audit

**Status:** working crosswalk against the frozen SCAP-NG 0.2.0 design. This document does not change, supersede, or ratify any published proposal.

**Reviewed:** 2026-10-04

This audit compares the actual yes/no questions in published proposals P001–P058 with the current [SCAP 1.4 → SCAP-NG key changes](SCAP-1.4-TO-SCAP-NG-KEY-CHANGES.md). A topic is counted as covered only when the voting question addresses the semantic decision; related rationale or implementation text alone is not treated as Board approval.

## Major changes already covered

| Current key change | Existing proposal coverage | Coverage |
| --- | --- | --- |
| Benchmark → Rule → Assessment; no separate Policy object | P002 | Direct |
| Preserve required OVAL semantics without reproducing XML structure | P003, P056 | Direct design principle |
| Cleaner native capability names with an exact OVAL crosswalk | P004 | Direct |
| Deprecated source Tests block automated conversion | P005 | Direct |
| Dependency ordering and cycle rejection | P009 | Direct for ordering/cycles only |
| Safe collection-result reuse and cache identity | P014, P015 | Direct |
| Assessment-internal applicability / OVAL applicability markers | P016–P018 | Direct, but P016 wording predates native conditionals |
| Assessment and local-node versioning | P019, P020 | Direct |
| Informational policy separate from Assessment technical truth | P023 | Direct |
| Result hierarchy, bounded evidence, completeness | P024–P027, P035 | Direct |
| Self-contained manifest package and signing/trust | P028–P033 | Direct |
| Rules enabled by Benchmark membership; Profiles subtractive only | P036 | Direct |
| Tailoring boundaries and provenance | P037, P038 | Direct |
| Typed Organizational Input cannot change executable behavior | P039, P046 | Direct for safety/type boundary |
| XCCDF refine-value normalization | P040 | Direct |
| Manual assessment model | P042–P046 | Direct |
| Executable applicability rather than CPE/scanner magic | P047, P048 | Direct |
| Stable identity independent of filenames | P049 | Direct |
| Publisher extension isolation | P050 | Direct |
| Source migration, defaults, defects and unsupported paths | P051, P056 | Direct |
| Independent conformance evidence layers | P052 | Direct |
| Resolved execution representation / authoring view | P053, P054 | Direct |
| Alternate result encodings | P055 | Direct |

## Missing or stale Board decisions

### 1. Native conditional execution — current P058 conflicts with 0.2.0

The frozen working design now supports structured `if / then / else` in an Assessment `evaluate` expression. Only the selected branch executes, and result-domain semantics are preserved.

P058 asks the Board to **defer** general IF/ELIF/ELSE or unrestricted conditional programming. P016 also says narrow applicability predicates should come before introducing general conditional programming. Those published proposal texts must remain immutable, but they are now stale relative to the 0.2.0 design.

**Candidate new vote:**

> SCAP-NG automated Assessment expressions SHALL support explicit structured `if / then / else` conditional evaluation. The condition and selected branch SHALL preserve the complete Assessment result domain, and the unselected branch SHALL NOT execute. Existing OVAL Boolean criteria SHALL NOT be rewritten as conditionals unless equivalent source semantics actually require conditional execution.

If adopted, the new proposal should explicitly supersede the design direction proposed by P058.

### 2. Standalone, independently executable Assessments

P002 defines Benchmark → Rule → Assessment and P019 assumes independently published Assessments, but no yes/no question ratifies the more fundamental architecture now stated by the specification:

- an automated Assessment is independently valid and executable;
- it does not require a Benchmark or Rule wrapper;
- standalone execution can produce an Assessment Result directly;
- SCAP-NG consumes this assessment language rather than making its technical semantics dependent on policy constructs.

**Candidate new vote:**

> An automated Assessment SHALL be an independently valid and executable unit that can run without a Benchmark or Rule wrapper and can produce an Assessment Result directly. SCAP-NG policy MAY reference and package Assessments, but SHALL NOT make core automated Assessment semantics depend on Benchmark or Rule constructs.

### 3. Assessment-result dependencies and OVAL `extend_definition`

P009 addresses dependency order and cycles, but does not approve the first-class composition mechanism now in the specification:

- an Assessment can consume another Assessment's result as an `evaluate` leaf;
- the complete result domain is preserved;
- compatible dependency execution may be reused with provenance;
- result dependency reuse is distinct from Collection/Item reuse;
- OVAL `extend_definition` maps to an Assessment-result dependency instead of being blindly inlined.

**Candidate new vote:**

> An automated Assessment MAY statically depend on another Assessment and consume its complete result as a logical evaluation leaf. OVAL `extend_definition` SHALL migrate through this dependency mechanism when semantics can be preserved. Assessment-result reuse SHALL preserve execution provenance and SHALL remain distinct from sharing collected Items.

### 4. Exact semantic Assessment normalization and deduplication

P014/P015 concern runtime Collection reuse, not authored Assessment-definition deduplication. The current full-corpus normalizer can replace multiple exact duplicate Assessment definitions with one shared reusable Assessment only after semantic equivalence is proven.

This is a major reason NG can be smaller without being lossy and deserves an explicit Board decision.

**Candidate new vote:**

> Conversion and normalization MAY replace multiple Assessment definitions with one shared Assessment only when exact semantic equivalence is proven. Every original Rule/check binding, effective input, applicability relationship and source-provenance relationship SHALL remain represented. Similar or near-duplicate Assessments SHALL NOT be merged automatically.

### 5. OVAL 5.12.3 semantic baseline plus reviewed later changes

Several proposals use OVAL 5.12.3 evidence, but none directly asks the Board to approve the baseline policy described in the key-changes document: 5.12.3 as the inherited semantic baseline, later corrections/reinstatements reviewed explicitly, and the prior OVAL 6 work used mainly to identify genuinely new Test semantics rather than as an automatic wholesale replacement.

**Candidate new vote:**

> The initial NG automated-assessment semantic baseline SHALL be OVAL 5.12.3, augmented only by explicitly reviewed later errata, reinstatements, or genuinely new semantics. Prior OVAL 6 work SHALL NOT be imported wholesale merely because it is newer.

### 6. General disposition of unused XCCDF features

P040 handles `refine-value`, P048 handles the CPE dictionary direction, and P056 says used/conformance-tested semantics must be preserved. But there is no complementary yes/no decision establishing what happens to **unused** XCCDF machinery.

The current design intentionally does not reproduce unused wrappers, indirections, and serialization constructs merely for structural compatibility.

**Candidate new vote:**

> XCCDF constructs that are neither used by supported real-world/conformance content nor required to preserve effective policy semantics SHALL NOT be reproduced automatically in native SCAP-NG Benchmarks. Each omitted, normalized, replaced, or blocked legacy construct SHALL have an explicit disposition and migration/provenance treatment.

This should be read together with P056: used semantics are preserved; genuinely unused structure does not receive automatic native equivalents.

### 7. Organizational Input as the successor to legacy interactive/unresolved policy values

P039 correctly ratifies type/cardinality/safety behavior, and P046 separates human expected values from evidence/outcomes. Neither question explicitly asks whether Organizational Input is the native policy-resolution mechanism for organization-delegated values instead of carrying forward legacy interactive-variable behavior.

**Candidate new vote:**

> When policy intentionally delegates an expected value to the deploying organization, SCAP-NG SHALL resolve that value through typed Organizational Input before Assessment execution rather than through executable interactive-variable semantics. Supplying Organizational Input SHALL NOT by itself constitute Tailoring.

### 8. Tests whose natural source is not an Object

The current Assessment design allows a Test to evaluate another first-class source, such as a Variable, without requiring an artificial Object wrapper. P057 covers the special `independent.unknown` objectless Test, but there is no general proposal establishing this native design principle.

**Candidate new vote:**

> A native Test SHALL NOT require an Object solely for structural compatibility when its defined semantic source is another first-class Assessment node, such as a Variable. Capability contracts SHALL explicitly define the permitted source kind and type compatibility.

## Recommended next proposal round

The next proposal round should not reopen decisions already cleanly covered. The highest-priority additions are:

1. native structured conditional execution, explicitly replacing the P058 direction;
2. standalone independently executable Assessments;
3. Assessment-result dependency / `extend_definition` composition;
4. exact semantic Assessment normalization and deduplication;
5. OVAL 5.12.3 semantic baseline;
6. disposition rule for unused XCCDF features;
7. Organizational Input as the organization-delegated value mechanism;
8. non-Object Test source contracts.

These should be new immutable proposal versions/IDs. Published P001–P058 text should remain unchanged for historical voting integrity.

## Full-corpus evidence requirement

The Board review should include a fresh conversion of all **65 pinned NIWC Current SCAP 1.4 datastream packages**, not only the small illustrative cases.

The deliverable should contain:

- fresh source-derived NG trees;
- exact-semantics normalized NG trees;
- compiled readable `.scapng` packages;
- conversion/blocker status for all 65 source packages;
- schema, semantic and package-graph validation before and after normalization;
- normalization evidence showing Assessment-definition reduction;
- source revision/checksums and conversion provenance.

The reviewer-facing explanation should describe the conversion as **semantically lossless for supported conversion paths while normalized in representation**. Exact duplicate Assessments may be collapsed into one shared Assessment only after equivalence is proven; all Rule/check bindings and provenance remain represented. Near-duplicates remain separate and require human review.
