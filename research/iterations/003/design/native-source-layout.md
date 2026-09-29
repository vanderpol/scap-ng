# Iteration 003 Native Source Layout

## Governing principle

A separate native file/object must justify its existence through semantic
independence, reuse, ownership, or maintainability.

SCAP 1.4 decomposition is not sufficient justification.

## Benchmark-owned policy

benchmark.yaml owns:

- Benchmark identity and metadata;
- target Platform identity/reference;
- Rule membership;
- meaningful Group hierarchy;
- publisher-defined Profiles;
- Benchmark/policy Parameters and publisher defaults;
- Benchmark-level policy composition.

Iteration 003 SHALL NOT generate standalone:

- profiles.yaml
- groups.yaml
- values.yaml
- platforms.yaml
- processing.yaml

## Applicability registry

A small applicability.yaml remains in the split-rule-assessment design as an
indirection layer:

    applicability ID -> Assessment Method

Rules reference applicability IDs rather than Assessment file paths.

The registry SHALL contain only native SCAP-NG identity/binding information and
SHALL NOT contain migrated XCCDF/OVAL/CPE structures.

## Source organization

    source/
      split-rule-assessment/
        <benchmark>/
          benchmark.yaml
          applicability.yaml
          rules/
          assessments/
            automated/
            manual/
            applicability/

Reusable/shared Assessments may later move into a clearly named shared subtree
once exact reuse is demonstrated.

Source and sample results SHALL remain in different top-level directories.


## Explicit native field visibility

Iteration 003 SHALL favor self-describing source over implicit defaults or
tribal knowledge.

For native objects intended for human authoring/review, every field supported
by that object type SHOULD be serialized even when it has no value.

Use:

- `null` for an optional scalar/object that is supported but unset;
- `[]` for a supported collection with no members;
- `{}` for a supported mapping with no entries.

A field SHALL be omitted only when it is not part of that native object model
or when omission has a deliberately defined semantic meaning.

This rule applies especially to Rule source. The supported Rule
surface for iteration 003 is:

    rule:
      id:
      version:
      title:
      severity:
      role:
      weight:
      discussion:
      rationale:
      extensions:
      warnings:
      identifiers:
      references:
      requires:
      conflicts:
      applicability:
      parameters:
      remediation:
      checks:
      default_check:

The exact vocabulary may evolve during iteration 003, but once a field is part
of the supported Rule model it SHALL remain visible in generated review
source even when unset.

This is intentionally different from opaque legacy content models where authors
and reviewers needed external schema knowledge to discover available
properties.

This explicit-field rule does not override Profile canonicalization decisions
where omission itself is semantically meaningful (for example, omission of
`disabled_rules` means the Profile does not alter Benchmark Rule selection).


## Hierarchical Group taxonomy

Groups SHALL support child Groups recursively.

For the iteration-003 migration experiment, the preferred generated hierarchy
is assessment-oriented at the top level and functional beneath it.

Illustrative form:

    groups:
      - id: automated
        title: Automated
        groups:
          - id: automated.ssh
            title: SSH
            rules:
              - RHEL-09-...
          - id: automated.password-policy
            title: Password Policy
            rules:
              - RHEL-09-...

      - id: manual-or-managerial
        title: Manual or Managerial
        groups:
          - id: manual-or-managerial.account-management
            title: Account Management
            rules:
              - RHEL-09-...
          - id: manual-or-managerial.documentation
            title: Documentation / Managerial Review
            rules:
              - RHEL-09-...

The top-level classification SHOULD follow the Rule's effective/default
Assessment Method, not merely the existence of an alternate manual check.

A Rule whose default check is automated but that also provides a manual
alternative belongs under `automated` unless human/managerial judgment is
material to the effective policy decision.

Functional subgrouping MAY be inferred from title, discussion, remediation,
manual procedure, Assessment capability, and affected configuration artifact.

Generated Group classification is migration metadata and navigation structure.
It SHALL NOT alter Rule applicability, Rule selection, Assessment behavior,
Parameter binding, or result semantics.

When the converter cannot infer a useful functional subgroup with sufficient
confidence, it SHOULD place the Rule under a `needs-grouping` child of the
appropriate assessment-mode parent rather than fabricate a topic.


