# SCAP-NG examples

Examples are supporting material for the specification. They do not override the
normative text and are not automatically accepted merely because they validate.

## Source examples

Start with these small native Assessment examples:

- [UNIX file](../../board/review-content/0.2.0/content/unix-file.assessment.yaml)
- [Windows registry](../../board/review-content/0.2.0/content/registry.assessment.yaml)
- [Text-file content](../../board/review-content/0.2.0/content/textfilecontent54.assessment.yaml)
- [Linux RPM information](../../board/review-content/0.2.0/content/rpminfo.assessment.yaml)
- [Variable and Set/filter dataflow](../../board/review-content/0.2.0/content/filter.assessment.yaml)
- [Manual Assessment](../../board/review-content/0.2.0/content/manual.assessment.yaml)

For the complete maintained source-example inventory, including feature and
stress cases, see
[Assessment feature samples](../../board/review-content/0.2.0/FEATURE-SAMPLES.md).

## Result examples

For a complete linked Assessment Result example, including Test/State/entity
comparison, Items, provenance, completeness, conditional execution, and reused
dependency results, see:

- [linked Assessment Result set](../../tests/assessment-results-0.2.0/expected-results/conditional-ownership.result-set.json)
- [result example explanation](../../tests/assessment-results-0.2.0/README.md)

The normative result model is
[Results and Evidence](../results/results.md).

## Larger converted content

The current human-review area links to representative full converted benchmarks
and current candidate review artifacts:

- [Current review](../../review/current/README.md)

Large generated benchmark sets remain CI/evidence artifacts rather than being
duplicated into the specification tree.
