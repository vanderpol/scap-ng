# Focused regression fixtures

This directory is for **small, permanent reproducers** of schema, conversion, semantic-validation, evaluator, compiler, and result-model defects.

The purpose is fast, understandable iteration. A large STIG or the 65-benchmark NIWC corpus is not an acceptable first-line reproducer.

## Rule for adding a fixture

Each fixture SHALL include:

- a short issue identifier/name;
- the smallest source/native content that reproduces the behavior;
- an independently stated expected result or expected diagnostic;
- the defect category:
  - source content defect;
  - converter defect;
  - schema/model defect;
  - semantic-validator defect;
  - evaluator/test-harness defect;
  - collector/platform limitation;
  - unresolved specification question;
- the command/test that exercises it;
- provenance back to the original source case when one exists.

Keep fixtures human-readable and avoid generated bulk content.

## Workflow

1. Find a failure in real or synthetic content.
2. Reduce it here.
3. Confirm the reduced case still fails for the same reason.
4. Fix the implementation or raise the semantic question.
5. Keep the reduced case as a permanent regression.
6. Use the fast integration lane for broader confidence.
7. Use the 65-benchmark corpus only at an intentional deliverable/review checkpoint.

A focused reproducer is preferred over repeatedly re-running a large benchmark while diagnosing one semantic issue.
