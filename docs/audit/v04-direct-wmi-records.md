# Direct WMI record integration — 2026-10-26

Continued autonomously after the [user-rights checkpoint](v04-direct-userright.md)
under [#251](https://github.com/vanderpol/scap-ng/issues/251). No approved schema,
production converter/compiler, release gate or original source bytes changed.

| Field | Verified result |
| --- | --- |
| BASE_SHA | `f9e3b0978e4b04935f49c530f2f82ff13438386d` |
| RESULT_SHA | `4087e43092e3821eba939adf58af3b6c92fe0985` |
| IMPLEMENTED | Generic record predicates and source-grounded titles for genuinely shared parameter acquisitions |
| SOURCE_PROVED / COMPILED_UNPROVED / BLOCKED | **201 / 0 / 90** of 291 original Rules |
| WMI | **18** complete closures proved; **8** remain blocked |
| USER-RIGHTS | **All 39** original candidate closures proved, including five mixed WMI dependencies |
| AUTHORING | 201 Assessments / 272 Tests; 165 inline Test Objects, 36 references to 12 genuinely shared Objects, 71 no-Object Tests, 120 compact Registry Objects; deprecated grammar zero |
| TESTS / CI | **3,037 tests**, zero failures/errors, one unchanged skip; 38 related tests pass; all five implementation-head hosted workflows PASS |
| NEXT | Source-backed password/lockout-policy capability census and proof |

**Source semantics.** The new small `record_predicate` visitor uses the approved
`record: {records_found, records_matching, fields}` grammar. It evaluates named
field requirements inside the same record before record and Item aggregation.
Original names and literal datatypes remain exact: numeric-looking source strings
such as `"2"` stay strings; explicitly typed integers remain integers. WMI
namespace/query parameters retain original values. The independent source/native
reader already supported record terms and is reused as an external gate; no old
conversion path or intermediate representation was added.

Required-member lookup remains error-producing according to original
`EntityStateFieldType` and the existing approved native record contract. Field
value cardinality does not turn a missing record member into empty successful
evidence. Controlled regression mutants split two fields across existential
records while retaining the original Test cardinalities; independent proof
rejects that boundary change. Original record comparators other than equality,
duplicate/invalid source field names, unsupported record absence, record-level
Variables and masking fail closed. These are bounded supported constructs, not
claims of arbitrary record or scanner conformance.

**Authoring integration.** Four mixed user-rights Rules first remained blocked
because their multiply used WMI Objects lacked comments and meaningful titles.
The generic title function now describes collection-parameter facts as well as
selectors: the original namespace and WQL identify the actual acquisition.
This supplies meaningful stable shared references without manufacturing purpose,
forcing private titles or changing the Assessment-local sharing policy.

**Evidence and limits.** All 18 newly supported original WMI closures independently
compare and compile. Five are also user-rights candidates; capability counts
overlap and are never added as separate Rules. The remaining eight WMI closures
need unsupported `windows.user`/`windows.cmdlet` behavior or unapproved
`all_exist` semantics. They remain complete explicit blockers. No partial
Assessment is substituted for a blocked dependency graph.

Run `PYTHONPATH=tools python tools/test_v04_direct_wmi.py -v` for the five focused
tests, including original-source positives, string/integer distinctions,
multi-field correlation, missing-member/error reference cases and invalid-source
mutants. The [developer guide](../developer/DIRECT-V04-CONVERTER.md) documents
the public entry points, exact source pin and record extension contracts.
The [machine packet](v04-direct-wmi-records.json) records every admitted source
Rule/Definition/dependency, compiled hash, validation result and remaining blocker.
No scanner parity, full six-STIG coverage, signing/trust or release readiness is
claimed. No source repair or additional `all_exist` normalization was applied.

Public paired gates validate **404 JSON and 404 YAML documents**, compile 201 programs and pass the independent package consumer. All **183** prior program hashes are unchanged. [Actual pinned WMI YAML/JSON examples](../examples/direct-wmi/README.md) show record requirements and legitimate shared acquisition.

Issue commenting remains blocked: the previous attempt returned `Post "https://api.github.com/graphql": Forbidden`; no repeated retry was made. This report is the fallback.

Exact implementation CI: [Markdown navigation and duplication audit](https://github.com/vanderpol/scap-ng/actions/runs/40300995943), [0.4.0 canonical authoring fast checks](https://github.com/vanderpol/scap-ng/actions/runs/40300995897), [Current-design regression contracts](https://github.com/vanderpol/scap-ng/actions/runs/40300995948), [Commit issue reference](https://github.com/vanderpol/scap-ng/actions/runs/40300996049), [Rebaseline smoke regression](https://github.com/vanderpol/scap-ng/actions/runs/40300996137).
