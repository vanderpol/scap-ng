# SCAP-NG 0.4.0 — a short six-STIG review

**Audience:** owner, implementers and OVAL Board reviewers. This is an authoring-sample review, not a request to certify or ratify a scanner.

**Download:** [YAML source](https://github.com/vanderpol/scap-ng/releases/download/v0.4.0-six-stig-authoring-approved-20261020/scap-ng-0.4.0-six-stigs.yaml.zip) · [JSON source](https://github.com/vanderpol/scap-ng/releases/download/v0.4.0-six-stig-authoring-approved-20261020/scap-ng-0.4.0-six-stigs.json.zip) · [all release evidence](https://github.com/vanderpol/scap-ng/releases/tag/v0.4.0-six-stig-authoring-approved-20261020)

Open either ZIP and follow `authoring/`. Both contain the same **4,001 logical source documents**.

| Explore | What to verify |
| --- | --- |
| `authoring/rhel_9/` | Benchmark policy and Rule `assessment_choices` resolving to actual logical Assessment IDs |
| `authoring/ms_windows_server_2025/` | Complex `windows.wmi.query`, `windows.userright`, record fields and composed `evaluate` branches |
| `authoring/ms_windows_server_dns/` | Windows record predicates and multi-source collection requirements |
| `authoring/apache_server_2-4_unix_server/` | Filters, Sets and Variables alongside the simple inline-Test contract |
| `authoring/shared/assessments/` | Reuse without missing or duplicate Assessment IDs |
| Each `benchmark*.yaml` or `.json` | Exact reachable `assessment_specifications` version **0.4.0**, without unused 0.3.0 declarations |

**Start with simple Tests before complicated Windows ones.** Inside `tests`, read `test_title`, `capability`, `object`, `require`, then the enclosing `evaluate` expression. Legacy-looking converted IDs are not new capability names. A more readable authoring presentation is covered in the [Assessment examples](../../specification/examples/assessments.md).

**Known limits:** 172 exceptional matching requirements remain source-exact; 25,628 generic existence/matching result checks passed, but there is not yet a full capability-specific scanner equivalence proof or native signed 0.4 bundle compiler. See [finalization gates](0.4.0-FINALIZATION-GATES.md).

The historical [0.3.0 compiled/prerelease content](../../archive/0.3.0/README.md) remains independently accessible; do not compare its scanner bundles as if they were compiled 0.4.0 content.
