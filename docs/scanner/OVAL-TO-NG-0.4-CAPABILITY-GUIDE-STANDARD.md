# OVAL 5.12.3 → SCAP-NG 0.4.0 scanner guide standard

**Purpose:** create concise, actionable implementation guides without blindly inheriting OVAL behavior. Keep the full pinned upstream annotations separately; these guides are the reviewed NG-specific interpretation.

## Classification before writing

For each material collection/Item/status behavior from pinned OVAL XSD, classify it as:
- **unchanged** — same observable contract
- **modified** — same concern, different NG behavior or interface
- **replaced** — NG implements the concern differently
- **not applicable** — deliberately unsupported with an authoritative reason
- **unresolved** — insufficient evidence; blocks a conformance claim

**A syntax rename alone does not imply changed collection semantics.** Equally, identical names do not prove equivalence. Link each material deviation to the accepted NG 0.4.0 specification decision and one test or a missing-test issue. Never infer behavior from a prototype or from an authoring-only roundtrip.

## Suggested single-capability guide (target: one page, two only for complexity)

1. **Scope:** capability name; source OVAL element(s), pinned tag and blob; NG mapping/spec version
2. **Collection contract:** which Items must be selected; Item identity; fields and types; critical missing/error/partial evidence behavior
3. **Differences from OVAL:** short table (OVAL behavior | NG status | authoritative reason)
4. **Implementation pitfalls:** only practical points that alter safety, correctness or efficiency; link to preserved original for optional details
5. **Conformance examples:** a few high-value positive, negative and boundary cases, linked to executable fixtures
6. **Open issues:** unresolved decisions, owner and release gate; don't state these as facts

Detailed APIs, Windows registry recipes and historical commentary belong in the pinned source archive or supplemental developer reference, not the quick guide. Reference the exact upstream annotation location rather than copying paragraphs.

## Release checks

- Every actively supported NG capability has a guide or an explicit, tracked, justified exemption.
- Every material OVAL behavior is classified, and every **modified**, **replaced** or **not applicable** row cites a current 0.4.0 decision and expected consequence.
- Every **unresolved** behavior that could change assessed results blocks scanner conformance/production-readiness claims.
- Tests cover empty collections, partial collection, errors, datatype/operation constraints, per-Item and per-field cardinality where applicable.
- Validate the guide against the effective NG schema, compiler and provider code, not only the OVAL XSD.
- A future OVAL source version bump requires a new compatibility review; do not silently inherit updated wording.

**Separation of concerns:** JSON Schema = authoring contract and concise metadata; capability specification = normative collection/result semantics; quick scanner guide = implementation-critical NG behavior and deviation map; complete OVAL annotations = archival reference.
