# Seven-workflow reconciliation — #251, 2026-10-24

Task authority: [coordination comment](https://github.com/vanderpol/scap-ng/issues/251#issuecomment-6390147990).
Started from clean, synchronized `main` at
`4f3ff7ac3278d9fe9d445fc8b6bbf1db6e684b6d`. The historical test partition and
pinned RHEL all_exist normalization were already implemented and were not redone.
No schema, production converter/upgrader/compiler, original source, existing test
assertion, editor or scanner code changed. No six-STIG regeneration or historical
replay was dispatched.

## Classification and evidence

**All seven workflows are mixed.** Their dated archive/ledger replay is
historical, while some assertions are genuine current production requirements.
The [auditable manifest](../../tests/ci/legacy-workflows.json) records each original
workflow Git blob and SHA-256 at source ref
`2de578c088291558f44d0c7a505ad149dea5fc76`, its complete original trigger paths,
called script hashes, artifact/release references, exact command digests and
mandatory assertion modules. Thirty-nine directly referenced scripts were
inspected, including importers/exporters, experimental builders/censuses,
validators, migration tools and their existing tests. Classification is based on
inputs and assertions, not filenames or the fact that a run failed.

| Original workflow / failed run | Historical portion and evidence | Current assertions retained as mandatory |
| --- | --- | --- |
| `v04-oval-constant-family-roundtrip.yml` / [40133633917](https://github.com/vanderpol/scap-ng/actions/runs/40133633917) | `convert_v04_oval_constant_family.py` emits `states` and scalar require; secondary research-C source view comes from artifact run 39344457603 | Pinned family XML, native schema, singleton omission, constant Variable binding, Item/field/value cardinalities, both independent reverse exporters, XSD/root graph, literal/cardinality mutations |
| `v04-oval-family-variable-roundtrip.yml` / [40133633876](https://github.com/vanderpol/scap-ng/actions/runs/40133633876) | Raw importer emits the same obsolete authored structure; fixed 3/167 cumulative ledger and historical predecessor artifact are not current ledger acceptance | Same original family source with current shared converter; schema/JSON/YAML, source var_check and checksum, native/source mutation guards, independent reverse proof |
| `v04-oval-multitest-leaf.yml` / [40133633843](https://github.com/vanderpol/scap-ng/actions/runs/40133633843) | Pilot emits `require.items`; replays old 44-candidate/2-certified-of-167 artifacts and ledger promotions | Both certified IOS/IOS-XE global sources, two flat Objects/Tests under AND, original selectors, source quantifier/operation negatives, native mutation differential, schema/XSD/graph/compiler |
| `v04-complete-boolean-preview.yml` / [40133633919](https://github.com/vanderpol/scap-ng/actions/runs/40133633919) | Experimental 4,001-document spelling candidate and temporary schema; all/and alias drift | Actual expression schema, Boolean six-state migration guards, Test/Item/State scope separation, source inverse and reference closure |
| `v04-state-alternatives-and-or.yml` / [40133633855](https://github.com/vanderpol/scap-ng/actions/runs/40133633855) | Dated artifact 39503111241, 123-Test candidate, fixed scope census; comparator/absence mismatch must fail closed | Apache compatibility/inverses, whole-State AND/OR, original Enterprise/EnterpriseS registry source, duplicates/group boundaries and negative semantics |
| `v04-flat-object-six-stig.yml` / [40133633807](https://github.com/vanderpol/scap-ng/actions/runs/40133633807) | Dated field-layout artifact 39593978798, 4,001-file preview, absence/comparator mismatch | Apache source fixtures, flat Object/hybrid YAML equivalence, inverse/collision/selector guards and native schema/compiler tests |
| `research-04-native-content-deep-validation.yml` / [40133633853](https://github.com/vanderpol/scap-ng/actions/runs/40133633853) | Immutable **0.3** authoring ZIP lowered by experimental census against 0.4; old States/scalar require, not current generated content | Reviewed enum literal lowering, nested Sets/type/identity, unknown/unverified values and Variables rejected loudly |

### Previously unclassified family failure

The actual public [job annotation](https://github.com/vanderpol/scap-ng/actions/runs/40133633876/job/120990438410)
identifies **“Validate current native 0.4 schema, Variable cardinality and
YAML/JSON”**, exiting with code 1. Reproduced that step against the original
Self-Assertion family source at revision
`e3538595c5083b9c34d937a81d319234df9bbfaa`, SHA-256
`6966982d66e004f77ceb9e5ccceb5161275a79729d4178f290f99efd3b8b84a7`:

```text
assessment/tests/system-family-matches-test/require [oneOf]:
'at_least_one_exists_and_some_match' is not valid under any of the given schemas
assessment/tests/system-family-matches-test [additionalProperties]:
Additional properties are not allowed ('states' was unexpected)
```

This is raw historical-importer output failing the current schema, not a new
failure of the current shared converter. Public annotations plus the local exact
validation reproduction establish the diagnosis; authenticated full hosted logs
were not available through this task's blocked API, and are not claimed read.

## Routing and preservation

The seven existing workflow files remain executable as **Historical manual**
`workflow_dispatch` jobs, with their original job bodies, source pins, negative
assertions, download references, failure exits and `if: always()` artifacts.
Repository policy additionally requires explicit `allow_historical: true` at
dispatch; its default is false and every historical job has that existing-style
opt-in guard. This does not change mandatory production execution.
Their own code/schema checkout is now pinned to the exact failing snapshot
`2de578c088291558f44d0c7a505ad149dea5fc76`; Python is pinned to 3.12.14.
The one formerly floating `jsonschema` installation in the deep census is pinned
to 4.25.1. No assertion was removed or rewritten and no failure is converted to
success. Command-hash tests verify this, allowing only that dependency pin.
`docs/repository-policy.json` records their historical-manual disposition.

No push/PR/schedule trigger remains on these dated replays. Their old red runs
and artifacts are preserved, not relabeled green. Historical Actions artifacts
may expire; manual reproduction may report an unavailable dependency rather than
reach the earlier dialect failure. No replacement artifact or successful replay
is fabricated. The old State-OR replay also retains its original mutable NIWC
download URL; the mandatory proof instead uses immutable checked-in original XML.

Current guards are retained/strengthened:

- Mandatory rebaseline continues to run **all current selected tests**, including
  RHEL normalization, original synthetic-does_not_exist counterexample, absence,
  registry AND/OR, upgrader/compiler/schema and negative semantic tests. Workflow
  changes now trigger that gate directly.
- Canonical fast CI explicitly runs the moved Boolean-schema/reference,
  State-boundary, enum and Apache tests; all also remain in the full mandatory
  discovery set. No historical-test partition exclusion was added or changed.
- Shared converter-core CI explicitly runs five new current-source tests from
  `test_v04_reconciled_workflow_sources.py`. Mandatory CI binds original family,
  IOS and IOS-XE global XML from the same immutable Self-Assertion revision.
- Three routing regressions verify seven manual/pinned replays, original command
  preservation, live source bindings and that every mapped current assertion
  method is outside the historical partition. New tests default into mandatory
  discovery under the existing routing invariant.

The test-only inverse view for retained independent reverse exporters is never
compiler input or current authoring. Current native documents validate first;
typed IR and `.scapng` compile only current structured require. No legacy schema
alias or weaker absence/comparator rule was introduced.

## Source-backed validation

| Original XML | Definition | SHA-256 | Compiled Tests |
| --- | --- | --- | ---: |
| `agnostic/ind-def_family_test.xml` | `oval:org.mitre.oval.test:def:95` | `6966982d66e004f77ceb9e5ccceb5161275a79729d4178f290f99efd3b8b84a7` | 1 |
| `ios/ios-def_global_test.xml` | `oval:navy.navwar.niwcatlantic.scc.ios:def:1` | `6015ddb9a1540fff61b7d8d6749a2bf6a1d309d823b40f53941e5ce6e488c7ec` | 2 |
| `iosxe/iosxe-def_global_test.xml` | `oval:navy.navwar.niwcatlantic.scc.iosxe:def:1` | `f88a4eea2858c07f76f6b03904cf6ce530a1e6b39bfc547589896dd586b0c87c` | 2 |

All use the existing production converter, current generic/generated capability
schemas, paired YAML/JSON, typed-IR reconstruction and native bundle verification.
Both independent family exporters and the IOS/IOS-XE exporter regenerate OVAL
from native operands; pinned OVAL 5.12.3 XSD and original semantic-root comparisons
pass. Changed Variable literals/selectors produce semantic inequality; changed
value_match/Test cardinalities, source quantifiers and unsupported operations are
rejected. Existing mature-lowering and source-mutation guards remain unchanged.

Bundle checks use an explicit synthetic minimal Benchmark/Rule policy wrapper
around each real converted Assessment: this is not whole-Benchmark migration.
Bundles are unsigned and `scanner_evaluated: false`. No conformance ledger is
silently promoted from its historical 2/3-of-167 counts.

Focused verification: **13 source/converter tests passed**, then **three routing
tests passed**, no skips. Dependencies: Python 3.12.14, PyYAML 6.0.3, jsonschema
4.25.1, lxml 6.1.1, cryptography 50.0.2. Workflow YAML parses; whitespace and
repository-preservation checks pass. Full mandatory and hosted results follow.

Reproduce from the repository root using the exact original-source bindings in
`.github/workflows/rebaseline-smoke.yml` (including the new IOS-XE global binding):

```bash
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH=.:tools:tools/scap_upconvert_v003:tools/scap_ng_roundtrip_v003
python -m unittest -v test_v04_reconciled_workflow_sources \
  test_scap_converter_core_family test_scap_converter_core_multitest \
  test_v04_workflow_reconciliation
python tools/run_current_tool_regressions.py --report /tmp/current-reconciled.json
```

Local Python executable: `/workspace/.onboarding/rebaseline-venv/bin/python`.
The full mandatory run passed **2,906 tests, zero failures/errors, one unchanged
optional research-corpus skip**, in 145.594 seconds (prior baseline: 2,898 /
zero failures/errors / one skip). The eight added methods are five source tests
and three routing tests. Selection comparison reports **zero missing baseline
IDs**, the same 181 historical methods, and **100 mapped production assertion
methods** still mandatory. After adding the required historical-dispatch guard,
all three routing tests passed again and the repository preservation audit passed.
No historical-test exclusions, original XML or existing test assertions changed.

No new semantic decision or external authorization was required. Remaining true
release gates are source/capability coverage, separately authorized whole-package
acceptance, production signing/trust, release reproducibility/documentation and
scanner/collector acceptance. This task does not declare release readiness.
Issue writes remain unavailable (`Post "https://api.github.com/graphql": Forbidden`);
this committed report is the authorized handoff.
