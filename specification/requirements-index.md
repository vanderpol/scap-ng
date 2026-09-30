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

SCAP-NG SHOULD reuse established NIST/SCAP/XCCDF/OVAL terminology when the
existing term remains semantically correct. New normative terminology SHOULD
be introduced only when no existing standards term accurately represents the
NG concept or when retaining the legacy term would preserve obsolete
architecture or ambiguity. Intentional terminology changes SHOULD be recorded
in the SCAP 1.4 compatibility crosswalk.

SCAP-NG policy SHALL preserve selectable-check semantics. An explicitly
requested check selector that does not resolve SHALL fail rather than silently
falling back to another or default check.

SCAP-NG automated assessment semantics SHALL represent existence and
cardinality explicitly. Expected absence and expected presence SHALL have
portable truth semantics independent of scanner implementation.

SCAP-NG Assessment Methods SHALL declare an Assessment class independently
from invocation purpose. The inherited class vocabulary is `compliance`,
`vulnerability`, `patch`, `inventory`, and `miscellaneous`. A true
Assessment result SHALL be interpreted according to its declared class rather
than universally as pass/fail.

Applicability SHALL be modeled as invocation purpose, not as an Assessment
class. A conforming processor SHALL preserve both the Assessment class and the
purpose for which it was invoked.

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
- whether to add an `information` Assessment class; this is not an inherited
  OVAL class and requires affirmative OVAL Board / SCAP-NG governance approval
  before becoming normative;
- exact Tailoring rule-selection semantics;
- final severity and scoring models;
- final set of SCAP-NG use cases;
- final source serialization policy for publishers;
- final schema for richer manual observations/questions;
- final extension and digital-signature wire formats;
- final privacy/redaction requirements for sensitive results and inputs.

<!-- spec-nav:start -->

---

**Specification navigation:** [← Previous: SCAP-NG Terminology](terminology.md) · [Contents](README.md) · [Next: Conformance →](core/conformance.md)

<!-- spec-nav:end -->


## Open blocker: OVAL Object behavior defaults

Before certifying the v003 Assessment model as fully OVAL-compatible, the
project SHALL inventory and verify all Object `behaviors` types and
their XSD/Schematron constraints; derive and expose effective defaults where
normatively established; and execution-test behavior variants.

The current converter copies explicit behavior attributes but does not fully
normalize inherited/implicit defaults or prove behavior execution. This is
**not** resolved merely by green document round-trip CI. See
[behavior audit](../research/iterations/003/design/oval-object-behaviors-audit.md).

## OVAL schema-to-assessor specification program

The OVAL 5.12.3 XSD/Schematron semantics extraction starts during iteration
003. The project SHALL track each inherited semantic requirement to its
upstream schema/constraint anchor and to an NG model location, implementation
status, and conformance test. This does **not** mandate copying the XML schemas
or all their annotations verbatim into the native NG specification.

Priority order:

1. graph, reference, criteria, class, and result semantics;
2. Test/Object/State, existence, states, comparisons, quantifiers, sets,
   filters, behaviors and schema defaults;
3. variable kinds, allowed values/restrictions, functions and dataflow;
4. per-family and per-capability entity typing and schema constraints;
5. collector execution rules, complete error/unknown propagation and
   target-evaluation conformance; and
6. results, evidence and operational security rules.

Generic assessor semantics supported by schema and comparative evidence
SHOULD enter the draft now. Platform-specific execution details SHOULD remain
provisional until reference-scanner behavior and differential fixtures
support normative claims.

The complete discovery ledger and staged proof gates are in
[OVAL-derived specification lessons](../research/iterations/003/design/oval-derived-specification-lessons.md).
