# 0.4-C — Authored observation inside Apache derived value: source graph proof

**2026-10-19 · [#245](https://github.com/vanderpol/scap-ng/issues/245) · Research only. Not the accepted 0.4-C language; no OVAL runtime or scanner parity claim.**

## Decision

Use **observation** on the candidate human-facing C surface and keep **Object** only in the pinned A/OVAL execution intermediate representation. A derived value may read a field from a private observation or refer to a named reusable observation. This is more coherent with the existing unified C `observations` checks than exposing `object` in new C examples. This is a vocabulary and authoring-graph experiment, not authorization to rewrite the 0.3 normative syntax.

## Actual independently authored input

[Apache SV-214273 C sample](c-derived-apache-version.research.yaml) derives executable paths by observing a shell command, extracting a captured path, then combining that path with ` -V`. It visibly says `observation`, not `object`. Source Test titles, existing meaningful Variable IDs, full command, shell, collection regex, error flags, and multi-value sequence are preserved in the compiler's typed native-A graph.

[Authoring bridge](../../../tools/research_c_observation_values.py) compiles to [the source-independent derived-value compiler](../../../tools/research_c_derived_values_compiler.py); there is no new collector. [Apache tests](../../../tools/test_research_c_observation_values.py) validate the original two-Variable sample and full 19-Variable Apache SV-214268 shared/inline Object graph. The source-graph bridge never reads the original Assessment during compilation; source-backed tests independently compare against pinned source. Named shared observations retain their original Object IDs, fail on unused/duplicate/missing references, and carry separate SHA-256 source pins for **both** Variable definitions and shared Object definitions. A changed named collection cannot be silently accepted simply because Variables were unchanged.

## Real limits

- This bridge only handles a narrow, bounded set of derived string value operations and typed A acquisition descriptors; it **rejects** unknown C source shapes rather than guessing. The full source-compatible Set, Filter, foreach, records, and multi-state expression path is not provided by this module.
- The real 19-Variable Apache specimen contains **four private inline Objects and one named shared Object**. It compiles to **19 native source Variables**, not a claimed smaller executable graph. [Read-only grouping audit](../../../tools/research_c_variable_folding_safety.py) identified four pure single-consumer display-group candidates; it does not delete or optimize any source Variable, dynamic collection, or Test.
- Supplied offline command-Item fixtures verify `values`, `unknown`, `error`, `not_applicable` boundary handling in this bounded evaluation graph. They **do not** establish OVAL source scanner result parity, actual OS command execution, or OVAL's true collection order/regex dialect.
- **Verified CI:** [250 focused tests passed](https://github.com/vanderpol/scap-ng/actions/runs/39316587088) at commit `f51bde4a9b26e1b00ffb11f6dbf688c324553f14`. Earlier failed workflow iterations caught both a missing named shared-Object digest guard and invalid terminal-status evidence envelopes. Those failures were fixed, not bypassed.

## OVAL Self-Assertion source conversion: separate readiness gate

The project owner's review target is **actual original OVAL 5.12.3 Self-Assertion test content**, not Apache graph equivalence. The earlier *local, uncommitted* prototype reported **291/785 source Tests converted and 51/167 complete Definitions**, but only **18 complete standalone C YAML Assessments** were packaged for review; its complete generated corpus and converter have **not** been checked into this repository, so these numbers are historical **unreproduced research** rather than current GitHub-verified coverage. Do not claim they establish 0.4-C conversion of Self-Assertion.

For an actual handoff, preserve and publish on GitHub.com: the exact pinned source `OVAL-Community/SCAP-Self-Assertion@e3538595c5083b9c34d937a81d319234df9bbfaa`, tested converter source, source-to-Test/Definition crosswalk, all generated C Assessments, explicit omissions with reasons, source-native Test comments/titles/descriptions, capability and OVAL datatype scope, output checksums, independent lossless source/evaluator checks including empty/error/unknown/not-applicable and Set/Filter/Variable/record/foreach boundaries, and a reproducible source-pinned CI job. The existing [pinned offline source export workflow](../../../.github/workflows/research-c-self-assertion-fixtures.yml) is a source input mechanism only, not conversion evidence.

**Until those checks are passed, call 0.4-C Self-Assertion conversion incomplete; do not present the 18-example archive as finished.**
