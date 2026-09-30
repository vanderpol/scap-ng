# Iteration 003 Variable and Dataflow Requirements

**Status:** schema-derived design requirements; native syntax is not yet final.

## Source of truth

The requirements in this document are derived from the pinned SCAP 1.4 / OVAL
5.12.3 XSD and Schematron corpus.

XSD and Schematron are authoritative for compatibility. Production content is
used to identify important combinations and provide regression coverage, not to
define the language surface.

## Variables are normal assessment dataflow

SCAP-NG SHALL treat chained variables as a normal case rather than an edge case.

A native Assessment SHALL support arbitrarily deep dependency chains in which
named value-producing nodes can depend on:

- literals;
- external/user-provided values;
- values extracted from collected target objects/items;
- other variables;
- nested functions over any of the above.

A variable MAY feed another variable, which MAY feed another variable, and so
on. Implementations SHALL resolve dependencies by reference and SHALL NOT depend
on source-file order.

“Arbitrarily deep” describes the language's recursive expressiveness, not
unlimited implementation resources. It SHALL NOT be interpreted as a fixed
three-layer language limit. Implementation resource exhaustion SHALL be
reported separately from invalid source and SHALL NOT produce a partial
Assessment presented as successfully converted. Computation limits are distinct
from caps on reported evidence. Exact budgets and their configuration remain
under review in [issue #38](https://github.com/vanderpol/scap-ng/issues/38).

The current v003 feature-accounting pass is iterative. Native lowering still
uses recursive calls; exceeding Python's available recursion returns
`conversion_resource_limit:python_recursion` without an Assessment. This is an
implementation limitation, not a claim that the input violates OVAL.

Direct Variable self-reference remains prohibited as in OVAL. Whether SCAP-NG
SHALL reject every indirect cross-node dependency cycle is a working proposal
pending OVAL Board review; see `../board-review/dependency-ordering-and-cycles.md`.

## OVAL variable categories that must be preserved

OVAL 5.12.3 defines three variable forms:

- constant variables;
- external variables;
- local variables.

Local variables are defined by exactly one component or function expression.
That expression may recursively contain object components, variable components,
literal components, or nested functions.

SCAP-NG MAY use a cleaner native vocabulary, but lossless conversion SHALL
preserve the behavior of all three forms.

## Variables are multi-valued

An OVAL variable represents zero, one, or many values.

SCAP-NG SHALL therefore define variable/value nodes as collections of typed
values, even when a particular expression produces exactly one value in normal
use.

The native model SHALL preserve the distinction between:

- zero values;
- one value;
- multiple values;
- evaluation error;
- incomplete/not-collected conditions where they affect the consuming
  semantics.

A scalar-only variable model is insufficient for lossless OVAL conversion.

## Object-derived values

OVAL object_component semantics allow a local variable to obtain values from a
referenced Object by selecting:

- an item field; and
- optionally a field within a record-valued item entity.

The referenced Object may collect zero, one, or many Items, and an Item may
provide zero, one, or many matching entities.

Native SCAP-NG SHALL provide a reusable named collection/object concept or an
equivalent referenceable dataflow node so that object-derived values do not
require duplicating the complete collection definition in every variable that
uses it.

The native design SHOULD make the dependency visible to a human reviewer, for
example conceptually:

    interactive-users-collection
        -> interactive-uids-variable
        -> unique-uids-variable
        -> unique-uid-count-variable

The exact syntax remains open.

## Variables used by Objects and States

OVAL simple Object and State entities inherit variable-reference semantics.

SCAP-NG SHALL therefore permit a typed variable/value reference anywhere the
corresponding native Object selector or State predicate accepts a typed value,
except where the source schema explicitly prohibits variable references.

A variable reference is not merely an Assessment-expression feature. It can
participate directly in target collection and state comparison.

The converter SHALL preserve the different empty-variable behavior defined by
OVAL:

- when an Object entity references a variable that has no value, the Object is
  considered not to exist;
- when a State entity references a variable that has no value, evaluation is an
  error.

Errors computing a referenced variable SHALL propagate to the consuming entity
according to the source semantics.

## var_check and many-to-many comparison

When a referenced variable produces multiple values, OVAL var_check controls
how those values are combined during Object collection or State evaluation.

If var_check is absent while var_ref is present, OVAL specifies the effective
default as `all`.

For State entities that also correspond to multiple collected item entities,
entity_check and var_check form a two-level many-to-many comparison:

1. compare one collected item value against all referenced variable values and
   combine those comparisons using var_check;
2. combine the per-item interim results using entity_check.

SCAP-NG SHALL preserve this behavior explicitly. A generic list comparison with
unspecified quantification is not sufficient.

## Datatype consistency

A variable reference and the entity consuming it SHALL be datatype compatible
according to the XSD/Schematron rules.

OVAL prohibits var_ref on record-valued entities. Object-component extraction
may nevertheless select a field from a record through item_field plus
record_field.

SCAP-NG conversion SHALL distinguish those two cases.

## Functions and Cartesian products

OVAL functions can be nested recursively.

When function operands yield collections of values, OVAL function evaluation
may operate over the Cartesian product of the operand collections. For example,
arithmetic over values [1,2] and [3,4,5] produces six combinations.

SCAP-NG SHALL define deterministic collection/cardinality semantics for every
native expression operator used to preserve OVAL behavior.

The OVAL 5.12.3 FunctionGroup includes at least:

- arithmetic;
- begin;
- concat;
- end;
- escape_regex;
- split;
- substring;
- time_difference;
- regex_capture;
- unique;
- count;
- glob_to_regex;
- merge.

Lossless conversion SHALL support each non-deprecated source function used by
the supported SCAP/OVAL version or stop the affected Assessment with an explicit
diagnostic.

## Sets and filters participate in the same graph

OVAL Objects may be defined through nested sets of Object references, with
UNION/intersection/complement-style set operations as permitted by the schema,
and one or more filters.

Filters reference States. Those States may themselves contain variable
references. The Objects referenced by a set may likewise use variables.

Therefore sets, filters, collections, states, variables, and expressions SHALL
be resolved as one dependency graph rather than as independent conversion
features.

A valid dependency path may conceptually resemble:

    variable A
      -> object B selector
      -> collection B
      -> filter state C
      -> variable D
      -> object E
      -> variable F
      -> state G

provided that the dependency relationships are schema-valid. The proposed NG
rule that the complete executable dependency graph also be acyclic is pending
OVAL Board review.

## Execution model

The native execution model SHOULD be expressed as dependency-driven dataflow:

    resolve references
        -> validate types/cardinality
        -> detect prohibited/unresolvable dependency recursion
        -> collect target data
        -> derive dependent values
        -> apply collection/set/filter transformations
        -> evaluate states/assertions
        -> produce result/evidence

This is conceptual execution order, not required source serialization order.

## Naming

Every named/addressable native object SHOULD identify its type in its logical
identifier.

For variable nodes, identifiers SHALL include `variable`, preferably as a
suffix:

    interactive-uids-variable
    unique-uids-variable
    unique-uid-count-variable

The same global convention applies to other addressable native types such as
`-rule`, `-assessment`, `-check`, and `-collection`.

Type semantics SHALL come from the object declaration/schema, not by parsing
the identifier suffix. The suffix is an authoring/readability requirement.

## Conversion requirements

The converter SHALL NOT inline a shared collection or expression merely because
the source OVAL graph used a separate Object or Variable if doing so:

- duplicates meaningful computation;
- obscures dependency relationships;
- changes evaluation/error propagation;
- changes cardinality semantics; or
- makes a complex daisy-chained graph materially harder to review.

Conversely, the converter SHALL NOT preserve opaque OVAL object/variable IDs in
native source solely to mirror source decomposition.

The goal is a human-readable native dependency graph that is semantically
equivalent to the authoritative XSD/Schematron-defined source.

## Conformance strategy

Two complementary test corpora SHALL be used:

1. OVAL Self-Assertion content for systematic language/operator coverage; and
2. production SCAP content (including RHEL 9 and Windows 11) for realistic,
   deeply chained and cross-feature dependency graphs.

Coverage SHALL be measured against the XSD/Schematron language surface, not only
against constructs observed in one benchmark.


## Working decision: named Variables and inline expression trees

**Status:** working SCAP-NG design decision; SHALL be presented to the OVAL Board for review.

SCAP-NG SHALL follow the existing OVAL design principle that a named Variable
may contain a recursively nested expression tree.

Functions/components within a Variable MAY be nested inline and do not require
individual Variable identifiers merely because they produce intermediate
results.

A derived value that is referenced outside its containing expression tree SHALL
be promoted to a named Variable and its identifier SHALL include `variable`.

Authors MAY voluntarily promote any intermediate expression to a named Variable
for:

- reuse;
- readability;
- diagnostics;
- debugging; or
- breadcrumb-style dependency tracing.

For example, the compact form:

    unique-uid-count-variable:
      expression:
        count:
          unique:
            variable: interactive-uids-variable

and the breadcrumb form:

    unique-uids-variable:
      expression:
        unique:
          variable: interactive-uids-variable

    unique-uid-count-variable:
      expression:
        count:
          variable: unique-uids-variable

are semantically equivalent when the intermediate value is not otherwise
consumed.

Checks, Collections, States, Filters, and other Variables SHOULD consume named
Variables rather than embedding arbitrary expression trees directly at those
consumption sites. The expression tree belongs to the Variable definition.

### OVAL Board review question

Confirm whether SCAP-NG should retain this OVAL-derived model:

> A Variable is the named/addressable value node; its internal function/component
> expression may be arbitrarily nested. Intermediate expressions need not have
> IDs unless referenced externally, but authors may name them for reuse or
> debugging.

The board review should include both compact and breadcrumb examples and confirm
that no interoperability or diagnostics requirement justifies forcing every
intermediate expression to become a separately named Variable.


## Working decision: named and embedded Collections inside Variables

**Status:** owner-agreed working design, reconfirmed 2026-09-30; formal Board review is separate. Both forms SHALL be supported. This does not authorize erasing source sharing during lossless conversion.

SCAP-NG SHALL permit a Variable expression to obtain values either from:

1. a named reusable Collection; or
2. an inline local Collection defined inside that Variable when the collection
   is used only to produce that Variable's value.

Example using a named Collection:

    collections:
      interactive-users-collection:
        capability: unix.password
        ...

    variables:
      interactive-uids-variable:
        expression:
          values:
            collection: interactive-users-collection
            field: user_id

Example using an inline local Collection:

    variables:
      interactive-uids-variable:
        expression:
          values:
            collection:
              capability: unix.password
              select:
                username:
                  operation: pattern_match
                  value: ".*"
              filters:
                - action: include
                  match:
                    field: user_id
                    operation: greater_than_or_equal
                    value: 1000
            field: user_id

The inline form avoids forcing native authors to create a top-level Collection
that has no independent reuse or meaning outside the Variable.

A local inline Collection SHALL be scoped to the containing Variable and SHALL
not be referenceable by other nodes.

If a Collection is consumed by more than one Variable, Check, Filter, Set, or
other named node, it SHOULD be promoted to a named `*-collection`.

For SCAP 1.4 conversion, existing OVAL Object boundaries SHOULD remain named
Collections even when the resulting Collection has only one consumer. The
inline-local form is primarily an authoring convenience for new native NG
content and SHALL NOT be used by the converter to erase meaningful source graph
structure.

### Board review point

The OVAL Board should formally review the working design supporting both:

- named reusable Collections; and
- anonymous/local Collections scoped to a single Variable expression.

The proposed distinction is semantic reuse/scope, not capability. Both forms
would use the same Collection definition model and execution semantics.
