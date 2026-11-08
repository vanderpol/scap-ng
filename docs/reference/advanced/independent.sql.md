# independent.sql — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/independent.sql.schema.json#) | {} | source-derived-proposal |
| [/$defs/meanings/properties/engine](../../../proposed-schema/documentation/capabilities/independent.sql.schema.json#/$defs/meanings/properties/engine) | {"declared_values_not_new_validation_restrictions": ["access", "aurora", "azuresql", "crunchypostgres", "derby", "db2", "cache", "firebird", "firstsql", "foxpro", "informix", "ingres", "interbase", "lightbase", "mariadb", "maxdb", "monetdb", "mimer", "mysql", "oracle", "paradox", "pervasive", "postgre", "sqlbase", "sqlite", "sqlserver", "sybase"]} | source-meaning-reviewed |

[/$defs/meanings/properties/engine](../../../proposed-schema/documentation/capabilities/independent.sql.schema.json#/$defs/meanings/properties/engine): Database engine.

`engine` identifies the specific database engine used to connect to the database.

`engine` defines the specific database engine to use.

`engine` defines a specific database engine.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/version](../../../proposed-schema/documentation/capabilities/independent.sql.schema.json#/$defs/meanings/properties/version) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/version](../../../proposed-schema/documentation/capabilities/independent.sql.schema.json#/$defs/meanings/properties/version): Database engine version.

`version` identifies the version of the database engine used to connect to the database.

Below are some examples, but make sure to refer to DBMS system documentation for complete/current methods to determine versions

`version` defines the specific version of the database engine to use.

`version` defines a specific version of a given database engine.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/instance](../../../proposed-schema/documentation/capabilities/independent.sql.schema.json#/$defs/meanings/properties/instance) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/instance](../../../proposed-schema/documentation/capabilities/independent.sql.schema.json#/$defs/meanings/properties/instance): Database instance name.

This could be a separate installation of binaries (such as with MS SQL Server), or just a set of running processes used to manage the DBMS.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/database](../../../proposed-schema/documentation/capabilities/independent.sql.schema.json#/$defs/meanings/properties/database) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/database](../../../proposed-schema/documentation/capabilities/independent.sql.schema.json#/$defs/meanings/properties/database): Database or catalog name.

This is primarily useful for queries that gather instance configuration settings, such as SQL Servers SERVERPROPERTY data.

See https://learn.microsoft.com/en-us/sql/t-sql/functions/serverproperty-transact-sql?view=sql-server-ver16 Example:

SELECT SERVERPROPERTY('IsClustered') AS [is_clustered]

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/sql](../../../proposed-schema/documentation/capabilities/independent.sql.schema.json#/$defs/meanings/properties/sql) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/sql](../../../proposed-schema/documentation/capabilities/independent.sql.schema.json#/$defs/meanings/properties/sql): SQL query text.

`sql` holds the specific query used to identify the object(s) in the database.

`sql` defines a query used to identify the object(s) to test against.

However, SELECT * FROM ... is not valid.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/result](../../../proposed-schema/documentation/capabilities/independent.sql.schema.json#/$defs/meanings/properties/result) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/result](../../../proposed-schema/documentation/capabilities/independent.sql.schema.json#/$defs/meanings/properties/result): Values returned by the SQL query.

`result` holds the results of the specified SQL statement.

`result` specifies how to test objects in the result set of the specified SQL statement.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/independent.sql.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |
| [/$defs/object/properties/engine](../../../proposed-schema/documentation/capabilities/independent.sql.schema.json#/$defs/object/properties/engine) | {"declaration_only": {"type": "string", "enum": ["access", "aurora", "azuresql", "crunchypostgres", "derby", "db2", "cache", "firebird", "firstsql", "foxpro", "informix", "ingres", "interbase", "lightbase", "mariadb", "maxdb", "monetdb", "mimer", "mysql", "oracle", "paradox", "pervasive", "postgre", "sqlbase", "sqlite", "sqlserver", "sybase"], "required": true, "allow_variable": true}} | source-meaning-reviewed |
| [/$defs/object/properties/version](../../../proposed-schema/documentation/capabilities/independent.sql.schema.json#/$defs/object/properties/version) | {"declaration_only": {"type": "string", "required": true, "allow_variable": true}} | source-meaning-reviewed |
| [/$defs/object/properties/instance](../../../proposed-schema/documentation/capabilities/independent.sql.schema.json#/$defs/object/properties/instance) | {"declaration_only": {"type": "string", "required": true, "allow_variable": true}} | source-meaning-reviewed |
| [/$defs/object/properties/database](../../../proposed-schema/documentation/capabilities/independent.sql.schema.json#/$defs/object/properties/database) | {"declaration_only": {"type": "string", "required": true, "allow_variable": true}} | source-meaning-reviewed |
| [/$defs/object/properties/sql](../../../proposed-schema/documentation/capabilities/independent.sql.schema.json#/$defs/object/properties/sql) | {"declaration_only": {"type": "string", "required": true, "allow_variable": true}} | source-meaning-reviewed |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/independent.sql.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/independent.sql.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
