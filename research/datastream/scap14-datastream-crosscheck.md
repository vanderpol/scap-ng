# SCAP 1.4 Source Data Stream Cross-Check for SCAP-NG

**Status:** design research  
**Date:** 2026-09-29  
**Primary reference:** NIST SP 800-126 Rev. 4 (SCAP 1.4)

## Purpose

SCAP-NG intentionally removes the SCAP 1.x XML source data stream construct.
This review identifies which source-data-stream semantics still need an
explicit NG replacement and which constructs are only legacy XML packaging
mechanics.

The key rule is:

> Removing the SCAP 1.x data-stream serialization SHALL NOT silently remove
> useful package, use-case, integrity, validation, or relationship semantics.

## 1. High-level use-case classification — preserve

SCAP 1.4 requires each source data stream to declare one `use-case`:

- `CONFIGURATION`
- `VULNERABILITY`
- `INVENTORY`
- `OTHER`

This declaration is above the XCCDF Benchmark and is not the same as an OVAL
Definition `class`.

This is a real NG gap.

### Recommended NG direction

Add a high-level content-use-case declaration to the compiled package/index
layer, not automatically to each Benchmark.

Candidate native vocabulary:

- `compliance` or `configuration` — naming requires design decision;
- `vulnerability`;
- `inventory`;
- `other`.

A package MAY need to declare one use case per contained Benchmark/publication
unit if future packages can contain heterogeneous Benchmark types.

The use-case declaration SHALL remain distinct from Assessment `class`
(`compliance`, `vulnerability`, `patch`, `inventory`,
`miscellaneous`).

## 2. Collection versus individual data stream — preserve conceptually

SCAP 1.4 distinguishes:

- a source data stream **collection**; and
- one or more individual source **data streams** within that collection.

A collection can group related data streams and allow component reuse across
them.

NG currently has a compiled Benchmark package concept but no clearly defined
equivalent of a multi-publication collection.

### Recommended NG direction

Retain two conceptual levels if justified:

1. **NG package/bundle** — transport/integrity container;
2. **publication/index entry** — one executable Benchmark/use-case unit.

Do not recreate the XML hierarchy merely for compatibility.

Open question: whether one NG ZIP may contain multiple Benchmarks/use cases or
whether each distributable package should contain exactly one executable
Benchmark publication.

## 3. Explicit membership/reference graph — preserve

The SCAP 1.4 data stream explicitly identifies the checklist, check,
dictionary, tailoring, and extension components belonging to a data stream.

NG already replaces this with:

- Benchmark -> Rule membership;
- Rule -> Assessment bindings;
- applicability registry -> Assessment bindings;
- package manifest -> members.

This is a good replacement, but the compiled package/index must be authoritative
and explicit.

No object SHOULD become executable merely because it is physically present in
a ZIP.

## 4. Component reuse — preserve

SCAP 1.4 allows one component to be referenced from multiple data streams in a
collection.

NG should preserve this through stable logical identities and package-level
deduplication.

Reusable Assessments, applicability Assessments, and shared metadata SHOULD be
stored once per compiled package and referenced by stable identity.

## 5. URI/catalog remapping — replace, do not preserve

SCAP 1.4 uses component references plus OASIS XML Catalog `uri` and
`rewriteURI` rules to redirect references inside components to the intended
bundled components.

The useful semantic capability is deterministic reference resolution.

NG already has a cleaner replacement:

- source references are explicit;
- compilation resolves them;
- compiled content uses stable logical IDs;
- execution does not depend on XML URI rewriting.

The XML Catalog mechanism itself SHOULD NOT be carried forward.

## 6. Local versus remote components — explicit NG decision required

SCAP 1.4 component references may resolve to local or remote content.

Current NG direction favors a self-contained scanner package and prohibits
execution from mutable external dependencies.

That is safer and more reproducible.

### Recommended NG direction

Compiled packages SHALL be self-contained.

Authoring source MAY reference remote/shared content during build if the compiler
pins, validates, and embeds the exact resolved version.

Runtime remote dereferencing SHOULD NOT be required for conformance.

