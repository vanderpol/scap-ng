# SCAP-NG shared capability schema primitives v0.4.1

Proposed documentation. Defaults are schema annotations, not inferred scanner fallbacks. Conditional requirements and alternatives remain linked in the schema.

Pre-alpha reusable authored-Assessment primitives shared by generated capability schemas. Capability-specific schemas SHOULD reference these definitions instead of copying them. Base entity definitions intentionally leave closure to the capability schema via unevaluatedProperties so capability-specific fields can be composed without duplicating common properties. Generic OVAL mask is intentionally absent from native authored predicates; sensitive evidence redaction is a separate results concern. Native 0.4 authoring may omit an inferred literal comparison datatype or use a self-describing typed operation; published compiled Assessments retain fully explicit canonical datatypes. compare_as is not supported.

## `/`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `variable_reference` | object | Definition | Uses the value of a declared Variable. | [/$defs/variable_reference](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/variable_reference) |
| `entity_value` | array, boolean, integer, number, object, string | Definition | Literal scalar, literal collection, Variable reference, or Input reference. | [/$defs/entity_value](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/entity_value) |
| `object_entity_base` | object | Definition | Version-local 0.4 Object selector, no 0.3 value+operation longhand. | [/$defs/object_entity_base](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/object_entity_base) |
| `state_entity_base` | object | Definition | Shared scalar field comparison grammar. | [/$defs/state_entity_base](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/state_entity_base) |
| `state_filter` | object | Definition | Includes or excludes collected Items that match a field condition. | [/$defs/state_filter](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/state_filter) |
| `test_reference_set` | array | Definition | Test-local comparison expressions; no State IDs or redundant capability declarations. | [/$defs/test_reference_set](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/test_reference_set) |
| `comparison_operation` | string | Definition | Names a comparison operation from the retained vocabulary. | [/$defs/comparison_operation](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/comparison_operation) |
| `match_quantifier` | string | Definition | Specifies how many values must match a condition. | [/$defs/match_quantifier](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/match_quantifier) |
| `existence_requirement` | string | Definition | Specifies how many values must be present. | [/$defs/existence_requirement](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/existence_requirement) |
| `logical_operator` | string | Definition | Names a logical grouping operator. | [/$defs/logical_operator](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/logical_operator) |
| `native_datatype` | string | Definition | Names the datatype used for a native value. | [/$defs/native_datatype](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/native_datatype) |
| `file_traversal` | object | Definition | Controls recursive searching through directories and symbolic links. | [/$defs/file_traversal](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/file_traversal) |
| `file_selection` | object | Definition | File selection fields shared by file-oriented capabilities. | [/$defs/file_selection](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/file_selection) |
| `set_object_operand` | object | Definition | References an Object used as a Set operand. | [/$defs/set_object_operand](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/set_object_operand) |
| `set_nested_operand` | object | Definition | Supplies a nested Set expression as an operand. | [/$defs/set_nested_operand](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/set_nested_operand) |
| `set_operand` | object | Definition | An Object reference or nested Set expression. | [/$defs/set_operand](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/set_operand) |
| `set_expression` | object | Definition | Combines Object collections using union, intersection, or difference. | [/$defs/set_expression](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/set_expression) |
| `hierarchy_traversal` | object | Definition | Controls downward traversal from the selected hierarchy entry. | [/$defs/hierarchy_traversal](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/hierarchy_traversal) |
| `record_field_predicate` | object | Definition | Comparison condition for one field within a record. | [/$defs/record_field_predicate](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/record_field_predicate) |
| `record_predicate` | object | Definition | Conditions on named fields within a record. | [/$defs/record_predicate](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/record_predicate) |
| `scalar_value_predicate` | object | Definition | Comparison condition for a scalar value. | [/$defs/scalar_value_predicate](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/scalar_value_predicate) |
| `structured_value_predicate` | object | Definition | Condition on a scalar, record, or list value. | [/$defs/structured_value_predicate](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/structured_value_predicate) |
| `list_predicate` | object | Definition | Condition on the members of a collected list. | [/$defs/list_predicate](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/list_predicate) |
| `file_traversal_base` | object | Definition | Shared non-deprecated downward file recursion structure. | [/$defs/file_traversal_base](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/file_traversal_base) |
| `windows_file_traversal` | object | Definition | Windows file traversal. | [/$defs/windows_file_traversal](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/windows_file_traversal) |
| `object_record_field` | object | Definition | Collector Object record field. | [/$defs/object_record_field](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/object_record_field) |
| `object_record` | object | Definition | Authored WMI/cmdlet collector input record. | [/$defs/object_record](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/object_record) |
| `filesystem_scope` | string | Definition | Filesystem scope: all, local, or the starting filesystem (same). | [/$defs/filesystem_scope](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/filesystem_scope) |
| `foreach_binding` | object | Definition | **Withheld.** Retained schema definition; not approved for native authoring. | [/$defs/foreach_binding](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/foreach_binding) |
| `foreach_selector_binding` | object | Definition | Bind this selector from one field of a visible foreach lineage alias, e.g. user.home_dir. | [/$defs/foreach_selector_binding](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/foreach_selector_binding) |
| `object_reference` | string | Definition | Reuses a named Object for collection. | [/$defs/object_reference](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/object_reference) |
| `inline_object` | object | Definition | Inline native Object. | [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object) |
| `object_use` | object, string | Definition | Use an inline Object or an existing shared Object. | [/$defs/object_use](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/object_use) |
| `literal_collection` | array | Definition | Non-empty ordered literal collection. | [/$defs/literal_collection](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/literal_collection) |
| `input_reference` | object | Definition | Uses the value of a declared Input. | [/$defs/input_reference](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/input_reference) |
| `inline_predicate` | object | Definition | A field predicate or logical combination of predicates applied to one collected Item. | [/$defs/inline_predicate](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_predicate) |
| `authoring_type_resolution` | See schema | Definition | Retained type-resolution helper. | [/$defs/authoring_type_resolution](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/authoring_type_resolution) |

