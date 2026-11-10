# independent.textfilecontent

Proposed documentation; frozen 0.4.0 validation is unchanged.

The `independent.textfilecontent` element is used to check the contents of a text file (aka a configuration file) by looking at individual blocks of text.

**Contract status: unresolved.** Encoding, match ordering, duplicate captures, missing files and read failures require native runtime evidence.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/independent.textfilecontent.md) retain the validated encodings and any broader schema acceptance.

## Object

The set of files to be evaluated may be identified with either a complete filepath or a path and filename.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/independent.textfilecontent.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/independent.textfilecontent.schema.json#/$defs/object/properties/filters) |
| `full_path` | string | 0..1 | Full path of the text file. | [/$defs/object/properties/full_path](../../../proposed-schema/documentation/capabilities/independent.textfilecontent.schema.json#/$defs/object/properties/full_path) |
| `directory` | string | 0..1 | Directory component of the file path. | [/$defs/object/properties/directory](../../../proposed-schema/documentation/capabilities/independent.textfilecontent.schema.json#/$defs/object/properties/directory) |
| `name` | string | 0..1 | File name without the directory. | [/$defs/object/properties/name](../../../proposed-schema/documentation/capabilities/independent.textfilecontent.schema.json#/$defs/object/properties/name) |
| `pattern` | string | 0..1 | Regular expression used to extract matching text. | [/$defs/object/properties/pattern](../../../proposed-schema/documentation/capabilities/independent.textfilecontent.schema.json#/$defs/object/properties/pattern) |
| `instance` | integer | 0..1 | Ordinal occurrence of a pattern match. | [/$defs/object/properties/instance](../../../proposed-schema/documentation/capabilities/independent.textfilecontent.schema.json#/$defs/object/properties/instance) |
| `ignore_case` | boolean | 0..1 | Case-insensitive pattern matching control. | [/$defs/object/properties/ignore_case](../../../proposed-schema/documentation/capabilities/independent.textfilecontent.schema.json#/$defs/object/properties/ignore_case) |
| `multiline` | boolean | 0..1 | Control for line-anchor matching within the input. | [/$defs/object/properties/multiline](../../../proposed-schema/documentation/capabilities/independent.textfilecontent.schema.json#/$defs/object/properties/multiline) |
| `singleline` | boolean | 0..1 | Control for whether a dot matches newline characters. | [/$defs/object/properties/singleline](../../../proposed-schema/documentation/capabilities/independent.textfilecontent.schema.json#/$defs/object/properties/singleline) |
| `item_creation` | string | 0..1 | Item creation mode for matching text. | [/$defs/object/properties/item_creation](../../../proposed-schema/documentation/capabilities/independent.textfilecontent.schema.json#/$defs/object/properties/item_creation) |
| `traversal` | object | 0..1 | Controls recursive searching through directories and symbolic links. | [/$defs/object/properties/traversal](../../../proposed-schema/documentation/capabilities/independent.textfilecontent.schema.json#/$defs/object/properties/traversal) |

### traversal

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `max_depth` | integer, string | 1..1 (required) | Maximum downward recursion depth; 0 includes only the starting directory. | [/$defs/file_traversal_base/properties/max_depth](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/file_traversal_base/properties/max_depth) |
| `recurse` | string | 1..1 (required) | Entry types to follow during recursion. | [/$defs/file_traversal/allOf/1/properties/recurse](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/file_traversal/allOf/1/properties/recurse) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

The Item looks at the contents of a text file (aka a configuration file) by looking at individual lines.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `full_path` | string | 0..1 | Full path of the text file. | [/$defs/meanings/properties/full_path](../../../proposed-schema/documentation/capabilities/independent.textfilecontent.schema.json#/$defs/meanings/properties/full_path) |
| `directory` | string | 0..1 | Directory component of the file path. | [/$defs/meanings/properties/directory](../../../proposed-schema/documentation/capabilities/independent.textfilecontent.schema.json#/$defs/meanings/properties/directory) |
| `name` | string | 0..1 | File name without the directory. | [/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/independent.textfilecontent.schema.json#/$defs/meanings/properties/name) |
| `pattern` | string | 0..1 | Regular expression used to extract matching text. | [/$defs/meanings/properties/pattern](../../../proposed-schema/documentation/capabilities/independent.textfilecontent.schema.json#/$defs/meanings/properties/pattern) |
| `instance` | integer | 0..1 | Ordinal occurrence of a pattern match. | [/$defs/meanings/properties/instance](../../../proposed-schema/documentation/capabilities/independent.textfilecontent.schema.json#/$defs/meanings/properties/instance) |
| `text` | 12 declared types; see details | 0..1 | Text matched by the pattern. | [/$defs/meanings/properties/text](../../../proposed-schema/documentation/capabilities/independent.textfilecontent.schema.json#/$defs/meanings/properties/text) |
| `subexpression` | 12 declared types; see details | 0..1 | Text captured by a parenthesized group in the pattern. | [/$defs/meanings/properties/subexpression](../../../proposed-schema/documentation/capabilities/independent.textfilecontent.schema.json#/$defs/meanings/properties/subexpression) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

The comparison fields contain entities that are used to check the file path and name, as well as the text block in question and the value of the subexpressions.

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/independent.textfilecontent.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |
| Object.`ignore_case` | {"required": true, "type": "boolean"} | source-meaning-reviewed |
| Object.`multiline` | {"required": true, "type": "boolean"} | source-meaning-reviewed |
| Object.`singleline` | {"required": true, "type": "boolean"} | source-meaning-reviewed |
| Object.`item_creation` | {"enum": ["all_object_elements_fullfilled", "filepath_exists"], "required": true, "type": "string"} | source-meaning-reviewed |
| Item.`text` | string, boolean, integer, float, binary, version, ipv4, ipv6, rpm_evr, debian_evr, fileset_revision, ios_version | native-mapping-reviewed |
| Item.`subexpression` | string, boolean, integer, float, binary, version, ipv4, ipv6, rpm_evr, debian_evr, fileset_revision, ios_version | native-mapping-reviewed |

See the [schema](../../../proposed-schema/documentation/capabilities/independent.textfilecontent.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `independent-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
