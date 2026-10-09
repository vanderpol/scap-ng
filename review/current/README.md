# Current SCAP-NG 0.3 review

**Status:** pre-alpha. The six-STIG readability candidate has passed
conversion and its native schema/semantic checks. Final 65-source and
six-state runtime-conformance work continues; do **not** infer release
approval from the example ZIP.

**For a quick owner review, start at the
[10-minute sample guide](REVIEW-GUIDE.md).**
It points to the verified
[six-benchmark candidate artifact](https://github.com/vanderpol/scap-ng/actions/runs/37915343548/artifacts/11609966698)
containing complete authoring trees for RHEL 9, Oracle Linux 9, Windows 11,
Windows Server 2025, Windows Server DNS, and Apache 2.4.

The **candidate** uses `benchmarks/<name>/candidate-authoring/`; the
corresponding `faithful-authoring/` is included for side-by-side inspection.
It is an authoring/design example, **not** a scanner runtime result or a
compiled package. The normative current syntax is defined in
[selection and filtering](../../specification/assessment/selection-and-filters.md).

For a simpler in-browser view first, use the
[Benchmark and Rule](../../specification/examples/README.md) and
[Assessment examples](../../specification/examples/assessments.md) pages.

Technical release evidence: [embedded-filter migration #208](https://github.com/vanderpol/scap-ng/issues/208),
[0.3 release gate #191](https://github.com/vanderpol/scap-ng/issues/191), and
[full corpus correctness #202](https://github.com/vanderpol/scap-ng/issues/202).
The earlier 65-source run [37914508160](https://github.com/vanderpol/scap-ng/actions/runs/37914508160)
uncovered audit-policy regex schema validation gaps, now addressed in the
converter regression suite. Latest-run results must be inspected independently
before describing full-corpus conformance as established.

The [0.2 schema](../../schema/v0.2.0/README.md) remains the historical
Board reference; deferred features are listed in
[deferred-after-0.3](../../specification/deferred-after-0.3.md).
