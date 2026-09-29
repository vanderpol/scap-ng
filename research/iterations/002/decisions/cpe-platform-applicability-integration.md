# CPE Integration with Platform and Applicability

**Status:** working design decision  
**Iteration:** 002  
**Scope:** CPE identifiers, CPE matching/applicability, SCAP 1.4 migration, and future CPE/OVAL Board compatibility

Normative terms in this research note are provisional but intentionally use
SHALL, SHALL NOT, SHOULD, SHOULD NOT, and MAY in the sense expected for a
future standards specification.

## Decision summary

SCAP-NG SHALL NOT make CPE the only executable applicability mechanism.

SCAP-NG SHALL nevertheless provide an explicit integration point for
standardized external platform/product identifiers such as CPE when those
identifiers are useful to publishers, tools, asset inventories, vulnerability
management systems, or future OVAL/CPE standards work.

CPE is treated as an **identity and matching facet of Platform**, not as a
replacement for the Platform Assessment that establishes truth on a target.

The intended layering is:

    Platform logical identity
        |
        +-- executable Platform Assessment
        |
        +-- zero or more external identifiers
              |
              +-- CPE 2.3 / future CPE version
              +-- other standardized namespaces

Rule applicability remains a separate layer for target conditions beyond basic
product/platform identity.

## Why preserve a CPE integration point

CPE provides a standardized way to name classes of operating systems,
applications, and hardware products. Those identifiers can be useful outside a
single SCAP-NG scanner, including:

- vulnerability management;
- software/hardware inventory correlation;
- product dictionaries and catalogs;
- security-content discovery;
- content routing;
- interoperability with existing SCAP ecosystems;
- migration from SCAP 1.4;
- future OVAL/CPE Board work.

Removing any structured place for CPE would make later interoperability harder
and could force publishers to place product identifiers in arbitrary metadata.

At the same time, requiring CPE for applicability would recreate coupling that
SCAP-NG is intentionally removing.

## Platform object integration

A Platform MAY declare zero or more external identifiers.

Illustrative source syntax:

    platform:
      id: windows.11
      identifiers:
        - scheme: cpe
          version: "2.3"
          value: "cpe:2.3:o:microsoft:windows_11:*:*:*:*:*:*:*:*"

      assessment:
        ref: assessments/shared/platforms/windows-11.assessment.yaml

The exact final serialization remains under schema review.

The stable SCAP-NG Platform identifier remains authoritative inside SCAP-NG.

An external identifier SHALL NOT replace the SCAP-NG logical Platform
identifier.

A CPE identifier SHALL NOT by itself be interpreted as proof that the target
matches the Platform unless the applicable conformance profile explicitly
defines CPE matching as an executable Platform mechanism.

## Executable Platform truth

By default, executable Platform truth SHALL be established by the Platform's
bound Assessment Method.

A processor SHALL NOT infer a Platform result merely from:

- the textual SCAP-NG Platform identifier;
- a filename;
- an operating-system display string;
- a CPE identifier embedded as metadata;
- scanner-specific hard-coded product tables.

This maintains the current SCAP-NG principle that Platform truth is explicit
and testable.

## Optional CPE matching capability

If CPE continues to be standardized and useful for machine applicability,
SCAP-NG MAY define a CPE matching capability or standardized Platform
Assessment primitive.

Conceptually:

    platform:
      id: windows.11
      identifiers:
        - scheme: cpe
          version: "2.3"
          value: "cpe:2.3:o:microsoft:windows_11:*:*:*:*:*:*:*:*"

      assessment:
        capability: platform.cpe-match
        expected:
          identifier_ref: <the CPE identifier above>

Such a capability would need to define:

- supported CPE version(s);
- name binding syntax;
- matching semantics;
- treatment of ANY / NA / wildcard values;
- dictionary dependence, if any;
- unknown/unmapped product behavior;
- evidence produced by matching;
- error/indeterminate behavior;
- version transition rules.

Until those semantics are standardized, CPE identifiers remain external
identity/provenance data and SHALL NOT silently acquire scanner-specific
matching behavior.

## CPE Applicability Language

CPE 2.3 defines an Applicability Language for Boolean combinations of CPE
product names.

SCAP-NG SHOULD NOT duplicate that complete expression language inside the core
Rule `when` syntax merely for legacy compatibility.

For Stage-1 SCAP 1.4 migration:

1. a legacy CPE applicability expression SHALL be interpreted semantically;
2. when it can be mapped exactly to NG Platform identity plus Rule
   applicability Assessments, the converter SHOULD perform that decomposition;
