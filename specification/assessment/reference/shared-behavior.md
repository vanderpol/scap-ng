# Shared assessment behavior

**Status:** guide to maintained working contracts, not a separate truth-table
definition. Base capability authoring is 0.1.0; conditional expressions and the
additional reporting/result features described below belong to draft 0.2.0.

## Assessment graph and validation

An automated Assessment contains named Objects, Variables, States, Tests, and
an `evaluate` expression as needed. An Object selects/acquires resources; its
runtime Collection produces Items and collection status. A State compares
typed Item fields. A Variable produces typed values. A Test consumes the source
kind defined by its capability and optionally compares States. Some capabilities
consume a Variable directly or require no resource source.

Where present, Test, Object, and State capability declarations are independently
validated. A reference does not inherit or overwrite the referenced node's
capability. Resolve references before execution, independently of mapping key
order, and reject incompatible references and static dependency cycles. Draft
0.2.0 validates unselected conditional branches and unused declared dependencies
too; an invalid branch is not valid content merely because execution skips it.

The maintained contracts are [Assessment Method](../assessment-method.md),
[current authoring decisions](../../../research/iterations/003/design/CURRENT-DESIGN.md),
and [evaluation semantics §§1, 10.1](../../../research/iterations/003/design/assessment-evaluation-semantics.md).

## Existence, comparison, and quantifier scopes

For an Object-backed Test, collection status and resource existence are resolved
before State satisfaction. A missing-resource result cannot be repaired by a
favorable State comparison. Without States, the Test checks existence only.

| Native property/value | Role | OVAL-derived correspondence |
| --- | --- | --- |
| Test `existence: all` | Every identified resource must exist, subject to collection status | `all_exist` |
| Test `existence: some` | At least one resource must exist | `at_least_one_exists` |
| Test `existence: none` | No resource may exist | `none_exist` |
| Test `existence: one` | Exactly one resource must exist | `only_one_exists` |
| Test `existence: optional` | Existence is optional under the inherited status table | `any_exist` |
| Test `match: all/any/one/none` | Combine per-Item State satisfaction | `all/at least one/only one/none satisfy` |
| Test `states_match` | Combine multiple States for one Item | Test `state_operator` |
| State predicate `match` | Combine corresponding Item entity instances | `entity_check` |
| State predicate `variable_match` | Combine comparisons against Variable values | `var_check` |
| State predicate `existence` | Check corresponding entity existence/status | State entity `check_existence` |

These are separate scopes. For each Item entity, compare against Variable values,
combine those rows with `variable_match`, then combine corresponding entities
with predicate `match`. Combine predicates within a State, States within an
Item, and finally Items within a Test. Reordering those stages can change results.

`optional` is not another spelling of `some`: the inherited existence table
can permit zero existing resources. Error/unknown status and incomplete
population effects require the full tables rather than Boolean counting.
See [evaluation semantics §§3–5, 8–9, 14–15](../../../research/iterations/003/design/assessment-evaluation-semantics.md)
and [truth-table regressions](../../../tools/test_oval_result_truth_tables.py).

## Technical results and conditional execution

Technical results distinguish `true`, `false`, `error`, `unknown`,
`not_evaluated`, and `not_applicable` in the draft expression/result serialization.
Legacy semantic prose may spell the last two with spaces. Technical `true`
does not universally mean policy pass: Rule role and Assessment class remain
part of [policy result interpretation](../../results/results.md).

Draft 0.2.0 adds `if`, `then`, and `else`; all three expressions are required.
A Boolean true guard executes only `then`; false executes only `else`. An error,
unknown, not-evaluated, or not-applicable guard propagates its outcome and executes
neither branch. A skipped occurrence has an explicit not-evaluated trace without
overwriting a shared Test result obtained elsewhere. Ordinary Boolean siblings
are eagerly evaluated in the current expression helper.

`not_applicable: {reason: ...}` is an explicit expression leaf with a nonblank
reason. It is not a fake collector/Test and does not automatically terminate the
entire Assessment. Intrinsic applicability runs before the main expression;
false yields Assessment N/A. See [the draft expression contract and guard
table](../../../schema/v0.2.0/README.md) and [conditional examples](../../../tests/conditional-0.2.0/README.md).
The older experimental fixture identifier is not interchangeable with the
draft 0.2.0 identifier. Automatic conditional normalization is excluded because
Boolean equivalence does not establish six-state or evidence equivalence.

## Incomplete observations and sensitive results

Collection completeness, logical completeness, and retained-evidence completeness
are different. Incomplete population usually leaves truth unknown, but established
truth-table cases permit conclusive outcomes. Evidence capping must not change
truth. A resource or privilege failure must not be represented as an ordinary
empty, completely collected population. See [evaluation semantics §§8–10](../../../research/iterations/003/design/assessment-evaluation-semantics.md).

Draft 0.2.0 Test `reported_elements` defaults to `all` when omitted. Authors
may request `compared` or an array of known capability field names. The helper
creates a derived Item report from recorded field-use lineage, retaining required
identity/decisive evidence. It does not remove canonical observations or alter
truth. Shared consumers contribute their requests; requested but unavailable
fields remain explicitly accounted for. An empty array is permitted and still
retains required evidence. See [reporting examples and expected selections](../../../tests/reported-elements-0.2.0/README.md).

`redact_result: true` is sensitive-value policy and applies before reporting.
Selection is not redaction: requesting a field must never reveal a value already
redacted, and using `compared` is not sufficient to protect a sensitive compared
value. Emitted redacted typed values omit `value`. See [evaluation semantics
§13](../../../research/iterations/003/design/assessment-evaluation-semantics.md).

Result-only resolved user/group names improve readability without becoming Object
selectors or State predicates. Numeric identities retain their meaning; a failed
name lookup does not change a numeric comparison. [Item validity examples](../../../tests/collected-items-0.2.0/README.md)
and [invocation-linked results](../../../tests/assessment-results-0.2.0/README.md)
document the draft representation and lookup provenance. Imported observations
and unsigned result packages have their own context/integrity contracts in
[materialization](../../../tests/item-materialization-0.2.0/README.md) and
[result packaging](../../../tests/result-package-0.2.0/README.md).

## What the current helpers prove

Schema and graph checks validate representation and reference compatibility.
The expression evaluator accepts normalized Test outcomes from callbacks;
result helpers validate recorded evidence and scheduling consistency. Neither
acquires real resources nor independently proves all State comparisons. Migration
round trips establish a separate representation claim. Vendor/target conformance
requires independently justified expected outcomes and actual execution evidence.
