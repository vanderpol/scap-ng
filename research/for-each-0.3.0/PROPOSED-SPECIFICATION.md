# Proposed SCAP-NG 0.3.0 value-flow and scoped-iteration specification

**Status:** proposed 0.3.0 normative design derived from corpus research.
**Branch:** research/for-each-audit-20261006.
**Compatibility:** does not change frozen 0.2.0 semantics.

This document is the authoritative proposal for the value-flow / scoped-iteration
research track. Supporting corpus notes and counterexamples remain evidence, not
parallel normative specifications.

## Standards authority and implementation evidence

The authority order for this proposal is:

1. pinned OVAL 5.12.3 XSD;
2. pinned OVAL 5.12.3 Schematron;
3. normative OVAL 5.12.3 schema/prose semantics and documented standards decisions;
4. production SCAP 1.4 corpus evidence;
5. independent evaluator behavior such as OpenSCAP, ovaldi, SCC, or other implementations.

Implementation behavior is supporting evidence only. It SHALL NOT override a
clear standards requirement.

OpenSCAP is useful for differential experiments, but this project SHALL NOT
treat OpenSCAP as normative authority for OVAL 5.12.3. In particular, an
OpenSCAP result, validation result, or implementation limitation SHALL be
recorded as implementation evidence and compared with the pinned OVAL 5.12.3
contract before it influences SCAP-NG semantics.

If implementation behavior and the authoritative OVAL 5.12.3 contract disagree,
the migration specification SHALL preserve the standards-defined behavior unless
an explicit governance decision intentionally chooses a native divergence.

A differential test MAY therefore be classified as:

- standards-confirming implementation evidence;
- implementation divergence;
- unsupported-version/tooling limitation;
- unresolved behavior requiring further standards evidence.

It SHALL NOT silently become a normative rule merely because one evaluator
behaves that way.


## 1. Conclusion

SCAP-NG 0.3.0 SHOULD distinguish two concepts that OVAL commonly expresses
through Variables:

1. **flattened value projection** — obtain a value set from fields of Items
   produced by an Object without retaining originating Item identity;
2. **scoped Item binding** — retain one Item's identity while evaluating
   dependent logic for that Item.

These concepts SHALL NOT be conflated.

The proposed native authoring model is:

> Objects identify populations. Bindings identify Items. Variables represent
> named inputs, reusable value sets, or meaningful value transformations.

A multi-valued Variable SHALL NOT imply iteration or correlation.

The lossless converter SHALL NOT automatically rewrite existing OVAL
value-set dataflow into scoped iteration unless a future P2 equivalence class
passes the proof gates in this document.

## 2. Evidence basis

The pinned current NIWC SCAP 1.4 corpus at revision
8c8e5dff860af6b1290ee9273a282db24278f8d5 contains 65 signed benchmark
packages. The completed census examined 7,344 per-rule/platform OVAL closures.

Observed structural signals:

- 396 closures contain dependent-dataflow candidates;
- 388 contain a Variable-derived Object dependency;
- 70 contain multi-level dependent Object paths;
- 120 contain multiple projections from one source population;
- 3 contain same-Item multi-field correlation risk.

The three same-Item cases are the same audit-partition arithmetic pattern reused
by RHEL 9, Oracle Linux 9, and Amazon Linux 2023.

Across benchmark-local unique Variables the census found:

- 2,285 total Variables;
- 541 constants;
- 434 external Variables;
- 204 pure Object-field projections;
- 1,106 transformations.

After direct Variable-Test consumers and reuse were accounted for, 162 pure
Object-field Variables were single-use Object-selector or State-expected-value
plumbing candidates. Five additional pure projections feed one Variable
expression and remain a separate proof class.

These are corpus counts, not claims that every candidate may be removed.

## 3. Terminology

### 3.1 Object

An **Object** is an authored typed population selector/acquisition declaration.

### 3.2 Collection execution

A **Collection execution** is the runtime evaluation of an Object that produces
zero or more Items plus status/completeness information. Collection is not a
new authored node name.

### 3.3 Item

An **Item** is one collected observation produced by Object collection.

