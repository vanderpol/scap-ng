# SCAP-NG shared capability schema primitives v0.4.1 — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/variable_reference](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/variable_reference) | {"type": "object", "required": ["variable"], "additionalProperties": false} | editorially-approved |

[/$defs/variable_reference](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/variable_reference): Uses the value of a declared Variable.

Editorial receipt: editorial-batch.json case 02

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/variable_reference/properties/variable](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/variable_reference/properties/variable) | {"type": "string", "minLength": 1, "pattern": "^[a-z0-9]+(?:-[a-z0-9]+)*-variable$", "maxLength": 64} | existing-native |
| [/$defs/entity_value](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/entity_value) | {} | native-grammar-derived |
| [/$defs/entity_value/oneOf/0](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/entity_value/oneOf/0) | {"type": ["string", "number", "integer", "boolean"]} | existing-native |
| [/$defs/state_entity_base](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/state_entity_base) | {} | native-grammar-derived |
| [/$defs/state_filter](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/state_filter) | {} | editorially-approved |

[/$defs/state_filter](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/state_filter): Includes or excludes collected Items that match a field condition.

Editorial receipt: editorial-batch.json case 20

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/state_filter/oneOf/0](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/state_filter/oneOf/0) | {"type": "object", "required": ["include"], "additionalProperties": false} | existing-native |
| [/$defs/state_filter/oneOf/1](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/state_filter/oneOf/1) | {"type": "object", "required": ["exclude"], "additionalProperties": false} | existing-native |
| [/$defs/test_reference_set](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/test_reference_set) | {"type": "array"} | existing-native |
| [/$defs/comparison_operation](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/comparison_operation) | {"type": "string", "enum": ["equals", "not_equal", "case_insensitive_equals", "case_insensitive_not_equal", "greater_than", "greater_than_or_equal", "less_than", "less_than_or_equal", "bitwise_and", "bitwise_or", "pattern_match", "subset_of", "superset_of", "float_equals", "float_not_equal", "float_greater_than", "float_greater_than_or_equal", "float_less_than", "float_less_than_or_equal", "binary_equals", "binary_not_equal", "version_equals", "version_not_equal", "version_greater_than", "version_greater_than_or_equal", "version_less_than", "version_less_than_or_equal", "ipv4_equals", "ipv4_not_equal", "ipv4_greater_than", "ipv4_greater_than_or_equal", "ipv4_less_than", "ipv4_less_than_or_equal", "ipv4_subset_of", "ipv4_superset_of", "ipv6_equals", "ipv6_not_equal", "ipv6_greater_than", "ipv6_greater_than_or_equal", "ipv6_less_than", "ipv6_less_than_or_equal", "ipv6_subset_of", "ipv6_superset_of", "rpm_evr_equals", "rpm_evr_not_equal", "rpm_evr_greater_than", "rpm_evr_greater_than_or_equal", "rpm_evr_less_than", "rpm_evr_less_than_or_equal", "debian_evr_equals", "debian_evr_not_equal", "debian_evr_greater_than", "debian_evr_greater_than_or_equal", "debian_evr_less_than", "debian_evr_less_than_or_equal", "fileset_revision_equals", "fileset_revision_not_equal", "fileset_revision_greater_than", "fileset_revision_greater_than_or_equal", "fileset_revision_less_than", "fileset_revision_less_than_or_equal", "ios_version_equals", "ios_version_not_equal", "ios_version_greater_than", "ios_version_greater_than_or_equal", "ios_version_less_than", "ios_version_less_than_or_equal"]} | native-grammar-derived |
| [/$defs/match_quantifier](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/match_quantifier) | {"type": "string", "enum": ["every", "one_or_more", "exactly_one", "none"]} | native-grammar-derived |
| [/$defs/existence_requirement](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/existence_requirement) | {"type": "string", "enum": ["every", "one_or_more", "none", "exactly_one", "zero_or_more"]} | native-grammar-derived |
| [/$defs/logical_operator](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/logical_operator) | {"type": "string", "enum": ["and", "or", "one", "xor"]} | native-grammar-derived |
| [/$defs/native_datatype](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/native_datatype) | {"type": "string", "enum": ["string", "boolean", "integer", "float", "binary", "version", "ipv4", "ipv6", "rpm_evr", "debian_evr", "fileset_revision", "ios_version", "record"]} | native-grammar-derived |
| [/$defs/file_traversal](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/file_traversal) | {"unevaluatedProperties": false} | existing-native |

