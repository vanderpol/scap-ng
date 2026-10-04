# SCAP-NG 0.2.0 Board review content

Status: **seven-sample pilot; pending human review**

This directory is the human-reviewable sample-content portion of the SCAP-NG 0.2.0 OVAL Board checkpoint.

The checkpoint SHALL include 5–10 small SCAP-NG Assessments chosen to demonstrate important 0.2.0 semantics without forcing reviewers to inspect full STIG conversions.

## Read the pilot

Frozen technical baseline: `7cd8b1242d7fb4a2eb9b5f49c7ec3f48b2dd622d`.
Work started on clean `main` at `6ba41d4e9e34a88ced8d930d9f3126738350b65d`.
Source: OVAL-Community/SCAP-Self-Assertion at
`e3538595c5083b9c34d937a81d319234df9bbfaa`, verified locally and through GitHub.

| Sample | Origin / source Definition | Review value | Expected technical outcomes |
| --- | --- | --- | --- |
| [Family](examples/family.md) | Converted, complete `def:95` | Objectless system source; retained regex Variable | true, false, error, unknown |
| [Constants](examples/constants.md) | Converted, complete `def:92` | Direct Variable source; typed values; boundary and mismatch | true, false |
| [Concat](examples/concat.md) | Converted, `def:65`, criterion `tst:722` | Cartesian products, quantifier scopes, derived zero values | true, false, error |
| [UNIX file](examples/unix-file.md) | Converted, `def:1`, criterion `tst:9` | Small Object/State/Test graph; linked result evidence | true, false, error, unknown, not_applicable |
| [Registry](examples/registry.md) | Converted, `def:38`, criterion `tst:1020` | Reviewed hive name; case-insensitive State; exactly one satisfying Item | true, false, error |
| [Filter](examples/filter.md) | Native; source `def:276` / `tst:451` is inspiration | Object-component and Variable chains, arithmetic, operand filter, nested intersection | true, false, error |
| [Dependency](examples/dependency.md) | Native | Platform guard; conditional scheduling; repeated dependency reuse | All six states |

The table abbreviates source IDs only for reading. [Provenance](provenance/)
records full original IDs, source versions, original-file hashes, extracted-node
hashes, and exact source links. [Manifest](manifest.json) is the machine-readable
sample inventory; [coverage](coverage.json) distinguishes evidence layers and gaps.

For each converted sample, open its explanation, `sources/<name>.xml`,
`content/<name>.assessment.yaml`, then `expected/<name>.json`. The three selected
criteria are **fragments**, not conversions of their complete multi-Test source
Definitions. The Definition's metadata is preserved in the extract; its criteria
is reduced intentionally and recorded in provenance. Unreferenced source nodes
are omitted. No executable XML residue is placed in native Assessments.

These five conversions are manually transcribed against frozen versioned mappings.
The maintained converter's intermediate round trips are separately tested; they
do not certify the strict native Board files. The pilot does not alter the converter.

All observations are **synthetic**. The bounded test helper computes Variables,
scalar State comparisons, Test aggregation, and native nested Set/filter selection
from supplied observations. It acquires no resources and does not execute Object
selectors, filesystem traversal, registry access, or a general regex engine.
Provider lifecycle injection is labeled separately. No scanner equivalence or
live collector conformance is claimed.

The 30 case expectations were written from source/specification reasoning before
running the helper. Case-local `variant` is an explicitly authored mutation for
a negative/boundary test, not Organizational Input overriding publisher values.
All results are technical Assessment outcomes. A miscellaneous Assessment's
`true` is not a policy pass; no fabricated Benchmark/Rule wrapper is needed.

Run from the repository root with Python, PyYAML, lxml and jsonschema installed:

```sh
python tools/test_board_samples_v02.py
python tools/validate_native_json_schemas.py board/review-content/0.2.0/content --schema-dir schema/v0.2.0
python tools/check_current_authoring_contract.py board/review-content/0.2.0/content
python tools/assessment_results_v02.py --assessments board/review-content/0.2.0/content --result-set board/review-content/0.2.0/expected/unix-file.result-set.json
```

The commands also work on Windows; paths are short and no shell-specific fixture
setup is required. See [validation](validation.md), [review questions](questions.md),
and the [handoff](handoff.md). MITRE source notices are retained with the extracts;
the [source license](sources/MITRE-terms.txt) is copied from the pinned source.

## Required contents

The final sample set should contain:

- native-authored SCAP-NG Assessment examples;
- converted OVAL-backed examples with pinned provenance;
- independent expected results;
- concise per-sample review notes;
- validation commands/evidence;
- a manifest listing every included sample and the feature it demonstrates.

At least one sample should demonstrate a nontrivial reference/dependency path such as Variables, Sets, Filters, or another graph interaction. At least one should demonstrate Results/evidence that makes the reason for the outcome understandable.

## Design goals

Samples should be:

- small enough to review by hand;
- semantically representative;
- intentionally named;
- free of irrelevant benchmark bulk;
- usable later as canonical conformance examples after human acceptance.

Do not copy an entire benchmark into this directory merely to prove conversion works.

## Human acceptance gate

Codex may create and validate the pilot, but the directory is not considered an approved Board sample package until a human reviewer has examined the examples and their expected semantics.

When the pilot is ready for review, add a manifest with a per-sample status of `pending-review`. Human acceptance changes the status to `accepted`, with reviewer/date recorded.

See:
- `board/SCAP-NG-0.2.0-REVIEW-CHECKPOINT.md`
- `transition/codex-test-content-0.2.0-task.md`
- `MAINTAINING.md`
