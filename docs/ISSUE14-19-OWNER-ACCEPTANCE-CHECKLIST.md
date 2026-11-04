# Issues #14/#19 owner acceptance checklist

This checklist prepares draft PRs #15–#21 for coordinated acceptance. It does
not merge any PR and does not select a filesystem naming candidate.

## Dependency chain and merge order

Recommended order after owner review:

1. **PR #15** — native selector baseline from `main`.
2. **PR #17** — filesystem/Windows selector batch, based on #15.
3. **PR #18** — next selector batch, based on #17.
4. **PR #20** — Issue #19 retained-function documentation, based on #18.
5. **PR #21** — cross-repository compatibility audit and this acceptance evidence, based on #20.
6. **PR #16** is semantically independent documentation, but is **not mergeable as-is** beside #15: it conflicts in frozen generated documentation, `tests/test_schema_integrity.py`, and `tools/generate_docs.py`. Rebase it onto the accepted #15→#18 chain, regenerate all artifacts, and then place it before #20 or merge its resolved content during that chain.

The chained pairs #15→#17→#18→#20→#21 are ancestry-clean. The only
identified textual conflict is #16 against the selector chain; it is caused by
both branches updating frozen counts/digests and generated outputs, not by a
semantic disagreement in the authoring prose.

## Acceptance status

| PR | Recommendation | Required owner action |
|---|---|---|
| #15 | Acceptable pending selector-baseline approval | Confirm the reviewed operator/value/nullability restrictions and retain the 0.4.0 baseline. |
| #16 | Rebase/regenerate before merge | Resolve frozen-artifact conflicts; accept documentation-only changes separately from grammar decisions. |
| #17 | Acceptable after #15 and naming decision | Choose whether its public filesystem names remain provisional A; do not merge a silent alias. |
| #18 | Acceptable after #17 | Confirm its nine-selector batch and generated count reconciliation. |
| #20 | Documentation-safe, grammar unchanged | Decide whether the documented `unique` arity gap is acceptable for now. |
| #21 | Review report/tests safe after #20 | Record owner decisions for filesystem naming, tools repin, and runtime qualification. |

No PR in this stack should be merged while it is marked draft or while its
base branch omits the prior schema/integrity changes.

## Filesystem naming decision

The current public overlay uses Candidate A (`filepath` / `path` / `filename`).
The converter mapping at `scap-ng-tools@1f4f74d` emits
`full_path` / `directory` / `name`. Candidate B is
`full_path` / `directory` / `filename`; it therefore still requires a
coordinated converter/mapping change for the final component. Neither option
is implemented here.

Representative assessments and expected outcomes are in
`docs/evidence/issue21/filesystem-selector-alternatives/`:

* `alternative-a.assessment.yaml` validates against the current public schema.
* `alternative-b.assessment.yaml` is a proposed Candidate-B shape and is
  intentionally rejected by the current schema.
* `tools-emission.assessment.yaml` records the exact current converter shape
  and is intentionally rejected by the current public overlay.

Recommendation: **do not add permissive aliases**. Select one vocabulary,
update the canonical mappings and converter snapshot in one reviewed change,
then migrate/regenerate converted content and provenance together.

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

After the filesystem choice, update the tools in a separate reviewed change:

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

The current tools baseline is intentionally blocked against this checkout:
it expects 143 JSON files, 34 roots, 242 root references, and digest
`ab1933f2d9171ee0af70c0fab855b00f5faf78bf59ad4924fbf24b402ac4072a`; the
current SCAP-NG candidate is 145 JSON files, 35 roots, 652 root references,
and digest `2adf88f5c1fd950e997579c00064388b5f12e9e29cde38075bf75b76d1f25843`.

Provenance records the same current candidate and historical boundary in `docs/PROVENANCE.md` under “Current coordinated selector/function draft”.

## VS Code editor pin

The exact current PR #21 candidate commit required by the editor's offline
schema pack is:

```
7b9b61108aa30a601828268576308e510477094e
```

The authoritative values for the current candidate are:

* schema digest: `2adf88f5c1fd950e997579c00064388b5f12e9e29cde38075bf75b76d1f25843`
* JSON/root/reference counts: `145 / 35 / 652`
* editor candidate pack manifest SHA-256: `2aa28f9926d4d7774edcf48b991f1f48b121e34a7dce9006b1db129a6301727e`
* stable rollback commit: `463675f3b931e596c922352a131cb3c515ab2265`

Final editor metadata must use the full values above. If #16 is accepted or A/B changes are made, this commit and
manifest must be replaced with the new combined schema commit; the editor must
never pin a moving branch or an unmerged draft.
