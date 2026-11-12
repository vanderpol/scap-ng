# Issue #48 — 0.4.0 Variable-function decision matrix

This is the design record for the coordinated 0.4.0 amendment. The active
schema uses explicit recursive objects; the historical generic
`{function: {name, arguments, options}}` envelope remains inactive and is
never emitted.

## Authority

- Recursive `count` is owner-approved for active 0.4.0 by
  [SCAP-NG #60](https://github.com/vanderpol/scap-ng/pull/60).
- `arithmetic`, `split`, and `substring` use the bounded owner-approved
  contract in [SCAP-NG #10](https://github.com/vanderpol/scap-ng/issues/10)
  and its review packet.
- Issue #48 directs restoration of `begin`, `end`, and exact multi-component
  `unique`/`merge` semantics. The source contract is pinned OVAL 5.12.3;
  runtime/scanner equivalence remains a separate qualification gate.

## Active native forms

| Function | Native 0.4 shape | Source boundary | Status |
|---|---|---|---|
| `count` | `{count: expression}` | Exactly one source component in active corpus; integer result; duplicates count; empty success is zero; status is not coerced | Schema/converter qualified structurally; runtime unproved |
| `split` | `{split: {delimiter, value}}` | One string input; literal delimiter; preserve empty parts, order and duplicates | Restored; runtime unproved |
| `substring` | `{substring: {substring_start, substring_length, value}}` | One string input; signed 32-bit options and OVAL one-based boundaries | Restored; runtime unproved |
| `arithmetic` | `{arithmetic: {arithmetic_operation, values: [...]}}` | At least two numeric inputs; ordered Cartesian product; add/multiply; integer/float widening | Restored; source datatype blockers remain |
| `begin` / `end` | `{begin/end: {character, value}}` | One string input; prepend/append the complete character/string only when absent | Restored from pinned OVAL contract; source use is limited |
| `unique` | `{unique: expression}` or `{unique: [expression, ...]}` | Flatten ordered populations then remove later duplicates, preserving first occurrence and status | Multi-component widening is explicit |
| `merge` | `{merge: {delimiter, sort, order, values: expression|[...]}}` | Flatten ordered populations, preserve duplicates, then explicit join/sort | Multi-component widening is explicit |

The array forms are the smallest explicit collection composition that preserves
OVAL operand order and multiplicity without introducing a generic call envelope.
Existing one-expression forms remain valid.

## Deferred functions

`escape_regex`, `glob_to_regex`, and `time_difference` have no active source
uses in the 65-benchmark inventory and remain deferred. They are not silently
claimed equivalent or emitted by the converter.

## Rejected alternatives

- Generic function envelopes or hidden options.
- Replacing multi-component `unique` with `concat` or set union.
- Zipping arithmetic populations instead of Cartesian expansion.
- Treating schema validation as execution or scanner equivalence.
- Implicit datatype casts, default options, or status-to-value coercion.
