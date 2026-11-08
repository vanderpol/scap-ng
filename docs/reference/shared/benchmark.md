# SCAP-NG Benchmark v0.4.0

Proposed documentation. Defaults are schema annotations, not inferred scanner fallbacks. Conditional requirements and alternatives remain linked in the schema.

## `/`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `benchmark` | object | 1..1 (required) | **Unresolved description** | [/properties/benchmark](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark) |

## `/properties/benchmark`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `id` | string | 1..1 (required) | Benchmark identifier. | [/properties/benchmark/properties/id](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/id) |
| `ng_schema_version` | null, string | 1..1 (required) | SCAP-NG schema version label recorded for this Benchmark. | [/properties/benchmark/properties/ng_schema_version](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/ng_schema_version) |
| `use_case` | string | 1..1 (required) | Intended use declared for the Benchmark. | [/properties/benchmark/properties/use_case](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/use_case) |
| `title` | array | 1..1 (required) | Benchmark titles with their language labels. | [/properties/benchmark/properties/title](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/title) |
| `description` | array | 1..1 (required) | Descriptions of the Benchmark content with their language labels. | [/properties/benchmark/properties/description](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/description) |
| `language` | null, string | 1..1 (required) | Language label associated with the Benchmark text. | [/properties/benchmark/properties/language](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/language) |
| `status` | array | 1..1 (required) | Status declarations associated with the Benchmark. | [/properties/benchmark/properties/status](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/status) |
| `version` | object | 1..1 (required) | Version information recorded for this Benchmark. | [/properties/benchmark/properties/version](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/version) |
| `metadata` | object | 1..1 (required) | Additional descriptive metadata about the Benchmark. | [/properties/benchmark/properties/metadata](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/metadata) |
| `notices` | array | 1..1 (required) | Notices accompanying the Benchmark content. | [/properties/benchmark/properties/notices](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/notices) |
| `front_matter` | array | 1..1 (required) | Introductory text for the Benchmark. | [/properties/benchmark/properties/front_matter](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/front_matter) |
| `rear_matter` | array | 1..1 (required) | Closing text for the Benchmark. | [/properties/benchmark/properties/rear_matter](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/rear_matter) |
| `references` | array | 1..1 (required) | External references supporting the Benchmark. | [/properties/benchmark/properties/references](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/references) |
| `text_blocks` | array | 1..1 (required) | Reusable text blocks carried by the Benchmark. | [/properties/benchmark/properties/text_blocks](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/text_blocks) |
| `platform` | object | 1..1 (required) | Platform metadata and applicability information for the Benchmark. | [/properties/benchmark/properties/platform](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/platform) |
| `applicability_catalog` | string | 1..1 (required) | Reference to the applicability catalog used by the Benchmark. | [/properties/benchmark/properties/applicability_catalog](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/applicability_catalog) |
| `scoring` | array | 1..1 (required) | Scoring declarations; calculation and rollup policy require a native contract. | [/properties/benchmark/properties/scoring](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/scoring) |
| `parameters` | array | 1..1 (required) | Parameter declarations carried by the Benchmark. | [/properties/benchmark/properties/parameters](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/parameters) |
| `default_selection` | boolean | 1..1 (required) | Default Rule-selection flag declared by the Benchmark. | [/properties/benchmark/properties/default_selection](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/default_selection) |
| `groups` | array | 1..1 (required) | Group declarations organizing the Benchmark content. | [/properties/benchmark/properties/groups](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/groups) |
| `profiles` | array | 1..1 (required) | Named profile declarations for the Benchmark. | [/properties/benchmark/properties/profiles](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/profiles) |
| `rules` | array | 1..1 (required) | Rule declarations contained in the Benchmark. | [/properties/benchmark/properties/rules](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/rules) |
| `assessment_specifications` | array | 1..1 (required) | External automated assessment specifications required by Assessments referenced from this Benchmark. | [/properties/benchmark/properties/assessment_specifications](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/assessment_specifications) |

