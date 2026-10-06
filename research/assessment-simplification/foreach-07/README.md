# Foreach modernization research

**Status:** research / pending human review. This document does not change the
0.2.0 language, schema, converter, or current accepted design.

**Working baseline:** `main` at
`0c85d8a563b3320f80b7215c0f18e4dec4b064b4` (2026-10-06).

## Goal

Determine whether selected faithful SCAP 1.4 / OVAL 5.12.3 conversions can be
automatically modernized into smaller, clearer native SCAP-NG using an explicit
iteration construct without changing technical truth, collection scope,
six-state result behavior, or decisive evidence.

The working pipeline is:

```
SCAP 1.4 / OVAL
    -> semantic IR
    -> faithful NG
    -> modernization analysis
    -> optional native foreach lowering
```

Faithful conversion and modernization are separate gates. Failure to prove a
modernization leaves the faithful NG representation unchanged.

## Primary discovery: collection iteration and evaluation iteration are different

A single informal phrase such as "for each user" hides at least two materially
different semantics.

### A. Collection expansion

For each source value/item, instantiate a target Object selector, collect the
matching Items, then combine those Items into the target Object population.
The Test evaluates the combined population using its existing
`check_existence`, `check`, States, and other aggregation semantics.

This is the closest native analogue for many OVAL
`object_component -> local_variable -> Object entity var_ref` graphs.

Conceptual authoring form:

```yaml
objects:
  non_system_users:
    capability: unix.password
    # existing set/filter semantics remain unchanged

  initialization_files:
    capability: unix.file
    for_each:
      source:
        object: non_system_users
      as: user
      select:
        path:
          from: user.home_dir
        filename:
          operation: pattern_match
          value: '^\\.[^\\s\\.]+'
      collect: union
```

`collect: union` is shown explicitly because collection-level iteration SHALL
NOT imply per-iteration Test evaluation.

### B. Evaluation iteration

For each source value/item, evaluate a Test/evaluation body independently, retain
an iteration result, then aggregate the iteration results with an explicit
quantifier.

Conceptual authoring form:

```yaml
evaluate:
  for_each:
    source:
      object: users
    as: user
    match: all
    do:
      # scoped evaluation using user fields
```

This is a stronger semantic operation. It is NOT automatically interchangeable
with collection expansion.

## RHEL 9 counterexample establishing the distinction

Source:
`research/assessment-simplification/evidence/rhel_9/SV-257889/source-oval.xml`

The source:

1. collects users;
2. filters the password Item population to the relevant account class;
3. projects `home_dir` through `object_component`;
4. supplies the resulting multi-valued Variable to the File Object's `path`;
5. collects initialization files across those paths;
6. applies one File Test to the resulting Item population.

For the non-system-user Test, `check_existence="any_exist"` applies to the
combined File Object result. Rewriting this as "evaluate one Test per user and
require all users to pass" can change the result when some home directories
produce no matching initialization files while another does.

Therefore an automatic modernization SHALL preserve the aggregation boundary.
This case is evidence that iteration syntax needs either distinct collection and
evaluation forms or an equally explicit scope discriminator.

## Initial safe-automatic candidate

A graph is a candidate for **collection-expansion foreach** when all of the
following can be proven from the semantic IR:

1. a source Object produces Items;
2. a local Variable is a direct projection of one Item field using
   `object_component` (record field included where applicable);
3. the projected Variable is consumed as selector input by a target Object;
4. replacing the Variable plumbing with a scoped binding preserves the same
   target selector values, datatype, multiplicity, error/empty status, and
   provenance;
5. the target Object's complete Item population is combined before the existing
   Test's existence/check/State evaluation;
6. Sets and Filters feeding the source Object retain their original ordering and
   semantics;
7. no correlation is invented between independent multi-valued sources;
8. no function with cross-product or ordering behavior is silently changed.

This transformation should remove representation plumbing, not alter the
collector or policy requirement.


## Standards correction: zero-source ObjectComponent is an error

The OVAL ObjectComponentType contract is stricter than a generic zero-value
Variable rule. For a direct `object_component`:

- if the referenced Object finds zero Items, determining the component value is
  an **error**;
- if a collected Item lacks the requested `item_field`, determining the
  component value is an **error**;
- if one or more matching entities exist, all matching values contribute to the
  component value set.

Therefore a native foreach modernization SHALL NOT reinterpret zero source
Items as a normal empty iteration or as an ordinary empty Variable. The
modernized form must preserve the ObjectComponent error before the target
Object/Test is evaluated.

This correction narrows the first automatic candidate class: the selector
population equivalence is proven only after successful ObjectComponent
projection. Non-success source collection/component status remains a separate
proof gate.


## Normative desugaring contract for the first foreach class

The strongest way to preserve non-complete source status is to avoid defining a
second runtime semantics for foreach.

For the first candidate family, native foreach SHALL be defined as authoring
shorthand for the same semantic graph produced by faithful OVAL conversion:

```
source Object
  -> object_component(item_field)
  -> local Variable
  -> target Object selector var_ref(var_check="at least one")
  -> existing target Object population
  -> existing Test check_existence/check/state semantics
```

The rewrite removes authoring plumbing only. It does not remove or bypass the
source Object, ObjectComponent, Variable status, target Object aggregation
boundary, or downstream Test aggregation.

Consequences:

- source Object collection status remains observable through the same
  ObjectComponent/Variable dependency;
- `object_component` zero-Item and missing-field errors remain errors;
- an incomplete source remains an incomplete value-producing dependency rather
  than being silently treated as a complete list of the Items seen so far;
