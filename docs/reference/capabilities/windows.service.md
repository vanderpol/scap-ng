# windows.service

Proposed documentation; frozen 0.4.0 validation is unchanged.

The `windows.service` is used to check metadata associated with Windows services.

**Contract status: unresolved.** Service enumeration, status transitions, access failures and multi-value collection behavior require native runtime evidence.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/windows.service.md) retain the validated encodings and any broader schema acceptance.

## Object

The Object is used by `windows.service` to define the specific service(s) to be evaluated.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/windows.service.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/windows.service.schema.json#/$defs/object/properties/filters) |
| `set` | object | 0..1 | Combines Object collections using union, intersection, or difference. | [/$defs/object/properties/set](../../../proposed-schema/documentation/capabilities/windows.service.schema.json#/$defs/object/properties/set) |
| `service_name` | string | 0..1 | Internal service name. | [/$defs/object/properties/service_name](../../../proposed-schema/documentation/capabilities/windows.service.schema.json#/$defs/object/properties/service_name) |

Validation shape: [/$defs/windows_service_object/oneOf/1](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_service_object/oneOf/1).

## Item

This item stores information about Windows services that are present on the system.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `service_name` | string | 0..1 | Internal service name. | [/$defs/meanings/properties/service_name](../../../proposed-schema/documentation/capabilities/windows.service.schema.json#/$defs/meanings/properties/service_name) |
| `display_name` | string | 0..1 | Service display name. | [/$defs/meanings/properties/display_name](../../../proposed-schema/documentation/capabilities/windows.service.schema.json#/$defs/meanings/properties/display_name) |
| `description` | string | 0..1 | Service description. | [/$defs/meanings/properties/description](../../../proposed-schema/documentation/capabilities/windows.service.schema.json#/$defs/meanings/properties/description) |
| `service_type` | string | 0..1 | Service type. | [/$defs/meanings/properties/service_type](../../../proposed-schema/documentation/capabilities/windows.service.schema.json#/$defs/meanings/properties/service_type) |
| `start_type` | string | 0..1 | Configured service startup mode. | [/$defs/meanings/properties/start_type](../../../proposed-schema/documentation/capabilities/windows.service.schema.json#/$defs/meanings/properties/start_type) |
| `current_state` | string | 0..1 | Reported service state. | [/$defs/meanings/properties/current_state](../../../proposed-schema/documentation/capabilities/windows.service.schema.json#/$defs/meanings/properties/current_state) |
| `controls_accepted` | string | 0..1 | Control codes that a service will accept and process. | [/$defs/meanings/properties/controls_accepted](../../../proposed-schema/documentation/capabilities/windows.service.schema.json#/$defs/meanings/properties/controls_accepted) |
| `start_name` | string | 0..1 | Account configured to run the service. | [/$defs/meanings/properties/start_name](../../../proposed-schema/documentation/capabilities/windows.service.schema.json#/$defs/meanings/properties/start_name) |
| `path` | string | 0..1 | Service executable path. | [/$defs/meanings/properties/path](../../../proposed-schema/documentation/capabilities/windows.service.schema.json#/$defs/meanings/properties/path) |
| `pid` | integer | 0..1 | Process ID of the service. | [/$defs/meanings/properties/pid](../../../proposed-schema/documentation/capabilities/windows.service.schema.json#/$defs/meanings/properties/pid) |
| `service_flag` | boolean | 0..1 | Flag indicating whether the service runs in a system process. | [/$defs/meanings/properties/service_flag](../../../proposed-schema/documentation/capabilities/windows.service.schema.json#/$defs/meanings/properties/service_flag) |
| `dependencies` | string | 0..1 | Dependencies of this service on other services. | [/$defs/meanings/properties/dependencies](../../../proposed-schema/documentation/capabilities/windows.service.schema.json#/$defs/meanings/properties/dependencies) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

The comparison fields define the different metadata associated with a Windows service.

This includes the service name, display name, description, type, start type, current state, controls accepted, start name, path, pid, service flag, and dependencies.

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/windows.service.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |

See the [schema](../../../proposed-schema/documentation/capabilities/windows.service.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

## Examples

**Illustrative expected outcomes; native evaluation unverified.** Syntax validation is reported separately from evaluation. For these compliance teaching cases only, technical `true` is labelled Pass and `false` Fail; a consuming Rule defines policy outcomes. Items are explicit synthetic evidence, not observations from a scanned host.

Both cases use this native Test (inline Object and Require):

```yaml
tests:
  windows-service-example-test:
    test_title: Compare the explicitly supplied start_type
    capability: windows.service
    object:
      service_name: {equals: Spooler}
    require:
      item_requirement: {items_found: one_or_more, items_satisfying: every}
      field_requirement: {values_found: one_or_more, values_matching: every}
      fields:
        start_type: {datatype: string, equals: SERVICE_DISABLED}
    reported_elements: all
evaluate: {test: windows-service-example-test}
```

### Pass — expected `true` (unverified)

The supplied start_type is 'SERVICE_DISABLED', so the string equality to "SERVICE_DISABLED" matches; this does not assert whether the service is currently running.

```yaml
collection_result:
  id: windows-service-pass-collection
  capability: windows.service
  status: complete
  item_refs: [windows-service-pass-item]
  logical_complete: true
  population_complete: true
collected_items:
- id: windows-service-pass-item
  capability: windows.service
  status: exists
  fields:
    service_name: {datatype: string, status: exists, value: Spooler}
    start_type: {datatype: string, status: exists, value: SERVICE_DISABLED}
  provenance: {kind: synthetic-documentation-fixture}
```

[Complete version-pinned fixture](../../../examples/paired/v0.4.0/windows.service.pass.yaml).

### Fail — expected `false` (unverified)

The supplied start_type is 'SERVICE_AUTO_START', so the string equality to "SERVICE_DISABLED" does not match; this does not assert whether the service is currently running.

```yaml
collection_result:
  id: windows-service-fail-collection
  capability: windows.service
  status: complete
  item_refs: [windows-service-fail-item]
  logical_complete: true
  population_complete: true
collected_items:
- id: windows-service-fail-item
  capability: windows.service
  status: exists
  fields:
    service_name: {datatype: string, status: exists, value: Spooler}
    start_type: {datatype: string, status: exists, value: SERVICE_AUTO_START}
  provenance: {kind: synthetic-documentation-fixture}
```

[Complete version-pinned fixture](../../../examples/paired/v0.4.0/windows.service.fail.yaml).

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `windows-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
