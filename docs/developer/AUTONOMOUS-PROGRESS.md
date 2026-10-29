# Autonomous development checkpoint

Updated: 2026-10-29. Task: [converter #251](https://github.com/vanderpol/scap-ng/issues/251).
Execution order: [owner comment 6477986104](https://github.com/vanderpol/scap-ng/issues/251#issuecomment-6477986104).
Schema/normative dependencies: [#255](https://github.com/vanderpol/scap-ng/issues/255).
Read [AGENTS.md](../../AGENTS.md), [MAINTAINING.md](../../MAINTAINING.md), and
[branch policy](../../BRANCH-MANAGEMENT.md) before resuming. This is a restart
record, not a release/scanner-conformance declaration.

## Current integration — real coverage and release blockers

Latest owner direction: recover real STIG coverage, preserve the baseline, and
identify exactly what prevents the 0.4 release. Source `main` was independently
verified at `7070e7990` before this increment; no newer work was overwritten.

This integration activates only the existing `solaris.smf` mapping through the
generic converter and independent scalar identity contract. **37 affected tests
pass**, including seven new original-backed regressions. Actual production-code
acceptance proves **14** original Solaris 11 Rules (seven SPARC, seven x86);
their original Rule/dependency identities match the frozen DRAFT. All **3,130**
preceding cohort proof/source/native-term/authoring hashes and all **523**
conformance four-hash records retain parity. Three additional original SMF
conformance Tests prove: **526/716 configured**, separately counted from Rules.

Own exact-commit hosted maintained/six-source integration is pending publication.
Do not supersede that active gate or claim the older suite verifies new code.
Published baseline stays **4,206** primary static proofs until this integration
and durable evidence pass; the candidate total is **4,220**. Schemas, mappings,
compiler, scanner/editor, protected workflows and #255 contracts are unchanged.

[SMF source-backed review packet](../audit/v04-solaris-smf-activation-20261029.md).
[Exact release-blocker reconciliation](../audit/v04-release-readiness-20261029.md):
all 8,892 original Rules reconcile, with 3,033 automated unproved at the published
baseline. Primary buckets are 1,630 blocked-contract, 992 catalog binding,
150 effectively deprecated Test type, 137 nonstandard sqlext, 96 converter/reader
investigation and 28 known original-invalid/deprecated cases. Secondary blockers
overlap; these are not guaranteed unlock counts. The 14 SMF cases are among 96.
The report separates full migration from clean toolchain-release gates and a
deliberately scoped subset prerelease. It does not authorize release or schema work.

Recovery: `/workspace/coverage-next-20261029/` contains `smf-final/`, complete
conformance output/retention, the 3,130-proof retention log, frozen-ledger overlay,
and selected original Rule hashes. Next: let exact-code integration finish,
publish durable SMF evidence and update these counts, then investigate the next
source-valid existing-mapping cases. Forty-three IOS XE line/global candidates
are selected but not yet source-validated; do not count them. Reuse exact-commit
CI and do not regenerate the frozen all-65 archive. Commits/pushes are consolidated
at least 30 minutes apart without routine owner approval questions.

## Completed assignment — compiled-cohort proof expansion

**3,130 independently proved / 3,138 assessed / zero pending**, across all 32
benchmarks in the frozen candidate cohort. Seven invalid originals and one
deprecated original remain explicitly rejected; every valid, nondeprecated
candidate is proved. The prior 1,076 primary proofs and all 523 conformance
four-hash records remain retained. Total primary static proofs: **4,206**.
[Cumulative index, exact evidence and eight exclusions](../audit/v04-compiled-proof-expansion-20261029.md).

Final [35-Rule evidence](https://github.com/vanderpol/scap-ng-evidence/tree/42979846586581a431dfc4dc6727709a303d53e6/runs/v04-converter/2026-10-29-compiled-proof-batch-005-5e847f826) binds the exact published reader implementation
to original source pins, unchanged frozen authoring/program hashes and all
retention records. The retries supersede 35 first-pass reader limits; they do
not enlarge the original denominator. No all-65 regeneration was performed.
The complete 0.4.0 release and scanner runtime remain separate claims.

Routine scoped commits/pushes are authorized without further approval, in
consolidated windows **at least 30 minutes apart**. Assignment completion does
not authorize #255 contracts, source repair, schema/mapping/compiler changes,
scanner/editor work or 0.5. Existing larger draft blockers remain unresolved.
Recommendation for the eight exclusions: preserve rejection until corrected
upstream inputs are pinned and validated. No new owner decision is needed for
that disposition.

Recovery root `/workspace/proof-expansion-20261029/`: `batch-008/` is the final
exact-commit replay; `published-runs.json` records five immutable evidence runs;
`reader-integration-ci.json` binds hosted gates; prior retention and complete
conformance evidence remain alongside them. Inputs remain under
`/workspace/recovery-20261029/inputs/`. Earlier local batch-005/006/007 results
are superseded by batch-008; do not promote them or rerun this completed cohort.

## Last fully verified implementation

All eight path-selected workflows at `5e847f8268697f7555a442256c06f5bfa48f4676` passed. [Maintained run 40904268977](https://github.com/vanderpol/scap-ng/actions/runs/40904268977), job 123554611774, artifact 12910359527: **3,292 run / 3,291 passed / zero failures and errors / one existing skip**, 619.389 seconds. [Six-source gate 40904268774](https://github.com/vanderpol/scap-ng/actions/runs/40904268774), job 123554610454, artifact 12910957628: all **1,072** original anchor proofs retained. The Bluetooth workflow was not path-selected by these reader-only edits; its unchanged original-source acceptance CLI also passes locally, and its regression tests are included in the maintained suite.

The corrected independent Registry readers pass 61 focused tests, all 35 final
target originals, retention of 3,095 preceding new proof hashes and 523
conformance records. Four preceding guard additions remain proved with unchanged published
program hashes. [Reader packet](../audit/v04-registry-reader-proof-expansion-20261029.md).
Do not repeat the maintained suite for this exact implementation.

### Preceding Solaris verification


`10f4e35b331c622c14f6e3aa2bd4aa8981c810c1` admits explicit default equality on
nil UNIX filenames for two original Solaris 11 SPARC/x86 Rules. All nine
exact-commit workflows passed. [Maintained run 40867417638](https://github.com/vanderpol/scap-ng/actions/runs/40867417638),
job 123425584553: **3,284 run, 3,283 passed, zero failures/errors, one existing
skip**, 1143.910 seconds; artifact 12895541852.
[Six-source run 40867417851](https://github.com/vanderpol/scap-ng/actions/runs/40867417851),
job 123425584157, artifact 12894249637, retains all 1,072 primary proofs.
All 523 conformance four-hash records and both preceding NTUSER program hashes
also retain parity. These increments add four independently source-proved original
Rules outside the six anchors; they do not regenerate or relabel the frozen
all-65 DRAFT. [Receipt](../audit/v04-nil-filename-defaults-20261029.json) includes
actual generated Object/require excerpts. This is static verification only.
Do not repeat the maintained suite for this exact implementation.

### Preceding NTUSER verification

`f141efb07603e72a3982ffda87489da8f0d5c74f` reconstructs NTUSER empty-State
comparison operands for two original Windows 10/Server 2016 Rules. All nine
exact-commit workflows passed. [Maintained run 40863822537](https://github.com/vanderpol/scap-ng/actions/runs/40863822537),
job 123413419074: **3,279 run, 3,278 passed, zero failures/errors, one existing
skip**, 1,139.313 seconds; artifact 12893188443. [Six-source run 40863826463](https://github.com/vanderpol/scap-ng/actions/runs/40863826463),
job 123413430092, artifact 12892323743: all 1,072 primary proofs retained.
All 523 preceding conformance four-hash records also retain parity. See its
[receipt](../audit/v04-ntuser-empty-state-recovery-20261029.json). No scanner claim.

### Preceding closed-enum verification

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

## Completed guard increments and recovery state

The NTUSER and nil UNIX filename increments are published and fully hosted-green.
The working implementation is `10f4e35b3`; subsequent verification receipt and
checkpoint changes are documentation only. No implementation CI is pending or
paused. No local-only implementation remains. The two receipts contain original
source ZIP/blob pins, dependency identities, negative/mutant evidence, exact
program hashes and actual generated Object/require excerpts for all four additions.
The old all-65 DRAFT is unchanged. Schemas, mappings, specification, compiler,
scanner/editor, protected workflows and production all_exist remain unchanged.

Recovery root: `/workspace/recovery-20261029/`. It retains thirteen SHA-256/Git-blob
verified original ZIPs under `inputs/`, source validation audits, `selected/`,
`solaris-narrow-selected/`, `ntuser-retained-under-nil/`, both six-source gates,
full conformance reports and focused/maintained logs. The discarded compiler-test
negative XML inputs were moved out of source Git into
`maintained-generated-negative-fixtures/`; no generated artifacts remain dirty
in the source checkout. Earlier isolated copies are diagnostic recovery only,
not source authority. No scanner results or verified toolchain release are claimed.

Owner approved both converter publications. Verification documentation is part of
those approved increments; do not ask again for the same work. Future GitHub
approval requests must be consolidated to at most one batch every 30 minutes.
Further converter admission for the documented acquisition cases needs the
existing #255 source operation/datatype clarification; do not silently choose it.

## Remaining boundaries after this increment

The bounded guard audit covers ten additional original primary closures: all eight
nil cmdlet datatype cases are original Schematron INVALID (required record type
is omitted), not candidates for silent repair. The two acquisition-primary
cases are VALID/nondeprecated and stay blocked: .NET SV-225226's case-insensitive
command operation, and Windows 10 SV-220812's version-typed module acquisition.
The [nil filename packet](../audit/v04-nil-filename-defaults-20261029.md) gives the
smallest examples/recommendation; adjacent JSON records all ten source pins and
actual original errors. No schema, operation or datatype projection is chosen.
Two Solaris Variable-source default-attribute cases still reach unsupported split.
Other all_exist/population, import/export, aggregation/functions and float cases
remain under their existing #255/#218 decisions. Continue only independently
justified converter work; do not infer acceptance or repair invalid originals.

## Preceding NTUSER recovery record — 2026-10-29

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
is still pending at this integration. This local record preceded the subsequently successful hosted verification
recorded above.

Recovery root is `/workspace/recovery-20261029/`: original ten SHA-256/Git-blob-verified
ZIPs under `inputs/`, `selected/` for the two new Rules, `six-after/`, focused,
conformance and maintained logs, and reproduction scripts. Published all-65
archive remains unchanged. Latest owner message is interpreted literally as
requiring permission before a GitHub commit. The owner approved committing and
pushing this concrete NTUSER increment after the running checks pass. Publication proceeds through the connected GitHub API after that passing gate;
the receipt records exact tested code/fixture hashes. No workflow is dispatched
or superseded manually.
The subsequent isolated work was `nil-increment/`: two original-valid Solaris directory
Rules prove after accepting explicit default equality on a nil UNIX filename.
Five focused tests passed there. Those probes subsequently resumed and passed;
the nil filename correction is now this integration. Two other Solaris
default-attribute cases still hit split.


## Historical closed-enum recovery record (superseded above)

The preceding enum integration reconstructed the lost identity-domain
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

The previous session used `/workspace/recovery-20261028/`; that directory did not
survive this restart. The active recovery root is `/workspace/recovery-20261029/`
as recorded above. The previous root contained downloaded
published archives, source pins/inputs, full DRAFT generation/finalizer scripts,
large conformance reports, both six-source gates and focused logs. The isolated
`enum-candidate/` has the pre-integration experiment; current source Git is the
implementation authority. Large evidence remains outside the source repository.

The old `/workspace/.onboarding/scap-converter-recovery-20261028/` and stash
`aa515185a8120ba1b1079cebd4a91fa4be6f8152` did not survive in this workspace.
Old local `work` at `a65aba621` is preserved, with no local-only commits lost.
Earlier restart history remains in the
[preceding checkpoint](https://github.com/vanderpol/scap-ng/blob/24889577233c6a75e739676adffe8f676a0f9f3b/docs/developer/AUTONOMOUS-PROGRESS.md).

## Earlier backlog priorities (current boundaries recorded above)

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
