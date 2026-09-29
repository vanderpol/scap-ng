# Stable Identity, Revision, and Publisher Extensions

**Status:** working design decision  
**Iteration:** 002  
**Scope:** benchmark/rule identity and legacy interoperability

Normative terms in this research note are provisional but intentionally use
SHALL, SHALL NOT, SHOULD, SHOULD NOT, and MAY in the sense expected for a
future standards specification.

## Stable Rule identity

A SCAP-NG Rule SHALL have a stable logical identifier that remains unchanged
when the same requirement is revised.

Rule revision/version SHALL be represented separately from Rule identity.

A publisher-specific identifier that embeds a revision SHALL NOT force the
SCAP-NG logical Rule identifier to change.

Common DISA STIG XCCDF practice illustrates the problem:

    STIG ID shown in the XCCDF version field:
      RHEL-09-212030

    Rule identifier:
      SV-257791r991589_rule

The `r991589` portion is revision information. A later revision changes the
legacy Rule identifier even though the logical requirement remains the same,
which makes longitudinal correlation unnecessarily difficult.

SCAP-NG SHOULD preserve these source identifiers while representing logical
identity and revision independently.

Example:

    rule:
      id: disa.rhel9.RHEL-09-212030
      revision: 991589
      identifiers:
        - scheme: disa-stig-id
          value: RHEL-09-212030
        - scheme: disa-vuln-id
          value: V-257791
        - scheme: disa-rule-id
          value: SV-257791r991589_rule

A later revision of the same requirement retains the SCAP-NG logical ID while
changing the revision and current legacy Rule ID.

## Version means version

Fields named `version` or `revision` in SCAP-NG SHALL carry actual version
or revision semantics defined by the specification.

Publishers SHALL NOT be required to overload those fields to preserve legacy
identifiers.

Data historically stored in a semantically unrelated XCCDF field SHALL be
migrated into a correctly typed SCAP-NG field, a generic identifier/reference,
or a publisher extension.

## Generic identifiers and references

Common external identifiers SHOULD use generic repeatable structures rather
than publisher-specific top-level fields.

Examples include:
- STIG ID;
- Vulnerability ID;
- legacy Rule ID;
- CCI;
- NIST control identifiers;
- vendor advisory IDs;
- CVE identifiers;
- source Benchmark/Profile identifiers.

The specification SHOULD define well-known scheme names for widely used
identifiers while permitting additional schemes.

## Publisher extensions

SCAP-NG SHALL provide a namespaced extension mechanism for publisher-specific
data that has no standard semantic field.

Extensions SHALL:
- identify their owning namespace/publisher;
- preserve supported values losslessly;
- remain distinguishable from normative SCAP-NG properties;
- survive parse/serialize cycles by conformant tools that claim preservation
  support.

Extensions SHALL NOT:
- redefine the meaning of normative SCAP-NG fields;
- modify Assessment Method execution semantics;
- bypass Parameter input restrictions;
- silently override standard values.

Frequently used extension data SHOULD be considered for promotion into a
future standard field when multiple publishers demonstrate the same semantic
need.

## Migration rule

Up-conversion from SCAP 1.4 SHALL preserve source identifiers and
publisher-specific metadata even when the source stored those values in
semantically inappropriate XCCDF fields.

The converter SHOULD record both:
- the normalized SCAP-NG interpretation; and
- source provenance identifying the original element/attribute and value.

This allows DISA and other publishers to migrate without losing operational
metadata while also ending field overloading in newly authored content.

## SCAP 1.4 analog

| SCAP-NG concept | SCAP 1.4 analog | Relationship |
| --- | --- | --- |
| stable Rule id | XCCDF Rule @id | changed: identity no longer changes merely because revision changes |
| Rule revision | often embedded in DISA XCCDF Rule @id | normalized into a first-class field |
| identifiers[] | XCCDF id/version/reference conventions | generalized |
| extensions{} | XCCDF metadata / foreign-namespace extension points | formalized and constrained |


## Human-readable internal identifiers

SCAP-NG internal identifiers for Tests, Objects, States, Variables, and similar
Assessment-local nodes MAY use readable semantic names rather than opaque
numeric identifiers.

A tool MAY derive an initial identifier from a human-readable title, for
example by normalizing:

    Verify rngd service is active
        -> verify_rngd_service_is_active

Once assigned, the identifier SHALL be treated as a stable logical identifier.

Changing a title, discussion, remediation, policy wording, or other
human-readable text SHALL NOT require the identifier to change.

An identifier MAY be renamed only as an explicit identity-maintenance action,
with the same care as any other reference-breaking change.

This permits readable authoring without coupling object identity to prose.
