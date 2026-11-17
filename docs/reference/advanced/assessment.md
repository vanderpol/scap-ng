# SCAP-NG Assessment v0.4.1 draft — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/assessment.schema.json#) | {"type": "object", "required": ["assessment"], "additionalProperties": false} | editorially-approved |

[schema](../../../proposed-schema/documentation/assessment.schema.json#): Defines an Assessment's metadata and its manual procedure or automated checks.

Editorial receipt: editorial-batch.json case 25

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/properties/assessment](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment) | {"type": "object", "required": ["id", "version", "assessment_title", "mode", "class"], "additionalProperties": false} | existing-native |
| [/properties/assessment/properties/id](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/id) | {"type": "string", "minLength": 1, "pattern": "^[a-z0-9]+(?:-[a-z0-9]+)*$", "maxLength": 64} | native-grammar-derived |
| [/properties/assessment/properties/version](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/version) | {"type": ["integer", "string"]} | native-grammar-derived |
| [/properties/assessment/properties/assessment_title](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/assessment_title) | {"type": ["string", "null"]} | native-grammar-derived |
| [/properties/assessment/properties/mode](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/mode) | {"type": "string", "enum": ["manual", "automated"]} | editorially-approved |

[/properties/assessment/properties/mode](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/mode): Selects whether the Assessment uses a manual procedure or automated Tests.

Editorial receipt: editorial-batch-2.json case 01

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/properties/assessment/properties/class](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/class) | {"type": "string", "enum": ["compliance", "vulnerability", "patch", "inventory", "miscellaneous"]} | native-grammar-derived |
| [/properties/assessment/properties/variables](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/variables) | {"type": "object"} | existing-native |
| [/properties/assessment/properties/variables/propertyNames](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/variables/propertyNames) | {"type": "string", "pattern": "^[a-z0-9]+(?:-[a-z0-9]+)*-variable$", "maxLength": 64} | existing-native |
| [/properties/assessment/properties/tests](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/tests) | {"type": "object"} | editorially-approved |

[/properties/assessment/properties/tests](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/tests): Defines the named Tests available to this Assessment.

Editorial receipt: editorial-batch-2.json case 02

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/properties/assessment/properties/tests/additionalProperties](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/tests/additionalProperties) | {"type": "object", "required": ["test_title", "capability", "require"], "additionalProperties": false} | existing-native |
| [/properties/assessment/properties/tests/additionalProperties/properties/test_title](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/tests/additionalProperties/properties/test_title) | {"type": ["string", "null"]} | existing-native |
| [/properties/assessment/properties/tests/additionalProperties/properties/reported_elements](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/tests/additionalProperties/properties/reported_elements) | {"default": "all"} | existing-native |
| [/properties/assessment/properties/tests/additionalProperties/properties/capability](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/tests/additionalProperties/properties/capability) | {"type": "string", "minLength": 1} | existing-native |
| [/properties/assessment/properties/tests/additionalProperties/properties/variable](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/tests/additionalProperties/properties/variable) | {"type": "string", "pattern": "^[a-z0-9]+(?:-[a-z0-9]+)*-variable$"} | existing-native |
| [/properties/assessment/properties/tests/additionalProperties/not/anyOf/0](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/tests/additionalProperties/not/anyOf/0) | {"required": ["result"]} | existing-native |
| [/properties/assessment/properties/tests/additionalProperties/not/anyOf/1](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/tests/additionalProperties/not/anyOf/1) | {"required": ["existence"]} | existing-native |
| [/properties/assessment/properties/tests/additionalProperties/not/anyOf/2](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/tests/additionalProperties/not/anyOf/2) | {"required": ["match"]} | existing-native |
| [/properties/assessment/properties/tests/additionalProperties/not/anyOf/3](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/tests/additionalProperties/not/anyOf/3) | {"required": ["state"]} | existing-native |
| [/properties/assessment/properties/tests/additionalProperties/not/anyOf/4](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/tests/additionalProperties/not/anyOf/4) | {"required": ["states"]} | existing-native |
| [/properties/assessment/properties/tests/additionalProperties/not/anyOf/5](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/tests/additionalProperties/not/anyOf/5) | {"required": ["states_match"]} | existing-native |
| [/properties/assessment/properties/tests/additionalProperties/not/anyOf/6](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/tests/additionalProperties/not/anyOf/6) | {"required": ["state_fields_require"]} | existing-native |
| [/properties/assessment/properties/tests/additionalProperties/allOf/0/if](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/tests/additionalProperties/allOf/0/if) | {"required": ["capability"]} | existing-native |
| [/properties/assessment/properties/tests/additionalProperties/allOf/0/if/properties/capability/not](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/tests/additionalProperties/allOf/0/if/properties/capability/not) | {"const": "independent.unknown"} | existing-native |
| [/properties/assessment/properties/tests/additionalProperties/allOf/0/then](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/tests/additionalProperties/allOf/0/then) | {"required": ["reported_elements"]} | existing-native |
| [/properties/assessment/properties/tests/propertyNames](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/tests/propertyNames) | {"type": "string", "pattern": "^[a-z0-9]+(?:-[a-z0-9]+)*-test$", "maxLength": 64} | existing-native |
| [/properties/assessment/properties/evaluate](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/evaluate) | {} | editorially-approved |

