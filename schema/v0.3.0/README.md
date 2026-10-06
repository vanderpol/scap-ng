# SCAP-NG 0.3.0 schema

**Status:** active pre-alpha development tree.

This directory is a complete, independent SCAP-NG **0.3.0** schema snapshot.
It was opened from the frozen 0.2.0 baseline and is now versioned entirely as
0.3.0. Files in this directory SHALL resolve to other 0.3.0 files, not back to
the frozen 0.2.0 tree.

The 0.2.0 release remains unchanged and is the frozen OVAL Board review
baseline. New semantic work, including the proposed Object-level `for_each`
collection-expansion construct, belongs here.

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
