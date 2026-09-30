# OVAL XSD documentation → SCAP-NG JSON Schema → published assessor reference

**Status:** iteration-002 design proposal; not an approved normative specification.
**Scope:** automated assessment capabilities and their author-facing documentation.

## Proposed direction

For *native SCAP-NG assessment syntax*, a versioned JSON Schema should eventually be the canonical **machine-readable source for field-level documentation** and validation. A documentation generator should produce the assessment field reference from those schemas. Separate specification prose remains authoritative for operational algorithms and semantics that JSON Schema validation cannot express.

Do **not** directly transform OVAL XSD into normative SCAP-NG schema. The OVAL XSD is historical evidence; migration requires examination of the corresponding OVAL documentation, schema defaults, normative definitions, and observed evaluation behavior. Model the effective behavior explicitly in NG and record intentional differences.

## Authoring contract

- Use JSON Schema 2020-12 or a deliberately selected, pinned future dialect, with `$id`, `$schema`, `$defs`, `$ref`, `title`, `description`, `default`, `examples`, and `deprecated` where appropriate.
- `description` is human-readable prose and `$comment` is non-normative maintainer commentary. Neither is a reliable machine-executable assertion of OVAL evaluation behavior.
- JSON Schema `default` is an annotation: it **does not make validators insert missing values**. NG processors shall not depend on validators materializing a default.
- SCAP-NG source SHOULD serialize all behavior-affecting evaluation parameters explicitly. During migration the converter resolves an *absent* legacy attribute to its effective OVAL value and emits that value explicitly.
- For structured semantics requiring more than prose, define a separate SCAP-NG-owned, versioned annotation vocabulary (for example `x-scap-ng-semantics`) **only after** defining its schema, consumers, and tests. Do not assume arbitrary `x-` keys are validated by generic JSON Schema validators.
- Retain OVAL origin references in documentation/migration metadata, **not as required native runtime inputs**.
- Maintain an authoritative semantic registry for rules that cannot be adequately defined by schema properties alone: evaluation truth tables, item/variable quantification, error/unknown propagation, collector-specific algorithms, and platform behavior. Link registry entries to JSON Schema `$id`/JSON Pointers.
- Generated published reference pages SHALL visibly identify the specification/schema version and normative status. Generated pages MUST NOT silently override the manually reviewed normative semantics.

## Suggested metadata for each assessment capability

| Field | Purpose |
| --- | --- |
| Stable NG capability ID | e.g. `unix.file`; naming versions remain a governance decision |
| Title and summary | Concise content-author guidance |
| Property definitions and constraints | JSON Schema validators can check these |
| Fully explicit effective semantics | Existence, quantifiers, operations, collection behaviors |
| Defaults and omissions | Legacy default, native policy, and effect on migration, distinguished |
| Examples | Pass, fail, absent, multiple matches, unknown, and error |
| Results and evidence | Expected message and evidence shape, including caps |
| Source crosswalk | OVAL 5.12.3 schema/type/element + documentation provenance |
| Known source flaws | Ambiguous wording, surprising defaults, issues, resolutions |
| Conformance tests | Positive, negative, omission/default, and round-trip fixtures |

## Illustration (design sketch; NOT an adopted schema)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.invalid/scap-ng/assessment/common/test-options.schema.json",
  "title": "Assessment test options",
  "type": "object",
  "properties": {
    "check_existence": {
      "type": "string",
      "description": "Explicit required cardinality/existence semantics for collected items. See linked normative truth table.",
      "examples": ["at_least_one_exists"],
      "$comment": "The legacy omitted-attribute default must be resolved before emitting native NG."
    }
  },
  "required": ["check_existence"]
}
```

The final NG authoring names and values remain open: the sketch illustrates traceable documentation, **not** a decision to retain OVAL XML names.

## Extract/import workflow

1. Pin the exact SCAP 1.4/OVAL 5.12.3 schema revision and the related authoritative documentation; record SHA256 hashes.
2. Inventory every XSD `documentation`, `default`, `fixed`, optional/required attribute, enumeration, restriction, substitution group, inheritance, and wildcard. Identify what is specified outside the XSD.
3. Record each source item as `verified`, `ambiguous`, `source defect`, or `unsupported/deprecated`. Deprecated OVAL tests remain prohibited in NG, with conversion errors.
4. Resolve effective defaults (`check`, `check_existence`, `entity_check`, `var_check`, object behaviors, state/existence semantics, etc.) **by actual declaration and element context**, never by a global assumption.
5. Map verified semantics to NG capability definitions and migration crosswalks; write independently reviewable author-facing summaries instead of wholesale XSD text dumps.
6. Generate draft JSON Schemas and derived documentation, then compare the generated pages against the inventory for coverage, including exceptions.
7. Add fixture pairs that omit and explicitly specify each legacy default; verify equal semantics at Stage 1, and verify explicit NG output.
8. Gate publication on schema validation, link checks, coverage checks, semantic fixture tests, and reviewer approval.

## Specification boundary

**Schema-derived reference:** field names, types, mandatory/optional fields, enumerations, constraints, syntax examples, links, and concise descriptions.

**Normative prose / semantic registry:** collection procedures, Boolean and multi-valued logic, error and unknown propagation, result cardinality, `var_check` and entity quantification, variable resolution, evidence limits, portability, and security model.

Aim for **one maintained explanation per behavior**, with cross-links and generated presentation surfaces, rather than competing human-written copies.

## Immediate follow-up

- Continue the ongoing exhaustive OVAL XSD default/constraint audit.
- Produce a traceability table from each relevant OVAL declaration to an NG semantic requirement, generated schema property, reference page, and conformance test.
- Pilot with common Test/Object/State behaviors and two contrasting collector families before scaling to the full OVAL family catalog.
- Promote this proposal into `specification/` only after completeness and conversion semantics have been reviewed.
