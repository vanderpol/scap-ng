# Board Review: Collection Identity and Reuse

**Status:** proposed SCAP-NG execution rule derived from OVAL collection semantics.

## Schema-derived foundation

OVAL System Characteristics identifies collected object instances by object ID,
version, and variable_instance. It also records the actual variable values used
during collection, including variables reached through referenced sets.

The schema documentation explicitly recognizes that the same OVAL Object may
produce different matching item sets when variable values differ.

Therefore collection reuse is safe only when the effective collection request
is semantically identical.

## Proposed NG rule

A scanner SHOULD collect a semantically identical Collection only once per
assessment execution context and MAY reuse the resulting items for all consumers.

Two Collection requests SHALL be considered reusable only when their fully
resolved collection semantics are equivalent.

The equivalence calculation must include, as applicable:

- collection capability/type;
- all selector/entity operations and values;
- resolved Variable values and cardinality;
- collector behaviors/options and schema defaults;
- nested Set structure and set operators;
- referenced Collections;
- Filters and their include/exclude actions;
- resolved Filter/State predicates, including Variables used by those predicates;
- datatype/operation semantics;
- platform/execution context when it can alter collection results; and
- any other schema-defined property that can alter the matching item set or
  collection status.

Human-readable labels, provenance, comments, and source identifiers do not by
themselves alter semantic collection identity.

## Identity is after resolution

Collection identity SHALL be determined from normalized/resolved semantics, not
from raw source text or YAML structure.

For example, two source Collections that both reference the same Variable are
not necessarily reusable across executions if that Variable is externally bound
to different values.

Likewise, two Collections with identical base selectors but different Filters
are not the same effective Collection result.

## Base collection versus filtered view

NG SHOULD distinguish between:

1. a **base collection operation** that obtains candidate target items; and
2. a **derived/filtered collection view** that applies filters/set semantics.

An implementation MAY optimize by reusing a common base collection and applying
different filters locally when doing so preserves all schema-defined behavior.

However, such optimization is implementation-internal. The logical identity of
the filtered Collections remains distinct.

## Cache key concept

Implementations SHOULD be able to derive a deterministic semantic fingerprint
from the fully resolved Collection dependency graph.

Conceptually:

    semantic-collection-key =
      hash(
        capability
        + normalized selectors
        + resolved variable bindings
        + behaviors/defaults
        + set semantics
        + filter semantics
        + relevant execution context
      )

The specification need not mandate a cryptographic hash representation, but it
should define the semantic equivalence inputs.

## Board questions

1. Should NG normatively require scanners to avoid duplicate collection for
   semantically identical resolved Collections, or merely recommend it?
2. Which exact properties form Collection semantic identity?
3. Should the spec explicitly distinguish base collection reuse from filtered
   Collection identity?
4. Should results expose a Collection instance/fingerprint so multiple Checks
   can show that they consumed the same collected evidence?
5. How should externally supplied Variable values scope Collection cache
   identity and lifetime?

## Initial recommendation

Define semantic Collection equivalence normatively and state that scanners
SHOULD reuse a Collection result when equivalence is proven.

Do not permit reuse when equivalence cannot be proven.

Permit internal reuse of a broader base collection for multiple filtered views
only when the implementation can guarantee identical observable semantics.


## Scope correction: no snapshot-consistency guarantee

SCAP-NG SHALL NOT require a scanner to provide a coherent snapshot of target
configuration across an Assessment run.

Target configuration may change at any time. A Collection or Check reflects the
target state observed at the time that operation is performed.

Two semantically identical Collections evaluated at different times MAY
therefore legitimately observe different target data if the target changed
between evaluations.

Collection caching, reuse, deduplication, scheduling, and synchronization are
implementation concerns unless an optimization changes the correctness of the
individual operation being evaluated.

The core specification should define the semantics of each Collection, Variable,
Check, and aggregate result, but SHOULD NOT require:

- collection-result caching;
- duplicate-collection suppression;
- assessment-wide snapshot isolation;
- a shared observation timestamp across independent Checks; or
- deterministic equality between observations made at different times.

Results SHOULD retain sufficient per-check/per-evidence timing metadata to make
the observation time understandable where timing is relevant, but timing does
not imply snapshot consistency.

Accordingly, the earlier proposal for normative semantic collection identity or
mandatory reuse is downgraded to implementation guidance. Vendors MAY optimize
collection reuse when safe and useful.
