# SCAP-NG 0.2.0 specification coverage audit against content-development handoff

Date: 2026-10-03

Status: **pre-Codex audit for the 0.2.0 freeze candidate**.

Purpose: compare the detailed content-development handoff against the current
draft specification so implementation guidance does not become an accidental
source of normative language semantics.

Authority target:

**specification → implementation/reference guidance → conformance content → editor**

This audit classifies each handoff concern as:

- **normative-covered** — already represented adequately in current spec text;
- **normative-promoted** — promoted during this audit because it is universal
  author/processor behavior;
- **reference/conformance guidance** — important, but belongs in examples,
  capability references, or conformance methodology rather than the language core;
- **project workflow only** — Codex/repository process, not specification text;
- **future/open** — deliberately unresolved or deferred.

## Summary

The content-development handoff is substantially consistent with the existing
draft specification. Most architecture and safety rules are already normative.

The main gaps identified during this audit were:

1. explicit conformance evidence layers;
2. native typed-literal authoring versus legacy lexical migration;
3. direct `variable.value` zero-value semantics;
4. stronger wording that synthetic observations do not establish collector or
   live-target conformance;
5. clearer cross-reference between evidence lineage/completeness/redaction and
   result conformance.

Items 1–3 are now represented in the specification/reference text. Item 4 is
included in the new conformance evidence-layer section. Item 5 is already broadly
present in Results and requires editorial consolidation rather than a new model.

## Architecture and object responsibilities

| Handoff requirement | Status | Spec location / disposition |
| --- | --- | --- |
| Benchmark/policy separate from Assessment | normative-covered | requirements index; policy model; Assessment Method |
| Rule selects a check/Assessment rather than embedding scanner behavior | normative-covered | Benchmark/policy and check-selector conformance |
| Assessment graph contains Tests/Objects/States/Variables | normative-covered | Assessment Method |
| Collected Items are runtime observations, not policy | normative-covered | Assessment Method / Results |
| Manual Assessment is first-class | normative-covered | Manual Assessment |
| Applicability is authored assessment logic, not scanner magic | normative-covered | Platform and Applicability |
| Organizational Input is policy data, not executable control | normative-covered | Parameters and Organizational Input; Security |
| Paths/filenames do not define semantic identity | normative-covered | Package/identity requirements |
| Editor is not language authority | project architecture principle | keep in handoff/editor planning; no editor-specific normative model needed |

## Technical outcomes and evaluation

| Handoff requirement | Status | Spec location / disposition |
| --- | --- | --- |
| preserve six technical outcomes | normative-covered | Results / Assessment Method |
| do not equate technical true/false universally with policy pass/fail | normative-covered | Assessment class/result interpretation |
| dependency/conditional execution must preserve non-Boolean outcomes | normative-covered | Assessment Method / Results |
| direct Variable zero values produce technical error | normative-promoted | Assessment reference: `variable.value`; truth-table regression |
| empty string is one value, not zero values | normative-promoted/reference | `variable.value` reference |
| State/Object variable-reference contexts can differ | normative-covered/reference | Assessment Method and `variable.value` reference |
| evaluator must preserve aggregation layers | normative-covered | Assessment Method |

## Native authoring and datatype rules

| Handoff requirement | Status | Spec location / disposition |
| --- | --- | --- |
| native authored literals use native JSON/YAML types | normative-promoted | Assessment Method |
| Boolean `false`, not string `"false"` | normative-promoted | Assessment Method plus semantic-validator regression |
| integer must not accept Boolean/string aliases | normative-promoted | Assessment Method plus regression |
| float must be finite native numeric value | normative-promoted | Assessment Method plus validator |
| legacy XML lexical aliases are importer inputs, not native authoring forms | normative-promoted | Assessment Method |
| record values use structured representation | normative-covered | Assessment Method |

## Conformance evidence

| Handoff requirement | Status | Spec location / disposition |
| --- | --- | --- |
| schema validity is not semantic conformance | normative-covered | Conformance |
| semantic validation separate from schema | normative-covered | Conformance |
| known-result evaluator proof separate from collector proof | normative-promoted | Conformance evidence layers |
| synthetic observations do not prove live collection | normative-promoted | Conformance evidence layers |
| live-target execution is a stronger evidence layer | normative-promoted | Conformance evidence layers |
| migration round-trip is not evaluator equivalence | normative-covered/promoted | Assessment Method + Conformance |
| every expected result should be independently reasoned | reference/conformance guidance | Codex task / future conformance-corpus guide; specification should require deterministic semantics, not prescribe fixture-author workflow |

## Results, evidence, and provenance

| Handoff requirement | Status | Spec location / disposition |
| --- | --- | --- |
| results explain why an outcome occurred | normative-covered | Results |
| evidence lineage identifies observations consumed | normative-covered, editorial consolidation useful | Results / Assessment Method |
| completeness distinct from truth and evidence projection | normative-covered | Results |
| redaction does not change technical truth | normative-covered/reference | Results + capability shared behavior |
| Organizational Input provenance persists into results | normative-covered | Results |
| effective policy/input provenance | normative-covered | Results |
| deterministic messages/reasons | normative-covered | Results |
| bounded evidence does not imply bounded collection | normative-covered direction; conformance expansion needed | Results |
| reusable normalized collected Items | draft-covered | Results; broader runtime implementation remains downstream |

