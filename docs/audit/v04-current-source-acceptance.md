# Current-source acceptance and historical preservation — #251

BASE_SHA: `2e497980566ba8f3f35f73d8dc0f06c3a97b437b`. SCHEMA_VERSION: 0.4.0.
RESULT_SHA: `a3e30e27fc9e65a5fda331a88efaea984d12fc1d`.
The repaired six source workflows pass. Local and exact-head hosted maintained
results: **3,088 tests, zero failures/errors, one existing skip**, with identical
selected IDs and the hosted artifact SHA-256 independently verified. All **15
triggered current workflows** and the separate archival reproduction passed.
The [machine packet](v04-current-source-acceptance.json) records every run.

**Bluetooth:** the October 21 archive remains unchanged at ZIP SHA-256
`7a053e0aeaa866a3a019d76b6d35e441a4cdfc4c22fd0405c8b4dd29be645170` and
Assessment SHA-256 `e096d70827b032ea0029e43c252bc4a439a7e386b2e6717e333da6f974347b1b`.
Its original validator/export proof reproduces locally with schema/tool snapshot
`5ff36c8e2c7d18068e0d89255e047132e8ac6f97`. The separately named, explicitly
opted-in manual archival workflow pins that snapshot and retains the original
validation/mutation commands. Prior current-schema failure
[40367741314](https://github.com/vanderpol/scap-ng/actions/runs/40367741314) and
[reconciliation](v04-ceb2-ci-reconciliation.md) remain historical evidence.

The mandatory replacement reads **original SCAP**, not generated preview JSON:
Windows 11 V2R10 enhanced V18, ZIP
`e4b8d55b58aa80124bd0974977af4c7f7bde35c748e2940e02857419292d8c3d`, XML
`cfc5061d275235f6c5e0719cc384fb887f8624ae6e0dbac03f4a9cb3f43c06a5`.
Definition `oval:navy.navwar.niwcatlantic.scc.windows:def:102` resolves through
the original CPE applicability check/catalog to Test `...windows:tst:101`,
Object `...windows:obj:101` and Filter State `...windows:ste:101`.
The original has **no Set**: it directly includes stdout lines case-insensitively
equal to `Bluetooth`, then checks Item presence. The derivative uses the unchanged
generic direct converter, inline Object/structured requirement, and `purpose:
applicability`. Independent OVAL/native readers compare the full Test and
applicability expression. Five negatives detect an invented singleton UNION,
lost Filter, reversed action, altered value and changed Item existence.
Successful derivative validation never means the archived bytes validate today.

**Five retained source obligations:** unchanged Self-Assertion inputs/hashes,
independent reverse exporters, source assertions and negative mutations remain.
Four proof producers now expose current authoring through one approved projection
boundary: **12 Assessments / 17 Tests** across shellcommand, cmdlet, cmdlet
Variables and WMI57. Each passes current schema/capability validation, YAML/JSON
typed compilation, native packaging and an independent package/operand consumer.
Their retained reverse readers receive a private explicit-count source view only
after current-schema validation; it is never authoring or compiler input.
The Set/Filter proof retains seven original Set Objects, all three operators,
depth-three nesting, default exclusion, pre-operator filtering and loss/reversal
negatives, using canonical field/expected-value counts. Its Item fixtures remain
synthetic, not scanner or full-Definition proof. Existing cumulative-ledger
replays and their negative checks are retained, not counted as new Server 2025
or 883-Assessment equivalence coverage.

**Additional compiler defect exposed:** WMI57's record-field map produced an
insertion-order-dependent derived field index. Canonical JSON sorts map keys;
decoding the compiler's serialized output therefore rejected its own index.
Sorting field-map keys when indexing fixes this; source operands, record
boundaries and Boolean operand-array order are unchanged. The regression uses
the original WMI57 record and still rejects a forged index. Deprecated scalar
`wmi_object`/`wmi_test` remain errors, with separate negative coverage; they are
never translated into WMI57.

Focused evidence: **seven new tests** and **31 related schema/converter/contract
tests pass**. Historical Bluetooth CLI and hosted reproduction pass separately.
All approved normative schemas remain unchanged. No original input, release
asset, source normalization or production converter behavior is changed.

**Generator-trigger preflight:** ten other active source workflows have older red
runs (nine additional source checks plus an immutable 4,001-YAML archive gate).
These were not triggered by RESULT_SHA; they are not relabeled green or newly
introduced failures. Their recorded run IDs/hashes remain in the machine packet.
Reconcile these obligations before widening the generator change. Its full
100-capability schema fingerprints have been captured, but generator decoupling
has not started. No globally all-green prerequisite is claimed from only the
triggered subset. The committed original XML fixtures retain their original
whitespace as well as their exact SHA-256 values.

Reproduce with the commands in the [fixture guide](../../tests/fixtures/v04-current-source-proofs/README.md).
[`v04_source_proof_contract.py`](../../tools/v04_source_proof_contract.py) documents
the current/proof-view boundary and synthetic compiler wrapper;
[`prove_v04_current_bluetooth_source.py`](../../tools/prove_v04_current_bluetooth_source.py)
documents source binding and independent comparison. These helpers are proof
infrastructure, not another production conversion path. Scanner equivalence,
publisher trust and release readiness remain unproved.
