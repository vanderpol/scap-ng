# Frozen compiled-cohort independent proof expansion

**Completed assigned cohort: 3,130 independently proved / 3,138 assessed / zero pending**, across 32 benchmarks of the frozen all-65 archive. The seven invalid originals and one deprecated original remain explicitly rejected. Every valid, nondeprecated original in this previously compiled/unproved cohort now has an independent primary OVAL proof.

The prior 1,072 anchor proofs, four guard additions, and all 523 conformance four-hash records remain retained. Total independently proved primary Rules across those distinct source/Rule identities: **4,206**. Conformance Tests use a separate denominator. This does not establish complete 0.4.0 release readiness or scanner-runtime equivalence.

[Machine-readable cumulative index and full exclusion diagnostics](v04-compiled-proof-expansion-20261029.json).

## Published bounded batches

- [2026-10-29-compiled-proof-batch-001-dc42163d2](https://github.com/vanderpol/scap-ng-evidence/tree/cf70833bc532f801c000ab305e16ac836a8289f8/runs/v04-converter/2026-10-29-compiled-proof-batch-001-dc42163d2): 243/243 selected primary closures proved; 22 representative source/compiled cardinality mutations rejected. ZIP 2,216,969 bytes; SHA-256 `665c1f8a99cfb4788a101348cfe4ccd866fd0877f239aa0afb9fde2ce4b0f879`.
- [2026-10-29-compiled-proof-batch-002-dc42163d2](https://github.com/vanderpol/scap-ng-evidence/tree/cf70833bc532f801c000ab305e16ac836a8289f8/runs/v04-converter/2026-10-29-compiled-proof-batch-002-dc42163d2): 602/602 selected primary closures proved; 70 representative source/compiled cardinality mutations rejected. ZIP 5,542,985 bytes; SHA-256 `195923b007a3be79e11840e18de15a3f6cfea40e369ec70d0e27d215fe5387f0`.
- [2026-10-29-compiled-proof-batch-003-dc42163d2](https://github.com/vanderpol/scap-ng-evidence/tree/b08a01c33cf84dcc5d50ca9e781b08f546d9134e/runs/v04-converter/2026-10-29-compiled-proof-batch-003-dc42163d2): 446/448 selected primary closures proved; 44 representative source/compiled cardinality mutations rejected. ZIP 4,372,264 bytes; SHA-256 `4e23bda8b45bd032c10dd97426db8205f844cdd094ffe1f8770236b728f65ac6`.
- [2026-10-29-compiled-proof-batch-004-dc42163d2](https://github.com/vanderpol/scap-ng-evidence/tree/b08a01c33cf84dcc5d50ca9e781b08f546d9134e/runs/v04-converter/2026-10-29-compiled-proof-batch-004-dc42163d2): 1804/1845 selected primary closures proved; 268 representative source/compiled cardinality mutations rejected. ZIP 17,926,832 bytes; SHA-256 `1895e7d70e619da340e8cdac85748217728e930475d60d1c73a8fd6bb1f83860`.
- [2026-10-29-compiled-proof-batch-005-5e847f826](https://github.com/vanderpol/scap-ng-evidence/tree/42979846586581a431dfc4dc6727709a303d53e6/runs/v04-converter/2026-10-29-compiled-proof-batch-005-5e847f826): 35/35 selected primary closures proved; 8 representative source/compiled cardinality mutations rejected. ZIP 959,855 bytes; SHA-256 `e7165846f8017d86463a455cfa9eebfd0befdf3aeacfe2b92ee83712508e8b36`.

The final 35 are retries of earlier reader-limited outcomes. They supersede those outcomes and do not increase the 3,138 distinct-candidate denominator. Earlier evidence remains immutable.

## Verification and preservation

All eight path-selected workflows at `5e847f8268697f7555a442256c06f5bfa48f4676` passed. [Maintained run 40904268977](https://github.com/vanderpol/scap-ng/actions/runs/40904268977), job 123554611774, artifact 12910359527: **3,292 run / 3,291 passed / zero failures and errors / one existing skip**, 619.389 seconds. [Six-source gate 40904268774](https://github.com/vanderpol/scap-ng/actions/runs/40904268774), job 123554610454, artifact 12910957628: all **1,072** original anchor proofs retained. The Bluetooth workflow was not path-selected by these reader-only edits; its unchanged original-source acceptance CLI also passes locally, and its regression tests are included in the maintained suite.

The correction implements existing Registry constant-multiset, multi-string equality and filtered-projection contracts; [original-backed review packet](v04-registry-reader-proof-expansion-20261029.md). Its 61 focused tests include eight new positive/negative/mutant/Filter/cycle tests. Final selected acceptance at the exact published commit proves all 35 targets. Both corrected readers retain all 3,095 preceding new primary proof/source/native-term hashes and frozen canonical authoring digests. All 523 preceding conformance four-hash records retain parity (523/713 configured Tests, 803 originals). The four preceding NTUSER/Solaris additions recompare and retain their exact published program hashes.

Every original ZIP is SHA-256/Git-blob checked at NIWC `8c8e5dff860af6b1290ee9273a282db24278f8d5`. Original primary closures pass XSD, Schematron, semantic-reference and deprecation checks before acceptance. Frozen Rule/dependency identities, native schemas, independent source/native terms, compiled operands and package consumers are checked. Every frozen authoring document and compiled program hash is retained. The final evidence additionally verifies the four earlier distributed archives against manifests/CRCs and binds all 3,095 full terms/authoring records back to their compact receipts.

## Eight excluded originals

| Original Rule | Exclusion |
| --- | --- |
| `SV-251550r961194` | Invalid required pattern operation in the original closure |
| `SV-221655r958390` | Invalid required pattern operation in the original closure |
| `SV-225228r1043178` | Invalid required pattern operation in the original closure |
| `SV-225233r1117179` | Invalid required pattern operation in the original closure |
| `SV-225237r1043178` | Invalid required pattern operation in the original closure |
| `SV-214433r879756` | Deprecated original file_test check="none exist" |
| `SV-230226r1069298` | Invalid required pattern operation in the original closure |
| `SV-248528r958390` | Invalid required pattern operation in the original closure |

The immutable inputs are not repaired or relabeled. Recommendation: retain these exclusions until corrected upstream source is pinned and independently validated. No owner decision is required to preserve the current rejection policy.

## Boundaries and recovery

Schemas, mappings, converter/compiler, scanner/editor, protected workflows and #255 semantic contracts remain unchanged. The frozen all-65 archive was not regenerated. Full policy, applicability/CPE, manual execution, runtime parity and complete toolchain-release verification remain separate work. The larger draft automated blockers and #255 decisions are not discharged by completing this cohort.

Recovery: `/workspace/proof-expansion-20261029/`; final exact-commit acceptance is `batch-008/`, with final retention, CI and immutable evidence refs alongside it. Inputs remain `/workspace/recovery-20261029/inputs/`. Do not repeat the exact-commit maintained suite or restart this completed cohort. Commits/pushes remain consolidated into windows at least 30 minutes apart without routine approval requests.
