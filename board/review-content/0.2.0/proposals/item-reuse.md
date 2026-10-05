# Proposed collected-Item reuse syntax

**Status:** Board/design proposal. The result-side verified import/materialization
contract exists today, but native Assessment 0.2.0 does not yet have an authored
consumer contract for reusable Items. These files make that missing language
surface concrete before schema adoption.

## Why two layers are necessary

Reusable Assessment source cannot safely contain a prior execution ID, result
artifact digest, target reference, binding-set ID, or source Item IDs because
those values do not exist until a run has happened.

The proposal therefore separates:

1. **Assessment source contract** — declares the capability and semantic source
   from which reusable Items are acceptable.
2. **Assessment Request/runtime binding** — identifies and cryptographically pins
   the exact prior result artifact and exact Items used for this invocation.

This is deliberately different from an Assessment-result dependency. A result
dependency consumes another Assessment's technical outcome. Item reuse consumes
canonical collected observations and evaluates them locally under the consumer's
own States, Tests, and evaluate expression.

## Proposed author view

The consumer declares an `item_inputs` entry:

```yaml
item_inputs:
  configuration-file-items:
    capability: unix.file
    required: true
    source_contract:
      assessment_id: board.shared-file-collection
      assessment_version: 1
      object: configuration-files
    reuse_constraints:
      target: same
      bindings: exact
      preserve_source_completeness: true
```

A normal native Object then uses those Items:

```yaml
objects:
  imported-configuration-files:
    capability: unix.file
    items:
      input: configuration-file-items
```

All normal State/Test logic remains local and visible. The imported source
Assessment's pass/fail result is never reused as this Test's truth.

## Proposed runtime binding

The Assessment Request supplies the exact prior artifact and identities:

```yaml
item_bindings:
  configuration-file-items:
    result_artifact: prior-collection.result.json
    source_digest: sha256:<exact-result-artifact-digest>
    source_execution_id: <exact-source-execution-id>
    source_object: configuration-files
    target_ref: <exact-target-reference>
    binding_set_id: <exact-nonempty-binding-set-id>
    item_refs: [...]
    id_map: {...}
```

This corresponds directly to the existing verified-import implementation: exact
UTF-8 source bytes are digest-pinned, source execution/target/bindings are
checked, selected Item IDs are explicit, local IDs are collision-checked, and
source completeness/provenance is retained.

## Questions this exposes for Board/design review

- Is `item_inputs` the right native term, or should this be framed as an
  imported/reusable Object source?
- Should the source contract name an Assessment + Object as shown, or a
  separately named collection identity that can be shared by multiple Assessments?
- Is `same target + exact bindings` the only v0.2.0 reuse policy, leaving
  freshness/cache equivalence for a later version?
- Should the consumer be allowed to select a subset of source Items by Item ID
  only at request time, or should ordinary native Object/Set/filter logic be the
  only way to narrow a reusable population after import?
- Should import authorization/trust be expressed in the Assessment Request,
  package/trust policy, or both?

The current result-side contract already answers one point: imported Items are
materialized locally with full provenance; the consumer does not depend on an
opaque external join to explain its result.