### 3.4 Binding

A **Binding** gives one Item lexical identity within a scoped Test.

A Binding preserves the relationship among fields belonging to that Item.

### 3.5 Projection

A **Projection** derives a value set from one field of zero, one, or many Items
produced by an Object and deliberately does **not** preserve originating Item
identity.

### 3.6 Variable

A **Variable** is a named typed value-set node. It may represent an input,
constant/reusable value set, or value transformation.

A Variable SHALL NOT carry lexical Item identity.

## 4. Native Variable boundary

Native authors SHOULD retain a named Variable when the value is:

- an external/organizational input;
- reused by more than one semantic consumer;
- the direct subject of a Variable Test;
- a meaningful named transformation or policy value;
- independently useful for results/provenance.

Native authors SHOULD NOT be required to create a named Variable solely to
project one Object field into one Object selector or State expected value.

A Variable SHALL NOT be interpreted as:

- a loop declaration;
- a lexical binding;
- an implicit zip between equal-length value sets;
- a mechanism that preserves which source Item produced a projected value.

OVAL-compatible Variable functions SHALL retain their defined value-set
semantics, including Cartesian-product behavior where applicable.

## 5. Flattened Projection value source

### 5.1 Proposed authoring form

A value position that can consume a Variable value set MAY consume a Projection:

    value:
      projection:
        object: discovered-config-paths
        field: subexpression

Record-field extraction MAY be expressed as:

    value:
      projection:
        object: query-results
        field: result
        record_field: path

The final YAML spelling is subject to the 0.3.0 vocabulary/schema review, but
the semantic node projection(object, field, record_field?) is normative in this
proposal.

### 5.2 Projection semantics

A Projection SHALL have the same value-producing semantics as OVAL 5.12.3
ObjectComponentType for migrated content:

1. The referenced Object SHALL be evaluated using its ordinary collection
   semantics.
2. If zero Items are available from the referenced Object, Projection
   resolution SHALL be error.
3. Every considered Item SHALL contain at least one entity matching field.
   A missing field SHALL make Projection resolution error.
4. If record_field is present, every considered record entity SHALL contain
   the requested record field. A missing record field SHALL make Projection
   resolution error.
5. All matching values SHALL contribute to one flattened value set.
6. Projection SHALL NOT retain source-Item identity as semantic correlation.
7. The Projection's effective datatype SHALL be compatible with the consuming
   value position.
8. The consuming entity's value-set comparison quantifier SHALL apply exactly
   as it would to an equivalent Variable value set.
9. Collection error/unknown/not-collected/not-applicable status SHALL propagate
   according to the applicable Assessment semantics; it SHALL NOT be converted
   into an empty value set.

### 5.3 Projection is not a Binding

For Items:

    user-1: { username: alice, home: /home/alice }
    user-2: { username: bob,   home: /home/bob }

a Projection of home produces the value set:

    [/home/alice, /home/bob]

It does not represent the relationships:

    user-1 -> /home/alice
    user-2 -> /home/bob

Content that requires those relationships SHALL use Binding/scoped iteration.

## 6. P1 automatic Projection normalization

A converter MAY automatically replace a named OVAL local Variable with a
Projection only when all of the following are machine-proven:

1. the Variable is a local_variable;
2. its complete expression root is exactly one object_component;
3. the referenced Object and requested item_field/record_field are preserved;
4. the Variable has exactly one semantic consumer after full graph closure and
   benchmark-local deduplication;
5. that consumer is an Object entity or State entity value position;
6. the Variable is not the direct source of a Variable Test;
7. the Variable is not the source of a variable_object or analogous first-class
   Variable-backed Test/Object construct;
8. no Variable component, filter, Set, dependency, or other reachable node also
   references it;
9. datatype is preserved exactly;
10. the consumer's operation and value-set quantifier are preserved exactly;
11. the Projection implements the zero-Item, missing-field, record-field, and
    status rules in section 5;
12. source Variable identity/comment/version are retained in migration
    provenance even though the executable native Variable node is removed.

A failure of any precondition SHALL cause the converter to preserve the named
Variable.

