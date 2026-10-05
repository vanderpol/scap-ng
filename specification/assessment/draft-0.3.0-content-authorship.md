# Draft 0.3.0 content authorship

**Status:** deferred design tracker for SCAP-NG 0.3.0; non-normative; does not change 0.2.0 schema.

## Problem

Converted native SCAP-NG content needs to distinguish **who authored the security check** from:

- the repository that supplied the SCAP 1.4 package;
- the organization that enhanced or repackaged the source;
- the converter/operator that performed migration;
- the organization that normalized or compiled the resulting NG content.

Using a repository/publisher prefix such as `niwc.` in native Assessment IDs falsely suggests that NIWC authored every converted Assessment. That is not a valid provenance claim.

The 0.2.0 converter therefore uses publisher-neutral native IDs and keeps repository/source information as migration provenance.

## Proposed 0.3.0 Assessment field

Add a first-class free-text Assessment property:

```yaml
assessment:
  id: benchmark.rhel_9.SV-257777.automated
  version: 1
  content_author: DISA
```

Proposed semantics:

- `content_author` identifies the organization/person credited with authoring the Assessment/check content.
- It is **free text**, not an enum.
- Native authors MAY enter any appropriate attribution string.
- It SHALL NOT be inferred from the repository or converter identity when better source authorship evidence exists.
- Repository/source/converter provenance remains separate metadata.
- Shared and applicability Assessments use the same field.

## SCAP 1.4 conversion guidance

For automated content converted from OVAL, the converter SHOULD derive Assessment authorship from the **root source OVAL Definition identity** when that identity provides reliable publisher information.

Initial deterministic rules for the demonstration corpus:

- source Definition ID contains `disa` (case-insensitive) → `content_author: DISA`;
- source Definition ID contains `navwar` or `niwc` (case-insensitive) → `content_author: NIWC`;
- otherwise → do not guess; leave author unset/unknown unless another authoritative source metadata field identifies the author.

The exact source Definition ID SHALL remain in migration provenance even after authorship is derived.

## Extended Definition / mixed provenance

OVAL `extend_definition` can incorporate logic from other Definitions.

The proposed authorship rule is:

- the converted Assessment's `content_author` follows the **root Definition** that corresponds to the Rule/check being migrated;
- referenced/extended Definitions retain their own source identity in detailed migration provenance;
- a nested NIWC/NAVWAR Definition SHALL NOT cause an otherwise DISA-authored root Assessment to be relabeled NIWC;
- if future authoring intentionally combines independently authored native Assessments, provenance may identify multiple contributors without overloading `content_author`.

This keeps the human attribution simple while preserving complete technical lineage separately.

## Applicability Assessments

Applicability Assessments are authored content and follow the same attribution rules.

If an applicability Assessment is proven semantically identical across multiple Benchmarks and normalized into `shared/assessments/`, its `content_author` SHALL come from the underlying authored check rather than from the Benchmark that happened to be processed first.

## Shared Assessment normalization

Normalization SHALL NOT change content authorship merely because an Assessment becomes shared.

If exact duplicate Assessments carry conflicting non-empty `content_author` values, the normalizer SHALL NOT silently select one. The conflict must be surfaced for review or the values must be shown to be aliases for the same author before promotion.

## Open 0.3.0 decisions

1. Should `content_author` be required or optional?
2. Should the schema permit one string or a structured list of credited authors/contributors?
3. Should Benchmark and Rule objects receive the same first-class authorship field?
4. Should a separate `content_maintainer` field exist, or is that better represented only in repository/provenance metadata?
5. How should source-generator metadata interact with Definition-ID-derived attribution?
6. What exact provenance structure should retain all source Definition IDs involved through `extend_definition`?
7. Should unknown converted authorship be omitted or explicitly represented as `unknown`?

## Promotion requirements

Before this becomes normative 0.3.0 schema:

- validate the derivation rules against a representative DISA/NIWC corpus;
- add positive/negative schema fixtures;
- add conversion regression tests for DISA, NIWC/NAVWAR, unknown, applicability, shared content and `extend_definition`;
- verify normalization cannot silently change attribution;
- document the field in the glossary and SCAP 1.4 → NG crosswalk.
