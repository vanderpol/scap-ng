# What still prevents a complete 0.4 release

This non-normative checkpoint separates real primary-source coverage, blocked
assessment contracts and uncompleted release verification. It does not change
release scope or ratify a semantic decision. Sources: the immutable all-65
DRAFT, five published proof batches, four subsequent guard proofs, original
deprecation declarations and explicit support overrides. No conversion archive
was regenerated. The [machine-readable reconciliation](v04-release-readiness-20261029.json)
retains exact original Rule representatives and primary messages.

## Current coverage, before the pending SMF integration

All **8,892** original Rules reconcile: **4,206** independently proved primary
OVAL Rules, **1,653** manual/OCIL-only Rules and **3,033** unproved automated Rules.
The previously compiled/unproved cohort is complete: 3,130 proved, seven invalid
originals and one deprecated original excluded. It is not the entire corpus.

The following disjoint buckets partition the 3,033 residual automated Rules:

| Primary disposition | Rules | Next action |
| --- | ---: | --- |
| Blocked assessment contracts under #255 | 1,630 | Owner/contract decisions before production lowering |
| Original catalog binding unresolved | 992 | Investigate pinned packaging; preserve source and explicit failure |
| Effective deprecated Test types | 150 | Upstream remediation; do not implement deprecated collectors |
| Nonstandard SQL-extension package exceptions | 137 | Keep four packages isolated and fail-closed |
| Converter/independent-reader investigation | 96 | Validate originals and implement existing approved contracts in bounded batches |
| Known original invalidity/deprecation | 28 | Preserve rejection; pin corrected upstream inputs before retry |

The 150 type-based exclusions independently apply original XSD deprecation and
the existing reinstatement overrides, including deprecated access-token/WMI/user
Tests. The 28 validity exclusions include earlier recorded invalid closures and
the eight nil-record cmdlet failures. They are distinct buckets. Counts are
primary dispositions, not guaranteed unlocks; secondary blockers overlap and
remaining closures have not all had original-source validity checks.

The [pending Solaris SMF activation](v04-solaris-smf-activation-20261029.md)
proves 14 of the 96 investigation cases locally. After its own integration and
evidence gates pass, primary coverage becomes **4,220**, automated unresolved
becomes **3,019**, and the investigation bucket becomes **82**. These totals
remain pending here; do not count an unpublished/unverified increment as green.
The next large existing-mapping candidates are 43 IOS XE line/global cases;
their original validity and secondary blockers still need checking.

## Contract decisions with the largest measured impact

The 1,630 primary cases split into **1,184 all_exist/population**, **382 OVAL
check import/export bindings**, **30 multiple aggregation components**, **32
function cases** (15 split, 14 count, three substring), and **two acquisition
comparison/type cases**. Existing [#255](https://github.com/vanderpol/scap-ng/issues/255)
and [#218](https://github.com/vanderpol/scap-ng/issues/218) boundaries remain
blocked. No source repair, lossy cast, operation erasure or incomplete-population
shortcut is authorized by these counts.

Small concrete unresolved acquisition examples already documented in the
[guard packet](v04-nil-filename-defaults-20261029.md): .NET `SV-225226r961041`
uses case-insensitive command acquisition; Windows 10 `SV-220812` uses a
version-typed module acquisition. Both original closures are valid and
nondeprecated. Recommendation: retain both blocked until an explicit acquisition
contract is accepted. Population/all_exist and source-bound external inputs have
the highest recorded primary impact; their examples and secondary diagnostics
are retained in the frozen ledgers and #255. No new owner answer is inferred.

## Release gates beyond primary conversion

A full-migration or production-replacement claim remains **NO-GO**. A deliberately
scoped subset prerelease is a separate release-scope decision; this report does
not require every published STIG Rule to convert before any prerelease.

The [toolchain-release contract](../releases/TOOLCHAIN-RELEASES.md) still requires
an exact committed/tagged source snapshot with complete version-local schemas,
specification, guides, examples, dependency bill of materials and checksums;
clean extraction/CLI execution; a pinned repeatable installation plan; and a
source-to-native-to-compiled-package independent verification run with negative
and deprecated cases. These final release gates are not established by the
current proof census or by an archive-integrity check alone. Do not describe
unrun gates as passing. No new release/tag is authorized by this checkpoint.

Full Benchmark policy, applicability/CPE, manual choices and selection remain
outside primary OVAL proof coverage. Scanner-runtime equivalence, publisher trust
and human acceptance are separate claims; signing is required when the release
claims authenticated publisher artifacts. The historical
[finalization matrix](../../review/current/0.4.0-FINALIZATION-GATES.md) contains
dated evidence, not an exact current-code certification. Its Studio work remains
outside this converter task; no scanner/editor changes are made.

Next practical order: finish the bounded SMF integration; investigate source-valid
existing-mapping cases; preserve source-remediation debt; obtain the existing
high-impact #255 decisions; then run the deliberately scoped clean-toolchain
release gates at the final exact release candidate. Keep all unresolved cases
and proof/hash baselines explicit.
