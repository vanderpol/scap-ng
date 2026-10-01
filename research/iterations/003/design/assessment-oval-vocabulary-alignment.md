# Assessment vocabulary alignment with OVAL

**Status:** pre-alpha design decision for iteration 003

This document records the SCAP-NG Assessment vocabulary to use before deeper
capability-schema generation.

The governing principle is:

> When SCAP-NG retains substantially the same semantic concept as OVAL, use the
> established OVAL term. Introduce a different term only when SCAP-NG
> deliberately changes or improves the concept.

SCAP-NG is not required to reproduce OVAL XML serialization. This decision is
about semantic vocabulary, not element nesting or XML compatibility.

## Adopted vocabulary

| OVAL concept | Earlier/current NG vocabulary | SCAP-NG vocabulary | Decision |
| --- | --- | --- | --- |
| Definition | Assessment | **Assessment** | Intentional NG term; an Assessment is the executable condition bound to a Rule or applicability use. |
| Test | check / Test | **Test** | Retain OVAL term. |
| Object | collect / Collection | **Object** | Retain OVAL term. "Collection" is the runtime act of evaluating an Object and producing Items. |
| State | assert / embedded state | **State** | Retain OVAL term and make States independently identifiable nodes. |
| Variable | Variable | **Variable** | Retain OVAL term. |
| Item | Item | **Item** | Retain OVAL term for runtime observations/results. |
| criteria / criterion | evaluate | **evaluate** | Intentional NG improvement; preserve full nested logical expressive power. |
| Test check | item_quantifier / check | **check** | Retain OVAL term because semantics are retained. |
| Test check_existence | existence | **check_existence** | Retain OVAL term because semantics are retained and distinct from State/entity existence. |
| Test state_operator | state_operator | **state_operator** | Retain OVAL term. |
| State operator | operator | **operator** | Retain OVAL term. |
| State entity entity_check | entity_check | **entity_check** | Retain OVAL term. |
| State entity var_check | var_check | **var_check** | Retain OVAL term. |
| Object filter | filter | **filter** | Retain OVAL term and post-filter Item population semantics. |
| Object set | set | **set** | Retain OVAL term. |
| comment | generic comment | **typed *_title fields** | Intentional NG improvement. |

## Typed descriptive titles

OVAL `comment` is intentionally **not** retained as the native field name.
Migration maps useful comments to the node they describe:

- Definition metadata title -> `assessment_title`;
- Test comment -> `test_title`;
- Object comment -> `object_title`;
- State comment -> `state_title`;
- Variable comment -> `variable_title`.

These fields are descriptive metadata and do not alter evaluation semantics.

## Native automated Assessment shape

The preferred native shape has independently named Tests, Objects, States and
Variables:

```yaml
assessment:
  id: example
  version: 1
  assessment_title: Example
  mode: automated
  class: compliance
  purpose: assessment

  objects:
    object-config:
      object_title: Configuration file
      capability: unix.file
      select:
        filepath:
          operation: equals
          datatype: string
          value: /etc/example.conf

  variables: {}

  states:
    state-mode:
      state_title: File mode is acceptable
      capability: unix.file
      entities:
        mode:
          operation: equals
          datatype: string
          value: "0644"

  tests:
    test-mode:
      test_title: Configuration file has the required mode
      capability: unix.file
      object: object-config
      check_existence: at_least_one_exists
      check: all
      state_operator: AND
      states:
        - state-mode

  evaluate:
    test: test-mode
```

Exact capability-specific Object and State payload grammar remains subject to
generated schema work. The semantic node boundaries above are the important
decision.

## Object and collection are not synonyms

An **Object** is authored content describing what observations are selected.

**Collection** is runtime behavior: evaluating an Object against a target to
produce zero or more Items plus collection status/completeness information.

A result may therefore contain an Object result / collection-execution record,
but native source should not rename the authored Object itself to Collection.

Filters are part of Object semantics. The canonical Item population is the
effective population after Object selection, set operations and filters have
been applied. A scanner may push filters into its collector/query planner and
need not materialize or count a pre-filter candidate population.

## Test semantics

A Test references an Object and zero or more States.

Behavior-affecting OVAL Test terms whose semantics are retained remain explicit:

- `check_existence`;
- `check`;
- `state_operator`.

SCAP-NG SHALL NOT rename `check` to `item_quantifier` merely to make the
field sound more descriptive. The specification and generated documentation
instead define precisely what an Item means and how `check` aggregates
per-Item results.

## State identity

States are independently meaningful typed predicates and SHOULD have stable
local identities in native Assessment source.

This is important for:

- multiple Tests reusing one State;
- filters referencing States;
- result-to-source traceability;
- semantic graph comparison;
- future shared/reusable components;
- capability-specific schema validation.

Migration should preserve useful source identity in conversion provenance, but
native IDs need not reproduce OVAL IDs.

## Evaluate

`evaluate` is the intentional native successor to OVAL `criteria` /
`criterion`.

It SHALL support arbitrary nesting required to preserve legacy logical
structure, including AND/OR/ONE/XOR/NOT-equivalent expressions and Test
references as supported by the adopted model. No arbitrary language nesting
limit shall be introduced for conversion convenience.

Conditional evaluation may provide a clearer native authoring mechanism for
some future cases, but it does not remove the need for full `evaluate`
compatibility.

## Results vocabulary relationship

Assessment Results retain the same semantic identities:

- Test result -> Test;
- Object/collection-execution result -> authored Object;
- State evaluation -> State;
- Variable binding -> Variable;
- collected observation -> Item.

Assessment truth remains distinct from Rule policy outcome:

- compliance true -> pass;
- compliance false -> fail;
- vulnerability true -> fail;
- vulnerability false -> pass.

This vocabulary alignment should be completed in converter output and schemas
before generated deep capability schemas are treated as a baseline.