This transformation is **P1 structural normalization**. It does not create Item
scope and is not for_each.

## 7. Scoped iteration

### 7.1 Purpose

Scoped iteration is used when assessment truth depends on the identity of a
specific originating Item while dependent logic is evaluated.

The canonical use case is:

> For each interactive user, evaluate that user's home directory against data
> belonging to that same user.

### 7.2 Proposed Test form

A Test MAY declare one or more ordered for_each scopes before its ordinary
Object/State evaluation.

Illustrative source:

    objects:
      interactive-users:
        object_title: interactive local users
        capability: unix.password
        ...

    tests:
      home-primary-group-correct:
        test_title: each interactive user's home has that user's primary group
        capability: unix.file

        for_each:
          - binding: user
            object: interactive-users
            check_existence: at_least_one_exists
            check: all

        object:
          object_title: bound user's home directory
          capability: unix.file
          select:
            filepath:
              operation: equal
              datatype: string
              value:
                binding: user
                field: home_dir

        states:
          - state_title: home group matches bound user's primary group
            group_id:
              operation: equal
              datatype: integer
              value:
                binding: user
                field: primary_gid

        check_existence: at_least_one_exists
        check: all

The exact capability field names in this example are illustrative. The scope,
Binding, and aggregation semantics are the proposal.

### 7.3 Lexical scope

For each for_each entry:

- binding SHALL be a non-empty local name;
- Binding names SHALL be unique within one Test;
- Binding shadowing SHALL NOT be permitted;
- a Binding becomes visible after its scope source is established;
- an outer Binding MAY be referenced by later nested scope Objects and by the
  final Test Object/States/value expressions;
- an inner Binding SHALL NOT be visible before its declaration;
- a Binding SHALL NOT escape the Test that declares it.

A top-level reusable Object, State, or Variable SHALL NOT implicitly depend on a
Binding.

If an Object or State requires a Binding value, that Object or State SHOULD be
private/embedded within the scoped Test unless a future explicit parameterized
node contract is standardized.

### 7.4 Binding value reference

A Binding field MAY be used in a typed value position:

    value:
      binding: user
      field: home_dir

A record field MAY additionally identify record_field.

Binding reference semantics:

1. the named Binding SHALL be in lexical scope;
2. the requested field SHALL exist on the bound Item;
3. datatype SHALL be compatible with the consumer;
4. missing/error-valued fields SHALL produce an explicit evaluation error;
5. repeated field values remain a value set and SHALL use the consuming
   value-set quantifier where required;
6. the Binding retains Item identity even when the field value is equal to a
   value from another bound Item.

### 7.5 Nested scopes

for_each is an ordered outer-to-inner scope list.

Example:

    for_each:
      - binding: user
        object: interactive-users
        check_existence: at_least_one_exists
        check: all

      - binding: file
        object:
          object_title: files in bound user's home
          capability: unix.file
          select:
            path:
              value:
                binding: user
                field: home_dir
        check_existence: at_least_one_exists
        check: all

The second scope is evaluated independently for each user.

The final Test is evaluated independently for each complete Binding chain.

SCAP-NG SHALL NOT define general while, recursion, mutable variables,
assignment, break, continue, or arbitrary procedural control flow as part of
scoped iteration.

## 8. Scoped aggregation

Every scope SHALL explicitly define:

- source existence semantics (check_existence or the final 0.3.0 canonical
  equivalent);
- result aggregation semantics (check or the final 0.3.0 canonical equivalent).

Hidden defaults SHALL NOT be used.

For a complete source population, scope check SHALL aggregate the six-state
outcomes produced by evaluating the remainder of the scope/Test using the same
canonical result-combination semantics adopted for Test check.

Source existence SHALL be evaluated before body aggregation.

If source existence resolves false/error/unknown/not-evaluated/not-applicable,
the scope SHALL return that outcome and need not evaluate child scopes.

If the source population is zero, the scope result SHALL be determined by the
explicit source-existence rule; generic programming-language vacuous truth
SHALL NOT be used.

