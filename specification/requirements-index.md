# SCAP-NG Requirements Index

**Status:** pre-alpha working specification index

This index tracks the major normative areas of SCAP-NG and distinguishes
requirements already supported by project decisions from areas that remain
under design.

## Normative areas

| Area | Specification section | Status |
| --- | --- | --- |
| Conformance roles and validation | `core/conformance.md` | draft |
| Benchmark / Rule / Group structure | `policy/benchmark.md` | draft |
| Platform specification and applicability | `policy/platform-and-applicability.md` | draft |
| Profiles and Tailoring | `policy/profiles-and-tailoring.md` | draft |
| Policy resolution/evaluation order | `policy/policy-resolution.md` | draft |
| Parameters and Organizational Input | `policy/parameters-and-organizational-input.md` | draft |
| Assessment Methods | `assessment/assessment-method.md` | draft |
| Manual Assessment defaults | `assessment/manual-assessment.md` | draft |
| Results and evidence | `results/results.md` | draft |
| Source, compilation, packaging, integrity | `package/package-and-integrity.md` | draft |
| SCAP 1.4 migration | `migration/scap-1.4-migration.md` | draft |
| OVAL 5.12.3 construct migration | `migration/oval-5.12.3-to-ng.md` | draft |
| OVAL 5.12.3 capability crosswalk | `migration/oval-5.12.3-capability-crosswalk.md` | informative appendix |
| Security considerations | `security/security-considerations.md` | initial draft |
| SCAP 1.4 / SP 800-126r4 concept review | `crosswalk/sp800-126r4-concept-review.md` | informative |

## Cross-cutting principles

SCAP-NG SHALL preserve one authoritative semantic location for each property.

SCAP-NG SHALL distinguish policy from assessment implementation.

SCAP-NG SHALL favor explicit author-controlled relationships over processor
inference.

SCAP-NG SHALL support lossless migration of supported SCAP 1.4 semantics before
optional native refactoring.

SCAP-NG policy SHALL preserve selectable-check semantics. An explicitly
requested check selector that does not resolve SHALL fail rather than silently
falling back to another or default check.

SCAP-NG automated assessment semantics SHALL represent existence and
cardinality explicitly. Expected absence and expected presence SHALL have
portable truth semantics independent of scanner implementation.

SCAP-NG source organization and filenames MAY aid authors, but semantic
identity and object type SHALL come from object content rather than path or
filename.

Historical SCAP 1.4 provenance MAY be retained in authoring comments and
conversion reports. Historical lineage SHALL NOT be required in scanner-facing
objects merely because content originated in SCAP 1.4.

## Open architectural areas

The following remain explicitly open and SHALL NOT be treated as settled by
this index:

- final cross-mode outcome vocabulary;
- exact Tailoring rule-selection semantics;
- final severity and scoring models;
- final set of SCAP-NG use cases;
- final source serialization policy for publishers;
- final schema for richer manual observations/questions;
- final extension and digital-signature wire formats;
- final privacy/redaction requirements for sensitive results and inputs.
