# Converter pilot validation evidence

Date: 2026-10-04. Status: **local validation passed; human review pending**.

Starting checkout: clean `/workspace/scap-ng`, `main`,
`345d8de7436adbba15cf0fe546684dbc4ba8ef5d`. The existing 12-test Board regression was
reproduced before changes. That commit's schema/specification and converter core
remain unchanged. Frozen technical baseline:
`7cd8b1242d7fb4a2eb9b5f49c7ec3f48b2dd622d`. Current maintenance was retained.

Self-Assertion was accessible: local HEAD and GitHub commit API both verify
`e3538595c5083b9c34d937a81d319234df9bbfaa`, tree
`d0b680aa781cde9e55ad8778b71ee82da37ebab3`. Six selected whole-file hashes are checked
against exact pinned Git blobs. Working files may differ only in platform checkout
newlines; source identity/hashes are never weakened. Extracts preserve original
nodes, notice text and exact criterion scope, with complete dependency closure.

| Check actually run locally | Result | Evidence limit |
| --- | --- | --- |
| Existing Board regression before implementation | 12 tests passed | Earlier seven-file/manual pilot baseline, not proof of the new converter path |
| Eight maintained promotion/semantics/authoring/existence/truth-table/conditional/results/Variable-filter modules | 176 tests passed | Current frozen regression surface, rerun during this pilot |
| Existing lower → reverse/comparator → align → ready mappings → explicit case mappings | 6/6 selected source closures pass intermediate parity and strict mapping | Case-scoped existing APIs; no broad file/registry readiness claim |
| Reproducible conversion CLI with `--source-root ... --check` | 6/6 committed pairs identical | Exact pin/full-file/closure verification; no expected outputs generated |
| Board conversion regression | 8 tests passed | Actual regenerated artifacts, repeated conversion, unrelated-source/reordering stability, reference/selector contracts, provenance, naming reproducer, independent mechanical/native oracles |
| Board semantic regression | 12 tests passed, 48 independent cases | 31 primary plus 17 supporting synthetic expectations; scalar/record/Variable/Set/scheduling slice only |
| Strict 0.2.0 schema CLI | 6 mechanical + 10 native documents valid; no unclassified documents | No legacy bridge or relaxed validation |
| Capability semantic checks and authoring contracts | Both forms pass | Source presentation is not scanner equivalence; local dataflow separately guarded |
| Source XSD checks | 8 Board extracts plus new minimal naming closure pass | XML structural validity, not a claim that all upstream content is semantically valid |
| Source-aware linked UNIX Result validation | Pass | Structure, references, comparison lineage and recorded scheduling; observations remain synthetic |
| Final maintained unittest discovery | 795 tests passed | Repository smoke includes all 20 bounded pilot tests |
| Repository layout audit and authored-file whitespace checks | Pass | Existing review boundaries preserved; no parallel review repository/tree |

Focused commands (existing Python environment was used):

```sh
python tools/convert_board_pilot_v02.py --source-root /workspace/scratch/self-assertion-e353 --check
python tools/test_board_conversion_v02.py
python tools/test_board_samples_v02.py --report work/board-pilot-validation.json
python tools/validate_native_json_schemas.py board/review-content/0.2.0/mechanical --schema-dir schema/v0.2.0
python tools/validate_native_json_schemas.py board/review-content/0.2.0/content --schema-dir schema/v0.2.0
python tools/check_current_authoring_contract.py board/review-content/0.2.0/content
python tools/assessment_results_v02.py --assessments board/review-content/0.2.0/content --result-set board/review-content/0.2.0/expected/unix-file.result-set.json
python tools/audit_repository_layout.py --check
```

The adapter can write reproducible pairs with `--output work/board-conversion`.
It never writes expected tables. Mechanical and native graphs compare equal after
normalizing only explanatory titles and the two accepted Constant literal forms.
Independent expectations include correlated-record false versus true, numeric zero,
missing/uncollected fields, duplicate Variable values under `one`, negative symlink
leaves, collection errors, absence and incomplete populations. Pure source cases and
native fixture variants remain distinguishable.

Baseline/smoke commands:

```sh
python -m unittest tools.test_schema_v02_promotion tools.test_validate_generated_capability_semantics tools.test_current_authoring_contract tools.test_ng_existence_semantics tools.test_oval_result_truth_tables tools.test_conditional_integration tools.test_assessment_results_v02 tools.test_variable_filter_dependencies
python -m unittest discover -s tools -p 'test_*.py'
```

For discovery, set `PYTHONPATH` to `tools`, `tools/scap_upconvert_v003`, and
`tools/scap_ng_roundtrip_v003` using the OS path separator. Direct pilot commands
work on Linux and Windows without shell-specific fixture setup.

CI integration is the existing **Current-design regression contracts** matrix,
Ubuntu and Windows. Both jobs checkout the exact pinned Self-Assertion source,
reproduce just six conversions, compare committed bytes, validate both forms and
run both focused modules. The uploaded Board receipt records the exact tested HEAD
and tracked-working-tree state; it does not label an uncommitted local run as
commit-only certification. Rebaseline smoke discovers the added tests; the
maintained fast-five integration remains the small benchmark gate. Publication
commit and exact run URLs are reported to the user after CI completes.

The earlier manual/native pilot at `d720d2c4103450f48574bf7f8adf2f2539cdfb68` had 30
independent cases and 787 smoke tests. Its meaningful-ID revision at
`345d8de7436adbba15cf0fe546684dbc4ba8ef5d` passed Ubuntu/Windows, smoke and fast-five CI.
Those are historical baseline evidence. New converter verification is recorded
above and in the publication CI receipt; earlier manual output is not reclassified
as mechanically converted without running the actual converter.

Four minimal reproducer groups are documented in questions.md and
`tests/focused-regressions/board-pilot/`. New naming correction is presentation
only, scoped to the six-case source-ID plan. Shared semantic validators, production
conversion logic/readiness and versioned schemas were not changed.

No 0.2.0 schema semantics, specification behavior, converter capability rename or
architecture was changed. No deprecated Test, ESX/deferred Kubernetes work, editor,
full STIG conversion, or **65-benchmark NIWC run** was performed. No live collector,
independent scanner/evaluator, signing/trust pipeline or exhaustive language
conformance was run. Schema validity alone is never claimed as scanner equivalence.