## 7. Package/use-case version — preserve

SCAP 1.4 data streams declare the SCAP version they conform to.

NG needs an equivalent high-level specification/profile version so a processor
can know which normative object model and validation rules apply before
processing Benchmark internals.

Candidate concepts:

    format: scap-ng
    specification_version: ...
    profile: ...

Exact naming remains open.

## 8. Creation/update timestamp — preserve where meaningful

SCAP 1.4 data streams may have a creation timestamp, and source components have
required created/last-updated timestamps.

NG already has Benchmark publication/version metadata, but package/index-level
creation time and object revision time are not fully standardized.

Recommended distinction:

- semantic publication/version;
- package build timestamp;
- source-object revision/update timestamp;
- provenance retrieval/conversion timestamp.

Timestamps SHALL NOT substitute for immutable identity/digest.

## 9. Validation profile/version — preserve concept, not Schematron

SCAP 1.4 records a Schematron version at the collection level and validates:

- container structure;
- each component schema;
- cross-component semantic relationships.

NG should preserve all three classes of validation:

1. syntax/schema validation;
2. per-object semantic validation;
3. cross-object/package validation.

The specific Schematron mechanism is not needed.

A compiled package should identify the SCAP-NG specification/schema profile
against which it was validated.

## 10. Extension point — preserve deliberately

SCAP 1.4 has `extended-component` for non-standard content, though using it
makes the stream non-conformant in defined circumstances.

NG already has publisher extensions at object level but has not fully defined
package-level extensions.

Open question:

- Should NG packages allow non-standard extra objects?
- If yes, must processors ignore unknown optional extension members?
- Can an extension ever affect semantics while retaining core conformance?

Recommended principle: unknown extensions SHALL NOT silently alter standardized
execution semantics.

## 11. Digital signatures and integrity — preserve

SCAP 1.4 can sign the whole collection or a data stream and its referenced local
components.

NG already intends to replace XMLDSIG with signing over a canonical manifest or
equivalent package representation.

This is a sound replacement.

Still open:

- signature format;
- trust anchors;
- signing scope;
- countersigning;
- handling of detached evidence/provenance;
- whether signatures cover source, compiled form, or both.

## 12. Globally unique container/component IDs — simplify but preserve stable identity

SCAP 1.4 imposes globally unique naming conventions on collection, data-stream,
component-ref, component, and extension IDs.

NG should not preserve those opaque identifier formats.

The useful requirements are:

- stable logical identities for semantic objects;
- unambiguous references;
- immutable package identity/digest;
- deterministic duplicate detection.

## 13. Explicit content categories — preserve semantically

SCAP 1.4 organizes data-stream members into:

- dictionaries;
- checklists;
- checks;
- extended components.

NG should not reproduce these XML buckets.

Their semantic successors are approximately:

- Platform/product identity metadata and applicability -> former dictionaries;
- Benchmark/Rule/Tailoring -> former checklists;
- Assessment Methods -> former checks;
- publisher/package extensions -> former extended components.

This mapping should be documented in the compatibility crosswalk.

## 14. Use-case-specific content rules — likely missing and important

SCAP 1.4 does more than label the use case. Section 5 defines requirements for
what content is valid for:

- compliance/configuration checking;
- vulnerability scanning;
- inventory scanning.

NG currently defines Assessment classes but has not yet fully defined
**package/use-case conformance rules**.

Examples of likely NG requirements:

### Compliance package

- SHALL contain a Benchmark with evaluable Rules;
- selected/default Rule Assessments should normally use compliance semantics or
  explicitly defined alternative semantics;
- manual Assessments MAY be present;
- applicability/inventory Assessments MAY support selection.

### Vulnerability package

- SHALL identify vulnerability Rules/findings and their external CVE or other
  vulnerability identifiers where applicable;
- vulnerability truth polarity SHALL be explicit;
- applicability MAY rely on inventory-class Assessments;
- vendor/product affectedness provenance SHOULD be retained.

### Inventory package

