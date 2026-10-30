# Autonomous development checkpoint

## Active #251/#255 — bounded independent source validation (2026-10-30)

Owner instruction: continue pinned-original 0.4 independent validation, leaving
#264/#265/#266 contracts and all immutable libraries/hashes unchanged.
Recovered live published main `b450d150f25d92a9391b1fbb192e4c9f064f04dc`, clean,
with its four triggered workflows passing; fast-forwarded local main.
Read all three pending issue bodies and latest compaction/sample notes. Current
schema remains authoritative; no purpose-context or authoring migration here.

Completed eleven fixed original Rule closure validations against six exact
NIWC-distributed ZIPs: 4 typed-term PROVED, 4 all_exist unsupported, 1 invalid
and 2 deprecated. Three separate proof records lie outside frozen 4,258 floor
(Apache SV-214228/SV-214251, IOS-XE SV-215838); RHEL SV-257851 is a retained
control. All eight native authoring/program hashes unchanged, schema/independent
program operand checks PASS. No corpus status change, export or rebaseline.
Count reader now retains exact source/canonical-native aggregation components,
projection, duplicates and integer cast; no function/flag execution is added.
Fixtures and manifest: `tests/fixtures/v04-independent-validation/` (eleven
node-exact slices with full-component validation observations, ~183 KB).
Tool: `tools/audit_v04_bounded_source_validation.py`; --originals rejoined all
source nodes and replayed XSD/Schematron against pinned original components.
Full reports/logs: `/workspace/validation-v04-20261030/`.
[Source findings and precise review hold](../audit/v04-independent-validation-20261030.md).

DISA: one deprecated .NET WMI Object (SV-225230), no invalid assertion in this
sample. NIWC: two input-type Schematron failures in SV-215833, one deprecated
WMI Object in SV-278143. Attribution follows original OVAL node IDs, not XCCDF
or distributor. Numeric text capture to integer 5 remains valid; whole timeout
configuration text is a different intermediate type.

Genuine semantic/review hold: existing reference helper reports UNKNOWN for
SV-278021's all_exist +check=all with incomplete collection and one false Item;
pinned OVAL Results TestType exception 3a literally requires FALSE. This work
records both interpretations and the source hash, without changing that helper,
its old tests, native result semantics or approved contracts. Resolve ordered
existence versus incomplete exceptions under #255 before all_exist promotion.
Independent count proofs do not rely on this conflicting vector.

Focused integration: 59 selected /56 passed /3 source-checkout-location skips,
10.357s, zero failures/errors; separate operator fixture bound explicitly to
vendored pinned OVAL schemas: 4/4 PASS, zero skips. Twelve new tests include
count mutants, namespace/hash/accounting guards, logic/cardinality/error/unknown
boundaries and the explicit reference-model discrepancy. Implementation ready
for issue-linked commit and automatic maintained CI; reuse exact-SHA runs,
do not duplicate/cancel them. Publish a compact separate proof-evidence run
and #251/#255 handoff after observing the gate. No broader corpus work needed.

## Completed #261 — native library layout / editor-callable maintenance

