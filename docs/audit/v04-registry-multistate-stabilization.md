# Registry multi-State stabilization — issue #251

This implements the already-approved structured `Test.require` grammar; it does
not change the schema or decide new result semantics. It is not scanner parity.

## Source and converter root cause

The pinned source fixture is
`research/assessment-simplification/evidence/ms_windows_11/SV-253254/source-oval.xml`.
Its adjacent provenance record identifies NIWC source revision
`8c8e5dff860af6b1290ee9273a282db24278f8d5` and original ZIP Git blob
`712cc3176b1e44616aaf2f3ba5e62b299ad0643c`. The extracted fixture SHA-256 is
`a056aafd7326bac213cab63da8c3746a49dfd5fc03f1812426bc8804e6e32926`.

- Definition: `oval:mil.disa.stig.defs:def:253254`.
- Test: `oval:mil.disa.stig.win:tst:25325400`.
- Object: `oval:mil.disa.stig.win:obj:20000017`.
- States: `oval:mil.disa.stig.win:ste:25325400` (Enterprise) and
  `oval:mil.disa.stig.win:ste:20000018` (EnterpriseS).

The production direct Object/Test adapter called `one(..., 'mapped scalar State')`.
That was a deliberately narrow production boundary, not an incorrect test
assertion. The earlier end-to-end test exercised lower-level upgrade functions
and manually inlined the Object, so it did not detect the unified converter gap.

The adapter now independently checks each original State against mature 0.3
lowering before composing the approved requirement. Test `state_operator=OR`
becomes `require.or`; each branch retains `(type=string AND value=edition)`.
Test AND (including the OVAL default) and State field AND/OR remain separate
scopes. Item existence/matching and scalar datatype/operation/value/counts are
checked explicitly. Registry hive/type enums use the existing version-local
crosswalks. The single-consumer Object is emitted inline with `hive`, `key`, and
`name`. Generated 0.4 content has no `states`, `states_match`, or
`state_fields_require` aliases.

The bounded path accepts direct registry Objects with literal scalar string or
version State comparisons and Test checks `all`/`at least one`. It rejects
Variables, records, unsupported enum comparisons, State ONE/XOR, unproven Item
population/field quantifiers, shared/missing reference graphs and other source
shapes outside this adapter's proof. Existing unrelated converter paths remain
unchanged. Source-scalar comparison tests and schema/compiler validation remain
strict; unhandled constructs are never approximated.

## Regression evidence

`test_scap_converter_core.EnterpriseRegistryStateTests` invokes production
conversion and its CLI. A narrow, independent reverse oracle creates OVAL from
only generated Object and requirement operands, then compares effective Test,
Object and complete-State semantics with the repository's ID-independent OVAL
comparator. No original XML subtree is copied into that reverse oracle.

Tests cover explicit OR, explicit/default AND, separate State field AND/OR,
rejection of changed grouping/operands, corrupt mature-lowering values/operators,
unsupported source constructs, and real YAML rendering. The approved-pipeline
regression now calls the production converter directly, validates source schemas,
checks YAML/JSON parity, builds/verifies a native bundle, and inspects the actual
compiled JSON Object and complete requirement. No live scanner is run.

Local focused validation passed **143 Tests, with no skips** using the CI-pinned
dependencies. Suites: `test_scap_converter_core`,
`test_scap_converter_core_object_presence`, `test_scap_converter_core_multistate`,
`test_scap_converter_core_apparmorstatus`,
`test_scap_converter_core_environment_uname`, `test_v04_approved_pipeline`,
`test_v04_schema_draft`, `test_v04_field_requirement_schema`,
`test_v04_native_bundle_compiler`, and `test_oval_result_truth_tables`.
Pinned original IOS/IOS XE, AppArmor, environmentvariable58 and uname inputs were
provided for the source-dependent suites.

## Independent rebaseline-smoke diagnosis

