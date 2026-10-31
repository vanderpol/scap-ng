# SCAP-NG 0.4.0 editor defaults ↔ pinned OVAL 5.12.3 crosswalk

**Status:** Initial audit; **not yet a definitive owner-approved default catalog**. Created 2026-10-31 for owner review as part of [Decisions 4 and 7](v04-owner-final-decisions-20261031.md) and [#255](https://github.com/vanderpol/scap-ng/issues/255).

The 0.4.0 authoring contract explicitly materializes applicable editor choices into saved YAML. A graphical editor may hide **only an explicitly serialized value** that equals its documented authoring default. JSON Schema `default` is a UI suggestion, not a validation insertion rule, conversion repair, or scanner runtime fallback.

The pinned source is `third_party/scap-1.4-schemas/oval_5.12.3/` in this repository. Across the 11 pinned OVAL definitions XSDs carrying defaults, an initial scan found **204 `default="..."` attribute declarations** (not 204 distinct knobs or 204 NG defaults). Most are specialized and many refer to capabilities outside 0.4.0. A per-capability mapping review remains required.

## 1. Existing explicit editor defaults

These are the complete `default` plus `x-scap-ng-authoring.hide_when_default: true` annotations in the current draft schema as of this audit, not a claim that the *desired* list is complete.

| NG authored location | Current editor default | OVAL 5.12.3 counterpart | Equivalence/status |
|---|---|---|---|
| `Test.reported_elements` | `all` | No exact source `reported_elements` control. OVAL has different source/results representation. | **NG-specific** reporting choice; hidden in editor only after explicit saved YAML. |
| `Test.require.items_found` | `one_or_more` | `oval-def:TestType/@check_existence`: default `at_least_one_exists`. | **Aligned** for the ordinary no-synthetic-Items case; OVAL `all_exist` requires distinct source-evidence review. |
| `Test.require.items_satisfying` | `every` | `oval-def:TestType/@check`: **required attribute; no default**. | **NG editor preference, not an OVAL default.** Do not fill a missing/invalid OVAL source `check` from this suggestion. |
| `Test.require.field_requirement.values_found` | `one_or_more` | `EntityStateSimpleBaseType/@check_existence`: default `at_least_one_exists` (same for complex state entities). | **Aligned** as the common field-presence choice, subject to correct item/record semantics. |
| `Test.require.field_requirement.values_matching` | `every` | `EntityState*BaseType/@entity_check`: default `all`. | **Aligned** as the common field match choice. A field with an explicit override must write its complete pair. |

Schema references: `schema/v0.4.0/assessment.schema.json` (`reported_elements`) and `schema/v0.4.0/assessment-language.schema.json` (`canonical_all_items_requirement`). OVAL XSD: `oval-definitions-schema.xsd`, `TestType` and `EntityState*BaseType`.

## 2. High-value candidates — **not yet approved as hidden defaults**

| NG control / UX action | OVAL 5.12.3 source default | Proposed editor behavior | Review hazard |
|---|---|---|---|
| Object selector comparison operator | Entity `@operation="equals"` by default. | Offer `equals` first and always serialize `{equals: ...}`. | NG encodes the operation as a YAML key, not a separate `operation` property. No hidden runtime operation. |
| Field / Object expected datatype | Entity `@datatype="string"` by default. | Derive from capability contract, typed operator, YAML scalar, Variable or Input; allow explicit compatible datatype. | **Not** a fixed NG string default. Quoted versions and numeric registry values must retain their actual semantic type. |
| Variable comparison `value_match` | `@var_check` omitted is processed as `all` under the pinned OVAL XSD text. | Consider proposing `every` where a Variable or array comparison actually requires `value_match`, and serialize it. | Source-derived `var_check` may be explicit and non-default; never overwrite it. No implicit array behavior. |
| File Object `filesystem` scope | `FileBehaviors/@recurse_file_system="all"` in OVAL; maps `defined` to NG `same`. | For **new NG authoring**, consider suggesting `local` and explicitly serializing it. | **Intentional difference** from OVAL source default `all`: conversion of omitted OVAL scope must preserve `all` unless owner explicitly approves a documented non-lossless normalization. |
| File recursion off | `FileBehaviors/@recurse_direction="none"`. | Editor can initially show “No recursion”; do **not** invent a NG `recurse_direction: none` property. | NG currently models traversal as an optional nested construct; omitting traversal and explicitly specifying none are not the same serialization pattern. Review whether this satisfies the owner’s no-hidden-behavior policy. |
| File traversal type (`traversal.recurse`) | `FileBehaviors/@recurse="symlinks and directories"` for OVAL independent/Unix; **`recurse="directories"` for Windows**. | If the author enables recursion, offer `symlinks_and_directories` for Unix or `directories` for Windows as the source-aligned suggestion, with the selected value explicit in YAML. | This is **not** `recurse_file_system=all`. The OVAL platform defaults differ; do not accidentally follow Windows junctions by default. A default traversal type is inert while `recurse_direction=none`. |
| File traversal maximum depth | `FileBehaviors/@max_depth="-1"` (unbounded), paired with default recursion off. | When traversal is actually enabled, use `max_depth: unlimited` for unbounded traversal; nonnegative integers represent bounded depth. | Owner approved `unlimited` 2026-10-31; `null` and `-1` are rejected in NG 0.4. Omit traversal entirely when recursion is off. |
| Multi-State logical combination | `oval-def:TestType/@state_operator="AND"`. | In a guided multi-condition editor, start with `and`; always serialize the `and` key. | The operator is part of the expression structure; do not imply a default where multi-state correlation is not faithful. |
| Set union / filter exclusion | `SetType/@set_operator="UNION"`; `Filter/@action="exclude"`. | Consider first-choice editor controls; write the selected NG `union` and `exclude` structure explicitly. | OVAL default has meaning only when Set/Filter exists; do not create a Set/Filter to manufacture a default. |
| Shellcommand error policy | `error_if_exit_status_not_0=false`, `error_if_stderr_exists=false` in the independent XSD. | Review capability-specific controls and choose safe initial values if these flags remain in 0.4. | A `false` choice can suppress diagnostic failures; source intent and scanner evaluation must be explicit. |

## 3. Rules for source conversion and editor implementation

1. **No implicit scanner defaults:** YAML output shall include each applicable authoring choice. Omitted/invalid source values do not become valid by accepting a JSON Schema `default` annotation.
2. **Track source origin:** Record whether a value came from an explicit OVAL attribute, an XSD/Schematron omission default, a deterministic typed contract, an owner-approved NG normalization, or a new-authoring editor suggestion.
3. **Do not confuse three values:** `source_oval_default`, `editor_suggested_default`, and `serialized_ng_value` are distinct. Where they differ, add a conversion note and source-exact regression.
4. **UI affordance:** “Show all fields” reveals the actual serialized YAML state. “Hide defaults” hides only values verified present and equal to the schema metadata. Non-default overrides remain visible. A user can alter a proposed value before save.
5. **Scope:** A field-level override inherits nothing unspecified; full paired `values_found` and `values_matching` remains required when overriding the Test/group baseline.
6. **Default metadata format proposal:** Retain standard JSON Schema `default` and `x-scap-ng-authoring: {group, hide_when_default}`. Add a separate source crosswalk annotation (e.g. `x-scap-ng-oval-crosswalk`) with source XSD/type/attribute, omitted-source value, semantic status (`aligned`, `ng_only`, `changed`, `conditional`), and conversion/provenance rule. Do not overload JSON Schema `default` with OVAL metadata.
7. **Audit breadth:** For each of the 100 supported native capability mappings, resolve relevant source XSD default attributes and whether corresponding NG controls are present, inferred, renamed, absent, or unsupported. The 204 raw declarations are the **search inventory**, not the editor defaults list.

### File recursion is four separate controls, not one `all` default

| Source OVAL `FileBehaviors` | Default in pinned XSD | Current NG 0.4 representation |
|---|---|---|
| `recurse_direction` | `none` | No `traversal` object means no recursive traversal; `down` is represented by an authored `traversal`; deprecated `up` is unsupported. |
| `recurse` | `symlinks and directories` (independent/Unix); `directories` (Windows) | `traversal.recurse: symlinks_and_directories` or `traversal.recurse: directories` respectively, only when traversal is enabled. Windows can explicitly request junction recursion, but does not do so by default. |
| `max_depth` | `-1` | `traversal.max_depth: unlimited` means unbounded when enabled. |
| `recurse_file_system` | `all` | `filesystem: all`, or `filesystem: local`, or `filesystem: same` for OVAL `defined`; search scope is independent of the recursion switch. |

The source XSD itself recommends `recurse_file_system=local` for most content *despite* its omission default of `all`. This supports a **candidate new-authoring suggestion** of local, but **not** a blanket change to source-conversion equivalence. The editor must never conflate source-effective `all` with the `recurse` traversal choice, or treat `all` as an instruction to recursively search. The pinned Windows `FileBehaviors` XSD defaults `recurse=directories`, **not** `junctions and directories`; a converter that follows junctions on an omitted Windows `recurse` attribute silently changes the source search.

## 4. Owner decisions still needed before finalizing

- Should the editor **hide** `items_satisfying: every` once serialized, even though OVAL Test `check` has no default? (Already annotated as a suggested NG default; this question is about hiding, not OVAL equivalence.)
- For new file authoring, should `filesystem: local` be the editor suggestion while the converter preserves omitted OVAL `recurse_file_system=all` as `filesystem: all`? This is the safest source-preserving split, but it needs an explicit owner decision.
- Which conditional or capability-specific defaults beyond the five existing annotations are worth hiding in the UI? The candidate table is for review, not automatic schema activation.

## Primary pinned source anchors

- `oval-definitions-schema.xsd`: `TestType` defaults `check_existence=at_least_one_exists` and `state_operator=AND`, while `check` is mandatory (around lines 354–378); `SetType`, Filter and `StateType` operators (around 454–500); Entity `datatype=string`, `operation=equals`, `var_check` implicit `all` (around 1375–1405); Entity State `entity_check=all` and `check_existence=at_least_one_exists` (around 1598–1630).
- `independent-definitions-schema.xsd`: `FileBehaviors` defaults `max_depth=-1`, `recurse=symlinks and directories`, `recurse_direction=none`, `recurse_file_system=all`, and separately recommends filesystem `local` (around 2878–2936); shellcommand error controls (around 1159–1168).
- `windows-definitions-schema.xsd`: `FileBehaviors` defaults `max_depth=-1`, `recurse=directories`, `recurse_direction=none`, `recurse_file_system=all` (around 1823–1886); junction recursion requires an explicit `recurse` selection.
- `schema/v0.4.0/capability-common.schema.json`: `filesystem_scope` allows `all/local/same`, `file_traversal_base` uses `unlimited` for unbounded depth and no authored upward traversal.

**Release gate:** Complete and approve this crosswalk, update version-local schema metadata/fixtures, then regenerate authoring gallery with a warning report for any default whose conversion is not source-equivalent. Do not silently change the pinned 65-benchmark evidence archive.