Exact enum token spelling remains tied to the 0.3.0 OVAL-to-NG vocabulary
alignment. The semantic scopes SHALL remain distinct even if vocabulary tokens
are renamed.

## 9. Partial populations and early termination

logical_complete, population_complete, and evidence_complete remain independent
dimensions.

An implementation MAY stop evaluation early only when unseen scope results
cannot change the selected aggregation.

At minimum:

- check=all: an observed false is logically decisive;
- check=at_least_one: an observed true is logically decisive;
- check=only_one: observing two true outcomes is logically decisive false;
- check=none_satisfy: an observed true is logically decisive false.

When evaluation stops because truth is decisive:

- logical_complete MAY be true;
- population_complete MAY be false;
- the final technical outcome MAY be true/false.

When evaluation stops because of timeout/resource/implementation limit before a
decisive result:

- logical_complete SHALL be false;
- population_complete SHALL be false;
- the technical outcome SHALL be an explicit non-success outcome according to
  the final result contract;
- the stop reason SHALL be recorded.

Migrated OVAL collected_object flag=incomplete semantics SHALL remain a separate
compatibility behavior and SHALL NOT be silently reused as native
evaluator-partial-population semantics.

## 10. Evidence and result model

Scoped iteration SHALL NOT create one Assessment Result or Rule Result per
Binding.

One Test Result SHOULD contain:

- final Test outcome;
- declared scope definitions;
- count of source Items/scoped evaluations where known;
- outcome counts by technical outcome;
- logical_complete;
- population_complete;
- evidence_complete;
- early-termination/resource-limit reason when applicable;
- bounded retained scope evidence.

A retained scope-evidence record SHOULD contain:

- result of that scoped evaluation;
- Binding name -> result-local Item reference for the relevant Binding chain;
- final/base Test Item references;
- structured failure reason;
- expected values that materially explain the failure;
- lineage references where useful.

Passing scope records need not all be serialized.

A collected physical Item SHOULD be materialized once per result-local
observation identity and MAY be referenced by multiple scoped evidence records.

Collection reuse SHALL NOT collapse distinct scoped relationship outcomes.

## 11. Lineage is not scope

A processor MAY retain non-semantic dataflow lineage such as:

    config-a -> /etc/target
    config-b -> /etc/target

without evaluating /etc/target twice or creating two semantic parent/child
relationships.

Lineage records explain derivation.

Bindings define semantic relationship scope.

The result model SHALL permit both concepts without conflating them.

## 12. Object collection reuse

Two scoped Object invocations MAY reuse one physical collection execution when
their effective collection semantics are equivalent, including:

- capability;
- selectors;
- behavior;
- privilege;
- target;
- effective bound values;
- relevant execution context.

Reuse SHALL NOT change:

- scoped truth;
- Binding identity;
- semantic relationship multiplicity;
- collection completeness;
- evidence attribution;
- sensitivity/redaction semantics.

## 13. Security requirements

Binding values SHALL be typed values.

A capability MAY permit a Binding value to populate typed selector fields such
as a filesystem path, account name, registry path, SID, certificate identifier,
or other declared data field.

A Binding or Projection value SHALL NOT be interpolated into executable shell,
SQL, script, or equivalent command text merely because it is a string.

Capabilities that support executable operations SHALL define explicit safe
parameter-binding semantics. General textual interpolation SHALL NOT be the
portable native authoring mechanism.

Implementations SHALL enforce dependency-depth and work/resource limits for
nested scopes.

Evidence-retention limits SHALL remain independent from execution-work limits.

## 14. Migration classes

The converter SHALL classify each relevant construct as one of:

### P0 — preserve

Preserve the source Object/Variable/State/Test graph and value-set semantics.

### P1 — proven structural normalization

Simplify syntax without adding Item identity or changing values, cardinality,
quantifiers, errors, flags, multiplicity, or status propagation.

The section-6 Projection rewrite is the first proposed automatic P1 class.

### P2 — proven scoped equivalence

Lower to for_each only when machine-checkable preconditions plus differential
execution prove complete equivalence for cardinality, duplicate/shared Items,
zero values, errors, incomplete state, quantifiers, functions, and results.

