# SCAP-NG Schema Creation Research

**Status:** research only — no schema approved or created  
**Iteration:** 002  
**Date:** 2026-09-28  
**Purpose:** prepare a schema strategy for project-owner review before any
normative or prototype SCAP-NG schema files are introduced.

This document intentionally stops short of creating a SCAP-NG schema. The
project owner will review the current iteration-002 content before authorizing
schema creation.

## Research question

At what point should SCAP-NG begin formal schema work, and which parts can be
constrained safely before OVAL Board review?

The current conclusion is:

> Begin schema design research now. If approved, create a pre-alpha
> design-validation schema before OVAL Board review, but do not freeze the
> Assessment execution-language portions until Board feedback has been
> incorporated.

A schema at this stage would be a tool for exposing ambiguity and validating
the four-anchor examples. It would not be a compatibility commitment.

## Candidate schema technology

### Recommended starting point: JSON Schema Draft 2020-12

The current research recommendation is to use **JSON Schema Draft 2020-12** as
the structural schema language for both YAML and JSON SCAP-NG authoring
documents.

Reasons:

- SCAP-NG authoring objects are already designed as JSON-compatible mappings,
  sequences, scalars, and references.
- YAML 1.2 authoring can be parsed into the JSON data model and validated
  against the same structural schema.
- JSON Schema Draft 2020-12 supports modular schema composition with
  `$id`, `$ref`, and `$defs`.
- `$dynamicRef` / `$dynamicAnchor` provide a possible extension mechanism
  if recursive or capability-specific composition later requires it.
- `unevaluatedProperties` can support deliberate control over unknown fields
  after composed schemas have been applied.
- Compound schema documents/bundling are defined by the JSON Schema model if
  distribution later benefits from bundling several schema resources.
- A single schema technology can validate equivalent YAML and JSON source
  serializations.

Primary references researched:

- https://json-schema.org/draft/2020-12/
- https://json-schema.org/draft/2020-12/json-schema-core
- https://yaml.org/spec/1.2.2/

This is a recommendation for review, not yet a normative SCAP-NG dependency.

### Why not use YAML syntax as the schema language

YAML is an authoring serialization, not a sufficient semantic validation model
by itself.

SCAP-NG SHOULD avoid defining validation by YAML parser behavior because:

- equivalent JSON source should remain possible;
- YAML tags and implementation-specific coercion could create portability
  problems;
- schema validation should operate on the normalized data model after parsing.

If schema creation is approved, SCAP-NG should define a supported YAML subset
compatible with its JSON data model rather than permit arbitrary YAML-native
types/tags.

### Why not use XML Schema

XSD would reintroduce an XML-centered toolchain that SCAP-NG is intentionally
moving away from. It also would not naturally validate the native YAML source
being designed in iteration 002.

The SCAP 1.4 XSD schemas remain essential migration inputs and compatibility
references, but they should not dictate the NG authoring schema technology.

### Custom JSON Schema vocabulary

JSON Schema 2020-12 supports formal vocabularies, which could theoretically be
used for SCAP-NG-specific validation keywords.

The current recommendation is **not** to create a custom SCAP-NG JSON Schema
vocabulary initially.

A custom vocabulary would increase validator implementation burden and should
only be introduced when ordinary JSON Schema plus a semantic validator cannot
express a requirement cleanly.

## Two validation layers

A key schema-design conclusion is that SCAP-NG will require both structural and
semantic validation.

### Layer 1 — structural schema validation

JSON Schema should validate properties such as:

- object shape and required fields;
- scalar datatypes;
- enumerated values;
- local field combinations;
- Boolean-expression syntax;
- identifier/reference syntax;
- modality-specific object shape;
- standard result object shape;
- target-inventory representation;
- extension containers.

### Layer 2 — SCAP-NG semantic validation

A separate SCAP-NG validator will still be required for rules such as:

- referenced files/objects SHALL resolve exactly once;
- logical IDs SHALL be unique in the applicable scope;
- `default_check` SHALL name an exposed selector;
- a requested Tailoring selector SHALL exist;
- Profile/Tailoring resolution order;
- Rule-to-Assessment reference validity;
- Parameter binding compatibility;
- applicability catalog resolution;
- capability availability and compatibility;
- cross-object identity collisions;
- Assessment dependency cycles where prohibited;
- package/reference integrity;
- migration-equivalence checks;
- semantic restrictions that require information from multiple source files.

The schema should not be distorted in an attempt to encode every cross-document
semantic requirement.

## Candidate modular schema organization

If schema creation is approved, the initial tree should be modular rather than
one monolithic schema.

