# OVAL 5.12.3 Self-Assertion Conformance Findings

**Iteration:** 001  
**Status:** Active language-conformance findings  
**Evidence role:** OVAL language conformance / evaluator semantics, not production STIG migration evidence  
**Pinned source:** `OVAL-Community/SCAP-Self-Assertion` revision `e3538595c5083b9c34d937a81d319234df9bbfaa`  
**Path:** `SCAP_1.4/OVAL_Test_Content`

## Why this corpus is separate

The OVAL Community Self-Assertion content is educational/unit-test content intended to exercise OVAL Definition Evaluator behavior. It complements but does not replace the pinned NIWC published STIG corpus.

- Self-Assertion answers: **does the importer/evaluator understand this OVAL language feature?**
- NIWC published content answers: **can SCAP-NG faithfully migrate real production STIG content?**

Do not combine the two evidence roles into one coverage percentage.

## Finding 1 — complete structural import of the current Self-Assertion OVAL corpus

The pinned corpus currently contains 144 OVAL XML documents across 12 platform groups:

| Group | Documents |
|---|---:|
| agnostic | 35 |
| AIX | 2 |
| ASA | 2 |
| IOS | 11 |
| IOS XE | 11 |
| JunOS | 2 |
| Linux | 16 |
| macOS | 20 |
| PanOS | 2 |
| Solaris | 6 |
| Unix | 12 |
| Windows | 25 |
| **Total** | **144** |

All 144 documents parse successfully through the SCAP-NG OVAL semantic importer with:

- zero parse failures;
- zero unresolved OVAL references;
- namespace-qualified test/object/state identities retained;
- platform-specific payloads preserved in the semantic tree.

This proves structural/reference closure for this corpus. It does **not** prove native execution support for every platform collector.

## Finding 2 — the agnostic corpus is largely executable offline

The 35 platform-agnostic documents contain 195 variables.

- 194 resolve exactly without a target system;
- one remains explicitly `runtime_time_dependency` because its `time_difference` semantics depend on the evaluator's current time.

The offline verifier executes 308 tests:

- 224 evaluate true;
- 83 evaluate false;
- one evaluates unknown;
- one additional current-time-dependent test is deliberately skipped.

At definition level:

- 44 definitions match their documented expected result;
- one definition requires current-time context;
- one `family_test` definition requires real platform collection;
- zero fully evaluated definitions disagree with the expected result.

The offline cases exercise criteria nesting, negation, `extend_definition`, variable tests, existence semantics, check semantics, datatypes, and the OVAL variable/function model.

## Finding 3 — target-independent ComponentGroup/function coverage is now broad

The agnostic corpus exercises the OVAL 5.12.3 ComponentGroup/function surface including:

- `object_component`
- `variable_component`
- `literal_component`
- `arithmetic`
- `begin`
- `concat`
- `end`
- `escape_regex`
- `glob_to_regex`
- `merge`
- `regex_capture`
- `split`
- `substring`
- `time_difference`

Synthetic `variable_object` content allows many `object_component` cases to be evaluated without a host. Real platform-backed `object_component` dependencies remain explicit rather than being guessed.

Across the complete 144-file corpus, only eight variables remain `dynamic_object_dependency`. They occur where real collection is actually required, including SELinux booleans, platform environment variables, macOS keychain data, and Solaris package data.

## Finding 4 — real recursive set/filter content matches the parser model

Dedicated Unix and Windows Self-Assertion set documents exercise:

- `UNION`
- `INTERSECTION`
- relative `COMPLEMENT`
- default `set_operator="UNION"`
- filters whose omitted `action` defaults to `exclude`
- filters nested inside multi-level recursive sets.

A regression parses both documents and verifies:

- the Unix and Windows set/filter structures are semantically equivalent;
- default filter action is `exclude`;
- filter state references are present in the dependency graph;
- recursive nesting reaches four set levels in the deepest test case.

The OVAL 5.12.3 rule that filters apply to referenced object items before the enclosing set operator is retained explicitly in the IR.

Set collection flag propagation (`complete`, `incomplete`, `error`, `does_not_exist`, `not_collected`, `not_applicable`) is separately modeled with the OVAL operator-specific combination tables.

## Finding 5 — Self-Assertion does not cover the entire schema surface

The vendored OVAL 5.12.3 schema catalog defines:

- 259 test types;
- 258 object types;
- 257 state types.

The current Self-Assertion corpus exercises:

- 100 qualified test types;
- 100 qualified object types;
- 75 qualified state types.

Every observed qualified type is declared by the vendored OVAL 5.12.3 schemas.

Therefore the current unexercised schema surface is:

- 159 test types;
- 158 object types;
- 182 state types.

These unexercised entries are an explicit coverage backlog. They are **not** assumed to be semantically validated merely because the generic importer can preserve them.

## Finding 6 — the current production-only gap is legacy Windows OVAL

The combined schema/conformance/production ledger found only one production-only test type in the four priority STIG benchmarks: Windows `user_test`. Its `user_object` and `user_state` are likewise production-only, and one production rule uses the older `wmi_object`.

OVAL 5.12.3 documentation marks these constructs deprecated:

- `user_test`, `user_object`, and `user_state` were deprecated as of OVAL 5.11 and replaced by the SID-based `user_sid55_*` family because trustee names are not unique.
- `wmi_object` was deprecated as of OVAL 5.7 and replaced by `wmi57_object`, which supports multiple selected fields through record semantics.

Both successor families are exercised by the Self-Assertion corpus.

**Implication:** these production-only gaps are **source-remediation blockers, not SCAP-NG runtime requirements**. SCAP-NG intentionally contains no deprecated OVAL tests. A converter must report the affected definition as `unsupported: deprecated_oval_test` and require the publisher to replace the deprecated test in SCAP 1.4 before conversion. No automatic rewrite or `legacy_compatible` path is allowed.

This also explains why the pinned Self-Assertion corpus is especially useful for defining SCAP-NG's supported OVAL surface: its current OVAL test content does not exercise deprecated test families.

## Current confidence boundary

The current evidence supports the following claims:

1. The importer can structurally ingest every OVAL document in the pinned Self-Assertion corpus and preserve complete OVAL reference closure.
2. Core OVAL Boolean/result algebra, variables/functions, checks, existence semantics, and synthetic variable tests have strong offline conformance evidence.
3. Recursive set/filter syntax and semantics are explicitly modeled and match the dedicated Unix/Windows Self-Assertion structures.
4. Platform-specific test/object/state payloads are losslessly represented.

The current evidence does **not** yet support the claim that SCAP-NG can natively execute every OVAL 5.12.3 platform collector. Schema-only types and platform collection behavior remain explicit work items.

## Next work

Use the generated combined OVAL evidence ledger to classify each schema-defined test/object/state type as:

- conformance and production;
- conformance only;
- production only;
- schema only.

Prioritize:

1. production-only types because real STIG content depends on them without focused Self-Assertion coverage;
2. core/shared semantics that appear in multiple platforms;
3. schema-only types relevant to likely SCAP-NG target platforms;
4. lower-priority/deprecated platform types after the main migration gate is stable.

Keep native collector implementation separate from faithful structural import so lack of a collector can never cause content to be silently discarded or reinterpreted.