- provenance continues to identify the source Object/Item and projected field;
- a scanner MAY optimize execution but MUST produce behavior equivalent to this
  desugared graph.

This avoids maintaining two independently specified flag-propagation systems.

The older OVAL processing-model documentation explicitly classified direct
ObjectComponent results as `complete` when the referenced Object is complete
and `incomplete` when the referenced Object is incomplete. OVAL 5.12.3 retains
the ObjectComponent rules for zero Items and missing fields and contains no
contradictory semantic change. For any source status not fully determined by the
current normative material, the graph-desugaring definition remains the
authoritative SCAP-NG behavior rather than an invented loop-specific rule.

## Automatic rejection / review-required conditions

The first modernization pass should refuse or require human review when any of
these are present unless a focused equivalence rule exists:

- two or more independent multi-valued sources whose OVAL function semantics can
  form a Cartesian product;
- `concat`, arithmetic, or another function where collection-valued operands
  combine rather than map independently;
- a proposed rewrite that changes a combined Object population into
  per-source-value Test results, or the reverse;
- ambiguous duplicate/multiplicity handling;
- variable evaluation error/unknown/not-collected behavior that cannot be
  represented identically;
- empty Variable behavior whose consuming context would change;
- `var_check` / `entity_check` / Test `check` levels that would be flattened
  or reordered;
- correlation inferred from coincident list positions, shared string values, or
  human intent rather than source semantics;
- set/filter ordering changes;
- acquisition changes such as converting independent Apache root/config arrays
  into a keyed installation join;
- source defects or deprecated-Test blockers.

The Apache assessment-simplification cases are an explicit negative example:
multi-valued `concat` may intentionally produce Cartesian paths. A foreach/join
rewrite must not silently correlate those values.

## Normative-semantics direction

If adopted, foreach should be a declarative source-level construct whose meaning
is defined by equivalence to the existing typed dependency graph. It should not
create a second scanner execution model.

A scanner MAY execute foreach directly for efficiency, but its behavior must be
equivalent to the defined graph/desugaring semantics, including collection
status, six-state truth, cardinality, provenance, and aggregation.

This lets:

- authors read a requirement-oriented representation;
- the converter retain a lossless semantic IR;
- modernization prove a bounded graph rewrite;
- implementations continue to use the existing dependency planner.

## Binding identity and evidence

Prefer binding a complete source Item rather than only a scalar value:

```yaml
for_each:
  source:
    object: users
  as: user
```

Then references such as `user.home_dir`, `user.username`, and `user.user_id`
retain correlation because they originate from one Item. This is safer than
independently projecting several arrays and later attempting to zip them.

Result evidence should be able to retain:

- source Object identity;
- source Item reference/key;
- projected field/value used by the child selection;
- resulting child Item references;
- collection status/completeness;
- decisive failures.

Evidence caps may limit retained samples but SHALL NOT change the verdict.

## Modernization classifications

The modernization analyzer should emit one of:

- **safe_automatic** — a reviewed rewrite rule matched and all semantic
  preconditions were proven;
- **review_required** — a plausible simplification exists but at least one
  semantic dimension is not proven;
- **not_applicable** — no useful foreach pattern exists;
- **blocked** — source defect, unsupported/deprecated construct, or semantic
  ambiguity prevents modernization.

Every applied rewrite should record a machine-readable transformation ID and
source-node provenance so it can be audited or reversed to the faithful form.

## Required equivalence tests

Before any foreach rewrite is eligible for `safe_automatic`, focused fixtures
should cover at minimum:

1. zero source Items;
2. exactly one source Item;
3. multiple source Items;
4. duplicate projected values;
5. source collection `error`, `incomplete`, `does_not_exist`, and
   `not_collected`;
6. target child collection with zero Items for one binding but Items for another;
7. child collector error for one binding;
8. source Sets and include/exclude Filters;
9. all relevant Test `check_existence` values;
10. all relevant Test `check` quantifiers;
11. State `entity_check` and Variable `var_check` where they remain in the
    graph;
12. decisive-evidence equivalence;
13. ordering/multiplicity cases where the source primitive defines them.

A transformation passes only when faithful and modernized representations
produce the same normative verdict and equivalent decisive evidence for the
covered semantic space.

## Candidate implementation architecture

Keep the modernization engine downstream of semantic IR construction:

```
semantic IR
  -> faithful native lowering
  -> pattern matcher
  -> proof/precondition report
  -> foreach rewrite
  -> equivalence comparator
```

The pattern matcher should operate on semantic nodes, not XML syntax or IDs.
A source can therefore match even when publishers use different OVAL IDs or
decomposition styles.

The modernization output should be deterministic. If preconditions are not
satisfied, it must fail closed and retain the faithful form.

## Next research steps

1. Build minimal fixtures for collection-expansion versus evaluation-iteration
   semantics, starting with the RHEL home-directory pattern.
2. Audit RHEL 9 and Solaris production graphs for direct
   `object_component -> var_ref Object selector` patterns.
3. Partition candidates by scalar projection, mapped function, multi-source
   Cartesian function, Set/Filter dependency, and State-variable use.
4. Define exact empty/error/multiplicity behavior for collection expansion from
   OVAL 5.12.3 and the existing NG result model.
5. Prototype a semantic-IR detector that reports candidates without rewriting.
6. Compare candidate counts and complexity reduction before proposing schema
   syntax.
7. Only after those proofs, prepare a human review packet for any 0.3.0 language
   addition.

## Human status

`pending-review`

No schema or accepted specification change is made by this research record.
