# Owner decision: SCAP-NG 0.4.0 canonical authoring (2026-10-20)

**Accepted direction for 0.4.0 (#227, #232, #239, #246).** The A/B/C/D labels were internal research alternatives. They are not user-visible product versions.

1. Keep the OVAL-aligned names **Assessment, Test, Object, Variable and Item**. Use `object` for a source declaration, `require` for Test predicates and population requirements, `evaluate` for composition of Test results.
2. Test `capability` determines an *inline* Object's capability. Omit the redundant inline `object.capability` from authored 0.4.0. Reject a contradictory explicit duplicate. Standalone or shared Objects retain their own explicit capability.
3. Adopt `require: {items: one_or_more, all_items_must: ...}` for **source-proven** one-or-more/all-match Tests, and `items: may_be_absent` when that is the original existence requirement. Existence and matching are distinct; zero Items must not accidentally pass a one-or-more requirement. Inside the predicate tree, retain independent field/record cardinality and exact `and` / `or` grouping. Do not collapse a per-Item match to a substring check.
4. Do not silently rewrite uncommon existence/match combinations, error/unknown/partial-result boundaries, alternative State semantics or nested record cardinality. A clearly marked explicit requirement fallback remains necessary until independently verified replacements exist; it is *not* a separate release or grammar. Every converted Assessment must roundtrip to the preserved source.
5. **YAML presentation (owner update 2026-10-21):** Prefer hybrid formatting: one-line flow mappings for short, simple predicates or complete conditions; multiline block style for long or complex content. Authors MAY choose fully compact or expanded YAML, since both must parse to identical JSON. Editor formatting must not alter semantics or unexpectedly overwrite an author's layout. This is separate from the Object schema change.
6. Regenerate all **six** benchmark authoring sets in YAML and JSON from the verified, pinned October 15 source. Require schema, source-reconstruction and reference-closure regression gates. No scanner parity claim from a source roundtrip.
7. The browser editor SHALL show *0.4.0* rather than *0.4-A*, explain `object` as collection source and `require` as expectations. It SHALL load and export the actual 0.4.0 structure; older fixtures must be explicitly identified as legacy or migrated, never silently re-saved with different semantics.

**Release gate:** this decision authorizes implementation but does not constitute evidence that all six generated benchmarks, native JSON Schema, YAML editor export, compiler, or scanner pass. Publication of a package as validated requires checking each gate independently. Historical research remains auditable but shall not be advertised as a competing specification.

## 2026-10-21 field requirement naming — owner-approved direction (#248 #239)

- **Use one `field_requirement` key at Test, logical-group, complete-condition, and individual-field scope**, rather than a local generic `require`, `override_fields_requirement`, or restored `state` wrapper. At Test scope place it inside `require` alongside `items`. An upper-level `field_requirement` applies to **all descendant fields within its scope**, including all branches of a nested logical operator, unless a nearer `field_requirement` is explicitly declared. A condition-level declaration overrides the inherited requirement for **all fields of that condition** without changing sibling conditions; an individual field's declaration overrides it **for that field only**. Effective precedence is Test → enclosing logical group(s) → complete condition → individual field. The closest explicitly defined field requirement wins; omission never creates an implicit default. This inheritance rule SHALL appear in machine-readable JSON Schema descriptions for each applicable scope, not merely in example documentation.
- `require.items` is the distinct collected-Item population requirement; `field_requirement` governs only field presence and matching. `and/or/one/xor` are logical operators between complete conditions, not per-Item matching quantifiers.
- This authoring vocabulary is accepted **as design direction**, not an assertion of currently implemented schema support, lossless source converter parity, scanner execution, or official v0.4.0 package readiness. Promote it only through the native version-local schema, source-aware reversible migration, JSON/YAML and independent OVAL 5.12.3 six-state/record/variable tests. Preserve existing released 0.4 authoring samples and historical source forms until those gates pass.
- See the [field requirement scope review](../../../review/current/0.4.0-FIELD-REQUIREMENT-SCOPE.md) and [finalization gates](../../../review/current/0.4.0-FINALIZATION-GATES.md).

## 2026-10-21 field-group AND semantics — owner-confirmed (#248 #239)

- Ordinary `fields:` mapping is **one original OVAL State-sized complete condition**. **All distinct field predicates in that mapping must match (AND)** for the condition to match. This is a **documented grammar rule**, not a hidden runtime fallback or per-field `field_requirement` setting. The 5.12.3 OVAL `StateType.operator` default is `AND`.
- A surrounding `or:` joins **complete conditions/States**, corresponding to the Test `state_operator=OR`, and does **not** mean the fields inside either condition are ORed. `field_requirement` independently governs existence/matching of **each** field at the declared scope, including nearer overrides; it never changes AND into OR.
- Rare source State `operator=OR/ONE/XOR` cases **must** remain representable explicitly, without changing the ordinary `fields:` case. Investigate the existing research-only `fields_operator` + ordered `fields` form where necessary for repeat field names, and independently test the OVAL truth tables and six-state/error behavior before normative schema promotion. Never flatten multiple original States into one fields map.
- Original XML evidence: [2026-10-21 source operator audit](../../../review/current/0.4.0-BOOLEAN-OPERATORS-VS-QUANTIFIERS.md) recorded 817 original States across the pinned NIWC Windows 11 and OVAL Self-Assertion samples, including 182 multi-field States and **zero** States with non-default field operators; sample statistics are not a universal compatibility limit. Source-backed proof does not substitute for executable scanner semantics.

## 2026-10-21 Object authoring grammar decision — drop `select` and `collect`

**Owner direction for the single canonical 0.4.0 schema**, not merely a style toggle: **remove generic `object.select` and `object.collect` containers**. Place capability-specific Object selector fields and acquisition parameters directly under `object`. Preserve explicitly named `filters`, `set`, traversal and behavioral structures where required, and preserve every native OVAL-equivalent selection and acquisition constraint in the capability registry and compiled IR.

```yaml
# Single Object selector; research syntax until versioned schemas are migrated
capability: linux.partition
object: {mount_point: {equals: /home}}

# Multiple selectors, preserving registry hive/key/name
capability: windows.registry
object:
  hive: {equals: local_machine}
  key: {equals: 'SOFTWARE\Microsoft\Windows NT\CurrentVersion'}
  name: {equals: CurrentVersion}

# Acquisition parameters likewise become direct Object fields
capability: independent.shellcommand
object:
  shell: powershell
  command: (Get-PnpDevice -class bluetooth -status OK).class
  error_if_exit_status_not_0: false
  error_if_stderr_exists: false
```

The native Windows cmdlet Object has a capability-specific acquisition field itself named `select` (PowerShell result-property selection). That field is **not** a reintroduced generic `object.select` container and must be validated unambiguously under its capability. The old generic wrappers cannot be permitted as competing native synonyms. Existing source imports must be migrated explicitly with versioned provenance, not guessed from nesting or renamed silently.

**Implementation acceptance gates, not yet claimed as completed:** audit all supported capability selector/parameter/control-name collisions; update the version-local common and generated capability schemas, source converter, inverse ledger, native compiler, tests, Studio, and full six-STIG YAML/JSON packages; prove source reconstruction, set/filter/variable behavior, and relevant OVAL six-state outcomes. The current published 0.4.0 archives remain unchanged until a new verified release. This decision authorizes the schema change but does **not** imply that the current schema already accepts it.