The failing hosted run is
[40098715202](https://github.com/vanderpol/scap-ng/actions/runs/40098715202), for
commit `ccf0b3f1ecad045768e083654693209edfb44030`. Its public annotation identifies
`Run maintained tool regressions` and `Process completed with exit code 1.`
Detailed hosted logs require authentication; the Actions API returned `Forbidden`.

Before changing production code, the local maintained runner failed with 3,012
Tests, 18 failures, 148 errors and 26 skips. This first run lacked CI-injected
original source fixtures. Repeating with CI's Python 3.12, PyYAML 6.0.3,
lxml 6.1.1, jsonschema 4.25.1 and cryptography, and its four original OVAL fixtures
from Self-Assertion revision `e3538595c5083b9c34d937a81d319234df9bbfaa`, ran
3,031 Tests: **19 failures, 142 errors, 26 skips**. It used the workflow's
`PYTHONPATH=.:tools:tools/scap_upconvert_v003:tools/scap_ng_roundtrip_v003` and
`python tools/run_current_tool_regressions.py`, with the workflow's AppArmor,
environmentvariable58, uname and Gatekeeper source-variable bindings.

Confirmed independent causes include:

- 120 errors end in `KeyError: 'enum'`: research C code reads
  `defs[PAIRED]['enum']` from the current schema although paired/presence tokens
  belong to its older research grammar.
- Four errors end in `KeyError: 'all_items_requirement'`: the historical
  condition-fields candidate builder assumes a definition absent from the
  approved current grammar.
- Capability-generator tests still feed legacy `states`, scalar `require`, old
  Object wrappers and old quantifier tokens to current schemas. Strict rejection
  conflicts with their historical positive assertions.
- Historical Apache preview stages pass unflattened Object wrappers or old
  quantifier spellings into strict canonical validation.
- Additional historical fixture/reference failures include
  `Unresolvable: reported-elements.schema.json` and the Gatekeeper generated/base
  schema disagreement.

These failures do not originate in the registry multi-State adapter. No schema
was relaxed, no assertions or suites were disabled, and no corpus rebaseline was
performed. Repairing all historical research consumers is a separate bounded
workstream; the broad smoke result must remain reported as failing.

Issue: [#251](https://github.com/vanderpol/scap-ng/issues/251).

## Authorized base-versus-fix comparison

The latest owner coordination instructions in #251 explicitly allow the focused
push once the historical failures are confirmed unchanged. With identical
Python/dependencies/fixtures, temporarily restored the three changed Python
files from unchanged base `ccf0b3f1ecad045768e083654693209edfb44030`, ran the
maintained runner, restored the pending fix, and ran the same command again.
Original pending file bytes were preserved and restored in a `finally` block.

| Tree | Tests | Failures | Errors | Skips |
| --- | ---: | ---: | ---: | ---: |
| Unchanged base | 3031 | 19 | 142 | 26 |
| Candidate fix | 3036 | 19 | 142 | 26 |

Compared every failure/error identity, including subtest labels and duplicate
occurrences: **161 unchanged occurrences, zero new, zero resolved**. The five
new regression methods pass. No historical suite was omitted or weakened.

The exact focused command was:

```bash
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH=.:tools:tools/scap_upconvert_v003:tools/scap_ng_roundtrip_v003 \
SCAP_NG_APPARMOR_SOURCE_XML=/workspace/.onboarding/rebaseline-fixtures/linux-def_apparmorstatus_test.xml \
SCAP_NG_ENVIRONMENT58_SOURCE_XML=/workspace/.onboarding/rebaseline-fixtures/ind-def_environmentvariable58_test_linux.xml \
SCAP_NG_UNAME_SOURCE_XML=/workspace/.onboarding/rebaseline-fixtures/unix-def_uname_test.xml \
SCAP_NG_IOS_LINE_SOURCE_XML=/workspace/.onboarding/rebaseline-fixtures/ios-def_line_test.xml \
SCAP_NG_IOSXE_LINE_SOURCE_XML=/workspace/.onboarding/rebaseline-fixtures/iosxe-def_line_test.xml \
/workspace/.onboarding/rebaseline-venv/bin/python -m unittest -v \
  test_scap_converter_core test_scap_converter_core_object_presence \
  test_scap_converter_core_multistate test_scap_converter_core_apparmorstatus \
  test_scap_converter_core_environment_uname test_v04_approved_pipeline \
  test_v04_schema_draft test_v04_field_requirement_schema \
  test_v04_native_bundle_compiler test_oval_result_truth_tables
```

For each broad comparison, the exact runner command was
`/workspace/.onboarding/rebaseline-venv/bin/python tools/run_current_tool_regressions.py`,
with the same `PYTHONDONTWRITEBYTECODE`, `PYTHONPATH`, AppArmor, environmentvariable58
and uname bindings above, plus
`OVAL_GATEKEEPER_SOURCE=/workspace/.onboarding/rebaseline-fixtures/macos-def_gatekeeper_test.xml`.
The IOS source bindings were not set in the broad runs, matching rebaseline CI.

## Codex coordination scheduling and reporting

No recurring Codex task is enabled. The session exposes no scheduling tool;
`codex --help` and `codex cloud --help` expose no recurring scheduling command.
A task-local cron process would not establish durable Codex cloud scheduling,
so none was substituted. A scheduler-capable Codex interface/tool must first be
provided; configure one hourly task there with the issue's instruction cursor,
non-overlap, deduplication and no-heartbeat requirements, then verify it.

Posting a result comment using `gh issue comment 251 --repo vanderpol/scap-ng`
failed with the exact sanitized error:
`Post "https://api.github.com/graphql": Forbidden`.
No GitHub connector is exposed in this session. Issue-write access through a
connector or an authorized API route is required to publish the result comment;
Git push access works separately. This report and issue-linked commit preserve
the engineering evidence without claiming comment publication or scheduling.

The separate source `all_exist` owner-decision boundary remains open.
No schema redesign, deprecated aliases, six-STIG rebaseline or scanner-parity
claim is included. Related issue: [#248](https://github.com/vanderpol/scap-ng/issues/248).