[/$defs/file_traversal](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/file_traversal): Controls recursive searching through directories and symbolic links.

Traversal is downward. Its binding to equality-selected path versus filepath is not yet specified consistently by the native contracts.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/file_traversal/allOf/1](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/file_traversal/allOf/1) | {"type": "object"} | existing-native |
| [/$defs/file_traversal/allOf/1/properties/recurse](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/file_traversal/allOf/1/properties/recurse) | {"type": "string", "enum": ["directories", "symlinks", "symlinks_and_directories"], "default": "symlinks_and_directories"} | existing-native |
| [/$defs/file_selection](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/file_selection) | {"type": "object", "additionalProperties": false} | native-grammar-derived |
| [/$defs/file_selection/oneOf/0](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/file_selection/oneOf/0) | {"required": ["full_path"]} | existing-native |
| [/$defs/file_selection/oneOf/0/not/anyOf/0](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/file_selection/oneOf/0/not/anyOf/0) | {"required": ["directory"]} | existing-native |
| [/$defs/file_selection/oneOf/0/not/anyOf/1](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/file_selection/oneOf/0/not/anyOf/1) | {"required": ["name"]} | existing-native |
| [/$defs/file_selection/oneOf/0/not/anyOf/2](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/file_selection/oneOf/0/not/anyOf/2) | {"required": ["traversal"]} | existing-native |
| [/$defs/file_selection/oneOf/1](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/file_selection/oneOf/1) | {"required": ["directory", "name"]} | existing-native |
| [/$defs/file_selection/oneOf/1/not](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/file_selection/oneOf/1/not) | {"required": ["full_path"]} | existing-native |
| [/$defs/set_object_operand](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/set_object_operand) | {"type": "object", "required": ["object", "filters"], "additionalProperties": false} | native-grammar-derived |
| [/$defs/set_object_operand/properties/filters](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/set_object_operand/properties/filters) | {"type": "array"} | existing-native |
| [/$defs/set_nested_operand](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/set_nested_operand) | {"type": "object", "required": ["set"], "additionalProperties": false} | native-grammar-derived |
| [/$defs/set_operand](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/set_operand) | {} | native-grammar-derived |
| [/$defs/set_expression](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/set_expression) | {"type": "object", "required": ["operator", "operands"], "additionalProperties": false} | editorially-approved |

[/$defs/set_expression](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/set_expression): Combines Object collections using union, intersection, or difference.

