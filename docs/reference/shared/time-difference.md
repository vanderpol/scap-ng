# Active `time_difference` expression — SCAP-NG 0.4.1

`time_difference` is an active native Variable expression, not the inactive
`variable-function-expression` envelope. Its result datatype is `integer` and
its unit is seconds.

```json
{
  "time_difference": {
    "values": [
      {"literal": "2009-02-04"},
      {"literal": "2004-02-04"}
    ],
    "format_1": "year_month_day",
    "format_2": "year_month_day"
  }
}
```

`values` has one or two expressions. With two, the result is first minus
second. With one, the result is current UTC minus the explicit operand.
Missing formats default to `year_month_day`; the one-operand form uses
`format_2` for its explicit operand. Supported formats are
`year_month_day`, `month_day_year`, `day_month_year`, `seconds_since_epoch`,
and `win_filetime`. Multiple operand values use source order and bounded
Cartesian products. Invalid lexical values, range failures, missing or
incomplete collected evidence, and acquisition errors remain errors/unknown;
they are never coerced into a value.

The active schema contract is in
[`schema/variable-expression.schema.json`](../../../schema/variable-expression.schema.json).
The inactive generic call schema remains intentionally unreferenced.

Qualification uses the pinned OVAL 5.12.3 Self-Assertion
`oval:org.mitre.oval.test:def:580` and is recorded in the RI repository's
`docs/qualification/issue59/time-difference-20261115/` receipt. The receipt
proves converted RI execution, not independent equivalence to an OVAL
interpreter.
