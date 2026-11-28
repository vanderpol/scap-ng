# Pinned OVAL external Variable witness

[Definition 562 and its companion binding file](expected.json) come from
the same pinned OVAL Self-Assertion archive. The replay independently
reads both source members and checks the source State comparisons and
Input restrictions. It also verifies that the current converter preserved
each Test and Variable identity, Input datatype, required cardinality,
allowed values and regex alternatives. The binding values are passed to
RI at evaluation time through the public evaluator context.

All 18 Test leaves returned true. Eleven bindings had one value and seven
had four. Separate integer controls exercised missing, explicitly empty,
wrong-type and valid nonmatching bindings. Missing and invalid bindings
returned diagnostics through the direct Test API. The valid nonmatching
binding returned false. Benchmark policy enforcement, Assessment rollup
and the general converter parity checker retain separate qualification.

```sh
python conformance/tools/qualify_external_input_fixture.py --check \
  --self-assertion /path/to/pinned/SCAP-Self-Assertion \
  --converted /path/to/converted/definition-562 \
  --ri /path/to/pinned/scap-ng-ri
```

- [RI replay receipt](ri-receipt.json)
- [SCAP-NG Input operand contract](../../docs/contracts/0.4.1-input-variable-expression.md)
- [Tools parity audit gap](https://github.com/vanderpol/scap-ng-tools/issues/128)
