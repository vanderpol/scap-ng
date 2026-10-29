# Closed identity enum selector recovery

Continuation of [converter #251](https://github.com/vanderpol/scap-ng/issues/251)
from fully verified `24889577233c6a75e739676adffe8f676a0f9f3b`.
[Machine-readable retention receipt](v04-identity-enum-selector-recovery-20261029.json).

The failed session's uncommitted enum/diagnostic batch and stash object were
absent in this workspace. This reconstructs its bounded identity-domain enum
selector behavior from pinned original sources. It does not claim recovery of
the old patch or restore unrelated diagnostic changes.

## Original cases and existing contract

Original Self-Assertion AppCmd Test
`oval:navy.navwar.niwcatlantic.scc.test:tst:101` selects `identifier_type`
through local string Variable `var:101`, whose literal is `Apppool`.
AppCmdListConfig Test `oval:navy.navwar.niwcatlantic.scc.test:tst:301` similarly
uses local Variable `var:301`, whose literal is `Site`. Both files are pinned
at Self-Assertion `e3538595c5083b9c34d937a81d319234df9bbfaa`.
The [new original fixture pin](../../tests/fixtures/v04-direct-enum-selectors/provenance.json)
and existing Windows acquisition provenance retain their exact bytes.

These strings already belong to the same source/native selector domains.
Previously the converter accepted direct literals/constants but rejected a
named local Variable reference before inspecting its complete closed graph.
The generic validator now admits only existing string literal, Variable-reference
and `unique` forms whose complete leaves belong to the declared enum domain.

The native selector still references the original named Variable. Names,
declarations, duplicate constant values, shared references, graph structure and
`var_check` remain unchanged; no clone, rename, constant folding or new function
is emitted. Original dependency IDs and hashes remain in existing provenance.
This is implementation of existing syntax/contracts, not a new grammar or a
decision about arbitrary runtime enum strings.

Arbitrary computations, Object-derived strings, casts, unknown values, external
bindings, cycles and unsupported selector comparators stay rejected. Equality
over a closed identity domain needs no alias projection. Reusing the renamed
enum-copy path would unnecessarily change identities; accepting arbitrary string
Variables would lose the domain guarantee. Neither alternative is used.

## Verification

40 focused/affected tests pass with zero failures/errors/skips. Positive fixtures
validate under the original XSD/Schematron, remain nondeprecated, compile with
independently checked operands and match the unchanged independent typed-term
reader. Controlled graph cases cover references, duplicate values, `unique`
and all four Variable quantifiers. Unknown values/casts/computed graphs and
cycles fail closed; mutated native enum values/quantifiers fail independent
comparison. All 100 generated capability contracts retain parity.

The complete byte-pinned conformance probe has **523 compiled and independently
proved Tests out of 713 configured / 803 original**. All **521** previous
configured proofs retain their authoring, source-term, native-term and compiled
program hashes. Exactly the two original Tests above are added; zero mismatches.
These are synthetic single-Test conformance Assessments, not production Rules
or scanner execution. Original closure validity for both additions is separately
checked by the focused tests.

The affected six-source primary gate retains **all 1,072 current program hashes**
and identical outcomes: 324 blocked automated and 171 manual/OCIL-only Rules.
It also enforces the pinned 1,055-program floor. No new primary production Rule
is claimed for this change. Schemas, mappings, compiler, independent readers,
scanner/editor, protected workflows and production `all_exist` are unchanged.

Reproduction:

```sh
PYTHONPATH=tools python -m unittest test_v04_direct_identity_enum_selectors \
  test_v04_direct_enum_variables test_v04_acquisition_source_proof \
  test_v04_windows_acquisition_source_proof test_v04_direct_registry_hive \
  test_v04_converter_contracts test_v04_native_schema_generation -v
PYTHONPATH=tools python tools/audit_v04_oval_test_corpus.py \
  --source-root PINNED_OVAL_TEST_CONTENT --output NEW_CORPUS_REPORT.json
PYTHONPATH=tools python tools/verify_v04_direct_scope.py \
  --inputs ORIGINAL_SIX_ZIP_DIRECTORY --output NEW_EVIDENCE_DIRECTORY
```

An initial focused invocation used a nonexistent registry module name and
reported one import error; the corrected final invocation above passes.
Large reports are in `/workspace/recovery-20261028/`, not source Git.
Exact-commit hosted integration is the next gate; preceding green evidence at
`248895772` does not by itself verify this implementation.
