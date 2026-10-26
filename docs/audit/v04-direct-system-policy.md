# Direct password/lockout policy proof — 2026-10-26

Continued the [#251 engineering authorization](https://github.com/vanderpol/scap-ng/issues/251#issuecomment-6401652271)
after the [WMI record checkpoint](v04-direct-wmi-records.md). No approved schema,
production converter/compiler, source fixture or release gate changed.

| Field | Verified result |
| --- | --- |
| BASE_SHA | `e5bd741f905e38679710f1d6accfbf27cb689e38` |
| RESULT_SHA | `740bc8039470a824197da25ceee0a694439d3879` (corrected); initial implementation `88eaa0133` |
| IMPLEMENTED | Capability-driven password/lockout policy acquisition and required source datatypes |
| SOURCE_PROVED / COMPILED_UNPROVED / BLOCKED | **211 / 0 / 80** of 291 original Windows Server 2025 Rules |
| CANDIDATES | All **7 password-policy + 3 lockout-policy** original closures independently prove and compile |
| AUTHORING | 211 Assessments / 286 Tests; 165 inline Test Objects, 36 references to 12 genuinely shared Objects, 85 intentional no-Object Tests, 120 compact Registry Objects; deprecated grammar zero |
| TESTS / CI | 3,043 initial local tests, zero failures/errors, one existing skip; corrected focused tests 6/6; all five corrected-head hosted workflows PASS |
| NEXT | Original-source Windows service capability census and proof |

**Source contract.** Both approved capability mappings use `test_source.kind:
none`; original OVAL Objects explicitly describe the system as a whole. Native
Tests omit meaningless Objects while original IDs, versions, hashes and edges
remain in provenance. No singleton Variable acquisition, selector, Set or Filter
is invented. The existing generic dependency visitor handles both capabilities.

The small `v04_direct_system_policy` adapter preserves the original typed-entity
contracts: `EntityStateIntType` and `EntityStateBoolType` require explicit
`datatype` attributes fixed to `int` and `boolean`. Omissions fail closed; a fixed
required attribute is not an omission default. Original source bytes and hashes
remain untouched. Native literals and explicit datatypes remain exact.
Original embedded Schematron requires nonnegative literal `max_passwd_age`,
`force_logoff` and `lockout_duration`; invalid literals fail closed. Other range
constraints and unit conversions are not invented. Variable operands retain
their types and original `var_check`, including omitted **all** → **every**.

**Independent evidence.** The independent reader derives field names, types and
literal restrictions from original OVAL XSD, without importing the producer's
mapping or adapter. All ten actual source dependency closures compare against
native terms and exact compiled operands. Six focused tests additionally cover
controlled datatype-omission negatives and constant-Variable derivatives; these are not counted
as extra original Rules. Negative tests reject altered expected-value matching,
Item cardinality, AND/OR logic, invalid source fields/types/ranges, invented
acquisitions and dummy native Objects. Existing error/unknown evidence contracts
are preserved; no new evaluator or source-specific normalization was added.

Public paired gates validate **424 JSON / 424 YAML documents**, compile 211
programs and pass the independent package consumer. All **201** previous compiled
program hashes are unchanged. The [machine packet](v04-direct-system-policy.json)
records every new original Rule/Definition/dependency hash, proof, program hash,
remaining blocker, exact commands and CI evidence. Source ZIP SHA-256 remains
`2f46264b5fa21c8a033236121794ebe372314bf7458dac0aca4f81179fe7ece0`;
the XML SHA-256 remains
`52b7918ea577095cb1c130589e5061c52ef4b12370ebb4ce84d2dfba68757440`.

Reproduce with `PYTHONPATH=tools python tools/test_v04_direct_system_policy.py -v`;
the [developer guide](../developer/DIRECT-V04-CONVERTER.md) documents capability
extension, source pins and public conversion/validation/compilation commands.
Typed/comparator-bearing absence and constructs outside this bounded proof remain
blocked. No scanner parity, complete Benchmark policy equivalence, six-STIG
coverage, signing/trust or release readiness is claimed.

Issue commenting remains blocked: the earlier attempt returned
`Post "https://api.github.com/graphql": Forbidden`; no repeated retry was made.
The committed engineering report and ledger are the GitHub handoff.

Internal review corrected the initial policy implementation (`88eaa0133`), which
incorrectly accepted omitted typed attributes. Every actual pinned policy Rule
already has explicit valid datatypes; the ten original outputs and all prior
programs are unchanged. The corrected regression rejects omissions in both
producer and independent reader. No source normalization is authorized.

Corrected implementation CI: [Markdown navigation and duplication audit](https://github.com/vanderpol/scap-ng/actions/runs/40303409496), [Commit issue reference](https://github.com/vanderpol/scap-ng/actions/runs/40303409469), [Current-design regression contracts](https://github.com/vanderpol/scap-ng/actions/runs/40303409676), [0.4.0 canonical authoring fast checks](https://github.com/vanderpol/scap-ng/actions/runs/40303409618), [Rebaseline smoke regression](https://github.com/vanderpol/scap-ng/actions/runs/40303409578).
