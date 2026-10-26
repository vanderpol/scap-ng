# Canonical metadata and schema-change synchronization

Authority: [#251](https://github.com/vanderpol/scap-ng/issues/251).
BASE_SHA: `52efe1195d2cee9318a3b8934476ad257e78e7c5`.
RESULT_SHA: `ceb2e6aadd0c855aadf912841c81d2c7bc979703`.
SCHEMA_VERSION: 0.4.0. No normative schema, converter/compiler behavior or existing
release gate is changed. The 883-Assessment package ledger is unchanged.

**Why the residue existed.** `aa26ba6a5` copied the stale acquisition crosswalk
paths into the 0.4 catalog on October 15. `5b712d934` introduced the maintained 0.4
schema adapter, which invokes the preceding generator and flattens/rewrites its
output. The fresh converter reused current versioned mappings and the required
public validator/compiler, but the intake review did not catch obsolete metadata.
That was a review gap. Accepted authoring already rejects generic wrappers; that
does not justify retaining them in the current mapping contract.

**Correction.** Twenty-seven metadata files now use canonical Object paths and
the approved `filesystem: all` spelling. All **30 normative schema files** remain
byte-identical. All **100 generated validation structures** remain identical,
excluding descriptive semantic-rule annotation text updated to the canonical paths.
The cmdlet `select` parameter, its nullable record contract and source semantics
are preserved; a regression explicitly accepts it and rejects generic wrappers.
No deprecated aliases or source normalizations are introduced.

**Automatic process.** A new read-only workflow reacts to native schema/mapping
and pinned OVAL schema changes, regenerates native contract data, checks target
paths, and runs focused source/schema/compile tests. Its artifact contains all
100 generated contracts and source-route review items. Ordinary field refresh is
tested without a Python capability branch. Invalid metadata fails the check while
preserving a review artifact. The unresolved `file.hash` algorithm route is
reported; it is not inferred or admitted. The process updates declarative contract
data, not arbitrary Python. Current runtime field maps remain data-driven; new
semantics still require explicit shared implementation and proof.

**Evidence.** Independent original-source comparison still proves **249 Rules**,
with **zero compiled-unproved / 42 blocked**. All **500 authoring documents** and
**249 compiled-program hashes** are identical to the preceding checkpoint. The
original source ZIP/XML hashes remain
`2f46264b5fa21c8a033236121794ebe372314bf7458dac0aca4f81179fe7ece0` /
`52b7918ea577095cb1c130589e5061c52ef4b12370ebb4ce84d2dfba68757440`.
All 39 user-rights closures remain proved. Source-invalid cases remain blocked.
The [machine packet](v04-schema-converter-sync.json) records schema hashes, program
hashes, changed mappings, exact tests and CI outcomes.

TESTS: the initial **3,081-test** maintained run had one failure, zero errors,
one existing skip: two stale native metadata citation hashes. Both citations were
refreshed with their original revisions/hashes retained; strict assertions are
unchanged. The affected **18-test** proof suite and **seven** final contract tests
pass; 34 related schema/source checks and the 100-capability generation audit pass.
The final local maintained run and exact-head hosted mandatory artifact both
confirm **3,081 run, zero failures or errors, one existing skip** (3,080 passed),
with identical selected test IDs. The downloaded hosted ZIP digest matches
GitHub's recorded SHA-256. No failed check is hidden, skipped or relabeled as a pass.
CI: **12 successful / six failed / zero pending** at RESULT_SHA. The
[mandatory rebaseline](https://github.com/vanderpol/scap-ng/actions/runs/40367741429),
[schema synchronization](https://github.com/vanderpol/scap-ng/actions/runs/40367741273),
current-design, canonical, shared-core, capability-generation and clean-extract
checks passed. This is **not an all-green checkpoint**: six older source-proof
consumers still emit or consume obsolete native grammar. All six reproduce at
unchanged `52efe1195` and RESULT_SHA; authenticated hosted logs now independently
confirm their failure diagnostics. The [complete reconciliation](v04-ceb2-ci-reconciliation.md)
records all 18 runs, original source pins, exact errors and the remaining gate.

**Maintainability and scale.** The active conversion/source/inventory/rendering
core is 1,344 physical lines across eight modules; the initial retained experiment,
sample publisher and independent proof tools are separate. This count is not a
claim that fewer lines automatically establish maintainability. Necessary
complexity includes scoped dependencies, quantifiers, ordered Set/Filter boundaries,
records, error/unknown collection and independent verification. Avoidable debt
includes old generator adaptation, per-capability source-validation branches and
duplicated work. The recorded baseline spends about 0.16 s lowering versus
28.85 s validating (32.07 s conversion phase, excluding serialization). The parity
run was concurrent with regressions, so its timings are not a speedup comparison.
Neither result proves scaling to all capabilities or a whole corpus.

NEXT_ENGINEERING_OBJECTIVE: reconcile the six source-proof consumers while
preserving their original evidence and assertions. Removing legacy schema-generation
coupling under exact contract parity remains conditional on the requested fully
green checkpoint; that refactor has not started. Later shared work includes source
XSD/Schematron validation and validator reuse. No replacement framework,
scanner implementation, production replacement, signing or release is authorized
by this checkpoint. See the [developer guide](../developer/DIRECT-V04-CONVERTER.md)
for the regeneration command and module responsibilities.

Earlier issue commenting returned `Post "https://api.github.com/graphql": Forbidden`.
During this reconciliation, authenticated REST access to issue comments, exact-head
Actions metadata, logs and the mandatory result artifact succeeded. Read access
does not establish issue-write access; the final engineering handoff records the
actual comment attempt separately.