Editorial receipt: editorial-batch.json case 19

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/set_expression/properties/operator](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/set_expression/properties/operator) | {"type": "string", "enum": ["union", "intersection", "difference"]} | native-grammar-derived |
| [/$defs/set_expression/properties/operands](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/set_expression/properties/operands) | {"type": "array", "minItems": 1} | native-grammar-derived |
| [/$defs/set_expression/allOf/0/if](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/set_expression/allOf/0/if) | {"required": ["operator"]} | existing-native |
| [/$defs/set_expression/allOf/0/if/properties/operator](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/set_expression/allOf/0/if/properties/operator) | {"const": "difference"} | existing-native |
| [/$defs/set_expression/allOf/0/then/properties/operands](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/set_expression/allOf/0/then/properties/operands) | {"maxItems": 2} | existing-native |
| [/$defs/hierarchy_traversal](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/hierarchy_traversal) | {"type": "object", "required": ["max_depth"], "additionalProperties": false} | existing-native |
| [/$defs/hierarchy_traversal/properties/max_depth](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/hierarchy_traversal/properties/max_depth) | {"default": "unlimited"} | existing-native |
| [/$defs/hierarchy_traversal/properties/max_depth/oneOf/0](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/hierarchy_traversal/properties/max_depth/oneOf/0) | {"type": "integer", "minimum": 0} | existing-native |
| [/$defs/hierarchy_traversal/properties/max_depth/oneOf/1](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/hierarchy_traversal/properties/max_depth/oneOf/1) | {"const": "unlimited"} | existing-native |
| [/$defs/record_field_predicate](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/record_field_predicate) | {} | native-grammar-derived |
| [/$defs/record_predicate](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/record_predicate) | {} | native-grammar-derived |
| [/$defs/scalar_value_predicate](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/scalar_value_predicate) | {} | native-grammar-derived |
| [/$defs/structured_value_predicate](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/structured_value_predicate) | {} | native-grammar-derived |
| [/$defs/structured_value_predicate/oneOf/1](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/structured_value_predicate/oneOf/1) | {"type": "object", "required": ["record"], "additionalProperties": false} | existing-native |
| [/$defs/structured_value_predicate/oneOf/2](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/structured_value_predicate/oneOf/2) | {"type": "object", "required": ["list"], "additionalProperties": false} | existing-native |
| [/$defs/list_predicate](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/list_predicate) | {"type": "object", "required": ["item", "values_matching", "values_found"], "additionalProperties": false} | native-grammar-derived |
| [/$defs/list_predicate/properties/redact_result](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/list_predicate/properties/redact_result) | {"type": "boolean", "const": true} | existing-native |
| [/$defs/file_traversal_base](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/file_traversal_base) | {"type": "object", "required": ["max_depth", "recurse"], "additionalProperties": false} | existing-native |
| [/$defs/file_traversal_base/properties/max_depth](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/file_traversal_base/properties/max_depth) | {"default": "unlimited"} | existing-native |
| [/$defs/file_traversal_base/properties/max_depth/oneOf/0](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/file_traversal_base/properties/max_depth/oneOf/0) | {"type": "integer", "minimum": 0} | existing-native |
| [/$defs/file_traversal_base/properties/max_depth/oneOf/1](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/file_traversal_base/properties/max_depth/oneOf/1) | {"const": "unlimited"} | existing-native |
| [/$defs/file_traversal_base/properties/recurse](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/file_traversal_base/properties/recurse) | {"type": "string", "minLength": 1} | existing-native |
| [/$defs/windows_file_traversal](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/windows_file_traversal) | {"unevaluatedProperties": false} | existing-native |
| [/$defs/windows_file_traversal/allOf/1](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/windows_file_traversal/allOf/1) | {"type": "object"} | existing-native |
| [/$defs/windows_file_traversal/allOf/1/properties/recurse](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/windows_file_traversal/allOf/1/properties/recurse) | {"type": "string", "enum": ["directories", "junctions", "junctions_and_directories"], "default": "directories"} | existing-native |
| [/$defs/object_record](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/object_record) | {"type": "object", "required": ["fields"], "additionalProperties": false} | existing-native |
| [/$defs/object_record/properties/fields](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/object_record/properties/fields) | {"type": "object"} | native-grammar-derived |
| [/$defs/object_record/properties/fields/propertyNames](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/object_record/properties/fields/propertyNames) | {"type": "string", "minLength": 1} | existing-native |
| [/$defs/object_record/properties/redact_result](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/object_record/properties/redact_result) | {"type": "boolean", "const": true} | existing-native |
| [/$defs/filesystem_scope](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/filesystem_scope) | {"type": "string", "enum": ["all", "local", "same"], "default": "local"} | existing-native |

[/$defs/filesystem_scope](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/filesystem_scope): Filesystem scope: all, local, or the starting filesystem (same).

Filesystem scope is independent of recursion. Link/target metadata, cycle handling and precise local/same mount classification remain unspecified.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/foreach_binding](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/foreach_binding) | {"type": "object", "required": ["item", "in"], "additionalProperties": false} | withheld |

[/$defs/foreach_binding](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/foreach_binding): Native 0.4 collection-expansion foreach binding. The source is one named shared/referenceable Object. Chaining is permitted: a source Object may itself use for_each, creating correlated lexical lineage. Independent multi-source Cartesian expansion is not implicit.

