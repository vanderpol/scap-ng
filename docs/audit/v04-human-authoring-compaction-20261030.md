# 0.4.0 readable Test `require`: opt-in review candidate (2026-10-30)

**Status: candidate, not a new final release or scanner proof. Refs #264.**

The 0.4.0 canonical Assessment JSON Schema already accepts a Test-wide
`require.field_requirement` pair. The direct OVAL converter repeated the
identical `values_found` and `values_matching` on each predicate, and split
each scalar field of a single source OVAL State into an explicit `and` branch.
This needlessly inflated simple Tests and contradicted the agreed direction
for inherited field requirements.

## Original source-backed Windows registry example

The pinned Windows direct-converter fixture includes DISA
`SV-278080r1180946`, source Test `oval:mil.disa.stig.win:tst:25335200`, and
source State `oval:mil.disa.stig.win:ste:20000001`: the Windows lock-screen
slideshow registry DWORD must equal 1. Only the Test `require` is shown.

Before:

```yaml
require:
  items_found: one_or_more
  items_satisfying: every
  and:
    - fields:
        type: {equals: dword, values_found: one_or_more, values_matching: every}
    - fields:
        value: {equals: 1, datatype: integer, values_found: one_or_more, values_matching: every}
```

With `--human-compact`:

```yaml
require:
  items_found: one_or_more
  items_satisfying: every
  field_requirement: {values_found: one_or_more, values_matching: every}
  fields:
    type: {equals: dword}
    value: {equals: 1, datatype: integer}
```

The separate Test-wide `items_found` and `items_satisfying` have deliberately
not been conflated with field-level cardinality. The native JSON Schema has
no hidden defaults: the explicit `field_requirement` is inherited by both
fields and can be overridden on an individual field.

## Boundaries

Two transformations are implemented separately:

1. **Single source State only:** an AND of distinct non-record scalar fields
   can be expressed by one `fields` mapping. Source State IDs and complete
   prior trees stay in the undo sidecar. Conjunctions of *different* source
   States are never flattened on this basis.
2. **Test-wide cardinality:** a repeated explicit pair is promoted to
   `require.field_requirement`, with differing explicit pairs retained on
   individual fields. OR, ONE, XOR, AND grouping and all predicate values
   remain in place. Unknown predicates, absence-only or record cases veto
   the rewrite.

The converter's default still emits the provenance-pinned 0.4 source form.
The opt-in mode emits an explicit, source-hashed, exact-undo ledger in
`source-trace.json` under each affected Rule's
`human_authoring_compaction_review`. It labels these candidates
`CONVERTED_UNVERIFIED`; new compiled program hashes must not inherit
historical source-proof statuses by fiat.

### Running a focused review

```bash
python tools/v04_direct_converter.py <pinned-scap-zip> \
  --sha256 <exact-source-sha256> --rule <xccdf-rule-id> \
  --human-compact --compile --output <new-empty-output-path>
python tools/audit_v04_human_compaction.py \
  --authoring-root <existing-human-v2-authoring-root>
```

`--human-compact` is incompatible with `--verify`: the original source-proof
checker and a new presentation claim require separate acceptance steps.

## Focused evidence and full-library prevalence

- 2026-10-30: **32 focused tests passed** in
  `test_v04_direct_converter`, `test_v04_field_requirement_schema`, and
  `test_v04_human_authoring_compact` (later refined test scope may differ).
- The pinned original Windows source Test terms matched the independent
  expanded-native reader after opt-in compaction. Native schema validation
  and package compilation also passed. This is bounded term comparison,
  **not a scanner-run six-state parity claim**.
- Read-only census of the immutable 65-stream human-v2 authoring tree:
  **6,817 automated Assessment files**, **12,045 Tests**, **2,887 eligible
  Tests** in **51 STIGs**, with approximately **8,063 YAML lines removed**
  by Test-wide cardinality inheritance alone. Source-State AND folding is
  excluded from this census because the native archive does not establish
  source State boundaries.
- No published #261/#263 archive, GitHub download link, original native YAML,
  compiled program digest, or existing 4,258 accepted proof records was
  overwritten by this candidate work.

## Next review gate

Use original pinned OVAL with source-State provenance to regenerate a small
representative set (Windows, Linux, record/absence/OR cases), compare exact
requirements and compiled outcomes, and obtain the owner's explicit authoring
decision before producing a separate immutable public human-v3 archive.
