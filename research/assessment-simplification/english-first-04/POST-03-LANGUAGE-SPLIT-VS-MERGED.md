# Post-0.3 Assessment language: review and split-vs-merged decision

**17 October 2026. Research recommendation, not Board approval or promotion into the normative 0.4 schema.**

## What changed since the 0.3 Board readability checkpoint

User feedback described the 0.3 Board reception as a failure to make Assessment content sufficiently understandable. The GitHub review page does **not** record a formal Board ratification/rejection vote; this is the owner's qualitative assessment, not a claim of formal Board action.

| Topic | Released 0.3 authoring | 0.4 working draft | Latest English-first research |
| --- | --- | --- | --- |
| State comparison | Separate `field`, `value`, `operation`/`match` fields | Observed field as key, e.g. `owner_uid: {equals: 0, require: ...}` | Keep field-as-key, native comparator names (`equals`, `case_insensitive_equals`, etc.) |
| Object selection | Selector `value` + `operation` in converted examples | Comparison-as-key selector, e.g. `directory: {equals: /home}` | Retain comparison-as-key; `where` separates selection from the Test expectation |
| Test Item existence and matching | `existence: one_or_more` + `match: all` | Explicit `require` with combined cardinality labels in the draft | Separate `require.items` and `require.match`, see decision below |
| Whole State / field logic | State arrays/OVAL-derived `check` structure | Explicit Boolean State and field expressions in research overlay | Structural `states.and/or` and `fields.and/or`, not a generic `scope` wrapper |
| Windows nested records | Record and record-field requirements distinguished | Distinction preserved | `records` and local `match` within record clause; outer `states.or` never cascades into records |
| Field presence | Scoped OVAL-like field existence requirements | Test/State-level shared-field requirement prototype | **Unresolved**: optional, absent and inherited field rules still need one clear authoring design |
| Control/dataflow | `evaluate`, `for_each`, shared resources, Variables | Preserved | Preserved, not simplified by renaming |

0.3 remains published unchanged. The base `schema/v0.4.0/` is an independent pre-alpha working draft; **the latest `require.items` / `require.match` syntax is still research**, not its adopted schema. Six-STIG structural reconstruction is not proof of six-state scanner/evidence parity.

## A vs B: one real RHEL 9 requirement

**A: split Item existence from matching — PREFERRED**

```yaml
require:
  items: at_least_one
  match: all
  mount_options:
    at_least_one_value_equals: nosuid
```

**B: merged long-English clause — NOT PREFERRED**

```yaml
require:
  at_least_one_exists_and_all_match:
    mount_options:
      at_least_one_value_equals: nosuid
```

Both encode one real source requirement: at least one selected partition exists, *all* selected partitions must satisfy the field predicate, and *at least one value* of each multi-valued `mount_options` must equal `nosuid`. Neither can replace `at_least_one_value_equals` with ordinary `equals` without checking operand cardinality.

## Harder cases decide the outcome

| Required meaning | Split | Merged |
| --- | --- | --- |
| At least one Item exists and all Items match | `items: at_least_one` + `match: all` | `at_least_one_exists_and_all_match` |
| At least one Item exists and one or more Items match | `items: at_least_one` + `match: at_least_one` | `at_least_one_exists_and_at_least_one_matches` |
| At least one Item exists and exactly one matches | `items: at_least_one` + `match: exactly_one` | `at_least_one_exists_and_exactly_one_matches` |
| Exactly one Item exists (not a matching predicate) | `items: exactly_one` only | `exactly_one_exists` |
| Items optional, but all present Items must match | `items: if_present` + `match: all` | `if_present_all_match` |
| All observed Items must avoid a forbidden value | `items: if_present` + `match: none` | `if_present_none_match` |

**Record example:**

```yaml
require:
  items: at_least_one
  match: all
  states:
    or:
      - result:
          records: at_least_one
          match: all
          domainrole: {equals: '1'}
      - result:
          records: at_least_one
          match: all
          domainrole: {equals: '3'}
```