A possible source layout is:

    schema/
      0.1/
        common.schema.json
        benchmark.schema.json
        policy.schema.json
        profile.schema.json
        tailoring.schema.json
        parameter.schema.json
        platform.schema.json
        applicability.schema.json
        assessment.schema.json
        manual-assessment.schema.json
        result.schema.json
        assessment-request.schema.json
        capabilities/
          common.schema.json
          independent/
          linux/
          unix/
          windows/
          ...

The exact paths and names remain research questions.

The schema resource ID SHOULD be independent of the repository path so schemas
can later be moved, bundled, or published without changing their semantic
identity.

## Areas sufficiently stable to schema before OVAL Board review

The following portions of the current model appear mature enough to benefit
from a pre-alpha design-validation schema.

### Benchmark

Candidate constraints include:

- logical ID;
- title;
- version/revision;
- publisher;
- Platform expression;
- Rule references;
- Group references/structure;
- Profile references;
- applicability-catalog reference;
- Parameter definitions/references.

### Rule policy

Candidate constraints include:

- logical ID and revision;
- title/severity/discussion;
- references/identifiers;
- remediation;
- Rule applicability expression;
- policy-to-check-selector structure;
- Assessment references.

### Check selection

This area is now supported by real four-anchor conversion evidence.

Candidate constraints include:

- one or more named selectors;
- selector identifier syntax;
- Assessment reference on each selector;
- optional `default_check`;
- Tailoring/Profile `check_selector` representation.

Some validity rules, such as ensuring `default_check` names an actual selector,
remain semantic-validator responsibilities.

### Profile and Tailoring

The source shape for:

- Rule enable/disable deltas;
- selector refinement;
- Parameter value refinement;
- inheritance/revision metadata

can be structurally constrained now, while exact processing remains normative
specification text plus semantic validation.

### Parameters and Organizational Input

The distinction between Parameter definition, effective value, and
Organizational Input is sufficiently important and stable to schema early.

The schema should support explicit typed values rather than a universal
string-valued variable surface.

### Platform and applicability policy

The stable structural concepts include:

- stable Platform logical identity;
- explicit Platform Assessment reference;
- Boolean Platform expressions;
- applicability catalog;
- Rule `when` expression containing named applicability conditions.

The CPE work reinforces that target inventory output is separate from
applicability truth.

### Manual Assessment

The Manual Assessment contract is relatively stable and can be structurally
constrained independently of the automated Assessment language.

### Results and target inventory

The following structures are good early schema candidates:

- run metadata;
- target identity;
- descriptive target product inventory;
- OS/application external identifiers including CPE;
- Rule result identity;
- outcome;
- deterministic message;
- structured reason;
- bounded evidence;
- selector/Assessment provenance;
- completeness flags.

### File/object type conventions

Schemas can provide object-type validation while repository tooling separately
enforces filename conventions such as `.policy.yaml` and
`.assessment.yaml`.

## Areas that should remain deliberately provisional before Board review

The deepest automated Assessment execution model should be schema-drafted only
far enough to validate experiments. Its structure should not be frozen before
OVAL Board review.

### Collection/object model

Questions still likely to benefit from OVAL Board input include:

- relationship between capability, object/query, and collected entities;
- multiple-object joins;
- object sets;
- filters;
- variable-derived collection;
- platform-family differences;
- historical OVAL test-family suffix/version treatment.

### State/predicate model

Still provisional:

- entity comparison representation;
- datatype operations;
- pattern/regex rules;
- state operators;
- multi-state relationships;
- missing/entity-status semantics.

### Test/evaluation model

Still provisional:

- quantifiers;
- `check` semantics;
- complete `check_existence` / cardinality surface;
- state_operator interactions;
- Boolean criteria trees;
- error/unknown/not-evaluated propagation.

The current existence semantics should be retained as required behavior, but
their final serialization should remain open.

### Variables/derive model

Board review is especially valuable for:

- external variables;
- local variables;
- object components;
- function composition;
- variable dependency closure;
- structured Organizational Input binding;
- avoiding the XCCDF-to-OVAL variable stovepipe.

### Capability-specific schema

Capability families should not be frozen until:

- the generic Assessment envelope is stable;
- the OVAL family/test crosswalk has been reviewed;
- the handling of historical numbered OVAL test types is decided;
- representative real content has demonstrated the proposed native shape.

## Recommended schema extension model

A likely approach is:

1. one stable generic Assessment envelope;
2. a declared capability name;
3. capability-specific structural schema selected by that capability;
4. shared schemas for common collection/state/evaluation constructs;
5. explicit extension points for publisher/private metadata that cannot alter
   core execution semantics.

This would permit:

    capability: windows.registry

to select Windows Registry-specific collection fields without making one giant
schema contain every capability's properties at every node.

How capability dispatch is expressed in JSON Schema—static `oneOf`, generated
capability unions, or another mechanism—should be tested before approval.

