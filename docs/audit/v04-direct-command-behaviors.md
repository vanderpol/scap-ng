# Direct command collection-error proof — 2026-10-26

Continued under [#251](https://github.com/vanderpol/scap-ng/issues/251#issuecomment-6401652271)
after the [file-rights checkpoint](v04-direct-file-rights.md). No approved schema,
production converter/compiler, source fixture or release gate changed.

| Field | Verified result |
| --- | --- |
| BASE_SHA | `083ec0e3e6b9acf27b2d706b5b9d39ac596971af` |
| RESULT_SHA | `fab566b2a12f8b5e844f11e3c0e5be524fa6e89c` |
| IMPLEMENTED | Exact source command collection-error controls through the common Object visitor |
| SOURCE_PROVED / COMPILED_UNPROVED / BLOCKED | **238 / 0 / 53** of 291 original Rules |
| CANDIDATES | All **ten** original behavior-bearing closures independently prove and compile |
| AUTHORING | 238 Assessments / 335 Tests; 211 inline Test Objects, 39 references to 15 genuinely shared Objects, 85 no-Object Tests, 127 compact Registry sites; deprecated grammar zero |
| TESTS / CI | **3,061** maintained tests, zero failures/errors, one existing skip; **66** related tests pass; all five implementation-head hosted workflows PASS |
| NEXT | Original-source cmdlet nullable/input-record support; seven candidate closures |

**Source semantics.** Both approved Boolean parameters default false in original
`ShellCommandBehaviors`: `error_if_exit_status_not_0` and
`error_if_stderr_exists`. Explicit true requests collection-error evidence;
it is not an ordinary failed matching condition. The small new helper preserves
each acquisition's flags, scripts, interpreter and pattern. One actual closure
also uses a separate default-behavior command; its false flags stay false.
Unknown, duplicate, foreign or nonempty behavior nodes and invalid Boolean
lexical values fail closed. No command is executed by conversion or these tests.

The independent reader separately interprets original attributes/defaults without
importing the helper or modifying original XML. Four focused tests cover all ten
actual closures, source optional/default declarations, all four flag combinations,
changed/deleted flags, incorrect replacement with a matching predicate, existing
error/incomplete/not-collected evidence guards, and invalid-source mutants.

**Historical proof reconciliation.** Fixed packaged case `windows-14`,
SV-278146, previously expected unverifiable because command behaviors were not
read. It now proves. Its immutable fixture, original source, manifest and compiled
program hashes remain unchanged. The regression still asserts the historical
reader is unverifiable, verifies the new proof, and rejects a native false-flag
mutation as a mismatch. This is stronger evidence, not a removed negative test.
The packaged 883-Assessment ledger is not broadened or silently rebaselined.

Public gates validate **478 JSON / 478 YAML documents**, compile 238 programs and
pass the separate package consumer. All **228** previous program hashes are
unchanged. The [machine packet](v04-direct-command-behaviors.json) records original
bindings, dependency/proof/program hashes, commands, remaining blockers and CI.
ZIP/XML SHA-256 remain
`2f46264b5fa21c8a033236121794ebe372314bf7458dac0aca4f81179fe7ece0` /
`52b7918ea577095cb1c130589e5061c52ef4b12370ebb4ce84d2dfba68757440`.

[Actual command YAML/JSON examples](../examples/direct-command-behaviors/README.md)
are pinned in `b9e6a7af3`, including an actual true-error-flag Assessment selected
by emitted structure. Regenerate from the manifest SHA with
`PYTHONPATH=tools python tools/v04_direct_authoring_examples.py --capability independent.shellcommand --output /tmp/direct-command-examples`.
Run `PYTHONPATH=tools python tools/test_v04_direct_command_behaviors.py -v`;
see the [developer guide](../developer/DIRECT-V04-CONVERTER.md). No scanner parity,
regex-engine conformance, signing/trust, six-STIG rebaseline, source-specific
normalization or release readiness is claimed.

The earlier issue-comment attempt returned exactly
`Post "https://api.github.com/graphql": Forbidden`; no repeated retry was made.
This committed report and the engineering ledger are the handoff.

Exact implementation CI: [Commit issue reference](https://github.com/vanderpol/scap-ng/actions/runs/40317820633), [Markdown navigation and duplication audit](https://github.com/vanderpol/scap-ng/actions/runs/40317820568), [0.4.0 canonical authoring fast checks](https://github.com/vanderpol/scap-ng/actions/runs/40317820675), [Current-design regression contracts](https://github.com/vanderpol/scap-ng/actions/runs/40317820565), [Rebaseline smoke regression](https://github.com/vanderpol/scap-ng/actions/runs/40317820791).
