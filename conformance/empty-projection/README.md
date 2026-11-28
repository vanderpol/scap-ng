# Empty, absent and failed collected projections

This [Assessment](empty-collection.assessment.yaml) projects `full_path`
from a shared UNIX file Object and counts the produced values. The
[expectation manifest](expected.json) distinguishes a complete zero-Item
population from an absent collection, incomplete collection, explicit
collection failure, omitted Item field, empty field array and error field.

The current RI Test evaluator returns true for `count == 0` on the
complete empty population. Its separate Test requiring a value returns
false with zero observed values. The earlier RI rejected both with
`variable_empty_population_held`. Missing, failed, incomplete and
invalid field cases still receive their explicit diagnostics before a
technical Test outcome can be supplied. The empty field array and omitted
field retain different diagnostic identities.

The [receipt](ri-receipt.json) pins both RI revisions and the exact
Assessment and supplied fixture. Qualification covers this Test scope
through RI's public evaluator and the canonical `count` contract.
Actual file acquisition, whole-Assessment rollup and broader empty
status propagation remain open.

```sh
python conformance/tools/replay_empty_projection.py --check \
  --current-ri /path/to/current/pinned/scap-ng-ri \
  --prior-ri /path/to/prior/pinned/scap-ng-ri
```

- [Canonical count semantics](../../schema/variable-expression.schema.json)
- [RI scanner-neutral conformance](https://github.com/vanderpol/scap-ng-ri/issues/196)