No author-facing description is approved or offered. Neither foreach helper is reachable from accepted Assessment authoring; resolve placement/activation with Jack before advertising support or providing an authored for_each example.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/foreach_binding/properties/item](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/foreach_binding/properties/item) | {"type": "string", "pattern": "^[A-Za-z_][A-Za-z0-9_-]*$"} | existing-native |
| [/$defs/foreach_selector_binding](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/foreach_selector_binding) | {"type": "object", "required": ["from"], "additionalProperties": false} | existing-native |
| [/$defs/foreach_selector_binding/properties/from](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/foreach_selector_binding/properties/from) | {"type": "string", "pattern": "^[A-Za-z_][A-Za-z0-9_-]*\\.[A-Za-z_][A-Za-z0-9_-]*$"} | existing-native |
| [/$defs/object_reference](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/object_reference) | {"type": "string", "minLength": 1, "maxLength": 64, "pattern": "^[a-z0-9]+(?:-[a-z0-9]+)*-object$"} | editorially-approved |

[/$defs/object_reference](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/object_reference): Reuses a named Object for collection.

Editorial receipt: editorial-batch.json case 03

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object) | {"type": "object", "required": [], "additionalProperties": true} | existing-native |
| [/$defs/inline_object/properties/capability](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object/properties/capability) | {"type": "string", "minLength": 1} | existing-native |
| [/$defs/inline_object/properties/filters](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object/properties/filters) | {"type": "array", "minItems": 1} | existing-native |
| [/$defs/inline_object/not/anyOf/0](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object/not/anyOf/0) | {"required": ["result"]} | existing-native |
| [/$defs/inline_object/not/anyOf/1](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object/not/anyOf/1) | {"required": ["collect"]} | existing-native |
| [/$defs/inline_object/allOf/0/not](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object/allOf/0/not) | {"required": ["set", "filters"]} | existing-native |
| [/$defs/literal_collection](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/literal_collection) | {"type": "array", "minItems": 1} | existing-native |
| [/$defs/literal_collection/items](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/literal_collection/items) | {"type": ["string", "number", "integer", "boolean"]} | existing-native |
| [/$defs/input_reference](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/input_reference) | {"type": "object", "required": ["input"], "additionalProperties": false} | editorially-approved |

[/$defs/input_reference](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/input_reference): Uses the value of a declared Input.