**No production OVAL pattern is currently approved as automatic P2.**

### P3 — correlation recommendation

Source/policy suggests a per-Item relationship but source OVAL does not encode
enough identity to prove it. Preserve source behavior and emit a modernization
recommendation.

### P4 — new native automation

A manual rule expresses a correlated requirement with no source OVAL
automation. A native scoped Test may be proposed for human review, but SHALL
NOT be described as lossless conversion.

## 15. Negative conversion examples

The following SHALL NOT be automatically converted to scoped iteration merely
because native scoped syntax is clearer:

- RHEL 9 SV-258155;
- Oracle Linux 9 SV-271596;
- Amazon Linux 2023 SV-274067.

These rules project block_size and total_space from the same partition Object
into an arithmetic Variable. OVAL collection-valued function semantics can form
a Cartesian product. Native same-Item arithmetic would add row correlation and
may change meaning.

Likewise, nested Apache/NGINX/config-discovery pipelines SHALL NOT become
for_each merely because they contain multiple dependent Objects. Most are
flattened value-flow/collection-planning problems unless policy truth depends on
the originating Item identity.

## 16. Positive native example family

The following recurring manual family strongly motivates scoped Binding:

- RHEL 9 SV-258053;
- Oracle Linux 9 SV-271783;
- SLES 12 SV-217174;
- SLES 15 SV-234994;
- Solaris 11 SV-216188;
- related older RHEL/Oracle controls.

The policy requires a home-directory property to match data belonging to the
specific account that names/owns that home directory.

This is a P4 native-automation family unless a future benchmark supplies source
automation with sufficient relationship semantics.

## 17. Conformance requirements

Before the feature is promoted to released schema/specification, conformance
fixtures SHALL cover at least:

1. one parent -> one child;
2. multiple parents with unequal child counts;
3. zero parent Items under each supported source-existence mode;
4. zero child Items;
5. shared child Item referenced by different parents;
6. duplicate equal values from distinct parent Item identities;
7. two and three nested Binding levels;
8. missing bound field;
9. repeated values in one bound field;
10. complete versus native partial population;
11. decisive early termination for each supported check;
12. resource limit before decisiveness;
13. evidence cap with unchanged truth;
14. one physical observation referenced by multiple scopes;
15. Projection zero-Item/missing-field/record-field errors;
16. Projection multi-Item flattening;
17. Projection consumer quantifiers;
18. direct Variable Test preservation;
19. OVAL Cartesian function negative case;
20. dynamic-command binding rejection;
21. dependency cycle/static scope rejection;
22. Binding shadowing rejection.

P2 automatic lowering SHALL additionally require differential execution against
the source OVAL for the complete proof family.

## 18. Recommended 0.3.0 adoption

The recommended 0.3.0 direction is:

- adopt Projection as a first-class flattened value source;
- permit automatic P1 normalization only for fully proven single-use
  object_component plumbing;
- adopt lexical scoped for_each as a native authoring/evaluation construct;
- keep named Variables for inputs, reuse, direct Variable Tests and meaningful
  transformations;
- prohibit treating multi-valued Variables as implicit loops;
- keep automatic OVAL -> for_each lowering disabled until a P2 class is
  independently proven;
- support P3 modernization advisories and P4 reviewed native automation;
- extend Results with compact scope summaries and bounded Binding evidence.

## 19. Deliberately deferred details

The following remain 0.3.0 specification/editor/schema work rather than settled
research conclusions:

- final enum token spelling from the full OVAL-to-NG vocabulary audit;
- final YAML property spelling if Board review favors alternatives to
  projection, for_each, or binding;
- whether inline transform expressions beyond Projection are adopted;
- parameterized reusable named Objects that accept Bindings;
- exact JSON Result serialization for scope summaries;
- whether any production source pattern can satisfy automatic P2 lowering.

Those deferred choices SHALL NOT reopen the semantic distinction between
Projection, Binding, Variable, lineage, and collection reuse unless new evidence
demonstrates that the distinction is incorrect.
