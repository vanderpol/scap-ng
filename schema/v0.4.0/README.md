# SCAP-NG v0.4.0 — working schema draft

**Pre-alpha draft, not accepted or Board approved.** The v0.3.0 schemas are unchanged.

This directory is a complete physically independent version-local copy-forward of the 0.3 schema and capability mapping surface. Versioned metadata, IDs and references identify v0.4.0; each unchanged file preserves its substantive modification date.

## Meeting-ready six-STIG YAML + JSON review packet (October 15, 2026)

**[Download the pinned Joval discussion preview release](https://github.com/vanderpol/scap-ng/releases/tag/v0.4.0-joval-meeting-preview-20261015-r2)**, with **six complete source-backed STIG authoring sets in both YAML and JSON**. [Short technical meeting guide](../../research/assessment-simplification/compact-authoring-04/JOVAL-TECHNICAL-PREVIEW.md). The generated scoped State-field requirements and `and`/`or` group spelling are **research candidates**, not yet adopted by the base 0.4 schema; they validate via [research schema overlay](../../tools/research_04_scoped_schema.py), fully explicit scope expansion, full 0.4 Assessment validation and native capability schemas. Both formats have equivalent parsed values. This is **not** a scanner bundle and the JSON mirror retains source YAML reference strings.

## Draft Assessment grammar

- A single versioned authoring grammar: no mixed legacy `field:/value:/operation:/existence:/match:` State forms.
- Every Test explicitly declares `require:`; State-free and State-bearing Tests have separate valid requirement names.
- State fields use observed field keys, e.g. `- owner_uid: {equals: 0, require: at_least_one_exists_and_all_match}`.
- **Object selectors now use the same comparison-as-key vocabulary**, e.g. `select.directory: {equals: [/lib, /lib64], datatype: string, value_match: one}`, but SHALL NOT carry `require` or consume Organizational Input. Legacy `value` + `operation` Object selectors fail draft 0.4 validation. This is enforced by the full Assessment schema for native inline/shared Object `select` properties and the version-local shared schema.
- Exactly one comparison operation per scalar predicate; arrays, Variables and Organizational Input references retain explicit `value_match` and datatype requirements.
- Windows record and nested field requirements are distinct. Object Set filters use `include:` or `exclude:` on a field-key predicate.
- `evaluate`, `for_each`, typed Variable graphs, manual choices and collected Items/results do not acquire new semantics.

## Current real-world 0.4 authoring previews

The [strictly validated interim RHEL 9 and Windows 11 authoring preview](https://github.com/vanderpol/scap-ng/actions/runs/38798029627/artifacts/12002887248) provides two distinct ZIPs containing complete real automated/applicability Assessment YAML in the present one-grammar 0.4 draft. Source Rules, Benchmark, manual alternatives and referenced shared content are present for context, with YAML/source inversion and native Test validation recorded in each ZIP's `provenance.json`. These are **not** scanner bundles or a normative release. The 90-day Actions artifact is research evidence, not a permanent distribution.

## Native generator and real-content evidence

The [version-local native 0.4 capability generator](../../tools/generate_capability_schema_v04.py) successfully emits JSON Schema draft contracts for **all 100 supported reviewed capability mappings** ([successful 100-capability CI](https://github.com/vanderpol/scap-ng/actions/runs/38759490558)). The frozen 0.3 generator remains unchanged. This proves schema generation, reference locality and selected native field-name checks, **not** acceptance of all real authored Tests.

The first generated-native deep audit exposed 541 rejected Tests and guided targeted corrections; that run is **historical failure evidence**, not the current outcome. The [strict six-anchor authoring schema gate](https://github.com/vanderpol/scap-ng/actions/runs/38770315633) now validates **all 1,396 automated/applicability Assessment documents and all 2,144 Test occurrences**, with **1,384 exact parsed source reconstructions** and **12 independently documented State-free reference-model normalizations**. This is complete representative **schema/source-lowering** coverage, not scanner/runtime interoperability approval. All 100 reviewed capability mappings generate independent 0.4 schemas ([CI](https://github.com/vanderpol/scap-ng/actions/runs/38768460733)).
## Source provenance for constant Variables

The original Windows 11 / Windows Server 2025 OVAL userright selectors
reference a 45-value constant Variable. The source omits `var_check` and
`operation`. Under OVAL 5.12.3, those mean **all** and **equals**,
respectively. The 0.4 research migration therefore uses an explicit
array with `value_match: all`, **not** `one` (which would change truth
semantics). See [#228](https://github.com/vanderpol/scap-ng/issues/228)
and the pinned-source verification workflow. This is a source-semantic
conversion guard, not a scanner correctness claim.

## Verified six-anchor draft integration

The complete six-STIG native-structure audit covers RHEL 9, Oracle Linux 9,
Windows 11, Windows Server 2025, Windows Server DNS and Apache. It validates
the complete authored automated Assessment document as well as each generated
capability-specific Test schema, preserving individual source re-expansion
and distinguishing source-exact changes from separately documented State-free
model normalizations. This is **not** scanner execution and does not promote
a candidate semantic change to normative specification.

## Promotion gates still open

The [strict six-anchor structural gate](https://github.com/vanderpol/scap-ng/actions/runs/38770315633) passes and rejects unsupported native field, operand, cardinality and mixed-dialect shapes in focused tests. Remaining independent gates: owner review of human-readable rare `require:` terminology and exact semantics; reference-model boundary and negative fixtures for every supported uncommon capability; full authoring-to-package compiler integration for 0.4; resolution of existing current-main legacy converter regression [#226](https://github.com/vanderpol/scap-ng/issues/226); and intentional full 65-source checkpoint before release. No SCAP-NG scanner exists, and none is needed to draft the language; vendor execution conformance comes later. Source-only Variable modules and debugging views remain unapproved [research #223](https://github.com/vanderpol/scap-ng/issues/223).
See [0.4 scope and release gates](../../research/assessment-simplification/compact-authoring-04/0.4-SCOPE-AND-RELEASE-GATES.md), [issue #227](https://github.com/vanderpol/scap-ng/issues/227) and [variable research #223](https://github.com/vanderpol/scap-ng/issues/223).
