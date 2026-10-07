# Windows Server 2025 event-log path family

**Status:** research only; no schema or converter contract change.

## Production family

Pinned Windows Server 2025 V1R1 content contains three automated Rules with the
same semantic graph:

- SV-278043 — Application event log;
- SV-278044 — Security event log;
- SV-278045 — System event log.

After normalizing only the event-log name and the three STIG control IDs, the
complete converted Assessment documents are structurally identical.

Each Assessment contains:

- 6 Objects;
- 2 Variables;
- 5 States;
- 3 Tests;
- Variable functions: 2 `regex_capture`, 3 `values`, 1 `concat`;
- the same complementary two-branch Boolean evaluate shape.

The family is therefore one useful stress test, not three independent language
problems.

## What locality already removes safely

The current locality work can present all five States at their consumers:

- the `%SystemRoot%` predicate beside its registry Test;
- the four allowed-trustee predicates beside each Set Filter that uses them.

The two file-rights source Objects are single-use filtered Set operands, so the
filtered-Set locality experiment can also colocate them inside their respective
permission Sets without moving or changing the Filters.

Those changes are presentation-only and are guarded by mechanical re-expansion
to the faithful source graph.

After those locality steps, the meaningful named acquisition/dataflow core is
approximately:

1. registry Object for the configured event-log path;
2. registry Object for `SystemRoot`;
3. direct/strict path Variable;
4. expanded-`SystemRoot` path Variable;
5. the three Tests and their existing Boolean evaluation.

That is already much smaller than the faithful top-level registry of
Objects/States.

## Remaining Variable boundary

The first Variable wraps the configured registry value in
`regex_capture('^(.*)$')`. It looks identity-like, but automatic removal is not
yet claimed because the exact regex/status behavior must be proven, including
non-matching/error cases.

The second Variable concatenates:

- values collected from the `SystemRoot` registry Object; and
- a regex capture from the configured event-log path.

Both operands can be collection-valued. This is **not** the proven unary-concat
`foreach` class. Generic concat can create a Cartesian product, so the current
modernizer must leave this graph explicit.

The apparent intent is environment-variable expansion, but intent is not enough
for a lossless converter rewrite. A future typed Windows path/environment
primitive would require its own semantics and counterexamples.

## Conditional boundary

The evaluate tree is the familiar:

`(strict-path AND NOT uses-SystemRoot) OR (built-path AND uses-SystemRoot)`.

That is clear human intent, but the existing six-state proof still applies:
ordinary OVAL Boolean aggregation is not generally equivalent to lazy
if/else execution. Faithful conversion therefore keeps the Boolean graph unless
a declarative shorthand is defined as exact desugaring.

## Current conclusion

This family does **not** currently justify another broad language feature.

Consumer-local States plus filtered-Set Object locality remove most of the
presentation burden. The two remaining Variables are real dataflow and should
stay explicit until a narrower equivalence proof or a deliberately native
Windows path-expansion contract exists.

This is positive evidence for the emerging 0.3 direction:

> localize graph plumbing first; add a new construct only when the remaining
> semantic operation is both common and precisely specified.

Reproducible analyzer: `tools/analyze_windows_eventlog_family.py`.
