# Iteration 001 Decision and Requirements Register

This register separates current working decisions from unresolved questions. It should be updated only when evidence or reviewer feedback justifies a change.

| ID | Status | Current direction | Evidence / next action |
|---|---|---|---|
| D-001 | Accepted requirement | **SCAP 1.4 datastream -> SCAP-NG forward conversion is a non-negotiable hard requirement**; reverse conversion is not. | Every architecture and syntax candidate must demonstrate faithful conversion of existing content. |
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
| D-021 | Accepted direction | Source-level reuse dependencies are resolved at build time; published automated packages remain self-contained. | Demonstrated by shared assessments and shared-rule overlays across two Windows benchmarks. |
| D-022 | Accepted direction | Benchmark membership and source provenance should not be conflated with intrinsic policy-rule semantics. | Remove benchmark-specific generic source metadata from reusable rule semantics; provenance remains separate. |
| D-023 | Accepted direction | Combined-rule architecture must be evaluated using constrained shared-rule overlays rather than forced automation duplication. | Five Windows technical concepts now reused across Client and Server overlays. |
| D-024 | Accepted direction | Combined-rule overlays may specialize policy fields and declared parameters but must not directly patch shared assessment logic. | Build resolver enforces source separation; refine normative override list with reviewers. |
| D-025 | Accepted direction | Build validation should compare resolved automated policy fields with authoritative policy-only rules. | Implemented in iteration 001 builder. |
| D-026 | Open | Combined shared-rule overlays vs split policy/assessment/binding remains unresolved. | Both now demonstrate cross-STIG exact and parameterized reuse; seek reviewer feedback on lifecycle complexity. |
| D-027 | Accepted requirement | Benchmark scoring must be deterministic and reproducible; every scored rule needs an effective weight. | Prototype scoring after architecture examples stabilize. |
| D-028 | Open | Severity-derived default weights, exact numeric mapping, and exceptional per-rule overrides. | Compare mappings against representative STIGs and seek OVAL/DISA feedback. |
| D-029 | Open | Compliance scoring treatment of error/indeterminate/not-evaluated and whether assessment coverage is separately mandatory. | Prototype score + coverage results before external review. |
| D-030 | Accepted requirement | Every supported human-authoring syntax must be generatable from the same SCAP 1.4 faithful semantic conversion model. | Compare original and Ansible-inspired renderings of the same real OVAL cases and compile both to equivalent canonical semantics. |
| D-031 | Accepted direction | SCAP 1.4 conversion should use a faithful semantic intermediate representation before optional authoring-style rendering or reviewed normalization. | Prevent authoring syntax from driving migration semantics. |
| D-032 | Accepted requirement | Conversion must preserve policy, applicability, variables/parameters, automation logic, manual procedures, profiles, identifiers, and provenance when represented in the source datastream; unsupported or lossy constructs receive explicit migration status. | Expand converter fixtures across real datastreams. |
| D-033 | Accepted requirement | Final SCAP-NG specification readiness requires a repeatable automated conversion run across a versioned public SCAP 1.4 corpus manifest. | Corpus converter harness and pinned NIWC Current source added in iteration 001. |
| D-034 | Accepted requirement | Public-corpus conversion success must be construct-accounted; parsing alone is insufficient and unsupported/review-required constructs cannot be silently ignored. | Ingestion, migration-accounting, native-semantic, and differential-equivalence gates defined. |
| D-035 | Accepted direction | The stronger native-conversion gate should remain visibly failing until every in-scope configuration assessment is exact_native/exact_normalized or has an explicitly standards-approved exception. | Do not allow legacy compatibility to create a false completeness claim. |
| D-036 | Accepted architecture | SCAP 1.4 semantics are interpreted once into a faithful semantic IR; human authoring variants and canonical JSON are renderers of that IR. | Prevent separate converters and semantic drift. |
| D-037 | Accepted requirement | Conversion may derive only semantics justified by source content; ambiguous interpretation becomes `requires_review`. | No invented policy intent. |
| D-038 | Accepted requirement | Real-world migration evidence for iteration 001 must trace to pinned published NIWC `Current/` artifacts. | Development/experimental content removed from evidence corpus. |
| D-039 | Accepted priority | Initial depth targets are RHEL 9, Oracle Linux 9, Windows 11, and Windows Server 2025. | Mine hard semantics before broadening across all 65 individual published benchmarks. |
| D-040 | Accepted experiment | Quantify RHEL 9 ↔ Oracle Linux 9 and Windows 11 ↔ Server 2025 overlap at multiple semantic strengths. | Similar policy references alone do not establish reusable automation. |
