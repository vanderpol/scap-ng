# Pinned OVAL merge witness

Definition 38 contains four Test leaves over homogeneous integers and
simple ASCII strings. The [oracle](expected.json) records the source
sequence, sort and delimiter, and the independently calculated string.
The production conversion and direct RI evaluation use the exact source
and manifest hashes in the [receipt](ri-receipt.json).

Reordering the same integer values preserves the natural-sort result and
changes the document-order result. Both controls ran through the actual RI
evaluator on the converter's Assessment with just the input order changed.

```sh
python conformance/tools/qualify_merge_fixture.py --check \
  --self-assertion "$SELF_ASSERTION_CHECKOUT" --converted "$CONVERTED_DEFINITION_DIRECTORY" \
  --ri-evaluate "$RI_EVALUATE" --ri-revision f39ac725b820353e6f6b8fc71af673c08857d895
```

This bounds the evidence to the pinned Definition's sorted and ordered
sequence comparisons. The general parity checker still requires a
recursive source-backed comparison for merge options and operands.
Full Assessment scheduling and mixed datatype or locale behavior remain
unqualified. [Tools #128](https://github.com/vanderpol/scap-ng-tools/issues/128).
