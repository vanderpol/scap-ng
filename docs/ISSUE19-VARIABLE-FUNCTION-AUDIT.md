# Issue #19 variable-function audit and authoring documentation

This audit uses the pinned OVAL 5.12.3 `oval-definitions-schema.xsd` as the
semantic baseline. The source is the `v5.12.3` tag at commit
`2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`; its SHA-256 is
`06b79e8683d6b9dcaad3ab074a456588ed82c4edd2e8fff209def10aa0a366cc`.
The repository keeps source identity and paraphrased findings, not copied XSD
prose.

## Retained native forms

The active `schema/variable-expression.schema.json` vocabulary contains seven
forms:

| Form | Source relationship | Native authoring and parity boundary |
|---|---|---|
| `literal` | Typed literal/component data | Preserves scalar/list/record shape, datatype, order, and duplicates. |
| `variable` | OVAL `VariableComponentType` | References another Variable; cycle/type/status checks are semantic. |
| `values` | Native collected-field composition | Reads one field from a selected Object; no one-to-one OVAL function. |
| `concat` | `ConcatFunctionType` (XSD 770–823) | Requires 2+ ordered components; multi-values form Cartesian products; missing/status outcomes are inherited. |
| `regex_capture` | `RegexCaptureFunctionType` (931–953) | Applies to each input value and returns the first capture under the inherited regex contract. |
| `unique` | `UniqueFunctionType` (954–962) | Removes duplicate scalar values; records are outside the retained domain. |
| `merge` | Native composition | Explicit delimiter, sort mode, and order; it does not implicitly deduplicate. |

`concat` authoring example:

```yaml
concat:
  - literal: "https://"
  - variable: host-name-variable
  - literal: "/policy"
```

If the variable produces `edge-a` and `edge-b`, the result population is
`https://edge-a/policy` and `https://edge-b/policy`. With multiple-valued
components, every component combination is evaluated. A missing or nonexistent
component is not converted into text; Error, Incomplete, Does Not Exist, Not
Collected, and Not Applicable outcomes remain status outcomes. The schema
cannot execute or prove those outcomes.

## Broader OVAL disposition

The pinned OVAL `FunctionGroup` includes `arithmetic`, `begin`, `concat`,
`end`, `escape_regex`, `split`, `substring`, `time_difference`,
`regex_capture`, `unique`, `count`, and `glob_to_regex`. Only `concat`,
`regex_capture`, and `unique` are retained as direct native forms. The active
schema's `values` and `merge` are native compositions, not claims that OVAL
has identically named functions. The remaining functions are deferred, not declared unsupported without an owner decision; no unsupported function disposition is asserted. The
inactive `variable-function-expression.schema.json` is a migration candidate,
not active editor or runtime support.

## Verification status

The repository has no compiler, interpreter, scanner, or independent function
proof implementation to execute. The automated suite therefore verifies schema
shape, nested authoring help, `concat` minimum cardinality, examples, and
explicitly documented boundaries. It does **not** claim runtime parity.

Before qualification, a runnable evaluator must provide vectors for casting,
Cartesian products, duplicate/order behavior, regex capture edge cases, and
all Error/Incomplete/Does Not Exist/Not Collected/Not Applicable propagation.
Those are documented compatibility gaps, not guessed semantics.

The machine-readable inventory is
`docs/metadata/variable-function-audit.json`.
