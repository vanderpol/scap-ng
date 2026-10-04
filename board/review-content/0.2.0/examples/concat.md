# Concat: Cartesian values and nested quantifiers

Compare [selected source](../sources/concat.xml), [Assessment](../content/concat.assessment.yaml),
[provenance](../provenance/concat.json), and [expectations](../expected/concat.json).
Human status: **pending-review**. Provenance: Inherited selected criterion.

Scope: only criterion `oval:org.mitre.oval.test:tst:722` within Definition
`oval:org.mitre.oval.test:def:65`. The other three concat criteria are not claimed
to be covered. The extract retains the selected criterion's complete closure.

Before: Test → Object `obj:793` → local Variable `var:885` → concat of `var:443`
and `var:711`; State `ste:796` compares with expected Variable `var:322`.
After: `test-combined-values → combined-values → concat(prefixes, suffixes)` and State `matches-one-expected-value`
compares with `expected-combinations`. The direct Test removes only the Variable Object wrapper.

| Prefix | Suffix | Derived value |
| --- | --- | --- |
| abc | 123 | abc123 |
| abc | 456 | abc456 |
| def | 123 | def123 |
| def | 456 | def456 |

Concat produces the Cartesian product, not a zip of corresponding positions.
For **each** produced value, `variable_match: one` requires exactly one match in
the expected four-string set. State `match: all` then requires every produced
value to satisfy that comparison. The source Test's `check: any` combines Items;
it does not replace this inner `all` across the Variable Item's value entities.

The published case is true. Replacing `def` with `xyz` yields two matches and two
nonmatches: the Assessment is false, even though some derived values are correct.
The zero-value case is a separate native edge variant: `prefixes` becomes a local
Variable extracting `name` from a named exact-file Object whose collection
confirms absence. No Items means zero extracted values; concat produces zero
values, and the direct Test errors before comparison. It does not assume an
empty authored constant is valid or that the published constants resolve empty.
The complete variant graph and synthetic absence record are in the expectation
file. These are explicit authored variants with independently reasoned expectations.
