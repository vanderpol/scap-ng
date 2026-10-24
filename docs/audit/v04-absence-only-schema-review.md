# 0.4.0 absence-only schema review — #248 / #251

**Status: schema-only candidate awaiting owner review (2026-10-24).** No
converter, compiler, scanner, normative specification, or result evaluator was
changed. Schema validation alone does not prove six-state runtime parity.

## Recovered requirement and original source

On 2026-09-28 the owner requested first-class State-entity absence distinct
from comparing observed values. The 0.3 round-trip tests already distinguished
State entity `check_existence` from Test Item `check_existence`. On 2026-10-24
the owner selected one canonical comparator-free spelling, with no aliases:
`field: {values_found: none}`. The language must also distinguish confirmed
absence from empty strings, incomplete collection, error, and unknown.

Pinned OVAL-Community Self-Assertion source: `e3538595c5083b9c34d937a81d319234df9bbfaa`,
`SCAP_1.4/OVAL_Test_Content/macos/macos-def_gatekeeper_test.xml`.
Its Gatekeeper State checks `enabled` equals boolean `1` **and** has
`<unlabeled check_existence="none_exist"/>`, without a comparison operand.
The official OVAL 5.12.3 macOS Definitions XSD declares `unlabeled` as
`EntityStateStringType`; the shared State-entity base defines `check_existence`.
This is a language-conformance fixture, not evidence that macOS Gatekeeper is a
supported 0.4.0 runtime capability.

### Proposed native requirement (illustrative Test fragment)

```yaml
require:
  items_found: one_or_more
  items_satisfying: every
  fields:
    enabled: {equals: true, values_found: one_or_more, values_matching: every}
    unlabeled: {values_found: none}
```

There is no `values_matching`, comparator, datatype, or expected operand for
`unlabeled`. A compared field still requires both count properties unless a
nearer `field_requirement` supplies them. A local absence-only field overrides
the inherited pair. `values_matching: none` is a different requirement: actual
values exist and none match a specified comparator.

The candidate also applies the same one-form rule to record-member fields and
the record wrapper: `record: {records_found: none}`. This consistency extension
needs explicit owner review; it is not evidence that a source OVAL record case
has been proven. A shared `field_requirement` pair may not encode absence-only
using `values_found: none` plus a meaningless matching count.

## Rejected alternatives and proof boundary

- Reject `absent: true`, `exists: false`, `require: none_exist`, `equals: null`,
  a comparator alongside `values_found: none`, and a redundant matching count.
- Reject record absence with `records_matching` or nested member predicates.
- Preserve ordinary comparisons, `values_matching: none`, explicit
  `field_requirement` inheritance/overrides, and `and`/`or`/`one`/`xor` logic.
- Keep source lexical comparison operands and existence attributes in migration
  provenance when required; do not manufacture comparison operands in authoring.
- A scanner must distinguish confirmed field absence from an empty value, an
  uncollected field, incomplete/error collection, or unknown status. JSON Schema
  cannot establish these runtime outcomes; separate semantic tests are required
  before a release claim.

## Validation and compatibility

The focused `test_v04_field_requirement_schema` and `test_v04_schema_draft`
suites include positive/negative schema acceptance for direct fields, inherited
scopes, record members, record wrappers, and obsolete alternatives. The wider
schema/generator and integration tests must run before promotion. Earlier
generated outputs such as `values_found: none` **with** a comparator will be
rejected by this strict authoring candidate; those outputs require a separately
reviewed converter migration, not an alias.

The existing `test_v04_clear_cardinality_schema` checks the entire field and
record existence × matching token cross-product. No combinations were removed
from the test: those using `found: none` with a redundant matcher/comparator now
must fail validation; each absence-only count has one positive form. The
previous cross-product accepted all such pairings. This acceptance change is
intentional in the candidate but requires owner review before promotion.

The older `test_v04_scalar_none_exist_source` fixture still builds deprecated
`states` and scalar `require` output. It is source-backed evidence of the need
for follow-up converter migration, not a reason to restore those aliases in
the schema or to claim the source-to-current-language path is already green.

Other open semantic boundaries are **not resolved** here: Item-level
`items_found: none` combined with satisfaction/field predicates, the OVAL
`all_exist` vs `at_least_one_exists` population issue, and exact scanner
propagation of missing/error/unknown field statuses. Each needs an independent
source-backed review rather than an inferred syntax change.
