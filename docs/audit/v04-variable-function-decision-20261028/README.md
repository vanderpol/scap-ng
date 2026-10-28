# Grouped Variable-function decision — proposed, not approved

Owner-requested design package for [#255](https://github.com/vanderpol/scap-ng/issues/255),
with converter implementation tracked in [#251](https://github.com/vanderpol/scap-ng/issues/251).
**No syntax in this proposal is normative or emitted by the converter. No schema,
compiler, scanner, editor or specification implementation is changed.**

## Decision and recommendation

Approve one function-call expression shape for all OVAL-derived functions:

```yaml
expression:
  function:
    name: substring
    arguments:
      - variable: source-text-variable
    options:
      substring_start: 3
      substring_length: 2
```

Every call has exactly `function`, whose body has exactly `name`, `arguments`
and `options`. `name` is one of the 13 original OVAL function names.
`arguments` is an ordered array of expression nodes, even for a unary function;
`options` is a literal typed mapping, including `{}` when empty. Use the exact
original option names to avoid unnecessary terminology or off-by-one translation.
Do not accept both `value`/`components` or `start`/`substring_start` layouts as
interchangeable runtime grammars. Native-only `to_lower`/`to_upper` names are not
OVAL 5.12.3 functions and are outside this proposal.

Leaf `literal`, `variable` and Object-value projection expressions retain their
existing contracts. Only the function-call envelope is proposed here. A literal
or record whose data happens to contain keys named `function` or `variable`
remains opaque data. Reference discovery visits only grammar-owned expression
positions, especially `function.arguments`; option strings never become code.

This shape is recommended because one traversal can handle arity, nested calls,
DAG references, typing and provenance, while closed per-function option schemas
handle the differences. It avoids function-specific argument container names.
Unknown names/options, wrong arity and malformed expressions fail validation;
they must not be accepted merely because they are JSON objects.

The existing four emitted forms (`concat`, `regex_capture`, `merge`, `unique`)
remain unchanged until approval. If adopted, migrate all function calls through
one explicit versioned upgrader and independently compare semantics. Do not add
permanent alternative schema branches for the old layouts. Immutable historical
refs/proof packets remain reproducible. Any expected new program hashes require
individual review; current proof identities must survive the migration.

## Original authority and reproducible evidence

The original source is OVAL 5.12.3 `oval-definitions-schema.xsd`, vendored under
[the pinned SCAP schemas](../../../third_party/scap-1.4-schemas/oval_5.12.3/oval-definitions-schema.xsd).
The [source-contract inventory](source-contracts.json) contains its exact SHA-256,
source lines, all 13 XSD signatures, option types/defaults/enumerations, complete
function documentation, embedded Schematron XPath assertions, and applicable
global Variable/entity and record-reference rules. It is evidence, not a new
schema. [Checksums](manifest.json) bind this package's inputs.

Reproduce it with the read-only [inventory utility](../../../tools/audit_v04_variable_function_contracts.py):

```bash
PYTHONPATH=tools python tools/audit_v04_variable_function_contracts.py \
  --source-root ORIGINAL_OVAL_TEST_CONTENT --output NEW_FUNCTION_REPORT.json
```

The collection is pinned to Self-Assertion
`e3538595c5083b9c34d937a81d319234df9bbfaa`; all source files are checked before
analysis. Usage follows complete Variable dependency closures, including nested
functions hidden behind another conversion blocker. The previous first-error
inventory reported 67 cases. The full inventory has **80 function/Test pairs
across 80 distinct original Tests**, with nine remaining source function names.
These are existing original Tests, not 80 newly converted or additional source Tests. The transitive audit exposes 13 uses hidden by earlier blockers.

Eight remaining functions have source-valid, nondeprecated original examples;
the inventory records each document/hash, Test, Variable, exact function and
Variable excerpts, plus original XSD/Schematron validity. `count` has no original
example in the pinned corpus. Its [constructed example](constructed-count.xml)
uses fresh identifiers and is explicitly not upstream original-source proof.
It [validates under the original XSD/Schematron](constructed-count-validity.json).
One input contains `foo`; another contains `foo, bar`; the documented count is
3, including the duplicate. No count implementation is enabled by this example.

Global source rules still apply: a referenced Variable and its associated entity
must agree on datatype; whole-record `var_ref` is forbidden. Function-specific
Schematron separately constrains direct literal/Variable components. The common
FunctionGroup documentation permits OVAL-compatible casts of runtime component
data before reporting a type error. Do not use that permission to repair an
original Schematron-invalid declaration.

## Signatures and multiplicity

All inputs and outputs are typed value collections with status/provenance.
A unary function still receives one collection-valued argument. Argument order,
duplicate occurrences and separate references to the same Variable are retained.
The table is the recommended source-compatible profile after approval; source
lines and exact assertions are in the inventory.

| Function | Argument collections | Input/result types | Options | Collection behavior |
| --- | --- | --- | --- | --- |
| `arithmetic` | 2 or more | integer/float → integer when all integer, float when mixed | required `arithmetic_operation`: `add` or `multiply` | Cartesian product, one result per combination; duplicates retained. |
| `begin` | 1 | string → string | required string `character` | Map each value; prepend the entire string only if not already present. |
| `end` | 1 | string → string | required string `character` | Map each value; append the entire string only if not already present. |
| `escape_regex` | 1 | string → string | none | Map each value; escape the exact OVAL Perl metacharacter set. |
| `glob_to_regex` | 1 | string → string | Boolean `glob_noescape`, original default false | Map each value; malformed glob is an error, not an empty result. |
| `split` | 1 | string → string collection | required string `delimiter` | Split every value and concatenate the resulting collections; retain empty strings and duplicates. |
| `substring` | 1 | string → string | required signed 32-bit integers `substring_start`, `substring_length` | Map each value using the original one-based/clamping/error rules below. |
| `time_difference` | 1 or 2 | string/integer date-time representations → integer seconds | `format_1`, `format_2`, both original default `year_month_day` | Two inputs use Cartesian first-minus-second; one input uses evaluation-time UTC minus its values. |
| `count` | 1 or more | simple typed values → one integer | none | Aggregate all argument values and count occurrences; not a Cartesian product and not a count of argument slots. |
| `concat` (existing subset) | 2 or more | string → string | none | Ordered Cartesian concatenation, preserving duplicate results. |
| `regex_capture` (existing subset) | 1 | string → string | string `pattern`; see omission boundary below | Map each value; first match/first capture; no capture or no match gives an empty string. |
| `unique` (existing subset) | 1 or more | components treated as strings → unique string collection | none | Aggregate all argument values, then deduplicate according to the original string semantics. |
| `merge` (existing subset) | 1 or more | string-convertible components → one string | `delimiter` default `""`; `sort` default `document`; `order` default `ascending` | Aggregate values before the specified sorting/joining; not Cartesian joining. |

The current converter's single-component `merge`/`unique` support is a subset;
XSD permits multiple components. The new representation must not imply those
combinations are already implemented or independently proved.

### Precise source boundaries

- `substring_start < 1` means 1; start beyond the string length is an error.
  Length 0 produces an empty string. A negative or overlong length takes the
  remainder. `abcdefg`, start 3, length 2 produces `cd`. Do not adopt host-language
  zero-based slicing or silently truncate an invalid start.
- `split` retains leading/trailing/adjacent-delimiter empty strings. For `-a-a-`
  split on `-`, retain `"", "a", "a", ""`. A string `""` is not a zero-value
  collection. Empty delimiter behavior is not specified by the XSD prose;
  retain it as an explicit unimplemented boundary until pinned source/reference
  semantics establish it. Do not invent character splitting or a regex delimiter.
- `escape_regex` escapes precisely `^$\.[](){}*+?|` as enumerated in the original
  prose; do not substitute a host `re.escape` with different whitespace/dash rules.
- Glob conversion preserves path-separator, dotfile, `.`/`..`, case, no-brace-
  expansion and no-tilde-substitution behavior. `glob_noescape` controls literal
  versus escaping backslashes. Invalid/unclosed brackets produce error.
- Date-time enum values are all six XSD values: `year_month_day`, `month_day_year`,
  `day_month_year`, `win_filetime`, `seconds_since_epoch`, `cim_datetime`.
  The TimeDifference prose lists fewer; the actual enumeration includes CIM.
  Record the exact documented lexical formats rather than using a permissive
  host date parser. One-argument mode uses `format_2`; do not inject conversion-
  time timestamps or a literal `now` argument. Clock access belongs to function
  evaluation, not conversion/compilation.
- Preserve timezone, subsecond truncation/rounding, Unicode indexing and source
  cast boundaries as explicit conformance questions where the pinned XSD does
  not fully specify them. Implement only independently established cases; do not
  choose local timezone, binary64 arithmetic or byte indexing as silent defaults.
- Original `regex_capture/@pattern` is optional in XSD with no declared default.
  The current converter requires an explicit pattern. Recommend requiring an
  explicit pattern in canonical authored calls; source omission remains an
  explicit unsupported case until its original evaluation contract is established.
  Do not replace omission with an empty regex to increase coverage.

## Nested Variables, typing and provenance

Nested functions use this same envelope recursively:

```yaml
expression:
  function:
    name: begin
    arguments:
      - function:
          name: substring
          arguments:
            - variable: original-text-variable
          options: {substring_start: 3, substring_length: 2}
    options: {character: "prefix-"}
```

A shared Variable is a DAG node, not a macro to duplicate or reevaluate. Keep
its identity, declared datatype, dependency edges and acquisition provenance.
Two references to a many-valued Variable in two Cartesian argument positions
still create all combinations; they are not zipped or collapsed. Source Object
projections retain their Object, field, filters and status. No function may
silently execute extra commands or reinterpret collection parameters as filters.

A signature fixes each function's input and result types. Preserve the containing
Variable's declared datatype and all required source cast boundaries. Do not
change a declaration to make a program validate. Only a documented OVAL-compatible
runtime cast may be attempted; unsuccessful casts are errors. A declaration/
result mismatch or unresolved cast profile remains unsupported until proved.
Records are not ordinary string/numeric arguments; existing record-field access
and source restrictions remain in force.

Arithmetic float results require the separately approved IEEE-32/nonfinite
contract in [#218](https://github.com/vanderpol/scap-ng/issues/218). Keep integer
arithmetic separate; do not route floats through binary64 or strings. Require
explicit range/overflow tests for large integers rather than accepting host
numeric truncation as language semantics.

Options with XSD defaults are materialized using their exact native types:
Boolean `glob_noescape`, integer substring offsets, strings/enums elsewhere.
Required options stay required. Unknown options fail, and no semantic default
is manufactured where XSD has none.

## Error, unknown and incomplete behavior

A call is not a Boolean predicate. Its output is a typed collection plus
completeness/evaluation status and original Item/Variable provenance. Keep
zero values, one empty string, unknown values, incomplete values and errors
separate. Do not use `[]`, `""`, 0, null or false as a universal error fallback.

Recommend extending the existing Variable-result status model with an explicit
`incomplete` status **only after owner approval**. The current draft enum has
`complete`, `error`, `unknown`, `not_evaluated`, `not_applicable`, `zero_values`,
and cannot explicitly label partial collection completeness. Preserve exact
original component flags in existing provenance/diagnostics as well. This is a
recorded schema design dependency, not a change made by this package.

- `complete` is reserved for complete known results with successful required
  operations/casts. `zero_values` must mean a proved complete empty result.
- Incomplete input must never produce a falsely complete result. Retain known
  values and their multiplicity, mark incompleteness, and preserve the original
  uncertainty for downstream quantifiers, aggregation and filters.
- A required parse/cast, out-of-bounds substring, invalid regex/glob or numeric
  failure produces the original error behavior. Preserve component diagnostics
  and do not discard a failing branch because another branch has values.
- Not-collected/unknown and not-evaluated states are distinct from zero values;
  not-applicable is not converted into an empty collection.
- Exact aggregate flag precedence, including all-empty/mixed-status aggregation
  and `count`/`unique` special cases, must be pinned to the OVAL variable/function
  evaluation rules and independently tested before approval/implementation.
  XSD syntax alone is not a normative status truth table. Do not assume a count
  of 0 from an unknown or incomplete input simply because no values are present.

## Independent acceptance requirements

1. Validate each original source closure with original XSD/Schematron; preserve
   its bytes, IDs, dependency hashes and source status. Label constructed cases.
2. Derive source terms/evaluation from the original contract and separately
   decode the one proposed NG grammar. Neither reader imports renderer helpers.
3. Test arity, option types/defaults/enums, nested calls, shared references,
   repeated arguments, empty strings, duplicate values and Cartesian growth.
4. Use independently justified outcomes: arithmetic 2×3 products, count versus
   unique versus merge, delimiter empties, substring bounds, exact escape/glob
   output and invalid syntax. Add metamorphic and mutation tests that still
   satisfy authoring schema but change meaning.
5. Pin error/unknown/incomplete flag matrices separately from value examples.
   Test failures in each argument, missing fields, partial acquisitions, zero
   results and unknown cardinality. Do not infer evaluator conformance from AST
   equality or successful compilation.
6. Bind a controlled evaluation clock for time tests, formats/UTC boundaries,
   one-/two-argument subtraction order, Cartesian dates and invalid dates.
   Preserve clock provenance; no conversion-time constant folding of `now`.
7. Validate native authoring and semantics, compile and inspect every operand/
   option/reference, validate compiled output and independently evaluate the
   documented profile. Unknown functions may not pass as opaque executable data.
8. Re-run maintained regression, six original primary sources, all 100 contract
   parity checks, all 39 Server 2025 user-rights Rules, eight process58 Tests and
   pinned hash Tests 305/544/354. Preserve all existing proof identities and
   individually justify approved program-hash changes. Scanner execution,
   complete policy/applicability and release conformance remain separate gates.

## Approval and implementation boundary

The requested grouped decision is: approve this single envelope and the
source-compatible signature/status profile, with the documented unresolved
edge cases kept unsupported until evidenced. Approve the explicit migration
plan for the four existing forms and the incomplete-status dependency. Do not
approve competing payload layouts merely because current schemas compile them.

After approval, the schema owner supplies a committed authoritative baseline;
converter work can then add shared typed function handlers and independent
proofs in bounded checkpoints. Until then, all nine remaining function names
stay explicitly unsupported. Independent #251 work continues; no unrelated
conversion is blocked or downgraded by this design dependency.
