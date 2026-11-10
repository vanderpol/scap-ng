# Issue #40 — Phase 1 review package

Start with the **[bounded editorial review batch](EDITORIAL-REVIEW.md)** and its [machine worksheet](editorial-batch.json): 27 author-facing candidates plus one withheld foreach case, prepared under the [owner editorial instruction](https://github.com/vanderpol/scap-ng/pull/41#issuecomment-6721264010). Each case separates original wording, the Codex draft, edited `author_description`, and `engineering_note`; semantic decisions remain pending. No candidate is added to the bulk patch bundle or installed.

For the earlier Phase 1 discovery, use the generated [inventory summary](REPORT.md), [wording review table](CROSSWALK.md) and [Require/concat previews](PILOTS.md). The complete [node inventory](inventory.jsonl), [gap register](gaps.jsonl), [wording crosswalk](crosswalk.jsonl) and [annotation patch proposal](proposed-annotations.patch.json) are machine-readable research records, not an additional documentation authority.

**Authorization:** [Phase 1 only](https://github.com/vanderpol/scap-ng/issues/40#issuecomment-6715925830), including the preceding owner requirements for actionable gaps and exact proposed language. Nothing in this package approves a language contract or applies a schema edit.

## Reproduce

Use the existing `requirements-dev.txt`, then run from the repository root:

```sh
python tools/audit_schema_documentation.py
python tools/audit_schema_documentation.py --check
python tools/audit_schema_documentation.py --diff-baseline
python -m unittest discover -s tests -v
```

One generic command regenerates the inventory, findings, crosswalk, patch bundle, summary, review tables and two previews. The same command also validates the bounded editorial worksheet and regenerates its small review sheet. The read-only `--check` rejects stale output and new/changed baseline findings. `--diff-baseline` lists new/changed/disappearing IDs without writing anything. `--write-baseline` is an explicit research-baseline operation, not part of normal generation; review the change before using it. No command writes canonical schema files.

## Pins, scope and branch relationship

- Native schema/source pin: `7354a24cdbfe18321153ccaef5d772801a10cd71`. [schema-manifest.json](schema-manifest.json) enumerates all 145 JSON inputs and discovers the 35 JSON Schema documents by their actual `$schema`/`$id`, rather than a guessed filename list.
- This purpose-specific branch, `docs/issue40-core-documentation-inventory`, is **stacked on draft PR #39** at `f61fff037f18832aa04db140b3e3209dfddf7219`. It extracts the existing inspection code into `tools/schema_documentation.py`; the unix.file renderer and this generic audit use the same implementation. PR #39's remote branch and generated content are unchanged.
- Forty-three generated capability-specific definitions are exact-pointer scope exclusions. Non-schema metadata is enumerated and pinned but is not counted as JSON Schema annotation coverage. No 104-capability expansion occurs.
- The inactive canonical-function-call migration schema is inventoried separately. Reachability from the actual Assessment entry distinguishes active forms from unconnected helper definitions. Structural reachability is not evidence of runtime implementation.
- Intended disposition: **held for owner review**. Review PR #39's renderer architecture first, then this Phase 1 inventory/design. Do not merge either PR or silently retarget/repin an editor.

## Audit method and limits

Every discovered schema-valued node is inventoried, including anonymous alternatives, array/map entries, guards, conditional overrides and inactive-candidate nodes. Public prose ownership is assigned to roots, named definitions and property declarations. Anonymous structural constraints retain their exact facts and containing owner; they are not each treated as a separate missing prose field. A conditionally introduced field is public when no unconditional declaration already owns that instance location. Schema guards are distinguished from language properties literally named `if` or `then`.

Description presence records own, `$ref` and same-instance applicator sources separately. A containing object's description is **not** borrowed as its child field's meaning. Shared missing definitions create one finding with explicit consumers. Repeated inline validation copies are not falsely reported as existing `$ref` aliases.

Quality is a separate review dimension. Heuristics identify definite absence, malformed text, obvious filler and default/conditional explanations requiring review. They are not an exhaustive semantic quality certification: populated but unreviewed descriptions remain `present_not_semantically_reviewed`. Curated notes identify specific native-contract gaps. A provisional statement is not useful coverage and cannot resolve a semantic gap merely by becoming a populated string.

Findings are keyed by canonical URI/pointer + role + category. The baseline permits preexisting findings; disappearing IDs are reported without automatically marking them resolved. `review-notes.json` contains source-guarded wording proposals and may hold proposal-ID dispositions with approval links and explicit resolution pointers. Accepted canonical wording is checked for drift when a resolution pointer exists; missing approval or a falsely closed gap is rejected. The original bulk crosswalk has **no accepted/resolved annotations**; the bounded editorial receipts below track their separate wording approvals.

## How to review the crosswalk

There are three approval groups: `editorial_only`, `clarification_no_validation_change`, and `normative_contract_decision_required`. The summary also splits decision kinds so shared-binding design questions are not confused with hundreds of distinct runtime decisions.

- The small source-reviewed table gives concrete wording for references, core evaluation/Require structures, concat, regex capture, unique, merge sorting, typed payloads and foreach activation.
- Remaining entries propose only facts actually encoded in schema. Where meaning cannot be established from the audited contract, wording is clearly provisional and requests native-basis review; it is not offered as publication-ready prose or a claim that no other project source could resolve it.
- `proposed_description_ref` identifies one proposed wording owner for repeated Input/Variable/typed-comparison roles. It is **not an instruction to reference the whole existing validator**: different inline identifier/operand constraints could otherwise tighten acceptance. Those consumer bindings have no duplicate annotation patch; a shape-preserving annotation-only shared-binding mechanism needs review in the future pack.
- Editor deployment association is an integration follow-up, not a made-up schema-description fix. The audit proves offline pointer/help resolution only. No editor repository or live hover session is changed or exercised.

The bundle has exact old text, new annotation destinations and file-hash preconditions. Only description/title/example operations are permitted. All candidates are applied **in memory** to verify that validation assertion trees are identical; the two previews use only their selected core/concat candidates. This is not bulk canonical annotation implementation.

Historical concat evidence is the already pinned 5.12.3 annotation reference recorded in the crosswalk. It is labelled as historical evidence rather than automatic native authority. Missing native casting, status/return, ordering and activation decisions remain owner questions; no legacy behavior is silently inherited.

**Stop for Jack's review of the inventory, wording and generator design.** No Phase 2, schema-byte edits, semantic adoption, editor repin, merge, release or runtime-equivalence claim.

## Bounded editorial iterations

[Batch 1 receipt](EDITORIAL-REVIEW.md) records 21 accepted descriptions, six semantic
holds and one withheld case, with the exact independent-review and owner-authorization
links. Editorial acceptance does not authorize canonical installation or clear semantic
holds. The three approved refinements are recorded in the review worksheet; selected wording
is exercised only by the bounded proposal below.
The review's optional merge phrasing preference remains uninstalled: the continuation
explicitly authorizes wording revisions only for 04, 07 and 13.

[Batch 2](EDITORIAL-REVIEW-2.md) records 25 editorial acceptances (22 unchanged and three
revised), with three semantic holds retained. Its [machine worksheet](editorial-batch-2.json)
records a single proposed description owner per concept and related consumer pointers
where duplicated structures need a future shared binding. It does not create a second
canonical authority or copy descriptions into those consumers.

Both review sheets regenerate with `python tools/audit_schema_documentation.py` and
are checked by the existing `--check` gate after changes. The gate verifies source
hashes, pointers, old/inherited text, witness validity, approval provenance and distinct
batch targets. The Phase 1 baseline and bulk patch bundle remain unchanged.

**Stop for editorial review.** Frozen schemas, the editor, runtime contracts and the earlier bulk patch bundle
remain unchanged. The owner-authorized [eight-description integration prototype](../../pilots/approved-annotations/RECEIPT.md)
materializes only those approved annotations in isolated next-version schema fixtures.
Its reference and offline help read the actual proposal schema nodes; no live editor
verification or canonical placement is claimed.
