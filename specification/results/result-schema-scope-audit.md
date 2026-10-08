# Result schema scope audit

Status: current-design architectural audit after the Rule Result scope defect.

## Ownership model

The canonical result hierarchy is:

```text
Scan Result
  -> Benchmark Result
       -> Rule Results
            -> Assessment Result references
                 -> Test/Object collection/Item/State/Entity/Variable detail
```

Each layer has one primary responsibility:

| Layer | Owns | Does not own |
| --- | --- | --- |
| Scan Result | run identity, scanner identity, targets, package/index references, signature status | effective Benchmark policy, Rule outcomes, Assessment execution graphs |
| Benchmark Result | Benchmark identity, target reference, effective policy, summary, collection of Rule Results | full scanner/target records, detailed Assessment execution |
| Rule Result | effective Rule policy context, outcome/reason, selected Assessment identity, invocation references, applicability, **compact typed decisive findings** and optional population counts | raw collected Item records, full State/entity trees, Variables, Test/Object execution graphs, full evidence ledger, consumed Organizational Input provenance |
| Assessment Result | one Assessment invocation, technical truth, Test/Object/Item/State/Entity/Variable graph, effective bindings, consumed Organizational Inputs, completeness and detailed evidence accounting | Benchmark policy aggregation or run-wide scanner/target inventory |
| Test Result | one Test's aggregation and per-Item State results | Rule policy or run/Benchmark metadata |
| Object Collection Result | one Object collection execution and Item references | State comparison or Rule policy |
| Collected Item | one observed Item and provenance | policy interpretation |
| State Result | one State evaluation for one Item | Rule policy |
| Entity Result | one State-entity comparison/aggregation | run/Benchmark/Rule policy |
| Variable Result | one resolved runtime Variable value set and provenance | run/Benchmark/Rule policy |

A derived SIEM/JSONL projection may intentionally denormalize these layers for
query convenience. That projection is not authoritative schema ownership.

