# Foreach modernization research

**Status:** v1 collection-expansion authoring and validation integrated into the
active 0.3.0 pre-alpha tree. The converter now has an explicit opt-in 0.3.0 modernization pass for the exact
v1 proof class, including a pinned RHEL production-source regression. Automatic
modernization remains disabled by default pending broader authoring-language review.
The frozen 0.2.0 language and schemas remain unchanged.

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
      item: user
      in: non_system_users
    select:
      directory:
        from: user.home_dir
      name:
        operation: match
        value: '^\\.[^\\s\\.]+'
```

Object-level `for_each` v1 has one intrinsic meaning: collection expansion
whose child Items form one combined target Object population. The author does
not spell `collect: union` because v1 offers no alternate collection mode;
this is grammar semantics rather than a hidden default.

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
  item: user
  in: users
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


## Canonical evidence-equivalence contract

The native foreach representation does not need to reproduce every faithful
Variable/result serialization detail byte-for-byte, but it must preserve the
same decisive evidence.

For the first direct projection class, faithful and modernized Results SHALL be
reducible to the same canonical evidence view containing:

- source Object identity;
- source Item identities consumed by the projection;
- each projected source field/value paired with its source Item identity;
- projection/value-production status;
- the combined target Item population used by the existing Test boundary.

The canonical view deliberately does **not** require a parent-value -> child Item
correlation unless the faithful result actually established that relationship.
Inventing such a correlation would add unsupported meaning.

Duplicate projected values are retained with their distinct source Item
identities in the provenance view even though duplicates do not change
`var_check="at least one"` selector truth.

Focused fixtures fail closed if the faithful Variable values cannot be
reconstructed from its recorded source `item_refs` and source Item fields, or
if the modernized target Item population differs.


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

## Current integration state and next steps

Completed for 0.3.0:

1. opened a complete independent `schema/v0.3.0/` tree without modifying
   frozen 0.2.0;
2. added Object-level `for_each` / selector `from:` structural primitives;
3. added cross-Object alias, field, direct-Test, and datatype-compatibility
   semantic validation;
4. made capability-registry and deep schema validation version-aware so 0.3.0
   resolves only its own schema/mapping catalog;
5. added an end-to-end 0.3.0 authoring fixture using the simplified syntax;
6. retained the faithful Object -> ObjectComponent -> Variable -> Object graph
   as the normative semantic oracle;
7. kept all frozen-0.2 regression, Board conversion, and smoke gates green.

Next:

1. integrate the exact v1 rewrite into the SCAP 1.4 converter as an explicit,
   fail-closed modernization pass;
2. initially keep that converter modernization opt-in / disabled by default;
3. compare faithful and modernized converted output plus canonical evidence for
   the five pinned production candidates;
4. enable `safe_automatic` only after the integrated converter path passes
   those gates;
5. keep fan-out, helper-target, record-field, alternate-quantifier, derived
   expression, and evaluation-iteration shapes as separate later proof classes.


## Current recommendation

The semantic proof for the narrow first class is complete enough to move from
OVAL-algebra research into human language review.

Proposed specification:
[PROPOSED-SPEC.md](PROPOSED-SPEC.md)

Human review packet:
[REVIEW.md](REVIEW.md)

Machine-readable rewrite contract:
[transformation-v1.json](transformation-v1.json)

Pinned production proof:
[PRODUCTION-PROOF.md](PRODUCTION-PROOF.md)

Research-only schema/lowering prototype:
[prototype/](prototype/)

The recommendation is to review **collection-expansion foreach v1** as a
0.3.0 language addition with the exact transformation identifier
`foreach.direct-object-component.at-least-one.v1`.

Automatic rewriting remains disabled until the syntax and normative wording are
accepted. Eligible analyzer hits remain `review_required`.


## Human status

`v1-ready-for-0.3.0-integration-review`

No schema or accepted specification change is made by this research record.
