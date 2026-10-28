# Maintained regression timing review — 2026-10-28

Engineering execution evidence for [#251](https://github.com/vanderpol/scap-ng/issues/251).
This is a performance investigation, not a new semantic contract or a workflow
change. No tests were rerun or removed to produce this profile.

## Measured baseline

Exact commit: `f789583e6bc5bebebaae6c00b7a3d790d9cefbbb`.
[Run 40719820070](https://github.com/vanderpol/scap-ng/actions/runs/40719820070),
job `122927340809`, completed successfully on 2026-10-28.
The unittest runner reports **3,253 tests in 853.508 seconds**, zero failures,
zero errors, one existing skip (3,252 passed). The historical partition contains
181 tests and was not executed as current coverage. All ten workflows triggered
for this commit passed.

GitHub step timestamps show 857 seconds in maintained regressions and 889
seconds for the entire job. Dependency installation took three seconds; the
initial checkout took fourteen seconds. Dependency caching alone therefore
cannot explain or remove most of the current runtime.

The verbose log has 3,239 identifiable single-line test records. The longest
intervals between consecutive such records are approximately 297 seconds near
the whole-benchmark proof/compiled-operand test, 104 seconds near the authoring
style/benchmark boundary, 35 seconds near the audit-policy/authoring boundary,
and 33 seconds within the benchmark group. These are **localization clues**,
not precise per-method CPU times: class setup/teardown, multiline records and
log buffering can be attributed to an adjacent test. Do not sum them into a
claimed speedup or treat them as an exhaustive per-test profile.

## Source inspection and safe next experiments

1. `test_v04_direct_benchmark.py` invokes `verify_compiled` three times on the
   same unchanged positive documents/bundle in one method. Measure that call
   directly and, if material, reuse its positive result within that method.
   Retain the independent verifier, original 249-Rule proof count, mismatch
   coverage, and separate corrupted-program/bundle rejection tests. Do not cache
   results across mutated documents or convert a negative test into a cache hit.
2. Several test classes separately parse and convert the same pinned Server
   2025 source. Measure fixture setup separately from test methods before
   considering shared immutable fixture construction. Mutant tests must receive
   isolated copies. Source hashes, mapping/schema content, conversion options,
   and tool revision must participate in any persistent cache key. Keep source
   and native semantic readers independent; cached converter output cannot
   substitute for independent source verification.
3. Independent test modules are candidates for **process**, rather than thread,
   isolation. Before adoption, audit fixed output paths, environment variables,
   global caches and filesystem mutations; compare selected/executed IDs,
   failures, errors and skips with the serial runner; and check peak memory.
   Balance by measured class/module cost rather than test count. Class fixtures
   and tests with ordering/shared-state assumptions stay together.
4. The existing pinned-source and six-benchmark workflows already run alongside
   the maintained job. Preserve their separate proof obligations. Reuse existing
   exact-commit runs instead of dispatching redundant copies. Do not run the
   release-only 65-benchmark corpus for this investigation.

No concurrency, required checks, test selection, historical partition, CI
workflow, cache, or validator was changed in this checkpoint. Adopting protected
workflow changes requires owner direction under the standing workflow policy.
