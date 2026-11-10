# Main handoff integration — owner approval required

Both main branches are unchanged. These draft candidates preserve every included original commit with normal merge ancestry. They are rehearsal branches, not permission to merge.

**Recommended integration order after explicit approval:** [canonical #55](https://github.com/vanderpol/scap-ng/pull/55), then [RI #50](https://github.com/vanderpol/scap-ng-ri/pull/50), using merge commits; do not squash or rebase. This carries the tested conflict resolutions together with the original histories. Recheck exact heads, current main, and all candidate checks immediately before merging. If any moves, repeat qualification for the new candidate.

If merging the original PRs individually, use the construction order below, retargeting each successor only after its predecessor reaches main. Apply the two recorded reconciliation changes before declaring the integrated tree ready. Do not use an intermediate main as the handoff baseline.

Canonical: **#23 → #30 → #37 → #39 → #41 → #44 → #45 → #47 → #48 → #49 → #51 → #52 → #54**, followed by the prototype-preservation reconciliation in #55.

RI: **#32 → #33 → #34 → #38 → #39 → #40 → #41 → #42 → #44 → #45 → #48 → #49 → #37**, retaining both workflow settings at the final inventory merge. #37 is a parallel child of #34, not an ancestor of #49.

## Exact inventory

All 30 original open PRs were audited: 13 RI and 17 canonical. All 13 RI and 13 canonical heads are included. RI #43/#46/#47 and canonical #53 are issues, not missing PRs. The machine ledger records exact heads, reported and live bases, CI run links, draft state, schema paths and dispositions. GitHub mergeability against an individual base does not prove combined integration. PR #32 has no individual workflow run; the combined candidate exercises its design checks.

| PR | Exact original head | Reported base | Candidate disposition |
| --- | --- | --- | --- |
| [#9](https://github.com/vanderpol/scap-ng/pull/9) | `d4e477998cda438a1e53a7c3c84123ec92e5ba1f` | `main` | Held; preserve branch |
| [#11](https://github.com/vanderpol/scap-ng/pull/11) | `246a8d37cc54875386768a7d76b60a6f9c01d013` | `codex/issue8-native-discovery` | Held; preserve branch |
| [#13](https://github.com/vanderpol/scap-ng/pull/13) | `da4c48dfc60dc96a46e7b85425f70fb8f301a0b1` | `codex/issue14-native-functions` | Held; preserve branch |
| [#23](https://github.com/vanderpol/scap-ng/pull/23) | `0fe3ce1fbb6f29b3f9cb8c42431434972291a7bf` | `main` | Included |
| [#27](https://github.com/vanderpol/scap-ng/pull/27) | `919732d4c570b521edf82196a7694dfd8c27fe50` | `main` | Held; preserve branch |
| [#30](https://github.com/vanderpol/scap-ng/pull/30) | `0bf00877a4d6642661ac4d1f671dbf49ffbe5196` | `main` | Included |
| [#37](https://github.com/vanderpol/scap-ng/pull/37) | `5e6c49d0a34b3b5380d753fa0142037e494275bd` | `main` | Included |
| [#39](https://github.com/vanderpol/scap-ng/pull/39) | `f61fff037f18832aa04db140b3e3209dfddf7219` | `main` | Included |
| [#41](https://github.com/vanderpol/scap-ng/pull/41) | `532fbbfe52a220d2672256ac54d1e117d69cd043` | `docs/issue38-schema-description-pilot` | Included |
| [#44](https://github.com/vanderpol/scap-ng/pull/44) | `b1bdefa6bc07f5e78db7951be92cef9e8414d1df` | `docs/issue40-core-documentation-inventory` | Included |
| [#45](https://github.com/vanderpol/scap-ng/pull/45) | `976a5fa67e8195ca5fc2eb2779eab0da502b1afe` | `docs/issue43-review-pack` | Included |
| [#47](https://github.com/vanderpol/scap-ng/pull/47) | `7e27c23e53fdfdf018fa483a24b857462992b109` | `docs/production-documentation-104` | Included |
| [#48](https://github.com/vanderpol/scap-ng/pull/48) | `6012ae25281352a9c2d8a4fde7cb5a4968b4432c` | `docs/documentation-fidelity` | Included |
| [#49](https://github.com/vanderpol/scap-ng/pull/49) | `d5fdff3b869ab97769dadf5406eb2c6306291fe2` | `main` | Included |
| [#51](https://github.com/vanderpol/scap-ng/pull/51) | `0e8af65fa8c8fb5ef7b63c8299c7a3babd1d3f85` | `docs/issue42-five-capability-examples` | Included |
| [#52](https://github.com/vanderpol/scap-ng/pull/52) | `a2f681bcf33cdbf7d8a6ff624a4a2791c2005032` | `docs/model-a-conformance` | Included |
| [#54](https://github.com/vanderpol/scap-ng/pull/54) | `e42300bfe800c5a28864cbc53440a059babe5a69` | `docs/sqlite-integration-qualification` | Included |

## Conflicts and excluded changes

- RI #37 conflicts only in `.github/workflows/gate-b.yml`. Both the newer evaluator/Tools evidence environment and original inventory audit environment remain active. All eight inventory tests are retained: combined RI Python count is 36, zero skips. The recorded historical private-document audit is hash-checked and reused, not claimed rerun.
- Canonical #37 is textually mergeable but places a hand-written prototype in the newer generator-owned tree. The prototype is retained byte-for-byte under `docs/pilots/pr37-table-first/unix-file.md`; strict generated-directory ownership is unchanged. PR #30 research is preserved and explicitly labeled historical, avoiding a second documentation authority. Its STOP/GO failure is not promoted to a qualified contract.
- Canonical #9/#11/#13 are old amendment branches: replay has real merge conflicts with current contracts and the heads differ from the current frozen family. Preserve their commits/proofs; do not blindly replay them. Their Input/functions/binary32 work overlaps later integrated canonical work. This audit does not authorize closing them or claiming every historical proof newly executed.
- Canonical #27 is textually mergeable but changes frozen `schema/assessment.schema.json` and `schema/variable-expression.schema.json` (including relational Inputs and function declarations). It is excluded explicitly. Recover any still-required feature in separately approved next-version work; do not change the RI schema pin to admit it.
- All original PRs remain drafts awaiting owner approval. The four held historical/schema amendments do not block the qualified supplied-evidence candidate; they need separate disposition. No administrative settings were inspected for this audit. Prior HTTP 403 administrative-read limits are not configuration defects or reasons to block normal testing. Tools #40 remains open for final deployment verification.

## Verification and limits

Local: **311 Go race pass records across four test-bearing packages; 36 RI Python tests; 161 canonical Python tests; no skips; vet; module verification; five 10-second fuzz targets; Windows cross-compilation; schema-pack and design checks; every existing generated-output gate.** The 71 protected implementation/dependency files and all 145 frozen schema JSON bytes remain unchanged. No tests were weakened. See `validation.json` and `COMMANDS.sh`; raw receipts are in RI #50 under this directory.

**23 actual native conformance executions** (15 Model A and eight supplied-evidence examples), **eight original OVAL equality Tests** independently compared, **five separately labeled negative mutations false**, **ten original Tests held**, **zero Definition outcomes**, and **eight historical CLI exit/stdout/stderr responses byte-identical**. Expected results are not evaluator inputs.

Memory and SQLite produced identical full true/false decisions at **100,000 and 1,000,000 synthetic Items**. The finite million-v1 qualification profile does not raise production defaults. Measurements were taken with other checks active; they are qualification observations, not tuning or scanner-performance claims. FULL/256/1MiB defaults remain unchanged.

Exact source pins: schema `6012ae25281352a9c2d8a4fde7cb5a4968b4432c`, family `63a61b3eb0ca95790721699f5e63b6f5a16b146660b9545a437519b508351db5`; OVAL `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`; Self-Assertion `e3538595c5083b9c34d937a81d319234df9bbfaa`; immutable Tools Assessments `d326e9d025c81f0292eadfb3dbf86e768960219d`; canonical conformance producer `ff3e95c7b1f9cb99b4d1129bf85525f491c7ffff`. Publication checker remains pinned to `053eeeb3b33e3ee5f683604fd66ae8c833450cd0`; local combined audit found zero recognized unprotected publication sinks.

CI status must be read from the exact draft head, not inferred from these local results or ancestor green runs. The final PR/Issue #43 receipt records completed versus pending checks. Required-check administration was not audited.

## Work Codex handoff

Until owner-approved integration, **main is not the implemented RI baseline**. For review/testing, fetch `review/handoff-integration` in each repository and detach at the exact published PR head; keep `RI_NATIVE_SOURCE` at immutable schema commit 6012ae2, not the documentation branch. Use the existing pinned workflows for source setup and the commands here. Do not run collectors, install SCC, change production pins, or treat SQLite staging as host observation consistency.

Preserved holds: empty/error/incomplete Variable propagation, unsupported functions/operators/datatypes and Definition roll-up; acquisition/status/view/traversal choices; persistent/effective authority; sensitive evidence protection and full native Result export. Approved-but-unimplemented collection/filter/binding features remain implementation gaps, not newly invented language restrictions. Scheduler/registry/explanation interfaces in #49 are design declarations; 30 planned cases are not runtime execution. No scanner equivalence or release readiness is claimed.

**Stop here for Jack’s integration approval.** Existing collectors/storage/reporting handoff priorities remain in RI Issue #43 and #49; this audit does not authorize the next implementation gate.