## Relationship to XCCDF design

SCAP-NG is replacing the XCCDF serialization and legacy SCAP coupling model,
not discarding useful policy-language design merely because it originated in
XCCDF.

Iteration 003 SHOULD retain or adapt XCCDF concepts when they remain useful,
clear, and interoperable in a native NG model.

Examples include:

- Benchmark as the authoritative policy container;
- hierarchical Groups;
- Profiles as publisher-defined Benchmark variations;
- Rule-level policy metadata such as severity, role, weight, rationale,
  warnings, identifiers, references, dependencies, and remediation;
- explicit check selection;
- typed policy Parameters;
- platform and Rule applicability composition.

These concepts SHOULD be simplified where historical XCCDF behavior was
needlessly complex, but their useful semantics SHOULD NOT be removed simply to
make NG look different.

The design test is:

1. Does the concept have demonstrated authoring, interoperability, or execution
   value?
2. Can it be represented more clearly without legacy XML/SCAP coupling?
3. Can it remain self-describing without hidden defaults or schema tribal
   knowledge?

If yes, SCAP-NG SHOULD preserve the concept in native form.

Legacy XML namespaces, opaque identifiers, component hrefs, wrapper structures,
and cross-language stovepipes remain out of native NG source.


## Explicit Benchmark surface

The same explicit-field rule used for Rule applies to `benchmark.yaml`.

The Benchmark is the complete native policy-publication record. A reader SHALL
NOT need knowledge of the historical source schema to discover which
Benchmark-level properties SCAP-NG supports.

For iteration 003, the supported Benchmark surface is:

    benchmark:
      id:
      title:
      description:
      language:
      status:
      version:
      metadata:
      notices:
      front_matter:
      rear_matter:
      references:
      text_blocks:
      platform:
      applicability_catalog:
      scoring:
      parameters:
      groups:
      profiles:
      rules:

Supported fields SHOULD remain visible even when their value is `null`, `[]`,
or `{}`.

### Benchmark-level conversion intent

The converter SHALL preserve the information content of useful source
Benchmark-level properties in native form, including:

- status and status dates;
- title and description;
- natural-language identity;
- legal/advisory notices;
- document-generation front matter and rear matter;
- references;
- reusable human-readable text blocks when still referenced after conversion;
- Benchmark platform applicability;
- version, version time, and update location;
- authorship/publisher/support/discovery metadata;
- suggested scoring models and parameters when retained by NG;
- Parameters;
- Groups;
- Profiles;
- Rules.

Multiple source values such as multilingual titles/descriptions SHALL NOT be
collapsed when doing so would lose information. The native form SHOULD use
structured entries containing language where needed.

### Benchmark-level source properties intentionally relocated or removed

Some historical Benchmark children/attributes do not belong in native
`benchmark.yaml` even when they appeared at the source Benchmark level:

- historical assessment results belong under the NG result model, not policy
  source;
- XML digital signatures are replaced by NG package/signature provenance rather
  than embedded XML signature structure;
- XML signature helper IDs are not native content;
- source-resolution state is compiler provenance, not authored policy;
- authoring `style` / stylesheet URLs are not retained unless a concrete NG
  interoperability requirement is demonstrated;
- XML namespaces and XML base/URI processing state are never native NG policy.

These omissions are intentional model decisions, not accidental conversion
loss.

### Metadata

Known metadata SHOULD be normalized into native fields rather than preserved as
arbitrary XML.

The Benchmark `metadata` mapping MAY carry useful publication metadata that
does not already have a first-class Benchmark property, for example creator,
publisher, contributor, subject, rights, source, and support/contact data.

Raw XML metadata elements and namespace-qualified keys SHALL NOT appear in
native source.

If arbitrary source metadata cannot be normalized without information loss, the
converter SHALL report it for design review rather than embedding an XML-shaped
blob.

### Regeneration goal

The lossless-conversion target is sufficient native information to regenerate
the same meaningful Benchmark publication data and policy semantics.

It is not byte-for-byte reproduction of the original XML serialization.


## First-class manual assessment

SCAP-NG treats manual assessment as a native Assessment Method, not as a
secondary legacy questionnaire mechanism.

