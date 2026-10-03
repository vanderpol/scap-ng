# Capability coverage and new OVAL 6.0 tests

Provenance: **Evidence/Audit** of the owner-scoped review; **Adapted** upstream schema metadata with source pins; **Common** inventory tools and regressions. This is development evidence outside the active reviewer packet. No native schema, collector, conversion behavior or historical review tree is changed.

## Scope and sources

SCAP-NG replaces OVAL 6.0. The owner narrowed this comparison to new 6.0 tests and their associated Object/State/Item contracts. Existing-test/core/result/namespace/encapsulated-definition differences are excluded. Keep 5.12.3 fixes that have not been ported to 6.0. A new native capability does not imply an OVAL 6.0 ingestion feature. Effective deprecated predecessors remain excluded; registry view stays excluded.

[Source pins](source-pins.json) bind the current repository baseline and OVAL v6.0 commit. [The machine-readable new-test inventory](oval-new-tests.json) includes every newly added Test name, associated field/cardinality/type constraints, inherited contracts and embedded assertions. The comparison scans all definition families; only ESX and Kubernetes add Test names. Inheritance is linked to shared qualified types, so VM/device fields are not lost. Choice/sequence structure and group references remain explicit; this inventory is not an automatically lowered native schema.

## Current mapped capability coverage

All **100** current authoring mappings generate meta-valid schemas; **99** have generated draft Item contracts (the unknown Test has no collected Item). Only **2** capabilities have standalone Assessment content under tests/: unix.file and variable.value, both with partial feature oracles. **98** lack standalone Assessment content there. Four capabilities have explicit collected-Item validity cases. These narrow fixtures do not cover every field, collection failure, State operation or platform behavior.

[The per-capability matrix](current-mappings.json) links mappings, standalone content, Item cases and maintained-test reference candidates. Static test-string matches require method-level review; lack of a static match does not prove no dynamic test exists. Dated census mentions are migration leads, not per-capability round-trip proof. No current mapping has demonstrated collector/target execution in this inventory. #128 remains open for exhaustive vendor content.

