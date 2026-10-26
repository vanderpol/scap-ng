# Direct Windows primitive closure checkpoint — 2026-10-26

Continued under [#251](https://github.com/vanderpol/scap-ng/issues/251#issuecomment-6401652271)
after the [cmdlet checkpoint](v04-direct-cmdlet.md). The latest
[coordination review](https://github.com/vanderpol/scap-ng/issues/251#issuecomment-6419525046)
was read before publication; the nil-record correction below is a subsequent finding. Only the isolated direct
converter, independent evidence reader, tests and documentation change. The
approved schema, production converter/compiler and mandatory gates are unchanged.

| Field | Verified result |
| --- | --- |
| BASE_SHA | `71a3af528` (current main; compare implementation `c117b06c8`) |
| RESULT_SHA | `c721ed0f6f8ce5fd66bc890f015afd5bb7ff08f2` |
| SCHEMA_VERSION | 0.4.0; approved schema tree unchanged |
| SOURCE_PROVED / COMPILED_UNPROVED / BLOCKED | **249 / 0 / 42** of 291 original Windows Server 2025 Rules |
| NEW CASES | SV-278027, SV-278028, SV-278197, SV-278198, SV-278240; complete original dependency closures |
| AUTHORING | 249 Assessments / 357 Tests; **229 inline**, **43 shared references / 17 genuinely shared Objects**, **85 no-Object**, **128 compact Registry** sites; deprecated grammar zero |
| TESTS / CI | **3,074** mandatory tests; zero failures/errors, one existing skip; 79 related tests PASS. All five exact `c721ed0f6` implementation workflows PASS. |
| REGRESSIONS | 244 retained programs unchanged; one malformed-source admission withdrawn |
| NEXT_ENGINEERING_OBJECTIVE | Resolve documented source/policy boundaries before admitting the affected Rules; retain fail-closed behavior |

**Source preservation.** Generic case-insensitive inequality preserves original
Administrator/Guest strings and field cardinalities. NTUSER retains original
optional defaults (`include_default=false`, `item_creation=key_and_name_exist`),
registry type mapping and ordered enabled/age exclusions. IIS `"false"` remains a
string. Environment `pid: null` preserves original `xsi:nil` current-process
selection, distinct from PID zero. Complete one-value string constants become
typed scalar function operands; multi-value products and cross-datatype folding
remain unsupported. Shell acquisition Filters stay before the original Variable
collection boundary. No Rule-ID switches or new semantic normalization apply.

The independent reader separately constructs source and native terms. Seven
focused tests cover all five actual closures, YAML/JSON equality, schema and
compiled operands; mutations of comparator, null PID, defaults, type, Filter and
function order fail proof. Multi-value function inputs fail closed. Public gates
validate **500 JSON / 500 YAML documents**, compile **249** programs and pass the
separate package consumer. The [machine packet](v04-direct-remaining-primitives.json)
records source IDs, dependency graphs, exact terms, program hashes and commands.
ZIP/XML SHA-256 remain
`2f46264b5fa21c8a033236121794ebe372314bf7458dac0aca4f81179fe7ece0` /
`52b7918ea577095cb1c130589e5061c52ef4b12370ebb4ce84d2dfba68757440`.

**Remaining frontier: 42 unique blocked Rules.** An independent original-XCCDF
ZIP/XML census shows that thirty have **only OCIL** (default and manual), with no
OVAL check to convert; eight need unapproved original
Test-level `all_exist`; one uses unmapped legacy `user_test`; SV-278143 uses
explicitly deprecated scalar WMI plus unsupported functions; SV-278008 has an
original-source defect. SV-278031 has an omitted nil-record datatype. Categories
are disjoint here; capability/message counts
can overlap and must not be added as Rule counts. Thus **249/261 OVAL-bearing Rules
(95.40%)** prove, while **249/291 total Rules (85.57%)** prove. The twelve remaining
OVAL-bearing Rules retain their actual blockers; manual-only Rules are not invented
as automated Assessments. The packet records all thirty original check/reference
sets independently of the producer inventory.

**Correction to the preceding checkpoint.** SV-278031's original cmdlet parameters
are `xsi:nil="true"` without `datatype="record"`. Original Windows Schematron
unconditionally requires that datatype, even at this nil site. Both readers had
accepted its omission; they now reject it and missing required version types.
This withdraws one previously admitted Rule, rather than claiming a normalization.
The [original XML/assertion packet](v04-source-invalid-cmdlet-nil.json) preserves the
counterexample. A controlled explicitly typed derivative proves and compiles but
adds no original coverage. Historical examples/reports are preserved and marked
superseded. Restoring this Rule needs corrected pinned source or explicit owner
approval; no source fixture is modified. Six other actual cmdlet closures, both
mixed WMI dependencies and all 39 user-rights closures remain proved.

For SV-278008, original Objects `27800801` and `27800802` combine
`path operation="pattern match"` with `max_depth="-1"` and
`recurse_direction="down"`. Both original OVAL 5.12.3 path-context Schematron
assertions fail. The [minimal source packet](v04-source-invalid-file-recursion.json)
preserves XML, original IDs, source/schema hashes and executed assertions; a
regression keeps this Rule blocked. Choosing different acquisition semantics,
dropping recursion, or normalizing this source needs explicit owner approval.
No such repair is implemented. Legacy name-based user acquisition is not silently
replaced by SID-based acquisition, nor scalar WMI by record WMI.

The [sample navigation page](../examples/README.md) links actual generated YAML/JSON,
published in `a5743a96a`, including the new [NTUSER](../examples/direct-ntuser/README.md) and
[IIS configuration](../examples/direct-iis/README.md) cases. The publisher's capability
flag selects consuming Tests, so the appcmd acquisition used only through a Variable
is covered by source/compiled evidence rather than that sample-selection flag.

Hosted [rebaseline smoke](https://github.com/vanderpol/scap-ng/actions/runs/40350495821),
[current contracts](https://github.com/vanderpol/scap-ng/actions/runs/40350495813),
[canonical checks](https://github.com/vanderpol/scap-ng/actions/runs/40350495939),
[documentation](https://github.com/vanderpol/scap-ng/actions/runs/40350496126) and
[issue references](https://github.com/vanderpol/scap-ng/actions/runs/40350495842)
all pass on the implementation SHA. Local exact test counts and hosted success
are separate evidence; report/example-only heads do not imply another full CI run.
Markdown audit retains three known current Board links and 39 historical broken
links, with no new broken links from these changes.

Authoring remains local by default, with compact Registry presentation, genuine
sharing, structured requirements and current Boolean grammar. The guide and
focused tests support human reproduction and extension. The architecture can
support further bounded increments; source-invalid admission remains an owner
review gate, not a reason to change the language or force coverage.

Run `PYTHONPATH=tools python tools/test_v04_direct_remaining_primitives.py -v`.
The [developer guide](../developer/DIRECT-V04-CONVERTER.md) documents extension and
regeneration. This is source/compiled-operand verification, not scanner execution,
signing/trust acceptance, six-STIG rebaseline or production-release readiness.
The prior issue-comment error was exactly
`Post "https://api.github.com/graphql": Forbidden`; it was not repeatedly retried.
The committed report and ledger provide the authorized handoff.
