# OVAL Board Review: Assessment Versioning and Generator Metadata

**Status:** open design questions  
**Iteration:** 003

## Background

OVAL versions each major reusable definition entity independently:

- Definition;
- Test;
- Object;
- State;
- Variable.

OVAL also includes document-level generator metadata describing the tool,
tool version, schema version(s), and document-generation timestamp.

SCAP-NG currently collapses an OVAL Definition graph into an Assessment file
whose internal test/object/state/variable-like nodes are normally local to that
Assessment rather than globally reusable top-level entities.

## Question 1: Assessment-level version

Should every SCAP-NG Assessment be required to carry an explicit version?

### Current project recommendation

Yes.

An Assessment is an independently addressable executable semantic unit. A
version is useful for:

- result traceability;
- content comparison;
- reusable Assessment lifecycle management;
- compiled-package identity;
- determining whether an Assessment changed without changing its logical ID.

For migrated OVAL content, the OVAL Definition version is the closest source
analog and SHOULD be preserved as the initial native Assessment version when
semantically appropriate.

For native/manual Assessments without an OVAL Definition analog, the
specification needs a clear initial-version and increment policy.

## Question 2: Lower-level node versioning

Should SCAP-NG require independent versions on internal Assessment nodes
corresponding conceptually to OVAL Tests, Objects, States, and Variables?

### OVAL precedent

OVAL requires versions on Definition, Test, Object, State, and Variable
entities because those entities have globally addressable identities and are
designed for sharing/reuse.

### Current project concern

In the current SCAP-NG design, test/object/state/variable-like nodes are
normally scoped inside one Assessment and are not independently published or
globally reusable objects.

Requiring a version on every nested node may therefore add authoring and
maintenance cost without delivering the same reuse/change-tracking value that
it provides in OVAL.

### Current project recommendation

Do not require lower-level independent versions unless a node is itself made
independently addressable/reusable.

Ask the OVAL Board whether losing mandatory per-node versioning would remove a
proven interoperability, repository-management, provenance, or content-update
capability that SCAP-NG should preserve.

## Question 3: Generator metadata

Should SCAP-NG preserve an OVAL-like generator metadata construct?

OVAL generator metadata records:

- product/tool name;
- product/tool version;
- schema version(s);
- document-generation timestamp.

These values describe the generated OVAL document, not the semantic truth of a
Definition.

### Possible NG locations

1. **Assessment source metadata** — each generated Assessment records its
   generator.
2. **Benchmark publication/build metadata** — one generator record describes
   the build that created the publication.
3. **Conversion provenance only** — generator information is retained outside
   native executable source.
4. **Both build metadata and provenance** — runtime package keeps relevant
   build identity while migration-specific generator details remain evidence.

### Current project recommendation

Do not silently discard generator metadata.

The likely NG replacement is publication/build provenance rather than repeated
Assessment-level semantic fields, because the source OVAL generator describes
the containing document as a whole. However, this should be an affirmative
standards decision.

The OVAL Board should advise whether generator metadata has operational value
for content trust, debugging, repository management, validation, or
interoperability that requires it to remain first-class in SCAP-NG.

## Related design principle

SCAP-NG should preserve the proven purpose of OVAL constructs even when it does
not preserve their XML location or granularity.

A construct should be removed only after determining that its operational
purpose is either:

- preserved elsewhere in NG; or
- no longer needed.


## Question 4: Assessment title

Should SCAP-NG retain an optional `assessment_title` field, or remove it from
the native model?

### OVAL precedent

OVAL Definitions may carry a human-readable title under
`definition/metadata/title`.

In many compliance content sets, that title is identical or nearly identical
to the governing Rule title, which can make it redundant in a Rule/Assessment
architecture.

However, an Assessment may also be reusable across multiple Rules or may have
a standalone technical description that differs meaningfully from the Rule
title.

### Current project recommendation

Retain `assessment_title` as OPTIONAL for now.

Migration tooling SHOULD preserve an OVAL Definition
`metadata/title` when present.

Native authoring SHOULD NOT synthesize an Assessment title merely by copying
the governing Rule title.

An absent source title SHOULD remain absent/null.

The OVAL Board should advise whether the field provides enough value for
standalone Assessment reuse, diagnostics, repositories, or interoperability to
justify keeping it in the normative NG model. If not, NG can remove the field
and preserve legacy Definition titles only in conversion provenance.
