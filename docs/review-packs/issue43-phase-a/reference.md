# Review-only documentation pack

<!-- Generated: python tools/generate_review_documentation_pack.py -->

**Issue #43 Phase A only; no approved release or live editor proof.**

[Advanced constraints](constraints.md) · [Integration receipt](RECEIPT.md).

## unix.file Object

Select filesystem entries and collect their metadata for comparison.

Occurrences below apply to the inline Object branch. Selector pairing is not enforced by 0.4.0; no new pairing rule is added.

| Field | Type | Occurrences | Description |
| --- | --- | --- | --- |
| filepath | string selector | 0..1 | Full path of the selected entry. |
| path | string selector | 0..1 | Directory containing the selected entry. |
| filename | string selector or null | 0..1 | Entry name within the selected directory; null selects the directory itself. |
| filesystem | string | 0..1 | Filesystem scope: all, local, or the starting filesystem (same). `all`, `local`, `same`. Editor suggestion: `local`. |
| traversal | object | 0..1 | Controls recursive searching through directories and symbolic links. |

### traversal

Child occurrences apply when traversal is present; array/map entries are separate from named properties.

| Field | Type | Occurrences | Description |
| --- | --- | --- | --- |
| traversal.max_depth | integer or string | 1..1 | Maximum downward recursion depth; 0 includes only the starting directory. integer ≥ 0, `unlimited`. Editor suggestion: `unlimited`. |
| traversal.recurse | string | 1..1 | Entry types to follow during recursion. `directories`, `symlinks`, `symlinks_and_directories`. Editor suggestion: `symlinks_and_directories`. |

## unix.file collected Item

The generic 0.4.0 typed-value wrapper or array remains accepted. Payload types are not tightened to PR #39’s proposed field datatypes. Status/redaction constraints still apply. Each row counts its named key.

| Field | Type | Occurrences | Description |
| --- | --- | --- | --- |
| fields.full_path | object or array | 0..1 key | Full path of the collected entry. |
| fields.directory | object or array | 0..1 key | Directory component of the collected path. |
| fields.name | object or array | 0..1 key | Entry name without the directory. |
| fields.type | object or array | 0..1 key | Kind of filesystem entry. |
| fields.owner_uid | object or array | 0..1 key | Numeric user ID of the owner. |
| fields.owner_gid | object or array | 0..1 key | Numeric group ID of the owning group. |
| fields.size | object or array | 0..1 key | File size. |
| fields.access_time | object or array | 0..1 key | Last data-access time. |
| fields.change_time | object or array | 0..1 key | Last inode-status change, not creation time. |
| fields.modify_time | object or array | 0..1 key | Last content-modification time. |
| fields.setuid | object or array | 0..1 key | Set-user-ID permission flag. |
| fields.setgid | object or array | 0..1 key | Set-group-ID permission flag. |
| fields.sticky | object or array | 0..1 key | Sticky/restricted-deletion flag. |
| fields.owner_read | object or array | 0..1 key | Whether the owner-read permission bit is set. |
| fields.owner_write | object or array | 0..1 key | Whether the owner-write permission bit is set. |
| fields.owner_execute | object or array | 0..1 key | Whether the owner-execute/search permission bit is set. |
| fields.group_read | object or array | 0..1 key | Whether the group-read permission bit is set. |
| fields.group_write | object or array | 0..1 key | Whether the group-write permission bit is set. |
| fields.group_execute | object or array | 0..1 key | Whether the group-execute/search permission bit is set. |
| fields.other_read | object or array | 0..1 key | Whether the other-read permission bit is set. |
| fields.other_write | object or array | 0..1 key | Whether the other-write permission bit is set. |
| fields.other_execute | object or array | 0..1 key | Whether the other-execute/search permission bit is set. |
| fields.has_extended_acl | object or array | 0..1 key | Whether ACL permissions differ from standard UNIX permissions. |

## unix.file Require

Comparison context; existence-only uses its separate native alternative. Field-value counts and Item counts remain independent.

| Field | Type | Occurrences | Description |
| --- | --- | --- | --- |
| item_requirement | object | 1..1 | Independent requirements for the number of selected Items and the number satisfying the comparison. |
| field_requirement | object | 1..1 | Explicit shared values_found/values_matching pair; a closer complete pair overrides it without runtime defaults. Editor suggestion: `{'values_found': 'one_or_more', 'values_matching': 'every'}`. |
| fields | object | conditional | One complete condition; distinct field predicates are combined with logical AND. |

### item_requirement

| Field | Type | Occurrences | Description |
| --- | --- | --- | --- |
| item_requirement.items_found | string | 1..1 | Required cardinality of selected Items. `none`, `exactly_one`, `one_or_more`, `zero_or_more`. Editor suggestion: `one_or_more`. |
| item_requirement.items_satisfying | string | 1..1 | Required cardinality of Items satisfying the comparison. `none`, `exactly_one`, `one_or_more`, `every`. Editor suggestion: `every`. |

### field_requirement

| Field | Type | Occurrences | Description |
| --- | --- | --- | --- |
| field_requirement.values_found | string | 1..1 | Required count of observed values for a field. `exactly_one`, `one_or_more`, `every`, `zero_or_more`. |
| field_requirement.values_matching | string | 1..1 | Required count of observed values satisfying its predicate. `none`, `exactly_one`, `one_or_more`, `every`. |

Field predicates use the same field descriptions as collected Items; [all exact field routes](editor-metadata.json) point to one owner per field.

## Approved core/shared examples

| Field | Type | Occurrences | Description |
| --- | --- | --- | --- |
| input-reference | object | — | Uses the value of a declared Input. |
| input-cardinality | string | — | Sets how many values a supplied Input may contain. `exactly_one`, `zero_or_one`, `one_or_more`, `zero_or_more`. |
| input-required | boolean | — | Specifies whether this Input must be supplied. |
| field-predicate | object | — | Compares a collected field's values or checks for confirmed absence. |
| else-if | array | — | Selects the first true alternative branch when preceding conditions are false. |
| not-evaluated | object | — | Declares that this branch cannot be evaluated and provides a reason. |
| technical-outcome | string | — | Reports whether a Test or Assessment is true, false, errored, unknown, unevaluated, or inapplicable. `true`, `false`, `error`, `unknown`, `not_evaluated`, `not_applicable`. |
| value-redaction | boolean | — | Indicates that the value was intentionally omitted from the reported evidence. |

This is a review slice. Nine proposed semantic descriptions and foreach authoring remain excluded. Offline lookup does not establish live YAML/Graphical help or scanner equivalence.
