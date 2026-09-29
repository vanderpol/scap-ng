# OVAL Board Review: Assessment-Internal Applicability and Scenario Branches

**Status:** open design question  
**Iteration:** 003

## Problem

Rule applicability and Assessment-internal applicability solve different
problems.

Rule applicability answers:

> Does this Rule apply to this target at all?

Assessment-internal applicability answers:

> Given that the Rule applies, which scenario or expected state applies to this
> target?

This distinction matters for real publisher content. A single Rule may contain
multiple valid scenarios, for example:

- on a domain controller, setting A SHALL equal 1;
- on a non-domain controller, setting A SHALL equal 2.

The Rule itself applies to both systems. What changes is the expected state.

## Problem with Boolean-only lowering

Such content can be represented as nested Boolean logic, for example:

    (domain_controller AND setting == 1)
    OR
    (NOT domain_controller AND setting == 2)

That representation is logically adequate but operationally weak.

It obscures:

- which scenario was selected;
- why that scenario was selected;
- which expected state applied;
- whether a failure came from scenario selection or from the scenario's
  compliance assertion;
- how to generate a useful human-readable failure explanation.

This becomes increasingly difficult when there are more than two scenarios,
nested conditions, or organizational inputs.

## Candidate NG model

SCAP-NG should consider first-class named Assessment scenarios.

Illustrative syntax:

    assessment:
      id: example.assessment
      version: 1
      class: compliance
      scenarios:
        - id: domain-controller
          applicability:
            assessment: windows.domain-controller
          evaluate:
            check: setting-equals-1

        - id: non-domain-controller
          applicability:
            not:
              assessment: windows.domain-controller
          evaluate:
            check: setting-equals-2

The exact serialization is not decided.

The important semantic requirements are:

1. Scenario applicability SHALL be explicit and separately explainable.
2. A conforming processor SHALL identify which scenario or scenarios were
   applicable.
3. Compliance evaluation SHALL occur only against applicable scenario logic.
4. Results SHALL distinguish:
   - scenario not applicable;
   - scenario selected and passed;
   - scenario selected and failed;
   - scenario applicability unknown/error.
5. Failure output SHOULD state both the selected scenario and the failed
   assertion.
6. Scenario selection SHALL NOT be hidden solely inside opaque Boolean
   expressions when the authoring semantics contain distinct scenarios.

## Relationship to Rule applicability

Assessment-internal scenario applicability SHALL NOT replace Rule
applicability.

A Rule-level applicability predicate can cause the entire Rule to be out of
scope.

Assessment scenario applicability selects among valid evaluation paths within
an in-scope Rule.

## Relationship to OVAL

Historical OVAL/SCAP content often encoded scenario behavior using combinations
of criteria, inventory-class definitions, CPE applicability checks, or other
Boolean constructions.

OVAL also contains the `applicability_check` marker, but implementation
evidence indicates that this marker was not a complete policy-level
applicability/result mechanism.

SCAP-NG SHOULD preserve the operational intent of scenario-dependent
evaluation rather than mechanically reproducing the legacy Boolean shape.

## Board questions

The OVAL Board should review:

1. whether Assessment-internal applicability should be a first-class NG
   construct;
2. whether the construct should be called `scenario`, `branch`,
   `conditional`, or another established term;
3. whether exactly one scenario must match, multiple scenarios may match, or
   both modes are needed;
4. how no-match, multi-match, unknown, and error conditions map into NG
   results;
5. whether scenario applicability should reference reusable Assessments,
   contain local predicates, or support both;
6. how this interacts with Assessment `class` and the historical use of
   OVAL `inventory` definitions for applicability;
7. how migration tooling should recognize scenario patterns in existing OVAL
   criteria without inventing semantics that are not explicit in the source.

## Current project recommendation

Do not force all applicability into Rule applicability.

Retain Rule applicability for whole-Rule scope, and design an explicit
Assessment-internal scenario mechanism for conditional expected-state
selection.

Do not finalize the serialization until the historical OVAL/SCAP implications
and result-state behavior have been reviewed.
