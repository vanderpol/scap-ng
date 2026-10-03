# Conditional schema and compiler integration checkpoint

Owner direction, 2026-10-03: continue from the known-result conditional suite to
0.2.0 schema and evaluator integration. Baseline:
`dec2cef9a3a5de01bc4cf4cfe15ca8fac86df170`, PR #127. This checkpoint builds on that
suite and preserves its controlled outcome fixtures separately from authored
content. It does not merge either PR or declare a completed 0.2.0 release.

The new `schema/v0.2.0` is an explicitly partial Assessment expression draft.
Its [contract](../schema/v0.2.0/README.md) defines guard propagation, mandatory
branches, explicit N/A with a reason, eager ordinary aggregation, dependency
resolution and expression-stage traces. The existing fixture grammar remains
pinned to proposal-01 for reproducible experimental evidence.

The maintained expression engine is now `tools/assessment_expression.py`, with
a lazy Test callback and optional normalized manual-result callback. The old
`ConditionalModel` is a compatibility adapter for controlled fixtures. Test
acquisition/State evaluation is still supplied by the caller, not a reference
scanner. Runtime output does not serialize effective binding values into its
trace. Existing fixture-only context output remains clearly marked `model_only`.

The content compiler now packages static dependency closure, including unused
declarations and unselected branches, rather than only Assessments directly
referenced by Rules/applicability catalogs. It verifies authored identity/version/
purpose expectations, rejects cycles, duplicate identities and dependency path
escapes, and emits immutable logical bindings backed by manifest content hashes.
The bundle verifier checks dependency closure and the draft expression grammar.
0.1.0 source schemas and expression handling remain unchanged; new 0.2.0 source
must explicitly opt into its provisional specification version.

`tools/test_conditional_integration.py` covers all fourteen authored examples
against the versioned draft; all 216 local guard/branch combinations through the
runtime callback and result schema; actual constant-Boolean content with an
unselected Test that must not execute; binding-value nondisclosure; one/odd
aggregation; normalized manual dependency outcomes; source-to-package-to-runtime
execution; invalid references in unselected branches; unused dependency cycles;
version mismatches; shared nested dependency bindings; and semantic defects in bundles whose hashes are valid.

Reproduction:

```
PYTHONPATH=tools python tools/test_conditional_integration.py
PYTHONPATH=tools python tools/test_conditional_conformance.py
python tools/conditional_conformance.py --help
```

The existing fixture suite remains 465 known-result evaluations plus ten invalid
cases. Its nineteen test methods also include the full 1,296-case intrinsic
applicability matrix. These are language/representation tests, separate from
published STIG migration evidence. No claim of target collector equivalence,
complete scanner implementation, full corpus 0.2.0 conversion, or complete vendor
feature coverage follows from these results.

Remaining: integrate typed expression traces with the complete 0.2.0 result graph
and collected Item work (#129); implement `reported_elements` (#125); complete
the vendor-facing benchmark/standalone Assessment/expected-results corpus (#128).
Owner follow-up, 2026-10-03: normalization candidates/upgrades (#126) are removed
from planned features and the issue is closed as not planned. The general rewrite
is not lossless across six-state truth or collection/evidence behavior; retain
the existing counterexample regression. Unsupported existing
expression forms require explicit semantic lowering before any version upgrade.

Validation: 123 focused and existing regressions passed using `PYTHONPATH=tools python -m unittest tools.test_conditional_integration tools.test_conditional_conformance tools.test_scap_ng_content_compiler tools.test_schema_issue_regressions tools.test_validate_native_package_graph tools.test_package_manifest_schema tools.test_current_validation_names tools.test_oval_result_truth_tables tools.test_oval_result_truth_tables_exhaustive`. All three draft schemas meta-validate. The fixture CLI checks 465 cases and ten invalid cases with no failures. `tools/check_current_authoring_contract.py` passes for all fourteen example Assessments, with its documented vocabulary-only limit. `git diff --check` passes.
