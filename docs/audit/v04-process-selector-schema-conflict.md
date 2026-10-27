# Owner review: combined process selectors conflict with generated 0.4 schema

**Owner-approved correction, 2026-10-27.** The owner authorized exact selector
alternatives in `flat_object`, retained `oneOf` and Set/direct restrictions, and
required all-100 contract review and original-source/compiler/regression gates.
Normative schemas, mappings, original XML, compiler and scanner behavior remain
unchanged. All eight original process cases now validate, compile and independently
prove; `unix.process58` uses the existing scalar visitor/proof contract. Remaining
whole-assignment verification is recorded in the engineering ledger under
[#251](https://github.com/vanderpol/scap-ng/issues/251). The original hard boundary was:
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
fields without being mutually exclusive. Before correction the pair matched all
three branches, so all eight originals failed: “is valid under each of …”. Dropping a selector
changes collection meaning and is not an acceptable workaround.

## Approved correction and preserved scope

In `flat_object` in `tools/v04_capability_native.py`, keep `oneOf` and make each
direct alternative exact: forbid `set` and selector fields absent from that
alternative. The existing Set variant continues to forbid direct selectors.
The three process variants then accept each listed single and the pair.

The isolated equivalent is retained inside `test_v04_process_selector_conflict.py`
and agrees with the active generator. It accepts the original pair and listed singles, and still rejects
unknown fields, Set/selector mixtures and explicitly incompatible pid datatype.
Replacing `oneOf` with `anyOf` was considered but would treat alternatives as
minimum sets and permit extra combinations in other mappings; it is not recommended.

The correction changes generated validation, not source operands, evaluation,
provenance, cardinalities or scanner behavior. The completed
[all-100 review](v04-exact-selector-contracts.md) and [machine audit](v04-exact-selector-contracts.json)
explains each expected difference: ten contracts change only direct-alternative
prohibitions, 90 are byte-identical, and all Set branches are unchanged. The parity
lock updates only those ten hashes. Positive/negative tests and all eight original
source/schema/compiler proofs pass. Mandatory verification passes 3,155 tests with
zero failures/errors and one existing skip; three new retention guards pass
separately, accounting for all 3,158 current identities.
Neither this proposal nor passing structural checks establishes scanner parity.

Reproduce the retained legacy rejection and approved correction:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tools python -m unittest test_v04_process_selector_conflict -v
```

Three tests pass, covering the original legacy rejection, all eight corrected
original cases, listed single forms, exact file alternatives and Set/direct
exclusions. The dated owner approval is recorded above; no further schema approval
is required for this bounded correction.
