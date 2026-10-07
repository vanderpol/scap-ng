# SCAP-NG examples

Examples are supporting material for the specification. They do not override the
normative text and are not automatically accepted merely because they validate.

## Version rule

The active examples track the active prerelease specification. Each published
prerelease/review checkpoint SHALL regenerate or revalidate its source and result
examples against the exact schema/specification version being reviewed. A sample
from an older prerelease must not be presented as current merely because it still
parses.

Completed review iterations preserve their exact example set immutably under
`review/iterations/`.

## Active 0.3 source candidate

The current six-benchmark 0.3 human-review candidate is generated from pinned
SCAP 1.4 sources and includes complete faithful-versus-modernized authoring trees:

- [0.3 candidate review build](https://github.com/vanderpol/scap-ng/actions/runs/37649993955)
- [combined six-benchmark artifact](https://github.com/vanderpol/scap-ng/actions/runs/37649993955/artifacts/11496651572)

This is prerelease review material, not accepted 0.3 syntax.

## Frozen 0.2 source examples

For small checked-in examples, start here:

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

The checked-in result fixtures below are the frozen 0.2 baseline. They remain
useful examples, but they SHALL be revalidated/version-labeled for 0.3 before a
0.3 prerelease is published.

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
