# Issue #28: OVAL variable-function recovery

This document records the coordinated 0.4.0 schema contract for the recovered
OVAL 5.12.3 variable functions. The canonical representation is the
`function.name`, ordered `function.arguments`, and explicit `function.options`
envelope in `variable-expression.schema.json`; the legacy native forms remain
accepted for compatibility and are not reinterpreted.

## Contract

| Function | Result | Input/option boundary |
|---|---|---|
| `count` | integer | One or more arguments; options `{}`. Flatten values, retain empty values and duplicates, and count the resulting population. |
| `concat` | string | Two or more string arguments; options `{}`. Evaluate the ordered Cartesian product. |
| `unique` | string collection | One or more string arguments; options `{}`. Flatten in source order and retain first occurrences only. |
| `merge` | string | One or more scalar arguments; explicit delimiter, sort, and order. Records are not silently flattened. |
| `split` | string collection | One string argument and a literal delimiter. Preserve leading, trailing, adjacent empty parts and duplicates. |
| `substring` | string | One string argument and signed 32-bit options. OVAL one-based indexing; starts below one clamp, starts past the end are errors, and negative/oversized lengths mean remainder. |
| `arithmetic` | integer or float | Two or more numeric arguments and `add`/`multiply`; integer plus float widens to float. No boolean/string coercion. |

JSON Schema validates authoring shape and explicit options. It does not claim
execution or source equivalence. The tools converter's opt-in recovery path
emits this envelope and records `UNPROVED` provenance until independent OVAL
comparison and runtime/compiler evidence exists.

The independent source-semantic vectors cover empty populations, duplicate and
ordered aggregation, Cartesian products, datatype errors, status propagation,
substring boundaries, and merge ordering. AccessToken and SQLEXT remain
intentionally unsupported.
