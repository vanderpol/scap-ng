# Draft invocation-linked Assessment Results

These standalone synthetic Assessments demonstrate conditional execution,
explicit N/A, reused dependency results, concrete Unix numeric ownership
comparison, resolved name evidence, and a derived compared-field report.
They are not production STIG migration evidence or target acquisition tests.

The conditional guard is supplied as a normalized six-state Test callback.
When true, the ownership Assessment runs once and its result is referenced twice.
The fixture file has UID 1001; the authored State requires UID 0, so ownership
is false. The conditional result is false. When the guard is false, the authored
N/A leaf wins and ownership has no invocation or Item evidence. The four other
guard outcomes propagate without invoking ownership.

`expected-results/cases.json` is the independently specified six-case oracle.
`expected-results/conditional-ownership.result-set.json` is a deterministic
snapshot assembled from synthetic observations, with stable fixture execution
IDs replacing random run IDs. It demonstrates the complete linked shape;
it is not an independent proof of every State comparison algorithm.
`ownership-observations.json` supplies local canonical Items, a Test/State/entity
comparison, Object collection, actual-use lineage and explicit completeness.
The report retains path and numeric UID; canonical evidence also retains the
resolved user name and its lookup provenance. Selection never removes canonical
observations or changes false to true.

```sh
PYTHONPATH=tools python tools/test_assessment_results_v02.py
PYTHONPATH=tools python tools/assessment_results_v02.py \
  --assessments tests/assessment-results-0.2.0/content \
  --result-set tests/assessment-results-0.2.0/expected-results/conditional-ownership.result-set.json
```

On PowerShell, set `$env:PYTHONPATH = 'tools'` and invoke the same Python commands
without the Unix environment prefix. The helper validates schema, local
references, source identity and recorded expression scheduling entirely offline.
It does not acquire resources, resolve user names or independently verify target
truth. Broader vendor feature coverage remains tracked in #128.
