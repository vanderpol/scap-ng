# ESXi host authentication — `esx.host_authentication`

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
| `domain` | string | scalar | The name of the domain | `domain` |
| `domain_membership_status` | string | scalar | The status of the ESXi host's membership in the domain | `domain_membership_status` |

The seven membership categories are case-sensitive: `ClientTrustBroken`, `InconsistentTrust`, `NoServers`, `Ok`, `OtherProblem`, `ServerTrustBroken`, `Unknown`. `Unknown` is a recorded category, not a technical result. The upstream Item type includes an empty placeholder described as supporting Variable references. Native observed values have no Variable-reference indirection: this placeholder is excluded from the reviewed native category domain, documented as a source anomaly; missing or unavailable observations use status. No upstream bytes are changed.

## Tests, reporting and examples

[Shared behavior](shared-behavior.md) defines existence, comparison scopes,
collection status, incomplete populations and redaction. Repeated entities SHALL
remain arrays; do not collapse them to a scalar, discard duplicates or confuse
entity match with Test Item match. Unavailable or redacted entities omit values.
Reporting uses recorded field-use lineage and SHALL retain target/invocation
provenance; these host-wide observations have no invented resource-name field.
Domain names, exception accounts and network destinations can be sensitive.

[Standalone Assessment](../../../tests/esx-host-0.2.0/content/authentication.assessment.yaml),
[synthetic Item](../../../tests/esx-host-0.2.0/authentication-item.json) and
[expected results](../../../tests/esx-host-0.2.0/expected-results/hostwide.json)
exercise equality against `Ok`.
The fixture is a narrow illustration, not a universal STIG policy or live probe.

## Provenance and gaps

[Mapping](../../../schema/v0.2.0/capability-mappings/esx.host_authentication.json) adapts the
new `host_authentication_test/object/state/item` contract from [pinned licensed OVAL 6.0
sources](../../../third_party/oval-6.0-new-tests/README.md). Existing 5.12.3
contracts remain the baseline. Classification: Inherited sources; Adapted fields,
categories and cardinality; Common native syntax; Evidence/Audit fixtures.

Live host/version/privilege acquisition, operation boundaries, Variable resolution,
filter evaluation and independent vendor conformance remain #128/#131. Schema,
graph and unsigned compilation tests do not establish runtime equivalence.
