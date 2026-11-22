# Native SCAP-NG 0.4.1 conformance corpus

This is the issue #87 native Self-Assertion and Conformance Test Content. The
active corpus is **only** the root `manifest.json`, `schema-coverage.json`,
`cases/`, `fixtures/`, and `expected/` generated from the exact canonical
0.4.1 schema family. The older `0.4/` material is retained as historical
Model-A evidence and is not an active 0.4.1 authoring corpus.

Generated Assessment YAML follows Issue #95: each Test serializes `object`
before `require` when both are present. This is deterministic presentation
order, not a language or JSON Schema rule; Issue #96's 0.5.0 `requirements`
rename is explicitly out of scope.

## Current inventory receipt

The generated inventory (`schema-coverage.json`) and conservative audit
(`coverage-audit.json`) record the source commit, whole-family digest, every
schema JSON document, `$ref`, property group, enum and constraint, plus each
supported/experimental capability mapping and its selectors, fields, datatypes,
and semantic validator rules. Regenerate it after a canonical schema change:

```sh
python conformance/tools/generate.py
python conformance/tools/runner.py validate
python conformance/tools/runner.py coverage
python -m unittest tests/test_issue87_conformance.py -v
```

The current mainline-rebased inventory is pinned to schema commit
`d1ab0283e09369c2c734d3b8f93b65007441cf07` and contains 105 capability
mappings (101 supported, 4 experimental), 35 root schemas, 146 JSON resources,
700 schema references, 142 enum nodes and 11,327 constraint nodes. The schema
family SHA-256 is
`1755c893712ef30334dc7ecadc88e5abf387c2d60a75211bc2445b7cefa2e7d4`. The exact
SHA-256 is in both generated receipts; do not edit the version label without
regenerating the complete pack.

The audit derives coverage from source mappings, authored Assessment YAML, and
corresponding fixture JSON—not from declared inventory counts or expected keys.
It finds 718/718 fields in both authored positive Assessments and positive
fixtures. Each capability has seven base vectors plus a deterministic
multi-Item vector (840 expanded capability vectors total); a dedicated suite
adds 104 applicable multi-value witnesses. Negative fixtures are derived from
each Assessment: selector fields remain unchanged when a Require field is
mismatched, and selector-only capabilities use a collected empty population.
The strict receipt oracle verifies identity, exact schema pin, fixture/expected
hashes, Test outcomes, decisive reasons, typed evidence, and provenance.
Dedicated suites cover all 67 active comparison operators, all 94 declared
selector alternatives, every cardinality token, `not_evaluated`, and
profile-disabled Rules. Native enum boundary values beyond the sentinel audit,
schema property/constraint combinations, collector execution, and scale remain
explicitly incomplete.

Authoring branches are separately witnessed: 20 schema-valid Assessments cover
both modes, all five Assessment classes, all three `reported_elements` branches
(including an explicit list), and all six manual technical-outcome choices.
Ten invalid-authoring vectors reject out-of-domain enums and representative
identifier, procedure, duplicate-list, cardinality, Variable-kind, and
specification-version constraints.

The audit also derives all 180 mapping semantic-validator rules. It marks explicit
source-shape checks (for example singleton/no-Object and resolved Variable
source) as structural witnesses. The generated `core-semantic-boundaries`
Assessment plus the fixed-result case records fifty independently justified
schema-valid semantic rule witnesses (file traversal, inline YAML content,
Windows literal-name, protocol, interface-type, family-vocabulary,
non-negative-time, materialized-default, selector equality, type compatibility,
and null-selector boundaries), with 19 structural witnesses. The remaining 111
rules are explicitly dispositioned unresolved: 81 are unsupported by the native
State-free Set/filter authoring surface, 13 are not-run pending collector/RI
receipts, and 17 are blocked on a documented semantic or normative decision.
No unresolved rule is silently counted as semantic coverage.
Core Evaluate content also covers FALSE, `not(false)`, double negation,
AND/OR/ONE/XOR, and status propagation. `not` is the only canonical negation
spelling; `negate` is an invalid-authoring regression.

The independent Model A oracle executes all 15 frozen complete-known-nonempty
integer/string cases, including aliases, duplicate preservation, expected-value
matching, and the three cardinality layers. It intentionally rejects empty,
unknown, error, and unsupported datatype cases rather than assigning outcomes.

The canonical `core-variable-interactions` Assessment separately connects a
local Variable alias to a multi-value `variable.value` Test and Require field
cardinality. Its decisive FALSE leaf is visible and enclosed only by canonical
`not`; the expected counts are independently derived from the two ordered
values.

The canonical `core-set-filters` Assessment covers shared Set operators
(`union`, `intersection`, `difference`) and both filter actions over deterministic
abstract populations. It is an independent schema/oracle witness, not proof of
collector-side Set or capability filter execution.

The canonical `core-variable-functions` Assessment covers `unique`, `count`,
`concat`, and `merge` over ordered duplicate values with local Variable
dependencies. Its expected values are independently derived and do not claim
status propagation or runtime function equivalence.

The canonical `core-input-guards` Assessment distinguishes supplied, absent,
empty, over-cardinality, and out-of-range Input bindings behind an explicit
`input_provided` guard. It proves authoring and independent binding semantics,
not Rule packaging or scanner invocation.

The canonical `core-applicability` Assessment binds a shared Assessment for
`purpose: applicability` and records applicable, NOT_APPLICABLE, and
NOT_EVALUATED handoff expectations. Graph resolution and runtime precedence
remain outside this portable corpus.

The falsifiable [Issue #87 gap matrix](GAP-MATRIX.md) separates structural,
independent-oracle, and runtime proof and records the exact RI #196 handoff.

For RI and third-party vendor reuse, see
[`ADAPTER-CONTRACT.md`](ADAPTER-CONTRACT.md) and the versioned
[`receipt.schema.json`](receipt.schema.json). They define a public adapter
workflow, five independent qualification dimensions, receipt states, and the
regression process for normative ambiguities without making any scanner the
semantic authority.

## Qualification boundary

The offline runner checks schema validity, deterministic fixture structure,
manifest hashes, expected typed outcomes, and inventory/vector completeness. It
does not execute a scanner and does not prove compliance or RI equivalence.
Scanner-neutral replay and receipt integration is coordinated with RI issue
#196. Platform collector qualification, large-scale execution evidence, and
independent multi-scanner evidence remain explicit follow-up gates rather than
being fabricated by this source corpus.
