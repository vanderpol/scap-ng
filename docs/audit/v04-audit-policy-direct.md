| Field | Verified result |
| --- | --- |
| BASE_SHA / RESULT_SHA | `02b50ec57a45ab6bb2496a597b25ae5d29da7eeb` / `ad6df4f71a6b679006fd174e9f225a9492802f7b` |
| IMPLEMENTED | Approved singleton-system acquisition and independently verified audit-policy capability |
| SOURCE_PROVED | 87 → **130** of 291 original Rules |
| COMPILED_UNPROVED / BLOCKED | **0 / 161** |
| REGRESSIONS / TESTS | Zero; **3,012 tests, zero failures/errors, one unchanged skip** |
| CI | All five implementation-head checks PASS |
| PERF | 262-document validation 11.532 s; cProfile 32.178 s; no optimization/speedup claim |
| NEXT | Closed-domain Registry selector proof; SID and WMI censuses; no production promotion |

# Autonomous checkpoint: original audit-policy conversion

Executed after the [architecture milestone](v04-architecture-acceptance.md) under
[owner engineering authority](https://github.com/vanderpol/scap-ng/issues/251#issuecomment-6401652271),
without an intermediate approval checkpoint. The original ZIP remains SHA-256
`2f46264b5fa21c8a033236121794ebe372314bf7458dac0aca4f81179fe7ece0`.

**Source/contract.** All 43 newly admitted Rules are selected by complete closure,
not IDs. Their original 86 Definitions, 63 Tests and 75 States reference two empty
audit-policy Objects and no Variables or other capability families. OVAL describes
this acquisition as the current system as a whole. The approved version-local
mapping says `test_source.kind: none` and explicitly prohibits a meaningless
native singleton Object. The converter now applies that generic source-kind
contract: native Tests omit `object`; original IDs/versions/hashes remain in
external dependencies. Source acquisition children and Variable Object extraction
remain unsupported, not approximated.

**Independent proof.** All 43 original closures compare PROVED against exact
native/compiled operands. The independent reader derives allowed fields,
values and deprecated-field boundaries from the original Windows OVAL XSD,
not the converter mapping. AUDIT_SUCCESS, AUDIT_FAILURE and
AUDIT_SUCCESS_FAILURE remain their original strings; no bit-splitting or new
interpretation is introduced. Source enum/type/deprecated-field and acquisition
mutants fail, as do changed native operands and invented singleton Objects.
No additional capability is enabled by inference from this success.

**Whole-source result.** 130 converted/source-proved + 161 blocked = 291.
All admitted content passes the maintained public CLI/paired compiler/separate
consumer regression, with **262 JSON and 262 YAML documents** and exact operands
for **130 programs**. This remains a labeled automated subset, not complete
Benchmark/policy/platform/manual equivalence, scanner parity, a corpus rebaseline
or production replacement. The packaged 883-Assessment ledger is unchanged.
The [machine packet](v04-audit-policy-direct.json) records every new original
proof, source/program hashes, all proof outcomes, remaining blockers and profiling.

**Performance/maintenance.** Validation remains dominated by schema branching.
The candidate workload is larger than the 170-document baseline and process
resources were warmed by admission/compilation; these timings are not a matched
optimization experiment. All strict checks remain; no schema or public validation
shortcut was introduced. Generic public structural schemas/generated capability
contracts do not certify every enumeration/cross-field semantic constraint for
arbitrary authored content; freeze-gate hardening remains required. This milestone
checks original source constraints in both producer and independent reader and
makes no broader release claim. The [developer guide](../developer/DIRECT-V04-CONVERTER.md)
contains the source-kind contract, supported bounds and runnable tests.

**Reproduce.** `python tools/test_v04_direct_audit_policy.py -v`, then the existing
maintained regression command with pinned Self-Assertion bindings. Public
`--all-rules` and the independent audit CLI regenerate the whole-source evidence;
profile emitted JSON with `tools/profile_v04_direct_validation.py`. No original
source, normative schema, production compiler/converter or release gate changed.

**Next ranked work.** The remaining Registry enum blockers include 19 original
case-insensitive hive selectors. A generic increment needs a proof over the
closed original hive domain and canonical native enum, including error evidence;
operator erasure without that proof is prohibited. Next are userright (39) and
WMI query (26), both requiring source censuses before implementation. These are
overlapping upper bounds, not promised conversion gains. GO for bounded engineering
under existing contracts; NO-GO for production promotion. Genuine semantic or
scope conflicts still go to Jack; routine checkpoints do not.

Exact implementation CI: [rebaseline](https://github.com/vanderpol/scap-ng/actions/runs/40226189895),
[canonical](https://github.com/vanderpol/scap-ng/actions/runs/40226190115),
[current regression](https://github.com/vanderpol/scap-ng/actions/runs/40226189894),
[documentation](https://github.com/vanderpol/scap-ng/actions/runs/40226190132),
[issue reference](https://github.com/vanderpol/scap-ng/actions/runs/40226189932).
All passed on `ad6df4f71a6b679006fd174e9f225a9492802f7b`; report-only publication
checks are separate. The committed packet is the authorized fallback if issue
commenting remains Forbidden.