Here the two visible axes repeat naturally inside record alternatives. A merged label at the top and another merged label inside records does **not** eliminate the distinction between complete alternative States and nested record predicates. The above source-backed shape is from Windows 11 SV-253495; not a proof that `domainrole: {in: ['1','3']}` is equivalent (mixed records are a counterexample).

## Quantitative evidence from the six-STIG proof

- Pinned source comprises **872 complete automated Assessments / 1,375 named Tests**.
- Both the original split/merged representations reconstruct **871/872 full Assessments and 1,374/1,375 Tests** exactly. They both reject the same known original bootloader source inconsistency.
- Existing comparison measured **9,916 requirement-related YAML lines for split vs. 7,942 for merged**; **189,029 characters for split vs. 178,250 for merged**. Merged saves **1,974 lines (19.9%)** and **10,779 characters (5.7%)** in these representations.
- The earlier proof predates later removal of `condition`/`scope` wrappers and restoration of canonical operators. The newer split examples are independently source-structurally reversible for the same 871/872, but a fully normalized merged variant has not been separately rerun. **Do not mislabel this review as a new integrated A/B execution proof.**
- **201 legacy `all_exist` source distinctions** remain unchanged; do not fold them into `at_least_one` until error/incomplete behavior is proved.

## Decision rationale

**Provisional winner: split `items` + `match`.**

1. It names independently meaningful questions, so changing `match` cannot silently change `items`.
2. It scales to unusual combinations without a growing vocabulary of concatenated operators; the editor can offer two semantic controls and explain their differences.
3. It uses the same cardinality words at the Test and record levels; `states.and/or` remains a separate operation.
4. Merged has a real benefit—fewer lines, especially for common one-field checks—but long labels are harder to parse, autocomplete and validate consistently in exceptional cases.
5. Do **not** add a third `condition` or generic `scope` layer to compensate. Presence-only requirements have only `items`, not an invented `match`.

**Limits:** This is an expert design recommendation, not a measured blind auditor comprehension win and not authorization to edit the normative grammar. We should test the two variants with non-OVAL readers as part of the editor/auditor preview rather than keep rewriting keywords.

## Next concrete checkpoint (avoid more open-ended renaming)

1. Keep the latest canonical research candidate frozen for prototype comparison. Do not bake provisional syntax into release packages.
2. Finish separately scoped **field existence/presence** requirements and inherited State-group behavior, especially DNS, optional Apache fields, Linux permission fields, and nested Windows record members. Test zero/error/unknown/incomplete outcomes; do not guess.
3. Render the real RHEL nosuid, Win11 seven-Test WMI/user-right and Linux dependent-file Assessments as a deterministic **auditor preview derived from the actual Assessment**, with drill-down showing the source predicate, missing-data behavior and decision tree. Avoid independent hand-written paraphrases that can drift.
4. Reuse the Assessment-first editor architecture in `vanderpol/scap-ng-editor` issues [#2](https://github.com/vanderpol/scap-ng-editor/issues/2) and [#3](https://github.com/vanderpol/scap-ng-editor/issues/3). Do not release 0.4-dependent semantic editing or task Codex until the owner lifts the tracked semantic gate [#229](https://github.com/vanderpol/scap-ng/issues/229). A read-only review/presentation proof and schema-neutral foundations are compatible with that gate.

## Sources

- [0.3 overview and examples](https://github.com/vanderpol/scap-ng/blob/main/specification/examples/assessments.md)
- [0.4 working schema](https://github.com/vanderpol/scap-ng/blob/main/schema/v0.4.0/README.md)
- [original source-exact split-vs-merged comparison](https://github.com/vanderpol/scap-ng/blob/main/research/assessment-simplification/english-first-04/require-presentation-comparison/report.md)
- [latest canonical-language proof](https://github.com/vanderpol/scap-ng/blob/main/research/assessment-simplification/english-first-04/canonical-operators/report.md)
- [current six real auditor samples](https://github.com/vanderpol/scap-ng/blob/main/research/assessment-simplification/english-first-04/AUDITOR-SAMPLE-GALLERY.md)
- [work tracking #235](https://github.com/vanderpol/scap-ng/issues/235) and [semantics gate #229](https://github.com/vanderpol/scap-ng/issues/229)