## Strictness strategy

The schema should be strict enough to catch misspelled or unexpected semantic
fields.

For core objects, the preferred direction is to reject unknown core properties
unless they appear in a defined extension container.

JSON Schema 2020-12 `unevaluatedProperties: false` is a candidate mechanism
for composed schemas.

However, strictness must be tested carefully around:

- schema composition;
- future capability extensions;
- publisher metadata;
- migration provenance;
- forward compatibility.

The project should avoid both extremes:

- arbitrary unknown fields everywhere; and
- a schema so closed that every extension requires changing the core schema.

## Versioning research

The schema version and SCAP-NG specification version should be related but
should not be conflated automatically.

Questions for review:

- Does each SCAP-NG release identify one normative schema set?
- May compatible schema errata occur without changing the SCAP-NG language
  version?
- How are experimental pre-alpha schemas identified?
- Does each source object declare its SCAP-NG language version?
- Do individual capability schemas version independently, or only with the
  containing language version?

For initial experimentation, any schema created after approval should be
clearly marked:

    SCAP-NG 0.1 pre-alpha / design-validation only

and SHALL NOT imply stable compatibility.

## YAML parsing constraints to research before schema approval

Because schema validation occurs after YAML parsing, SCAP-NG should eventually
state parsing constraints such as:

- YAML 1.2-compatible scalar resolution;
- duplicate mapping keys are invalid;
- custom/application-specific YAML tags are prohibited unless standardized;
- aliases/anchors, if allowed in authoring, do not create semantic object
  identity;
- timestamps should not depend on implicit YAML timestamp coercion;
- identifiers that look numeric should remain strings where the model requires
  strings.

These constraints prevent two YAML implementations from producing different
SCAP-NG data models from the same file.

## Four-anchor schema-validation plan

If schema creation is approved, the first gate should not be a synthetic unit
fixture alone.

The draft schema should validate:

1. the RHEL 9 converted source;
2. Oracle Linux 9;
3. Windows 11;
4. Windows Server 2025;
5. the exact-shared Assessment catalog;
6. Manual and automated selector alternatives;
7. Platform/applicability Assessments;
8. CPE product-inventory outputs;
9. representative Parameters/Organizational Inputs;
10. representative result fixtures.

The schema effort should produce two reports:

### Structural coverage report

For each source field encountered in the four anchors:

- defined by current draft schema;
- intentionally extension/provenance data;
- provisional Assessment-language field;
- unsupported/unmodeled.

### Semantic-validation responsibility report

For each normative requirement:

- enforceable by JSON Schema;
- enforceable only by SCAP-NG semantic validation;
- runtime-only requirement;
- migration/conformance requirement.

This prevents normative requirements from disappearing merely because JSON
Schema cannot express them.

## Questions to place before the OVAL Board

A schema review package should make the unresolved automated-Assessment areas
easy to identify.

Suggested Board questions include:

1. Is the proposed capability/object/state/evaluation separation capable of
   preserving complete OVAL semantics?
2. Which OVAL defaults should NG make mandatory and explicit?
3. Which cardinality/existence semantics must remain independent?
4. What variable/component constructs are essential for lossless conversion?
5. Which object-set/filter semantics are commonly missed by replacement
   formats?
6. Should OVAL family/test names remain the stable capability taxonomy?
7. How should historical numbered test types be represented?
8. Which datatype/operation semantics need exact compatibility constraints?
9. Is the proposed Platform Assessment + descriptive CPE inventory-output model
   compatible with expected future OVAL/CPE direction?
10. What conformance fixtures would the Board regard as essential before
    claiming OVAL-semantic coverage?

## Suggested work sequence after project-owner approval

If schema creation is authorized after review of the new iteration-002 content:

1. create an explicitly experimental `schema/0.1-pre-alpha/` tree;
2. implement common identity/reference/extension primitives;
3. schema Benchmark and Rule policy;
4. schema Profile, Tailoring, Parameters, and applicability;
5. schema Manual Assessment;
6. schema Results and target inventory;
7. add only a provisional generic automated Assessment envelope;
8. add structural validation to CI;
9. validate the four anchors and publish coverage gaps;
10. prepare the automated Assessment/capability questions for OVAL Board
    review;
11. revise automated Assessment schemas after Board feedback;
12. only then consider a schema candidate normative.

## Recommendation

Schema work is now worthwhile as a **design validator**.

The project should not wait until every Assessment-language issue is resolved
before beginning structural schema work, because early schemas will expose
inconsistencies in the policy/result model and four-anchor examples.

At the same time, schema creation should not be mistaken for language freeze.
The automated Assessment language is precisely the area where OVAL Board review
can still materially improve the design.

No schema files should be created until the project owner approves proceeding
after reviewing the current iteration-002 content.
