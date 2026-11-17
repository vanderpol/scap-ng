# SCAP-NG package manifest v0.4.1 — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/package-manifest.schema.json#) | {"type": "object", "required": ["format", "format_version", "benchmark_id", "benchmark_version", "entrypoint", "objects", "integrity", "build_provenance", "signature"], "additionalProperties": false} | existing-native |
| [/properties/format](../../../proposed-schema/documentation/package-manifest.schema.json#/properties/format) | {"const": "scap-ng-package-manifest"} | native-structure-derived |
| [/properties/format_version](../../../proposed-schema/documentation/package-manifest.schema.json#/properties/format_version) | {"type": "string", "minLength": 1} | native-structure-derived |
| [/properties/benchmark_id](../../../proposed-schema/documentation/package-manifest.schema.json#/properties/benchmark_id) | {"type": "string", "minLength": 1} | native-structure-derived |
| [/properties/benchmark_version](../../../proposed-schema/documentation/package-manifest.schema.json#/properties/benchmark_version) | {} | native-structure-derived |
| [/properties/entrypoint](../../../proposed-schema/documentation/package-manifest.schema.json#/properties/entrypoint) | {"type": "string", "minLength": 1} | existing-native |
| [/properties/objects](../../../proposed-schema/documentation/package-manifest.schema.json#/properties/objects) | {"type": "object", "minProperties": 1} | native-structure-derived |
| [/properties/objects/propertyNames](../../../proposed-schema/documentation/package-manifest.schema.json#/properties/objects/propertyNames) | {"type": "string", "minLength": 1} | existing-native |
| [/properties/integrity](../../../proposed-schema/documentation/package-manifest.schema.json#/properties/integrity) | {} | native-structure-derived |
| [/properties/build_provenance](../../../proposed-schema/documentation/package-manifest.schema.json#/properties/build_provenance) | {"type": "object"} | native-structure-derived |
| [/properties/signature](../../../proposed-schema/documentation/package-manifest.schema.json#/properties/signature) | {} | native-structure-derived |
| [/$defs/object_record](../../../proposed-schema/documentation/package-manifest.schema.json#/$defs/object_record) | {"type": "object", "required": ["type", "version", "path", "sha256", "size"], "additionalProperties": false} | native-structure-derived |
| [/$defs/object_record/properties/type](../../../proposed-schema/documentation/package-manifest.schema.json#/$defs/object_record/properties/type) | {"enum": ["benchmark", "rule", "assessment", "applicability_catalog"]} | native-structure-derived |
| [/$defs/object_record/properties/version](../../../proposed-schema/documentation/package-manifest.schema.json#/$defs/object_record/properties/version) | {} | native-structure-derived |
| [/$defs/object_record/properties/path](../../../proposed-schema/documentation/package-manifest.schema.json#/$defs/object_record/properties/path) | {"type": "string", "minLength": 1, "maxLength": 160, "pattern": "^(?!/)(?!.*(?:^\|/)\\.\\.(?:/\|$))(?![A-Za-z]:)[^\\\\]+$"} | native-structure-derived |
| [/$defs/object_record/properties/sha256](../../../proposed-schema/documentation/package-manifest.schema.json#/$defs/object_record/properties/sha256) | {"type": "string", "pattern": "^[0-9a-f]{64}$"} | native-structure-derived |
| [/$defs/object_record/properties/size](../../../proposed-schema/documentation/package-manifest.schema.json#/$defs/object_record/properties/size) | {"type": "integer", "minimum": 0} | existing-native |
| [/$defs/integrity](../../../proposed-schema/documentation/package-manifest.schema.json#/$defs/integrity) | {"type": "object", "required": ["algorithm", "unexpected_members"], "additionalProperties": false} | native-structure-derived |
| [/$defs/integrity/properties/algorithm](../../../proposed-schema/documentation/package-manifest.schema.json#/$defs/integrity/properties/algorithm) | {"const": "sha-256"} | native-structure-derived |
| [/$defs/integrity/properties/unexpected_members](../../../proposed-schema/documentation/package-manifest.schema.json#/$defs/integrity/properties/unexpected_members) | {"const": "reject"} | native-structure-derived |
| [/$defs/signature](../../../proposed-schema/documentation/package-manifest.schema.json#/$defs/signature) | {"type": "object", "required": ["format", "path", "certificate_path", "trust"], "additionalProperties": false} | native-structure-derived |
| [/$defs/signature/properties/format](../../../proposed-schema/documentation/package-manifest.schema.json#/$defs/signature/properties/format) | {"type": ["string", "null"]} | native-structure-derived |
| [/$defs/signature/properties/path](../../../proposed-schema/documentation/package-manifest.schema.json#/$defs/signature/properties/path) | {"type": ["string", "null"]} | native-structure-derived |
| [/$defs/signature/properties/certificate_path](../../../proposed-schema/documentation/package-manifest.schema.json#/$defs/signature/properties/certificate_path) | {"type": ["string", "null"]} | existing-native |
| [/$defs/signature/properties/trust](../../../proposed-schema/documentation/package-manifest.schema.json#/$defs/signature/properties/trust) | {"type": ["string", "null"]} | native-structure-derived |
| [/$defs/signature/allOf/0/if](../../../proposed-schema/documentation/package-manifest.schema.json#/$defs/signature/allOf/0/if) | {"required": ["format"]} | existing-native |
| [/$defs/signature/allOf/0/if/properties/format](../../../proposed-schema/documentation/package-manifest.schema.json#/$defs/signature/allOf/0/if/properties/format) | {"type": "string"} | existing-native |
| [/$defs/signature/allOf/0/then/properties/format](../../../proposed-schema/documentation/package-manifest.schema.json#/$defs/signature/allOf/0/then/properties/format) | {"const": "cms-detached-der"} | existing-native |
| [/$defs/signature/allOf/0/then/properties/path](../../../proposed-schema/documentation/package-manifest.schema.json#/$defs/signature/allOf/0/then/properties/path) | {"type": "string", "minLength": 1} | existing-native |
| [/$defs/signature/allOf/0/then/properties/certificate_path](../../../proposed-schema/documentation/package-manifest.schema.json#/$defs/signature/allOf/0/then/properties/certificate_path) | {"type": "string", "minLength": 1} | existing-native |
| [/$defs/signature/allOf/0/then/properties/trust](../../../proposed-schema/documentation/package-manifest.schema.json#/$defs/signature/allOf/0/then/properties/trust) | {"type": "string", "minLength": 1} | existing-native |
| [/$defs/signature/allOf/1/if](../../../proposed-schema/documentation/package-manifest.schema.json#/$defs/signature/allOf/1/if) | {"required": ["format"]} | existing-native |
| [/$defs/signature/allOf/1/if/properties/format](../../../proposed-schema/documentation/package-manifest.schema.json#/$defs/signature/allOf/1/if/properties/format) | {"type": "null"} | existing-native |
| [/$defs/signature/allOf/1/then/properties/path](../../../proposed-schema/documentation/package-manifest.schema.json#/$defs/signature/allOf/1/then/properties/path) | {"type": "null"} | existing-native |
| [/$defs/signature/allOf/1/then/properties/certificate_path](../../../proposed-schema/documentation/package-manifest.schema.json#/$defs/signature/allOf/1/then/properties/certificate_path) | {"type": "null"} | existing-native |
| [/$defs/signature/allOf/1/then/properties/trust](../../../proposed-schema/documentation/package-manifest.schema.json#/$defs/signature/allOf/1/then/properties/trust) | {"type": "null"} | existing-native |
