# Reported elements — single-commit draft checkpoint

Owner direction, 2026-10-03: implement the promising array-based explicit choice,
with all feature changes in one dedicated commit for easy Board review/revert.
Baseline content is PR #130, `31d54712a004b2172a5d3e1210a51e451f2de60e`.
This remains a draft working implementation, not Board ratification or a complete
0.2.0 release. No Object selector or State predicate is added.

## Authored control and scope

Each automated Test may declare exactly one of:

```yaml
reported_elements: all       # also the default when omitted
reported_elements: compared
reported_elements: [owner_uid, owner_user_name, owner_gid, owner_group_name]
reported_elements: []        # retain only required identity/decisive fields
```

The explicit list contains unique top-level Item field names, not paths, regexes,
record-property selectors or executable expressions. No null/object shorthand is
accepted. Unknown capability field names fail semantic/generated-schema validation,
even on unexecuted Tests. A known but unavailable field is identified in report
metadata, not fabricated as an observed null or assigned an invented acquisition
status. Record fields and repeated values are retained whole; selecting nested
record properties is not introduced in this checkpoint.

Placement is Test-only. There is no additional Assessment/Object/Benchmark default
or override chain. The compiler preserves and validates the signed source control.
Tailoring and Organizational Input do not mutate it. A different reporting choice
is an authored Test/Assessment revision, not an Organizational Input branch choice.

The capability schema overlay adds only this Test property. Object, State and
collected Item definitions remain identical to their current generator output.
`result-field-extensions.json` records the eight result-only name proposals from
#129 so explicit reports can select them without introducing name predicates.
It does not implement lookup or permit a numeric identity to be replaced by a
label. Consolidate the collected Item generator on this registry when integrating
#129 into the complete 0.2.0 result set; do not maintain diverging copies.

## Execution lineage and shared Items

Projection occurs after collection, evaluation and redaction. The projector takes
already validated canonical Items and complete actual execution lineage. Each use
records `test_ref`, `item_ref`, `used_elements` and `required_elements`; optional
`relationship` is direct, variable, filter or selection (default direct).
`used_elements` must include indirect use through Variables, Filters, selectors
and intermediate comparisons, not merely the final State. `required_elements`
must include resource identity and additional decisive explanation fields.
Item ID, status, capability, provenance and import-origin context remain intact.
The projector cannot infer complete usage from source expressions; the evaluator/
collector's lineage recorder owns that requirement. This is not a new collector.

Tests sharing an Item combine reporting requirements deterministically: any
executed use requesting `all` (including omission) retains all available fields;
otherwise use the union of explicit/compared requirements plus all required and
actually used fields. An unexecuted Test does not expand the report merely because
it declares a reporting preference. A shared imported Item follows the same rules.
An Item with no associated Test lineage is preserved in full, rather than guessed
to have no relevant fields; Item inclusion/materialization is a separate feature.

Explicit names belong to the Test's capability vocabulary. When a Variable or
Filter connects a Test to an upstream Item of another capability, `compared`
retains the recorder's actual upstream fields. An explicit list for the primary
capability is not reinterpreted as field names on that different upstream Item;
its used/required upstream fields are retained. Direct mismatched capability
associations fail instead of silently inheriting/coercing a capability.

Resolved names retain their authoritative numeric source field when available.
Resolution metadata for omitted names and locators pointing to omitted fields
are removed. Name-resolution status, original observation timing, origin references,
typed values, record correlation and redacted markers otherwise remain intact.

## Projection versus canonical results and masking

Output is explicitly marked `item_report.kind: reported_elements_projection`,
with the source execution reference and unchanged source logical/population/evidence
completeness flags. Each Item records omitted, requested-but-unavailable, and
retained-required elements. This is a derived report, not a replacement complete
Assessment Result or a claim that field selection made a capped population complete.
The canonical Items and technical results remain unchanged. Full Assessment Result
integration can reference this projection without removing authoritative Test/
Item/State/Entity evidence needed for logical reconstruction.

Owner follow-up: reported elements overlaps with OVAL mask for presentation but
does not fully replace privacy masking. `redact_result` remains the confidentiality
control. A field omitted from this Item report may still be present in canonical
Entity comparisons, Variables or another report path. Redaction must be applied
by the producer across all applicable result/evidence paths before projection.
Shared `all` preferences cannot override it; a redacted typed value retains its
marker and never contains a `value`. The projector rejects an existing redacted
value leak even if selection would otherwise omit it. It does not claim to scrub
unprovided canonical/auxiliary artifacts. No mask/redaction behavior is removed.

## Validation and promotion limits

Seventeen focused test methods cover the control grammar, all 100 capability Test
overlays, closed vocabularies, Test-only placement, six known-result selections,
shared unions/all precedence/order independence, indirect cross-capability lineage,
imported origins, dangling metadata, redaction, unresolved lookups, source caps,
input immutability, unchanged actual numeric truth and compiler rejection of bad
controls on unexecuted Tests. The portable CLI validates emitted reports locally.

Reproduction commands are in `tests/reported-elements-0.2.0/README.md`. The focused
and existing regression run passed 120 tests. Existing 0.1.0 schemas/generator and
JSONL/SIEM projection remain unchanged. Remaining before release: complete result
schema integration, actual lineage production on collector/evaluator paths,
target conformance, complete vendor feature coverage, and Board disposition.
Conditional normalization remains removed from scope (#126).

All source, schemas, fixtures, documentation and CI wiring for this feature are
published in one ordinary commit, on top of #130, so that commit can be reverted
without reverting earlier conditional work. No merges are performed here.

Validation command: `PYTHONPATH=tools python -m unittest tools.test_reported_elements tools.test_conditional_integration tools.test_conditional_conformance tools.test_scap_ng_content_compiler tools.test_schema_issue_regressions tools.test_generate_capability_schema tools.test_generate_variable_value_capability_schema tools.test_validate_native_package_graph tools.test_result_schema_scope tools.test_project_results_jsonl`. The fixture CLI and generated Unix file overlay both ran successfully. The authoring vocabulary guard passes for the sample Assessment; `git diff --check` passes.
