# Draft 0.2.0 Assessment expression slice

Read the [Assessment author and assessor reference](../../specification/assessment/reference/README.md)
for shared behavior, initial capability field guides, and linked expected-result
examples. Its coverage is incomplete; it does not turn this partial draft into
a released specification or claim live collector conformance.

This is a partial versioned draft, not a complete 0.2.0 release schema set.
The [draft capability additions](capability-mappings/README.md) include ESXi host
services and named advanced settings with typed repeated values, field
annotations and synthetic known-result cases. They do not expand 0.1.0.
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

## Reported elements draft

The [single-commit reporting checkpoint](../../transition/reported-elements-2026-10-03.md) adds Test-only `reported_elements`: `all` by default, `compared`, or a unique array of top-level Item field names. It provides generated capability overlays and a marked derived Item report, preserves canonical truth and source completeness, and keeps `redact_result` as the separate cross-result confidentiality control. Full Assessment Result integration and actual field-use lineage production remain release prerequisites.

## Assessment Result integration

The [result integration checkpoint](../../transition/assessment-results-2026-10-03.md)
adds a canonical draft Assessment Result graph with per-invocation expression
records, local Test/Object/Item/Variable evidence, dependency execution IDs and
optional derived Item reports. Shared Item/result types now have v0.2.0 IDs.
The source-aware helper validates capability Item contracts and recorded
scheduling offline. The result-set wrapper is development transport, not a final
result package. See the [known-result examples](../../tests/assessment-results-0.2.0/README.md).

## Item inclusion and import provenance

The [materialization checkpoint](../../transition/item-materialization-2026-10-03.md)
adds producer-side `all`/`consumed` Item scope with explicit availability accounting,
local Variable Item references and verified source-byte observation imports.
`all` is the default; consumed/decisive evidence remains mandatory. Source context,
origin history and incompleteness survive copying. This does not implement a
collection cache or invent a content-authored inclusion control. See
[standalone expected results](../../tests/item-materialization-0.2.0/README.md).

The unsigned result-package draft adds Scan/Benchmark/Rule Result schemas and a
closed exact-byte manifest connecting logical Assessment execution references.
See [the checkpoint](../../transition/result-package-2026-10-03.md) for scope,
validation limits and [the known result](../../tests/result-package-0.2.0/README.md).

Host account and installed VIB additions are documented in the
[capability reference](../../specification/assessment/reference/README.md), with
[synthetic known results](../../tests/esx-host-0.2.0/README.md). Four of the 22
OVAL 6.0-only Test contracts have draft native mappings. The remaining count is
**not** an active 0.2.0 backlog: ESX expansion is deferred pending upstream
guidance, and both Kubernetes Tests are reviewed/deferred for 0.2.0 in
[the disposition](../../transition/kubernetes-oval6-disposition-2026-10-03.md).
