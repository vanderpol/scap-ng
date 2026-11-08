# SCAP-NG Benchmark v0.4.0

Proposed documentation. Defaults are schema annotations, not inferred scanner fallbacks. Conditional requirements and alternatives remain linked in the schema.

## `/`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `benchmark` | object | 1..1 (required) | **Unresolved description** | [/properties/benchmark](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark) |

## `/properties/benchmark`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `id` | string | 1..1 (required) | **Unresolved description** | [/properties/benchmark/properties/id](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/id) |
| `ng_schema_version` | null, string | 1..1 (required) | **Unresolved description** | [/properties/benchmark/properties/ng_schema_version](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/ng_schema_version) |
| `use_case` | string | 1..1 (required) | **Unresolved description** | [/properties/benchmark/properties/use_case](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/use_case) |
| `title` | array | 1..1 (required) | **Unresolved description** | [/properties/benchmark/properties/title](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/title) |
| `description` | array | 1..1 (required) | **Unresolved description** | [/properties/benchmark/properties/description](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/description) |
| `language` | null, string | 1..1 (required) | **Unresolved description** | [/properties/benchmark/properties/language](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/language) |
| `status` | array | 1..1 (required) | **Unresolved description** | [/properties/benchmark/properties/status](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/status) |
| `version` | object | 1..1 (required) | **Unresolved description** | [/properties/benchmark/properties/version](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/version) |
| `metadata` | object | 1..1 (required) | **Unresolved description** | [/properties/benchmark/properties/metadata](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/metadata) |
| `notices` | array | 1..1 (required) | **Unresolved description** | [/properties/benchmark/properties/notices](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/notices) |
| `front_matter` | array | 1..1 (required) | **Unresolved description** | [/properties/benchmark/properties/front_matter](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/front_matter) |
| `rear_matter` | array | 1..1 (required) | **Unresolved description** | [/properties/benchmark/properties/rear_matter](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/rear_matter) |
| `references` | array | 1..1 (required) | **Unresolved description** | [/properties/benchmark/properties/references](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/references) |
| `text_blocks` | array | 1..1 (required) | **Unresolved description** | [/properties/benchmark/properties/text_blocks](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/text_blocks) |
| `platform` | object | 1..1 (required) | **Unresolved description** | [/properties/benchmark/properties/platform](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/platform) |
| `applicability_catalog` | string | 1..1 (required) | **Unresolved description** | [/properties/benchmark/properties/applicability_catalog](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/applicability_catalog) |
| `scoring` | array | 1..1 (required) | **Unresolved description** | [/properties/benchmark/properties/scoring](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/scoring) |
| `parameters` | array | 1..1 (required) | **Unresolved description** | [/properties/benchmark/properties/parameters](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/parameters) |
| `default_selection` | boolean | 1..1 (required) | **Unresolved description** | [/properties/benchmark/properties/default_selection](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/default_selection) |
| `groups` | array | 1..1 (required) | **Unresolved description** | [/properties/benchmark/properties/groups](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/groups) |
| `profiles` | array | 1..1 (required) | **Unresolved description** | [/properties/benchmark/properties/profiles](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/profiles) |
| `rules` | array | 1..1 (required) | **Unresolved description** | [/properties/benchmark/properties/rules](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/rules) |
| `assessment_specifications` | array | 1..1 (required) | External automated assessment specifications required by Assessments referenced from this Benchmark. | [/properties/benchmark/properties/assessment_specifications](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/assessment_specifications) |

## `/properties/benchmark/properties/title/items`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `text` | string | 1..1 (required) | **Unresolved description** | [/properties/benchmark/properties/title/items/properties/text](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/title/items/properties/text) |
| `language` | null, string | 1..1 (required) | **Unresolved description** | [/properties/benchmark/properties/title/items/properties/language](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/title/items/properties/language) |

## `/properties/benchmark/properties/description/items`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `text` | string | 1..1 (required) | **Unresolved description** | [/properties/benchmark/properties/description/items/properties/text](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/description/items/properties/text) |
| `language` | null, string | 1..1 (required) | **Unresolved description** | [/properties/benchmark/properties/description/items/properties/language](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/description/items/properties/language) |

## `/properties/benchmark/properties/front_matter/items`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `text` | string | 1..1 (required) | **Unresolved description** | [/properties/benchmark/properties/front_matter/items/properties/text](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/front_matter/items/properties/text) |
| `language` | null, string | 1..1 (required) | **Unresolved description** | [/properties/benchmark/properties/front_matter/items/properties/language](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/front_matter/items/properties/language) |

## `/properties/benchmark/properties/rear_matter/items`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `text` | string | 1..1 (required) | **Unresolved description** | [/properties/benchmark/properties/rear_matter/items/properties/text](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/rear_matter/items/properties/text) |
| `language` | null, string | 1..1 (required) | **Unresolved description** | [/properties/benchmark/properties/rear_matter/items/properties/language](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/rear_matter/items/properties/language) |

## `/properties/benchmark/properties/platform`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `id` | string | 1..1 (required) | **Unresolved description** | [/properties/benchmark/properties/platform/properties/id](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/platform/properties/id) |
| `title` | string | 1..1 (required) | **Unresolved description** | [/properties/benchmark/properties/platform/properties/title](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/platform/properties/title) |
| `applicability` | object | 1..1 (required) | **Unresolved description** | [/properties/benchmark/properties/platform/properties/applicability](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/platform/properties/applicability) |

## `/properties/benchmark/properties/profiles/items`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `id` | string | 1..1 (required) | **Unresolved description** | [/properties/benchmark/properties/profiles/items/properties/id](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/profiles/items/properties/id) |
| `title` | null, string | 0..1 | **Unresolved description** | [/properties/benchmark/properties/profiles/items/properties/title](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/profiles/items/properties/title) |
| `description` | null, string | 0..1 | **Unresolved description** | [/properties/benchmark/properties/profiles/items/properties/description](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/profiles/items/properties/description) |
| `extends` | string | 0..1 | **Unresolved description** | [/properties/benchmark/properties/profiles/items/properties/extends](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/profiles/items/properties/extends) |
| `disabled_rules` | array | 1..1 (required) | **Unresolved description** | [/properties/benchmark/properties/profiles/items/properties/disabled_rules](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/profiles/items/properties/disabled_rules) |
| `parameters` | object | 0..1 | **Unresolved description** | [/properties/benchmark/properties/profiles/items/properties/parameters](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/profiles/items/properties/parameters) |

## `/properties/benchmark/properties/assessment_specifications/items`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `id` | string | 1..1 (required) | **Unresolved description** | [/properties/benchmark/properties/assessment_specifications/items/properties/id](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/assessment_specifications/items/properties/id) |
| `version` | string | 1..1 (required) | **Unresolved description** | [/properties/benchmark/properties/assessment_specifications/items/properties/version](../../../proposed-schema/documentation/benchmark.schema.json#/properties/benchmark/properties/assessment_specifications/items/properties/version) |

## Advanced constraints

[Local constraints](../advanced/benchmark.md) and [complete JSON Schema](../../../proposed-schema/documentation/benchmark.schema.json) contain conditional requirements, alternatives, bounds and validation expressions. A mapping property occurs at most once; `items`, `minItems` and `maxItems` constrain array members separately. A definition is reusable schema grammar, not itself an authored mapping key.