Published implementation HEAD: `ff69d46b36e05e45074a5e7f43bf2ef3cf464ddf`.
Intermediate maintained integration `9e893266f42ea699a9a8798b37d8bbe9715e2e9c`
PASS: run [41049843626](https://github.com/vanderpol/scap-ng/actions/runs/41049843626),
3,359 selected /3,358 passed /one explicit optional full-corpus skip; no failures
or errors. Final exact-implementation run [41052208017](https://github.com/vanderpol/scap-ng/actions/runs/41052208017)
PASS: 3,359 selected /3,358 passed /one explicit optional full-corpus skip,
zero failures/errors; 1,159.586 test seconds. All three triggered workflows
(maintained, current design, issue reference) passed. The two subsequent fixes preserve
native output: original record ZIP member resolution uses original ZIP identity
rather than temporary input-folder labels; check JSON includes a readable summary.
44 focused/compatibility tests PASS (8.878s); clean-extracted source snapshot:
28 tests PASS (8.523s), fresh offline hash-pinned install, pip check, CLI export /
zero-change analyze / original records / status search / cache deletion+rebuild /
compile and independent package consumer PASS. Exact full-ref source snapshot
replay is byte-identical: SHA256
`adbb52973ce608ce918e840658ead7b3265c601b43dc71a466da4e8257fe421d`.

Completed review archive: 44,544,308 bytes, 13,890 payload files, CRC and every
expanded digest PASS; SHA256
`a01ea589501bf8a53e5df68e50ca9478f19543d2bd3844546667fde743c28d8c`.
Immutable [review download and evidence packet](https://github.com/vanderpol/scap-ng-evidence/tree/v04-normalized-library-review-20261030-ff69d46b3/runs/v04-library/2026-10-30-all65-normalized-review-ff69d46b3),
evidence commit `75e82a9`, tag `v04-normalized-library-review-20261030-ff69d46b3`.
Both published ZIPs were freshly downloaded at immutable evidence commit
`2fc4c4b`: SHA256 and ZIP CRC PASS. Do not regenerate the corpus. It includes the
source snapshot, separate reuse census, resource/acceptance/hash receipts,
source-only stream exceptions, CLI contract and bounded archive storage decision.
Delivery is complete: code, exact test identities/results, normalized-review ZIP,
exact source snapshot and CLI/editor contract. GitHub #261 carries the owner
handoff; VS Code #3 receives the backend integration contract. No additional
feature work, full-corpus export or proof replay is needed for #261. Future
sharing/repointing, independent unverified-candidate proof, genuine conversion
blockers, runtime scanner evidence, license selection and final release remain
separate workstreams; this task makes no decision on them.


Delivery acceptance completed after engine checkpoint
`03ddc6beda8dcda5ff57439b0c3d7a2d12763d1b`: exact pinned source archive admitted,
all 65 streams /8,892 original Rules retained, 6,817 compiled Assessment
program hashes and 4,258 accepted proof triples unchanged. All **13,754 native
YAML files remain byte-identical**; only paths change. Native kinds: 60 Benchmarks,
60 applicability catalogs, 6,817 Rules, 6,817 Assessments. Five original-only
streams stay in records with exact original publisher titles, no placeholders.
Counts: 4,258 verified /2,559 unverified /422 blocked /1,653 manual. Max/median
paths 215/187 ->138/122 chars. One intentional export: 705.84s, 279,924 KiB peak.
No source conversion or OVAL proof replay. Completed output:
`/workspace/library-v04-261/normalized-all65/`; never regenerate it routinely.

Actual cached scope search 0.059s and one-document check 0.574s (one parse,
173,004 KiB peak). Synthetic 100-stream /10,100-document index: search0.012s,
incremental0.433s, one parse, 82,256 KiB peak. Separate advisory census: 404 exact
ID-neutral structural groups, 100 near pairs examined, zero promotions/unused
Assessment docs. RHEL9/Server2025 compile + independent package consumer PASS:
415+257 unchanged programs; 20+18 shared Objects. See task work-root JSON logs.

Final hardening since first checkpoint: cached status search, lazy original
record queries, persistent edit/error recovery, disposable index restoration
from durable sidecars, Rule/Assessment proof demotion on edits, Benchmark file
rename ownership, cancellation/rollback, Input/Parameter/policy reference checks,
native kind dispatch independent of `catalog.yaml` filename. 44 focused +old
normalizer tests PASS (8.915s), repository layout check PASS. Final implementation is published; capture its automatically triggered
maintained CI once while packaging the completed review candidate. Do not
rerun all-65 conversion/export. The completed acceptance came from engine
03ddc6bed; subsequent changes add editor/provenance/transaction hardening and
generated title/status metadata without changing a single native YAML byte.
Actual normalized RHEL9 and Server2025 compilation/independent-consumer PASS,
415+257 programs unchanged. Wrapper source namespace adaptation was required
for the existing independent reader's authoring-archive interface; reader and
compiler were not changed. Separate reuse census at task root, no promotions.

First checkpoint maintained run `41039515793` and representative Board conversion
`41039515618` PASS. Older #214 0.3 preview `41039515609` failed in its unchanged
renderer/schema stage before invoking the normalizer (1,567 source rejects).
Its renderer/schema/driver bytes match recovered baseline; no protected workflow
or schema was altered to hide it. Capture this known unrelated failure in final
handoff, and reuse current maintained CI rather than rerunning old previews.

Authority: [owner task #261](https://github.com/vanderpol/scap-ng/issues/261).
Recovered clean published main `f6990f426`; documentary CI green. Frozen #260
candidate/DRAFT remain immutable. New in-scope implementation is
`tools/scap_ng_library/` with entry points `scap_ng_library_cli.py` and
`scap_ng_repo_normalizer.py v04`. The old normalizer invocation is unchanged.
See [implementation/preflight and CLI contract](NATIVE-LIBRARY.md).

Focused original-derived Linux/Windows/shared-Object/Input-warning export
passes: 14 native documents, four unchanged Assessment program hashes, three
retained proof pairs, three original manual ledger records, no fake Assessments.
31 focused/new +historical-normalizer tests PASS after final diagnostic/rollback
guards (8.463s). Repository layout check PASS. This is the first tested engine
checkpoint; full all-65 layout acceptance/publication remain pending.
Objective map includes #261 under O2/O4/O7/O8. No automatic dedup, normative
schema/compiler/scanner changes, source split or editor implementation.

Next: commit/push tested engine checkpoint; use automatic maintained CI once.
Run the single intentional all-65 layout acceptance using the **already built**
DRAFT, not source conversion/proof replay. Require pinned archive SHA, preserve
8,892 source rows /6,817 native /4,258 proof pairs; measure time/memory and
generate separate bounded reuse census. Publish a unique normalized-review
candidate with short before/after examples and immutable provenance; update
#261 and handoff. Existing corpus path `/workspace/rc-v040-20261029/all-65-draft/`,
published ZIP `/workspace/rc-v040-20261029/remote-verified-all-65-revised-draft.zip`.
Task work root `/workspace/library-v04-261/` contains focused export/test logs.
Never regenerate or modify the frozen DRAFT. Profiles stay embedded; all native
IDs/payloads unchanged, title-derived private navigation namespaces shorten paths.

## Release-candidate preparation complete — 2026-10-30

Candidate: **`a5db02e1b29a2d7c312ddcf593be1ee055afb750`**. Later main
documentation receipts do not change this exact committed toolchain candidate.
[Owner decision packet](https://github.com/vanderpol/scap-ng-evidence/tree/v04-toolchain-rc-20261030-a5db02e1b/runs/v04-toolchain/2026-10-30-v040-rc-a5db02e1b)
contains downloads/checksums, dependency/license inventory, commands, CI and
seven-case clean-extract evidence. Technical GO for pre-alpha evaluation;
final source/specification licensing and publication/tag approval remain owner
decisions. Owner replied "unsure" about licensing; no license was assigned.

Exact candidate maintained CI: run `41029222399`, job `123974642484`, artifact
`12966345704`: **3,331 tests / 3,330 passed / 0 failures/errors / 1 optional
census skip / 629.728 test seconds**. All four triggered workflows green.
The preceding implementation SHA `a08c9beb9` passed all 15 workflows, including
six-source hash retention. Final changes are release-walkthrough fixes/prose;
converter/compiler/schema bytes are unchanged. No unchanged expensive lane was
manually duplicated. Fresh source extraction without .git, fresh offline
11-dependency installation, pip check and all seven original/warning/negative
CLI cases PASS. Exact-ref archive builds are byte-identical (6,783 files).

[Published complete DRAFT](https://github.com/vanderpol/scap-ng-evidence/tree/v04-revised-all65-draft-files-20261030-a08c9beb9/runs/v04-converter/2026-10-30-all-65-revised-draft-download):
4,258 retained static proofs +2,559 UNVERIFIED native +422 automated blockers
+1,653 manual/OCIL =8,892 Rules across 65 original Benchmarks. All 6,817 native
candidates compile; all accepted proof/hash pairs and older frozen archives
unchanged. Fresh remote reconstruction and CRC/accounting/hash checks PASS.
ZIP SHA256 `a09ee9a13cdfeeb1b8599eab61308e935a19b99eb62eadafd32002d13d90f8bd`.
Recovered original primary cohorts: catalog 980/992; all_exist 1,181/1,184;
imports/exports 338/381; aggregation 30/30. Warning counts overlap; see receipt.

The preferred release-asset upload failed HTTP401 at uploads.github.com; it did
not yield a downloadable release asset. Bounded documented Git fallback:
evidence `9c37f56a5ab637d13b077d086ccd94fad635a0b6`, three <50MiB archive parts,
immutable DRAFT evidence tag and standard-library reconstruction/hash checker.
Candidate ZIPs are likewise retained with an explicit storage exception. No
final source `v0.4.0` tag/release. No scanner/editor/normative schema changes.

Samples: `vanderpol/scap-ng-editor-sample-data` commit
`b595b490226934a26cd7265b86974904d5db1cce`, five native sample cases, all 54 file
hashes and 22 JSON/YAML pairs checked. Historical views preserved.

Recovery: `/workspace/rc-v040-20261029/` retains completed corpus, source pins,
baseline/exclusions, candidate builds, offline wheels, fresh gate logs and
publication scripts. Do not regenerate the completed corpus. Reuse exact-SHA
CI/artifacts and immutable downloads. Independent proof of the 2,559 additions,
remaining unsupported/source cases and scanner-runtime/publisher-trust gates
remain separate follow-on work under #251/#255. #260 is ready for owner review.

## Active release-candidate task — #260 owner tasking

Authority: [owner comment 6510844015](https://github.com/vanderpol/scap-ng/issues/260#issuecomment-6510844015),
which supersedes earlier narrow checkpoint restrictions where they conflict.
Prepare the complete usable pre-alpha candidate; final release/tag still needs
owner approval. Recovered published main `4d78f700a4a555b474b38c230d7199e6e1a6bf21`.
Draft-only catalog/Test-all_exist/bounded export/function/aggregation support is
implemented without changing normative schemas/compiler/scanner or strict proof.
26 focused tests and 61 affected integration tests PASS (844.786s); the added
int32 function boundary check passes all 7 function/binding tests. The intentional
65-STIG build finalized: 4,258 verified +2,559 unverified native, 422 automated
blocked, 1,653 manual; all 6,817 native candidates compile and all 4,258 accepted
hash pairs are retained. See docs/audit/v04-draft-recovery-20261030.json.
Exact-SHA hosted CI, clean-extract acceptance and publication remain pending.

First implementation candidate `a08c9beb9dcf781a726adbdf05676f5ae2e57309`
completed all 15 hosted workflows green. Maintained run `40985824360`, artifact
`12947931615`: 3,331 selected, 3,330 passed, zero failures/errors, one recorded
optional full-source-census skip. Six-source run `40985824393` passed. No old
proof changed. A fresh offline 11-dependency environment installed successfully
and passed pip check. Exact-ref toolchain replay is byte-identical.

The new release walkthrough initially supplied directories to the independent
reader's ZIP arguments and treated a deliberately unproved negative as a
package-reader failure. Both invocation/assertion defects are fixed; the
corrected seven-case gate PASS includes original Linux, original Windows/shared
Object, three warning cases, incompatible source and synthetic ambiguous
catalog rejection. These changes affect release tooling/docs, not corpus
conversion. Commit them as the final candidate, then repeat exact-SHA clean
extraction and use the automatically triggered CI; do not duplicate full suites.

Evidence commit `829f543835e5dd1f005e15dc121aef7a5bfcbe69` is published. The
completed DRAFT ZIP is `/workspace/rc-v040-20261029/publication/all-65-revised-draft.zip`,
108,003,966 bytes, SHA256
`a09ee9a13cdfeeb1b8599eab61308e935a19b99eb62eadafd32002d13d90f8bd`.
Its 37,283 payload files passed CRC and every recorded digest. Prerelease
`v04-revised-all65-draft-20261030-a08c9beb9` was created, but uploads.github.com
rejected asset upload with HTTP401 while Git push succeeds. Do not imply the
release asset exists. Use an explicit bounded ordinary-Git storage fallback
with archive parts/checksums and update manifest/README/issue links accordingly.
Source/specification license remains undecided (owner replied "unsure"); never
invent a license or publish final 0.4.0. Finish all available candidate work.

Recovery root: `/workspace/rc-v040-20261029/`. Contains exact 4,258-proof baseline
(4,206 old +52 subsequently proved), 48 recorded original-invalid/deprecated
exclusions, hash-pinned dependency wheelhouse and test/build logs. Corpus output
`all-65-draft/` preserves completed per-source work. Check processes and logs
before resuming; never regenerate a completed corpus. Original pins/ZIPs remain
in `/workspace/recovery-20261029-resume/`. Earlier immutable archives and proof
receipts remain untouched. The pinned Linux/Python3.12 dependency download passed.

Next: commit the passing code/docs and completed branch audit as a candidate
on main, capture exact-SHA CI, build deterministic source archive, clean-extract
offline install and original Linux/Windows/shared/warning/negative CLI gates.
Publish revised DRAFT and candidate/decision packet in evidence; add bounded
0.4 samples to sample-data; update #251/#255/#260. No final release/tag.
Source tree has no project-wide license grant: record the gap for owner decision,
preserve original notices and dependency licenses, never invent a license.

Updated: 2026-10-29. Task: [converter #251](https://github.com/vanderpol/scap-ng/issues/251).
Execution order: [owner comment 6477986104](https://github.com/vanderpol/scap-ng/issues/251#issuecomment-6477986104).
Schema/normative dependencies: [#255](https://github.com/vanderpol/scap-ng/issues/255).
Read [AGENTS.md](../../AGENTS.md), [MAINTAINING.md](../../MAINTAINING.md), and
[branch policy](../../BRANCH-MANAGEMENT.md) before resuming. This is a restart
record, not a release/scanner-conformance declaration.

## Owner report — observed source oddities and numeric-capture clarification

The owner requested one actionable report of all observed oddity classes.
[Source oddities report](../audit/v04-source-oddities-owner-report-20261029.md)
contains 23 finding classes and suggestions for producer, standards and converter
ownership. The companion PDF/HTML, CSV (3,024 distinct Rules, covering all 2,981
residual automated blockers), detailed JSON and reconstruction driver are in the
[report evidence](https://github.com/vanderpol/scap-ng-evidence/tree/v04-source-oddities-report-20261029/runs/v04-converter/2026-10-29-source-oddities-owner-report).
The report joins existing pinned records; no corpus regeneration or source repair.

Owner clarification: a regex capture yielding `5` can be interpreted as integer
and used numerically. The original SV-215833 HTTP-timeout Variable
`...:var:21583310`, regex `ip http timeout-policy idle (\d+)`, does exactly that
and is explicitly excluded from the text-datatype concern. The concern is the
separate intermediate chain 21583304/21583307/21583305, which splits, captures
`timeout 5 0`, and merges text while declaring int. The later State pattern's
inner numeric group does not change the earlier captured Variable value. Exact
source excerpts and the report now distinguish these branches. No original or
validator was changed, and no runtime failure/equivalence is inferred.

User-delivery artifacts: `/workspace/reports/scap-ng-source-oddities-20261029/`
and `/workspace/reports/scap-ng-source-oddities-20261029.zip`. Recovery generators
are `/workspace/recovery-20261029-resume/build_owner_report.py` and
`render_owner_report.py`. Source implementation remains the previously fully
hosted-green `b70802028075850cf5f4397c50249813f86a7b14`; these changes are reporting
only. Keep #251/#255 population/producer-extension/casting decisions distinct.

## Recovery checkpoint — DRAFT published; IOS XE reader integration

Recovered 2026-10-29 from GitHub/source HEAD
`0b2fdb2d392c5d80a4128d73ae4ac5ada573cf26`; both checkouts were clean.
The previous workspace-only DRAFT/recovery directories were absent. Recovered all
65 ZIP/Git-blob pins, 4,206 published proof hash pairs and 32 source exclusions;
one necessary reconstruction with the existing pinned builder passed all original
preservation, accounting, native schema, compilation and retained-hash checks.
No frozen archive was overwritten and no routine full-corpus regression was run.

**Stage one is published and independently downloaded:** evidence commit
`57032484aa098d18fecf69fe186b2ef753473245`, immutable tag
`v04-all-65-complete-draft-stage-one-20261029-0b2fdb2d3`.
[Review/download](https://github.com/vanderpol/scap-ng-evidence/tree/57032484aa098d18fecf69fe186b2ef753473245/runs/v04-converter/2026-10-29-all-65-complete-draft-stage-one).
Archive **81,003,351 bytes**, SHA-256
`5338f760dbc043f6302bc7d65e65a130281c22549f9ea34f2a4e51f4921ff18c`.
Published download checksum/ZIP CRC PASS. Counts match the previous completed
report: 65 / 8,892 / 7,239 attempts / 4,206 retained static proofs / 52 UNVERIFIED
native / 2,981 blocked automated / 1,653 manual. All 4,258 candidates compile.
[#251 publication receipt](https://github.com/vanderpol/scap-ng/issues/251#issuecomment-6507303662).

All nine hosted workflows at **`0b2fdb2d3`** passed. Maintained
[40927089208](https://github.com/vanderpol/scap-ng/actions/runs/40927089208), job
123635368063, artifact 12920644342: **3,308 run, 3,307 passed, zero failures/errors,
one existing skip**, 603.717 seconds. Do not repeat that suite for this code.

The current integration adds independent frozen identity crosswalks and direct
admission for unchanged approved `iosxe.line`/`iosxe.global` mappings. **38**
original Rule closures prove with all DRAFT authoring/program hashes retained;
**66** source-pinned Tests pass, six new positive/negative regressions and 29
other affected tests pass. All **1,072 six-source proofs/program hashes** retain
parity. Fourteen existing SMF additions also independently replay with unchanged
DRAFT hashes. Candidate total: **4,258 static primary proofs**, with all prior
4,206 retained. The frozen DRAFT labels are unchanged. [Compact proof receipt](../audit/v04-iosxe-proof-recovery-20261029.json).
Exact implementation **`b70802028075850cf5f4397c50249813f86a7b14`** is now
hosted-green: all nine workflows passed. Maintained
[40947935428](https://github.com/vanderpol/scap-ng/actions/runs/40947935428), job
123708112106, artifact 12931846286: **3,314 run / 3,313 passed / zero failures
or errors / one existing skip**, 1188.663 seconds. Six-source
[40947935273](https://github.com/vanderpol/scap-ng/actions/runs/40947935273), job
123708111193, artifact 12931430305, retains all 1,072 anchor proofs.
Do not rerun this maintained suite for unchanged implementation.

[Population/catalog investigation](../audit/v04-population-binding-resumption-20261029.md)
is complete enough for owner decisions under #255. All **992** catalog failures
across 21 sources have exact embedded Definitions and complete target chains,
but foreign `ds:uri` elements have no standard XML Catalog URI semantics. They
are XSD-permitted extensions, not evidence of absent content or a demonstrated
standard resolver bug. No repair/admission is inferred. For **1,184** primary
all_exist blockers, 589 have States, 115 Variable closures, 136 Sets/Filters
(overlap); 577 simpler cases still require the collection contract. Eleven OVAL
boundary vectors preserve zero/positive/partial/error/unknown/incomplete cases.
No schema/compiler/scanner/oracle or prior proof meaning changed.

Recovery: `/workspace/recovery-20261029-resume/` contains complete originals,
DRAFT output, recovered baseline/exclusions, archive package driver, published
download checksum, population/binding audit, independent stage-two proof records,
six-source retention and focused logs. `stage-two/` is the superseded first
IOS XE reader attempt (UNVERIFIABLE); use **`stage-two-verified/`** with the new
crosswalks. Separate [52-proof evidence checkpoint](https://github.com/vanderpol/scap-ng-evidence/tree/v04-stage-two-52-static-verified-20261029-b70802028/runs/v04-converter/2026-10-29-stage-two-52-static-proofs-b70802028)
retains full original/native term comparisons, packages and all 52 unchanged
DRAFT hash pairs. The compact source receipt contains all identities/hashes.
The stage-one DRAFT archive and its labels remain unchanged. Evidence commit:
`5b1b027623cd454b263aa60e16122bba503566a9`.
Preserve the at-least-30-minute publication cadence per repository. The additional 39 source investigations yield 13 INVALID and 26 VALID
closures; six have deprecated WMI content (three also invalid). Thus 23 are
valid/nondeprecated, with existing comparator-absence, ordered-float, field
crosswalk and split/function boundaries still unresolved; no extra admission.
Owner-requested [IOS XE content report](../audit/v04-iosxe-content-investigation-20261029.md)
distinguishes four Schematron failures from semantic content defects: concat
integer casting conflicts with the same OVAL schema's casting prose, while
SV-215833 has stronger text-as-int and literal-backslash delimiter concerns.
All four occur in NIWC's enhanced oval2 component; DISA-origin attribution is
unestablished. No source or validator was repaired. Next: obtain #255 population,
producer-extension and function-casting decisions, pin corrected source where
required, and continue independently justified converter work. No unsupported
lowering or DRAFT regeneration.

## Preceding priority — complete reviewable all-65 DRAFT first

Owner revised release strategy on 2026-10-29: publish a complete, reviewable
all-65 DRAFT **before completing independent proof coverage**. Attempt every
automated conversion regardless of available independent readers. Preserve all
original Rules and manual content; include structurally valid unverified native
candidates with explicit labels, and retain unsupported/invalid blockers. Never
fabricate executable Assessments. Independent verification follows as stage two;
strict verified-upgrade/final-release validation is unchanged.

[Operator contract and exact command](ALL65-DRAFT-REVIEW.md). The new builder
uses all existing approved mappings diagnostically without activating unproved
production admission. No schema/mapping/compiler/scanner/editor/#255 change.
The original frozen all-65 archive remains immutable; a new unique DRAFT revision
is the expressly authorized full-corpus deliverable, not a routine regression.

Generation and the complete preservation/ledger/hash audit have finished:
**65 benchmarks, 8,892 original Rules, all 7,239 automated attempts**, 4,206
exact-hash retained published static proofs, **52 structurally valid UNVERIFIED
native candidates**, 2,981 explicitly blocked automated Rules, and 1,653
manual/OCIL-only Rules preserved. All 4,258 native candidates compile with checked
operands; complete originals/manual content remain separate from native partial
Rule-policy wrappers. Every Rule ID and original component was independently
reconciled against its preserved original ZIP. No fabricated blocked/manual
Assessment is present. All 65 ZIP pins and all 4,206 source/authoring/program
baseline hashes retain parity.

The nine DRAFT regression tests pass in scoped runs; the existing eight-test
representative benchmark/API/CLI suite also passes (17 distinct checks). No
all-65 regression was added to normal CI. Exact new-builder hosted integration
follows this commit; this DRAFT is not labeled a verified release.

Publication is the unique
[complete stage-one DRAFT](https://github.com/vanderpol/scap-ng-evidence/tree/main/runs/v04-converter/2026-10-29-all-65-complete-draft-stage-one),
with immutable archive/ledger/checksum links recorded in #251 after upload. Do not
wait for complete independent proof coverage before publication. The earlier
47 MB frozen all-65 archive remains unchanged.

Recovery `/workspace/full-draft-20261029/`: `all-65-draft/`, `generation.log`,
`proof-baseline.json` (4,206 records including original ZIP SHA-256),
`known-invalid-final.json` (32 source exclusions), final reporting/preservation
auditor, `RUN-STATE.json`, and the original driver snapshot. Reporting was
normalized after generation without rerunning conversion. Four additional IOS XE
invalid originals were already blocked; their precise validity diagnostics are
retained. `package_draft.py` packages the review with the exact new code commit.
Publish DRAFT, then continue stage-two independent verification in bounded batches;
strict verified-upgrade/final-release requirements stay unchanged.

### Preceding Solaris integration is green

`87417fb21ddcab8b9405a17987821fc6e5701111`: all nine exact-commit workflows pass.
[Maintained run 40914906704](https://github.com/vanderpol/scap-ng/actions/runs/40914906704),
job 123592419747, artifact 12916930695: **3,299 run / 3,298 passed / zero
failures or errors / one existing skip**, 609.640 seconds.
[Six-source gate 40914906671](https://github.com/vanderpol/scap-ng/actions/runs/40914906671),
job 123592418648, artifact 12916286651: all 1,072 anchor proofs retained.
Fourteen actual Solaris Rules pass selected primary acceptance; all 3,130 prior
cohort hashes and 523 prior conformance four-hash records retain parity. Three
SMF conformance Tests additionally prove: 526/716 configured of 803 originals.
Durable SMF proof promotion can follow DRAFT publication; do not let it block
stage one. The DRAFT's carried published proof baseline remains 4,206.

Recovery `/workspace/coverage-next-20261029/` retains SMF evidence, exact CI,
release-readiness overlay and a diagnostic IOS XE probe: 38/43 prove locally,
four original-invalid/deprecated and one count-function blocker. IOS XE is not
activated in strict production admission; further proof expansion is deferred
until DRAFT publication. [Release-blocker report](../audit/v04-release-readiness-20261029.md)
retains the measured unresolved contracts and source-remediation debt. No new
normative answer is inferred. Commit/push windows remain at least 30 minutes
apart without routine owner approval questions.

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