Editorial receipt: editorial-batch.json case 01

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/input_reference/properties/input](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/input_reference/properties/input) | {"type": "string", "minLength": 1} | existing-native |
| [/$defs/authoring_type_resolution](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/authoring_type_resolution) | {} | unresolved-legacy-helper |
| [/$defs/authoring_type_resolution/if](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/authoring_type_resolution/if) | {"required": ["datatype"]} | existing-native |
| [/$defs/authoring_type_resolution/then/properties/operation](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/authoring_type_resolution/then/properties/operation) | {"enum": ["equals", "not_equal", "case_insensitive_equals", "case_insensitive_not_equal", "greater_than", "greater_than_or_equal", "less_than", "less_than_or_equal", "bitwise_and", "bitwise_or", "pattern_match", "subset_of", "superset_of"]} | existing-native |
| [/$defs/authoring_type_resolution/else/anyOf/0](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/authoring_type_resolution/else/anyOf/0) | {"required": ["value", "operation"]} | existing-native |
| [/$defs/authoring_type_resolution/else/anyOf/0/properties/operation](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/authoring_type_resolution/else/anyOf/0/properties/operation) | {"enum": ["equals", "not_equal", "case_insensitive_equals", "case_insensitive_not_equal", "pattern_match"]} | existing-native |
| [/$defs/authoring_type_resolution/else/anyOf/0/properties/value](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/authoring_type_resolution/else/anyOf/0/properties/value) | {"type": "string"} | existing-native |
| [/$defs/authoring_type_resolution/else/anyOf/1](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/authoring_type_resolution/else/anyOf/1) | {"required": ["value", "operation"]} | existing-native |
| [/$defs/authoring_type_resolution/else/anyOf/1/properties/operation](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/authoring_type_resolution/else/anyOf/1/properties/operation) | {"enum": ["equals", "not_equal"]} | existing-native |
| [/$defs/authoring_type_resolution/else/anyOf/1/properties/value](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/authoring_type_resolution/else/anyOf/1/properties/value) | {"type": "boolean"} | existing-native |
| [/$defs/authoring_type_resolution/else/anyOf/2](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/authoring_type_resolution/else/anyOf/2) | {"required": ["value", "operation"]} | existing-native |
| [/$defs/authoring_type_resolution/else/anyOf/2/properties/operation](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/authoring_type_resolution/else/anyOf/2/properties/operation) | {"enum": ["equals", "not_equal", "greater_than", "greater_than_or_equal", "less_than", "less_than_or_equal", "bitwise_and", "bitwise_or"]} | existing-native |
| [/$defs/authoring_type_resolution/else/anyOf/2/properties/value](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/authoring_type_resolution/else/anyOf/2/properties/value) | {"type": "integer"} | existing-native |
| [/$defs/authoring_type_resolution/else/anyOf/3](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/authoring_type_resolution/else/anyOf/3) | {"required": ["value", "operation"]} | existing-native |
| [/$defs/authoring_type_resolution/else/anyOf/3/properties/operation](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/authoring_type_resolution/else/anyOf/3/properties/operation) | {"enum": ["equals", "not_equal", "greater_than", "greater_than_or_equal", "less_than", "less_than_or_equal"]} | existing-native |
| [/$defs/authoring_type_resolution/else/anyOf/3/properties/value](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/authoring_type_resolution/else/anyOf/3/properties/value) | {"type": "number"} | existing-native |
| [/$defs/authoring_type_resolution/else/anyOf/4](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/authoring_type_resolution/else/anyOf/4) | {"required": ["value", "operation"]} | existing-native |
| [/$defs/authoring_type_resolution/else/anyOf/4/properties/operation](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/authoring_type_resolution/else/anyOf/4/properties/operation) | {"enum": ["float_equals", "float_not_equal", "float_greater_than", "float_greater_than_or_equal", "float_less_than", "float_less_than_or_equal"]} | existing-native |
| [/$defs/authoring_type_resolution/else/anyOf/4/properties/value](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/authoring_type_resolution/else/anyOf/4/properties/value) | {"type": "number"} | existing-native |
| [/$defs/authoring_type_resolution/else/anyOf/5](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/authoring_type_resolution/else/anyOf/5) | {"required": ["value", "operation"]} | existing-native |
| [/$defs/authoring_type_resolution/else/anyOf/5/properties/operation](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/authoring_type_resolution/else/anyOf/5/properties/operation) | {"enum": ["binary_equals", "binary_not_equal"]} | existing-native |
| [/$defs/authoring_type_resolution/else/anyOf/5/properties/value](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/authoring_type_resolution/else/anyOf/5/properties/value) | {"type": "string"} | existing-native |
| [/$defs/authoring_type_resolution/else/anyOf/6](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/authoring_type_resolution/else/anyOf/6) | {"required": ["value", "operation"]} | existing-native |
| [/$defs/authoring_type_resolution/else/anyOf/6/properties/operation](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/authoring_type_resolution/else/anyOf/6/properties/operation) | {"enum": ["version_equals", "version_not_equal", "version_greater_than", "version_greater_than_or_equal", "version_less_than", "version_less_than_or_equal"]} | existing-native |
| [/$defs/authoring_type_resolution/else/anyOf/6/properties/value](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/authoring_type_resolution/else/anyOf/6/properties/value) | {"type": "string"} | existing-native |
| [/$defs/authoring_type_resolution/else/anyOf/7](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/authoring_type_resolution/else/anyOf/7) | {"required": ["value", "operation"]} | existing-native |
| [/$defs/authoring_type_resolution/else/anyOf/7/properties/operation](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/authoring_type_resolution/else/anyOf/7/properties/operation) | {"enum": ["ipv4_equals", "ipv4_not_equal", "ipv4_greater_than", "ipv4_greater_than_or_equal", "ipv4_less_than", "ipv4_less_than_or_equal", "ipv4_subset_of", "ipv4_superset_of"]} | existing-native |
| [/$defs/authoring_type_resolution/else/anyOf/7/properties/value](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/authoring_type_resolution/else/anyOf/7/properties/value) | {"type": "string"} | existing-native |
| [/$defs/authoring_type_resolution/else/anyOf/8](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/authoring_type_resolution/else/anyOf/8) | {"required": ["value", "operation"]} | existing-native |
| [/$defs/authoring_type_resolution/else/anyOf/8/properties/operation](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/authoring_type_resolution/else/anyOf/8/properties/operation) | {"enum": ["ipv6_equals", "ipv6_not_equal", "ipv6_greater_than", "ipv6_greater_than_or_equal", "ipv6_less_than", "ipv6_less_than_or_equal", "ipv6_subset_of", "ipv6_superset_of"]} | existing-native |
| [/$defs/authoring_type_resolution/else/anyOf/8/properties/value](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/authoring_type_resolution/else/anyOf/8/properties/value) | {"type": "string"} | existing-native |
| [/$defs/authoring_type_resolution/else/anyOf/9](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/authoring_type_resolution/else/anyOf/9) | {"required": ["value", "operation"]} | existing-native |
| [/$defs/authoring_type_resolution/else/anyOf/9/properties/operation](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/authoring_type_resolution/else/anyOf/9/properties/operation) | {"enum": ["rpm_evr_equals", "rpm_evr_not_equal", "rpm_evr_greater_than", "rpm_evr_greater_than_or_equal", "rpm_evr_less_than", "rpm_evr_less_than_or_equal"]} | existing-native |
| [/$defs/authoring_type_resolution/else/anyOf/9/properties/value](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/authoring_type_resolution/else/anyOf/9/properties/value) | {"type": "string"} | existing-native |
| [/$defs/authoring_type_resolution/else/anyOf/10](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/authoring_type_resolution/else/anyOf/10) | {"required": ["value", "operation"]} | existing-native |
| [/$defs/authoring_type_resolution/else/anyOf/10/properties/operation](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/authoring_type_resolution/else/anyOf/10/properties/operation) | {"enum": ["debian_evr_equals", "debian_evr_not_equal", "debian_evr_greater_than", "debian_evr_greater_than_or_equal", "debian_evr_less_than", "debian_evr_less_than_or_equal"]} | existing-native |
| [/$defs/authoring_type_resolution/else/anyOf/10/properties/value](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/authoring_type_resolution/else/anyOf/10/properties/value) | {"type": "string"} | existing-native |
| [/$defs/authoring_type_resolution/else/anyOf/11](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/authoring_type_resolution/else/anyOf/11) | {"required": ["value", "operation"]} | existing-native |
| [/$defs/authoring_type_resolution/else/anyOf/11/properties/operation](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/authoring_type_resolution/else/anyOf/11/properties/operation) | {"enum": ["fileset_revision_equals", "fileset_revision_not_equal", "fileset_revision_greater_than", "fileset_revision_greater_than_or_equal", "fileset_revision_less_than", "fileset_revision_less_than_or_equal"]} | existing-native |
| [/$defs/authoring_type_resolution/else/anyOf/11/properties/value](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/authoring_type_resolution/else/anyOf/11/properties/value) | {"type": "string"} | existing-native |
| [/$defs/authoring_type_resolution/else/anyOf/12](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/authoring_type_resolution/else/anyOf/12) | {"required": ["value", "operation"]} | existing-native |
| [/$defs/authoring_type_resolution/else/anyOf/12/properties/operation](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/authoring_type_resolution/else/anyOf/12/properties/operation) | {"enum": ["ios_version_equals", "ios_version_not_equal", "ios_version_greater_than", "ios_version_greater_than_or_equal", "ios_version_less_than", "ios_version_less_than_or_equal"]} | existing-native |
| [/$defs/authoring_type_resolution/else/anyOf/12/properties/value](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/authoring_type_resolution/else/anyOf/12/properties/value) | {"type": "string"} | existing-native |