| Capability | Standalone Assessment content | Item validity cases | Maintained test reference candidates |
| --- | --- | ---: | ---: |
| `aix.fileset` | Missing | 0 | 0 |
| `aix.fix` | Missing | 0 | 0 |
| `asa.line` | Missing | 0 | 0 |
| `asa.version` | Missing | 0 | 1 |
| `file.hash` | Missing | 0 | 3 |
| `independent.environmentvariable58` | Missing | 0 | 1 |
| `independent.family` | Missing | 0 | 1 |
| `independent.shellcommand` | Missing | 0 | 1 |
| `independent.sql512` | Missing | 0 | 0 |
| `independent.textfilecontent54` | Missing | 1 | 5 |
| `independent.unknown` | Missing | 0 | 1 |
| `independent.xmlfilecontent` | Missing | 0 | 1 |
| `independent.yamlfilecontent` | Missing | 0 | 1 |
| `ios.bgpneighbor` | Missing | 0 | 0 |
| `ios.global` | Missing | 0 | 0 |
| `ios.interface` | Missing | 0 | 0 |
| `ios.line` | Missing | 0 | 0 |
| `ios.routingprotocolauthintf` | Missing | 0 | 0 |
| `ios.section` | Missing | 0 | 0 |
| `ios.snmpcommunity` | Missing | 0 | 0 |
| `ios.snmpgroup` | Missing | 0 | 0 |
| `ios.snmphost` | Missing | 0 | 0 |
| `ios.snmpuser` | Missing | 0 | 0 |
| `iosxe.bgpneighbor` | Missing | 0 | 0 |
| `iosxe.global` | Missing | 0 | 0 |
| `iosxe.interface` | Missing | 0 | 0 |
| `iosxe.line` | Missing | 0 | 0 |
| `iosxe.routingprotocolauthintf` | Missing | 0 | 0 |
| `iosxe.section` | Missing | 0 | 0 |
| `iosxe.snmpcommunity` | Missing | 0 | 0 |
| `iosxe.snmpgroup` | Missing | 0 | 0 |
| `iosxe.snmphost` | Missing | 0 | 0 |
| `iosxe.snmpuser` | Missing | 0 | 0 |
| `iosxe.version` | Missing | 0 | 1 |
| `junos.show` | Missing | 0 | 0 |
| `linux.apparmorstatus` | Missing | 0 | 0 |
| `linux.dpkginfo` | Missing | 0 | 0 |
| `linux.inetlisteningservers` | Missing | 0 | 0 |
| `linux.kernelmodule` | Missing | 0 | 0 |
| `linux.partition` | Missing | 0 | 0 |
| `linux.rpminfo` | Missing | 0 | 2 |
| `linux.rpmverifyfile` | Missing | 0 | 3 |
| `linux.rpmverifypackage` | Missing | 0 | 2 |
| `linux.selinuxboolean` | Missing | 0 | 0 |
| `linux.selinuxsecuritycontext` | Missing | 0 | 1 |
| `linux.sestatus` | Missing | 0 | 0 |
| `linux.systemdunitdependency` | Missing | 0 | 0 |
| `linux.systemdunitproperty` | Missing | 0 | 1 |
| `macos.accountinfo` | Missing | 0 | 0 |
| `macos.authorizationdb` | Missing | 0 | 0 |
| `macos.disabledservice` | Missing | 0 | 1 |
| `macos.diskinfo` | Missing | 0 | 0 |
| `macos.filevault` | Missing | 0 | 0 |
| `macos.firmwarepassword` | Missing | 0 | 0 |
| `macos.gatekeeper` | Missing | 0 | 1 |
| `macos.installhistory` | Missing | 0 | 0 |
| `macos.keychain` | Missing | 0 | 0 |
| `macos.launchd` | Missing | 0 | 0 |
| `macos.nvram512` | Missing | 0 | 0 |
| `macos.plist511` | Missing | 0 | 1 |
| `macos.profiles` | Missing | 0 | 0 |
| `macos.pwpolicy512` | Missing | 0 | 1 |
| `macos.softwareupdate` | Missing | 0 | 1 |
| `macos.systemprofiler` | Missing | 0 | 1 |
| `macos.systemsetup` | Missing | 0 | 0 |
| `panos.config` | Missing | 0 | 1 |
| `panos.version` | Missing | 0 | 1 |
| `solaris.package` | Missing | 0 | 0 |
| `solaris.package511` | Missing | 0 | 0 |
| `solaris.smf` | Missing | 0 | 0 |
| `solaris.smfproperty` | Missing | 0 | 0 |
| `unix.file` | Partial | 6 | 15 |
| `unix.interface` | Missing | 0 | 0 |
| `unix.password` | Missing | 0 | 1 |
| `unix.process58` | Missing | 0 | 0 |
| `unix.shadow` | Missing | 0 | 0 |
| `unix.sshd` | Missing | 0 | 0 |
| `unix.symlink` | Missing | 0 | 0 |
| `unix.sysctl` | Missing | 0 | 0 |
| `unix.uname` | Missing | 0 | 0 |
| `variable.value` | Partial | 0 | 6 |
| `windows.appcmd` | Missing | 0 | 0 |
| `windows.appcmdlistconfig` | Missing | 0 | 0 |
| `windows.auditeventpolicysubcategories` | Missing | 0 | 1 |
| `windows.cmdlet` | Missing | 0 | 1 |
| `windows.file` | Missing | 0 | 3 |
| `windows.fileeffectiverights53` | Missing | 0 | 3 |
| `windows.group_sid` | Missing | 0 | 0 |
| `windows.lockoutpolicy` | Missing | 0 | 1 |
| `windows.ntuser` | Missing | 0 | 4 |
| `windows.passwordpolicy` | Missing | 0 | 0 |
| `windows.registry` | Missing | 1 | 4 |
| `windows.regkeyeffectiverights53` | Missing | 0 | 3 |
| `windows.service` | Missing | 0 | 0 |
| `windows.sid` | Missing | 0 | 2 |
| `windows.sid_sid` | Missing | 0 | 2 |
| `windows.user_sid55` | Missing | 0 | 0 |
| `windows.userright` | Missing | 0 | 0 |
| `windows.wmi.query` | Missing | 1 | 6 |
| `windows.wuaupdatesearcher` | Missing | 0 | 3 |

## New-test disposition

All 22 new tests lack current NG mappings. The following are native implementation candidates, not implemented or Board-ratified capabilities. Keep source names as provisional capability names until a deliberate native naming review. Each needs a native selector/State/Item mapping plus standalone positive, negative, absent, error, unknown, incomplete, redacted and set/filter/Variable cases where applicable. Share the existing typed values, quantifiers, status/completeness and capability-reference enforcement; add no duplicate OVAL-shaped runtime syntax.

