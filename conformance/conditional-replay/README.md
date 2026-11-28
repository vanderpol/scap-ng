# Ordered conditional report-side replay

The existing [Input-only Assessment](../cases/supplemental/conditional-ordered.assessment.yaml)
and the [mixed Test and Input guard Assessment](mixed-guards.assessment.yaml)
exercise first-true ordering, nested selection and indeterminate
guards. The replay supplies explicit leaf dispositions and Input
presence to the production RI report-side reducer.

Five Input-only scenarios and six mixed scenarios match the independent
outcomes and branch commitments. An explicitly empty Input is present.
An earlier true guard selects its body even when that body returns false.
An indeterminate later guard stops selection before a subsequent present
Input can select a body.

The [receipt](ri-receipt.json) records four remaining failures. Two
first-guard scenarios normalize distinct not-applicable and not-evaluated
states to unknown. Two later-guard scenarios return the expected technical
outcome, while projecting the trace fields into the canonical Result
schema rejects the combination of a false condition and null branch.
The replay tests the shared report-side reducer and reproduces its trace
projection. Full Benchmark execution and acquisition suppression need
separate runtime receipts.

```sh
python conformance/tools/replay_conditional_trace.py --check \
  --ri /path/to/pinned/scap-ng-ri
```

- [Approved ordered conditional contract](https://github.com/vanderpol/scap-ng/issues/25)
- [RI guard status and trace gap](https://github.com/vanderpol/scap-ng-ri/issues/309)
