# SCAP-NG package manifest v0.4.1

Proposed documentation. Defaults are schema annotations, not inferred scanner fallbacks. Conditional requirements and alternatives remain linked in the schema.

Pre-alpha manifest for the SCAP-NG logical object graph. Container member paths are storage bindings only; logical IDs are authoritative.

## `/`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `format` | string | 1..1 (required) | Discriminator identifying the SCAP-NG package-manifest format. | [/properties/format](../../../proposed-schema/documentation/package-manifest.schema.json#/properties/format) |
| `format_version` | string | 1..1 (required) | Version label of the package-manifest format. | [/properties/format_version](../../../proposed-schema/documentation/package-manifest.schema.json#/properties/format_version) |
| `benchmark_id` | string | 1..1 (required) | Logical identifier of the package Benchmark. | [/properties/benchmark_id](../../../proposed-schema/documentation/package-manifest.schema.json#/properties/benchmark_id) |
| `benchmark_version` | See schema | 1..1 (required) | Version recorded for the package Benchmark. | [/properties/benchmark_version](../../../proposed-schema/documentation/package-manifest.schema.json#/properties/benchmark_version) |
| `entrypoint` | string | 1..1 (required) | **Unresolved description** | [/properties/entrypoint](../../../proposed-schema/documentation/package-manifest.schema.json#/properties/entrypoint) |
| `objects` | object | 1..1 (required) | Packaged document members, keyed by their logical identifiers. | [/properties/objects](../../../proposed-schema/documentation/package-manifest.schema.json#/properties/objects) |
| `integrity` | object | 1..1 (required) | Digest-algorithm and container-membership policy declarations. | [/properties/integrity](../../../proposed-schema/documentation/package-manifest.schema.json#/properties/integrity) |
| `build_provenance` | object | 1..1 (required) | Provenance metadata describing creation of the package. | [/properties/build_provenance](../../../proposed-schema/documentation/package-manifest.schema.json#/properties/build_provenance) |
| `signature` | object | 1..1 (required) | Detached-signature metadata carried by the package manifest. | [/properties/signature](../../../proposed-schema/documentation/package-manifest.schema.json#/properties/signature) |
| `object_record` | object | Definition | Metadata binding a logical document to a stored package member. | [/$defs/object_record](../../../proposed-schema/documentation/package-manifest.schema.json#/$defs/object_record) |
| `integrity` | object | Definition | Integrity policy declarations carried by the package manifest. | [/$defs/integrity](../../../proposed-schema/documentation/package-manifest.schema.json#/$defs/integrity) |
| `signature` | object | Definition | Format, location and trust-policy labels for the package signature. | [/$defs/signature](../../../proposed-schema/documentation/package-manifest.schema.json#/$defs/signature) |

## `/$defs/object_record`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `type` | string | 1..1 (required) | Kind of SCAP-NG document stored in this member. | [/$defs/object_record/properties/type](../../../proposed-schema/documentation/package-manifest.schema.json#/$defs/object_record/properties/type) |
| `version` | See schema | 1..1 (required) | Logical version recorded for the packaged document. | [/$defs/object_record/properties/version](../../../proposed-schema/documentation/package-manifest.schema.json#/$defs/object_record/properties/version) |
| `path` | string | 1..1 (required) | Path recorded for this package member. | [/$defs/object_record/properties/path](../../../proposed-schema/documentation/package-manifest.schema.json#/$defs/object_record/properties/path) |
| `sha256` | string | 1..1 (required) | SHA-256 digest declared for this member. | [/$defs/object_record/properties/sha256](../../../proposed-schema/documentation/package-manifest.schema.json#/$defs/object_record/properties/sha256) |
| `size` | integer | 1..1 (required) | **Unresolved description** | [/$defs/object_record/properties/size](../../../proposed-schema/documentation/package-manifest.schema.json#/$defs/object_record/properties/size) |

## `/$defs/integrity`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `algorithm` | string | 1..1 (required) | Digest algorithm declared for package integrity metadata. | [/$defs/integrity/properties/algorithm](../../../proposed-schema/documentation/package-manifest.schema.json#/$defs/integrity/properties/algorithm) |
| `unexpected_members` | string | 1..1 (required) | Policy marker for container members absent from the manifest inventory. | [/$defs/integrity/properties/unexpected_members](../../../proposed-schema/documentation/package-manifest.schema.json#/$defs/integrity/properties/unexpected_members) |

## `/$defs/signature`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `format` | null, string | 1..1 (required) | Format label of the detached-signature metadata. | [/$defs/signature/properties/format](../../../proposed-schema/documentation/package-manifest.schema.json#/$defs/signature/properties/format) |
| `path` | null, string | 1..1 (required) | Location recorded for the detached signature. | [/$defs/signature/properties/path](../../../proposed-schema/documentation/package-manifest.schema.json#/$defs/signature/properties/path) |
| `certificate_path` | null, string | 1..1 (required) | Path to the referenced certificate. | [/$defs/signature/properties/certificate_path](../../../proposed-schema/documentation/package-manifest.schema.json#/$defs/signature/properties/certificate_path) |
| `trust` | null, string | 1..1 (required) | Trust-policy label carried with the signature metadata. | [/$defs/signature/properties/trust](../../../proposed-schema/documentation/package-manifest.schema.json#/$defs/signature/properties/trust) |

## Advanced constraints

[Local constraints](../advanced/package-manifest.md) and [complete JSON Schema](../../../proposed-schema/documentation/package-manifest.schema.json) contain conditional requirements, alternatives, bounds and validation expressions. A mapping property occurs at most once; `items`, `minItems` and `maxItems` constrain array members separately. A definition is reusable schema grammar, not itself an authored mapping key.