[/properties/assessment/properties/evaluate](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/evaluate): Combines Test and Assessment outcomes using Boolean operators and conditional expressions.

Editorial receipt: editorial-batch.json case 04

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/properties/assessment/properties/procedure](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/procedure) | {"type": "string"} | native-grammar-derived |
| [/properties/assessment/properties/inputs](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/inputs) | {"type": "object"} | existing-native |
| [/properties/assessment/properties/inputs/additionalProperties](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/inputs/additionalProperties) | {"type": "object", "required": ["datatype", "cardinality", "required"], "additionalProperties": false} | existing-native |
| [/properties/assessment/properties/inputs/additionalProperties/properties/cardinality](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/inputs/additionalProperties/properties/cardinality) | {"type": "string", "enum": ["exactly_one", "zero_or_one", "one_or_more", "zero_or_more"]} | editorially-approved |

[/properties/assessment/properties/inputs/additionalProperties/properties/cardinality](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/inputs/additionalProperties/properties/cardinality): Sets how many values a supplied Input may contain.

Editorial receipt: editorial-batch-2.json case 03

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/properties/assessment/properties/inputs/additionalProperties/properties/required](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/inputs/additionalProperties/properties/required) | {"type": "boolean"} | editorially-approved |

[/properties/assessment/properties/inputs/additionalProperties/properties/required](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/inputs/additionalProperties/properties/required): Specifies whether this Input must be supplied.

Editorial receipt: editorial-batch-2.json case 04

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/properties/assessment/properties/inputs/additionalProperties/properties/description](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/inputs/additionalProperties/properties/description) | {"type": ["string", "null"]} | existing-native |
| [/properties/assessment/properties/inputs/additionalProperties/properties/constraints](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/inputs/additionalProperties/properties/constraints) | {"type": "object", "additionalProperties": false} | existing-native |
| [/properties/assessment/properties/inputs/additionalProperties/properties/constraints/properties/allowed](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/inputs/additionalProperties/properties/constraints/properties/allowed) | {"type": "array"} | editorially-approved |

[/properties/assessment/properties/inputs/additionalProperties/properties/constraints/properties/allowed](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/inputs/additionalProperties/properties/constraints/properties/allowed): Lists the permitted values for this Input.

Editorial receipt: editorial-batch-2.json case 05

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/properties/assessment/properties/inputs/additionalProperties/properties/constraints/properties/allowed/items](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/inputs/additionalProperties/properties/constraints/properties/allowed/items) | {"type": ["string", "number", "boolean", "object"]} | existing-native |
| [/properties/assessment/properties/inputs/propertyNames](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/inputs/propertyNames) | {"type": "string", "pattern": "^[a-z0-9]+(?:-[a-z0-9]+)*-input$", "maxLength": 64} | existing-native |
| [/properties/assessment/properties/evidence](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/evidence) | {"type": "array"} | editorially-approved |

[/properties/assessment/properties/evidence](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/evidence): Defines the publisher’s evidence requirements and guidance for this Assessment.

