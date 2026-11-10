# independent.sql

Proposed documentation; frozen 0.4.0 validation is unchanged.

The sql512 test is used to check information stored in a database.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/independent.sql.md) retain the validated encodings and any broader schema acceptance.

## Object

The Object is used by a sql512 test to define the specific database and query to be evaluated.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/independent.sql.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/independent.sql.schema.json#/$defs/object/properties/filters) |
| `engine` | string | 0..1 | Database engine. | [/$defs/object/properties/engine](../../../proposed-schema/documentation/capabilities/independent.sql.schema.json#/$defs/object/properties/engine) |
| `version` | string | 0..1 | Database engine version. | [/$defs/object/properties/version](../../../proposed-schema/documentation/capabilities/independent.sql.schema.json#/$defs/object/properties/version) |
| `instance` | string | 0..1 | Database instance name. | [/$defs/object/properties/instance](../../../proposed-schema/documentation/capabilities/independent.sql.schema.json#/$defs/object/properties/instance) |
| `database` | string | 0..1 | Database or catalog name. | [/$defs/object/properties/database](../../../proposed-schema/documentation/capabilities/independent.sql.schema.json#/$defs/object/properties/database) |
| `sql` | string | 0..1 | SQL query text. | [/$defs/object/properties/sql](../../../proposed-schema/documentation/capabilities/independent.sql.schema.json#/$defs/object/properties/sql) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

The Item outlines information collected from a database via an SQL query.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `engine` | string | 0..1 | Database engine. | [/$defs/meanings/properties/engine](../../../proposed-schema/documentation/capabilities/independent.sql.schema.json#/$defs/meanings/properties/engine) |
| `version` | string | 0..1 | Database engine version. | [/$defs/meanings/properties/version](../../../proposed-schema/documentation/capabilities/independent.sql.schema.json#/$defs/meanings/properties/version) |
| `instance` | string | 0..1 | Database instance name. | [/$defs/meanings/properties/instance](../../../proposed-schema/documentation/capabilities/independent.sql.schema.json#/$defs/meanings/properties/instance) |
| `database` | string | 0..1 | Database or catalog name. | [/$defs/meanings/properties/database](../../../proposed-schema/documentation/capabilities/independent.sql.schema.json#/$defs/meanings/properties/database) |
| `sql` | string | 0..1 | SQL query text. | [/$defs/meanings/properties/sql](../../../proposed-schema/documentation/capabilities/independent.sql.schema.json#/$defs/meanings/properties/sql) |
| `result` | record | 0..1 | Values returned by the SQL query. | [/$defs/meanings/properties/result](../../../proposed-schema/documentation/capabilities/independent.sql.schema.json#/$defs/meanings/properties/result) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

The comparison fields contain two entities that are used to check the name of the specified field and the value associated with it.

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


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

See the [schema](../../../proposed-schema/documentation/capabilities/independent.sql.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `independent-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
