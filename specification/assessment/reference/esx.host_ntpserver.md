# ESXi host ntpserver — `esx.host_ntpserver`

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
| `ntp_server_name` | string | repeated | The domain name or the IP address of the NTP server(s) added to the host | `ntp_server_name` |

`ntp_server_name` is an array of configured names or addresses, preserving occurrences. These strings describe configuration, not DNS resolution, reachability, clock accuracy, or whether the NTP service runs. Predicate `match: all` requires every recorded server name to meet the stated condition; `any` has a different meaning.

## Tests, reporting and examples

[Shared behavior](shared-behavior.md) defines existence, comparison scopes,
collection status, incomplete populations and redaction. Repeated entities SHALL
remain arrays; do not collapse them to a scalar, discard duplicates or confuse
entity match with Test Item match. Unavailable or redacted entities omit values.
Reporting uses recorded field-use lineage and SHALL retain target/invocation
provenance; these host-wide observations have no invented resource-name field.
Domain names, exception accounts and network destinations can be sensitive.

[Standalone Assessment](../../../tests/esx-host-0.2.0/content/ntpserver.assessment.yaml),
[synthetic Item](../../../tests/esx-host-0.2.0/ntpserver-item.json) and
[expected results](../../../tests/esx-host-0.2.0/expected-results/hostwide.json)
exercise equality against `time.example.test`.
The fixture is a narrow illustration, not a universal STIG policy or live probe.

## Provenance and gaps

[Mapping](../../../schema/v0.2.0/capability-mappings/esx.host_ntpserver.json) adapts the
new `host_ntpserver_test/object/state/item` contract from [pinned licensed OVAL 6.0
sources](../../../third_party/oval-6.0-new-tests/README.md). Existing 5.12.3
contracts remain the baseline. Classification: Inherited sources; Adapted fields,
categories and cardinality; Common native syntax; Evidence/Audit fixtures.

Live host/version/privilege acquisition, operation boundaries, Variable resolution,
filter evaluation and independent vendor conformance remain #128/#131. Schema,
graph and unsigned compilation tests do not establish runtime equivalence.
