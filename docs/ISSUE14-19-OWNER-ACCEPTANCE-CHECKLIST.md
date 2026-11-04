# Issues #14/#19 owner acceptance checklist

This checklist prepares draft PRs #15–#21 for coordinated acceptance. It does
not merge any PR. The owner-approved Candidate A naming decision is recorded below.

## Dependency chain and merge order

Recommended order after owner review:

1. **PR #15** — native selector baseline from `main`.
2. **PR #16 (rebased)** — author-facing documentation, regenerated on top of #15.
3. **PR #17 (rebased)** — filesystem/Windows selector batch, on top of #16.
4. **PR #18** — next selector batch, based on #17.
5. **PR #20** — Issue #19 retained-function documentation, based on #18.
6. **PR #21** — cross-repository compatibility audit and acceptance evidence, based on #20.
7. **PR #22** — owner-approved Candidate-A mapping/snapshot coordination, based on #21; tools-side PR is `vanderpol/scap-ng-tools#22`.

PR #16 is semantically independent documentation, but is **not mergeable as-is**:
it conflicts with #15 in frozen generated documentation,
`tests/test_schema_integrity.py`, and `tools/generate_docs.py`. Rebase #16
onto #15, regenerate all artifacts, then rebase #17 onto that combined result.
The conflict is caused by both branches updating frozen counts/digests and
generated outputs, not by a semantic disagreement in the authoring prose.

## Acceptance status

| PR | Recommendation | Required owner action |
|---|---|---|
| #15 | Acceptable pending selector-baseline approval | Confirm the reviewed operator/value/nullability restrictions and retain the 0.4.0 baseline. |
| #16 | Rebase/regenerate before merge | Resolve frozen-artifact conflicts; accept documentation-only changes separately from grammar decisions. |
| #17 | Acceptable after #16 and approved mapping update | Candidate A is now canonical; retain the names without aliases. |
| #18 | Acceptable after #17 | Confirm its nine-selector batch and generated count reconciliation. |
| #20 | Documentation-safe, grammar unchanged | Decide whether the documented `unique` arity gap is acceptable for now. |
| #21 | Review report/tests safe after #20 | Filesystem naming is resolved to A; tools repin and runtime qualification remain tracked. |
| #22 | Draft coordination follow-up | Mapping-side schema candidate and tools-side snapshot repin are separate reviewable changes; consume the exact pins below without merging automatically. |

No PR in this stack should be merged while it is marked draft or while its
base branch omits the prior schema/integrity changes.

## Filesystem naming decision

The owner-approved Candidate A (`filepath` / `path` / `filename`) is now
canonical in the three affected SCAP-NG mappings. The pre-change converter
snapshot emitted `full_path` / `directory` / `name`; the separate tools PR
updates its snapshot/mappings so the converter emits Candidate A. Candidate B
is not implemented and no aliases are introduced.

Representative assessments and expected outcomes are in
`docs/evidence/issue21/filesystem-selector-alternatives/`:

* `alternative-a.assessment.yaml` validates against the current public schema.
* `alternative-b.assessment.yaml` is a proposed Candidate-B shape and is
  intentionally rejected by the current schema.
* `tools-emission.assessment.yaml` records the exact current converter shape
  and is intentionally rejected by the current public overlay.

Recommendation: **retain Candidate A and do not add permissive aliases**. The
canonical mapping update and converter snapshot repin remain separate reviewed
changes; migrate/regenerate converted content and provenance together.

## `unique` arity proposal

Pinned OVAL 5.12.3 `UniqueFunctionType` has a component sequence with
`maxOccurs="unbounded"` and therefore accepts one or more components
(`oval-definitions-schema.xsd:933–941`). The simplest additive native shape is:

```yaml
unique:
  - {variable: first-values-variable}
  - {values: {object: {object_ref: second-object}, field: name}}
```

The evaluator would concatenate component populations in source order, apply
OVAL's scalar/string treatment, and retain the first occurrence of each value
while propagating the inherited status/error outcome. Existing one-expression
`unique: expression` content could remain valid through a compatibility
`oneOf` during migration; multi-component conversion would use the array form.

This is a **proposal only**. It requires owner approval for array shape,
string casting, ordering, record exclusion, and status propagation before any
schema or converter change.

## Required scap-ng-tools compatibility changes

With the filesystem choice resolved, update the tools in a separate reviewed change:

1. Repin `FrozenSchemaSnapshot` constants to the accepted flat schema's exact
   JSON count, root count, reference count, and aggregate SHA-256.
2. Regenerate and integrity-pin
   `src/scap_ng_tools/converter/_v04_semantic/contracts-0.4.0.json` from the
   accepted schema/mappings; update `SCHEMA_HASH` and `PACK_HASH` in
   `_v04_semantic/__init__.py`.
3. Update the selector mapping crosswalk/output names and converter fixtures;
   do not change converter semantics merely to satisfy a schema alias.
4. Run tools' full unit suite with the accepted snapshot plus SCAP-NG's full
   suite. Keep source crosswalk metadata separate from native field names.

The historical tools baseline was intentionally blocked against the pre-mapping
checkout: it expected 143 JSON files, 34 roots, 242 root references, and digest
`ab1933f2d9171ee0af70c0fab855b00f5faf78bf59ad4924fbf24b402ac4072a`. The
separate tools candidate is now repinned and verified against 145 JSON files,
35 roots, 658 root references, and digest
`0a8c5a5840b5a17839db87decf034544286baf56383f52de71795862cca20593`; its
semantic pack digest is `5e3aa7a017cbce86cb724679fd1a3ce15e1ff63def48f09b61a3f83f3484fb92` from tools commit `3e69cd822fcd961f4d9492c9f9ea48f18693742f`.

Provenance records the same current candidate and historical boundary in `docs/PROVENANCE.md` under “Current coordinated selector/function draft”.

## VS Code editor pin

The pre-mapping PR #21 candidate was:

```
7b9b61108aa30a601828268576308e510477094e
```

The pre-mapping candidate values were:

* schema digest: `2adf88f5c1fd950e997579c00064388b5f12e9e29cde38075bf75b76d1f25843`
* JSON/root/reference counts: `145 / 35 / 652`
* editor candidate pack manifest SHA-256: `2aa28f9926d4d7774edcf48b991f1f48b121e34a7dce9006b1db129a6301727e`
* stable rollback commit: `463675f3b931e596c922352a131cb3c515ab2265`

The verified coordinated candidate now has source commit
`5a13698933c88ca1e271d635b9bee39af75bc027`, schema digest
`0a8c5a5840b5a17839db87decf034544286baf56383f52de71795862cca20593`, and
`145 / 35 / 658` JSON/root/reference counts. The editor-pack manifest is
`305dbd0b77729c69f3bc5d40232b0b3fbc5a32646310678f61ff2ae304831a5f` over 236
resources. The editor owner must consume these exact values; no VS Code files
are changed here.
