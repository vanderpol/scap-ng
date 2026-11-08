# independent.sql

Proposed documentation; frozen 0.4.0 validation is unchanged.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Field meanings below are documentation proposals derived from the pinned sources. Reviewed wording and unresolved entries are identified in the [coverage ledger](../coverage.json) and schema annotations.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Object tables describe inline forms; named Object references and Set composition use the [shared collection grammar](../shared/capability-common.md). Item fields use the shared [typed-value wrapper](../shared/result-types.md); a field may contain one wrapper or an array. Capability-specific units, multiplicity and error behavior require evidence.

## Object

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/independent.sql.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/independent.sql.schema.json#/$defs/object/properties/filters) |
| `engine` | See schema | 0..1 | Database engine. | [/$defs/object/properties/engine](../../../proposed-schema/documentation/capabilities/independent.sql.schema.json#/$defs/object/properties/engine) |
| `version` | See schema | 0..1 | Database engine version. | [/$defs/object/properties/version](../../../proposed-schema/documentation/capabilities/independent.sql.schema.json#/$defs/object/properties/version) |
| `instance` | See schema | 0..1 | Database instance name. | [/$defs/object/properties/instance](../../../proposed-schema/documentation/capabilities/independent.sql.schema.json#/$defs/object/properties/instance) |
| `database` | See schema | 0..1 | Database or catalog name. | [/$defs/object/properties/database](../../../proposed-schema/documentation/capabilities/independent.sql.schema.json#/$defs/object/properties/database) |
| `sql` | See schema | 0..1 | SQL query text. | [/$defs/object/properties/sql](../../../proposed-schema/documentation/capabilities/independent.sql.schema.json#/$defs/object/properties/sql) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `engine` | array, object | 0..1 | Database engine. | [/$defs/meanings/properties/engine](../../../proposed-schema/documentation/capabilities/independent.sql.schema.json#/$defs/meanings/properties/engine) |
| `version` | array, object | 0..1 | Database engine version. | [/$defs/meanings/properties/version](../../../proposed-schema/documentation/capabilities/independent.sql.schema.json#/$defs/meanings/properties/version) |
| `instance` | array, object | 0..1 | Database instance name. | [/$defs/meanings/properties/instance](../../../proposed-schema/documentation/capabilities/independent.sql.schema.json#/$defs/meanings/properties/instance) |
| `database` | array, object | 0..1 | Database or catalog name. | [/$defs/meanings/properties/database](../../../proposed-schema/documentation/capabilities/independent.sql.schema.json#/$defs/meanings/properties/database) |
| `sql` | array, object | 0..1 | SQL query text. | [/$defs/meanings/properties/sql](../../../proposed-schema/documentation/capabilities/independent.sql.schema.json#/$defs/meanings/properties/sql) |
| `result` | array, object | 0..1 | Values returned by the SQL query. | [/$defs/meanings/properties/result](../../../proposed-schema/documentation/capabilities/independent.sql.schema.json#/$defs/meanings/properties/result) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

Field meanings are shared with Item; comparisons use the [native Require grammar](../shared/assessment-language.md). This is a field vocabulary, not a whitelist or a promise that every field is collected.

### Condition logic

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `item_requirement` | object | 1..1 (required) | Sets how many Items must be found and how many must satisfy the comparison. | [/$defs/canonical_all_items_requirement/properties/item_requirement](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/item_requirement) |
| `field_requirement` | object | 1..1 (required) | Sets the shared value-count requirements for fields in this comparison. | [/$defs/canonical_all_items_requirement/properties/field_requirement](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/field_requirement) |
| `fields` | object | Conditional (at most 1) | Requires all listed field conditions to hold for an Item. | [/$defs/canonical_all_items_requirement/properties/fields](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/fields) |
| `and` | array | Conditional (at most 1) | Groups child conditions using logical AND. | [/$defs/canonical_all_items_requirement/properties/and](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/and) |
| `or` | array | Conditional (at most 1) | Groups child conditions using logical OR. | [/$defs/canonical_all_items_requirement/properties/or](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/or) |
| `one` | array | Conditional (at most 1) | **Unresolved description** | [/$defs/canonical_all_items_requirement/properties/one](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/one) |
| `xor` | array | Conditional (at most 1) | **Unresolved description** | [/$defs/canonical_all_items_requirement/properties/xor](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/xor) |

### Item existence requirement

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `item_requirement` | object | 1..1 (required) | Existence only; there is no satisfaction operation without a comparison. | [/$defs/item_presence_requirement/properties/item_requirement](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/item_presence_requirement/properties/item_requirement) |


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/independent.sql.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |
| Object.`engine` | {"allow_variable": true, "enum": ["access", "aurora", "azuresql", "crunchypostgres", "derby", "db2", "cache", "firebird", "firstsql", "foxpro", "informix", "ingres", "interbase", "lightbase", "mariadb", "maxdb", "monetdb", "mimer", "mysql", "oracle", "paradox", "pervasive", "postgre", "sqlbase", "sqlite", "sqlserver", "sybase"], "required": true, "type": "string"} | source-meaning-reviewed |
| Object.`version` | {"allow_variable": true, "required": true, "type": "string"} | source-meaning-reviewed |
| Object.`instance` | {"allow_variable": true, "required": true, "type": "string"} | source-meaning-reviewed |
| Object.`database` | {"allow_variable": true, "required": true, "type": "string"} | source-meaning-reviewed |
| Object.`sql` | {"allow_variable": true, "required": true, "type": "string"} | source-meaning-reviewed |
| Item.`engine` | string | source-meaning-reviewed |
| Item.`version` | string | source-meaning-reviewed |
| Item.`instance` | string | source-meaning-reviewed |
| Item.`database` | string | source-meaning-reviewed |
| Item.`sql` | string | source-meaning-reviewed |
| Item.`result` | record | source-meaning-reviewed |

See the [schema](../../../proposed-schema/documentation/capabilities/independent.sql.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `independent-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
