# RHEL 9 — SCAP-NG 0.4.0 authoring review

Use the [0.4.0 six-STIG sample release](https://github.com/vanderpol/scap-ng/releases/tag/v0.4.0-six-stig-authoring-approved-20261020) and open `authoring/rhel_9/` in either the [YAML](https://github.com/vanderpol/scap-ng/releases/download/v0.4.0-six-stig-authoring-approved-20261020/scap-ng-0.4.0-six-stigs.yaml.zip) or [JSON](https://github.com/vanderpol/scap-ng/releases/download/v0.4.0-six-stig-authoring-approved-20261020/scap-ng-0.4.0-six-stigs.json.zip) archive. The Benchmark, its Rules, automated/manual Assessments and reusable shared Assessments are part of the same verified 4,001-document source graph.

For a guided first read, see [Benchmark and Rule examples](../../../specification/examples/README.md) and [Assessment examples](../../../specification/examples/assessments.md). Follow each Rule's logical `assessment_choices` to the referenced Assessment, rather than treating source filenames as Assessment identities.

These are **pre-alpha authoring sources**, not live collected Items or signed native 0.4 bundles. Old RHEL 9 candidate/faithful comparisons and 0.3 files are retained in the [0.3 archive](../../../archive/0.3.0/README.md).
