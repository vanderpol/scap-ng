# Direct cmdlet input/result proof — 2026-10-26

Continued under [#251](https://github.com/vanderpol/scap-ng/issues/251#issuecomment-6401652271)
after the [command-error checkpoint](v04-direct-command-behaviors.md). No approved
schema, production converter/compiler, source fixture or release gate changed.

| Field | Verified result |
| --- | --- |
| BASE_SHA | `600fa14cb` |
| RESULT_SHA | `c117b06c8f0ec0a398b8c14d7751379c5cd7f067` |
| IMPLEMENTED | Approved nullable cmdlet inputs, structured invocation records and independent whole-closure proof |
| SOURCE_PROVED / COMPILED_UNPROVED / BLOCKED | **245 / 0 / 46** of 291 original Rules |
| CANDIDATES | All **seven** actual cmdlet closures prove and compile; two complete mixed WMI dependencies |
| AUTHORING | 245 Assessments / 349 Tests; 221 inline Test Objects, 43 references to 17 genuinely shared Objects, 85 no-Object Tests, 127 compact Registry sites; deprecated grammar zero |
| TESTS / CI | **3,066** mandatory tests; zero failures/errors, one existing skip; 71 related tests; all five exact implementation-head checks PASS |
| NEXT | Bounded remaining approved-capability/comparator audit; preserve source-invalid and explicitly deprecated boundaries |

**Canonical acquisition.** The small `v04_direct_cmdlet_inputs` helper implements
the existing reviewed contract: nullable module constraints and invocation/select
records preserve `xsi:nil` as null, distinct from an empty string. Named collector
fields carry explicit `selection_match`; expected-value `value_match` remains
independent, including original all/every defaults. Numeric-looking strings such
as Select-Object first `"100"` stay strings. Result predicates retain complete
record boundaries and structured Test requirements. No cmdlet is executed.

The capability-specific Object `select` is an approved input-record parameter,
not a generic selector wrapper. The unchanged canonical Object validator already
handles this distinction. Authoring statistics and the overly broad style
assertion now agree with it. A legacy wrapper shape still fails schema validation
and counts as obsolete; no validator or language gate is weakened.

The independent reader separately interprets original module, nil, scalar,
input-record, selection and result terms without importing the new helper.
Five focused tests cover all seven actual closures, schema/compile/YAML parity;
null identity; independent field-selection/value matching; malformed nils,
record types/operators, duplicate/invalid names and wildcards; and native
type/selection/result mutations. Controlled derivatives add no original coverage.
Unsupported masks, parent record Variables, non-equality scalar inputs and
unproved dynamic enum membership fail closed.

WMI coverage advances from 18 to **20 of 26**; six still need unsupported legacy
behavior or unapproved `all_exist`. The original WMI suite retains its 18/8
restricted-catalog boundary. The cmdlet and full-benchmark suites prove the new
complete closures rather than substituting partial Assessments.

Public gates validate **492 JSON / 492 YAML documents**, compile 245 programs and
pass the separate package consumer. All **238** previous program hashes are
unchanged. The [machine packet](v04-direct-cmdlet.json) records every admitted
source Rule/Definition/dependency, proof/program hash, command and blocker.
ZIP/XML SHA-256 remain
`2f46264b5fa21c8a033236121794ebe372314bf7458dac0aca4f81179fe7ece0` /
`52b7918ea577095cb1c130589e5061c52ef4b12370ebb4ce84d2dfba68757440`.

The [two actual YAML/JSON examples](../examples/direct-cmdlet/README.md) are pinned
in `8967d7d8c`. Hosted [rebaseline](https://github.com/vanderpol/scap-ng/actions/runs/40342188301),
[current regression](https://github.com/vanderpol/scap-ng/actions/runs/40342188714) and
[canonical checks](https://github.com/vanderpol/scap-ng/actions/runs/40342188487) pass;
the packet links the passing documentation and issue-reference checks.

Run `PYTHONPATH=tools python tools/test_v04_direct_cmdlet.py -v`; the
[developer guide](../developer/DIRECT-V04-CONVERTER.md) explains the parameter
contract and extensions. No scanner/PowerShell execution, signing/trust,
six-STIG rebaseline, source normalization or release readiness is claimed.

The earlier issue-comment attempt returned exactly
`Post "https://api.github.com/graphql": Forbidden`; no repeated retry was made.
This committed report and the engineering ledger are the handoff.
