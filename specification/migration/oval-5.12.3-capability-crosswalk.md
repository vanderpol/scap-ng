# OVAL 5.12.3 capability crosswalk

**Status:** Informative migration reference for native SCAP-NG **0.3.0**.
The normative conversion contract is
[OVAL 5.12.3 → SCAP-NG](oval-5.12.3-to-ng.md).

## One current mapping authority

The [0.3 supported capability catalog](../../schema/v0.3.0/capability-mappings/supported/README.md)
and its versioned JSON mappings are the source of truth for actual Test/Object/
State/Item family names, fields, datatypes, and provenance.
[Experimental mappings](../../schema/v0.3.0/capability-mappings/experimental/README.md)
are not supported language features. Do not use 0.2.0 candidate names or
the older research inventory to override a 0.3 mapping.

For each imported source Test:

- A reviewed, non-deprecated Test uses its exact matching supported mapping.
- A deprecated Test fails conversion and reports its authoritative source
  identity and a replacement when supported.
- An unknown Test or publisher extension fails closed; converters shall not
  invent a native capability or silently substitute a vaguely similar Test.
- Mappings preserve original OVAL version/family identities in provenance
  even when native capability naming is shorter or clearer.

An OVAL suffix such as `54`, `57`, or `512` may distinguish a
semantically revised Test from its deprecated predecessor. Only a reviewed
mapping can decide whether a suffix can be dropped in the native name.

## Known publisher exception

NIWC/SCC `independent.sqlext` is not standard OVAL 5.12.3.
It must not be advertised as a standard SCAP-NG capability. The
[65-source release gate](https://github.com/vanderpol/scap-ng/issues/202)
accounts separately for the four source packages blocked by this extension.
The standard `sql512` Test is not automatically interchangeable with
`sqlext`.

For actual capability support and datatype/cardinality auditing, use the
[0.3 catalog](../../schema/v0.3.0/capability-mappings/README.md)
and [conformance requirements](../core/conformance.md), rather than
duplicating another list of capability names in this document.

<!-- spec-nav:start -->

---

**Specification navigation:** [← Previous: OVAL 5.12.3 to SCAP-NG Migration](oval-5.12.3-to-ng.md) · [Contents](../README.md) · [Next: Security Considerations →](../security/security-considerations.md)

<!-- spec-nav:end -->
