# 0.4.0 schema-first reconciliation of accepted 0.3/0.4 modernizations

**Date:** 2026-10-27. **Tracking:** [#255](https://github.com/vanderpol/scap-ng/issues/255),
converter integration [#251](https://github.com/vanderpol/scap-ng/issues/251).
**Status:** schema-review candidate, not scanner equivalence or a 0.4.0 release.

## Problem and objective

OVAL 5.12.3 uses a named `constant_variable` with multiple `<value>` elements
to supply values to an otherwise scalar XML Object or State entity. The
[accepted 0.3 modernization](../../research/assessment-simplification/static-literals-21/README.md)
allows native typed literal arrays in **both** Object selectors and State
predicates, with original `var_check` retained as the independent `value_match`
quantifier. The current 0.4 common predicates already implement this grammar,
but capability-specific acquisition contracts can prevent its use.

`file.hash` was one such contract defect: the mapping treated OVAL
`filehash58_object/hash_type` as one required literal `algorithm` acquisition
parameter even though the original Object accepts a multi-value `var_ref` and
`var_check`. This version-local correction uses the **existing** Object
selector grammar instead of introducing another Boolean dialect or synthetic
per-algorithm Tests. The current converter still blocks original multi-algorithm
cases until source-lowering and collector-domain semantics are independently
proved. Source OVAL remains unchanged.

## Original-source counterexample and proposed native expression

Pinned Self-Assertion source:
`tests/fixtures/v04-filehash-acquisition-conflict/`, original SHA-256 and
validation in its `provenance.json`. OVAL Definition 566 uses three Tests:

| OVAL Test | Object `hash_type` Variable (`var_check`) | State `hash_type` Variable (`var_check`) |
| --- | --- | --- |
| 305 | MD5, SHA-1 (`at least one`) | SHA-224/256/384/512 (`none satisfy`) |
| 544 | SHA-224/256/384/512 (`none satisfy`) | MD5, SHA-1 (`at least one`) |
| 354 | SHA-224/256/384/512 (`at least one`) | SHA-224/256/384/512 (`at least one`) |

All three select algorithms over the finite six-algorithm filehash58 domain;
they are not digest-content comparisons. In Test 544, the Object selects the
complement of the four SHA-2 algorithms, and the State checks MD5/SHA-1.
The native Object (illustrative Test 544) is:

```yaml
capability: file.hash
object:
  full_path: {equals: /bin/ls}
  filesystem: local
  algorithm:
    equals: [sha224, sha256, sha384, sha512]
    datatype: string
    value_match: none
require:
  items_found: one_or_more
  items_satisfying: every
  fields:
    algorithm:
      equals: [md5, sha1]
      datatype: string
      value_match: one_or_more
      values_found: one_or_more
      values_matching: every
```

The complete Test uses its normal `test_title` and `reported_elements`; this
excerpt focuses on the selector and requirement. An Item's `algorithm` value,
its `digest` and collection completeness remain separate observations. A
complete selection of zero algorithms must not be manufactured from an
incomplete/error scan. The scanner must enumerate the complete algorithm
domain before applying an expected-value complement; ordinary equality
against one prechosen algorithm is insufficient.

The version-local `file.hash` mapping now classifies `hash_type` as the native
`algorithm` selector, requires it in each permitted direct selector combination,
declares the six native enum values, and gives the same source-to-native enum
crosswalk to Object and State. Negative tests reject omitted algorithm,
unsupported values, raw scalar-parameter syntax, wrong comparator and missing
`value_match`. The original XML/XSD/Schematron input remains pinned.

### Alternatives rejected

1. Select only the first Variable value: loses the other algorithms.
2. Replace `var_check: none satisfy` with `NOT OR`: invents an unapproved
   authoring syntax and conflates expected-value matching with Item logic.
3. Emit a synthetic Union or multiple Tests for each hash: changes the
   source Object population and Test evaluation/correlation boundaries.
4. Permit arbitrary arrays on all collection parameters: Boolean/structured
   acquisition controls are not ordinary multi-value selectors; dynamic
   command/query fan-out needs a separate exact acquisition contract.

## Whole-catalog capability audit

The 100 supported 0.4 mappings contain **141** mapped Object selector fields
across **77** capabilities and **694** generated State field entries (including
six record fields). The version-local generated schema sweep validates
each ordinary selector with both typed literal arrays and named Variable
references under all four `value_match` values:
`none`, `exactly_one`, `one_or_more`, `every`. It also checks absence of required
quantifiers and preserves scalar-shorthand acceptance. All 694 State field
entries are checked for the shared scalar or record wrapper grammar rather than
capability-specific OVAL State syntax. These are
structural schema checks; they do not imply 141 collector conformance proofs.

After the `file.hash` correction, 13 mappings still declare **45** special
acquisition parameters:

| Classification | Fields | Disposition |
| --- | ---: | --- |
| Boolean acquisition/behavior switches | 25 | Intentionally scalar; not static-Variable array sites. |
| Structured `windows.cmdlet` `parameters` / `select` | 2 | Structured schema-specific values; not scalar predicate arrays. |
| String `item_creation` controls | 3 | Finite behavior controls; keep scalar. |
| Variable-capable string acquisition parameters | 15 | Four capabilities: `independent.shellcommand` (3), `independent.sql512` (5), `windows.cmdlet` (5), `windows.wmi.query` (2). Keep named Variable support; multivalued command/query fan-out and `var_check` semantics require source-backed collection-domain proof before changing this contract. |

This distinction prevents mistaking all 30 scalar-only parameters for bugs.
The remaining 15 are **explicitly tracked as an acquisition/fan-out proof
boundary**, not silently certified as handling multi-valued Variables. Unlike
`file.hash`, their source values generally do not belong to a finite closed
algorithm domain; complement selection cannot be assumed to mean command or
SQL execution over an imaginary universe.

## Other 0.3 and 0.4 modernization decisions checked

| Accepted direction | Current 0.4 structural disposition | Regression/evidence boundary |
| --- | --- | --- |
| Object local to Test; shared Object reference optional | Retained: inline and referenced flat Objects | `test_v04_object_contract`, `test_v04_schema_draft` |
| Static scalar/literal collection in Object and State | Retained for 141 selectors and common State predicates; `file.hash` corrected | `test_v04_schema_modernization_invariants`, `test_v04_filehash_acquisition_conflict` |
| `var_check` independent of observed Item/field matching | Retained as `value_match`; four match cardinalities | `test_v04_field_requirement_schema`, pinned original filehash58 |
| Ordinary scalar compact type inference; explicit typed arrays/Variables when ambiguous | Scalar shorthand retained; **integration gap below** for strict explicit array types | `test_v04_object_selector_language`, Windows user-rights original fixture |
| Genuine runtime Variables, ObjectComponent, collection `for_each` and correlation | Existing graph and binding forms retained; no new flattening | `test_v04_object_contract`, `test_v04_semantic_boundary_cases` |
| Direct Organizational Input in expected State values | Existing State reference form preserved; not silently enabled in Object selection | Versioned Assessment language predicates |
| Genuine Sets and ordered Filters; no synthetic one-operand Union | Existing native Set/Filter surfaces retained | `test_v04_object_contract`, `test_v04_oval_set_filter_source` |
| Test-local `require` and explicit `items_found` / `items_satisfying` | Retained; no Test `states`, no hidden defaults | `test_v04_all_items_schema`, `test_v04_clear_cardinality_schema` |
| Independent field/record existence and matching with nearest `field_requirement` | Retained, including confirmed absence separate from incomplete evidence | `test_v04_field_requirement_schema`, `test_v04_clear_cardinality_schema` |
| `evaluate` logical `and`/`or`/`one`/`xor` | Retained; no legacy `any/every` Boolean aliases | `test_v04_evaluate_operator_schema` |
| Flat direct Object fields, no generic `select/collect` wrappers | Retained; capability-owned `windows.cmdlet.select` remains distinct | `test_v04_native_schema_generation` |
| Exact selector alternatives including combined process selectors | Retained; no return to overlapping oneOf branches | `test_v04_process_selector_conflict` and its approved issue #251 packet |
| Deferred shared Observation, broader conditionals, unsupported/deprecated OVAL Tests | Still deferred/unsupported; not promoted through this mapping correction | `CURRENT-DESIGN.md`, AGENTS.md |

The cross-check also used the final [0.3 IN/DEFER/OUT disposition
#174](https://github.com/vanderpol/scap-ng/issues/174), rather than assuming
every 0.3 research candidate became normative. The other accepted decisions
remain outside this mapping edit: meaningful `-object`/`-variable` naming and
benchmark-local IDs; full-word comparison operators; `filesystem` scopes
`all`/`local`/`same`; finite Variable-function enums; the narrow inherited
`if/then/else`; typed Organizational Input and non-executable provenance;
publisher Profiles/Tailoring; explicit `reported_elements`; human assessor
attribution; deterministic signing and manual Assessment conversion. Their
versioned schemas and tests were not modified. This mapping change does not
promote the explicitly deferred Observation, typed `linux.fstab`, new
conditionals, broad cross-Assessment sharing or Input-driven acquisition
routing. It does not resurrect the rejected hidden reporting defaults or
separate thin/full result profiles.

### Explicit datatype integration gap (schema-first finding)

The [0.3 static-literal decision](../../research/assessment-simplification/static-literals-21/README.md)
retains explicit `datatype` on literal arrays/Variable operands, and the 0.4
README says arrays and Variables require explicit type. The current 0.4
JSON Schema requires `value_match` but historically **did not require**
`datatype` on these operands. Requiring it at both Object and State scopes is
straightforward schema enforcement, but an attempted strict schema-only change
exposed a concrete compatibility regression: existing source-proved Windows
user-rights arrays use `{equals: [many values], value_match: every}` without
`datatype: string`. Three focused converter tests fail if strict enforcement
is turned on before the converter emits the explicit type.

**Integration decision:** preserve this as a known, reproduced cross-cutting
dependency. The strict common-schema adjustment must be committed together
with, or after, verified converter emission of explicit `datatype` for arrays
and Variable operands where required. Do not publish a knowingly red mandatory
converter gate, silently infer runtime types, or mislabel the existing output
as compliant with the strict modernization rule. The schema-first candidate
and its negative tests record the expected next interface change for Codex.

## Verification and release boundaries

- Original filehash58 XML must pass independent original XSD/Schematron.
- Generated `file.hash` schemas must admit Test 305/544/354 selector and
  State predicate shapes with all four allowed expected-value quantifiers.
- Every generated capability schema must validate against its same-version
  schema registry; no previous-version references.
- Changes to the native generated-contract fingerprint are limited to the
  reviewed capability (plus any separately documented common-language schema
  change), with positive/negative mutations.
- Original source conversion and compiled operand preservation remain Codex's
  separate next gate. Runtime scanner execution is **not** claimed.
- The full 65-benchmark corpus is a release/checkpoint gate only, never a
  routine schema-development loop.

No normative specification pages, frozen 0.3 schemas or source XML were
modified by this work.
