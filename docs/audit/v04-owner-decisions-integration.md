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

First implementation commit:
[`6836bb3bd`](https://github.com/vanderpol/scap-ng/commit/6836bb3bd).
Terminal hosted results for that SHA:

| Workflow | Result |
| --- | --- |
| [Mandatory rebaseline](https://github.com/vanderpol/scap-ng/actions/runs/40133051561) | Passed |
| [Pinned historical research](https://github.com/vanderpol/scap-ng/actions/runs/40133051545) | Failed, retained separately with actual diagnostics |
| [Repository preservation](https://github.com/vanderpol/scap-ng/actions/runs/40133051559) | Passed |
| [Markdown](https://github.com/vanderpol/scap-ng/actions/runs/40133051791) | Passed |
| [Issue references](https://github.com/vanderpol/scap-ng/actions/runs/40133051553) | Passed |

## Test-level all_exist normalization: reviewed semantic packet

**Dated owner decision: 2026-10-24**, linked above. The intended change is an
explicit semantic normalization under a narrower evidence model, not a schema
change or an unrestricted OVAL 5.12.3 equivalence proof. The review packet below
records the source-backed example, boundary evidence and rejected alternatives.
Implementation version: `scap-ng-0.4.0/actual-items-test-all-exist/1`.

Original pinned production source:
`research/assessment-simplification/evidence/rhel_9/SV-258179/source-oval.xml`,
SHA-256 `463b539c469c3302aa52c23fdca35814f40fd5fd7de31346964e1b4a97b5d8a9`.
Definition `oval:mil.disa.stig.defs:def:230413` extends other source Definitions;
its mature shared lowering retains 24 Tests and 17 Variables. Its generator
reports OVAL schema version **5.11**, preserved unchanged in provenance; the
semantic reference baseline is OVAL 5.12.3. Sixteen original Tests explicitly
use `all_exist`; eight use/default to `at_least_one_exists`.

Minimal source example (original Test has no State):

```xml
<textfilecontent54_test id="oval:mil.disa.stig.ind:tst:23041300"
  version="1" check_existence="all_exist" check="all">
  <object object_ref="oval:mil.disa.stig.ind:obj:23041300"/>
</textfilecontent54_test>
```

The original Object selects `/etc/audit/audit.rules`, the setxattr b32/auid>=1000
regex and `instance >= 1`. All remain unchanged. The previous source-backed
upgrade rejected the all_exist/one_or_more source-axis difference. After the
approved normalization the actual generated Test requirement is:

```yaml
require: {items_found: one_or_more}
```

Original OVAL Test/Object IDs, versions, the exact source file hash, serialized
original Object XML hash, original existence attribute, source schema version,
native Test ID, dated decision, scope/reason and contract version are recorded
outside authoring in `test_existence_normalizations`. The original XML remains
unchanged. The inverse ledger restores each original Test's `all_exist`; the
other eight retain their distinct original requirements. Original OVAL semantic
reconstruction is checked **before normalization**, never presented as an
unrestricted equivalence proof of the normalized result.

### Admission and evidence boundaries

- The shared converter admits the exact pinned file/Definition only, after
  original semantic-root reconstruction. Changed source bytes, corrupted mature
  lowering or an unreviewed collection contract fail closed. The ordinary
  source-axis oracle still rejects silent all_exist normalization without the
  explicit contract. State-bearing all_exist remains outside this new proof.
- The upgrader's explicit contract option changes only the source-axis audit for
  state-free Test existence. Structured source promotion, graph/reference checks,
  whole-document equality and both source/Object inverses remain enforced.
  Field/record existence, matching and comparisons are untouched; no new schema
  key, authored alias, collector implementation or evaluation kernel was added.
- `collected-item.schema.json` already excludes synthetic `does_not_exist` Items
  and retains `error`/`not_collected` diagnostics. The admission helper checks this
  unchanged schema contract. Source existence metadata stays in provenance, not
  synthetic authored/native Items.
- The evidence-conformance checker rejects synthetic Items and contradictory
  complete-success declarations containing error/not-collected Item evidence.
  It does not discard that evidence or compute Test results. Error/unknown
  diagnostics must retain collection-level error/unknown status. A real scanner
  must independently demonstrate this contract; no live collector/runtime proof
  is claimed by this conversion implementation.

Retained source-reference cases:

| Evidence | Original all_exist | Normalized native presence | Disposition |
| --- | --- | --- | --- |
| Complete, zero actual Items | false | false | Required absence outcome |
| Complete, one or more actual Items | true | true | Subject to separate State/matching requirements; pinned Tests have none |
| Error collection, including existing Items | error | error | Never silently converted to complete success |
| Incomplete or not-collected collection | unknown | unknown | Existing Items do not erase incomplete evidence |
| Complete, one exists + one synthetic does_not_exist OVAL Item | false | true under at_least_one_exists | **Retained counterexample**, intentionally outside native contract; synthetic Item rejected |
| Complete with material Item error/not-collected diagnostics | Not asserted equivalent | Invalid complete-success evidence for this proof | Reject contradictory evidence, preserve diagnostics |

No generic six-state/scanner parity follows. The generic matrix report explicitly
labels normalized native axes and reports `unrestricted_original_axes_equivalent:
false`; it is not relabeled an exact original-axes proof. Existing original OVAL
truth-table functions and their counterexamples are unchanged.

Rejected alternatives: changing approved grammar, adding legacy aliases,
inventing nonexistent Items, globally replacing every all_exist token (including
fields/records), silently discarding error evidence, or falsely asserting full
OVAL equivalence. None is needed or authorized.

### Source inventory, regressions and scope

The [read-only metadata inventory](v04-source-test-all-exist-inventory.json)
scanned all **13 checked-in production `source-oval.xml` fixtures**, finding
**16 all_exist occurrences**, all state-free textfilecontent54 Tests in this
one pinned file. This is not a full corpus conversion or conformance denominator.
No other source family is newly admitted. The 16 affected Tests and all eight
unaffected Tests in that Definition are checked explicitly.

`test_v04_all_exist_normalization` checks source/metadata/inverse preservation,
the public converter CLI, canonical YAML/JSON equality, typed IR reconstruction,
full schema validation, the actual compiled 24-Test program and bundle verifier,
the original mixed-population difference, empty/positive/error/incomplete/unknown
evidence, result-schema synthetic-Item rejection, source drift and corrupt mature
lowering. `test_v04_canonical_requirement_oracle` retains its implicit-mapping
negative and adds explicit-contract/field-axis boundary coverage. The existing
`test_real_all_exist_source_requires_owner_population_decision` identity now
tests the approved explicit normalization while keeping its original OVAL
counterexample; its historical method name is retained for inventory continuity.

Focused results: **20 tests passed** in the first repaired source/pipeline/oracle
run, then **16 passed** after adding public CLI and full result-schema evidence
checks (eight normalization plus eight oracle tests). No skip or expected failure
was added. Final full mandatory and hosted results follow after publication.

Reproduce with the same Python/dependencies and fixture bindings as above:

```bash
python -m unittest -v test_v04_all_exist_normalization \
  test_v04_approved_pipeline test_v04_canonical_requirement_oracle
python tools/scap_converter_core.py \
  --source-xml research/assessment-simplification/evidence/rhel_9/SV-258179/source-oval.xml \
  --definition-id oval:mil.disa.stig.defs:def:230413 \
  --output /tmp/audit-syscalls.json --evidence /tmp/audit-syscalls-provenance.json
python tools/run_current_tool_regressions.py --report /tmp/current-normalized.json
```

The native compiler already preserves these requirement operands; its code and
schema JSON are unchanged. The shared converter-core CI now explicitly runs the
new source-backed suite in addition to the mandatory full current partition.

Final local mandatory run after both changes: **2,898 tests, zero failures,
zero errors, one pre-existing optional research-corpus skip**, in 127.312 seconds.
All 3,070 baseline discovered identities remain accounted for; nine new methods
(eight normalization, one oracle boundary) default into mandatory CI. The exact
selection report records no missing baseline IDs. No historical test sources,
assertions or original OVAL XML were changed. Schema JSON and native compiler
code are unchanged. Layout-preservation and whitespace checks passed; standard
Markdown audit has no new broken references (three old Board-heading links remain).

Remaining release gates are independent source/capability coverage, whole-package
acceptance at its separately authorized checkpoint, production publisher trust
and signing policy, clean-extract toolchain reproducibility, normative-document
reconciliation and scanner/collector acceptance. The two decisions implemented
here no longer block this bounded work. No six-STIG or 65-benchmark conversion,
release publication, editor change or scanner-parity claim was made.

Issue-write access was previously denied with
`Post "https://api.github.com/graphql": Forbidden`; the committed engineering
report remains the authorized handoff without repeated permission attempts.

## Final publication and exact CI outcomes

- Historical routing implementation:
  [`6836bb3bd187418553c4fe1e47ee9fe2d5a82342`](https://github.com/vanderpol/scap-ng/commit/6836bb3bd187418553c4fe1e47ee9fe2d5a82342).
- Test normalization implementation:
  [`2de578c088291558f44d0c7a505ad149dea5fc76`](https://github.com/vanderpol/scap-ng/commit/2de578c088291558f44d0c7a505ad149dea5fc76).

Both were normal, non-forced pushes directly to `main`. The working tree was
clean after removing only this task's temporary Python caches/operator-XSD output.
The complete [hosted conclusion inventory](v04-owner-decisions-ci.json) records
all 18 runs observed for the normalization SHA: **11 passed, seven failed**.
The historical workflow ran separately on the routing SHA and remains red above.
Public run conclusions are not substituted for authenticated per-test logs;
precise local test counts/identities and hosted report artifacts are distinguished.

Current-workflow results on the normalization SHA:

| Workflow | Exact outcome |
| --- | --- |
| [Mandatory rebaseline](https://github.com/vanderpol/scap-ng/actions/runs/40133633841) | Passed |
| [0.4 schema](https://github.com/vanderpol/scap-ng/actions/runs/40133633882) | Passed |
| [Shared converter core, including normalization](https://github.com/vanderpol/scap-ng/actions/runs/40133633935) | Passed |
| [Canonical fast checks](https://github.com/vanderpol/scap-ng/actions/runs/40133633833) | Passed |
| [Current-design contracts](https://github.com/vanderpol/scap-ng/actions/runs/40133633898) | Passed |
| [Repository preservation](https://github.com/vanderpol/scap-ng/actions/runs/40133633837) | Passed |
| [Markdown](https://github.com/vanderpol/scap-ng/actions/runs/40133633913) | Passed |
| [Issue references](https://github.com/vanderpol/scap-ng/actions/runs/40133633864) | Passed |
| [Original core conversion coverage](https://github.com/vanderpol/scap-ng/actions/runs/40133633854) | Passed |
| [Toolchain clean-extract smoke](https://github.com/vanderpol/scap-ng/actions/runs/40133633910) | Passed; bounded smoke, not full release reproducibility/trust acceptance |
| [003 Self-Assertion semantics](https://github.com/vanderpol/scap-ng/actions/runs/40133633874) | Passed; not 0.4 scanner parity |

Other automatically triggered source-preview/research workflows remain visible:

| Workflow | Exact outcome |
| --- | --- |
| [Original OVAL multi-Test flat-Object pilot](https://github.com/vanderpol/scap-ng/actions/runs/40133633843) | Failed |
| [Original OVAL constant family Variable XML roundtrip](https://github.com/vanderpol/scap-ng/actions/runs/40133633917) | Failed |
| [OVAL family constant Variable original XML roundtrip](https://github.com/vanderpol/scap-ng/actions/runs/40133633876) | Failed |
| [Complete AND-OR-XOR authoring candidate proof](https://github.com/vanderpol/scap-ng/actions/runs/40133633919) | Failed |
| [Strict six-anchor authoring schema gate](https://github.com/vanderpol/scap-ng/actions/runs/40133633853) | Failed |
| [Six-STIG flat Object preview](https://github.com/vanderpol/scap-ng/actions/runs/40133633807) | Failed |
| [State alternatives AND/OR normalization proof](https://github.com/vanderpol/scap-ng/actions/runs/40133633855) | Failed |

These failures are neither hidden nor waived by the maintained-test split. Their
per-workflow diagnosis/reconciliation remains separate readiness work; this task
does not claim every workflow is green or that these seven all have the same root
cause. No fresh six-STIG production regeneration or manual dispatch was performed;
existing automation triggered the listed preview/research checks on the push.
Do not publish a final release based only on the now-green maintained regression.

Changed files by implementation (the report spans both):

- CI routing: `tools/run_current_tool_regressions.py`,
  `tests/ci/historical-research.json`, `.github/workflows/rebaseline-smoke.yml`,
  `.github/workflows/historical-research-regression.yml`, this engineering report.
- Normalization: `tools/v04_all_exist_normalization.py`,
  `tools/scap_converter_core.py`, `tools/build_v04_canonical_six_stigs.py`,
  `tools/v04_canonical_requirement_oracle.py`, `tools/v04_field_requirement.py`;
  `tools/test_v04_all_exist_normalization.py`, `tools/test_v04_approved_pipeline.py`,
  `tools/test_v04_canonical_requirement_oracle.py`;
  `.github/workflows/v04-converter-core-bridge.yml`, `CHANGELOG.md`,
  `schema/v0.4.0/README.md`, `research/iterations/003/design/CURRENT-DESIGN.md`,
  the source-Test inventory and this report. The final hosted-conclusion JSON is
  a report-only handoff addition.
