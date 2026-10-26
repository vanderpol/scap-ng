# Exact-head regression and CI reconciliation — #251

RESULT_SHA: `ceb2e6aadd0c855aadf912841c81d2c7bc979703` (synchronized `main`).
STATUS: **BLOCKED_NOT_ALL_HOSTED_CI_GREEN**. Schema version: 0.4.0.
Authority: [latest coordination review](https://github.com/vanderpol/scap-ng/issues/251#issuecomment-6424395691)
and the owner's request to reconcile this commit before removing generator coupling.

The complete **hosted maintained suite ran 3,081 tests: 3,080 passed, one existing
skip, zero failures/errors**. The [rebaseline run](https://github.com/vanderpol/scap-ng/actions/runs/40367741429)
is successful at the exact SHA. Its downloaded `current-v04-regression-results`
artifact contains the complete selected IDs and actual results; ZIP SHA-256
`7611e8d9970c4a2069a710dd8046e2770f667ed8e7304b8966949502a96294bb`
matches GitHub's digest. This supersedes the earlier precommit one-failure run;
that failed citation-hash evidence remains in the [original packet](v04-schema-converter-sync.json).
The sole skip is the unchanged full-corpus-only local-literal census.
The final **local** rerun independently reports the same 3,081 tests, zero
failures/errors and one skip; its selected test IDs exactly match the hosted
artifact. The local run uses the workflow's pinned dependencies and all 23
original-source bindings. Environment versions, source hashes and local
report/log hashes are recorded in the machine packet. The mandatory public
Benchmark/package test also passed its 500 JSON/YAML document checks and
deterministic compiled-bundle comparison.

All **18** exact-head hosted runs are complete: **12 success, six failure**.
Passing checks include mandatory rebaseline, current-design contracts, canonical
authoring, shared converter core, schema synchronization, native capability
generation, draft schemas, clean extraction, Self-Assertion, repository boundaries,
documentation and issue references. Full run URLs and authenticated failure-log
hashes are in the [machine evidence](v04-ceb2-ci-reconciliation.json).

| Failed source-proof workflow | Exact-head run | Reproduced cause |
| --- | --- | --- |
| Windows shellcommand | [40367743531](https://github.com/vanderpol/scap-ng/actions/runs/40367743531) | Obsolete `states` and scalar requirements |
| Windows WMI57 | [40367741455](https://github.com/vanderpol/scap-ng/actions/runs/40367741455) | Obsolete `states` |
| Windows cmdlet | [40367741745](https://github.com/vanderpol/scap-ng/actions/runs/40367741745) | Old record `selection_match: all` |
| Windows cmdlet Variable | [40367741482](https://github.com/vanderpol/scap-ng/actions/runs/40367741482) | Old record/expected-value cardinalities |
| Windows Set/Filter | [40367741671](https://github.com/vanderpol/scap-ng/actions/runs/40367741671) | Old scalar Filter requirement and `value_match: one` |
| Published Windows 11 Bluetooth | [40367741314](https://github.com/vanderpol/scap-ng/actions/runs/40367741314) | Immutable older package contains obsolete Filter requirements |

Each failure reproduces with identical original input at both unchanged
`52efe1195` and `ceb2e6a`; exact diagnostics, commands, source hashes and pinned
dependencies are retained in the machine packet. Hosted logs independently match
the local diagnostic in all six cases. These are native proof-consumer dialect
failures, not newly changed source OVAL or current direct-converter outputs.
The latest issue review also records these workflow names failing at `8d4774f4e9`.
They remain visibly red; no workflow is removed, rerouted, skipped or demoted.
No missing original-source assertion is credited as passing or replaced by the
different 249-Rule Server 2025 evidence.
These are the first failing diagnostics; downstream assertions and dated artifact
dependencies beyond those failures have not been established as passing.

**Preservation:** this reconciliation edits documentation only. All 30 normative
schema hashes and the pinned source ZIP hash were rechecked. Existing implementation
evidence remains **500 unchanged authoring documents, 249 unchanged compiled
program hashes, 249 source-proved / zero compiled-unproved / 42 blocked Rules**.
No separate conversion rebaseline was performed; mandatory tests exercise
conversion/package generation in temporary directories. No new coverage is claimed. The genuine cmdlet
`select` input remains supported. No schema, source, converter/compiler, release
gate or capability branch changed.

**Precise remaining decision:** the Bluetooth job asserts that the hash-pinned
October 21 package itself validates against current schema. It cannot pass that
assertion while retaining its obsolete bytes and today's schema. Agree whether
that archive check remains a historical reproduction, with its current semantic
assertions preserved in mandatory tests, or whether a separately identified,
source-proved current-schema derivative is the new acceptance target. A derivative
must not be reported as proof that the archived authoring validates unchanged.
The previous seven-workflow routing decision did not classify these six jobs.
Do not apply a historical partition or change release gates without authorization.

Generator decoupling is **not started**, honoring the owner's fully-green
prerequisite. Its later acceptance remains parity for all 100 generated contracts
and preservation of all existing source proofs/output hashes, without normative
changes or capability-specific conversion branches. No production-readiness,
scanner-parity or release claim is made.

Reproduction uses `python tools/run_current_tool_regressions.py --report RESULTS.json`
with the pinned bindings and dependencies in
[rebaseline-smoke.yml](../../.github/workflows/rebaseline-smoke.yml). Exact hosted
metadata/artifact commands and local rerun results are in the machine packet.
