# Current SCAP-NG design — authoritative authoring checkpoint

Owner reconfirmation: 2026-09-30. Read this file before selecting a generator, preparing examples, or claiming review readiness. Earlier conversation summaries, generated trees and superseded design prose do not override these decisions. Update this record when the owner changes a decision.

## Settled owner direction

- Architecture: **Benchmark → Rule → Assessment** for compliance and vulnerability content. There is no separate Policy object/file. Rule owns requirement/assertion metadata and named Assessment selections/defaults; Assessment owns the evaluation method.
- Benchmark membership enables every Rule. Publisher Profiles are subtractive only: they MAY disable Rules and SHALL NOT expose `enabled_rules` or re-enable ancestor-disabled Rules. A Profile SHALL expose `disabled_rules`, including `[]` when it disables no additional Rules. Empty lists preserve the supported-data-elements convention and never re-enable ancestor-disabled Rules. External Tailoring MAY enable/disable existing Benchmark Rules, including restoring a publisher-disabled Rule, choose among existing named Rule Assessment selections. It SHALL NOT replace bindings or implementations; Organizational Input cannot select Tests. See `specification/policy/profiles-and-tailoring.md`; source Profile XML description wrappers SHALL NOT appear in native descriptions.
- Authored Assessment selections use explicit YAML paths relative to the referring Rule. Preserve selector identity, aliases and default-versus-explicit provenance. Compiled resolution uses explicit manifest bindings; never guess filenames.
- Compiled SCAP-NG packages use a manifest-authoritative logical object graph. The current preferred container is deterministic ZIP with the `.scapng` extension; archive paths are storage locations only, never semantic identity. Packaged Benchmark/Rule/applicability objects reference logical IDs, and scanners resolve those IDs through the manifest. The manifest SHALL NOT duplicate Rule selector/default policy logic. See [package container and manifest decision](package-container-and-manifest.md).
- Native Assessment capabilities are a clean break from OVAL/XCCDF schema structure. Preserve required semantics, not legacy XML names, hidden defaults, type hierarchies, deprecated values, or serialization workarounds. Shared native comparison, quantifier, existence, Set/filter and file traversal primitives SHALL be reused across capabilities. The first stabilized slice is `unix.file`; see [native capability clean-break design](native-capability-clean-break.md).
- Native automated evaluation nodes are **Tests**. Use `tests`, `test_title`, `test-` IDs and explicit Test references.
- Native resource acquisition/selection nodes are **Objects**. **Collection** refers to the runtime act of evaluating an Object and producing Items plus collection status/completeness. Named/reusable Objects remain first-class where a capability actually selects/acquires system resources. Objects are **not** a mandatory wrapper around every Test source: a clean native capability MAY consume another first-class authored node directly when that is the natural semantic source. The first approved example is `variable.value`, whose Test references a named Variable directly instead of reproducing OVAL's `variable_object -> var_ref` indirection.
- Assessment source presentation SHOULD place metadata first, then `objects` → `variables` → `states` → `tests` → `evaluate`, omitting absent sections. Automated Assessments do not require empty `objects` or `states` sections when the selected capability has no such nodes; This is a readability/output convention, not execution order: mapping key order SHALL NOT affect reference resolution; forward references remain valid. Sequence order retains its meaning where defined, such as function arguments. Our generators consistently follow this recommendation; `tools/check_current_authoring_contract.py` checks generated review presentation in CI. An order warning does not make an otherwise valid authored Assessment semantically invalid.
- Variables SHALL support **both** references to existing named Objects and Collections embedded privately within the Variable. This is an agreed working-design requirement. Formal Board ratification is tracked separately; it does not remove either form from our working model.
- Converted source SHALL preserve meaningful named Object boundaries and Variable dependencies. Do not duplicate a shared source Object inline at every use. Embedded Objects are supported for native authoring; they SHALL NOT be used to erase shared source references during lossless conversion.
- Variables can consume Object fields or other Variables. Named intermediates and the complete graph through sets/filter States/functions must survive conversion. Source identity must remain in provenance so distinct source nodes are not merged merely because payloads match.
- Native Assessments have no `deprecated` attribute. Effectively deprecated source Tests are blockers; they do not become native runtime flags.
- Test, Object, and State/predicate capability/type remain independently declared where those nodes exist. An Object is a first-class reusable selection/acquisition node and SHALL retain its own capability when consumed by a Test or Variable. Tests declare their evaluation capability; States/predicates retain their comparison capability. A capability defines the Test's source kind (for example `object` or direct `variable`); validators SHALL resolve that source explicitly and reject incompatible or missing bindings rather than inventing an intermediate Object, inheriting a capability, or silently coercing declarations. Embedded/private resource selections likewise retain their own capability.
- **Migration and normalization evidence is separate from native NG content.** Native Benchmark/Rule/Assessment/Object source SHALL NOT embed converter diagnostics, skipped-source-defect records, legacy OVAL graph dumps, parity traces, or repository-normalizer lineage merely for migration traceability. Conversion/normalization tools SHALL emit those details into separate evidence/report trees that may reference native logical IDs. Native content SHALL remain executable without that evidence, and the compiler SHALL NOT package migration/normalization evidence by default.
- Pre-alpha: publish completed, appropriately tested work directly to `main` without routine permission requests. The owner authorized current-design full RHEL9 review generation on 2026-09-30. Historical publishing workflows remain held; use the new source-driven full review entry point.
- Conversion, normalization, audit, parity, source-defect, and legacy-node evidence SHALL remain outside the native Benchmark/Rule/Assessment/Object content graph. Evidence MAY reference native logical IDs, but native content SHALL NOT depend on migration evidence for execution. The compiler SHALL NOT package detailed conversion/normalizer evidence by default. Native fallback content contains only the valid resulting Assessment choices; exact source errors and skipped legacy paths belong in separate evidence reports.

