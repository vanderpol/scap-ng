# 0.4.0 owner-decision integration — #251

Starting `main`: `b1b1722acef4ee0a4f9d6f5be09c76aab65228aa`.
Authority: owner-approved [historical CI separation](https://github.com/vanderpol/scap-ng/issues/251#issuecomment-6388691847)
and [Test-level all_exist normalization](https://github.com/vanderpol/scap-ng/issues/251#issuecomment-6388735943),
both dated 2026-10-24. These are distinct implementation commits. No schema
redesign, legacy authoring aliases, editor change or six-STIG regeneration.

## Historical CI separation

The [routing manifest](../../tests/ci/historical-research.json) records every
pre-split discovered test ID, the 181 exact historical test methods across 16
reviewed modules, their original source SHA-256 values and all 128 failing
occurrences from the [prior inventory](v04-readiness-regression-classification.json).
Classification follows actual test content, not a filename prefix. The proposal
schema/field-scope modules exclusively exercise old candidate dialects; the
maintained Apache bridge, current schema, production converter, compiler and
negative semantic guards remain in the mandatory partition.

The runner verifies the historical source hashes and exact method selection,
rejects disappearing pre-split IDs, defaults new tests into the current gate,
and writes exact selections, actual counts, full failure identities and tracebacks
to JSON. The partition union covers all 3,070 previously selected discovered
methods, with no overlaps or missing IDs. Existing archived Board/dialect
exclusions predate this decision and are recorded unchanged.

Research CI checks out the complete original source/toolchain at
`b1b1722acef4ee0a4f9d6f5be09c76aab65228aa`, with Python 3.12.14,
PyYAML 6.0.3, lxml 6.1.1, jsonschema 4.25.1 and cryptography 50.0.2.
The current routing runner executes those original tests with the pinned source's
import paths. It requires the exact source ref and unchanged tracked tools,
schemas and tests. Failures cause a real failing job; no `continue-on-error`,
xfail, test rewrite, assertion removal or success wrapper is used. Results upload
with `if: always()`. This workflow is explicitly separate from 0.4 release gating,
as authorized; its red result is retained, not waived into a green result.

Local verification:

| Run | Tests run | Failures | Errors | Skips |
| --- | ---: | ---: | ---: | ---: |
| Prior unchanged combined baseline | 3045 | 1 | 127 | 26 |
| Current partition, same fixture bindings | 2881 | 0 | 0 | 26 |
| Original pinned research partition | 164 | 1 | 127 | 0 |
| Current partition, complete pinned converter fixtures and OVAL XSD | 2889 | 0 | 0 | 1 |

Research diagnostics match **128/128 exact original failing identities**. Counts
of discovered methods differ from `testsRun` because unittest class-level setup
errors/skips prevent those methods from executing. Mandatory current selection
contains 2,889 discovered methods. No current-production identity was lost.

The mandatory rebaseline workflow now also binds the complete existing converter
fixture set from immutable Self-Assertion revision
`e3538595c5083b9c34d937a81d319234df9bbfaa` and the vendored original OVAL 5.12.3
XSD. This strengthens source-backed execution rather than suppressing skips.
The source-backed suites and positive/negative schema guards retain their existing
assertions. Final expanded-fixture and hosted counts are recorded below.
The expanded current run passed in 123.449 seconds. Its only remaining skip is
the pre-existing optional full research-corpus census, not a production converter
guard. The four original positive/negative OVAL operator-XSD tests also passed
independently. No synthetic success runner replaces the actual regression run.

Commands (Python executable in this environment:
`/workspace/.onboarding/rebaseline-venv/bin/python`):

```bash
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH=.:tools:tools/scap_upconvert_v003:tools/scap_ng_roundtrip_v003
# Supply the exact SOURCE_XML bindings listed in rebaseline-smoke.yml.
python tools/run_current_tool_regressions.py --report /tmp/current-regressions.json
git worktree add --detach /tmp/scap-ng-research b1b1722acef4ee0a4f9d6f5be09c76aab65228aa
cd /tmp/scap-ng-research
python /path/to/current/tools/run_current_tool_regressions.py \
  --partition historical --source-root . --report /tmp/historical-regressions.json
```

Hosted workflows retain these same report artifacts. GitHub branch-protection
administration was not changed; selecting required check names externally is
distinct from the repository's authorized test routing.
