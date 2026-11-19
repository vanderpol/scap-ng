# Schema-first OVAL source-language coverage (initial audit)

[Canonical issue #80](https://github.com/vanderpol/scap-ng/issues/80) — [Tools release #71](https://github.com/vanderpol/scap-ng-tools/issues/71)

This **read-only** audit inventories global OVAL 5.12.3 Test/Object/State declarations by original QName, resolves XSD type/base/group references, records fields, attributes, choices, enumerations, original deprecation annotations and embedded Schematron assertions, and compares them with current SCAP-NG 0.4.1 primary capability mappings. The source XML grammar is authoritative; the signed benchmark corpus is a separate validation and regression input.

## Run

Checkout official OVAL source at \`OVAL-Community/OVAL@2f140ee5c5dd1ed9606fcd5afc301f6baeb48706\` (54 XSD files), then execute:

\`\`\`sh
python3 -m unittest discover -s tests -p 'test_audit_oval_language.py' -v
python3 tools/audit_oval_language.py --oval-dir /path/to/OVAL/oval-schemas \
  --mapping-root schema/capability-mappings --output /tmp/oval-grammar-5123.json
\`\`\`

Or run the **OVAL 5.12.3 normative grammar inventory** GitHub Actions workflow to create a pinned, read-only, downloadable inventory artifact. The authoritative CLI enforces the upstream commit SHA and 54 XSD count. \`--skip-pin-check\` is reserved for synthetic fixtures.

## Scope and evidence interpretation

\`mapped_declaration\` means only that an OVAL source QName appears in a canonical primary mapping. It **does not** prove that the target supports every legal field, behavior, choice, datatype, Set/Filter, subtype, cardinality, implicit default or any source evaluation semantics. Every entry is marked \`further_semantic_review_required\`. A mapped Variable Object with an XSD Set choice and a direct SCAP-NG Variable source is flagged for deliberate analysis, not automatically classified as a canonical defect.

This first pass inventories Schematron declarations but **does not execute** Schematron or XML Schema validation, analyze every source combination, or establish OVAL/scanner equivalence. The next phase adds an explicit field-level source→native semantic crosswalk, source-valid and source-invalid witness generation, XCCDF/CPE/OCIL grammar and documented evaluation semantics, approved scope/deprecation dispositions, converter source parity, and independent RI runtime vectors. Any missing source declaration must be reconciled rather than silently excluded. Do not modify the active SCAP-NG grammar or rewrite the converter solely on this inventory.
