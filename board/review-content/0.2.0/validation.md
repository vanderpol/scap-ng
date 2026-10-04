# Pilot validation evidence

Status: **local validation passed; human review pending**. Date: 2026-10-04.

Starting content state: clean `main`,
`6ba41d4e9e34a88ced8d930d9f3126738350b65d`, descendant of frozen technical baseline
`7cd8b1242d7fb4a2eb9b5f49c7ec3f48b2dd622d`. The existing older checkout was
fast-forwarded; no reset, recreation or SCAP-NG clone was performed.

Self-Assertion was accessible. Its separate local checkout verifies revision
`e3538595c5083b9c34d937a81d319234df9bbfaa` and tree
`d0b680aa781cde9e55ad8778b71ee82da37ebab3`. Whole-file and extract SHA-256 pins
are recorded in provenance. The six retained source extracts are XSD-valid.

| Check | Actual local result | Claim |
| --- | --- | --- |
| Eight baseline modules: promotion, semantic validation, authoring contract, existence, truth tables, conditional integration, results, Variable/filter dependencies | 176 tests passed before authoring | Frozen authoring/semantic regression readiness |
| Maintained rebaseline unittest discovery before authoring | 775 tests passed | Local smoke baseline reproduced |
| Board sample regression | 12 tests passed, including 30 independently reasoned cases | Bounded synthetic semantics, scheduling, source parity, evidence consistency, negative cases and reproducer preservation |
| Strict 0.2.0 schema validation | 7/7 native documents valid, zero unclassified | Version-local capability schemas; no legacy bridge enabled |
| Capability semantic validation and expression graph resolution | All seven pass | Capability compatibility, literals, dependency identity/version and scheduling graph; local dataflow separately guarded |
| Pilot-local dataflow guard | Seven pass; cycle reproducer rejected | Independent acyclic/missing-reference guard; core local-Variable cycle diagnostic gap remains |
| Authoring-contract check | Seven pass, no violations | Presentation/vocabulary only |
| Native comparison crosswalks | Five converted cases match selected source quantifiers, State settings and constants | Bounded source/native correspondence, pending human review |
| Selected Self-Assertion round trips | Five selected closures comparator-equal | Maintained intermediate lowering/reverse representation only; not strict native-file or scanner equivalence |
| Source extract XSD validation | Six pass | XML structural validity only, not complete source semantic validity |
| UNIX linked result validation | Pass | Result schema, source references, Item contract, comparison lineage and recorded expression scheduling |
| Rebaseline unittest discovery after authoring | 787 tests passed | Existing smoke tests plus twelve new pilot tests |
| Repository boundary audit and authored-file diff whitespace check | Pass | No forbidden generated tree; pinned verbatim MITRE terms excluded from whitespace check |

Run the baseline/smoke commands from the repository root:

```sh
python -m unittest tools.test_schema_v02_promotion tools.test_validate_generated_capability_semantics tools.test_current_authoring_contract tools.test_ng_existence_semantics tools.test_oval_result_truth_tables tools.test_conditional_integration tools.test_assessment_results_v02 tools.test_variable_filter_dependencies
python -m unittest discover -s tools -p 'test_*.py'
python tools/test_board_samples_v02.py --report work/board-pilot-validation.json
```

For unittest discovery set `PYTHONPATH` to `tools`, `tools/scap_upconvert_v003`
and `tools/scap_ng_roundtrip_v003` using the OS path separator. The direct pilot
command configures its own import path and is portable. Local runs used the
existing `/workspace/.venvs/scap-ng/bin/python` environment.

CI integration uses **Current-design regression contracts**, Ubuntu and Windows.
It runs the pilot, strict schemas and presentation check, and uploads
`board-pilot-validation-ubuntu-latest` / `board-pilot-validation-windows-latest`.
The receipt records the exact tested commit and evidence limits; it never changes
the checked-in oracle. Board content and reproducer paths now trigger this lane.
Rebaseline smoke also discovers the new tests. Local success is not labeled as
remote CI success; exact remote run evidence belongs in the final handoff report.

The first Windows CI pilot step failed; its log download was blocked by the
managed network policy. A local CRLF checkout simulation reproduces the inventory
hash failure. Scoped `.gitattributes` now keeps YAML, JSON, XML and documentation
as LF on every platform, preserving pinned bytes instead of weakening the hashes.
The corrected Windows run is required before reporting cross-platform success.
This is a pilot portability/harness issue, not a language/schema defect.

The verbatim upstream MITRE terms retain four trailing-whitespace lines so their
recorded source hash remains exact. All authored files pass the whitespace check.

No 0.2.0 schema/specification or converter code was changed. No new capability,
deprecated Test, ESX/Kubernetes expansion, editor, full STIG conversion, or
65-benchmark NIWC run was performed. No live scanner or independent evaluator
was run. Signing/trust, source compilation into a Benchmark package, collection
defaults/execution and exhaustive capability conformance remain outside this pilot.