Editorial receipt: editorial-batch-2.json case 28

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/properties/assessment/properties/specification](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/specification) | {"type": "object", "required": ["id", "version"], "additionalProperties": false} | existing-native |
| [/properties/assessment/properties/specification/properties/id](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/specification/properties/id) | {"type": "string", "minLength": 1} | native-grammar-derived |
| [/properties/assessment/properties/specification/properties/version](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/specification/properties/version) | {"const": "0.4.1"} | native-grammar-derived |
| [/properties/assessment/properties/dependencies](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/dependencies) | {"type": "object"} | existing-native |
| [/properties/assessment/properties/dependencies/additionalProperties](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/dependencies/additionalProperties) | {"type": "object", "required": ["assessment", "expected_version"], "additionalProperties": false} | existing-native |
| [/properties/assessment/properties/dependencies/additionalProperties/properties/assessment](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/dependencies/additionalProperties/properties/assessment) | {"type": "string", "minLength": 1} | existing-native |
| [/properties/assessment/properties/dependencies/additionalProperties/properties/expected_id](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/dependencies/additionalProperties/properties/expected_id) | {"type": "string", "minLength": 1} | existing-native |
| [/properties/assessment/properties/dependencies/additionalProperties/properties/expected_version](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/dependencies/additionalProperties/properties/expected_version) | {"type": ["string", "integer"]} | native-structure-derived |
| [/properties/assessment/properties/dependencies/additionalProperties/properties/purpose](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/dependencies/additionalProperties/properties/purpose) | {"enum": ["assessment", "applicability"]} | existing-native |
| [/properties/assessment/properties/dependencies/propertyNames](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/dependencies/propertyNames) | {"type": "string", "minLength": 1, "pattern": "^[a-z0-9]+(?:-[a-z0-9]+)*$", "maxLength": 64} | existing-native |
| [/properties/assessment/properties/applicability](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/applicability) | {} | native-grammar-derived |
| [/properties/assessment/properties/applicability/oneOf/1](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/applicability/oneOf/1) | {"type": "null"} | existing-native |
| [/properties/assessment/properties/response](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/response) | {} | native-grammar-derived |
| [/properties/assessment/properties/references](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/references) | {} | native-grammar-derived |
| [/properties/assessment/properties/evidence_guidance](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/evidence_guidance) | {} | native-grammar-derived |
| [/properties/assessment/properties/shared_objects](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/shared_objects) | {"type": "object"} | existing-native |
| [/properties/assessment/properties/shared_objects/additionalProperties/allOf/1](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/shared_objects/additionalProperties/allOf/1) | {"type": "object", "required": ["object_title", "capability"]} | existing-native |
| [/properties/assessment/properties/shared_objects/additionalProperties/allOf/1/properties/object_title](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/shared_objects/additionalProperties/allOf/1/properties/object_title) | {"type": ["string", "null"]} | existing-native |
| [/properties/assessment/properties/shared_objects/propertyNames](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/shared_objects/propertyNames) | {"type": "string", "pattern": "^[a-z0-9]+(?:-[a-z0-9]+)*-object$", "maxLength": 64} | existing-native |
| [/properties/assessment/allOf/0/if](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/allOf/0/if) | {"required": ["mode"]} | existing-native |
| [/properties/assessment/allOf/0/if/properties/mode](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/allOf/0/if/properties/mode) | {"const": "manual"} | existing-native |
| [/properties/assessment/allOf/1/if](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/allOf/1/if) | {"required": ["mode"]} | existing-native |
| [/properties/assessment/allOf/1/if/properties/mode](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/allOf/1/if/properties/mode) | {"const": "automated"} | existing-native |
| [/properties/assessment/allOf/1/then](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/allOf/1/then) | {"required": ["specification", "tests", "evaluate"]} | existing-native |
| [/properties/assessment/allOf/1/then/properties/version](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/allOf/1/then/properties/version) | {"type": "integer", "minimum": 1} | existing-native |
| [/properties/assessment/allOf/1/then/properties/specification/properties/id](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/allOf/1/then/properties/specification/properties/id) | {"const": "scap-ng.pre-alpha.assessment"} | existing-native |
| [/properties/assessment/allOf/1/then/properties/specification/properties/version](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/allOf/1/then/properties/specification/properties/version) | {"const": "0.4.1"} | existing-native |
| [/properties/assessment/allOf/1/then/not/anyOf/0](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/allOf/1/then/not/anyOf/0) | {"required": ["procedure"]} | existing-native |
| [/properties/assessment/allOf/1/then/not/anyOf/1](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/allOf/1/then/not/anyOf/1) | {"required": ["response"]} | existing-native |
| [/properties/assessment/allOf/1/then/not/anyOf/2](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/allOf/1/then/not/anyOf/2) | {"required": ["references"]} | existing-native |
| [/properties/assessment/allOf/1/then/not/anyOf/3](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/allOf/1/then/not/anyOf/3) | {"required": ["evidence_guidance"]} | existing-native |
