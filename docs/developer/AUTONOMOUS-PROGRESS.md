# Autonomous development checkpoint

Updated: 2026-10-29. Task: [converter #251](https://github.com/vanderpol/scap-ng/issues/251).
Execution order: [owner comment 6477986104](https://github.com/vanderpol/scap-ng/issues/251#issuecomment-6477986104).
Schema/normative dependencies: [#255](https://github.com/vanderpol/scap-ng/issues/255).
Read [AGENTS.md](../../AGENTS.md), [MAINTAINING.md](../../MAINTAINING.md), and
[branch policy](../../BRANCH-MANAGEMENT.md) before resuming. This is a restart
record, not a release/scanner-conformance declaration.

## Last fully verified implementation

`66a166bf282a377c233bc4a1ffd1ac43d0bd734c` adds the recovered closed identity
enum selector route. All nine exact-commit workflows passed. Its maintained
suite [40793748077](https://github.com/vanderpol/scap-ng/actions/runs/40793748077),
job `123185027830`, ran **3,273 tests: 3,272 passed, zero failures/errors, one
existing skip**, in 1,132.409 seconds. Artifact `12863807377` retains exact test
identities. Do not repeat that suite for this commit.

The exact-commit [six-source gate 40793748148](https://github.com/vanderpol/scap-ng/actions/runs/40793748148),
job `123185027661`, passed with the same 1,072 primary proofs and unchanged
programs. Artifact `12862983307` retains the evidence. The separately published
[static enum conformance checkpoint](https://github.com/vanderpol/scap-ng-evidence/tree/v04-identity-enum-static-verified-20261029-66a166bf2/runs/v04-converter/2026-10-29-identity-enum-static-verified-66a166bf2)
contains all 523 proof hashes and actual generated authoring/program/typed-term
excerpts for the two original additions; evidence commit `cdc0ed5`.

The preceding `24889577233c6a75e739676adffe8f676a0f9f3b` implements the mapped
shellcommand intrinsic regex correction. Its completed evidence is retained:

- [Maintained suite 40788102371](https://github.com/vanderpol/scap-ng/actions/runs/40788102371),
  job `123166258986`: **3,268 run, 3,267 passed, zero failures/errors, one existing
  skip**, 1,167.519 seconds. Artifact `12861341772` retains exact test identities.
  Do not repeat this suite for that commit.
- [Six-source validity/proof/hash gate 40788102434](https://github.com/vanderpol/scap-ng/actions/runs/40788102434),
  job `123166258359`: **1,072 primary OVAL Rules proved**, +17 (RHEL +12,
  Oracle +5); all 1,055 preceding program hashes retained. Still 324 blocked
  automated and 171 manual/OCIL-only, 1,567 total / 1,396 OVAL-bearing Rules.
  Artifact `12860901212` retains the full gate.
- [Implementation/recovery receipt](../audit/v04-shellcommand-regex-recovery-20261028.md)
  records the 44 focused/affected tests, exact source pins and new programs.
  Schema validity, independent static terms, compilation, live scanner execution
  and complete policy conversion remain different claims.

## Published evidence — do not regenerate or duplicate

Evidence repository commit: `d8e5337` (immutable tags below).
All source ZIP pins refer to NIWC
`8c8e5dff860af6b1290ee9273a282db24278f8d5`.

1. Original [six-source DRAFT](https://github.com/vanderpol/scap-ng-evidence/tree/v04-six-source-draft-20261028-c65a134b5/runs/v04-converter/2026-10-28-six-source-draft-c65):
   pristine toolchain `c65a134b539558609ccf3bdc0600f38e411bbb2e`, 4,301 files,
   12,276,247 bytes, SHA-256
   `07f7b24f4d0522630159fbddf9f6d643ffcac3d49d3c482dc7fb263de9793317`.
   Evidence commit `150d57f14050954161e4515d49a637991740fe01`. Accounts for
   1,055 eligible compiled/unproved, 341 blocked automated, 171 manual Rules.
   Recovered archive CRCs/checksum and ledger digest/counts match. No duplicate
   publication or conversion regeneration was performed.
2. [Verified static six-source primary OVAL](https://github.com/vanderpol/scap-ng-evidence/tree/v04-six-primary-static-verified-20261028-248895772/runs/v04-converter/2026-10-28-six-primary-static-verified-248895772):
   toolchain `248895772`, 1,072 independent primary proofs; 4,327 files,
   8,654,136 bytes, SHA-256
   `809e6da4c4139bf8a671ed0d81ae464feb41f82c28ebadbdfb4edc05a253f4bd`.
   Accepted bundles exclude invalid original closures. This is static evidence,
   **not runtime verified**, complete migration or a verified toolchain release.
3. [All-65 DRAFT — NOT RUNTIME VERIFIED](https://github.com/vanderpol/scap-ng-evidence/tree/v04-niwc-65-draft-20261028-248895772/runs/v04-converter/2026-10-28-niwc-65-draft-248895772):
   same toolchain, 65 individual Git-blob/SHA-256-verified ZIPs, 8,892 Rules.
   Disjoint statuses: 1,072 retained six-source proofs; 3,138 compiled candidates
   without original-source validity/proof checks; 3,029 blocked automated
   (137 across four sqlext package exceptions, 12 known invalid originals);
   1,653 manual/OCIL-only. 17,298 files, 47,484,177 bytes, SHA-256
   `5f86d016c1bce82018eec82c6468ab583816ff0b38c8d3ea5e9210a931cc1a08`.
   Other 59 sources are **not** original-source validated/proved. Diagnostic
   candidate bundles are not accepted production packages. Raw output was
   analyzed before its explicit bounded review-storage exception. Release-asset
   upload again returned HTTP 401, left no release, and authenticated Git
   publication succeeded. Both new published downloads independently matched
   their byte counts/checksums. No protected workflow was modified.

Publication/results are recorded in [#251 comment 6484065504](https://github.com/vanderpol/scap-ng/issues/251#issuecomment-6484065504).
The all-65 run was the owner-designated deliverable checkpoint, never a routine
regression. Do not rerun it for ordinary converter changes.

## Resumption integration — 2026-10-29

GitHub `main` independently resolves to `7acdf6d6f0995be1f310a69491fa81f6d7916767`;
local checkout was clean at that SHA. The previous recovery directory did not
survive. This integration publishes the reconstructed NTUSER work;
[review and retention packet](../audit/v04-ntuser-empty-state-recovery-20261029.md).
Both original Windows 10 SV-220955 and Server 2016 SV-225069 pass selected
original-validity/schema/independent-term/compilation/package gates. 38 focused
checks pass; all 1,072 six-source program hashes and all 523 conformance
four-hash records retain parity. Local maintained gate: **3,279 run, 3,278
passed, zero failures/errors, one existing skip**, 1507.413 seconds. Exact
implementation commit and hosted gates are recorded in #251; hosted verification
is still pending at this integration. The preceding fully hosted-verified
implementation remains `66a166bf2`.

Recovery root is `/workspace/recovery-20261029/`: original ten SHA-256/Git-blob-verified
ZIPs under `inputs/`, `selected/` for the two new Rules, `six-after/`, focused,
conformance and maintained logs, and reproduction scripts. Published all-65
archive remains unchanged. Latest owner message is interpreted literally as
requiring permission before a GitHub commit. The owner approved committing and
pushing this concrete NTUSER increment after the running checks pass. Publication proceeds through the connected GitHub API after that passing gate;
the receipt records exact tested code/fixture hashes. No workflow is dispatched
or superseded manually.
Next isolated work is `nil-increment/`: two original-valid Solaris directory
Rules prove after accepting explicit default equality on a nil UNIX filename.
Five focused tests pass. Six-source/conformance probes are paused locally to
prioritize the active NTUSER maintained suite; resume their processes after
publication. This candidate is outside source Git and is not part of the
NTUSER integration. Two other Solaris default-attribute cases still hit split.


## Current bounded integration and recovery files

The integration containing this checkpoint reconstructs the lost identity-domain
closed enum selector behavior only; it does not claim recovery of the original
uncommitted diagnostic patch. It adds existing literal/reference/unique graph
validation without changing names, graphs or quantifiers. See the
[review/retention packet](../audit/v04-identity-enum-selector-recovery-20261029.md).

- **40 focused/affected tests pass**; all 100 generated contracts retain parity.
- Full pinned conformance probe: **523 compiled and independently compared out
  of 713 configured / 803 original Tests**. All **521** preceding authoring,
  source-term, native-term and program hashes retained; exactly original AppCmd
  Test 101 and AppCmdListConfig Test 301 are added. Their original closures
  validate and are nondeprecated. These are conformance Tests, not primary
  production Rules. No scanner execution claim.
- Affected six-source gate preserves **all 1,072 current primary program hashes**
  and identical outcomes, as well as the checked-in 1,055-program floor.
- Exact-commit hosted maintained and six-source gates both passed, as recorded
  above. No duplicate full suite was dispatched.
- Subsequent NTUSER empty-State work is isolated under `ntuser-candidate/` in
  the recovery root, not published implementation. Two original Windows 10 /
  Server 2016 Rules pass a focused validity/schema/independent-term/compilation/
  package probe. The mapping already explicitly preserves this State lexical
  value; finish positive/negative and retention checks before integration.
  This is not a new collected Item type or a status-predicate rewrite.

Current recovery root: `/workspace/recovery-20261028/`. It contains downloaded
published archives, source pins/inputs, full DRAFT generation/finalizer scripts,
large conformance reports, both six-source gates and focused logs. The isolated
`enum-candidate/` has the pre-integration experiment; current source Git is the
implementation authority. Large evidence remains outside the source repository.

The old `/workspace/.onboarding/scap-converter-recovery-20261028/` and stash
`aa515185a8120ba1b1079cebd4a91fa4be6f8152` did not survive in this workspace.
Old local `work` at `a65aba621` is preserved, with no local-only commits lost.
Earlier restart history remains in the
[preceding checkpoint](https://github.com/vanderpol/scap-ng/blob/24889577233c6a75e739676adffe8f676a0f9f3b/docs/developer/AUTONOMOUS-PROGRESS.md).

## Next priorities and decision boundaries

- The [original 341-blocker report](../audit/v04-six-draft-blockers-20261028.md)
  remains the immutable-cohort analysis: 232 all_exist, 63 catalog bindings,
  17 acquisition guards (now fixed), 16 split/count, 12 invalid originals and
  one comparator-bearing absence. Primary counts sum to 341; secondary counts
  overlap. Representative original Rules and per-primary capabilities were
  reconciled from the actual published ledger, not historical estimates.
- The all-65 ledger adds production impact: primary all_exist 1,184, unresolved
  catalog bindings 992, import/export bindings 382, aggregation components 30,
  unsupported functions 32 (15 split, 14 count, three substring). These are
  upper bounds on potential unlocks, not valid-source/proof claims. See
  [#255 coordination 6484255338](https://github.com/vanderpol/scap-ng/issues/255#issuecomment-6484255338).
- After integration CI, investigate remaining bounded converter guards using
  exact original closures and focused tests. Do not silently repair catalog
  namespaces, invalid/deprecated source or capability mismatches. Preserve all
  source/proof identities and hashes. Schema/function/population/external-input
  contracts remain coordinated through #255; unsupported cases stay fail-closed.
- No schema/mapping, normative assessment semantics, compiler/scanner/editor,
  production all_exist, new platform activation or protected workflow changes
  are authorized by this recovery. Isolate decisions and continue independent
  approved work. Stop only for genuine owner decisions or unresolvable blockers.
