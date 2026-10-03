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

The original inventory found **22** OVAL 6.0-only Tests: 20 ESX and two
Kubernetes. That count is an inventory fact, not an active 0.2.0 implementation
backlog.

The current owner-approved disposition supersedes the earlier candidate language:

- **ESX (20 Tests): deferred pending upstream guidance.** Existing experimental
  0.2.0 ESX mappings and synthetic fixtures remain evidence, but the family is
  not a 0.2.0 freeze blocker and should not be expanded merely to reduce this
  inventory count.
- **Kubernetes `kubectl_test`: deferred for 0.2.0.** The useful semantic need is
  Kubernetes resource/API observation, but the OVAL 6.0 contract is shaped around
  `kubectl get ... -o=yaml` and YAML-path selection. SCAP-NG should define a
  native resource/API model with current content, typed Items, error/completeness
  behavior and collector equivalence before standardizing a capability.
  Do not lower it automatically to `independent.shellcommand`.
- **Kubernetes `kubepsp_test`: deferred for 0.2.0.** PodSecurityPolicy was
  deprecated in Kubernetes 1.21 and removed in 1.25. A new native capability
  tied to PSP is not justified for the modern 0.2.0 vocabulary solely because
  OVAL 6.0 added the Test. Legacy-platform migration can be revisited if concrete
  supported content requires it.

See [the detailed Kubernetes disposition](../../../transition/kubernetes-oval6-disposition-2026-10-03.md).
These rows SHALL be accounted as **reviewed/deferred**, not “missing
implementation.” SCAP-NG treats OVAL 6.0 new Tests as capability leads rather
than mandatory native serialization contracts.

### Acquisition and future-fixture gates

If ESX work resumes, distinguish ESXi host, VM-on-host and management-plane
distributed-switch targets; preserve source selector identity and explicit
permission/API-version/partial-retrieval behavior. PowerCLI examples remain
evidence, not a required runtime dependency.

If a native Kubernetes capability is proposed later, require explicit
cluster/namespace/resource identity, deterministic structured field selection,
current platform examples, repeated-result semantics, permission/absence/error
behavior, collection completeness, provenance, and evidence that API-backed and
optional CLI-backed collectors produce equivalent native Items.

Existence/population completeness and comparison lineage remain separate from
reported-element projection. A native schema alone is not conformance evidence.

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

Next bounded work for the 0.2.0 freeze is semantic/documentation reconciliation and exact-head validation. ESX and Kubernetes new-Test expansion are deferred as recorded above. The wider method-level coverage audit, vendor conformance corpus, and live target execution remain open under #131/#128.