Owner direction, 2026-09-30: run a complete round-trip regression of the pinned content corpus after the element-name and behavior changes. Production NIWC Current migration evidence and OVAL Self-Assertion language evidence remain separate. The broad corpus runner now defaults to the current named Object/Test graph; historical mode requires an explicit switch. Do not use an older-layout green run as current-design validation.

## Converter delivery and stability requirement

Owner direction, 2026-09-30: once conversion reaches stability, provide the exact
maintained converter and instructions for running it on the owner's Windows
development computer. Windows portability is an implementation requirement now,
not a late packaging task. The converter is the executable expression of the
working NG design; source syntax, documented semantics and regression fixtures
must evolve together. One documented entry point must reproduce the reviewed
output from pinned original SCAP input. See
[converter stability and Windows delivery](converter-stability-and-windows.md).

## Open or not yet implemented

- Exact Rule choice field names (`assessment_choices`, `default_assessment_choice`) are review proposals.
- Complete `Object/State vocabulary migration, including the final item/state quantifier syntax, is unfinished.
- Named Object graph conversion and reverse consumption now have a tested prototype (`collection_graph=True`), including source identity and Variable references. It is integrated into the complete pinned RHEL9 Rule/Benchmark research renderer; compiled package/signature and broader consumer integration remain unfinished. Object capability is retained on the Object itself; the earlier Variable-side `collection_capabilities` prototype is superseded and SHALL NOT be emitted.
- Formal Board review of embedded Objects and colocated Filters remains pending. Both named-reference and embedded-Object Variable forms are required in the working design, not optional pending implementation choices.
- Full runtime equivalence is unproven. Round-trip and source-reference checks alone do not establish evaluator equivalence.

## Object/dataflow checkpoint

[Source-generated sample](../review/collection-dataflow-source-sample/README.md):
selected Assessment output from 25 RHEL 9 Rules, converted from the pinned
original ZIP. This is a tested dataflow prototype, not a full Benchmark compiler.
Source graph sharing, Variable chains and private embedded native-authoring
Collections have regression coverage. All 42 Variable-bearing RHEL 9 cases
compare equal through the new graph/reverse path; 23 sample automated outputs
also regenerate omni-schema-valid OVAL. Runtime conformance, complete Rule/Profile
rendering were outside this slice. Windows/Linux graph and local-ZIP regressions subsequently passed; full-source review evidence is tracked separately below.

## Full RHEL9 checkpoint

[Current full review](../review/rhel9-current-full/README.md) uses the pinned original package, not old rendered YAML: 445 Rules, 11 Profiles, 418 automated and 445 manual Assessments, 18 source-driven applicability conditions. All 4,895 Rule/Profile selection comparisons match. Automated/applicability definition round trips and pinned omni-schema checks pass. Relative Rule paths, source selectors/defaults, shared manual questionnaire aliases, grouping and native presentation/cleanliness are checked. The exact research CLI is `tools/scap_upconvert_v003/convert_full_review.py`; Windows/Linux full-package CI evidence is recorded with the review. This is not finalized grammar, compiled packaging or runtime conformance.

## Current artifact status

[Tailoring worked examples](../examples/tailoring-all-options/README.md) cover the documented mutation surface, parent layering, provenance, publisher Profile values, named Assessment selections and separate Organizational Input. They include a real RHEL9 binding and resolved-policy snapshots. New detailed source field shapes remain proposals; the small resolver exercises the examples and is not a production assessor or finalized schema implementation.

Owner direction, 2026-09-30: Tailoring SHALL have an obvious human-readable `purpose` and distinct provenance locations for creator, modifier and authorizer, with dates, organizational ownership and authorization reference/status. Keep these near the top of examples and retain unset draft fields explicitly as null. Preserve them in resolved policy provenance without treating metadata as execution-changing data.

`review/test-vocabulary-slice` is **incomplete**, despite its passing narrow naming/path tests. It still contains older `collect`/`object_title`/capability duplication and has no Variable/Object dependency example. It SHALL NOT be described as a completed current-design slice.

`source/split-rule-assessment/rhel9-full` is historical generated baseline data, not current native syntax. `source/split-policy-assessment/rhel9-full` is a superseded architecture experiment. Neither tree is an automatic source of current authoring decisions.

## Assessment evaluator semantics checkpoint — 2026-10-01

The durable runtime semantic contract is now maintained in
[assessment-evaluation-semantics.md](assessment-evaluation-semantics.md).
Confirmed OVAL-derived behavior belongs there, with focused conformance tests;
JSON Schema is a structural projection and SHALL NOT be the sole source for
runtime/evaluation semantics. Ambiguous legacy behavior remains explicitly
unresolved rather than being guessed into the native model.

## Required working procedure

1. Read this record and repository instructions. Resolve conflicts in favor of the latest explicit owner instruction, update this record, and mark older prose superseded before generating examples.
2. Inspect the selected script's input/output contract and consumers. Use pinned original SCAP input and faithful IR for lossless changes; do not normalize a stale rendered tree and call it a fresh conversion.
3. Add focused regressions for the actual feature under review. Variable work must include named Object extraction, shared references, variable-to-variable dependencies, sets/filters and negative references/cycles. Do not use a no-variable slice as evidence for variable support.
4. Run `tools/check_current_authoring_contract.py` on proposed review output. Resolve reported violations before calling that output ready. A blocked report is a valid checkpoint, not a pass.
5. Record source pin, exact commands, results, unresolved blockers and coverage limits. Publish coherent checkpoints on main. Explain narrowly what is proved.
6. Before reviewer handoff, compare both generator output and consumer behavior against every settled decision above. Run a full round trip after the accepted source grammar is implemented end-to-end.

Provenance: **Evidence/Audit** of owner decisions and observed regressions; no external redesign proposal supersedes the established model.

## Complete current-design corpus regression

[2026-09-30 checkpoint](../evidence/full-current-roundtrip-2026-09-30/README.md): all 65 pinned NIWC Current packages accounted for, 11,628 of 11,973 definition occurrences comparator-equal; 204 deprecated-Test, 132 publisher-extension and 9 confirmed source type-binding blockers. All regenerated package XSD and source-relative Schematron steps pass. Separate Self-Assertion has 165 of 167 equal with only 2 expected deprecated-Test blockers. Fresh full RHEL9 and current contract suites pass on Windows/Linux. The run fixed the historical-mode coverage gap, renamed Object terminology documentation guard, lexical QName diagnostic comparison and masked Schematron pipeline errors. This is conversion evidence, not target runtime equivalence; the complete census remains red for the explicitly documented source type errors.


## OVAL-aligned vocabulary checkpoint — 2026-10-01

The authoritative authored Assessment vocabulary is now **Assessment, Test, Object,
State, Variable, and Item** where the underlying semantics remain aligned with
OVAL. `evaluate` is the intentional native replacement for OVAL
`criteria/criterion`, and typed `*_title` fields intentionally replace generic
OVAL `comment` metadata.

`Collection` is not an authored synonym for Object. It describes runtime
execution of an Object. Older iteration-003 prose, generated examples, tool
variable names, or evidence directories that use Collection as the authored
OVAL-Object concept are historical implementation terminology and SHALL NOT
override this decision.

Before capability schemas become a baseline, generators, validators, examples,
and current-design regression tooling SHALL either emit/consume the OVAL-aligned
authored vocabulary or be explicitly labeled as legacy migration internals.

## Tailoring Parameter boundary correction — 2026-10-01 owner decision recovered 2026-10-02

The earlier permission for Tailoring to refine publisher Parameter values is superseded. Tailoring SHALL NOT override those values. If the publisher requires X and an organization chooses Y, that is a different policy requiring distinct policy identity; Organizational Input supplies only delegated values. Tailoring MAY still select an existing publisher-provided Assessment choice, including manual checking when automation poses operational risk, and enable/disable existing Rules. See specification/policy/profiles-and-tailoring.md and specification/policy/parameters-and-organizational-input.md. The worked resolver and fixtures now reject Parameter mutations in every Tailoring layer.

## Informational policy disposition — retained working control

Owner direction, 2026-10-01: retain Rule `role` for informational/reporting-only use until an adequate alternative is agreed. It belongs to Rule policy, not the Assessment technical truth domain. Assessment-native informational and eventual role replacement remain research/Board topics; earlier replacement proposals do not authorize removal. See specification/results/results.md.
