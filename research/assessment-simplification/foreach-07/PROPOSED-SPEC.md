# Proposed SCAP-NG 0.3.0 foreach specification

**Status:** historical v1 automatic-modernization proof. The accepted 0.3
language now also supports correlated chained/nested collection iteration; see
[`specification/assessment/foreach.md`](../../../specification/assessment/foreach.md).
This document remains the proof boundary for the narrow automatic v1 rewrite.  
**Tracking:** #164  
**Does not modify:** frozen 0.2.0 schemas or semantics.

## 1. Purpose

`foreach` is an authoring construct for expressing a proven dependency pattern
without exposing representation-only Variable plumbing.

The first standardized form is **collection expansion** only.

It does **not** mean "evaluate one Test per source Item."

## 2. First supported semantic class

Version 1 of the proposal covers only the semantic graph:

```
source Object
  -> object_component(item_field)
  -> local Variable
  -> target Object selector var_ref(var_check="at least one")
  -> target Object population
  -> existing Test evaluation
```

The reviewed transformation identifier is:

`foreach.direct-object-component.at-least-one.v1`

Other shapes remain faithful graph form unless separately proven.

## 3. Proposed authoring form

```yaml
objects:
  non-system-users:
    capability: unix.password
    # ordinary Object selectors / sets / filters

  initialization-files:
    capability: unix.file

    for_each:
      item: user
      in: non-system-users

    select:
      directory:
        from: user.home_dir

      name:
        value: '^\\.[^\\s\\.]+'
        operation: match
        datatype: string
```

The binding name (`user`) is lexical authoring syntax. It is not runtime Item
identity.

`in: non-system-users` identifies the complete source Object dependency.

`from: user.home_dir` means that the target `directory` is bound from that field
of each source Item. In v1, `from` is a binding, not an authored comparison.
The equivalent `equals`, datatype compatibility, and
`var_check="at least one"` behavior belong to the normative desugaring rather
than the author-facing syntax.

Object-level `for_each` has exactly one v1 meaning: expand collection from the
bound source Items and combine the resulting target Items into one target Object
population. Because there is no author choice in v1, `collect: union` is not
authored. This is intrinsic grammar semantics, not a hidden configurable
default.

## 4. Normative meaning

A conforming processor SHALL interpret the example above exactly as if the
author had written the semantic equivalent of:

```
Variable projected-home-dirs:
  local
  datatype: string
  expression:
    object_component:
      object: non-system-users
      item_field: home_dir

Object initialization-files:
  directory:
    variable: projected-home-dirs
    var_check: at least one
    operation: equal
    datatype: string
  ...
```

The desugared semantic graph is normative.

An implementation MAY execute the foreach form directly, but observable
behavior SHALL be equivalent to that graph.

## 5. Collection boundary

`foreach` collection expansion:

1. evaluates the source Object using its existing selectors, Sets, Filters and
   collection behavior;
2. projects the requested field from the resulting source Items using existing
   ObjectComponent semantics;
3. supplies the resulting values to the target selector with
   `var_check="at least one"`;
4. forms one combined target Object population;
5. evaluates existing Test `check_existence`, State logic, and Test `check`
   against that combined population.

It SHALL NOT create one Test result per source Item.

## 6. ObjectComponent status preservation

The foreach form SHALL preserve the status of the normative desugared
ObjectComponent/Variable dependency.

In particular:

- zero source Items is an ObjectComponent error;
- a source Item missing the projected field is an ObjectComponent error;
- an incomplete source collection remains an incomplete dependency;
- no loop-specific empty-list success rule may replace these outcomes;
- datatype/cast errors remain errors;
- no source status may be promoted to complete merely because some usable Items
  were observed.

The construct therefore does not define a second flag-propagation table.

## 7. Quantification

The first form has fixed selector quantification:

`var_check = at least one`.

This quantifier is intrinsic to the v1 `from:` binding and is not authored
separately. If future forms support a real quantifier choice, that choice SHALL
be explicit rather than introduced as a hidden default.

It SHALL NOT be used to modernize a source selector whose effective
`var_check` is `all`, `only one`, `none satisfy`, or a mixed set of
quantifiers.

