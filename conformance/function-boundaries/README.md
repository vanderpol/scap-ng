# Variable function boundaries

[Function cases](function-boundaries.assessment.yaml) use literal inputs so
each population can be checked independently against the
[expected manifest](expected.json). Retain the order and multiplicity of the
Cartesian products, the first occurrence of each distinct string, and the
present empty strings produced by split, substring, and capture. The
Assessment uses a count and membership test for multiplication. For strings,
an explicit document-order merge makes order and empty elements visible to
the Test's exact equality check. The independent manifest retains each
pre-merge population.

[The native expression schema](../../schema/variable-expression.schema.json)
defines these forms and the inherited OVAL behavior. The OVAL 5.12.3
[definitions schema](https://github.com/OVAL-Community/OVAL/blob/2f140ee5c5dd1ed9606fcd5afc301f6baeb48706/oval-schemas/oval-definitions-schema.xsd)
documents the referenced function types. Capture cases use a small common
subset of regex syntax. A complete regex dialect contract remains open in
[Issue #62](https://github.com/vanderpol/scap-ng/issues/62).

The separate [substring range case](substring-out-of-range.assessment.yaml)
uses valid authoring with an out-of-range start. Its expected expression
status is error. The outcome of the full Assessment is held pending a
native propagation rule. Four invalid authoring controls exercise the
signed parameter bounds, operation vocabulary and minimum operand count.
