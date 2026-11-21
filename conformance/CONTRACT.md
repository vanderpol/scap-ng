# SCAP-NG 0.4.1 conformance contract

This directory is the implementation-neutral source oracle for issue #87. It is
pinned to the exact `schema_commit` and `schema_family_sha256` in `manifest.json`.
The inventory is generated from the flat `schema/` directory and capability
mappings; it is not a second hand-maintained grammar.

## Case tuple

Each capability has one schema-valid Assessment, a deterministic evidence fixture,
and an expected-result document. A vector is identified by
`(case_id, fixture_variant)`. The fixture is a replay input, not an evaluator
output. Expected results are independent oracle assertions.

Every ordinary capability case provides:

* `positive`: one collected Item and every declared field matching;
* `negative`: one decisive field mismatch, expected `false` (never hidden by `not`);
* `boundary`: minimum non-empty Item/field cardinalities;
* `empty`: no evidence, expected `unknown`;
* `permission-denied`: acquisition denied, expected `unknown`;
* `error`: collector error, expected `error`;
* `not-applicable`: typed applicability result, expected `not_applicable`;
* `multi-item`: two distinct matching Items;
* selector-only capabilities use an empty collected population for the negative
  vector, because no non-selector Require field exists to mutate.

Dedicated core suites additionally provide all 67 active comparison operators,
all 94 mapping-declared selector alternatives, all Item/field cardinality
values, 103 applicable multi-value field witnesses, typed `not_evaluated`, and
profile-disabled Rule witnesses. These are schema-valid semantic witnesses;
collector execution remains outside this source oracle.

`items_found` and `items_satisfying` remain separate cardinality observations.
A status is not Booleanized. A scanner MUST NOT turn missing evidence or ERROR
into success by applying `not`.

## Replay adapter interface

An adapter (RI issue #196) consumes `manifest.json` and emits a JSON receipt:

```json
{
  "format": "scap-ng-conformance-receipt-0.1",
  "schema_version": "0.4.1",
  "schema_commit": "<exact manifest commit>",
  "case_id": "windows.registry",
  "variant": "positive",
  "assessment_outcome": "true",
  "test_outcomes": {"windows-registry-test": "true"},
  "items_found": 1,
  "items_satisfying": 1,
  "decisive_reason": "...",
  "evidence": [{"item_id": "...", "field": "...", "status": "collected", "value": "..."}]
}
```

Allowed typed outcomes are `true`, `false`, `unknown`, `error`,
`not_applicable`, `not_evaluated`, and any additional status explicitly admitted
by the pinned result contract. Adapters must preserve source statuses and report
unsupported collector capabilities separately from schema validity. Receipts
must include fixture and expected-file SHA-256 values in a production run.

## Evaluate and `not`

`not` is the sole canonical negation syntax. `negate: true` is invalid. The core
Assessment contains an underlying FALSE leaf, `not(false)`, double negation,
and `and`/`or`/`one`/`xor` interaction. Comparators must assert the underlying
FALSE and the enclosing TRUE independently. Status propagation for UNKNOWN,
ERROR, and NOT_APPLICABLE is asserted without assuming that NOT_APPLICABLE is a
plain Boolean; adapters must follow the canonical result contract.

## Qualification boundary

`tools/runner.py validate` proves only schema and fixture contract validity.
`coverage` proves inventory/vector presence. Neither establishes scanner support,
execution equivalence, or compliance. An RI receipt and independent source
oracle comparison are separate gates. Platform/collector qualification and
scale evidence are intentionally tracked as adapter increments rather than
invented by this portable corpus.
