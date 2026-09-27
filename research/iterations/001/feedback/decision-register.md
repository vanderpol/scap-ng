# Iteration 001 Decision and Requirements Register

This register separates current working decisions from unresolved questions. It should be updated only when evidence or reviewer feedback justifies a change.

| ID | Status | Current direction | Evidence / next action |
|---|---|---|---|
| D-001 | Accepted direction | SCAP 1.4 -> NG migration is a primary requirement; reverse conversion is not. | Preserve in future architecture. |
| D-002 | Accepted direction | XML is not required for NG. | Prototype source in YAML and eventual canonical interchange in JSON. |
| D-003 | Accepted direction | Policy-only content is valid. | Prototype DISA-style policy-only rules and manual results. |
| D-004 | Accepted direction | Existing policy Check Content should serve as the default manual procedure. | Validate with DISA/NIST/OVAL reviewers. |
| D-005 | Accepted direction | Native semantic collectors are preferred to opaque shell commands. | Capability registry research required. |
| D-006 | Accepted direction | Deprecated OVAL constructs do not automatically become native NG constructs. | XSD inventory must still recognize them for migration. |
| D-007 | Accepted direction | Authors may bound detailed evidence returned from large violation populations. | Prototype `max_records`. |
| D-008 | Accepted direction | Scanners may stop collection when the verdict is invariant. | Result must report termination/completeness. |
| D-009 | Accepted direction | IF/ELIF/ELSE is a native declarative feature candidate. | Prototype Windows conditional example. |
| D-010 | Accepted direction | Published automated benchmarks are self-contained policy + automation artifacts. | No operator-managed runtime policy/automation pairing. |
| D-011 | Accepted direction | Signed modular ZIP bundle is the leading distribution architecture. | Signature/container details remain open. |
| D-012 | Accepted direction | Normal results should report compact root cause; full trace belongs in forensic detail. | Prototype nested AND/OR result. |
| D-013 | Accepted direction | Existing XSDs are semantic migration inputs, not a schema blueprint. | Develop schema inventory tooling. |
| D-014 | Open | Combined rule vs split policy/assessment/binding. | Compare iteration 001 prototypes and reviewer feedback. |
| D-015 | Open | Exact result outcome vocabulary. | Seek reviewer feedback and test more content. |
| D-016 | Open | Exact Boolean short-circuit defaults and bounded diagnostics semantics. | Exercise nested prototypes and gather feedback. |
| D-017 | Open | Normative package signature mechanism. | Research COSE/JWS/government trust requirements. |
| D-018 | Open | Exact capability registry design. | Inventory real OVAL constructs and current content usage. |
| D-019 | Open | Whether compact/explain/forensic result profiles are normative. | Test enterprise reporting scenarios. |
| D-020 | Open | Whether CBOR/streaming formats belong in the core specification. | Measure result volumes after prototype stabilizes. |
