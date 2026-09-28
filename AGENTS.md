# AGENTS.md

## SCAP-NG research evidence rules

SCAP-NG uses two deliberately separate classes of OVAL/SCAP evidence. Do not mix their roles or conclusions.

### 1. Published NIWC STIG corpus — production migration evidence

Repository: `niwc-atlantic/scap-content-library`

Purpose:
- Validate faithful forward conversion of real published SCAP 1.4/STIG content.
- Measure real-world construct usage, dependency closure, rule complexity, and cross-platform reuse.
- Provide production migration/conversion evidence for SCAP-NG architecture decisions.

Requirements:
- Use pinned published artifacts/revisions from the iteration corpus manifest.
- Preserve source behavior before proposing normalization, cleanup, or semantic repair.
- Record anomalies in the source rather than silently correcting them.
- Treat successful conversion of this corpus as evidence of practical migration coverage, not proof of complete OVAL language conformance.

### 2. OVAL Community Self-Assertion corpus — language-conformance evidence

Repository: `OVAL-Community/SCAP-Self-Assertion`
Path: `SCAP_1.4/OVAL_Test_Content`

Purpose:
- Unit-test OVAL Definition Evaluator semantics.
- Exercise OVAL 5.12.3 constructs that production STIG content may not use.
- Validate variables, functions, object components, sets, filters, datatypes, checks, existence semantics, result propagation, records, and platform-specific constructs.

Requirements:
- Keep this corpus logically and statistically separate from the published STIG corpus.
- Do not cite Self-Assertion content as production STIG migration evidence.
- Use expected evaluator behavior from the test content and OVAL 5.12.3 schema/documentation as the semantic contract.
- Prefer small focused Self-Assertion cases when implementing or debugging individual OVAL language features.
- Add regression tests when a Self-Assertion case exposes an importer/evaluator defect or ambiguity.

## Deprecated OVAL migration rule

Deprecated OVAL 5.12.3 constructs that are still present in published SCAP 1.4 content remain part of the forward-conversion requirement.

- Import and preserve their exact source semantics and provenance.
- Prefer a `legacy_compatible` migration treatment when a reviewed successor exists, rather than making the deprecated construct a preferred new SCAP-NG authoring primitive.
- Do not silently rewrite a deprecated construct to its successor unless semantic equivalence has been demonstrated for the specific source usage.
- Keep the original construct identifiable in source accounting even when a native normalized form is approved.
- Production use of a deprecated construct makes compatibility support higher priority than an unobserved schema-only construct, but does not by itself justify carrying the deprecated design forward into new authoring syntax.

## OVAL 5.12.3 importer expectations

The SCAP-NG importer must aim for lossless dependency and semantic representation before native lowering.

In particular:
- Follow recursive references across definitions, tests, objects, states, variables, object sets, filters, `extend_definition`, `object_component`, and `variable_component`.
- Preserve explicit versus defaulted OVAL attributes where the distinction matters for faithful round-tripping.
- Treat OVAL defaults as semantic behavior, not merely syntax. For example, a `filter` without an `action` defaults to `exclude`, and a `set` without `set_operator` defaults to `UNION`.
- Apply filters to each referenced object set before applying the enclosing set operator, per OVAL 5.12.3 semantics.
- Preserve recursive `UNION`, `INTERSECTION`, and relative `COMPLEMENT` semantics, including collection/result flag propagation.
- Do not claim arbitrary OVAL 5.12.3 semantic equivalence until the relevant Self-Assertion conformance cases and production corpus cases pass.
- When semantics are not yet implemented exactly, preserve them explicitly in the IR and mark them unresolved/requires-review rather than approximating them.

## Evidence hierarchy

Use evidence according to the question being answered:

- "Can SCAP-NG migrate real published STIG content?" -> NIWC published STIG corpus.
- "Does SCAP-NG correctly model this OVAL language feature?" -> OVAL Self-Assertion corpus plus OVAL 5.12.3 schema/documentation.
- "Can a native SCAP-NG representation replace the source behavior exactly?" -> require faithful IR plus differential/conformance testing; do not infer equivalence from syntax alone.