## `/$defs/variable_reference`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `variable` | string | 1..1 (required) | Identifier of the Variable whose values are referenced. | [/$defs/variable_reference/properties/variable](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/variable_reference/properties/variable) |

## `/$defs/state_filter/oneOf/0`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `include` | object | 1..1 (required) | A field predicate or logical combination of predicates applied to one collected Item. | [/$defs/state_filter/oneOf/0/properties/include](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/state_filter/oneOf/0/properties/include) |

## `/$defs/state_filter/oneOf/1`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `exclude` | object | 1..1 (required) | A field predicate or logical combination of predicates applied to one collected Item. | [/$defs/state_filter/oneOf/1/properties/exclude](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/state_filter/oneOf/1/properties/exclude) |

## `/$defs/file_selection`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `full_path` | object | Conditional (at most 1) | Version-local 0.4 Object selector, no 0.3 value+operation longhand. | [/$defs/file_selection/properties/full_path](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/file_selection/properties/full_path) |
| `directory` | object | Conditional (at most 1) | Version-local 0.4 Object selector, no 0.3 value+operation longhand. | [/$defs/file_selection/properties/directory](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/file_selection/properties/directory) |
| `name` | object | Conditional (at most 1) | Version-local 0.4 Object selector, no 0.3 value+operation longhand. | [/$defs/file_selection/properties/name](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/file_selection/properties/name) |
| `traversal` | object | 0..1 | Controls recursive searching through directories and symbolic links. | [/$defs/file_selection/properties/traversal](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/file_selection/properties/traversal) |
| `filesystem` | string | 0..1 | Filesystem scope: all, local, or the starting filesystem (same). | [/$defs/file_selection/properties/filesystem](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/file_selection/properties/filesystem) |

## `/$defs/set_object_operand`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `object` | object, string | 1..1 (required) | Use an inline Object or an existing shared Object. | [/$defs/set_object_operand/properties/object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/set_object_operand/properties/object) |
| `filters` | array | 1..1 (required) | Post-collection inclusion or exclusion filters applied to observed Items. | [/$defs/set_object_operand/properties/filters](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/set_object_operand/properties/filters) |

## `/$defs/set_nested_operand`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `set` | object | 1..1 (required) | Combines Object collections using union, intersection, or difference. | [/$defs/set_nested_operand/properties/set](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/set_nested_operand/properties/set) |