## `/properties/benchmark/properties/title/items`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `text` | string | 1..1 (required) | Text of this title. | [/properties/benchmark/properties/title/items/properties/text](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/title/items/properties/text) |
| `language` | null, string | 1..1 (required) | Language label for this title. | [/properties/benchmark/properties/title/items/properties/language](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/title/items/properties/language) |

## `/properties/benchmark/properties/description/items`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `text` | string | 1..1 (required) | Text of this description. | [/properties/benchmark/properties/description/items/properties/text](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/description/items/properties/text) |
| `language` | null, string | 1..1 (required) | Language label for this description. | [/properties/benchmark/properties/description/items/properties/language](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/description/items/properties/language) |

## `/properties/benchmark/properties/front_matter/items`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `text` | string | 1..1 (required) | Text of this introductory text. | [/properties/benchmark/properties/front_matter/items/properties/text](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/front_matter/items/properties/text) |
| `language` | null, string | 1..1 (required) | Language label for this introductory text. | [/properties/benchmark/properties/front_matter/items/properties/language](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/front_matter/items/properties/language) |

## `/properties/benchmark/properties/rear_matter/items`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `text` | string | 1..1 (required) | Text of this closing text. | [/properties/benchmark/properties/rear_matter/items/properties/text](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/rear_matter/items/properties/text) |
| `language` | null, string | 1..1 (required) | Language label for this closing text. | [/properties/benchmark/properties/rear_matter/items/properties/language](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/rear_matter/items/properties/language) |

## `/properties/benchmark/properties/platform`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `id` | string | 1..1 (required) | Identifier of the declared platform. | [/properties/benchmark/properties/platform/properties/id](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/platform/properties/id) |
| `title` | string | 1..1 (required) | Human-readable title of the declared platform. | [/properties/benchmark/properties/platform/properties/title](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/platform/properties/title) |
| `applicability` | object | 1..1 (required) | Applicability information associated with the declared platform. | [/properties/benchmark/properties/platform/properties/applicability](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/platform/properties/applicability) |

## `/properties/benchmark/properties/profiles/items`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `id` | string | 1..1 (required) | Profile identifier. | [/properties/benchmark/properties/profiles/items/properties/id](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/profiles/items/properties/id) |
| `title` | null, string | 0..1 | Human-readable profile title. | [/properties/benchmark/properties/profiles/items/properties/title](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/profiles/items/properties/title) |
| `description` | null, string | 0..1 | Description of the profile. | [/properties/benchmark/properties/profiles/items/properties/description](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/profiles/items/properties/description) |
| `extends` | string | 0..1 | Names the base profile referenced by this profile. | [/properties/benchmark/properties/profiles/items/properties/extends](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/profiles/items/properties/extends) |
| `disabled_rules` | array | 1..1 (required) | Rule identifiers declared disabled by this profile. | [/properties/benchmark/properties/profiles/items/properties/disabled_rules](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/profiles/items/properties/disabled_rules) |
| `parameters` | object | 0..1 | Parameter values declared by this profile. | [/properties/benchmark/properties/profiles/items/properties/parameters](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/profiles/items/properties/parameters) |

## `/properties/benchmark/properties/assessment_specifications/items`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `id` | string | 1..1 (required) | Identifier of the referenced Assessment specification. | [/properties/benchmark/properties/assessment_specifications/items/properties/id](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/assessment_specifications/items/properties/id) |
| `version` | string | 1..1 (required) | Version of the referenced Assessment specification. | [/properties/benchmark/properties/assessment_specifications/items/properties/version](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/assessment_specifications/items/properties/version) |

## Advanced constraints

[Local constraints](../advanced/benchmark.md) and [complete JSON Schema](../../../proposed-schema/documentation/benchmark.schema.json) contain conditional requirements, alternatives, bounds and validation expressions. A mapping property occurs at most once; `items`, `minItems` and `maxItems` constrain array members separately. A definition is reusable schema grammar, not itself an authored mapping key.
