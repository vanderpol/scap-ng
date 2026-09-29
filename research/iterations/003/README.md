# SCAP-NG Research Iteration 003

**Status:** active clean-room conversion redesign

Iteration 003 restarts SCAP 1.4 -> SCAP-NG conversion from the current SCAP-NG
design rather than attempting to repair the fidelity-first generators created
during iterations 001 and 002.

Iteration 001 remains migration/language research evidence. Iteration 002
remains the source-design and decision record. The large generated iteration-002
conversion trees are retained only as forensic/regression evidence and are not
authoritative native SCAP-NG source.

## Objective

Build a conversion process that is:

- semantically lossless for supported SCAP 1.4 constructs;
- explicit and loud when source semantics are unsupported;
- independent of SCAP 1.4 serialization in the resulting native source;
- concise enough for human authoring and review;
- based on the accepted iteration-002 Benchmark/Policy/Assessment architecture;
- suitable to evolve into a public standalone up-conversion tool.

## Governing pipeline

    pinned SCAP 1.4 source
        -> semantic extraction
        -> versioned normalized semantic IR
        -> semantic accounting / blocker gate
        -> native SCAP-NG lowering
        -> equivalence verification
        -> provenance/evidence report

The semantic IR is an internal converter contract. It is not SCAP-NG source
syntax and SHALL NOT be allowed to define the native authoring model by accident.

## Hard boundary: semantics vs provenance

Native SCAP-NG source contains only information required to author or execute the
NG content.

Legacy XCCDF/OVAL/OCIL/CPE serialization details belong in conversion evidence
and provenance unless a specific detail is proven to affect behavior.

The following are prohibited from native output merely for source fidelity:

- raw XML source trees;
- XML namespace URIs;
- source component filenames and hrefs;
- opaque OVAL object/test/state IDs;
- OCIL questionnaire scaffolding;
- CPE dictionary XML structure;
- XCCDF element-shaped mirrors;
- duplicate inherited profile snapshots.

Losslessness means preservation of behavior, not the ability to reproduce the
source XML byte-for-byte.

## 003 acceptance gates

Native rendering does not begin with full benchmark regeneration.

First, representative cases SHALL prove the IR and conversion rules for:

1. a simple automated Rule;
2. a manual Rule;
3. a Rule with default/automated/manual selectable checks;
4. complex Boolean OVAL logic;
5. OVAL variables and external/XCCDF-bound input;
6. Benchmark and Rule applicability;
7. profile selection/refinement deltas;
8. reusable/shared Assessment candidates;
9. existence/non-existence/cardinality semantics;
10. unsupported or deprecated constructs that must fail loudly.

Only after those cases are understandable as native SCAP-NG and pass semantic
accounting should the four anchor benchmarks be regenerated.

## Four anchor corpus

The standing production migration corpus remains:

- RHEL 9
- Oracle Linux 9
- Windows 11
- Windows Server 2025

Conversion SHALL begin from pinned original published SCAP 1.4 source artifacts,
not from iteration-001 or iteration-002 generated YAML.

## Reuse policy for older code

Iteration 003 converter code SHALL NOT import the old whole-benchmark conversion
pipeline or use old generated YAML as an input.

Older code MAY be consulted as research evidence for:

- source constructs previously encountered;
- regression cases;
- known dependency-closure traps;
- OVAL semantic lessons;
- diagnostics that should remain covered.

Any useful algorithm brought forward must be reimplemented against the 003 IR
contract and independently tested.

## Initial implementation

The first implementation lives under tools/scap_upconvert_v003/.

It intentionally performs only:

- XCCDF semantic extraction into a compact versioned IR;
- separate provenance/source accounting;
- explicit diagnostics for constructs not yet represented.

It does **not** yet emit native SCAP-NG YAML. That is deliberate: the IR must be
reviewed before another renderer is permitted to shape the source model.

See conversion-contract.md, semantic-ir.md, and native-source-layout.md.
