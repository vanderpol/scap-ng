# Input admission and policy selection

The [numeric Assessment](typed-policy.assessment.yaml) accepts a supplied
integer when either the legacy value list or the inclusive predicate
matches. The [invocation cases](expected.json) distinguish an omitted
optional Input from a supplied empty list. Both the first and later values
must pass validation. Admitted populations produce a known Model A
comparison or take the authored missing-Input fallback. The manifest
records admission failures before Test execution and makes no claim about
their later Result projection.

The [string Assessment](string-predicate.assessment.yaml) provides the
source for schema mutations at 4,096 and 4,097 characters. The numeric
Assessment supplies the Boolean predicate mutations at 0, 64 and 65
branches. These are authoring controls drawn from the
[Input contract](../../docs/contracts/0.4.1-input-variable-expression.md#typed-input-constraint-expressions).

The [selection cases](selection-expected.json) reuse the canonical
Benchmark and Tailoring. They cover default selection with no Profile,
switching between two independent Profiles, and applying one disjoint
Tailoring override to a selected Profile. The decision on independent
Profiles and the rejection of native Profile inheritance are recorded in
[Issue #73](https://github.com/vanderpol/scap-ng/issues/73). All expected
sets concern Rule selection. Applicability and Assessment outcomes are
separate stages.
