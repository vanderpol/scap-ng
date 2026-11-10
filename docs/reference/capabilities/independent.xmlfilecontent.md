# independent.xmlfilecontent

Proposed documentation; frozen 0.4.0 validation is unchanged.

The `independent.xmlfilecontent` element is used to explore the contents of an xml file.

This test allows specific pieces of an xml document specified using xpath to be tested.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/independent.xmlfilecontent.md) retain the validated encodings and any broader schema acceptance.

## Object

The set of files to be evaluated may be identified with either a complete filepath or a path and filename.

The Object is used by a xml file content test to define the specific piece of an xml file(s) to be evaluated.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/independent.xmlfilecontent.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/independent.xmlfilecontent.schema.json#/$defs/object/properties/filters) |
| `full_path` | string | 0..1 | Absolute path for a file on the machine. | [/$defs/object/properties/full_path](../../../proposed-schema/documentation/capabilities/independent.xmlfilecontent.schema.json#/$defs/object/properties/full_path) |
| `directory` | string | 0..1 | Directory component of the absolute path to a file on the machine. | [/$defs/object/properties/directory](../../../proposed-schema/documentation/capabilities/independent.xmlfilecontent.schema.json#/$defs/object/properties/directory) |
| `name` | string | 0..1 | Name of the file. | [/$defs/object/properties/name](../../../proposed-schema/documentation/capabilities/independent.xmlfilecontent.schema.json#/$defs/object/properties/name) |
| `xpath` | string | 0..1 | XPath expression selecting values from the XML document. | [/$defs/object/properties/xpath](../../../proposed-schema/documentation/capabilities/independent.xmlfilecontent.schema.json#/$defs/object/properties/xpath) |
| `item_creation` | string | 0..1 | Controls XML item creation. | [/$defs/object/properties/item_creation](../../../proposed-schema/documentation/capabilities/independent.xmlfilecontent.schema.json#/$defs/object/properties/item_creation) |
| `traversal` | object | 0..1 | Controls recursive searching through directories and symbolic links. | [/$defs/object/properties/traversal](../../../proposed-schema/documentation/capabilities/independent.xmlfilecontent.schema.json#/$defs/object/properties/traversal) |

### traversal

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `max_depth` | integer, string | 1..1 (required) | Maximum downward recursion depth; 0 includes only the starting directory. | [/$defs/file_traversal_base/properties/max_depth](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/file_traversal_base/properties/max_depth) |
| `recurse` | string | 1..1 (required) | Entry types to follow during recursion. | [/$defs/file_traversal/allOf/1/properties/recurse](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/file_traversal/allOf/1/properties/recurse) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

This item stores results from checking the contents of an xml file.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `full_path` | string | 0..1 | Absolute path for a file on the machine. | [/$defs/meanings/properties/full_path](../../../proposed-schema/documentation/capabilities/independent.xmlfilecontent.schema.json#/$defs/meanings/properties/full_path) |
| `directory` | string | 0..1 | Directory component of the absolute path to a file on the machine. | [/$defs/meanings/properties/directory](../../../proposed-schema/documentation/capabilities/independent.xmlfilecontent.schema.json#/$defs/meanings/properties/directory) |
| `name` | string | 0..1 | Name of the file. | [/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/independent.xmlfilecontent.schema.json#/$defs/meanings/properties/name) |
| `xpath` | string | 0..1 | XPath expression selecting values from the XML document. | [/$defs/meanings/properties/xpath](../../../proposed-schema/documentation/capabilities/independent.xmlfilecontent.schema.json#/$defs/meanings/properties/xpath) |
| `value_of` | 12 declared types; see details | 0..1 | Text or attribute values selected by the XPath expression. | [/$defs/meanings/properties/value_of](../../../proposed-schema/documentation/capabilities/independent.xmlfilecontent.schema.json#/$defs/meanings/properties/value_of) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

The comparison fields contain entities that are used to check the file path and name, as well as the xpath used and the value of the this xpath.

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/independent.xmlfilecontent.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |
| Object.`item_creation` | {"enum": ["all_object_elements_fullfilled", "filepath_exists"], "required": true, "type": "string"} | native-mapping-reviewed |
| Item.`value_of` | string, boolean, integer, float, binary, version, ipv4, ipv6, rpm_evr, debian_evr, fileset_revision, ios_version | source-meaning-reviewed |

See the [schema](../../../proposed-schema/documentation/capabilities/independent.xmlfilecontent.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `independent-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
