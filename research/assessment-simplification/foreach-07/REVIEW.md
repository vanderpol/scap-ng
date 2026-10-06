# Foreach v1 human review packet

**Status:** syntax review only. Semantic proof artifacts are under this directory.
No 0.2.0 schema or accepted design is changed by this packet.

Tracking: #164

## Decision requested

Is the proposed collection-expansion `foreach` form a meaningful authoring
improvement over the faithful Object -> Variable -> Object graph while keeping
the semantics obvious enough that authors and implementers will not confuse it
with per-iteration Test evaluation?

If yes, the next step is a 0.3.0 schema/compiler prototype for the narrow v1
class only.

If no, retain the faithful graph. No conversion capability is lost.

## Production example: RHEL 9 SV-257889

Requirement:

> All RHEL 9 local initialization files must have mode 0740 or less permissive.

One of the source paths is:

```
Password Object
  -> filters / Set selecting the account population
  -> object_component(home_dir)
  -> local Variable
  -> File Object path var_ref(var_check="at least one")
  -> one combined File population
  -> File Test
```

The source Test uses `check_existence="any_exist"` for one account class.
That is why this proposal is collection expansion rather than one Test per user.

### Faithful native graph

Illustrative current-aligned source shape:

```yaml
objects:
  non-system-users:
    object_title: Non-system users excluding /
    capability: unix.password
    # source Set and Filters retained here

  initialization-files:
    object_title: Initialization files for non-system users
    capability: unix.file
    select:
      path:
        operation: equals
        datatype: string
        variable: non-system-home-dirs
        var_check: at least one
      filename:
        operation: pattern_match
        datatype: string
        value: '^\\.[^\\s\\.]+'
    # original filters / behaviors retained

variables:
  non-system-home-dirs:
    variable_title: Home directories of non-system users
    kind: local
    datatype: string
    expression:
      object_component:
        object: non-system-users
        item_field: home_dir

tests:
  initialization-file-mode:
    object: initialization-files
    check_existence: any_exist
    check: all
    # original State references retained
```

The Variable is semantically real in the faithful graph, but for a human author
its only purpose here is to project one field from one Object and immediately
feed it to one target Object selector.

### Proposed v1 authoring form

```yaml
objects:
  non-system-users:
    object_title: Non-system users excluding /
    capability: unix.password
    # same source Set and Filters

  initialization-files:
    object_title: Initialization files for non-system users
    capability: unix.file

    for_each:
      source:
        object: non-system-users
      as: user
      collect: union

    select:
      path:
        from: user.home_dir
        operation: equals
        datatype: string
      filename:
        operation: pattern_match
        datatype: string
        value: '^\\.[^\\s\\.]+'
    # same filters / behaviors

tests:
  initialization-file-mode:
    object: initialization-files
    check_existence: any_exist
    check: all
    # same State references
```

The proposed form removes the named one-use Variable while keeping the source
Object and target Object independently visible.

## What is actually simpler

The author no longer has to:

1. invent a Variable ID/title for a one-use field projection;
2. jump from the target selector to the Variable and then back to the source
   Object to understand where the value comes from;
3. mentally reconstruct that the Variable is only acquisition/dataflow plumbing.

The author still sees:

- which source Object supplies Items;
- which exact source field is projected;
- the target selector operation/datatype;
- explicit union collection behavior;
- the target Object;
- the Test aggregation boundary.

This is deliberate. A shorter syntax that hides those facts would not be an
improvement.

## Why `collect: union` is explicit

The important semantic distinction is:

```
source Items
  -> child collection expansion
  -> ONE combined target Object population
  -> Test
```

not:

```
source Item
  -> child Object
  -> Test
repeat and aggregate Tests
```

Making `collect: union` authored and required is slightly more verbose, but it
protects the most important semantic boundary exposed by the RHEL production
counterexample.

## Error/status behavior

The authoring shorthand does not define independent loop behavior.

It desugars to the faithful semantic graph. Therefore:

- zero source Items remains an ObjectComponent error;
- missing projected field remains an ObjectComponent error;
- incomplete source collection remains incomplete;
- target collection/Test behavior is unchanged;
- a scanner optimization cannot convert error/incomplete into empty/success.

## Results comparison

The faithful form may expose a Variable Result. A native foreach implementation
may choose a smaller presentation, but both must reduce to the same canonical
evidence:

```
source Object
source Item refs
(source Item ref, projected field/value) pairs
projection status
combined target Item refs
downstream Test outcome
```

The modern form must not claim a parent->child correlation that the faithful
result did not establish.

## Production coverage of v1

Pinned census:

- RHEL 9: 4 eligible;
- Solaris 11 x86: 1 eligible;
- total: 5.

The five cases include downstream `any_exist`, `at_least_one_exists`, and
`none_exist` behavior and source Objects with Filters/Sets.

This is intentionally not broad coverage. It is enough to show the feature is
not a one-rule special case.

## Cases deliberately left faithful

### Fan-out

A projected Variable feeding multiple target Objects remains faithful graph
form in v1. This is likely modernizable later, but the best authoring scope for
one binding shared across several Objects needs review.

### Helper target

An intermediate target Object not directly referenced by a Test remains
faithful in v1. Its dependency/evidence lifetime should be reviewed separately.

### `var_check=all`

This is **not** equivalent to union expansion. Executable negative fixtures prove
that an Item matching any projected value is not the same population as an Item
matching all projected values.

### Derived functions

`concat`, arithmetic, merge and similar expressions may operate over Cartesian
products or otherwise transform value sets. They are not v1 foreach.

## Review questions

1. Is `for_each.source.object + as + collect: union` clearer than the named
   one-use Variable graph?
2. Should `collect: union` remain mandatory, as proposed, to avoid hidden
   semantics?
3. Is `from: user.home_dir` sufficiently explicit, or should the syntax say
   `field: home_dir` under a longer binding object?
4. Should v1 stay intentionally limited to `var_check="at least one"`, with
   that quantifier implicit in this exact construct, or should it be visible?
5. Is removal of one-use Variable result presentation desirable if canonical
   source/value provenance remains available?
6. If adopted, should converter modernization be opt-in initially even for
   `safe_automatic` matches, so Board/vendors can compare faithful and modern
   output side by side?

## Recommendation

Adopt the **semantic concept and v1 boundary** for 0.3.0 review.

Do not yet broaden syntax to fan-out, helper chains, `var_check=all`, or
function-derived values.

Prototype the schema/compiler only after the syntax questions above are
reviewed. Keep the faithful converter output available as the comparison oracle
throughout that prototype.
