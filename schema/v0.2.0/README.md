# Draft 0.2.0 Assessment expression slice

This is a partial versioned draft, not a complete 0.2.0 release schema set.
It adds `assessment.schema.json`, recursive `expression.schema.json`, and an
expression-stage `expression-result.schema.json`. Unchanged manual authoring is
explicitly pinned to the 0.1.0 manual schema. Use the maintained schema harness
to resolve these local references without retrieving schemas over the network.

Automated Assessments identify `scap-ng.pre-alpha.assessment` version `0.2.0`.
The identifier remains provisional pending Board naming. This does not change
the meaning of an Assessment's own integer revision `version`.

Expressions support Test/dependency leaves, `all`, `any`, `one`, `odd`, `not`,
`if`/`then`/`else`, and `not_applicable: {reason: ...}`. All three conditional
parts are mandatory; use nested conditions instead of a separate elseif form.
All references, including unselected branches and unused declared dependencies,
are validated before execution. Arbitrary expressions/Variables are not silently
coerced into Boolean guards; reference a Test that provides the desired comparison.

| Guard outcome | Execution | Conditional outcome |
| --- | --- | --- |
| `true` | Only `then` | Selected expression outcome |
| `false` | Only `else` | Selected expression outcome |
| `error` | Neither branch | `error` |
| `unknown` | Neither branch | `unknown` |
| `not_evaluated` | Neither branch | `not_evaluated` |
| `not_applicable` | Neither branch | `not_applicable` |

Explicit N/A is an expression leaf with a nonblank reason, not a synthetic Test
or collector capability. It has no technical resource observation and applies
at its position in the expression. It is not an unconditional Assessment-wide
early return. Surrounding operators retain their six-state aggregation semantics;
for example, N/A plus a Boolean sibling can aggregate to that Boolean outcome.
Intrinsic applicability executes before `evaluate`: false yields Assessment N/A;
other nontrue outcomes propagate without executing the main expression.

The evaluator uses eager sibling evaluation for `all`/`any`/`one`/`odd`; only the
conditional and intrinsic applicability select execution paths. This keeps
ordinary sibling diagnostics and does not invent a broader short-circuit policy.
Skipped expression occurrences have `not_evaluated` traces with a reason. This
does not overwrite a shared Test result acquired through another executed path.

`tools/assessment_expression.py` provides `AssessmentExpressionEvaluator`.
Construct it from the complete, resolved Assessment graph and call
`run(entry, evaluate_test, target=..., bindings=..., evaluate_manual=...)`.
The Test callback receives `(assessment_id, test_id, context)` only when its leaf
is executed, and supplies one of the six normalized technical outcomes.
The optional manual callback receives `(assessment_id, context)` and supplies
the normalized manual Assessment result. The caller owns authorization, provenance,
acquisition, State/Test evaluation and manual lifecycle. An absent manual provider
fails explicitly when invoked. Callback contexts are copies; returned traces do
not disclose binding values. Reuse is scoped to one run, target and effective
binding context, with dependent identity and invocation reference retained.

The compiler includes complete static dependency closure, verifies declared
identity/version/purpose expectations, rejects cycles and duplicate identities,
and binds dependencies to logical manifest objects with explicit identity/version
pins and content digests. The bundle verifier checks those bindings and validates
the draft expression slice again. It does not dynamically load unsigned sources
to resolve branches. Dependency composition does not implicitly import Items.

0.1.0 schemas and conversion output remain unchanged. In particular, current
OVAL-compatible `applicability_check` wrappers and historical `xor` aliases are
not automatically renamed or upgraded into this grammar. Source conversion to
0.2.0 remains blocked for unsupported expression forms until semantic lowering
is reviewed and tested; preserve the original 0.1.0 source rather than dropping
behavior. Automatic conditional normalization and candidate detection are removed from the
planned features; #126 is closed as not planned by owner direction on 2026-10-03.

An expression-stage result is not a complete Assessment Result. Connecting its
trace to the complete 0.2.0 Item/Test/State/result-package graph, target acquisition
conformance, and the remaining release features still precede 0.2.0 promotion.
See [the integration checkpoint](../../transition/conditional-integration-2026-10-03.md).
