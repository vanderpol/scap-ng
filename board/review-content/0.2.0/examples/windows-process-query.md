# Correlated Windows process records

Status: **pending-review**. [Native Assessment](../content/windows-process-query.assessment.yaml),
[mechanical conversion](../mechanical/windows-process-query.assessment.yaml),
[source closure](../sources/windows-process-query.xml),
[provenance](../provenance/windows-process-query.json),
[independent observations/results](../expected/windows-process-query.json).

Complete Self-Assertion `windows/win-def_wmi57_object_test.xml`, Definition
`oval:org.mitre.oval.test:def:10`; Test, Object and State IDs each end in `:10`.
The reviewed versioned mapping deliberately maps `wmi57_test` to
`windows.wmi.query`. This does not authorize stripping other numeric Test suffixes.
WMI means Windows Management Instrumentation; WQL is its query language.

`process-query-object` executes the fixed publisher query
`SELECT ProcessId, Name, Description FROM Win32_Process` in `root\cimv2`.
`explorer-process-record-state` requires matching namespace/query and **at least
one whole result record** containing process ID >= 0, name `explorer.exe`, and a
description matching `.*`. Test `test-explorer-process-record` requires some
Items to exist and all selected Items to satisfy its State. Organizational Inputs
cannot replace the query or choose different Tests.

Why record grouping matters:

| Synthetic record | Process ID comparison | Name comparison | Record outcome |
| --- | --- | --- | --- |
| `{processid: 42, name: other.exe, description: other}` | true | false | false |
| `{processid: -1, name: explorer.exe, description: Explorer}` | false | true | false |

There are matching fields in the combined population, but **no matching record**.
The expected Test/Assessment result is `false`. Flattening records into unrelated
values would give a syntactically valid but incorrect answer. The fixture contains
both complete records and independently authored per-record outcomes. The bounded
helper's comparisons retain `record_index` so a reviewer can see which row matched.

Other cases establish `0` as an included boundary, `-1` as a mismatch, and a valid
Explorer record as `true`. An explicitly uncollected description is `unknown`;
a missing expected description field is `error` under OVAL 5.12.3
`EntityStateFieldType`, and a query acquisition failure is `error` before matching.
These are typed synthetic Items, not fabricated live Windows evidence.

Native refinement only shortens titles. The record fields, numeric operation,
quantifiers, literal query and graph are unchanged from mapped mechanical output.
No shell command or actual Windows collector is run. Record grouping and result
reasoning are covered; live WMI acquisition and general regular-expression
conformance remain outside this pilot.
