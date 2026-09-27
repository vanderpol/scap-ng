# Generated NIWC Rule-Level OVAL Corpus

This directory is generated from the four priority published SCAP 1.4
benchmarks in the pinned NIWC Atlantic `Current/` corpus:

- RHEL 9
- Oracle Linux 9
- Windows 11
- Windows Server 2025

For every XCCDF Rule with an OVAL check, the generator creates:

```text
<benchmark>/rules/<xccdf-rule-id>/
  oval.xml
  oval-ir.json
  provenance.json
```

`oval.xml` is a standalone OVAL Definitions document containing the referenced
definition plus the complete transitive definition/test/object/state/variable
closure. It must validate against
`third_party/scap-1.4-schemas/omni-schema.xsd`.

`oval-ir.json` is the faithful semantic intermediate representation produced
from that standalone OVAL.

`provenance.json` links the generated artifact back to the exact signed NIWC
ZIP, repository revision, XCCDF Rule, OVAL definition IDs, component IDs,
closure IDs, hashes, and schema-validation result.

The original signed NIWC package is always authoritative. These files are
reproducible research artifacts used to develop and test SCAP-NG conversion.
