# Collection `for_each`

**Status:** accepted SCAP-NG 0.3 assessment-language requirement.

`for_each` expresses **collection expansion over collected Items**. It does not
mean "evaluate one Test per Item."

## Simple form

```yaml
shared_objects:
  users-object:
    capability: unix.password
    ...

  home-files-object:
    capability: unix.file
    for_each:
      item: user
      in: users-object
    select:
      directory:
        from: user.home_dir
```

`in` names one Assessment-scoped referenceable Object. `item` introduces a
lexical alias for one Item from that source. `from` binds a target selector to
one typed field of a visible alias.

The resulting target Items form **one Object population**. Existing Test
existence, State comparison, Test matching, and `evaluate` semantics operate on
that population unchanged.

## Nested correlated collection

A `for_each` Object MAY itself be the named source of another `for_each`
Object.

```yaml
shared_objects:
  zones-object:
    capability: windows.dns.zone
    ...

  hosts-object:
    capability: windows.dns.record
    for_each:
      item: zone
      in: zones-object
    select:
      zone:
        from: zone.name

  dnssec-response-object:
    capability: windows.dns.query
    for_each:
      item: host
      in: hosts-object
    select:
      name:
        from: host.fqdn
      zone:
        from: zone.name
```

The inner Object inherits the lexical lineage established by its source Object.
Each inner collection remains correlated to the outer Item lineage that caused
it to be collected. A conforming processor SHALL retain enough provenance to
identify that lineage in full results/evidence.

## Required semantics

1. A `for_each` source SHALL be a named referenceable Object in the same
   Assessment.
2. The Object dependency graph SHALL be acyclic.
3. An inner binding SHALL NOT shadow an inherited alias.
4. A `from` reference SHALL name the current binding or an inherited correlated
   binding and a typed collected field available from that binding.
5. Each `for_each` level SHALL use at least one selector from its **current**
   binding. An ancestor-only selector does not justify another iteration level.
6. Source-field and target-selector datatypes SHALL be compatible.
7. Independent multi-source inputs SHALL NOT silently become correlated or
   Cartesian iteration. A future Cartesian construct, if needed, must be
   explicit.
8. Sets and Filters on the source Object retain their ordinary semantics.
9. Duplicate projected values do not create a new truth rule. Where distinct
   source Items produce equal values, full evidence SHALL retain their distinct
   lineage.
10. Ordering has meaning only when the underlying capability explicitly defines
    observable order. `for_each` itself does not invent ordering semantics.

## Status, errors, and completeness

`for_each` SHALL preserve the effective status of its source collection and
projection dependencies.

- zero source Items follows the source/ObjectComponent-equivalent semantics; it
  is not silently converted to a loop success;
- a missing projected field or incompatible value is an error according to the
  underlying field/projection contract;
- an incomplete source collection yields an incomplete dependency;
- an implementation SHALL NOT report complete technical truth when configured
  resource/item/depth limits stopped collection;
- scanner resource limits MAY protect implementations, but hitting one must be
  visible in result completeness/error metadata rather than silently truncating
  truth.

These rules apply at every nesting level.

## Evaluation boundary

`for_each` is a **collection** construct only.

It SHALL NOT:

- create one Test result per source Item;
- change Test `existence`, `match`, State matching, or `evaluate`;
- introduce an implicit Boolean AND/OR across iterations;
- turn an incomplete collection into a complete result merely because some
  Items were usable.

## Results and provenance

A full result for a `for_each` collection SHALL retain enough information to
explain:

- the source Object;
- source Item identity;
- projected field/value;
- target Object and collected target Item;
- inherited outer lineage for nested collection;
- collection/projection error or completeness status.

Evidence caps MAY bound retained samples but SHALL NOT change the verdict or
claim completeness that was not achieved.

## Automatic SCAP 1.4 modernization

The language supports nested collection iteration, but automatic conversion is
fail-closed.

The converter MAY automatically emit `for_each` only for a transformation
class with an exact equivalence proof. The current proven automatic class is the
direct ObjectComponent → local Variable → target selector pattern with
source-equivalent `one_or_more` selector quantification.

More complex legacy graphs or shell/PowerShell loops remain faithful content
until a parser/transformation can prove the same semantics. DNS production
content is evidence for native nested authoring; it is not permission to guess
the meaning of arbitrary scripts.

## Relationship to Variables

Use a literal or typed literal array for source-time fixed values. Use
`for_each` for runtime expansion over collected Items. Keep a named Variable
for genuine runtime derivation or reusable/chained dataflow that is not
collection iteration.
