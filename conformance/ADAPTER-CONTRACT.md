# Portable SCAP-NG conformance adapter contract

This is a scanner-neutral qualification protocol for RI and independent vendors.
An implementation under test is an adapter; it is not allowed to modify the
Assessment, fixture, expected oracle, or schema pin.

## Inputs and outputs

The adapter receives only public corpus files:

1. `manifest.json` and the exact pinned schema family;
2. one canonical Assessment;
3. one deterministic fixture variant;
4. the corresponding independent expected-result document.

It emits one `scap-ng-conformance-receipt-0.1` JSON document per
`(case_id, variant)`. The receipt MUST validate against
`receipt.schema.json` and pass `tools/oracle.py`. No private repository,
scanner-specific API, or RI implementation module is part of this interface.

The adapter MUST execute the authored Assessment without rewriting it. It MUST
bind evidence only through the selected fixture and retain acquisition status,
missing/empty populations, permission boundaries, errors, and unsupported
capabilities as typed information. A schema-valid document is not an execution
receipt.

## Qualification dimensions

Every receipt reports five independent dimensions:

| Dimension | Meaning |
| --- | --- |
| `schema` | Assessment, fixture, and receipt conform to the pinned schemas/contracts. |
| `semantic` | Independent expected outcomes and decisive reasons agree. |
| `collection` | The implementation acquired the required evidence, or explicitly reports `unsupported`, `unknown`, `error`, or `not_run`. |
| `integration` | Assessment graph, dependency, applicability, and result packaging integration. |
| `operational` | Resource limits, cancellation, scale, repeatability, and host-scope behavior. |

Allowed states are `pass`, `fail`, `unsupported`, `untested`, `not_run`, and
`blocked`. `schema` MUST be `pass` for an accepted adapter receipt; the other
dimensions are not inferred from it. Aggregated qualification reports MUST
retain per-case receipts and must not turn unsupported or untested into pass.

## Qualification workflow

A vendor can qualify incrementally:

```text
select manifest case/variant
  -> validate exact schema pin and hashes
  -> execute unchanged Assessment against deterministic evidence
  -> emit receipt
  -> run oracle.py compare
  -> aggregate receipts by capability/feature/dimension
```

The corpus publisher records the adapter name/version, source commit, receipt
hash, environment metadata, and command line outside the normative expected
files. Re-running the same public inputs must reproduce the same receipt except
for explicitly declared execution timestamps.

## Coverage and regression process

Coverage reports distinguish schema/authored, independent semantic-oracle,
collection, integration, and operational evidence. Each capability/feature is
classified as `pass`, `unsupported`, `untested`, or `failed`; absence of a
receipt is never a pass.

When a normative ambiguity or interoperability defect is found, add a minimal
positive and negative/boundary case, an independently justified expected
result, and an adversarial regression that mutates the disputed condition.
Record the source/schema pointer, decision status, and affected adapters in
`GAP-MATRIX.md`. Do not change an expected result to accommodate one scanner;
resolve normative changes in the canonical schema/specification first.
