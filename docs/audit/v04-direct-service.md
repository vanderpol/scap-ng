# Direct Windows service proof — 2026-10-26

Continued under [#251 engineering ownership](https://github.com/vanderpol/scap-ng/issues/251#issuecomment-6401652271)
after the [policy checkpoint](v04-direct-system-policy.md). No approved schema,
production converter/compiler, original source fixture or release gate changed.

| Field | Verified result |
| --- | --- |
| BASE_SHA | `740bc8039470a824197da25ceee0a694439d3879` |
| RESULT_SHA | `fefbcc3a9c3e88e47d940615a175fe9e07b913d1` |
| IMPLEMENTED | Generic Windows service capability admission and independent selector/enum proof |
| SOURCE_PROVED / COMPILED_UNPROVED / BLOCKED | **213 / 0 / 78** of 291 original Rules |
| CANDIDATES | Both actual service closures independently prove and compile; all 39 user-rights cases remain proved |
| AUTHORING | 213 Assessments / 288 Tests; 167 inline Test Objects, 36 references to 12 genuinely shared Objects, 85 no-Object Tests, 120 compact Registry Objects; deprecated grammar zero |
| TESTS / CI | 3,047 maintained tests, zero failures/errors, one existing skip; 52 related tests and 15 final focused tests pass; all five implementation-head hosted workflows PASS |
| NEXT | Source-backed text-file acquisition/behavior census; seven current candidate closures |

**Original source and implementation.** SV-278018r1180760 uses `bthserv` with
the default equality selector and `SERVICE_AUTO_START`; its original surrounding
Boolean logic remains intact. SV-285313r1211167 uses case-insensitive equality
for `sshd` and `SERVICE_RUNNING`. No case folding, enum renaming, Rule-specific
switch or guessed Windows service behavior was added. The producer enables the
versioned capability and reuses its existing generic recursive visitors.

The independent reader obtains field/type/enum boundaries from original Windows
OVAL XSD, not the producer's mapping. Its scalar-selector reader now covers both
service names and user-right selectors, retaining their different constraints.
Four focused regressions check both source closures, schema validation and exact
compiled operands; altered selector/State/quantifier mutants; invalid original
fields/enums; and a controlled relative-COMPLEMENT Set whose ordered include
Filter applies to each operand before the operator. Repeated source acquisition
identity remains shared. Controlled derivatives are not extra original coverage.

Public gates validate **428 JSON / 428 YAML documents**, compile 213 programs and
pass the separate package consumer. All **211** prior program hashes are unchanged.
The [machine packet](v04-direct-service.json) contains both complete original
bindings/proofs, every compiled program hash, remaining blockers, exact commands
and CI evidence. ZIP/XML source SHA-256 remain respectively
`2f46264b5fa21c8a033236121794ebe372314bf7458dac0aca4f81179fe7ece0` and
`52b7918ea577095cb1c130589e5061c52ef4b12370ebb4ce84d2dfba68757440`.

Reproduce with `PYTHONPATH=tools python tools/test_v04_direct_service.py -v`.
The [developer guide](../developer/DIRECT-V04-CONVERTER.md) documents generic
capability extensions and public converter/validator/compiler entry points.
[Pinned user-rights examples](../examples/direct-userright/README.md) and
[WMI record examples](../examples/direct-wmi/README.md) remain independently
reproducible at their manifest SHAs. No original-source coverage is inferred from
formatting alone. No scanner parity, full six-STIG coverage, signing/trust or
production-release readiness is claimed.

Issue commenting remains blocked by the earlier exact error
`Post "https://api.github.com/graphql": Forbidden`; it was not repeatedly retried.
This committed report and the engineering ledger are the handoff.

The final trace now names unsupported record constructs explicitly rather than
incorrectly listing all records as unsupported. This wording-only correction
followed the full local suite; final focused tests pass and all 428 authoring
documents plus 213 independent source proofs remain unchanged. Exact-head hosted
CI validates the final implementation.

Exact implementation CI: [Markdown navigation and duplication audit](https://github.com/vanderpol/scap-ng/actions/runs/40305069160), [Commit issue reference](https://github.com/vanderpol/scap-ng/actions/runs/40305069393), [0.4.0 canonical authoring fast checks](https://github.com/vanderpol/scap-ng/actions/runs/40305069375), [Current-design regression contracts](https://github.com/vanderpol/scap-ng/actions/runs/40305069416), [Rebaseline smoke regression](https://github.com/vanderpol/scap-ng/actions/runs/40305069415).
