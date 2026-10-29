# Frozen compiled-cohort independent proof expansion

Under [#251](https://github.com/vanderpol/scap-ng/issues/251), **3,095 of the original 3,138 compiled/unproved Rules** now have independent original-source proofs. 43 processed cases remain unproved; 0 are pending. The original cohort spans 32 benchmarks.

The prior 1,072 anchor proofs, four subsequent guard additions, and all 523 conformance four-hash records remain unchanged. Total independently proved primary Rules across those distinct source/Rule identities: **4,171**. Conformance Tests remain a separate denominator.

[Machine-readable cumulative index](v04-compiled-proof-expansion-20261029.json).

## Published bounded batches

- [2026-10-29-compiled-proof-batch-001-dc42163d2](https://github.com/vanderpol/scap-ng-evidence/tree/cf70833bc532f801c000ab305e16ac836a8289f8/runs/v04-converter/2026-10-29-compiled-proof-batch-001-dc42163d2): 243/243 original primary closures proved; 22 representative source/compiled cardinality mutations rejected. Evidence ZIP: 2,216,969 bytes; SHA-256 `665c1f8a99cfb4788a101348cfe4ccd866fd0877f239aa0afb9fde2ce4b0f879`.
- [2026-10-29-compiled-proof-batch-002-dc42163d2](https://github.com/vanderpol/scap-ng-evidence/tree/cf70833bc532f801c000ab305e16ac836a8289f8/runs/v04-converter/2026-10-29-compiled-proof-batch-002-dc42163d2): 602/602 original primary closures proved; 70 representative source/compiled cardinality mutations rejected. Evidence ZIP: 5,542,985 bytes; SHA-256 `195923b007a3be79e11840e18de15a3f6cfea40e369ec70d0e27d215fe5387f0`.
- [2026-10-29-compiled-proof-batch-003-dc42163d2](https://github.com/vanderpol/scap-ng-evidence/tree/b08a01c33cf84dcc5d50ca9e781b08f546d9134e/runs/v04-converter/2026-10-29-compiled-proof-batch-003-dc42163d2): 446/448 original primary closures proved; 44 representative source/compiled cardinality mutations rejected. Evidence ZIP: 4,372,264 bytes; SHA-256 `4e23bda8b45bd032c10dd97426db8205f844cdd094ffe1f8770236b728f65ac6`.
- [2026-10-29-compiled-proof-batch-004-dc42163d2](https://github.com/vanderpol/scap-ng-evidence/tree/b08a01c33cf84dcc5d50ca9e781b08f546d9134e/runs/v04-converter/2026-10-29-compiled-proof-batch-004-dc42163d2): 1804/1845 original primary closures proved; 268 representative source/compiled cardinality mutations rejected. Evidence ZIP: 17,926,832 bytes; SHA-256 `1895e7d70e619da340e8cdac85748217728e930475d60d1c73a8fd6bb1f83860`.

## Gates and preservation

Each batch reads only its selected frozen compiled/unproved cohort. The frozen all-65 archive is SHA-256 checked, never regenerated, rewritten or relabeled. Every selected original ZIP is checked against both SHA-256 and pinned Git blob identity at NIWC `8c8e5dff860af6b1290ee9273a282db24278f8d5`. Original primary closures must pass XSD, Schematron, semantic-reference and deprecation checks. Generated native content must validate, independently compare typed source/native graphs, compile with independently checked operands, and pass the package consumer.

Every newly proved original Rule and dependency identity matches the immutable DRAFT ledger. Each frozen authoring document is structurally identical and each compiled program hash is unchanged. Full independent terms, accepted packages, generated JSON/YAML, source traces, source-validity outcomes, negative results and the reproduction snapshot are published in the evidence ZIPs; compact four-hash/provenance records and real representative authoring/terms are also browseable. Failed, invalid or unsupported closures stay explicit and do not enter accepted packages.

These four published evidence batches use unchanged production tools and proof rules at `10f4e35b3`. The current independent-reader correction is separately documented in the [reader packet](v04-registry-reader-proof-expansion-20261029.md), with its own integration gate. No schema, mapping, converter/compiler, scanner/editor or protected workflow changed. The existing nine green exact-code workflows at `10f4e35b3` remain valid for those first-pass batches; maintained run [40867417638](https://github.com/vanderpol/scap-ng/actions/runs/40867417638) ran 3,284 tests with zero failures/errors and one existing skip. No duplicate full suite was launched for new evidence inputs. This is not an all-65 regeneration or runtime equivalence claim.

## Continuing work

Batches proceed by original benchmark and real Rule impact. Pending #255 contracts remain blocked; no source repair, operation erasure, datatype cast, production all_exist lowering, scanner work or 0.5 expansion is included. Recovery/work files are under `/workspace/proof-expansion-20261029/`; original ZIPs remain under `/workspace/recovery-20261029/inputs/`. Commit/push publication is consolidated to no more than one window every 30 minutes; scoped passing work is already authorized and needs no routine approval.


The complete first pass leaves **35 reader-limited cases, seven invalid originals
and one deprecated original**. The reader correction locally proves all 35 with
unchanged frozen output, and preserves every prior new proof/hash. Those 35 are
not included in the published verified total until their exact integration gate
passes. See the reader packet for the original examples, tests and metadata.
