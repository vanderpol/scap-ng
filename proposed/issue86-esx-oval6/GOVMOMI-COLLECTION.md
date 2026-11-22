# Proposed govmomi collection requirements (Issue #86)

This is an RI handoff design, not an implementation or execution receipt.
The RI must use native Go `govmomi` APIs and must not invoke PowerCLI, shell
commands, or STIG-specific branches. `vcsim` fixtures are suitable for
planner/serialization tests; real ESXi/vCenter qualification requires an
authorized environment and a receipt that reports privileges, API version,
managed-object identity, and evidence completeness.

## Shared requirements

1. Connect to an explicitly authorized vCenter or ESXi endpoint with TLS and
   credential provenance recorded. Never infer host identity from a STIG ID.
2. Resolve `HostSystem`, `VirtualMachine`, `ServiceSystem`, `OptionManager`,
   `HostNetworkSystem`, `HostFirewallSystem`, `HostStorageSystem`, and
   distributed-switch managed objects through the PropertyCollector. Preserve
   per-target identity and return `UNKNOWN`/`ERROR` for missing, denied, stale,
   or partial properties; do not fabricate empty Items.
3. Build one generic gatherer per XSD-derived capability. A Rule/Assessment
   supplies selectors and Require predicates; it does not alter the gatherer.
4. Report the selected Object, returned Item fields, API/property paths,
   privilege checks, server/SDK versions, collection status, and completeness
   separately. A successful API call is not proof that the population is
   complete.
5. Bound paging, traversal, retries, concurrency, and cancellation. Record
   limits and truncation as explicit status/provenance rather than pass.

## XSD family to govmomi requirement matrix

| XSD family | Generic govmomi source / operation | Main evidence concerns |
| --- | --- | --- |
| `host_acceptancelevel` | `HostSystem` + `HostEsxAgentHostManager`/ESXCLI-backed supported API for image acceptance level | API availability and host privilege; no fake singleton Item |
| `host_vib` | `HostSystem.ConfigManager.SoftwareSystem` / image profile and VIB metadata | VIB population completeness and acceptance enum |
| `host_module` | Host configuration/module inventory exposed by the supported SDK endpoint | Module visibility and version typing |
| `host_coredump` | `HostSystem.ConfigManager.DiagnosticSystem` and coredump configuration | Active target, enabled state, network target, and privilege failures |
| `host_webserverssl` | `HostSystem.ConfigManager` security/web configuration properties | Version-dependent property paths; unsupported fields explicit |
| `host_authentication` | `HostSystem.ConfigManager.AuthenticationManager` and directory-service configuration | AD/proxy state, secret redaction, permission boundaries |
| `host_account` | `HostSystem.ConfigManager.AccountManager` account list and account metadata | No password collection; local-account scope and partial visibility |
| `host_advancedsetting` | `HostSystem.ConfigManager.AdvancedOption` / `OptionManager.QueryOptions` and `UpdateOptions`-compatible read path | Preserve repeated/typed option values; distinguish absent option from denied access |
| `host_service` | `HostSystem.Config.Service.ServiceInfo` / `HostServiceSystem.ServiceInfo` | `service_policy`, running, required, label and key must come from one coherent snapshot |
| `host_ntpserver` | `HostSystem.ConfigManager.DateTimeSystem` and NTP configuration | Server list, service policy, running status, and unsupported direct-host behavior |
| `host_lockdown` | `HostSystem.ConfigManager.HostAccessManager` lockdown mode and exception data | Normal/strict/disabled semantics and stale vCenter state |
| `host_firewallexception` | `HostSystem.ConfigManager.FirewallSystem.FirewallInfo.Ruleset` | Rule direction, ports, protocol, enabled state, allowed-host scope |
| `host_busadapter` | `HostSystem.Config.StorageDevice.HostBusAdapter` | Adapter type, identity, and inventory completeness |
| `host_vswitchpolicy` | `HostSystem.ConfigManager.NetworkSystem.NetworkInfo.Vswitch` | Per-vSwitch policy snapshot and default/override distinctions |
| `vm_advancedsetting` | `VirtualMachine.ConfigManager.AdvancedOption` / VM `OptionManager` | VM power/state and per-VM option identity |
| `vm_device` | `VirtualMachine.Config.Hardware.Device` | Device type, backing, connection state, and nested record preservation |
| `vm_harddiskdevice` | `VirtualMachine.Config.Hardware.Device` filtered to virtual disks | Disk backing, persistence, controller identity, and redaction |
| `host_portgroup` | `HostSystem.ConfigManager.NetworkSystem.NetworkInfo.Portgroup` | Port-group policy and host association |
| `vds` | `DistributedVirtualSwitch` configuration and runtime network properties | vCenter-only scope and version-specific fields |
| `vds_portgroup` | `DistributedVirtualPortgroup` configuration/policy | Port-group membership, policy inheritance, and vCenter privilege |

The matrix names API/property areas intentionally rather than prescribing one
implementation call sequence. The RI must pin the govmomi/VI API versions it
supports and attach a focused issue for any unavailable property.

## Initial RI #202 handoff

The first bounded demonstration should implement a generic
`host_advancedsetting` gatherer against `vcsim`, then qualify
`host_service` if the simulator exposes the required service properties. The
Assessment examples and fixtures in this directory are the portable contract;
this repository does not embed an evaluator or scanner receipt.
