# Direct Registry hive relation proof — 2026-10-25

Continued autonomously after the [authoring correction](v04-direct-authoring-acceptance.md),
under [#251 engineering ownership](https://github.com/vanderpol/scap-ng/issues/251#issuecomment-6401652271).
The pinned Windows Server 2025 source remains unchanged.

| Field | Verified result |
| --- | --- |
| BASE_SHA | `cef742119ea1097f5fb1179a46a3ebac79689a17` |
| RESULT_SHA | `2c850a36bc6297d7cdf0b39d3f3b3a0ffc87dcf2` |
| IMPLEMENTED | Original literal Registry hive comparison over its closed domain |
| SOURCE_PROVED | **130 → 149** of 291 original Rules (**51.20%**) |
| COMPILED_UNPROVED / BLOCKED | **0 / 142** |
| TESTS | **3,026**, zero failures/errors, one unchanged skip; **32** related checks pass |
| REGRESSIONS | **0**; all **130** pre-existing program hashes unchanged |
| CI | **All 5 exact-head workflows PASS** |
| AUTHORING | 149 Assessments / 192 Tests; **114** inline, **7** shared references to **1** named Object, **71** no-Object Tests; **120** compact Registry Objects; deprecated grammar **0** |
| NEXT | Independent user-rights proof, with mixed dependencies and Variable/filter cases isolated |

**Source proof.** Original `EntityObjectRegistryHiveType` and
`EntityItemRegistryHiveType` admit six canonical hives plus an empty placeholder.
The independent reader reads and hashes both original OVAL 5.12.3 XSD types and
checks all **49** pairs: equality and case-insensitive equality have the same
literal relation. The six nonempty tokens map one-to-one to the approved native
enum. No case correction is applied to invalid lowercase source tokens.

The producer now admits `case insensitive equals` only for **nonempty literal
Registry hive acquisitions** under this contract. Its typed native selector uses
`equals`; original Object IDs, attributes, values and rationale remain in external
provenance and are independently recorded by the proof reader. Source States,
dynamic operands, empty/unknown hives and other enum comparators remain strict.
Registry **key** comparisons retain their original operation; a negative mutant
demonstrates that erasing a key's case-insensitive comparison fails proof.

**Evidence.** All **19** newly admitted original Rules independently prove and
compile. Their exact Rule/Definition/Test/Object/State identities, original
dependencies, source hashes, per-case domain evidence and compiled program hashes
are in the [machine packet](v04-direct-registry-hive.json). Six separately labeled
controlled source copies exercise every literal hive. Equality-spelled and
case-insensitive-spelled copies emit identical collection, cardinality, reporting
and Boolean contracts. Empty/invalid/dynamic/type/State mutants reject; changed
native hive/key operands fail independent comparison. No synthetic Items or
error/incomplete/unknown normalization is introduced. Existing `all_exist`
blockers remain blocked.

The maintained public gates validate **300 JSON and 300 YAML documents**, compile
both serializations, and pass the separate package consumer with exact operands
for **149 programs**. All earlier 130 program hashes are preserved. The published
[human-readable examples](../examples/direct-v04/README.md) remain pinned to the
earlier authoring checkpoint; they were not silently regenerated. The approved
schema tree, production converter/compiler, release gates and six-STIG packages
are unchanged. This is original-source/compiled-term proof, **not scanner parity**
or production readiness.

**Reproduce.** Run `PYTHONPATH=tools python tools/test_v04_direct_registry_hive.py -v`.
The [developer guide](../developer/DIRECT-V04-CONVERTER.md) documents the contract,
public whole-source converter/audit commands and strict limits. Use the maintained
regression command with the unchanged pinned Self-Assertion bindings. The packet
records those results, public consumer evidence and generation metrics: one SCAP
parse/index, **14.549 s** admission validation for 300 documents. Workload differs
from the 262-document baseline; **no speedup is claimed**.

**Next census.** User-rights appears in 39 original Rule closures containing 79
Definitions, 53 Tests, 34 Objects, 18 States and one Variable. Two WMI Objects/four
record States are dependencies, so family-only admission would overclaim coverage.
One Object combines a 45-value enum Variable with a Filter. Its omitted
`var_check` defaults to `all` in original OVAL; preserve that token/meaning and
investigate source intent separately before any extension. No source-specific
repair or additional capability admission is included here. GO for that bounded
source-proof work; signing/trust, runtime acceptance and remaining release gates
remain open. Issue commenting was Forbidden earlier in this session; the committed
report is the authorized handoff and no further comment retry was made.

Exact implementation CI: [rebaseline](https://github.com/vanderpol/scap-ng/actions/runs/40237111067), [canonical](https://github.com/vanderpol/scap-ng/actions/runs/40237111054), [current regression](https://github.com/vanderpol/scap-ng/actions/runs/40237111170), [documentation](https://github.com/vanderpol/scap-ng/actions/runs/40237111096), [issue reference](https://github.com/vanderpol/scap-ng/actions/runs/40237111099). All are for `2c850a36bc6297d7cdf0b39d3f3b3a0ffc87dcf2`.
