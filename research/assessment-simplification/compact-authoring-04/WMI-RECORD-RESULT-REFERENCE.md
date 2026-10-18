# 0.4-A Windows DomainRole record — source-backed result boundary

**October 18, 2026 — Research-only Test/result reference fixtures.** Tracking: [#229 conformance](https://github.com/vanderpol/scap-ng/issues/229), [#232 native compiler](https://github.com/vanderpol/scap-ng/issues/232). This is **not** a Windows collector, a native executable Assessment, a published result contract, or a signed bundle.

## Real six-STIG source anchors

The pinned immutable r3 authoring JSON contains three actual `windows.wmi.query` Tests:

| Assessment source inside r3 | Test | Required observed `result.record.fields.domainrole` |
| --- | --- | --- |
| `authoring/ms_windows_11/assessments/automated/SV-253495.automated.json` | Non-domain-controller domain-joined | `1` or `3` |
| Same Windows 11 source | Standalone workstation/server | `0` or `2` |
| `authoring/ms_windows_server_2025/assessments/automated/SV-278001.automated.json` | Windows domain controller | `4` or `5` |

Every one has **two authored record States** with `states_match: any`; both Test Item existence/matching and nested record/field cardinality are explicit `at_least_one_exists_and_all_match` in the r3 0.4-A base/review representation. The WMI query is `SELECT DomainRole FROM win32_computersystem` (in namespace `root\\cimv2` for the inline Server 2025 source). The full source predicates are preserved in the [immutable six-STIG release](https://github.com/vanderpol/scap-ng/releases/tag/v0.4.0-joval-meeting-preview-20261015-r3); the exact source profiler is [tools/v04_a_source_semantics_profile.py](../../../tools/v04_a_source_semantics_profile.py).

## Reference fixtures and result boundaries

[Source-exact WMI fixture compiler and expected-result driver](../../../tools/v04_a_wmi_domainrole_source_fixture.py) refuses unreviewed source cardinalities, field names, comparator values, state scope and missing/extra record members. It derives **18** complete single-record expected outcomes (three Tests x six documented role literals) directly from the pinned source and checks predicted Results against independent literal membership expectations.

[Unit and mutation tests](../../../tools/test_v04_a_wmi_domainrole_source_fixture.py) also cover:
- complete zero collected Items cannot silently satisfy one-or-more existence;
- an incomplete stream with only matching observed Items remains `unknown` for all-Item matching, while an already observed nonmatching Item is decisively `false`;
- missing, wrongly typed, extra or malformed record fields propagate `error`, **not** the semantics of an absent collected Item;
- explicit collection flags for error, not-collected and not-applicable retain distinct result states;
- two Items with different role evidence cannot be treated as one matching witness, and source operator/quantifier changes fail closed.

The reference evaluator uses the repository's pinned OVAL 5.12.3 Test/existence and Boolean aggregation charts rather than implementing a newly invented six-state meaning.

## Audit and next step

- [Exact-head CI 39143413127](https://github.com/vanderpol/scap-ng/actions/runs/39143413127) exercises immutable r3 source IDs, exact Test predicates, the 18 source-role expected outcomes, and the unit/adversarial boundary cases together with the maintained 4,001-document six-STIG authoring/IR gate. **PASS**: 11 WMI reference/mutation tests, three source-backed WMI Tests, 18 exact role-literal fixture outcomes, alongside the maintained full six-STIG authoring and IR gates.
- Continue with an independently sourced **actual WMI collected Item/evidence provider** for this narrow record family, or a reproducible reference System Characteristics fixture. Separate record-field completeness, Item multiplicity and provenance. Then feed these Test outcomes into the already-verified nested `evaluate` trees of SV-253495 / SV-278001 without pretending the five `windows.userright` or four PowerShell Tests have been implemented.
- Original-source scanner parity, nested **multi-field** Windows records, collection timing/errors, WMI execution, and real Compliance/Rule results are still **not proved**.

No normalization of source OVAL truth or SCAP 0.3-to-0.4 version declaration is authorized by these tests.