| Proposed capability | Disposition and contract review |
| --- | --- |
| `esx.host_acceptancelevel` | Native implementation candidate. Host software acceptance level; preserve enum and missing/error status. |
| `esx.host_account` | Native implementation candidate. Account name, domain, role and shell access; distinguish local/domain identities. |
| `esx.host_advancedsetting` | Native implementation candidate. Named host setting; typed values can be repeated in Items. |
| `esx.host_authentication` | Native implementation candidate. Domain membership; preserve explicit status vocabulary. |
| `esx.host_busadapter` | Native implementation candidate. Adapter type and device identity; CHAP names are identity metadata, not credentials. |
| `esx.host_coredump` | Native implementation candidate. Network coredump configuration; preserve IP/port datatypes. |
| `esx.host_firewallexception` | Native implementation candidate. Firewall exception and service details; retain start/end ports and direction enum. |
| `esx.host_lockdown` | Native implementation candidate. Lockdown mode plus repeated allowed users; retain empty/error distinctions. |
| `esx.host_module` | Native implementation candidate. Module name, version and acceptance level; State version and Item string need explicit comparison semantics. |
| `esx.host_ntpserver` | Native implementation candidate. Repeated server names; zero servers and acquisition failure differ. |
| `esx.host_portgroup` | Native implementation candidate. Port group plus virtual switch identify selection; preserve VLAN integer. |
| `esx.host_service` | Native implementation candidate. Service policy/running/required flags; no service-management execution. |
| `esx.host_vib` | Native implementation candidate. Installed VIB identity, vendor, creation date, version and acceptance level. |
| `esx.host_vswitchpolicy` | Native implementation candidate. Switch MAC/promiscuous/forged-transmit policy enums. |
| `esx.host_webserverssl` | Native implementation candidate. Certificate validity/issuer/expiry; retain acquisition timestamp context for days remaining. |
| `esx.vds_portgroup` | Native implementation candidate. Distributed-switch plus port-group identity; IP/port/policy fields. |
| `esx.vds` | Native implementation candidate. Distributed-switch identity and health-check flags; management-plane target context required. |
| `esx.vm_advancedsetting` | Native implementation candidate. Inherited vm_name selector/State/Item identity plus named repeated typed setting. |
| `esx.vm_device` | Native implementation candidate. Inherited VM and device fields are essential; an empty local declaration is not an empty contract. |
| `esx.vm_harddiskdevice` | Native implementation candidate. Inherited VM/device identity and connection flags plus persistence enum. |
| `kubernetes.kubectl` | Native implementation candidate. Typed resource/namespace/YAML-path query and repeated record results; API-backed acquisition, not arbitrary shell text. |
| `kubernetes.kubepsp` | Native implementation candidate. Version-scoped PSP query and record results; preserve older supported contexts without treating absent API as empty success. |

## Acquisition and fixture gates

- VMware: distinguish ESXi host, VM-on-host and management-plane distributed-switch targets. Keep source VM/device and switch/port-group selectors; record stable acquisition identity/provenance so repeated names do not merge observations. API permissions, unsupported API versions and partial retrieval must be explicit. PowerCLI examples are evidence, not a required runtime dependency.
- Kubernetes: explicit cluster/namespace/resource identity and deterministic structured path evaluation; no arbitrary command injection. Record resource version, namespace and provenance as appropriate. Keep repeated record results and missing/error/redacted properties distinct.
- `kubepsp` is not marked deprecated in the pinned OVAL schema, but Kubernetes removed its API in 1.25. Retain the candidate for valid older contexts with explicit version prerequisites; do not silently substitute Pod Security Admission or declare policy compliance from a missing API. [Official Kubernetes prerequisite](https://kubernetes.io/docs/concepts/security/pod-security-policy/).
- Existence/population completeness and required comparison lineage are separate from reported-element projection. Native schemas are only one gate; source compilation, synthetic oracles and live target acquisition are separate evidence.

## New-test source finding

All four pinned ESX/Kubernetes definition and system-characteristics XSDs compile successfully. The four Kubernetes Test binding rule contexts use `kube-def:test`, while the actual declared Tests are `kubectl_test` and `kubepsp_test`. Namespace-aware regression demonstrates zero matches for those published contexts and one for the correctly named contexts. This finding concerns those patterns, not all possible complete validators. Track [#137](https://github.com/vanderpol/scap-ng/issues/137); do not edit vendored schemas or copy the dormant assertions into NG. Native validation must enforce exact Object/State capability bindings.

## Reproduction

```sh
git clone --branch v6.0 --depth 1 https://github.com/OVAL-Community/OVAL.git work/oval60
PYTHONPATH=tools python tools/audit_oval_new_tests.py --upstream-repo work/oval60 --check
PYTHONPATH=tools python tools/audit_capability_coverage.py --output work/current-mappings.json
PYTHONPATH=tools python tools/test_oval_new_tests_audit.py
```

The upstream tool requires the exact pinned commit and reads baseline and upstream Git blobs, avoiding checkout newline conversion. It performs no network calls itself. Recompute coverage separately from the new-Test comparison. The 13 focused regressions guard scope, family/type identity, inheritance, cardinality, missing contracts, cycles, pins and the isolated Kubernetes pattern finding.

Next bounded work: add versioned 0.2.0 native ESX/Kubernetes mappings and small standalone expected-result cases in coherent capability groups, starting with simple host settings/service/acceptance levels. Resolve management/VM target context and record-query semantics before claiming those groups complete. The wider method-level coverage audit and target conformance remain open under #131/#128.