## Migration

| Handoff requirement | Status | Spec location / disposition |
| --- | --- | --- |
| forward conversion from SCAP 1.4 is mandatory | normative-covered | Migration |
| preserve semantics, not XML shape | normative-covered | Migration / specification principles |
| resolve references completely | normative-covered | Migration / Conformance |
| do not silently repair malformed source | normative-covered | Migration |
| source defect vs converter vs NG defect must be distinguished | reference/conformance guidance with normative failure rules | Migration + project issue taxonomy |
| deprecated OVAL Tests are not automatically native NG capabilities | normative-covered in design/migration direction; capability-specific decisions remain governance | Migration / native feature admission |
| unsupported valid source must fail explicitly rather than weaken semantics | normative-covered | Migration / Conformance |
| historical provenance remains outside runtime semantics | normative-covered | Package / Migration |

## Applicability and platform identity

| Handoff requirement | Status | Spec location / disposition |
| --- | --- | --- |
| product Platform distinct from Rule applicability | normative-covered | Platform and Applicability |
| applicability indeterminate/error is not N/A | normative-covered | Platform and Applicability |
| applicability Assessments are reusable | normative-covered | Platform and Applicability |
| scanner SHALL NOT invent hidden OS classification | normative-covered in explicit-resolution principles; examples should reinforce | Platform and Applicability |
| Windows workstation/member server/domain controller distinctions remain authored applicability | reference/content requirement | content corpus should demonstrate; not a universal hard-coded platform taxonomy |

## Security boundaries

| Handoff requirement | Status | Spec location / disposition |
| --- | --- | --- |
| content treated as untrusted | normative-covered | Security |
| Organizational Input cannot inject executable behavior | normative-covered | Security / Parameters |
| `shellcommand` not a generic migration escape hatch | normative policy/reference-covered | Security plus capability mapping policy |
| executable capability interpreter semantics explicit | normative-covered | Security |
| sensitive results require minimization/redaction support | normative-covered, final profile open | Security / Results |

## Packaging and identity

| Handoff requirement | Status | Spec location / disposition |
| --- | --- | --- |
| compiled package resolves source paths/references | normative-covered | Package |
| runtime does not fetch unresolved authoring dependencies | normative-covered | Package |
| logical identity independent of filename | normative-covered | Package |
| migration diagnostics not packaged as executable semantics | normative-covered | Package |
| manifest/integrity deterministic | normative-covered draft | Package / Results |
| final signature/trust profile | future/open | explicitly not required for 0.2.0 content-development freeze |

## OVAL 6.0 / ESX / Kubernetes scope

These are **project/version scope decisions**, not generic core language rules.

- OVAL 5.12.3 remains the migration semantic baseline.
- OVAL 6.0 is inspected only for genuinely new Tests/capability leads.
- ESX expansion is deferred pending upstream guidance.
- `kubepsp_test` is deferred because it targets removed PodSecurityPolicy.
- `kubectl_test` is deferred pending a native Kubernetes resource/API model.
- Existing experimental ESX mappings remain evidence, not a requirement that
  0.2.0 standardize the family.

Keep these in transition/migration/coverage records rather than presenting them
as universal future-language prohibitions.

## Material that should remain outside the normative specification

The following Codex instructions are useful but should not be promoted into core
language requirements:

- develop minimal fixtures before full STIGs;
- commit in bounded coherent groups;
- update a coverage inventory after every group;
- prioritize RHEL 9 / Oracle Linux 9 / Windows 11 / Windows Server 2025;
- use Apache/DNS when they add distinct test complexity;
- exact GitHub branch/commit/handoff procedure;
- editor-development sequencing;
- issue/commit workflow;
- failure triage labels as repository process names.

A future **conformance corpus guide** may standardize fixture metadata and
evidence-level labels without making repository workflow normative.

## Remaining specification editorial work after 0.2.0 freeze

These are not freeze blockers unless validation exposes a semantic contradiction:

1. consolidate evidence-lineage terminology across Assessment Method and Results;
2. add cross-links from result completeness/redaction to conformance evidence layers;
3. define a future machine-readable conformance assertion/report format;
4. finish final unsupported/not-evaluated reason vocabulary;
5. finish signature/trust profile;
6. continue capability-specific reference documentation as content expands;
7. use the Codex corpus to discover any remaining underspecified semantics.

## Conclusion

The detailed Codex handoff does not reveal a missing alternate SCAP-NG
architecture. It mainly exposes the need for stronger conformance methodology
and capability-specific semantic examples.

The draft specification is therefore suitable to serve as the authority for the
0.2.0 content-development phase once the exact-head freeze validation is green.
The content corpus should now be used to challenge the specification, not to
silently define semantics outside it.
