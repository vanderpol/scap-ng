# ESXi host services — `esx.host_service`

**Status:** draft 0.2.0 structural addition and synthetic examples; no released
live VMware collector. Target one ESXi host, not a VM guest or an unspecified
management-plane population.

## Object and acquisition

The Object requires string predicate `select.service_name`, with explicit
datatype, operation and value. This is the service key, not its display label;
null is invalid. The Test consumes an Object and compatible States. Shared
native Sets/filters and Variable-valued predicates retain typed graph validation.

The source's `Get-VMHostService` example illustrates acquisition; it does not
mandate PowerCLI or arbitrary shell execution. Live fixtures must identify ESXi
version, assessed host, backend and management privileges. Denied acquisition
produces collection error, not a successful empty service population.

## State and Item field reference

All five fields are scalar per Item and available for State comparison.

| Native field | Datatype | Meaning | Source field |
| --- | --- | --- | --- |
| `service_name` | string | Key/name identifying the selected service. | `service_name` |
| `service_label` | string | Descriptive display label. | `service_label` |
| `service_policy` | string | Configured activation policy, independent of running state. | `service_policy` |
| `service_running` | boolean | Whether the service is currently running. | `service_running` |
| `service_required` | boolean | Whether the service is required to run on the host. | `service_required` |

No activation-policy enum is added: the pinned source declares a string.
Required-to-run is distinct from currently running and from the authored State.
Unavailable/error values must not be fabricated as false or empty strings.

## Tests, reporting and examples

[Shared behavior](shared-behavior.md) defines existence, State/Item aggregation,
statuses, redaction and reporting. `reported_elements` defaults to all; compared
or explicit selection retains required identity and decisive evidence. No
result-only resolved-name additions are defined for this capability.

[Standalone content and oracle](../../../tests/esx-host-0.2.0/README.md) require
`TSM-SSH` stopped: recorded false running state satisfies the State; true fails
it. The compared report retains service name and running state. Missing required
service is false; acquisition error is error; uncollected/incomplete empty
populations are unknown; collection N/A propagates. These are synthetic and
shared-table cases, not real VMware acquisition evidence.

## Provenance and gaps

[Mapping](../../../schema/v0.2.0/capability-mappings/experimental/esx.host_service.json)
adapts `host_service_test/object/state/item` from [exact pinned XSDs](../../../third_party/oval-6.0-new-tests/README.md).
Fields follow the declarations; native syntax uses shared NG primitives. Field
descriptions carry into JSON Schema annotations. Existing 5.12.3 behavior is not
replaced by broader OVAL 6.0 differences.

Live service/version/privilege cases, acquisition truth, operation boundaries,
Sets/filters and independent vendor execution remain open in #128/#131.
Classification: Adapted field semantics, Inherited exact source, Common native
guidance/mapping, Evidence/Audit synthetic validation and coverage limits.
