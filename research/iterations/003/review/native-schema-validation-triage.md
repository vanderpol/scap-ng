# Native SCAP-NG schema-validation triage

**Status:** active  
**Started:** 2026-10-02  
**Purpose:** classify every native schema-validation failure before changing either content or schema.

## Classification rules

Every failure is classified as one of:

- **content defect** — the document violates an established current SCAP-NG contract;
- **schema defect** — the schema rejects content that matches an established current design decision;
- **generator drift** — generated content predates or fails to materialize a current schema/design decision;
- **validator/classifier defect** — the wrong schema was selected or validation logic is incorrect;
- **historical/example drift** — an intentionally retained research fixture uses an older pre-alpha shape;
- **semantic-validator concern** — JSON Schema is not the correct layer for the rule.

No fix is made merely to make validation green. The design decision and source semantics determine whether content or schema changes.

## Initial validation pass

### TRIAGE-001 — committed RHEL9 full source tree

**Classification:** generator/content-version drift in committed artifact, not current generator logic.

The committed tree under `research/iterations/003/source/split-policy-assessment/rhel9-full` predates later current-design requirements. Examples include Rules using a legacy `policy:` pointer instead of `assessment_choices` / `default_assessment_choice`, nullable source Rule role values instead of materialized `full`, and Benchmark documents lacking later required discovery fields.

The current generator `tools/scap_upconvert_v003/convert_full_review.py` already emits the current structures, including:

- `role: full` when source role is omitted;
- `assessment_choices` and `default_assessment_choice`;
- `organizational_input_requirements`;
- `ng_schema_version`;
- `assessment_specifications`;
- `default_selection`.

**Disposition:** validate freshly generated current content as the normative CI gate; regenerate or replace the committed review tree separately rather than weakening current schemas.

### TRIAGE-002 — `tools/fixtures/rhel9-tailoring`

**Classification:** historical/example drift.

This compact fixture intentionally contains skeletal Benchmark and Rule documents that no longer satisfy the complete current authoring contract.

**Disposition:** keep visible as a migration/update task. Do not weaken Benchmark/Rule schemas to accept skeletal legacy fixtures.

### TRIAGE-003 — results-model-bakeoff examples

**Classification:** historical/example drift pending field-by-field migration review.

The examples use an earlier result model, including:

- YAML booleans for technical outcomes instead of the current string truth vocabulary;
- bare scalar collected Item fields instead of typed values;
- older Object/Test result field names;
- nested `evaluation` / `summary` structures superseded by the current completeness/evidence model.

**Disposition:** migrate the examples to the current result model after confirming each newer schema decision. Do not loosen current result schemas solely to preserve the bakeoff serialization.

### TRIAGE-004 — tailoring-all-options example

**Classification:** historical/example drift with useful design coverage.

The example exercises valuable tailoring semantics but predates portions of the current complete Benchmark/Rule contract.

**Disposition:** update this example deliberately after fresh-current validation is green; preserve its semantic coverage rather than deleting it.

## Required validation order

1. Validate every JSON Schema itself against Draft 2020-12.
2. Validate freshly generated current NIWC native content.
3. Validate normalized current NIWC content.
4. Validate current maintained focused fixtures/examples.
5. Run semantic/reference validation.
6. Migrate historical examples and add them to the required gate only after they match the current design.

## Exit criteria

The schema-validation milestone is green only when:

- the current JSON Schemas are meta-schema valid;
- fresh current native generation validates before normalization;
- normalized current native generation validates;
- capability State/Item parity remains green;
- maintained current fixtures validate;
- all remaining failures are explicitly classified as deferred historical/example migration work or semantic-layer checks.


## Prior fresh-current baseline evidence

The previously committed full-current native validation evidence records:

- freshly generated native documents checked before normalization: **25,147**;
- valid before normalization: **25,147**;
- invalid before normalization: **0**;
- normalized corpus invalid documents: **0**.

This is strong evidence that the current generator/schema contract was internally consistent across the 65-package NIWC Current corpus at that checkpoint. The current rerun remains authoritative for the latest commit because capability/schema work has continued since that evidence was produced.

This baseline also confirms that failures from committed historical review trees and bakeoff examples should not be generalized into schema defects without reproducing them in freshly generated current content.


## First triage outcome — 2026-10-02

The first broad repository validation failures did **not** establish defects in the current SCAP-NG JSON Schemas.

Classifications:

- committed RHEL9 review tree: **generator/content-version drift**;
- compact RHEL9 tailoring fixture: **historical/example drift**;
- results-model-bakeoff examples: **historical result-model drift**;
- tailoring-all-options example: **historical/example drift with useful semantic coverage**.

The current schema meta-validation gate is green. The current-only schema-validation workflow is also green after historical/review artifacts were separated into an advisory audit rather than treated as normative current content.

No schema was weakened merely to make stale examples validate.

## Semantic-validation phase

With structural schema validation green for fresh/current content, the next required layer is Assessment graph validation. The full-current workflow now validates both fresh generated and normalized corpora for:

- Test → Object existence;
- Test → State existence;
- Test/Object/State capability agreement;
- Test → Variable existence for direct Variable-backed tests;
- Set → Object existence and capability agreement;
- Set filter → State existence and capability agreement;
- capability-specific cross-field semantics currently implemented by the native semantic validator.

Semantic failures SHALL receive the same triage treatment as schema failures: classify as content/generator defect, semantic-validator defect, schema/design defect, or source migration issue before changing either content or validation rules.


## Generated capability-schema gate

The maintained Capability State/Item parity workflow now also generates every reviewed capability mapping and validates each generated fragment against JSON Schema Draft 2020-12.

Initial combined result on 2026-10-02: **green**.

This closes a gap that static top-level schema validation alone could not cover: a reviewed mapping or generator change can no longer silently produce a malformed capability schema while the shared schemas remain valid.


## Package-graph validation phase

Structural file validation and intra-Assessment graph validation are now complemented by a standalone cross-document package validator.

The validator checks, independently of the converter:

- Benchmark Rule IDs resolve to Rule documents;
- applicability catalog references resolve to the correct document type;
- applicability conditions resolve to Assessment documents;
- each Rule default assessment selector exists;
- every Rule assessment choice resolves to an Assessment;
- Rule applicability identifiers resolve to catalog conditions;
- Rule `requires` / `conflicts` references resolve to Benchmark Rules;
- Benchmark platform applicability identifiers resolve;
- Benchmark grouping contains exactly the Benchmark Rule population with no loss or duplication;
- duplicate native document identities are diagnosed;
- references cannot escape the package root.

The full-current workflow runs this check both before and after normalization. This specifically tests that normalization cannot preserve local JSON Schema validity while breaking the package graph.

As with schema failures, package-graph failures SHALL be triaged before repair as source/content defects, generator defects, normalizer defects, or validator defects.
