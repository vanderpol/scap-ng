# Owner review: combined process selectors conflict with generated 0.4 schema

**BLOCKED; proposal only.** Approved schemas, mappings and generator are unchanged.
`unix.process58` remains unconfigured; affected content cannot enter verified
packages. This blocks completing the approved 51-mapping scope under
[#251](https://github.com/vanderpol/scap-ng/issues/251). Its hard boundary says:
“If schema and source semantics conflict, give a minimal real counterexample
and stop for owner decision.”

## Original evidence

OVAL-Community/SCAP-Self-Assertion at `e3538595c5083b9c34d937a81d319234df9bbfaa`,
`SCAP_1.4/OVAL_Test_Content/unix/unix-def_process58_test.xml`, SHA-256
`a75037bfabd721b0f6a8a64a4eb4079a8b3feeb63c09776390e8fa9eb4d2f720`.
The unchanged original and provenance are in
`tests/fixtures/v04-process-selector-conflict/`. All eight original Tests use
both selectors; the file passes original OVAL 5.12.3 XSD/Schematron assertions.

Test `oval:navy.navwar.niwcatlantic.scc.test:tst:1` references Object
`oval:navy.navwar.niwcatlantic.scc.test:obj:1`. Its source selectors are
`command_line operation="not equal">init` and
`pid datatype="int" operation="greater than">0`.
The generic converter preserves both:

```yaml
capability: unix.process58
object:
  command_line: {not_equal: init}
  pid: {greater_than: 0, datatype: integer}
require:
  items_found: one_or_more
  items_satisfying: every
  fields:
    command_line: {not_equal: init, values_found: one_or_more, values_matching: every}
```

The approved mapping explicitly lists selector alternatives `[command_line]`,
`[pid]`, and `[command_line, pid]`. Generated `oneOf` branches test required
fields without being mutually exclusive. The pair matches all three branches,
so all eight originals fail: “is valid under each of …”. Dropping a selector
changes collection meaning and is not an acceptable workaround.

## Concrete correction candidate, not applied

In `flat_object` in `tools/v04_capability_native.py`, keep `oneOf` and make each
direct alternative exact: forbid `set` and selector fields absent from that
alternative. The existing Set variant continues to forbid direct selectors.
The three process variants then accept each listed single and the pair.

The isolated equivalent lives only inside
`test_v04_process_selector_conflict.py`; it is never converter/compiler/admission
authority. It accepts the original pair and listed singles, and still rejects
unknown fields, Set/selector mixtures and explicitly incompatible pid datatype.
Replacing `oneOf` with `anyOf` was considered but would treat alternatives as
minimum sets and permit extra combinations in other mappings; it is not recommended.

The correction changes generated validation, not source operands, evaluation,
provenance, cardinalities or scanner behavior. Before admission it needs review
of all 100 generated contracts, an intentional generation-parity baseline update,
positive/negative tests and original-source/schema/compiler verification.
Neither this proposal nor passing structural checks establishes scanner parity.

Reproduce current rejection and the review-only candidate:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tools python -m unittest test_v04_process_selector_conflict -v
```

Both tests pass. **Decision requested:** authorize the exact-alternative generator
correction and reviewed parity-baseline update, or retain these eight valid
original cases as explicitly blocked. No dated human approval is recorded.
