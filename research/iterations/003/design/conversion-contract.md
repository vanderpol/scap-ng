# Iteration 003 Conversion Contract

## Purpose

This document defines the conversion behavior that the clean-room SCAP 1.4
up-converter must satisfy before generated SCAP-NG source is accepted.

## Source authority

For SCAP 1.4 and OVAL compatibility, the authoritative language definition SHALL
be the applicable XSD plus its Schematron constraints.

The converter SHALL use:

1. XSD for valid structure, types, substitution groups, defaults, cardinality,
   allowed attributes/elements, and extension points; and
2. Schematron for cross-element, reference, datatype, and semantic constraints
   that cannot be expressed completely by XSD.

Specification prose, examples, existing scanner behavior, and production content
MAY be used to explain intent, discover real-world combinations, and construct
regression tests, but SHALL NOT override the XSD/Schematron language definition.

The converter SHALL consume pinned original SCAP 1.4 artifacts/components.
Generated iteration-001 and iteration-002 YAML SHALL NOT be authoritative input.

The converter SHALL record a cryptographic digest of every authoritative input
artifact used for conversion.

## Semantic preservation

For every supported source construct that can affect platform truth, Rule
applicability, Rule selection, Profile/Tailoring resolution, check selection,
Assessment behavior, parameter/input flow, result truth/result state, or
decisive evidence, the converter SHALL either represent the construct exactly
and prove a native lowering, or stop the affected path with an explicit
diagnostic.

The converter SHALL NOT silently approximate, drop, repair, weaken, strengthen,
or reinterpret source semantics.

## Serialization is not semantics

Raw XML trees, namespaces, component filenames, hrefs, legacy wrapper
structures, and other serialization details are provenance rather than native
SCAP-NG content unless they are proven to affect behavior.

## Versioned semantic IR

The converter SHALL use a versioned semantic IR independent of both SCAP 1.4
XML and final SCAP-NG source syntax.

The IR SHALL contain semantic concepts rather than XML mirrors, use typed fields,
preserve behaviorally relevant defaults, preserve unresolved references
explicitly, contain no raw XML source tree, and support deterministic
serialization for regression testing.

## Separate provenance ledger

Source lineage SHALL be emitted separately from native source.

The provenance ledger MAY contain original XCCDF/OVAL/OCIL/CPE IDs, source
paths/hrefs, namespace information, source hashes, and mappings from source
entities to semantic IR and NG entities.

## Explicit accounting

Every behaviorally relevant source construct SHALL be classified as:

- represented_exactly
- represented_normalized
- deferred_design
- requires_review
- unsupported

A successful full conversion SHALL contain no behaviorally relevant
requires_review or unsupported items.

## Native legacy-residue prohibition

Native SCAP-NG output SHALL NOT contain XCCDF, OVAL, OCIL, or CPE
Applicability Language namespaces, identifiers, hrefs, XML element structures,
or legacy execution IDs.

Such data MAY appear in separate conversion evidence only.

If preserving a legacy reference appears necessary for native semantics, that
conversion path SHALL stop for design review and SHALL NOT emit the reference
without explicit project-owner approval.

## Public-tool constraint

Reusable ingestion, IR, validation, diagnostics, provenance, and lowering code
SHOULD remain benchmark/vendor neutral.

NIWC/DISA-specific corpus orchestration belongs in research/evidence tooling,
not reusable converter logic.


## Publisher conversion profiles

The SCAP 1.4 converter SHALL implement standards-defined SCAP/XCCDF/OVAL
semantics independently from publisher-specific conventions.

Publisher-specific interpretation SHALL be isolated behind an explicit
conversion profile. The initial profile is:

- `disa-stig`

The default/generic conversion path SHALL NOT assume DISA STIG conventions.

A publisher profile MAY:

- interpret documented publisher-specific identifier conventions;
- normalize publisher-specific metadata;
- recover semantics encoded by that publisher in a non-standard or overloaded
  standard field;
- map publisher extensions into explicit SCAP-NG publisher-extension fields.

A publisher profile SHALL NOT:

- silently change standards-defined semantics for content outside that profile;
- discard the original source value used to derive a normalized value;
- infer undocumented publisher behavior without evidence;
- cause publisher-specific vocabulary to become normative SCAP-NG vocabulary.

### DISA STIG Rule version handling

The DISA XCCDF Rule identifier convention SHALL be parsed as publisher-specific
identity metadata. For example:

    xccdf_mil.disa.stig_rule_SV-280940r1184730_rule

normalizes to:

    rule.id: SV-280940
    rule.version: r1184730

The `disa-stig` parser SHALL validate this convention before deriving either
field. It SHALL NOT apply this transformation to generic SCAP/XCCDF content.


DISA STIG content is known to overload the XCCDF Rule `version` element for
publisher-specific Rule identification rather than using it solely as the
generic XCCDF Item version.

For `disa-stig` conversion:

1. the converter SHALL preserve the original XCCDF Rule `version` value in
   publisher-specific conversion metadata/provenance;
2. the converter SHALL derive the native Rule revision/version from the
   authoritative DISA Rule identifier convention when that convention can be
   validated;
