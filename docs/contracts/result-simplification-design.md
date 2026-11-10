# SCAP-NG 0.4 Result simplification design

**Status: owner review required — canonical design only.** This document
freezes no new wire behavior. The proposal is one explicitly versioned
canonical `0.4.1` Result contract; it is not an implicit output profile.
Frozen 0.4 schemas, historical goldens, and existing consumers are unchanged.

This is the canonical design companion to the RI review at
[RI Issue #43](https://github.com/vanderpol/scap-ng-ri/issues/43) and
[RI Result simplification design](https://github.com/vanderpol/scap-ng-ri/blob/codex/result-simplification-design-ri/docs/result-simplification-design.md).

## 1. Baseline: actual `rhel9-passwd-owner-test`

The baseline is the root-backed result produced on 2026-11-10 from
`examples/rhel9-unix-file-assessment.request.json`, using the current RI
binary and `/etc/passwd` in the current mount namespace:

- Assessment: `rhel9-unix-file-assessment`, version `1`.
- Test: `rhel9-passwd-owner-test`.
- Technical outcome: `true`.
- Acquisition: `success`, root, authoritative within the current mount
  namespace; one Item evaluated and one Item retained.
- Result size: **7,064 bytes** pretty-printed JSON.
- Assessment members emitted: **21**.
- Test members emitted: **16**.
- The Test contains one retained Item with seven fields, one requirement
  result, and one field comparison. Three path-like fields are redacted.
- The result contains generated execution/collection/evidence IDs, an
  expression trace, retention configuration, timing, and duplicated reference
  paths in addition to the human decision.

The exact sanitized baseline is retained in
`docs/evidence/result-reporting/root-pass.json` and its offline report in
`root-pass.html`. The companion `fail-redacted.json` and
`unknown-incomplete.json` preserve negative and incomplete shapes. This design deliberately does **not** use the
baseline as permission to change serialization.

## 2. Recommended minimal production contract

The smallest useful interoperable Result should carry authored identity,
authored Object and Require references, decisive typed comparisons, outcome and
completeness, plus concise acquisition provenance. It should not carry an RI
execution trace. The following is a proposed profile, not valid frozen 0.4
wire JSON and not an implementation request:

```json
{
  "result_schema_version": "0.4.1",
  "assessment": {
    "id": "rhel9-unix-file-assessment",
    "version": 1,
    "title": "RHEL 9 passwd ownership example"
  },
  "purpose": "assessment",
  "class": "compliance",
  "target": {"id": "local-linux"},
  "outcome": "true",
  "summary": "PASS: Object /tests/rhel9-passwd-owner-test/object found one Item; owner_uid 0 equals expected 0.",
  "completeness": {
    "logical_complete": true,
    "population_complete": true,
    "evidence_complete": true
  },
  "tests": [
    {
      "id": "rhel9-passwd-owner-test",
      "title": "The passwd file is owned by root",
      "outcome": "true",
      "object": {
        "object_ref": "/tests/rhel9-passwd-owner-test/object",
        "capability": "unix.file",
        "selector": {"filepath": {"equals": "/etc/passwd"}}
      },
      "require": {
        "require_ref": "/tests/rhel9-passwd-owner-test/require",
        "cardinality": {
          "items_found": "one_or_more",
          "items_satisfying": "every",
          "values_found": "one_or_more",
          "values_matching": "every"
        },
        "fields": {
          "owner_uid": {
            "operation": "equals",
            "expected": {"datatype": "integer", "value": 0},
            "observed": {"datatype": "integer", "value": 0},
            "outcome": "true",
            "reason": "Observed owner_uid 0 equals expected 0."
          }
        }
      },
      "reason": "The decisive owner_uid comparison passed.",
      "counts": {"items_observed": 1, "items_evaluated": 1, "items_retained": 1}
    }
  ],
  "provenance": {
    "authority": "authoritative-within-current-mount-namespace",
    "collector": "linux.unix-file.exact.v1",
    "acquisition_status": "success",
    "privilege": "root",
    "observation_scope": "current-mount-namespace",
    "trust": "authoritative-within-current-mount-namespace",
    "acquired_at": "2026-11-10T15:30:45.614939761Z"
  }
}
```

`filepath` is shown here because this is a controlled `/etc/passwd` fixture.
A production disclosure policy may replace its value with a canonical redacted
value while retaining the Object name, selector kind, field name, and decisive
comparison. Redaction must never change `outcome` or imply completeness.

### Proposed canonical schema shape (not installed)

The coordinated schema amendment would define one `0.4.1` Result contract with
these required semantic members. This is a review shape, not a checked-in
schema resource:

```yaml
required:
  - result_schema_version   # const: "0.4.1"
  - assessment              # authored id/version; title optional if authored
  - purpose
  - class
  - target
  - outcome
  - summary
  - completeness            # logical_complete/population_complete/evidence_complete
  - tests
  - provenance              # authority, privilege, observation scope and trust
properties:
  tests.items.required:
    - id                     # exact authored Test identifier
    - outcome
    - object.object_ref      # exact authored RFC 6901 Object reference
    - require.require_ref    # exact authored RFC 6901 Require reference
    - reason
    - counts
  require.fields.*.required:
    - operation
    - expected
    - observed
    - outcome
  counts.required:
    - items_observed
    - items_evaluated
    - items_retained
```

The amendment must retain the existing technical outcome enum (`true`,
`false`, `unknown`, `error`, `not_evaluated`, `not_applicable`), existing
cardinality vocabulary, typed-value status/redaction rules, and explicit
acquisition/error distinctions. It must reject a missing authored reference;
there is no fallback generated Object or Require name.

### YAML view

The same proposal is intentionally easy for a human to read as YAML:

```yaml
result_schema_version: 0.4.1
assessment: {id: rhel9-unix-file-assessment, version: 1}
outcome: "true"
summary: "PASS: owner_uid 0 equals expected 0."
completeness: {logical_complete: true, population_complete: true, evidence_complete: true}
tests:
  - id: rhel9-passwd-owner-test
    object: {object_ref: /tests/rhel9-passwd-owner-test/object, capability: unix.file}
    require:
      require_ref: /tests/rhel9-passwd-owner-test/require
      fields:
        owner_uid:
          operation: equals
          expected: {datatype: integer, value: 0}
          observed: {datatype: integer, value: 0}
          outcome: "true"
          reason: Observed owner_uid 0 equals expected 0.
    reason: The decisive owner_uid comparison passed.
provenance:
  authority: authoritative-within-current-mount-namespace
  collector: linux.unix-file.exact.v1
  privilege: root
  observation_scope: current-mount-namespace
  trust: authoritative-within-current-mount-namespace
```

The proposed field names are descriptive of the language, not an RI object
model. Independent scanners can produce the same logical structure without
sharing RI IDs, caches, or trace formats.

## 3. Required outcome examples

These are compact profile examples. They are semantic fixtures for coordinated
canonical conformance, not frozen Result files.

### Decisive Pass

```json
{"outcome":"true","summary":"PASS: owner_uid 0 equals expected 0.","completeness":{"logical_complete":true,"population_complete":true,"evidence_complete":true},"tests":[{"object":{"object_ref":"/tests/rhel9-passwd-owner-test/object"},"require":{"require_ref":"/tests/rhel9-passwd-owner-test/require","fields":{"owner_uid":{"expected":0,"observed":0,"operation":"equals","outcome":"true"}}},"outcome":"true"}]}
```

### Decisive Fail

```json
{"outcome":"false","summary":"FAIL: owner_uid 1001 does not equal expected 0.","completeness":{"logical_complete":true,"population_complete":true,"evidence_complete":true},"tests":[{"object":{"object_ref":"/tests/rhel9-passwd-owner-test/object"},"require":{"require_ref":"/tests/rhel9-passwd-owner-test/require","fields":{"owner_uid":{"expected":0,"observed":1001,"operation":"equals","outcome":"false","reason":"Observed owner_uid 1001 does not equal expected 0."}}},"outcome":"false"}]}
```

### Unknown from insufficient visibility

```json
{"outcome":"unknown","summary":"UNKNOWN: the observed Item satisfied the requirement, but population completeness cannot be established for non-root visibility.","completeness":{"logical_complete":true,"population_complete":false,"evidence_complete":false},"tests":[{"object":{"object_ref":"/tests/rhel9-passwd-owner-test/object"},"require":{"require_ref":"/tests/rhel9-passwd-owner-test/require","fields":{"owner_uid":{"expected":0,"observed":0,"outcome":"true"}}},"outcome":"unknown"}],"provenance":{"privilege":"unprivileged","trust":"non-authoritative","limitations":["inaccessible populations may not produce permission errors"]}}
```

### Incomplete/cancelled collection

```json
{"outcome":"unknown","summary":"UNKNOWN: collection stopped before a complete population was established; no compliance pass or fail was asserted.","completeness":{"logical_complete":true,"population_complete":false,"evidence_complete":false},"tests":[{"object":{"object_ref":"/tests/rhel9-passwd-owner-test/object"},"require":{"require_ref":"/tests/rhel9-passwd-owner-test/require"},"outcome":"unknown"}],"provenance":{"acquisition_status":"incomplete","trust":"untrusted","limitations":["cancelled before collection completed"]}}
```

### Redacted evidence

```json
{"outcome":"true","summary":"PASS: owner_uid 0 equals expected 0; filepath value redacted.","completeness":{"logical_complete":true,"population_complete":true,"evidence_complete":true},"tests":[{"object":{"object_ref":"/tests/rhel9-passwd-owner-test/object","selector":{"filepath":{"redacted":true}}},"require":{"require_ref":"/tests/rhel9-passwd-owner-test/require","fields":{"owner_uid":{"expected":{"datatype":"integer","value":0},"observed":{"datatype":"integer","value":0},"outcome":"true"}}},"outcome":"true"}],"provenance":{"privilege":"root","trust":"authoritative-within-current-mount-namespace"}}
```

A missing file or permission denial is an acquisition status/error and does not
become a synthetic Item or compliance failure. An observed decisive failure
may remain `false` under incomplete population only when unseen evidence cannot
reverse that authored condition; an apparent complete-population pass may not.

## 4. Expanded conformance design

The singleton sample is insufficient to approve the contract. The canonical
conformance set must add semantic fixtures using the exact Object and Require
references authored in each fixture; no fixture name or reference may be
invented by a renderer:

| Case | Required evidence and explanation |
|---|---|
| Multiple Items | Two or more Items under the authored `object_ref`; preserve observed/evaluated/retained counts and identify the decisive Item only when retained by policy. |
| Multiple field values | One Item field with a typed value array; preserve `values_found`, `values_matching`, expected/observed arrays and the decisive comparison. |
| Item cardinality | `items_found`/`items_satisfying` `none`, `exactly_one`, `one_or_more`, `every`, and a failing count; no empty-set inference. |
| Field cardinality | `values_found`/`values_matching` `none`, `one_or_more`, `every`, and a mismatch; distinguish field absence from Item absence. |
| AND / OR | Assessment expression with two authored Test references; report each Test and the expression outcome without serializing an engine trace. |
| Variables | Use actual authored identifiers such as `oval-org-mitre-oval-test-var-641-variable` and `oval-org-mitre-oval-test-tst-695-test` from the pinned constant fixture; report resolved expected values and preserve variable references. |
| Inputs | Add a canonical organizational-input fixture with its authored input-set/parameter identifiers; report presence, provenance and redaction without fabricating an input name. This is an unresolved fixture gap, not a claim of current RI Input execution. |
| Missing / error | Missing file, denied access and unsupported operation remain acquisition states with no synthetic Item. |
| Unknown / incomplete | Partial visibility, cancellation and incomplete evidence cannot produce an authoritative pass; a decisive irreversible failure may remain false. |
| Redaction | Redact path/secrets and, when required, decisive values while retaining typed status, comparison outcome, completeness and reason. |

A multi-Item semantic witness should therefore look like this (all angle-bracket
references are resolved from the authored fixture before emission):

```json
{
  "result_schema_version": "0.4.1",
  "tests": [{
    "id": "<authored-test-id>",
    "object": {"object_ref": "/tests/<authored-test-id>/object"},
    "require": {
      "require_ref": "/tests/<authored-test-id>/require",
      "cardinality": {"items_found":"one_or_more", "items_satisfying":"every",
        "values_found":"one_or_more", "values_matching":"every"},
      "fields": {"owner_uid": {
        "expected": [{"datatype":"integer","value":0}],
        "observed": [{"datatype":"integer","value":0}, {"datatype":"integer","value":0}],
        "outcome":"true", "reason":"Every observed owner_uid equals expected 0."
      }}
    },
    "counts": {"items_observed":2, "items_evaluated":2, "items_retained":1},
    "outcome":"true"
  }]
}
```

This fragment intentionally does not assign a name to the Object or Require;
the authored reference is the identity. The eventual conformance fixtures must
validate this shape alongside the full Result contract and test AND/OR,
Variable and Input dependency semantics independently.

## 5. Audit of the current frozen Result shape

This is a semantic audit, not permission to delete fields.

### Assessment-level members

| Current member | Classification | Reason / proposed disposition |
|---|---|---|
| `result_schema_version` | necessary | Wire/schema negotiation. |
| `execution_id` | diagnostic/interoperability | Useful correlation, but not human compliance information; move to optional diagnostics if canonical owners agree. |
| `assessment` | necessary | Identity and version; title/name should be available without reopening content. |
| `purpose`, `class` | necessary | Outcome meaning depends on them. |
| `outcome`, `summary` | necessary | Machine and human decision. |
| `logical_complete`, `population_complete`, `evidence_complete` | necessary but duplicated shape | Retain semantics; consider one named completeness object in a future version. |
| `tests` | necessary | Portable Test-level truth. |
| `objects` | necessary but currently reference-heavy | Keep collection status/completeness and safe Object identity; remove duplicate generated IDs from the minimal contract. |
| `variables` | conditional | Required only when Variables participate; empty arrays are serialization scaffolding. |
| `diagnostics` | conditional | Needed for acquisition/evaluation errors; routine timing/details do not belong here. |
| `mode`, `target_ref` | necessary/conditional | Mode is useful; target identity is necessary when it affects scope. |
| `expression_execution` | diagnostic-only in minimal profile | Repeats outcome/executed Test information and embeds RI-like traces. Preserve in optional diagnostics. |
| `field_uses` | conditional/diagnostic | Needed only for cross-reference explanation; empty baseline is redundant. |
| `dependent_assessments` | conditional | Needed for dependency consumers, not a routine singleton scan field. |
| `evidence_retention` | diagnostic/control metadata | Describes scanner policy, not compliance truth; move to diagnostic/evidence contract. |
| `evidence` | necessary provenance, too broad in current position | Keep a bounded provenance summary in the production result; move timing, collector internals and extensive limitations to the optional contract. |

### Test, collection, and evidence members

| Current member/group | Classification | Finding |
|---|---|---|
| `tests[].id`, `test_title`, `outcome`, `reason` | necessary | Recognizable decision and explanation. |
| `object_refs` + `objects[].id` | duplicated | Keep the actual authored RFC 6901 Object reference; do not invent a display name. A human title is optional only when authored. |
| `require_refs`, `decisive_require_refs` | duplicated | Keep the actual authored RFC 6901 Require reference plus decisive field entries; do not invent a Require name. |
| `item_refs`, `evidence_refs`, `per_item_results[].item_ref`, `objects[].item_refs` | duplicated/reference machinery | Keep bounded evidence references only where a consumer needs correlation; do not repeat the same opaque ID at four levels. |
| `per_item_results` and `require_results.field_results` | necessary | This is the canonical location for bounded decisive comparisons; it must not be replaced by free-form prose. |
| `item_summary`, `items_observed`, `items_found`, `items_satisfying`, `field_requirement` | necessary semantics, partly duplicated | Keep cardinality controls and concise counts, but consolidate duplicate count projections in a future profile. |
| `invocation_ref`, `binding_set_id` | diagnostic-only | Correlation/cache execution details; not needed for ordinary compliance review. |
| `existence_outcome` | conditional | Needed only when Item existence and field compliance differ. |
| `objects[].capability`, `status`, completeness, `stop_reason`, diagnostics | necessary acquisition semantics | Keep compact collection status and stop reason; omit generated collection IDs from minimal output. |
| Item `id`, `capability`, `status`, `fields`, `provenance` | necessary but bounded | Retain only safe fields and provenance summary under an explicit cap/redaction policy. |
| Item `context`, locators/materialization extensions | conditional/diagnostic | Keep only for capabilities that require them; never emit empty machinery in a singleton profile. |
| Evidence acquisition status, collector, timestamps, privilege, scope, trust, limitations | necessary provenance, separate contract preferred | Keep a short production provenance summary; extensive timings and limitations belong in the diagnostic/evidence sidecar. |

## 6. Optional diagnostic/evidence contract

A separate, content-addressed diagnostic object should carry execution detail
without making it part of the ordinary production Result:

```json
{
  "diagnostic_schema": "scap-ng.result-diagnostic.1",
  "result_digest": "sha256:<production-result>",
  "execution": {
    "execution_id": "execution-...",
    "invocation_ref": "...",
    "expression_trace": [],
    "cache_reuse": [],
    "duration_ns": 208841
  },
  "acquisition": {
    "collector": "linux.unix-file.exact.v1",
    "collection_ref": "collection-...",
    "evidence_refs": ["evidence-..."],
    "acquired_at": "...",
    "completed_at": "...",
    "limitations": []
  },
  "retention": {"scope":"per_test","maximum_items":1,"source":"scanner_configuration"}
}
```

This sidecar is optional, bounded, separately permissioned, and never a source
of compliance truth. It must not contain privileged raw evidence unless the
operator explicitly authorizes that disclosure. The production Result remains
self-explanatory without opening the sidecar.

## 7. Size and structural comparison

The actual current baseline is 7,064 bytes pretty JSON, 21 Assessment members,
16 Test members, 1 Item, 7 Item fields, 1 Require result and 1 Field result.
The proposal above is 2,111 bytes pretty JSON / 1,499 compact bytes when
serialized with the sample values: approximately **70.1% smaller pretty** and
**78.8% smaller compact**. It has 10 top-level members (including identity, target and completeness), 1 Test, 1 Object reference, 1 Require reference, 1 decisive Field comparison and 1 provenance summary. The
size is not itself normative; redaction, localized titles, and implementation
formatting will change it. The important reduction is removal of generated
execution machinery and repeated opaque references, not removal of semantic
counts or completeness.

## 8. Compatibility and migration

1. Frozen SCAP-NG 0.4 Results remain accepted and are never rewritten in place.
   Historical evidence keeps its original bytes and schema version.
2. A future minimal contract must have explicit canonical negotiation, as one explicitly versioned canonical `0.4.1` Result contract. It must not be
   inferred from missing fields in a historical 0.4.0 Result.
3. Consumers should first normalize either profile into a semantic view of
   Assessment/Test/Object/Require/comparison/completeness/provenance. Legacy
   consumers continue to receive the existing full Result.
4. A full-to-minimal adapter can discard traces and raw values under policy,
   but must preserve `unknown`, incomplete, acquisition errors, counts and
   decisive comparisons. A minimal-to-full adapter cannot fabricate execution
   IDs, traces, cache reuse, or missing evidence; it may only create an
   explicitly marked projection.
5. Existing JSON Schema validators reject the proposed members today because
   the frozen schemas use `additionalProperties: false` in relevant nodes.
   This is an intentional contract gap, not a reason to weaken validation.
6. Conformance must add equivalent Pass, Fail, Unknown, incomplete, missing,
   denied and redacted fixtures, plus 0.4.0-to-0.4.1 semantic equivalence tests.

## 9. Decisions requested

Owner approval is requested for the direction, not for implementation:

- whether the single canonical `0.4.1` Result contract within SCAP-NG 0.4 is
  approved as the successor for new Results while 0.4.0 bytes remain historical;
- whether `assessment_title`, actual authored Object/Require references and the
  compact completeness/provenance objects are normative members;
- the exact redaction and privilege/trust vocabulary;
- whether the diagnostic contract is a separate file, a Result package member,
  or an optional canonical member;
- migration and retention requirements for consumers and historical evidence.

Until these decisions are approved, RI will not change its Result serialization
or add further format-specific patches.