A future syntax may expose a selector quantifier only after separate
equivalence work. It must not overload collection aggregation.

## 8. Multiplicity and duplicates

Multiple source Items may project the same value.

Duplicate projected values do not alter target Item membership under the
first-class at-least-one selector semantics.

Result/evidence provenance SHALL nevertheless retain distinct source Item
identities so duplicate values from different source Items remain explainable.

## 9. Result and evidence requirements

A full result for the modernized form SHALL retain enough information to derive
the same canonical evidence view as the faithful graph:

- source Object identity;
- source Item references used by the projection;
- source field/value projections paired with source Item identity;
- projection/value-production status;
- combined target Item population;
- unchanged downstream Test aggregation/result.

A result SHALL NOT invent a parent-value -> child Item correlation when the
faithful graph does not establish one.

Evidence caps MAY reduce retained samples but SHALL NOT change the verdict or
claim completeness when decisive provenance was discarded.

## 10. First automatic-modernization preconditions

The transformation
`foreach.direct-object-component.at-least-one.v1` is eligible only when all of
the following are true:

1. the source is a reachable Object;
2. the Variable is a local Variable;
3. its expression is exactly one direct `object_component`;
4. the projection uses `item_field` only; `record_field` is not in v1;
5. the Variable is consumed by exactly one target Object selector;
6. the target selector's effective `var_check` is `at least one`;
7. that target Object has no independent additional Variable selector;
8. the target Object is directly referenced by at least one Test;
9. source Sets and Filters remain on the source Object unchanged;
10. the target selector's effective equality comparison and compatible datatype
    are preserved by desugaring even though they are not redundantly authored
    beside `from:`;
11. target Object population remains the Test aggregation boundary;
12. the canonical evidence view remains derivable.

Failure of any precondition leaves the faithful representation unchanged.

## 11. Explicitly excluded from v1

The first class SHALL NOT modernize:

- `var_check=all`;
- mixed selector quantification;
- Variables that fan out to multiple target Objects;
- helper/intermediate target Objects not directly referenced by a Test;
- `record_field` projection;
- derived functions such as `concat`, arithmetic, merge, regex transforms or
  other function trees;
- multiple independent multi-valued inputs;
- Cartesian-product expressions;
- inferred keyed/positional correlation;
- evaluation iteration;
- source defects or deprecated OVAL constructs.

These are potential later proof classes, not syntax errors in faithful content.

## 12. Analyzer states

The 0.3.0 authoring/schema and semantic-validation layers now implement this
v1 construct. The research analyzer SHALL nevertheless continue to report
legacy-conversion candidates as `review_required` until the production
SCAP 1.4 converter modernization pass is integrated and enabled.

After that converter gate is accepted, an implementation may report:

`safe_automatic`

only when the exact v1 transformation identifier and all preconditions match.

## 13. Production evidence

Pinned current-content census:

| Benchmark | v1 proof-class eligible |
| --- | ---: |
| RHEL 9 | 4 |
| Solaris 11 x86 | 1 |
| **Total** | **5** |

The five examples exercise multiple source/filter shapes and downstream
existence contracts including `any_exist`, `at_least_one_exists`, and
`none_exist`.

This demonstrates that the construct is not a one-rule special case while
keeping the first automatic class deliberately narrow.

## 14. Conformance requirements

At minimum, conformance fixtures SHALL cover:

- one and many source Items;
- duplicate projected values;
- source Set/Filter selection;
- zero source Items -> ObjectComponent error;
- missing projected field -> ObjectComponent error;
- complete and incomplete source dependency status;
- target zero/one/many Items;
- all Test existence modes used by supported content;
- Test `all` and `at least one` plus retained generic truth-table behavior;
- source/target Item evidence equivalence;
- negative `var_check=all` counterexample;
- fan-out rejection;
- helper-target rejection;
- derived/Cartesian-expression rejection.

## 15. Open questions for later classes

Separate work is required for:

1. safe fan-out of one source projection to multiple targets;
2. helper/intermediate target chains;
3. `record_field`;
4. all-values and other selector quantifiers;
5. mapped unary functions;
6. multi-input/Cartesian functions;
7. evaluation-level foreach.

None of these should delay review of the narrow v1 collection-expansion form.
