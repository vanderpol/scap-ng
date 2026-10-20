# SCAP-NG v0.4.0 — working schema draft

**Owner-approved pre-alpha 0.4.0 authoring-sample schema**, not OVAL Board ratification or scanner conformance. Historical 0.3.0 schemas remain [archived](../../archive/0.3.0/README.md).

**[Download current six-STIG 0.4.0 YAML and JSON authoring samples](https://github.com/vanderpol/scap-ng/releases/tag/v0.4.0-six-stig-authoring-approved-20261020).** All 4,001 files passed strict version-local schema checks in both formats. The 2,958 Rule-choice links resolve and all six Benchmarks declare the exact reachable automated Assessment specification **0.4.0**, under the owner's approved version policy. The build preserves the earlier source, its hashes and 172 exceptional source-exact Tests.

The earlier 0.4-A research syntax and October 15 r3 source preview remain pinned **research inputs**, not current authoring dialects. The canonical Test `require` carries source-proven structured `items` and `all_items_must` when supported, without redundant inline Object `capability`. See [current Assessment examples](../../specification/examples/assessments.md), [canonical decision](../../research/assessment-simplification/compact-authoring-04/OWNER-0.4.0-CANONICAL-DECISION.md), and [validation gates](../../review/current/0.4.0-FINALIZATION-GATES.md).

Passing authoring schema/graph validation and 25,628 generic OVAL result comparisons does **not** establish the native executable .scapng compiler, capability-specific scanner execution or independent runtime conformance.

## Shared authoring vocabulary (advisory preview)

The version-local [English authoring vocabulary](authoring-vocabulary.en.json) (research [#244](https://github.com/vanderpol/scap-ng/issues/244)) centralizes **display labels, questions and explanatory text** for editors, scanner GUIs and authoring agents. It does not alter any Assessment JSON/YAML grammar, evaluation results, capability semantics or native identifiers. Tool authors should first use standard JSON Schema `title`/`description` and then use this version-pinned sidecar for context-sensitive phrasing. The metadata is **not Board-approved** and is not an alternative to the authoritative schema.

For finite choices, the sidecar provides **references to** `native.selector_value_enums`, `native.state_value_enums` and `native.field_datatypes` in the exact same version's capability mapping; it deliberately does **not** copy allowed-value lists. Tools must render supported choices as dropdowns with the native token serialized unchanged, and must fail closed on missing/inconsistent sources. In particular, Windows Registry `type` stores a Registry storage type (`dword`, `multi_string`, etc.) drawn from `state_value_enums.type`, whereas Registry `value` comparisons may use multiple primitive datatypes drawn from `field_datatypes.value`; the two fields cannot be collapsed or silently cast.

The context-specific `test.require`, `state.field.require`, `test.states_match` and `assessment.evaluate.all/any` descriptions are intentionally distinct. Additional languages, wording reviews and strict schema-metadata/option cross-validation are tracked in #244. This is presentation research, not a 0.4-A language stabilization decision.
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
