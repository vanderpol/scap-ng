# Semantic authoring negatives

These Assessments are well shaped under 0.4.1. Their source graph or usage
makes them semantically invalid. The [independent expected manifest](expected.json)
records each reason, the governing source and the current RI diagnostics.

The regression checks exercise a one-change control for each source defect.
They keep local graph reasoning and scanner execution separate. The standalone
RI evaluator reported the dangling reference and held the two other cases
without a specific authoring diagnosis.