A publisher MAY provide automated and manual Assessment Methods for the same
Rule and expose them through normal check selection.

When a publisher supplies a manual Assessment Method directly, downstream
content processors SHOULD NOT need to construct an additional questionnaire
artifact merely to make that Rule manually assessable.

This design can eliminate historical enrichment workflows in which a downstream
organization had to add manual-question content to an otherwise complete
Benchmark solely because the publication format separated automated and manual
assessment mechanisms.

Migration evidence describing such historical enrichment SHALL remain in the
conversion evidence, while the native NG source SHOULD represent the resulting
manual Assessment directly.

## Assessment human-readable labels

Assessment source SHALL use labels that identify the semantic object being
described rather than overloading a generic `title` property at every level.

Iteration 003 uses:

- `assessment_title` for the Assessment Method;
- `test_title` for an executable test/check node;
- `object_title` for collected target/object meaning;
- `state_title` for expected-state meaning.

These labels MAY be populated from useful human-readable source comments during
conversion. Legacy source identifiers and namespaces SHALL NOT be carried into
native labels.


## Candidate publisher metadata versus core Rule semantics

Iteration 003 SHALL distinguish between:

1. semantics explicitly defined by XCCDF and intentionally carried forward into
   SCAP-NG; and
2. publisher-specific metadata discovered inside source content but not defined
   as first-class XCCDF semantics.

Publisher-specific metadata SHALL NOT become normative SCAP-NG Rule fields
merely because it is present in DISA STIG content.

Examples currently observed in DISA STIG Rule description payloads include:

- documentable;
- false positives;
- false negatives;
- mitigations;
- potential impacts;
- responsibility.

These fields are useful enough to preserve during conversion, but their
inclusion in the eventual SCAP-NG core model is an open governance question.

For iteration 003:

- their original values SHALL remain preserved in conversion evidence;
- they MAY be emitted in an explicitly marked experimental/publisher metadata
  section for review;
- they SHALL NOT be treated as settled core Rule properties;
- promotion into the core Rule vocabulary requires an affirmative design
  decision, ideally with OVAL Board / standards-community review.

The review question for each such field is:

- Is this broadly useful policy metadata beyond DISA STIGs?
- Does it affect assessment, tailoring, remediation, reporting, or
  interoperability?
- Is there demonstrated producer/consumer use?
- Would preserving it impose meaningful implementation burden?
- Is it better represented as general extensible publisher metadata instead of
  a standardized first-class field?

This prevents SCAP-NG from standardizing accidental publisher conventions while
still preserving information losslessly during migration.


### DISA STIG publisher metadata in the 003 review slice

The following values found inside DISA STIG Rule description payloads are not
first-class XCCDF Rule properties and are therefore not core SCAP-NG Policy
fields in iteration 003:

- `documentable`;
- `false_positives`;
- `false_negatives`;
- `mitigations`;
- `potential_impacts`;
- `responsibility`.

When preserved in native review source they SHALL appear under an explicitly
publisher-specific extension, for example:

    extensions:
      disa_stig:
        documentable: false
        false_positives: null
        false_negatives: null
        mitigations: null
        potential_impacts: null
        responsibility: null

Their inclusion in a future core SCAP-NG vocabulary is an open standards
question and requires affirmative governance review.


## Benchmark applicability catalog reference

When the Benchmark uses named Rule applicability conditions, the Benchmark
source SHALL expose an explicit `applicability_catalog` field.

For the iteration-003 split-rule-assessment layout:

    applicability_catalog: applicability.yaml

This field is a source reference, not a naming convention. A processor SHALL
NOT infer the applicability catalog from the presence, filename, or directory
location of `applicability.yaml`.


## Object filename conventions

Human-readable filenames SHOULD identify the native object type even when the
containing directory also conveys that information.

For iteration 003, Rule files use:

    <rule-id>.rule.yaml

and compiled/package Rule objects use:

    <rule-id>.rule.json

Assessment filenames continue to identify their Assessment role/type using
their established suffixes.

Filename conventions aid authors and reviewers but SHALL NOT establish semantic
identity or Benchmark membership. Stable logical IDs remain authoritative, and
the package manifest resolves those IDs to packaged paths.