- SHALL produce descriptive inventory facts;
- SHOULD NOT reinterpret inventory truth as compliance pass/fail;
- may operate without conventional security-policy remediation.

These need a dedicated normative design section.

## 15. Patch checking — subtle point

SCAP 1.4 has a high-level set of formal use cases that does not include a
separate `PATCH` data-stream use case, even though OVAL has a `patch`
Definition class and compliance use can reference patch definitions.

Therefore NG SHOULD NOT automatically equate Assessment class with package use
case.

This reinforces the need for two independent concepts:

- high-level package/content `use_case`;
- per-Assessment `class`.

## 16. Result/source linkage — already partly preserved

SCAP 1.4 result data streams preserve relationships between:

- target asset;
- source data stream;
- XCCDF result;
- OVAL/OCIL check results;
- tailoring;
- variable values.

NG intentionally removes nested component reports but still needs equivalent
traceability:

- exact package identity;
- exact Benchmark/version;
- effective Profile;
- Tailoring;
- Organizational Input;
- Rule;
- selected check;
- Assessment Method;
- target;
- result/evidence.

The current NG result direction is broadly aligned, but this relationship graph
should remain a formal completeness criterion.

## 17. Source content embedded in results — intentionally replace

SCAP 1.4 recommends including the source data stream collection in ARF results.

NG intentionally avoids embedding a full copy of source content in every result
package.

Recommended replacement:

- immutable package digest/identity;
- enough Rule metadata for independent downstream interpretation;
- optional archived source-package reference.

This appears to be an intentional improvement, not a gap.

## 18. Processing unsupported checking systems/components — preserve behavior category

SCAP 1.4 defines behavior for unsupported checking systems, including warnings
and continued processing where possible.

NG needs equivalent processor rules for:

- unknown Assessment capability;
- unsupported Assessment mode;
- unknown optional extension;
- unsupported required extension;
- unsupported package/use-case profile.

These should result in explicit unsupported/not-evaluated states rather than
silent omission.

## 19. Data-stream integrity scope and package manifest

SCAP 1.4 signature rules explicitly define which referenced components are
covered when a data stream is signed.

NG's manifest model should similarly make signing closure deterministic:

> every semantic object required to execute a publication SHALL be present in
> the canonical manifest and covered by the package integrity/signature scope.

This should include applicability and selected reusable Assessments, not just
Benchmark/Rule files.

## 20. Preliminary gap summary

### Clearly missing / should be added to NG design

1. high-level package/publication `use_case`;
2. package/specification conformance version/profile;
3. explicit use-case-specific package validation rules;
4. clearer bundle/index versus Benchmark relationship;
5. package-level build/revision metadata;
6. defined package extension behavior;
7. unsupported-capability/use-case processing rules.

### Already preserved in a cleaner form

1. explicit references and dependency closure;
2. component reuse/deduplication;
3. self-contained distribution;
4. schema + semantic validation intent;
5. signing/integrity intent;
6. source/result traceability;
7. stable identities;
8. target identity.

### Intentionally obsolete implementation machinery

1. XML data-stream container syntax;
2. OASIS XML Catalog URI remapping;
3. component-ref XLinks;
4. XML namespace-based component typing;
5. SCAP-specific opaque/global ID naming conventions;
6. XMLDSIG representation itself;
7. embedding full source stream in every result.

## 21. Recommended next design step

Before finalizing the iteration-003 Rule/Assessment rename, define a small
native NG package/index object that carries the semantics formerly owned by the
SCAP data-stream layer.

Illustrative, non-normative sketch:

    package:
      id: disa.rhel9.stig
      specification:
        name: scap-ng
        version: <draft-version>
      use_case: compliance
      version: 002.009.013
      created: ...
      benchmarks:
        - rhel9-stig
      manifest: manifest.yaml
      extensions: {}

or, if package integrity metadata belongs in a separate index:

    index:
      specification_version: ...
      use_case: compliance
      benchmarks:
        - id: rhel9-stig
          source: benchmark.yaml

The exact syntax should be designed only after deciding whether one NG package
may contain multiple executable Benchmarks and/or multiple use cases.
