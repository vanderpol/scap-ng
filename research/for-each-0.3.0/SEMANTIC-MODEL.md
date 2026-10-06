# Scoped iteration semantic model - research draft for SCAP-NG 0.3.0

Status: research only. No syntax here is normative.

## Core boundary

- Collection acquires typed Items.
- Binding gives one Item lexical identity inside a scope.
- Variable carries or transforms typed values.
- Iteration repeats a scoped assessment body over bound Items and combines scoped outcomes explicitly.

Working shorthand: Bindings identify Items. Variables derive values.

A multi-valued Variable is not automatically an iteration.

## Why OVAL cannot be blindly rewritten

OVAL object_component projects one field from zero, one, or many collected Items into a value collection. Functions over collection-valued components may use Cartesian-product semantics. Object and State var_ref compare entities against value collections using var_check. Those semantics do not retain a general lexical parent identity.

Therefore a converter SHALL NOT infer parent-child correlation merely because values originated from the same Object.

## Initial native iteration shape

The first scoped-iteration construct SHOULD produce scoped assessment outcomes, not act as a generic flatMap or arbitrary Collection producer.

Conceptually:

    for each user in interactive_users:
        home = collect file(path = user.home_dir)
        require home.group_id == user.group_id

The bound user remains one Item whose fields stay correlated.

Nested iteration may reference outer bindings.

No mutation, assignment, counters, recursion, break, continue, or arbitrary control flow.

## Required semantics before standardization

### Source population and identity

The source is a typed Collection of Items. Source order SHOULD be semantically irrelevant. Duplicate Item identity and imported/reused Item behavior must be defined.

### Outcome aggregation

Aggregation SHALL be explicit during research. We should reconcile names with the 0.3.0 OVAL-to-NG vocabulary audit rather than invent new synonyms.

At minimum we need semantics equivalent to all, at-least-one, none, and justified cardinality constraints.

### Zero Items

Zero-source semantics SHALL be explicit and SHALL NOT be inferred from generic Boolean vacuous truth. Existing NG/OVAL existence and status semantics must remain distinguishable.

### Errors and incomplete Collections

Error, incomplete, does-not-exist, not-collected, unknown and not-applicable behavior must be specified for each aggregation.

### Truncation and evidence caps

Evidence caps SHALL NOT change truth semantics.

For all: an observed failure can be conclusive, but observed passes cannot prove success if unseen Items remain.

For at-least-one: an observed pass can be conclusive, but observed failures cannot prove failure if unseen Items remain.

### Duplicate child Items across parents

This is a critical conversion distinction.

If parent A and parent B both select child X, correlated iteration may legitimately represent two relationship evaluations:

    A -> X
    B -> X

A flattened OVAL-derived Collection may represent X once.

Automatic conversion SHALL NOT introduce parent grouping when doing so changes multiplicity, deduplication, aggregate truth, or status propagation.

Required fixtures include shared children, overlapping child sets, and duplicate values from distinct parent Item identities.

### Same-Item field operations

A binding naturally supports operations such as:

    partition.block_size * partition.total_space

That is different from separately projecting block_size values and total_space values and applying OVAL collection-valued function semantics.

Replacing an OVAL Cartesian-product expression with same-Item arithmetic is a semantic correction, not a lossless conversion, unless equivalence is independently proven.

### Results and evidence

Results SHOULD retain enough iteration context to explain which parent and child caused failure without serializing every bound field.

Nested evidence should answer:

- which parent failed;
- which child failed;
- which parent-derived value was expected;
- whether evidence was capped;
- whether evaluation was incomplete.

### Early termination

An evaluator MAY terminate once the selected aggregation is logically conclusive, provided unseen Items cannot change the result and completeness/early-termination metadata remains explicit.


## Result cardinality and invocation boundary

Scoped iteration is internal evaluation within one Assessment invocation unless
the authored policy explicitly defines independently reported invocations.

A processor SHOULD NOT create one Assessment Result artifact or one Rule-result
instance for every bound Item. Doing so would make high-cardinality filesystem,
account, registry, or package checks produce result explosions.

Instead one Assessment Result should retain:

- aggregate scoped evaluation counts;
- logical/population/evidence completeness;
- bounded failing or decisive scope records;
- parent/child binding context needed to explain retained failures;
- optional summaries by outer scope when useful.

Passing scopes need not all be serialized merely because they were evaluated.

This keeps iteration compatible with the existing evidence-maximum and decisive-
expression result model while preserving enough relationship context to explain
why a rule failed.


## Resource and execution safety

Scoped iteration can amplify collection cost, especially when nested. A native
scanner therefore needs bounded execution semantics that are independent from
evidence-retention limits.

The standard should distinguish at least:

- collection/evaluation work limits;
- maximum retained evidence;
- semantic aggregation requirements;
- implementation safety/resource policy.

A resource limit reached before truth is conclusive SHALL produce an explicit
incomplete/error-style outcome according to the final result model; it SHALL
NOT be treated as ordinary evidence truncation.

Bound fields also create a security concern when consumed by executable
capabilities. A binding reference used as a filesystem path or typed comparison
value is not equivalent to textual interpolation into a shell, SQL, script, or
other executable expression.

