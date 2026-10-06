# SCAP-NG 0.3.0 schema

**Status:** active pre-alpha development tree.

This directory is a complete, independent SCAP-NG **0.3.0** schema snapshot.
It was opened from the frozen 0.2.0 baseline and is now versioned entirely as
0.3.0. Files in this directory SHALL resolve to other 0.3.0 files, not back to
the frozen 0.2.0 tree.

The 0.2.0 release remains unchanged and is the frozen OVAL Board review
baseline. New semantic work belongs here. The narrow Object-level `for_each`
collection-expansion v1 authoring/validation construct is now integrated into
this active pre-alpha tree; automatic SCAP 1.4 converter modernization remains
disabled pending its own equivalence gate.

## Change discipline

- Do not modify `schema/v0.2.0/` for 0.3.0 features.
- Every 0.3.0 schema and mapping file carries its own 0.3.0 identity/version.
- Relative schema references remain within this directory.
- Semantic changes require focused conformance evidence and human review.
- A schema-valid document is not automatically migration-equivalent,
  collector-conformant, live-target-tested, or Board-approved.

## Start here

1. [Assessment schema](assessment.schema.json)
2. [Shared capability primitives](capability-common.schema.json)
3. [Supported capability mappings](capability-mappings/supported/)
4. [Assessment result schema](assessment-result.schema.json)
5. [Packaging schema](package.schema.json)

For the current foreach research/proof package, see
[foreach-07](../../research/assessment-simplification/foreach-07/README.md).

## Foreach v1 integration

The first 0.3.0 `for_each` form is intentionally narrow:

```yaml
for_each:
  item: user
  in: users

select:
  directory:
    from: user.home_dir
```

Its normative meaning remains the faithful
Object -> ObjectComponent -> local Variable -> target Object selector graph with
at-least-one selector quantification and one combined target Object population.

The 0.3.0 semantic validator rejects unsupported v1 shapes such as missing
source Objects, mismatched aliases, incompatible source/target datatypes,
multiple bound selectors, helper targets not directly used by a Test, and
independent additional Variable selectors.

See the [foreach research/proof package](../../research/assessment-simplification/foreach-07/README.md)
for the production proof and explicit exclusions.