3. when CPE expression semantics cannot be decomposed losslessly, the converter
   SHALL preserve them through an explicit compatibility Assessment/capability
   or SHALL report a conversion blocker;
4. the converter SHALL NOT treat an unverified CPE string match as equivalent
   to a legacy CPE applicability expression.

This preserves losslessness without making CPE Applicability Language the
native SCAP-NG policy language.

## CPE dictionary relationship

A CPE dictionary is an external product-name registry/catalog.

SCAP-NG core SHALL NOT require every package to embed a full CPE dictionary.

A package MAY carry:

- the CPE identifiers directly required by its Platform definitions;
- a reduced/embedded dictionary when a selected conformance profile requires
  one;
- references/provenance identifying an external CPE dictionary/version.

A processor SHALL NOT depend on an unspecified mutable external dictionary when
doing so could change the truth of a signed or versioned Assessment without
that dependency being visible in package provenance.

If CPE matching depends on a dictionary, the effective dictionary identity or
version SHOULD be captured in execution provenance.

## Version independence

The SCAP-NG data model SHALL NOT hard-code CPE 2.3 syntax into the generic
external-identifier concept.

The identifier representation SHOULD permit:

    scheme: cpe
    version: "2.3"

and later, if standardized:

    scheme: cpe
    version: "3.0"

without changing the Platform logical identity model.

Version-specific matching semantics belong in the corresponding capability,
profile, or external standard binding.

## Target inventory versus content Platform

A target MAY expose observed product identifiers, including CPE identifiers,
as collected inventory facts.

A content Platform MAY expose expected/reference product identifiers.

These are different roles:

    observed target product identity
        versus
    content-declared applicable product identity

A CPE matching implementation compares those roles according to the applicable
CPE matching specification.

SCAP-NG SHALL NOT conflate either role with unique asset identity. CPE
identifies product classes, not unique installed asset instances.

## Results and provenance

When CPE contributes to a Platform/applicability decision, results SHOULD
identify:

- the SCAP-NG Platform logical identifier;
- the external identifier scheme and version;
- the content/reference CPE identifier or expression;
- the observed/matched product identity when safe and useful;
- the matching outcome;
- the matching standard/profile version;
- any dictionary dependency/version;
- decisive evidence or reason for false/indeterminate results.

Results SHOULD NOT require consumers to reconstruct a legacy CPE component
graph merely to understand why content applied or did not apply.

## Migration from SCAP 1.4

A Stage-1 converter SHALL preserve CPE-related source semantics that affect
applicability.

Legacy CPE names SHOULD be preserved as external identifiers/provenance even
when executable applicability is migrated into native Platform Assessments.

When legacy content uses local CPE dictionary entries whose applicability truth
is ultimately established by OVAL inventory checks, migration SHOULD preserve
both useful identities:

- the CPE-facing product identifier; and
- the executable Assessment semantics that establish the condition.

This allows interoperability without making the product identifier itself the
test.

## Relationship to OVAL

OVAL Assessment logic and CPE product identity solve different problems.

OVAL/NG Assessment logic establishes facts about the target.

CPE provides standardized product-class naming and matching semantics.

SCAP-NG SHOULD allow them to compose without requiring either one to subsume
the other.

If future OVAL Board work defines a normative CPE integration contract,
SCAP-NG SHOULD evaluate adoption through this Platform external-identifier and
matching-capability boundary rather than redesigning Rule applicability.

## Open questions to track

The following SHALL remain open until the relevant standards direction is
clear:

- whether CPE 2.3 remains the interoperability baseline for SCAP-NG;
- whether and how CPE 3.x changes naming or matching semantics;
- whether OVAL adopts a first-class CPE representation or matching contract;
- whether SCAP-NG should standardize a `platform.cpe-match` capability;
- whether CPE dictionary material belongs in compiled packages or is normally
  external;
- how signed packages pin external CPE dictionary dependencies;
- whether vulnerability/content-discovery use cases require additional product
  identifier metadata beyond applicability;
- whether hardware CPE requires different evidence than operating-system or
  application CPE.

## Design rationale

This approach keeps CPE useful without restoring the old stovepipe:

    CPE = standardized product identity/matching namespace
    Platform Assessment = executable truth
    Rule applicability = additional target condition
    Compliance Assessment = requirement evaluation

If CPE ultimately remains important, SCAP-NG has a natural integration point.

If CPE changes substantially or is not adopted by future OVAL/SCAP work, the
core Platform/applicability architecture remains valid.
