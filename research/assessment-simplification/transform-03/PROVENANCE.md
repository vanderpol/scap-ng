# Source and provenance ledger

2026-10-03. Checkout `vanderpol/scap-ng`, branch `main`, receiving SHA
`acdfa66b77d531a37e8fd36ad199c94883d3a7a5`, clean and equal to upstream before work.
The owner's latest direction permits a transform compiling to the current spec;
it does not change that spec. Current requirements/design/glossary, repository
policy, root AGENTS and transition records were consulted. No nested AGENTS applies.

| Class | Material | Pin / use |
| --- | --- | --- |
| Inherited | Current native architecture, permission mapping/common schema, result helpers | Receiving repository SHA; exact input hashes in [verification](evidence/verification.json). Authority: CURRENT-DESIGN and native-capability-clean-break under research/iterations/003/design, not historical generated samples. |
| Inherited | Original home-file Rule/Check Text, OVAL closure and packet metadata | [SV-257889 dossier](../dossiers/SV-257889.md), [original source XML](../evidence/rhel_9/SV-257889/source-oval.xml), parent sample-manifest and RHEL9 source-generation record. NIWC revision `8c8e5dff860af6b1290ee9273a282db24278f8d5`, RHEL9 V2R9/enhanced V13. |
| Inherited | Other eleven source cases and prior experiments | Parent dossiers and [source reproduction](../refinement-01/evidence/source-reproduction.json) retain five package/version/hash pins; method-02/refinement-01 remain intact. No fresh source downloads were needed this wave. |
| Adapted | Requirement-facing allowance syntax | Prior method-02 proposal; refined to per-bit native compilation instead of requiring one complete numeric mode. Fixed illustrative Objects explicitly do not reproduce the full source scope. |
| Common | Compiler, strict grammar, source-map diagnostic, tests and verification runner | Newly authored bounded research code. Reviewed generator/schema/result utilities imported, not modified. No target implementation copied. |
| Evidence/Audit | Hashes, actual command logs, comparisons, size/counts, source maps, decision candidates and handoff | Separate from executable native graph. SHA256 pins include original XML, schemas/mapping, generator and result helper. |

The native example contains no legacy XML IDs, Rule lineage or OVAL serialization
structures. Its source map connects only native generated nodes to the new author
clauses. The ledger/dossiers supply STIG lineage separately. Neither native
execution nor a future compiled package needs this research evidence.

No confidential target scan, external implementation, deprecated Test, new
Organizational Input command surface or supported-feature retirement is introduced.
The tests reuse repository schema-derived Test control flow and compare a Boolean
predicate with the pinned source. No fresh Self-Assertion corpus run, full source
scanner result, upstream conformance assertion, or usability measurement is claimed.
