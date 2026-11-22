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

Newly generated 0.4.1 Assessment YAML follows Issue #95 presentation order in
each Test: identification/metadata, `capability`, `object` when present,
`require`, then `reported_elements`. This is serialization guidance only; JSON
object order is not schema semantics and existing historical evidence is not
rewritten solely for formatting.

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
values, 104 applicable multi-value field witnesses, typed `not_evaluated`, and
profile-disabled Rule witnesses. `core-semantic-boundaries` adds paired,
schema-valid file-selection cases for five mapping semantic rules. Its
semantic `error` assertions mean the authored combination must be rejected by
a semantic validator before collection; they are not scanner execution
receipts. Positive cases carry deterministic typed Item evidence, while
rejected cases explicitly carry `not_run` and zero evidence. Collector execution
remains outside this source oracle.

Authoring/schema branches are tracked separately from executable semantics:
20 cases cover both automated/manual modes, all five Assessment classes, all
three `reported_elements` branches, and all six manual technical outcomes.
Invalid enum vectors are required to fail schema validation. These cases do not
select a manual response or assert a scanner result.

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
  "fixture_sha256": "<fixture bytes>",
  "expected_sha256": "<expected bytes>",
  "assessment_outcome": "true",
  "test_outcomes": {"windows-registry-test": "true"},
  "items_found": 1,
  "items_satisfying": 1,
  "decisive_reason": "All declared fields match the collected Item.",
  "evidence": [{"item_id": "...", "field": "...", "datatype": "string", "status": "collected", "value": "..."}],
  "provenance": {
    "source": "deterministic-fixture",
    "fixture_variant": "positive",
    "fixture_sha256": "<fixture bytes>",
    "expected_sha256": "<expected bytes>",
    "schema_commit": "<exact manifest commit>"
  }
}
```

The oracle rejects missing identity, hash, outcome, decisive-reason, typed
evidence, or provenance fields; it verifies every witness against the selected
fixture Item/field and requires Test outcome keys to exactly match the authored
Assessment. Item-level evidence uses `field: null`, `datatype: record`, and the
Item field map as its value. Adapters must not report a receipt whose evidence
or provenance is merely asserted rather than byte-linked.

Allowed typed outcomes are `true`, `false`, `unknown`, `error`,
`not_applicable`, `not_evaluated`, and any additional status explicitly admitted
by the pinned result contract. Adapters must preserve source statuses and report
unsupported collector capabilities separately from schema validity. Receipts
must include fixture and expected-file SHA-256 values in a production run.

## Independent Model A oracle

`conformance/tools/model_a_oracle.py` is a separate truth oracle for the owner-approved
complete-known-nonempty integer/string Model A domain. It preserves one logical
Variable source group, ordered duplicate values, and independently folds
`value_match`, `values_found`, `values_matching`, `items_found`, and
`items_satisfying`. `tests/test_model_a_oracle.py` executes all 15 frozen Model A
cases with hard-coded normative outcomes and rejects empty/out-of-domain inputs.
It does not implement unknown/error/empty status precedence or scanner
collection; those remain explicitly outside this oracle and RI #196.

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

## Portable vendor qualification

`receipt.schema.json` is the versioned, implementation-independent receipt
contract. `ADAPTER-CONTRACT.md` defines the public adapter workflow and
qualification dimensions. A vendor or RI adapter consumes only public manifest,
Assessment, fixture, expected, and pinned-schema bytes and emits one receipt
per `(case_id, variant)`. It must not import or rewrite scanner-specific corpus
logic. `tools/oracle.py` remains the independent comparison authority.

Receipts classify `schema`, `semantic`, `collection`, `integration`, and
`operational` evidence independently as `pass`, `fail`, `unsupported`,
`untested`, `not_run`, or `blocked`. Missing receipts and unsupported behavior
are not success. Expected results never come from an implementation under test.
Normative ambiguities require a minimal paired witness, independent expected
result, and adversarial mutation regression recorded in `GAP-MATRIX.md` before
an outcome or schema contract is changed.
