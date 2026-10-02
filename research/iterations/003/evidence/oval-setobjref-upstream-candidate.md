# Candidate upstream fix: recursive OVAL set Object type validation

**Status:** prepared compatibility proposal only; not submitted upstream.  
**Authority reviewed:** `OVAL-Community/OVAL@v5.12.3`,
`oval-definitions-schema.xsd`, Schematron pattern `oval-def_setobjref`.  
**Tracking:** SCAP-NG issue #37 and
`research/iterations/003/design/upstream-oval-schema-issues.md`.

## Problem

OVAL `set` is recursively defined, but the pinned Schematron pattern contains
three separate rules for Object references at nesting depths 1, 2 and 3.
An XSD-valid incompatible Object reference at depth 4 or deeper therefore
escapes that specific Schematron pattern.

This is a validation-coverage gap. It is **not** a general OVAL expression,
Variable, or scanner depth limit.

The committed regression constructs a `unix:file_object` whose nested Set
references a `unix:fileextendedattribute_object`. The existing upstream
pattern rejects depths 1 and 3 but accepts depths 4 and 32. The SCAP-NG
namespace-aware source audit rejects the mismatch at every depth.

## Candidate portable rule

A replacement can match every descendant Object reference beneath the root
Object's Set and compare the referenced Object to the root Object by **namespace
URI plus local name**, avoiding prefix-sensitive `name()` equality:

```xml
<sch:rule
  context="oval-def:oval_definitions/oval-def:objects/*/oval-def:set//oval-def:object_reference">
  <sch:assert test="
    local-name(ancestor::*[parent::oval-def:objects][1]) =
      local-name(ancestor::oval-def:oval_definitions/oval-def:objects/*[@id=current()])
    and
    namespace-uri(ancestor::*[parent::oval-def:objects][1]) =
      namespace-uri(ancestor::oval-def:oval_definitions/oval-def:objects/*[@id=current()])
  ">
    Each object referenced by the set must be of the same qualified type as
    the parent object
  </sch:assert>
</sch:rule>
```

The repository does **not** patch the pinned upstream schema. The candidate is
instantiated only in a focused test.

## Compatibility assessment

The candidate preserves the apparent intent of the existing three rules:
every Object referenced anywhere in a recursive Set must have the same
qualified element type as the Object owning the outer Set.

The candidate is intentionally stricter about XML namespace identity than the
old `name()` comparison. Prefix spelling is not semantic identity, so two
different prefixes bound to the same namespace should compare equal; the same
local name in two different namespaces must compare unequal.

Focused regression coverage includes depths 1, 3, 4 and 32 for:

- a matching `unix:file_object` reference — accepted;
- a same-namespace different type
  (`unix:fileextendedattribute_object`) — rejected;
- a different-namespace same-local-name
  (`windows:file_object`) — rejected.

Missing referenced IDs remain a separate referential-integrity concern and are
already diagnosed by the SCAP-NG source audit; this candidate rule is not
intended to replace key/reference validation.

## Minimum upstream reproducer

The existing regression
`VariableFilterDependencyTests.test_deep_set_schematron_coverage_gap`
builds the minimum semantic shape programmatically from pinned schemas. It
proves the old pattern's depth boundary independently of the SCAP-NG audit.

The companion regression
`test_candidate_recursive_set_schematron_covers_all_depths_and_namespaces`
proves the candidate rule across recursive depths and qualified-name cases.

## Submission boundary

No upstream ticket or pull request is authorized by this document. If an
upstream submission is later approved, include the exact v5.12.3 source pin,
the two focused regressions, compatibility reasoning above, and ask the OVAL
maintainers to confirm the same-type requirement and XPath portability before
changing the standard schemas.
