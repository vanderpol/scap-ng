# ESXi host coredump — `esx.host_coredump`

**Status:** draft 0.2.0 source-backed representation with synthetic fixtures.

## Object and acquisition

An Object SHALL use explicit `select: {}` to acquire this capability's host-wide
observations within one assessed ESXi host's invocation context. There are no
resource selector fields. The Object remains named/reusable; no host-name field
or scanner-side host discovery is invented. Target identity belongs in execution
context and Item provenance. Denied acquisition is error, never a successful empty
population. Host-wide scope does not require one Item or suppress collection status.

To filter observations, reference this Object from an ordinary native Set operand
with explicit State filters; a single-operand union preserves the filtered result.
This expresses the source Object's filter-only acquisition without fake selectors.
Shared Set/filter status and completeness rules apply. Direct selection and Set
forms are exclusive; `select: null`, invented fields and implicit selection fail.

## State and Item field reference

| Native field | Datatype | Item cardinality | Meaning | Source field |
| --- | --- | --- | --- | --- |
| `enabled` | boolean | scalar | Displays whether or not the ESXi dump collector is enabled for the ESXi host | `enabled` |
| `host_vnic` | string | scalar | The ESXi host's configured core dump destination vnic | `host_vnic` |
| `network_server_ip` | string | scalar | The ESXi host's configured core dump destination IP | `network_server_ip` |
| `network_server_port` | integer | scalar | The ESXi host's configured core dump destination port | `network_server_port` |

The Boolean `enabled`, destination vNIC, IP string and integer port are independent observations. Do not replace disabled with absent, infer delivery success from configuration, reinterpret the IP string as a resolved hostname, or impose an undocumented port range. IP syntax/operation conformance remains a runtime requirement.

## Tests, reporting and examples

[Shared behavior](shared-behavior.md) defines existence, comparison scopes,
collection status, incomplete populations and redaction. Repeated entities SHALL
remain arrays; do not collapse them to a scalar, discard duplicates or confuse
entity match with Test Item match. Unavailable or redacted entities omit values.
Reporting uses recorded field-use lineage and SHALL retain target/invocation
provenance; these host-wide observations have no invented resource-name field.
Domain names, exception accounts and network destinations can be sensitive.

[Standalone Assessment](../../../tests/esx-host-0.2.0/content/coredump.assessment.yaml),
[synthetic Item](../../../tests/esx-host-0.2.0/coredump-item.json) and
[expected results](../../../tests/esx-host-0.2.0/expected-results/hostwide.json)
exercise equality against `true`.
The fixture is a narrow illustration, not a universal STIG policy or live probe.

## Provenance and gaps

[Mapping](../../../schema/v0.2.0/capability-mappings/esx.host_coredump.json) adapts the
new `host_coredump_test/object/state/item` contract from [pinned licensed OVAL 6.0
sources](../../../third_party/oval-6.0-new-tests/README.md). Existing 5.12.3
contracts remain the baseline. Classification: Inherited sources; Adapted fields,
categories and cardinality; Common native syntax; Evidence/Audit fixtures.

Live host/version/privilege acquisition, operation boundaries, Variable resolution,
filter evaluation and independent vendor conformance remain #128/#131. Schema,
graph and unsigned compilation tests do not establish runtime equivalence.
