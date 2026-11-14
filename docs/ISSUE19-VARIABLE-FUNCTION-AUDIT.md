# SCAP-NG 0.4 Variable-function audit and Issue #48 restoration

The active SCAP-NG 0.4 grammar uses explicit recursive expression objects. It
inherits the pinned OVAL 5.12.3 operand order, collection, multiplicity, empty
value, and diagnostic-status boundaries unless an owner decision says
otherwise. JSON Schema validates authoring shape; it does not execute values or
prove scanner equivalence.

## Active forms

| Form | Native authoring shape | Contract |
|---|---|---|
| `literal` | `{literal: scalar|list|{datatype,value}}` | Preserve datatype, order, duplicates, and records. |
| `variable` | `{variable: name-variable}` | Preserve referenced population and status; semantic validation handles cycles/types. |
| `values` | `{values: {object, field}}` | Read a collected field without inventing values for missing/status outcomes. |
| `concat` | `{concat: [expression, ...]}` | Two or more ordered components; Cartesian product; no status-to-string coercion. |
| `regex_capture` | `{regex_capture: {pattern, value}}` | Process each input value under the inherited capture contract. |
| `unique` | `{unique: expression|[expression, ...]}` | Flatten ordered components and retain first occurrences; record data is not a transformation operand. |
| `count` | `{count: expression}` | Count values including duplicates; successful empty input is zero; statuses remain statuses. |
| `split` | `{split: {delimiter, value}}` | Literal delimiter; retain leading/trailing/adjacent empty values and duplicates. |
| `substring` | `{substring: {substring_start, substring_length, value}}` | Signed 32-bit explicit options; OVAL one-based boundary behavior. |
| `arithmetic` | `{arithmetic: {arithmetic_operation, values}}` | Numeric Cartesian product; add/multiply; integer/float widening. |
| `begin` / `end` | `{begin/end: {character, value}}` | Add the complete boundary string only when it is absent. |
| `merge` | `{merge: {delimiter, sort, order, values: expression|[...]}}` | Flatten ordered populations, preserve duplicates, explicit sorting and joining. |

The exact owner rationale and alternatives are recorded in
`docs/ISSUE48-VARIABLE-FUNCTION-DECISION-MATRIX.md`.

## Broader OVAL disposition

The pinned OVAL FunctionGroup also contains `escape_regex`, `time_difference`,
and `glob_to_regex`. They have no active source uses in this corpus and remain
deferred. The inactive generic function schema is a migration artifact and is
not an active editor or converter contract.

## Qualification boundary

The converter and structural tests preserve source AST shape and reject
invalid forms. Independent vectors cover collection order, multiplicity,
empty values, arithmetic Cartesian products, substring boundaries, and status
propagation. A scanner/runtime implementation and independent execution proof
are not present here; no runtime equivalence claim is made.
