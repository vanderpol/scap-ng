# SCAP-NG v0.4.0 — working schema draft

**Pre-alpha draft, not accepted or Board approved.** The v0.3.0 schemas are unchanged.

This directory is a complete physically independent version-local copy-forward of the 0.3 schema and capability mapping surface. Versioned metadata, IDs and references identify v0.4.0; each unchanged file preserves its substantive modification date.

## Draft Assessment grammar

- A single versioned authoring grammar: no mixed legacy `field:/value:/operation:/existence:/match:` State forms.
- Every Test explicitly declares `require:`; State-free and State-bearing Tests have separate valid requirement names.
- State fields use observed field keys, e.g. `- owner_uid: {equals: 0, require: at_least_one_exists_and_all_match}`.
- Exactly one comparison operation per scalar predicate; arrays, Variables and Organizational Input references retain explicit `value_match` and datatype requirements.
- Windows record and nested field requirements are distinct. Object Set filters use `include:` or `exclude:` on a field-key predicate.
- `evaluate`, `for_each`, typed Variable graphs, manual choices and collected Items/results do not acquire new semantics.

## Promotion gates still open

Capability-specific Object selectors, WMI/cmdlet `selection_match`, list edge cases, strong scope/type validation, an independent strict 0.4 validator, positive and negative fixtures, migration lowering and six-valued reference parity still need completion. 0.3 compilation/validation is **not** asserted to implement 0.4. Variable source-module imports and variable debug graphs are separate [research #223](https://github.com/vanderpol/scap-ng/issues/223), **not** adopted language features.

See [0.4 scope and release gates](../../research/assessment-simplification/compact-authoring-04/0.4-SCOPE-AND-RELEASE-GATES.md), [issue #227](https://github.com/vanderpol/scap-ng/issues/227) and [variable research #223](https://github.com/vanderpol/scap-ng/issues/223).