**0.3 intentional overlap (#203):** A Rule Result in its parent Benchmark Result
may repeat a limited, typed actual-versus-expected fact and associated
subject because readers must understand why the Rule passed/failed without
joining a Test/Object/State/Item graph. These facts are deterministic
projections, not independently evaluated truth or full collected Item records.
Collection counts distinguish evaluated Items from returned evidence. Detailed
Assessment Results remain authoritative and independently scannable.

## What went wrong

The Rule Result defect was introduced structurally rather than by JSON Schema
generation.

1. The first Benchmark Result schema defined Rule Results inline.
2. Organizational Input execution detail and mandatory expected-State detail
   were added to that inline Rule shape while the ownership boundary was still
   unclear.
3. The inline Rule shape was later extracted wholesale into
   `rule-result.schema.json`. Extraction made the shape look like an
   independent, authoritative contract even though it had already crossed the
   policy/execution boundary.
4. Later work added observed State and bounded-evidence summary fields to make
   Rule Results more "self describing." That interpreted self-description as
   duplication of Assessment detail rather than references to the authoritative
   Assessment Result.
5. Fixtures and regression tests then copied the same fields, turning the design
   mistake into a regression expectation.

JSON Schema validation could not catch this because every duplicated field was
syntactically valid. This was an architectural ownership error, not a structural
validation error.

## Corrective changes

The audit made these corrections:

- Rule Result is a compact policy-facing child of Benchmark Result.
  `expected_state`, `observed_state`, `organizational_inputs`, and
  `evidence_summary` were removed from Rule scope. For 0.3, bounded
  `findings` and optional `finding_counts` restore a useful typed
  explanation without restoring the detailed child execution graph.
- Benchmark Result now references the Scan-level target with `target_ref`;
  run-wide `scanner` and full `target` records are no longer duplicated.
- Detailed Test/Object/Item/State/Entity/Variable schemas are explicitly closed
  at their top-level object boundaries so undocumented cross-layer fields cannot
  silently validate.
- Regression fixtures and JSONL projection tests were aligned with the normalized
  ownership model.
- `tools/test_result_schema_scope.py` provides an architectural guard that
  fails if known cross-layer fields return to the wrong canonical schema.

## Deliberate duplication that remains

Some repeated information is intentional and has a different role rather than a
competing source of truth:

- Scan Result Benchmark entries may retain compact Benchmark/profile/summary
  information because they are an index.
- Benchmark Result keeps `run_id` for correlation with the owning Scan Result.
- Benchmark Result owns the effective Organizational Input registry/provenance;
  an Assessment Result records only the bindings/inputs actually consumed by
  that invocation.
- Rule Result may retain effective weight, selector, parameters, applicability
  disposition, and Assessment identity because those are policy context needed
  to interpret the Rule outcome.
- Entity comparison results may repeat typed operands needed to explain the
  comparison. They remain inside the same Assessment execution layer and do not
  create a competing policy-level source of truth.

## Audit findings that are not scope defects

The following deserve continued schema-quality review but are not the same
cross-layer ownership problem:

- `assessment_result.selected_branch` is a reserved future field. Whether to
  keep or remove speculative conditional-result syntax is a separate design
  decision.
- Several diagnostic/provenance payloads are intentionally open objects pending
  their final schemas.
- `manual-assessment-result.schema.json` remains a design/probe schema while
  canonical Assessment Result also supports manual execution provenance. Its
  eventual disposition should be handled as manual-result consolidation, not as
  Rule/Assessment scope leakage.

## Prevention rule

For canonical result schemas, a parent may reference or summarize a child but
SHOULD NOT duplicate the child's authoritative execution graph. Any intentional
denormalization must be documented as an index, projection, or compact policy
context. New canonical result properties should be checked against the ownership
table before being accepted.


## Second-pass schema boundary audit

A follow-up audit checked the remaining canonical result/source schemas for the
same two failure modes: speculative syntax and structurally complete records
that nevertheless accepted arbitrary properties.

Changes made in this pass:

- removed `assessment_result.selected_branch`; it was explicitly reserved for
  a future conditional-result design and had no current normative semantics;
- closed Assessment Result manual-response, consumed Organizational Input,
  reason, and input-binding records where their current property sets are
  already explicit;
- closed reusable `typed_value` objects;
- closed Scan Result target and Benchmark-index records;
- closed the Benchmark platform record and Organizational Input intended-scope
  record.
- removed the authored Test-level `result` field from `assessment.schema.json`; runtime Test outcomes belong only in result artifacts.

Open maps remain open only where extensibility is intentional, including
capability-specific Assessment structures, Parameter/input constraint payloads,
scanner implementation metadata, summary aggregates, and provenance/extension
maps whose vocabulary has not yet been standardized.

The regression guard now tests both layer ownership and these canonical
boundary decisions.

## Executable source-boundary follow-up — 2026-10-02

Removing `result` from the authored Test property list did not actually reject
it: capability-specific named nodes deliberately allow additional properties.
The previous guard checked property declarations rather than validating an
instance containing a runtime result, so this residual scope leak passed.

The structural Assessment schema now explicitly rejects a top-level `result`
property on named Tests, Objects, States and Variables while keeping their
capability payloads extensible. The instance regression covers scalar, null and
object-shaped runtime results on all four node families. A WMI State selecting
an observed field named `result` remains valid: that is an authored data-field
selection inside the State payload, not an attached runtime outcome.

This is an architectural boundary check, not deep capability validation or
proof of evaluator equivalence. Provenance: **Evidence/Audit**, reproduced from
the checked-in schema and corrected with failing-then-passing instance tests.

### Corpus follow-up: objectless unknown Tests

Run 37002838788 at `7cff61a364123f060c1d82a59fa213577f77df91` validated
25,147 fresh NIWC Current native documents and rejected 34. Every rejection was
the converter's authored `result: unknown` on `independent.unknown` Tests.
The pinned OVAL independent XSD defines `unknown_test` as always producing
unknown, without an Object, and ignores its required `check` value.
The converter now expresses this through the capability alone; the reverse
emitter recognizes that capability directly. The runtime-result prohibition is
retained. `tools/test_unknown_test_roundtrip.py` covers source lowering, native
schema acceptance, rejection of an attached runtime result and objectless reverse
conversion with several valid source `check` values. Artifact replay and fresh
CI generation are separate evidence gates; a replay is not a fresh conversion.
