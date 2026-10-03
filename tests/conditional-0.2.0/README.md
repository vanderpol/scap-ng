# Conditional known-result content — 0.2.0 research suite

**Status: experimental proposal-01.** This uses the small-example / controlled-input / known-result method of OVAL Self-Assertion. It is new project-authored conditional research, not copied SCAP 1.4 test content or a released 0.2.0 schema. Expected results describe the proposed contract below; they do not establish that this contract is ratified.

The owner requested explanatory test content for known conditional scenarios, and a way for a conditional to return `not_applicable`. The source baseline is `ab6e9fb1b291fab389157990e5a66f4d29ed1a97`. [Provenance](provenance.json) records the inspected contracts and hashes. Owner follow-up on 2026-10-03 removed automatic conditional normalization and candidate detection from planned features; [#126](https://github.com/vanderpol/scap-ng/issues/126) is closed as not planned. Reported elements are tracked separately in [#125](https://github.com/vanderpol/scap-ng/issues/125).

## Start with one example

Proposed conditional syntax in [local content](content/local.assessment.yaml):

```yaml
evaluate:
  if:
    test: test-guard
  then:
    test: test-then
  else:
    test: test-else
```

`true` selects then. `false` selects else. The selected expression determines the outcome; the other expression is not evaluated by this model. A false condition does not itself mean the requirement failed.

### Complete proposed guard table

| Condition result | Selected branch | Conditional outcome |
| --- | --- | --- |
| `true` | then | Outcome of then expression |
| `false` | else | Outcome of else expression |
| `error` | neither | `error` |
| `unknown` | neither | `unknown` |
| `not_evaluated` | neither | `not_evaluated` |
| `not_applicable` | neither | `not_applicable` |

The last four rows are a **proposal under test**, not an inferred existing OVAL conditional rule. The complete selected-branch outcome domain is preserved. Inactive branches cannot repair an unresolved condition, even if their hypothetical outcomes happen to agree. Else is required in this first grammar; omission has no implicit success or not-applicable default.

## Returning not applicable

[Explicit outcome example](content/explicit-na.assessment.yaml):

```yaml
evaluate:
  if:
    test: test-guard  # Is the optional component installed?
  then:
    test: test-then   # Is its configuration correct?
  else:
    not_applicable:
      reason: The optional component is absent, so its configuration requirement does not apply.
```

This proposes an explicit expression outcome with an authored explanation, rather than a new fake collector/Test. It consumes no additional resources and records a terminal explanation in the model trace. A guard `error` or `unknown` SHALL NOT take the absence branch. The exact key, permissible placement and explanation contract remain design questions. The terminal is an expression value, not a command to exit the entire Assessment regardless of enclosing logic.

[Existing intrinsic applicability](content/intrinsic-na.assessment.yaml) offers a cleaner alternative when absence invalidates the **whole** Assessment:

```yaml
applicability:
  test: test-guard
evaluate:
  test: test-then
```

False intrinsic applicability already yields `not_applicable`; its error/unknown outcomes remain distinct. Prefer this existing mechanism for whole-Assessment applicability. An explicit conditional outcome is useful when a branch needs a local not-applicable result and explanation.

Under an enclosing `all` or `any`, a `not_applicable` child does not necessarily make the complete Assessment not applicable. Existing aggregation semantics still apply. See the [all](content/na-in-all.assessment.yaml), [any](content/na-in-any.assessment.yaml), and [negation](content/negated-na.assessment.yaml) examples and known results before authoring a policy exception.

## Example and scenario coverage

| Content | What to learn | Known-result case IDs |
| --- | --- | --- |
| [Local](content/local.assessment.yaml) | Basic branching; all six condition and selected outcomes | `local-*`, `guard-*`, `selected-*`; 216 combinations |
| [Role](content/role.assessment.yaml) and [dependent condition](content/dependent.assessment.yaml) | Existing statically bound Assessment result as condition | `dependent-*`; 216 combinations |
| [Nested](content/nested.assessment.yaml) | Branches can contain conditionals; inner failure and skipped inner guard | `nested-*` |
| [Shared](content/shared.assessment.yaml) | Reuse a Test result without wrongly marking the actual Test unexecuted | `shared-guard` |
| [Intrinsic applicability plus conditional](content/applicability.assessment.yaml) | Applicability stage precedes normal evaluation | `intrinsic-*`; 1296 combinations in regressions |
| [Compound guard](content/logical.assessment.yaml) | AND outcome can be false despite an error sibling | `logical-*` |
| [Negated guard](content/negated.assessment.yaml) | Negate true/false; preserve other outcomes | `negated-*` |
| [Dependency in branch](content/branch-dependency.assessment.yaml) | Validate all dependencies; invoke only selected dependency | `selected-dependency`, `unselected-dependency` |
| [Explicit not applicable](content/explicit-na.assessment.yaml) | Branch outcome with reason; distinguish error from absence | `explicit-*`; 36 combinations in regressions |
| [Intrinsic absence](content/intrinsic-na.assessment.yaml) | Existing alternative for whole-Assessment applicability | `intrinsic-equivalent-absence` |
| [N/A under all](content/na-in-all.assessment.yaml), [any](content/na-in-any.assessment.yaml), [not](content/negated-na.assessment.yaml) | Local N/A versus whole-Assessment outcome | `na-under-*`, `negated-not-applicable` |

[cases.yaml](cases.yaml) contains 33 readable positive cases with supplied terminal Test outcomes, expected Assessment outcome, executed Tests and selected branches. [guard-table.json](guard-table.json) is the independently reviewed expected table. It is fixture data, not read by the model's conditional evaluator.

[invalid-cases.yaml](invalid-cases.yaml) contains 10 reproducible source mutations and expected static diagnostics: absent else, missing Test in an inactive branch, undeclared/missing/wrong-version dependencies, cycles even in unused dependencies, dynamic input/command forms, empty compound guard and missing N/A reason. They fail before execution.

Additional adversarial regressions cover missing runtime results, repeated references, target/binding isolation, mapping-order independence, non-Boolean fixture values, nested-depth resource limits and a normalizer counterexample. These are known scenario classes, not a claim to cover every future language feature or every platform collector behavior.

## What the model executes

`tools/conditional_conformance.py` evaluates expression structure and Assessment-result dependencies using **supplied terminal Test outcomes**. It does not perform collection, compare State entities, evaluate Variable functions or contact target systems. Source files use readable `variable.value` declarations with true constants as illustrative basic content; fixtures substitute controlled terminal results at the Test boundary. The error/unknown/etc fixtures are simulated runtime conditions, not claims that those constants naturally produce all six outcomes on a scanner.

The model validates references in every branch before execution. It resolves example dependencies by explicit relative source path, expected ID and version. Runtime Test/Assessment reuse is scoped to one invocation's target/bindings, and traces distinguish skipped expression paths from actual reused Test results. The model's traces are **not canonical Assessment Result artifacts** and have not been promoted into result schemas. They do not establish collected Item materialization, completeness, evidence caps or imported-Item behavior.

Logical `all` and `any` use the maintained OVAL-derived aggregation helper and evaluate their siblings eagerly in this model. This deliberately does not resolve the separate AND/OR short-circuit policy question. Conditional branches are selective; inactive branch expressions are recorded as `not_evaluated`. An actual Test also referenced by active logic remains evaluated with its real outcome, even if another expression path referring to it is inactive.

The default depth budget of 200 is a configurable model resource limit, not a new language limit. The expression grammar supports recursion; a 20-layer example is explicitly tested. Organizational Input cannot provide Test names, dependency aliases, branches, commands or executable expressions. Binding metadata in this model identifies an invocation and does not select the graph.

## Run it

From the repository root, install the repository's PyYAML and jsonschema dependencies, then:

```bash
python tools/conditional_conformance.py --report work/conditional-results.json
python tools/test_conditional_conformance.py
python tools/check_current_authoring_contract.py tests/conditional-0.2.0/content
```

The suite runner checks 465 positive evaluations (33 curated + 432 matrices) and 10 invalid-content cases. The 19 regression tests additionally cover a 1296-case applicability matrix and a 36-case explicit-N/A matrix, along with adversarial checks. They also validate illustrative Test/State declarations against current capability fragments and check their source references. Report these units separately rather than equating unittest method counts with content case counts. The vocabulary guard passes 14 source files; that is naming/presentation evidence, not execution equivalence.

## Normalizer feasibility finding

The apparently obvious `(G AND T) OR (NOT G AND E)` rewrite is not universally equivalent to this proposed conditional. With `G=error`, `T=false`, `E=false`, inherited aggregation yields `false`, while proposed conditional propagation yields `error`. A focused regression preserves this counterexample. A Boolean shape does not justify a lossless upgrade. The owner removed this potential normalizer feature on 2026-10-03; #126 is closed as not planned. Keep this counterexample as conformance evidence.

## Design questions before implementation

1. Ratify or revise the non-Boolean guard table, especially `not_applicable` and `not_evaluated`.
2. Choose final conditional syntax; decide whether else may be omitted and with what explicit meaning.
3. Decide the explicit N/A outcome's name, allowed scope and required explanation. Compare it with intrinsic applicability before adding a new Test capability.
4. Define branch/dependency trace records and result completeness in the canonical result contract, including required condition evidence and imported Items.
5. Specify interactions with evidence caps, early termination, shared collection and `reported_elements`; these cannot erase decisive guard evidence.
6. Decide whether typed values may be operands without letting Organizational Input select Tests or inject expressions. This first model only consumes Test/Assessment outcomes and ordinary logical composition.

Proposed normative requirements here are for discussion: both branches and dependencies SHALL be statically declared and valid; conditions SHALL preserve six-state outcomes; selected results SHALL retain explanatory provenance; skipped paths SHALL be distinguishable from actual Test results. No production schema/converter/normalizer behavior is changed by this suite. Board decisions belong in separate versioned yes/no Discussion proposals, not inferred from these passing experiments.