Native source SHOULD require capability-defined safe parameter binding for any
bound value that can influence executable text. General string interpolation
from a bound Item into command text SHOULD NOT be the default authoring model.

Nested iteration also needs implementation limits for dependency depth and
population expansion so malicious or accidental content cannot create an
unbounded evaluation bomb.


## Scope, lineage, and collection invocation are different concepts

The corpus study shows that a native evaluator needs to keep three identities
separate:

1. **Semantic scope/binding** — a parent Item is lexically bound because the
   truth of a child evaluation depends on that specific parent.
2. **Dataflow lineage** — an upstream Object/Variable/value explains why a
   downstream Item became reachable, but does not create a new semantic
   evaluation relationship.
3. **Collection invocation** — one execution of a Collection template with one
   effective selector/input binding set.

These identities SHALL NOT be conflated.

### Lineage without semantic iteration

A flattened value-set dependency can legitimately have two upstream derivations
for one downstream Item:

    config-a -> /etc/target
    config-b -> /etc/target

The downstream Item may still be evaluated once. Results MAY retain both
lineage edges for diagnosis without pretending there were two scoped compliance
relationships.

This is an important route to better converted-content results that does not
change OVAL truth semantics.

### Scoped relationships with shared observations

A true correlated requirement can have two parent bindings that resolve to the
same physical child:

    alice(expected_gid=100) -> /shared
    bob(expected_gid=200)   -> /shared

If /shared has gid 100, acquisition of the directory can be reused, but the two
relationship evaluations are semantically distinct: alice passes and bob fails.

A scanner SHOULD be able to store/reuse one immutable collected observation and
reference it from multiple scoped relationship results. Collection reuse SHALL
NOT collapse the parent bindings or their expected values.

### Parameterized Collection invocation identity

A Collection used inside a scope behaves conceptually as a typed Collection
template plus effective bound selector values. Implementations MAY cache/reuse
collection work when two invocations have equivalent capability, selector,
behavior, input, privilege, and target semantics.

Cache/reuse identity SHALL be based on those effective collection semantics, not
merely on source syntax or parent binding identity.

Reusing acquisition work SHALL NOT change:

- scoped truth;
- multiplicity of semantic relationships;
- collection completeness/status;
- evidence attribution;
- sensitivity/redaction requirements.

The final result schema should permit a compact structure in which collected
observations are normalized once and scoped outcomes reference them by stable
result-local identity.


## Production proof families

### Manual correlation - new native expressiveness

Confirmed recurring family:

- RHEL 9 SV-258053
- Oracle Linux 9 SV-271783
- SLES 12 SV-217174
- SLES 15 SV-234994
- Solaris 11 SV-216188
- older RHEL and Oracle equivalents

These require a home-directory property to match the specific account that names or owns that home.

These are native-automation candidates, not lossless automated conversions, when no source OVAL automation exists.

### Automated same-Item expression risk

- RHEL 9 SV-258155
- Oracle Linux 9 SV-271596

These project multiple partition fields into a Variable expression. They are important negative conversion cases because native same-Item arithmetic is clearer but is not automatically equivalent to OVAL collection-valued function semantics.

### Automated nested dependent dataflow

Solaris 11 includes several three-stage account/home/file dependency chains:

- SV-216181
- SV-216183
- SV-216184
- SV-216195
- SV-216196

These test nested scope, flattening, zero-value behavior, shared child Items, and evidence grouping.

### Value-set fanout - preserve by default

Many RHEL, Oracle, SUSE, Ubuntu, Windows and application rules derive paths or values from one Collection and use them to select another. Examples include dconf directories, audit-log locations, sudoers include files, faillock directories and configuration-derived paths.

These are a control group: dependent dataflow is not automatically correlated iteration.

## Conversion proof classes

P0 preserve:
Source uses value-set semantics and no scoped equivalence proof exists.

P1 structural simplification:
Syntax may be simplified without adding parent identity or changing value sets, quantifiers, flags, multiplicity, or status propagation.

P2 scoped iteration equivalence proven:
Every relevant source semantic is equivalent to the bound/scoped form, including cardinality, duplication, zero values, errors, incomplete status, quantifiers, and functions. Only P2 can be automatically lowered to scoped iteration.

No production P2 pattern is declared yet.

P3 likely intended correlation:
Policy or graph suggests per-parent correlation but source semantics are insufficient to prove it. Preserve source behavior and emit advisory review.

P4 manual native automation candidate:
Policy/manual procedure expresses a correlated requirement with no source OVAL automation. Native automation may be proposed for author approval but SHALL NOT be labeled a lossless conversion.

## Minimum automatic-lowering gate

For every proposed P2 rewrite class:

1. Define machine-checkable source preconditions.
2. Define exact target iteration semantics.
3. Cover all relevant quantifier/cardinality truth cases.
4. Test zero, one, and many source Items.
5. Test unequal child cardinalities.
6. Test shared and duplicate child Items.
7. Test error, incomplete, does-not-exist, not-collected and unknown.
8. Test evidence capping independently of truth.
9. Round-trip where a reverse representation exists.
10. Differentially execute source OVAL and target NG against controlled fixtures.

Until those gates pass, the planner remains advisory.
