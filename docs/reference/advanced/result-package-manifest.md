# Draft unsigned result-package integrity manifest — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/result-package-manifest.schema.json#) | {"type": "object", "required": ["format_version", "result_schema_version", "digest_algorithm", "signature_status", "run_id", "scan_result_ref", "members", "evaluation_groups"], "additionalProperties": false} | native-structure-derived |
| [/properties/format_version](../../../proposed-schema/documentation/result-package-manifest.schema.json#/properties/format_version) | {"const": "scap-ng.result-package.draft-1"} | native-structure-derived |
| [/properties/result_schema_version](../../../proposed-schema/documentation/result-package-manifest.schema.json#/properties/result_schema_version) | {"const": "0.4.0"} | existing-native |
| [/properties/digest_algorithm](../../../proposed-schema/documentation/result-package-manifest.schema.json#/properties/digest_algorithm) | {"const": "sha256"} | native-structure-derived |
| [/properties/signature_status](../../../proposed-schema/documentation/result-package-manifest.schema.json#/properties/signature_status) | {"const": "unsigned"} | native-structure-derived |
| [/properties/run_id](../../../proposed-schema/documentation/result-package-manifest.schema.json#/properties/run_id) | {"type": "string", "minLength": 1} | existing-native |
| [/properties/scan_result_ref](../../../proposed-schema/documentation/result-package-manifest.schema.json#/properties/scan_result_ref) | {"type": "string", "minLength": 1} | native-structure-derived |
| [/properties/members](../../../proposed-schema/documentation/result-package-manifest.schema.json#/properties/members) | {"type": "array", "minItems": 2} | native-structure-derived |
| [/properties/members/items](../../../proposed-schema/documentation/result-package-manifest.schema.json#/properties/members/items) | {"type": "object", "required": ["id", "kind", "path", "sha256", "size", "schema_version"], "additionalProperties": false} | existing-native |
| [/properties/members/items/properties/id](../../../proposed-schema/documentation/result-package-manifest.schema.json#/properties/members/items/properties/id) | {"type": "string", "minLength": 1} | native-structure-derived |
| [/properties/members/items/properties/kind](../../../proposed-schema/documentation/result-package-manifest.schema.json#/properties/members/items/properties/kind) | {"enum": ["scan_result", "benchmark_result", "assessment_result"]} | native-structure-derived |
| [/properties/members/items/properties/path](../../../proposed-schema/documentation/result-package-manifest.schema.json#/properties/members/items/properties/path) | {"type": "string", "minLength": 1} | native-structure-derived |
| [/properties/members/items/properties/sha256](../../../proposed-schema/documentation/result-package-manifest.schema.json#/properties/members/items/properties/sha256) | {"type": "string", "pattern": "^[0-9a-f]{64}$"} | native-structure-derived |
| [/properties/members/items/properties/size](../../../proposed-schema/documentation/result-package-manifest.schema.json#/properties/members/items/properties/size) | {"type": "integer", "minimum": 0} | existing-native |
| [/properties/members/items/properties/schema_version](../../../proposed-schema/documentation/result-package-manifest.schema.json#/properties/members/items/properties/schema_version) | {"const": "0.4.0"} | native-structure-derived |
| [/properties/evaluation_groups](../../../proposed-schema/documentation/result-package-manifest.schema.json#/properties/evaluation_groups) | {"type": "array"} | native-structure-derived |
| [/properties/evaluation_groups/items](../../../proposed-schema/documentation/result-package-manifest.schema.json#/properties/evaluation_groups/items) | {"type": "object", "required": ["entry_execution_id", "target_ref", "execution_ids"], "additionalProperties": false} | existing-native |
| [/properties/evaluation_groups/items/properties/entry_execution_id](../../../proposed-schema/documentation/result-package-manifest.schema.json#/properties/evaluation_groups/items/properties/entry_execution_id) | {"type": "string", "minLength": 1} | native-structure-derived |
| [/properties/evaluation_groups/items/properties/target_ref](../../../proposed-schema/documentation/result-package-manifest.schema.json#/properties/evaluation_groups/items/properties/target_ref) | {"type": "string", "minLength": 1} | existing-native |
| [/properties/evaluation_groups/items/properties/execution_ids](../../../proposed-schema/documentation/result-package-manifest.schema.json#/properties/evaluation_groups/items/properties/execution_ids) | {"type": "array", "minItems": 1} | native-structure-derived |
| [/properties/evaluation_groups/items/properties/execution_ids/items](../../../proposed-schema/documentation/result-package-manifest.schema.json#/properties/evaluation_groups/items/properties/execution_ids/items) | {"type": "string", "minLength": 1} | existing-native |