## `/$defs/set_expression`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `operator` | string | 1..1 (required) | Set operation applied to the operands. | [/$defs/set_expression/properties/operator](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/set_expression/properties/operator) |
| `operands` | array | 1..1 (required) | Ordered Object references or nested Set expressions. | [/$defs/set_expression/properties/operands](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/set_expression/properties/operands) |

## `/$defs/hierarchy_traversal`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `max_depth` | integer, string | 1..1 (required) | Maximum downward hierarchy recursion depth; 0 means the starting key only, and unlimited removes the depth limit. | [/$defs/hierarchy_traversal/properties/max_depth](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/hierarchy_traversal/properties/max_depth) |

## `/$defs/structured_value_predicate/oneOf/1`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `record` | object | 1..1 (required) | Conditions on named fields within a record. | [/$defs/structured_value_predicate/oneOf/1/properties/record](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/structured_value_predicate/oneOf/1/properties/record) |

## `/$defs/structured_value_predicate/oneOf/2`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `list` | object | 1..1 (required) | Condition on the members of a collected list. | [/$defs/structured_value_predicate/oneOf/2/properties/list](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/structured_value_predicate/oneOf/2/properties/list) |

## `/$defs/list_predicate`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `item` | object | 1..1 (required) | Condition on a scalar, record, or list value. | [/$defs/list_predicate/properties/item](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/list_predicate/properties/item) |
| `values_matching` | string | 1..1 (required) | Specifies how many values must match a condition. | [/$defs/list_predicate/properties/values_matching](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/list_predicate/properties/values_matching) |
| `values_found` | string | 1..1 (required) | Specifies how many values must be present. | [/$defs/list_predicate/properties/values_found](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/list_predicate/properties/values_found) |
| `redact_result` | boolean | 0..1 | When present, this value requests omission/redaction of the corresponding collected value from emitted result/evidence payloads. | [/$defs/list_predicate/properties/redact_result](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/list_predicate/properties/redact_result) |

## `/$defs/file_traversal_base`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `max_depth` | integer, string | 1..1 (required) | Maximum downward recursion depth; 0 includes only the starting directory. | [/$defs/file_traversal_base/properties/max_depth](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/file_traversal_base/properties/max_depth) |
| `recurse` | string | 1..1 (required) | Entry types to follow during recursion. | [/$defs/file_traversal_base/properties/recurse](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/file_traversal_base/properties/recurse) |

## `/$defs/object_record`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `fields` | object | 1..1 (required) | Named fields forming the record selector. | [/$defs/object_record/properties/fields](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/object_record/properties/fields) |
| `redact_result` | boolean | 0..1 | When present, this value requests omission/redaction of the corresponding collected value from emitted result/evidence payloads. | [/$defs/object_record/properties/redact_result](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/object_record/properties/redact_result) |

## `/$defs/foreach_binding`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `item` | string | 1..1 (required) | Lexical name for one Item produced by the source Object. | [/$defs/foreach_binding/properties/item](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/foreach_binding/properties/item) |
| `in` | string | 1..1 (required) | Reuses a named Object for collection. | [/$defs/foreach_binding/properties/in](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/foreach_binding/properties/in) |

## `/$defs/foreach_selector_binding`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `from` | string | 1..1 (required) | Bind this target selector from one field of the current foreach Item, e.g. user.home_dir. | [/$defs/foreach_selector_binding/properties/from](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/foreach_selector_binding/properties/from) |

## `/$defs/inline_object`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/inline_object/properties/capability](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/inline_object/properties/filters](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object/properties/filters) |

## `/$defs/input_reference`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `input` | string | 1..1 (required) | Identifier of the Input supplying the value. | [/$defs/input_reference/properties/input](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/input_reference/properties/input) |

## Advanced constraints

[Local constraints](../advanced/capability-common.md) and [complete JSON Schema](../../../proposed-schema/documentation/capability-common.schema.json) contain conditional requirements, alternatives, bounds and validation expressions. A mapping property occurs at most once; `items`, `minItems` and `maxItems` constrain array members separately. A definition is reusable schema grammar, not itself an authored mapping key.
