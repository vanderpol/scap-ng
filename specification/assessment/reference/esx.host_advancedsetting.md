# ESXi host advanced settings — `esx.host_advancedsetting`

**Status:** draft 0.2.0 structural addition and synthetic known results; no live
VMware collector. Target an ESXi host. VM settings have separate upcoming
target identity and inherited contracts.

## Object and acquisition

The Object requires string predicate `select.advanced_setting_name`, with
explicit datatype, operation and value. Null is invalid. The name identifies
a host setting, not a VM or command. Tests reference compatible Objects/States;
shared typed Variable predicates and native Set/filter composition apply.

`Get-AdvancedSetting` in source documentation is illustrative, not a required
PowerCLI backend. Live fixtures must specify ESXi version, assessed host,
management access/privileges, setting availability and acquisition method.
Missing named setting, failed acquisition, unavailable value and unfinished
population are distinct statuses.

## State and Item field reference

| Native field | Datatypes | Cardinality and meaning | Source field |
| --- | --- | --- | --- |
| `advanced_setting_name` | string | Scalar identity/name of the setting. | `advanced_setting_name` |
| `advanced_setting_value` | string, boolean, integer, float, binary, version, ipv4, ipv6, rpm_evr, debian_evr, fileset_revision, ios_version | Item array of typed values; every observed occurrence is retained. | `advanced_setting_value` |

The pinned State is AnySimple; the Item permits repeated AnySimple entities.
Preserve actual types and occurrences. Entity `match` combines corresponding
values within an Item; Test `match` combines different Items. Do not substitute
one scope for the other. Structured record is outside this reviewed simple-value
set. Type validity does not authorize meaningless datatype/operation combinations.

Absence is not an empty string, zero or false. Typed statuses, Variable references,
aggregation and redaction follow [shared behavior](shared-behavior.md). Complete
zero-value comparison/platform cases still require independent execution oracles;
XML cardinality alone does not define every outcome.

## Tests, reporting and examples

[Content and oracle](../../../tests/esx-host-0.2.0/README.md) select
`UserVars.ESXiShellTimeOut`, require integer 600 and compare synthetic 600
(true) and 300 (false). Observed values 600 and 300 under entity `match: all`
must not collapse to the matching first value. The report retains setting name
and value; requested repeated redacted values remain redacted.

`reported_elements` defaults to all and supports compared/explicit fields.
No resolved-name extensions are defined here. Shared collection/status rules
apply; denied API access is not successful empty collection. These cases do not
implement every State operation or query VMware.

## Provenance and gaps

[Mapping](../../../schema/v0.2.0/capability-mappings/esx.host_advancedsetting.json)
adapts `host_advancedsetting_test/object/state/item` from [pinned XSDs](../../../third_party/oval-6.0-new-tests/README.md).
Some source prose says `host_advancedconfig`, but the declared global names are
`host_advancedsetting`; native identity follows the declarations. Field
explanations carry into JSON Schema annotations.

Live typed settings, multiplicity/absence boundaries, version availability,
privilege failures, filters/Sets and independent vendor behavior remain in
#128/#131. Classification: Adapted source semantics, Inherited exact source,
Common native mapping/descriptions, Evidence/Audit synthetic cases and limits.
