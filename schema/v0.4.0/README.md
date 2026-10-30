# SCAP-NG v0.4.0 — working schema draft

**Download/navigation update (2026-10-30):** Find the [full original 65-stream DRAFT, **internal layout prototype**, exact toolchains and focused sample Assessments](../../docs/releases/0.4.0-downloads-and-samples.md). This page also preserves dated schema-design/checkpoint evidence; older six-STIG artifact links and their counts do **not** identify the latest native authoring corpus. Select the exact pinned toolchain/schema set for validation, not an earlier design excerpt.

**Pre-alpha schema review candidate**, not an accepted release, OVAL Board ratification, or scanner conformance. Historical 0.3.0 schemas remain [archived](../../archive/0.3.0/README.md).

**Current candidate implementation (#260):** use the committed version-local
schemas and [candidate guide](../../docs/releases/0.4.0-rc.md). The direct
converter and native compiler interoperate on a bounded automated subset.
Opt-in draft compatibility admits exact NIWC catalog extensions and Test-level
`all_exist` with provenance warnings; it does not change schemas, field/record
existence, compiler or scanner contracts. Inline/shared Objects, Test-level
`capability`, canonical `require`, explicit existence/matching and
`and`/`or`/`one`/`xor` remain current. The isolated Variable function migration
schema is a draft expression contract, not a completed normative migration.
Older dated paragraphs below describe their historical review checkpoint;
current conversion counts and proof status come from the candidate ledger.

**2026-10-27 schema-first modernization reconciliation ([#255](https://github.com/vanderpol/scap-ng/issues/255)):** `file.hash` now proposes a required, enum-constrained Object `algorithm` **selector** rather than a scalar acquisition parameter, preserving OVAL multi-algorithm and `none satisfy` acquisition through the existing typed-array/Variable `value_match` grammar. The source-to-native hash spelling crosswalk is shared by the Object and State fields. This is a mapping/generated-contract candidate: current direct conversion remains explicitly inactive for original filehash58 multi-value cases, and scanner collection over the six-algorithm domain remains unproved. The [100-capability modernization audit](../../docs/audit/v04-modernization-schema-reconciliation-20261027.md) also records a separate existing mismatch between documented explicit datatype on arrays and current converter output. A strict common-schema datatype requirement has **not** been promoted ahead of the coordinated converter change, because doing so would invalidate currently source-proved Windows user-rights content.

**2026-10-24 schema-only review candidate:** Automated Tests use `require: {items_found: ..., items_satisfying: ..., fields: ...}` (or Item-presence-only `require: {items_found: ...}`). Fields with comparisons use `values_found`/`values_matching`; record wrappers with comparisons use `records_found`/`records_matching`. The single absence-only spelling is `{values_found: none}` for an individual field or `{records_found: none}` for a record wrapper, without matching counts, comparator, or unrelated attributes. Such absence overrides a shared field requirement; it cannot be authored through a duplicate inherited `field_requirement` pair. No separate `state`/`states`/`states_match` or scalar legacy shorthand. `evaluate` accepts `and`/`or`/`one`/`xor`. Inline and referenced shared Objects are both valid. The new absence-only schema rules are **pending owner diff review**; converter/compiler migration and scanner-level six-state proof are separate subsequent gates.

**[Earlier six-STIG 0.4.0 YAML/JSON samples and evidence](https://github.com/vanderpol/scap-ng/actions/runs/39677900589#artifacts)** passed October 21 checks against the *earlier schema*, not this correction. The [October 20 tagged samples](https://github.com/vanderpol/scap-ng/releases/tag/v0.4.0-six-stig-authoring-approved-20261020) remain immutable historical review assets. The earlier build covered 4,001 files, 2,958 Rule-choice links, and 172 exceptional source-exact Tests; those counts are historical evidence, **not** validation of this candidate.

The earlier 0.4-A research syntax and October 15 r3 source preview remain pinned **research inputs**, not current authoring dialects. No redundant inline Object `capability` is required. See [earlier Assessment examples](../../specification/examples/assessments.md), [canonical decision](../../research/assessment-simplification/compact-authoring-04/OWNER-0.4.0-CANONICAL-DECISION.md), and [validation gates](../../review/current/0.4.0-FINALIZATION-GATES.md); those documents have not yet been regenerated for this candidate.

Passing authoring schema/graph validation and 25,628 generic OVAL result comparisons does **not** establish the native executable .scapng compiler, capability-specific scanner execution or independent runtime conformance.

**Authoring release status (2026-10-21):** The linked October 20 six-STIG ZIP is the previously pinned authoring baseline and has not been silently replaced. The approved flat-Object/hybrid-YAML regeneration now has a passing 4,001-file six-STIG native-schema, exact-inverse, independent source-package and generic OVAL-result CI run. Executable compilation, scanner parity, and an official signed release remain separate outstanding gates. A flow-style YAML mapping (`{...}`) and its block-style equivalent parse to identical JSON, but removing a generic `select`/`collect` wrapper changes the JSON graph and requires versioned conversion.

## Shared authoring vocabulary (advisory preview)

The version-local [English authoring vocabulary](authoring-vocabulary.en.json) (research [#244](https://github.com/vanderpol/scap-ng/issues/244)) centralizes **display labels, questions and explanatory text** for editors, scanner GUIs and authoring agents. It does not alter any Assessment JSON/YAML grammar, evaluation results, capability semantics or native identifiers. Tool authors should first use standard JSON Schema `title`/`description` and then use this version-pinned sidecar for context-sensitive phrasing. The metadata is **not Board-approved** and is not an alternative to the authoritative schema.

For finite choices, the sidecar provides **references to** `native.selector_value_enums`, `native.state_value_enums` and `native.field_datatypes` in the exact same version's capability mapping; it deliberately does **not** copy allowed-value lists. Tools must render supported choices as dropdowns with the native token serialized unchanged, and must fail closed on missing/inconsistent sources. In particular, Windows Registry `type` stores a Registry storage type (`dword`, `multi_string`, etc.) drawn from `state_value_enums.type`, whereas Registry `value` comparisons may use multiple primitive datatypes drawn from `field_datatypes.value`; the two fields cannot be collapsed or silently cast.

The sidecar's labels are aligned to the current review-candidate Test, field, record and logical-operator keys. Its explanatory text remains advisory and pending owner review (#244).
## Draft Assessment grammar

- A single native authoring grammar: no separate `states` array or scalar Test `require` fallback.
- Test `require` uses explicit existence and match cardinalities: `require: {items_found: one_or_more, items_satisfying: every, fields: {owner_uid: {equals: 0, values_found: one_or_more, values_matching: every}}}`. Nested complete conditions use `and`/`or`/`one`/`xor`; inherited `field_requirement` scopes use the same `values_found`/`values_matching` pair for comparison-bearing fields.
- **Comparator-free absence:** `require: {items_found: one_or_more, items_satisfying: every, fields: {unlabeled: {values_found: none}}}` is the sole field-level absence form. Nested record absence is `record: {records_found: none}`; record-member absence is the same individual-field form. These reject `values_matching`, `records_matching`, `equals`, datatype, or legacy `require: none_exist` when no values/records may exist. `values_matching: none` remains a distinct, comparison-bearing requirement for *existing* values. These authoring checks do not make an absent field synonymous with an empty value, a collection error, or unknown evidence.
- Match cardinalities are always `none`, `exactly_one`, `one_or_more`, `every`. Test Item existence allows `none`, `exactly_one`, `one_or_more`, `may_be_absent`. **Owner-approved 2026-10-24 Test-only normalization ([#251](https://github.com/vanderpol/scap-ng/issues/251#issuecomment-6388735943)):** source `all_exist` may map to `items_found: one_or_more` under the versioned 0.4.0 collection contract with no synthetic `does_not_exist` Items and preserved collection error/unknown evidence. This is intentional normalization, not unrestricted OVAL equivalence: a complete mixed OVAL population of one existing and one nonexistent Item yields `all_exist=false` but `at_least_one_exists=true`. The shared converter admits only the proven pinned RHEL 9 source; original Test/Object IDs, versions, file/object hashes and normalization scope/reason remain in separate provenance. Incomplete/error/not-collected evidence must not be discarded to manufacture complete success. Field/record `every`, absence and comparisons are unchanged. See the [source-backed integration report](../../docs/audit/v04-owner-decisions-integration.md).
- Collected Items and projected Item reports cannot contain synthetic `status: does_not_exist` entries. A successfully collected empty set is `collection.status: complete` with no Item references. Collection-level `does_not_exist` diagnostics and absent field-value statuses are separate, not removed by this Item decision.
- **Near-term scanner/result gate:** `does_not_exist` Items are a scanner-produced collection artifact, not an authoring/content construct. After schema review, ensure scanner collection and result serialization do not fabricate missing Items; represent missing Items by absence from the collected set and verify empty, incomplete, and error outcomes. Preserve source OVAL provenance separately. Confirmed field/record absence is independently meaningful and requires collector evidence; missing, incomplete or error collection is not confirmed absence. No scanner/evaluator implementation or proof is claimed by this schema-only change.
- Both `object: {filepath: /etc/passwd}` and `object: shared-file-object` are valid collection forms.
- **Native Object selectors and acquisition parameters are direct Object fields.** For example `object: {mount_point: {equals: /home}}` or multiline `object` with `hive`, `key`, and `name`. Generic `object.select` and `object.collect` wrappers are removed in the owner-approved 0.4.0 grammar. Direct selector predicates SHALL NOT carry State/Item `require` or Organizational Input; filters, sets, and traversal retain distinct semantics. The separate native `windows.cmdlet` acquisition field named `select` remains valid under that capability only. Legacy `value` + `operation` Object selectors fail draft 0.4 validation. This is enforced by the full Assessment schema for native inline/shared Object `select` properties and the version-local shared schema.
- Exactly one comparison operation per scalar predicate; arrays, Variables and Organizational Input references retain explicit `value_match` and datatype requirements.
- Windows record and nested field requirements are distinct. Object Set filters use `include:` or `exclude:` on field-key predicates; nested filter groups use the same `and`/`or`/`one`/`xor` and `field_requirement` vocabulary, without legacy `all`/`any`/`odd` aliases.
- `evaluate`, `for_each`, typed Variable graphs, manual choices and collected Items/results do not acquire new semantics.

## Historical 0.4 authoring previews

The [interim RHEL 9 and Windows 11 authoring preview](https://github.com/vanderpol/scap-ng/actions/runs/38798029627/artifacts/12002887248) was validated against a **previous** 0.4 draft. It contains earlier automated/applicability YAML and source inversion evidence, but is **not** validated against the new cardinality vocabulary or approved for current reuse.

## Native generator and real-content evidence

The [version-local native 0.4 capability generator](../../tools/generate_capability_schema_v04.py) successfully emits JSON Schema draft contracts for **all 100 supported reviewed capability mappings** ([successful 100-capability CI](https://github.com/vanderpol/scap-ng/actions/runs/38759490558)). The frozen 0.3 generator remains unchanged. This proves schema generation, reference locality and selected native field-name checks, **not** acceptance of all real authored Tests.

The first generated-native deep audit exposed 541 rejected Tests. A [later six-anchor authoring schema gate](https://github.com/vanderpol/scap-ng/actions/runs/38770315633) passed **1,396 automated/applicability Assessments and 2,144 Test occurrences** against the previous draft, including documented source reconstructions and State-free normalizations. Those are historical source-lowering results, **not** validation of this revised schema. All 100 supported capability mapping snapshots were previously generated ([CI](https://github.com/vanderpol/scap-ng/actions/runs/38768460733)).
## Source provenance for constant Variables

The original Windows 11 / Windows Server 2025 OVAL userright selectors
reference a 45-value constant Variable. The source omits `var_check` and
`operation`. Under OVAL 5.12.3, those mean **all** and **equals**,
respectively. The 0.4 research migration therefore uses an explicit
array with `value_match: every`, **not** `exactly_one` (which would change truth
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

The [earlier six-anchor structural gate](https://github.com/vanderpol/scap-ng/actions/runs/38770315633) must be rerun after the converter is explicitly migrated to this vocabulary. Remaining independent gates: owner review of semantic boundary cases, source-reference OVAL parity, full authoring-to-package compiler integration, current-main converter regression [#226](https://github.com/vanderpol/scap-ng/issues/226), and intentional full 65-source release checkpoint. No SCAP-NG scanner exists; vendor execution conformance is later. Source-only Variable modules and debugging views remain unapproved [research #223](https://github.com/vanderpol/scap-ng/issues/223).
See [0.4 scope and release gates](../../research/assessment-simplification/compact-authoring-04/0.4-SCOPE-AND-RELEASE-GATES.md), [issue #227](https://github.com/vanderpol/scap-ng/issues/227) and [variable research #223](https://github.com/vanderpol/scap-ng/issues/223).