3. the derivation rule SHALL be documented and regression-tested against real
   DISA content;
4. conversion SHALL stop for review if the identifier does not match a known,
   validated DISA convention.

The generic SCAP 1.4 conversion profile SHALL map XCCDF Rule version according
to the XCCDF specification and SHALL NOT apply the DISA interpretation.


### DISA STIG identifier mapping

Publisher-side STIG Viewer data confirms that DISA distinguishes the following
identities for a requirement:

    Group ID: V-280940
    Rule ID:  SV-280940r1184730
    STIG ID:  RHEL-10-000560
    SRG ID:   SRG-OS-000420-GPOS-00186

For the `disa-stig` conversion profile, these SHALL remain distinct.

The native Rule identity/revision SHALL be derived from the DISA Rule ID:

    rule.id: SV-280940
    rule.version: r1184730

The DISA STIG ID SHALL be preserved as a typed external identifier and SHALL
NOT be used as the native Rule version:

    identifiers:
      - scheme: disa-stig-id
        value: RHEL-10-000560

The DISA Group/Vulnerability ID and SRG ID SHALL likewise be preserved as typed
identifiers when present:

    identifiers:
      - scheme: disa-vulnerability-id
        value: V-280940
      - scheme: disa-srg-id
        value: SRG-OS-000420-GPOS-00186

When DISA XCCDF content stores the STIG ID in the inherited XCCDF Rule
`version` element, the `disa-stig` profile SHALL interpret that value as the
publisher STIG ID, preserve the original source value in provenance, and SHALL
NOT map it to native `rule.version`.

The generic SCAP 1.4 conversion profile SHALL NOT apply this publisher-specific
interpretation.

### Non-standard OVAL probe extensions

The generic SCAP 1.4 / OVAL converter SHALL derive the set of standard OVAL
Tests, Objects, and States from the pinned authoritative OVAL schemas.

If source content contains a Test, Object, or State element that is not declared
by those schemas, the generic converter SHALL classify it as a non-standard
OVAL extension and SHALL NOT silently reinterpret it as a standard OVAL
capability.

A publisher conversion profile MAY lower such an extension only when:

1. the extension owner and semantics are known;
2. the source extension can be mapped to an explicitly namespaced SCAP-NG
   capability or extension construct;
3. the mapping preserves execution and result semantics; and
4. reverse conversion uses the corresponding extension vocabulary rather than
   emitting schema-invalid standard OVAL.

Until such a publisher mapping exists, conversion of the affected Definition
SHALL stop with an explicit diagnostic while unrelated standard Definitions MAY
continue converting.


## Structural fidelity for OVAL-to-NG conversion

For lossless SCAP 1.4 / OVAL conversion, the converter SHOULD preserve the
author's existing semantic decomposition as closely as practical.

This includes, when present and behaviorally meaningful:

- OVAL Object boundaries -> SCAP-NG Collection boundaries;
- OVAL Variable boundaries -> SCAP-NG Variable boundaries;
- Variable-to-variable dependency chains;
- Object-component dependencies;
- State/filter boundaries;
- Set composition; and
- Explicit intermediate variables used for readability, reuse, or debugging.

The converter SHALL NOT collapse a chain of OVAL Variables into one nested NG
expression merely because the resulting expression is semantically equivalent.

Likewise, it SHALL NOT duplicate a referenced OVAL Object/Collection inline at
each use when the source represented one shared Object.

Normalization SHOULD focus on serialization artifacts rather than authored
semantic structure. Examples of appropriate normalization include:

- replacing OVAL IDs with human-readable native NG IDs while preserving source
  IDs in provenance;
- replacing XML element/attribute syntax with native NG syntax;
- removing namespace and href plumbing;
- applying schema-defined defaults explicitly where useful; and
- mapping OVAL Object to the working NG term Collection.

A converted Assessment SHOULD therefore remain recognizable to an experienced
OVAL author when comparing dependency structure, even though its serialization
is native SCAP-NG.

Native-authored SCAP-NG content MAY use a cleaner decomposition than converted
content, provided both forms have the same defined semantics.


### OVAL `extend_definition` normalization

OVAL `extend_definition` is a reusable reference to another Definition's
criteria graph. In native SCAP-NG assessment source, the converter SHALL
dereference the referenced Definition and preserve its resulting truth
semantics rather than reproducing a legacy Definition-reference graph.

Accordingly:

1. the converter SHALL recursively resolve the referenced Definition;
2. `negate` and `applicability_check` attributes on the
   `extend_definition` edge SHALL be applied to the dereferenced expression;
3. cycles SHALL stop conversion with an explicit diagnostic rather than being
   silently truncated;
4. the referenced Definition's descriptive metadata SHALL be preserved in
   provenance but SHALL NOT be required in native assessment truth semantics;
5. reverse conversion to OVAL MAY serialize the flattened criteria directly and
   is not required to reconstruct the original `extend_definition` edge; and
6. semantic comparison SHALL treat the referenced and flattened forms as equal
   when their truth semantics are identical.

This normalization is `represented_normalized`, not a loss of assessment
semantics. Structural XML comparison SHALL classify the removal of
`extend_definition` separately from unexplained differences.
