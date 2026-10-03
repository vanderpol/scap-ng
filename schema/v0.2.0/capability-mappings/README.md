# Draft 0.2.0 capability additions

`esx.host_service` and `esx.host_advancedsetting` are reviewed native structural
mappings for newly added OVAL 6.0 Tests. They describe an ESXi **host** target;
VM and management-plane resources are separate upcoming capability groups.

The mappings preserve named Object selectors, State/Item fields, Boolean
service observations, and all simple datatypes/multiple advanced-setting Item
values. They reuse existing shared native primitives. `specification_version`
pins these additions to 0.2.0; they are not inserted into the stable 0.1.0 catalog.

Generate a fragment with `tools/generate_capability_schema.py --mapping <path>
--output <path>`. The 0.2.0 validation harness checks these node contracts even
in skipped branches. Draft reporting/result helpers use the same versioned
registry. Existing JSON mappings remain generator inputs; field descriptions
are carried into the new JSON Schema annotations.

[Known-result content](../../../tests/esx-host-0.2.0/README.md) and [capability
references](../../../specification/assessment/reference/README.md) explain the
source contract and evidence limits. No live collector, mandatory PowerCLI
backend, OVAL 6.0 importer, or finalized 0.2.0 release is claimed.

The next host slice adds `esx.host_account` and `esx.host_vib`. Account shell
access is Boolean; VIB acceptance categories retain their exact five values.
VIB versions and creation dates remain strings. Explicit `item_value_types`
and `item_value_enums` restrict present observed payloads without requiring
payloads for redacted/unavailable entities. Their opt-in generator behavior
does not alter stable mappings. See the linked capability references and
`tools/test_esx_identity_software_v02.py`.

## Host-wide observations

Five more draft mappings cover acceptancelevel, lockdown, ntpserver, coredump
and authentication. `selectorless_object: true` opts into explicit `select: {}`
for source Objects with no selector payload. The generator rejects this flag
for 0.1.0 mappings or source Objects that do declare selector fields. Named
Objects retain shared graph identity. Direct and Set forms are exclusive;
State filtering is expressed by ordinary native Set operands rather than fake
host-name selectors. Invocation/Item provenance identifies the assessed host.

Repeated NTP-server and lockdown-user entities stay arrays. Reviewed categories,
Boolean/integer JSON payloads and redacted/unavailable observations are preserved.
The authentication Item's upstream empty Variable placeholder is documented and
excluded from native observed categories. See `tools/test_esx_hostwide_v02.py`,
linked capability references and `transition/esx-hostwide-2026-10-03.md`.
