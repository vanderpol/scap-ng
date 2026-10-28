# Autonomous development checkpoint

Updated: 2026-10-28. Task: [converter #251](https://github.com/vanderpol/scap-ng/issues/251).
Current execution order: [owner comment 6477986104](https://github.com/vanderpol/scap-ng/issues/251#issuecomment-6477986104).
Schema dependencies remain under [#255](https://github.com/vanderpol/scap-ng/issues/255).
Follow [AGENTS.md](../../AGENTS.md), [MAINTAINING.md](../../MAINTAINING.md), and
[branch policy](../../BRANCH-MANAGEMENT.md). This is an engineering recovery
index, not a release or scanner-conformance declaration.

## Recovery on 2026-10-28 (current workspace)

- Recovered GitHub `main` at `4f1400471d54a2b1b2fa8e2fd6f7233a03118f8f`
  by fast-forward; old local `work` at `a65aba621` is preserved. No dirty files
  or local-only commits were discarded. The old recovery directory and stash
  object `aa515185a8120ba1b1079cebd4a91fa4be6f8152` are absent here. The older
  uncommitted enum/diagnostic batch described below is historical recovery
  context, **not present in this workspace**. Reconstruct only after inspecting
  current code and source-backed evidence; do not claim its tests were rerun.
- Fetched the immutable evidence tag and checked its existing ZIP: 12,276,247
  bytes, 4,301 files, all CRCs good, SHA-256 matches the published manifest.
  Extracted ledger SHA-256 also matches the analysis report. All 341 primary
  message counts and overlapping capability counts reconcile directly.
- Recovery files and fresh focused/six-source evidence are under
  `/workspace/recovery-20261028/`; large artifacts remain outside source Git.
- Reconstructed only the bounded shellcommand intrinsic `pattern match`
  converter route, consuming the already committed source-operation metadata.
  Independent readers, schemas, mappings, compiler and workflows are unchanged.
  Eight acquisition positive/negative tests and 44 focused/affected tests pass.
  The affected six-source gate passes: 1,072 proved primary Rules (+17), 324
  blocked automated, 171 manual; all 1,055 prior program hashes retained. See
  [recovery receipt](../audit/v04-shellcommand-regex-recovery-20261028.md).
  Exact-commit hosted integration remains pending; no fresh full maintained-suite
  claim yet.

## Published code and completed verification (previous checkpoint)

- Latest synchronized source `main`: `c65a134b539558609ccf3bdc0600f38e411bbb2e`.
  All owner schema changes are preserved. The local converter batch remains
  uncommitted and is excluded from the published-code draft toolchain.
- Last full maintained-suite verification: exact `c65a134b5`,
  [run 40733597054](https://github.com/vanderpol/scap-ng/actions/runs/40733597054),
  job `122976470206`: **3,264 run, 3,263 passed, zero failures/errors, one existing
  skip**, 838.180 seconds. All twelve triggered workflows passed. Do not dispatch
  a duplicate full suite for this commit.
- Last exact published six-benchmark verification: `4365ffa82`,
  [run 40715616321](https://github.com/vanderpol/scap-ng/actions/runs/40715616321),
  **1,055/1,396 original OVAL Rules proved**. A later local gate on the preserved
  pre-c65 worktree also completed at `identity-six/`; this is not an exact-c65 gate.
- The explicitly authorized metadata-only correction `f789583e6` passed all ten
  workflows and its 3,253-test maintained suite. It grants no wider schema authority.

## Existing six-source draft — do not regenerate

Pristine detached toolchain: `c65a134b539558609ccf3bdc0600f38e411bbb2e`.
Pinned NIWC revision: `8c8e5dff860af6b1290ee9273a282db24278f8d5`.
Six original ZIP hashes are in `tests/fixtures/v04-direct-six-sources.json`.

Workspace recovery root:
`/workspace/.onboarding/scap-converter-recovery-20261028/`.
Existing archive: `six-source-draft-c65.zip`, **12,276,247 bytes, 4,301 files**.
SHA-256: `07f7b24f4d0522630159fbddf9f6d643ffcac3d49d3c482dc7fb263de9793317`.
`manifest.json`, `ledger.json`, `ledger.csv`, source pins and reproduction
instructions are inside it; expanded output is `six-source-draft-c65/`.

All **1,567** original Rules are accounted for: **1,396 OVAL-bearing**, with
**1,055 eligible compiled/unproved candidates**, **341 blocked automated** and
**171 OCIL-only/manual** Rules. All **1,055** prior proof-floor program hashes
match. This is **DRAFT — NOT RUNTIME VERIFIED**, not fresh original-source proof.
The raw converter emitted 1,057 candidates; two banner Rules (RHEL SV-270174 and
Oracle SV-271689) have retained original Schematron failures and are explicitly
blocked. Diagnostic bundles contain raw candidates and are not accepted packages.

Fresh draft checks completed: six existing converter CLI runs, schema validation,
JSON/YAML agreement, native compilation, 1,057 compiled operand comparisons,
bundle integrity, file inventory and archive checksum. No fresh full source
validity/semantic gate was launched before draft publication.

## Publication recovery

Evidence repository metadata/complete CSV ledger published at `fc22c1a535109155dd0036bb8131f9fb8f368b6b`.
Run path: `runs/v04-converter/2026-10-28-six-source-draft-c65/`.
The release-asset upload returned HTTP 401; recovery confirmed no release/asset
remained published. Do not assume the first upload succeeded.

The unchanged ZIP is now **published and independently downloaded/checksummed**.
Evidence commit: `150d57f14050954161e4515d49a637991740fe01`.
Immutable tag: `v04-six-source-draft-20261028-c65a134b5`.
[Download DRAFT — NOT RUNTIME VERIFIED](https://github.com/vanderpol/scap-ng-evidence/raw/refs/tags/v04-six-source-draft-20261028-c65a134b5/runs/v04-converter/2026-10-28-six-source-draft-c65/six-source-draft-c65.zip).
[Immutable summary/ledger/manifest](https://github.com/vanderpol/scap-ng-evidence/tree/v04-six-source-draft-20261028-c65a134b5/runs/v04-converter/2026-10-28-six-source-draft-c65).
Publication recorded in [#251 comment 6480344261](https://github.com/vanderpol/scap-ng/issues/251#issuecomment-6480344261).

The preferred release-asset upload returned HTTP 401 and left no release/asset.
The first streaming Git push also failed; the buffered HTTP/1.1 retry succeeded
atomically for main and tag. This is a transport fix, not expanded credentials.
A bounded evidence-storage decision accompanies the unchanged ZIP in evidence
Git. No archive/conversion regeneration or duplicate full-suite run occurred.
The downloaded published bytes match the checksum above. Do not republish it.

## Current 341-blocker analysis

Disjoint primary causes from the published Rule ledger: 232 `all_exist`, 63
unresolved catalog bindings (41 DNS, 22 Apache), 17 acquisition-parameter
operation/type, 16 function cases (10 split, six count), 12 invalid original
closures, and one comparator-bearing absence. This totals 341. Per benchmark:
RHEL 126, Oracle Linux 122, Windows 11 18, Server 2025 12, DNS 41, Apache 22.
Secondary diagnostic occurrences overlap and must be deduplicated per Rule.

Source-backed findings under investigation: malformed DNS/Apache catalog entries
use the SCAP data-stream namespace for `uri`, rather than the XML catalog
namespace; do not silently repair source bindings. Oracle Rule SV-271653 reaches
`split` through `extend_definition` (Definition 271653 to Definition 230511),
which contradicts the earlier zero-function Oracle estimate. Preserve that exact
counterexample and use the actual complete Rule graph for priority decisions.
The 17 acquisition primary cases are shell-command `pattern` fields with an
explicit `operation="pattern match"`; the committed mapping already permits
that intrinsic regex operation, but the shared parameter visitor currently
hardcodes equality. Investigate this bounded implementation gap without
admitting other invocation-input operations or modifying mappings/schemas.

## Preserved uncommitted converter batch

The enum-reference/diagnostic batch is preserved in the main checkout, in
`pre-c65-owner-sync-wip.tar.gz`, and retained stash
`aa515185a8120ba1b1079cebd4a91fa4be6f8152`. The changelog conflict was resolved by
retaining both owner and converter entries; all other original file hashes match.
Do not overwrite this work or repeat its completed tests without a reason.

Before the owner schema sync, 49 distinct focused/affected regressions passed:
13 new-selector/diagnostic, 30 existing enum/acquisition/user-rights/hash/contract,
five correct process/typed-operand, and one all-100-contract parity test. An
incorrect process module name caused one invocation error, resolved by running
the correct module. All eight original process58 Tests and 39 Server 2025 rights
Rules passed. Fresh post-c65 focused verification remains to be done before
publishing this implementation batch; it has no full-suite result yet.

Pinned corpus probe: 523/713 configured Tests compiled and typed-term compared,
521/803 source-valid/nondeprecated; all previous 521 authoring/program/term hashes
retained, zero mismatches. Capabilities remain 49/51 approved scope, 49/100 global.
Separate public cohorts remain YAML 45/51 and RPM verifyfile 1/1.
Files: enum helper/converter/diagnostics and tests, dependency register,
`tests/fixtures/v04-direct-enum-selectors/`, developer/audit docs and changelog.
Detailed logs/results are indexed by recovery `status.json`; its older entries
are historical snapshots, not the latest status.

## Next actions and owner boundaries

1. Publication is complete. Preserve its immutable tag, bytes and checksum; do
   not regenerate conversions or publish duplicate archives.
2. Analyze the actual 341 blocked automated Rules by benchmark, capability and
   construct. Separate disjoint primary counts from overlapping secondary counts,
   converter gaps from #255 contract/source limitations, and rank unlock impact.
3. Continue source-backed production-impact implementation and the preserved
   passing batch. The six-source function census reaches only one remaining
   unsupported function name (Server SV-278143, substring); do not prioritize all
   nine Self-Assertion functions over production blockers.
4. After draft publication, use exact-SHA six-benchmark/source/proof-hash gates
   for a separately labeled verified checkpoint. Reuse existing exact-SHA full
   CI, never cancel/duplicate it. The 65-source corpus is not a routine regression.
5. Update this checkpoint at publication/analysis/integration milestones and
   before interruption. On restart inspect checkout, WIP, latest GitHub main,
   publication refs/assets and existing CI first; avoid duplicate commits/uploads.

No schema, grammar, compiler/scanner/editor semantics or production `all_exist`
changes are authorized. Isolate normative dependencies under #255, preserve all
source/proof identities, and continue unrelated work. Stop only for a genuine
owner decision, protected/destructive/scope change or safely unresolvable blocker.
