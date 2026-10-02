# OVAL 5.12.3 Test-Type to SCAP-NG Capability Crosswalk

**Status:** pre-alpha informative migration appendix  
**Normative migration rules:** `oval-5.12.3-to-ng.md`

This appendix records the current OVAL 5.12.3 Test-type inventory and the
provisional native SCAP-NG Capability mapping.

Listing a Test type here does not freeze the final Capability name. It records
the migration surface that the specification must account for.

The earlier inventory contained 259 types, including the SCC/NIWC-only
`independent.sqlext_test`. Removing that non-standard element yields a
**provisional** inventory of 258 standard types, with 115 native-capability
candidates and 143 effectively deprecated/excluded types. The entire inventory
SHALL be regenerated against pinned **upstream** OVAL 5.12.3 schemas before
these numbers are considered authoritative; a locally augmented schema is
insufficient for defining the standard vocabulary.

The converter SHALL still account for excluded Test types. Exclusion means
"report source remediation/unsupported status", not "silently ignore".

## Mapping rule

For a supported OVAL Test:

    <family>:<basename>_test
        ->
    <family>.<basename>

The `_test` suffix is removed because SCAP-NG names a Capability rather than
an XML Test element.

Historical numeric suffixes remain provisional until the specification proves
that collapsing them would preserve semantics.

### Reviewed native mappings override the provisional inventory

The inventory below is historical naming research, not the current converter
registry. For reviewed clean native capabilities, the exact source family is
retained in [capability mappings](../../schema/v0.1.0/capability-mappings/README.md)
while the native capability name may differ from the source basename.

| Exact OVAL source Test | Current native capability | Mapping |
| --- | --- | --- |
| `unix:file_test` | `unix.file` | [unix.file](../../schema/v0.1.0/capability-mappings/unix.file.json) |
| `independent:filehash58_test` | `file.hash` | [file.hash](../../schema/v0.1.0/capability-mappings/file.hash.json) |
| `windows:file_test` | `windows.file` | [windows.file](../../schema/v0.1.0/capability-mappings/windows.file.json) |
| `windows:registry_test` | `windows.registry` | [windows.registry](../../schema/v0.1.0/capability-mappings/windows.registry.json) |
| `independent:variable_test` | `variable.value` | [variable.value](../../schema/v0.1.0/capability-mappings/variable.value.json) |
| `windows:wmi57_test` | `windows.wmi.query` | [windows.wmi.query](../../schema/v0.1.0/capability-mappings/windows.wmi.query.json) |
| `linux:rpminfo_test` | `linux.rpminfo` | [linux.rpminfo](../../schema/v0.1.0/capability-mappings/linux.rpminfo.json) |
| `independent:textfilecontent54_test` | `independent.textfilecontent54` | [independent.textfilecontent54](../../schema/v0.1.0/capability-mappings/independent.textfilecontent54.json) |
| `windows:auditeventpolicysubcategories_test` | `windows.auditeventpolicysubcategories` | [windows.auditeventpolicysubcategories](../../schema/v0.1.0/capability-mappings/windows.auditeventpolicysubcategories.json) |
| `windows:userright_test` | `windows.userright` | [windows.userright](../../schema/v0.1.0/capability-mappings/windows.userright.json) |
| `independent:shellcommand_test` | `independent.shellcommand` | [independent.shellcommand](../../schema/v0.1.0/capability-mappings/independent.shellcommand.json) |
| `unix:sysctl_test` | `unix.sysctl` | [unix.sysctl](../../schema/v0.1.0/capability-mappings/unix.sysctl.json) |
| `linux:partition_test` | `linux.partition` | [linux.partition](../../schema/v0.1.0/capability-mappings/linux.partition.json) |
| `linux:systemdunitproperty_test` | `linux.systemdunitproperty` | [linux.systemdunitproperty](../../schema/v0.1.0/capability-mappings/linux.systemdunitproperty.json) |
| `windows:fileeffectiverights53_test` | `windows.fileeffectiverights53` | [windows.fileeffectiverights53](../../schema/v0.1.0/capability-mappings/windows.fileeffectiverights53.json) |
| `windows:cmdlet_test` | `windows.cmdlet` | [windows.cmdlet](../../schema/v0.1.0/capability-mappings/windows.cmdlet.json) |
| `unix:symlink_test` | `unix.symlink` | [unix.symlink](../../schema/v0.1.0/capability-mappings/unix.symlink.json) |
| `windows:lockoutpolicy_test` | `windows.lockoutpolicy` | [windows.lockoutpolicy](../../schema/v0.1.0/capability-mappings/windows.lockoutpolicy.json) |
| `windows:passwordpolicy_test` | `windows.passwordpolicy` | [windows.passwordpolicy](../../schema/v0.1.0/capability-mappings/windows.passwordpolicy.json) |
| `unix:password_test` | `unix.password` | [unix.password](../../schema/v0.1.0/capability-mappings/unix.password.json) |
| `unix:shadow_test` | `unix.shadow` | [unix.shadow](../../schema/v0.1.0/capability-mappings/unix.shadow.json) |
| `linux:selinuxsecuritycontext_test` | `linux.selinuxsecuritycontext` | [linux.selinuxsecuritycontext](../../schema/v0.1.0/capability-mappings/linux.selinuxsecuritycontext.json) |
| `unix:interface_test` | `unix.interface` | [unix.interface](../../schema/v0.1.0/capability-mappings/unix.interface.json) |

Owner clarification, 2026-10-02: historical suffixes identify the OVAL version
in which the revised capability was introduced/fixed, for example `54` in
`textfilecontent54` means OVAL 5.4 and `57` in `wmi57` means OVAL 5.7. They are
not WMI product versions or evidence that the older unsuffixed Test is
interchangeable. Preserve the exact versioned source names in importer mappings
and provenance even when native names omit the suffix.

Pinned source documentation distinguishes the replacements: `wmi57` supports
multiple selected WMI fields where deprecated `wmi` permitted a single field;
`textfilecontent54` adds multi-line and multi-instance matching compared with
deprecated `textfilecontent`. See the pinned
[Windows schema](../../third_party/scap-1.4-schemas/oval_5.12.3/windows-definitions-schema.xsd)
and [independent schema](../../third_party/scap-1.4-schemas/oval_5.12.3/independent-definitions-schema.xsd).

`textfilecontent54` now has a reviewed native mapping in the table above. Historical candidate spellings below remain informational and do not independently prove native coverage.
Every future mapping SHALL identify the exact source Test/Object/State family,
field translation, preserved semantics, intentional divergences, unsupported
cases and regression evidence. Name simplification alone is not conversion
equivalence and SHALL NOT bypass effective deprecation checks.

## Inventory summary

| Family | OVAL tests | NG candidates | Effective deprecated/excluded |
| --- | ---: | ---: | ---: |
| aix | 10 | 9 | 1 |
| android | 13 | 0 | 13 |
| apache | 1 | 0 | 1 |
| apple_ios | 3 | 0 | 3 |
| asa | 11 | 2 | 9 |
| aws | 5 | 5 | 0 |
| catos | 4 | 0 | 4 |
| esx | 4 | 0 | 4 |
| freebsd | 1 | 0 | 1 |
| hpux | 6 | 0 | 6 |
| independent | 17 | 10 | 7 |
| ios | 17 | 12 | 5 |
| iosxe | 14 | 11 | 3 |
| junos | 4 | 1 | 3 |
| linux | 16 | 13 | 3 |
| macos | 27 | 17 | 10 |
| netconf | 1 | 0 | 1 |
| panos | 2 | 2 | 0 |
| pixos | 2 | 0 | 2 |
| sharepoint | 16 | 0 | 16 |
| solaris | 16 | 5 | 11 |
| unix | 18 | 9 | 9 |
| windows | 50 | 19 | 31 |
| **Provisional total** | **258** | **115** | **143** |

## Supported / in-scope candidates

### aix

| OVAL test | Provisional NG capability | Evidence | Disposition |
| --- | --- | --- | --- |
| `deviceattribute_test` | `aix.deviceattribute` | schema-only | candidate |
| `fileset_test` | `aix.fileset` | self-assertion:1 | candidate |
| `fix_test` | `aix.fix` | self-assertion:1 | candidate |
| `inittab_test` | `aix.inittab` | schema-only | candidate |
| `interim_fix_test` | `aix.interim_fix` | schema-only | candidate-reinstated |
| `nfso_test` | `aix.nfso` | schema-only | candidate |
| `oslevel_test` | `aix.oslevel` | schema-only | candidate-reinstated |
| `securitystanza_test` | `aix.securitystanza` | schema-only | candidate |
| `useraccount_test` | `aix.useraccount` | schema-only | candidate |

### asa

| OVAL test | Provisional NG capability | Evidence | Disposition |
| --- | --- | --- | --- |
| `line_test` | `asa.line` | self-assertion:1 | candidate |
| `version_test` | `asa.version` | self-assertion:1 | candidate |

### aws

| OVAL test | Provisional NG capability | Evidence | Disposition |
| --- | --- | --- | --- |
| `api_test` | `aws.api` | schema-only | candidate |
| `apicontent_test` | `aws.apicontent` | schema-only | candidate |
| `credentialreportcert_test` | `aws.credentialreportcert` | schema-only | candidate |
| `credentialreportkey_test` | `aws.credentialreportkey` | schema-only | candidate |
| `credentialreportuser_test` | `aws.credentialreportuser` | schema-only | candidate |

### independent

| OVAL test | Provisional NG capability | Evidence | Disposition |
| --- | --- | --- | --- |
| `environmentvariable58_test` | `independent.environmentvariable58` | self-assertion:14 | candidate; name-review |
| `family_test` | `independent.family` | self-assertion:1 | candidate |
| `filehash58_test` | `independent.filehash58` | self-assertion:6 | candidate; name-review |
| `shellcommand_test` | `independent.shellcommand` | production:80, self-assertion:11 | candidate |

**`independent.shellcommand` note:** this capability is intentionally in the
OVAL/NG **independent** family. The Assessment supplies the shell/interpreter to
use; the capability is not inherently Unix-specific. For example, selecting
`bash` makes a particular Assessment operationally Unix/Linux-oriented, while
the capability itself remains platform-independent. SCAP-NG SHALL NOT rename
this capability to `unix.command` merely because a common use invokes Bash.
| `sql512_test` | `independent.sql512` | schema-only | candidate; name-review |
| `textfilecontent54_test` | `independent.textfilecontent54` | production:797, self-assertion:21 | candidate; name-review |
| `unknown_test` | `independent.unknown` | self-assertion:1 | candidate |
| `variable_test` | `independent.variable` | production:19, self-assertion:308 | candidate |
| `xmlfilecontent_test` | `independent.xmlfilecontent` | self-assertion:14 | candidate |
| `yamlfilecontent_test` | `independent.yamlfilecontent` | schema-only | candidate |

### ios

| OVAL test | Provisional NG capability | Evidence | Disposition |
| --- | --- | --- | --- |
| `bgpneighbor_test` | `ios.bgpneighbor` | self-assertion:1 | candidate |
| `global_test` | `ios.global` | self-assertion:2 | candidate |
| `interface_test` | `ios.interface` | self-assertion:1 | candidate |
| `line_test` | `ios.line` | self-assertion:2 | candidate |
| `routingprotocolauthintf_test` | `ios.routingprotocolauthintf` | self-assertion:1 | candidate |
| `section_test` | `ios.section` | self-assertion:1 | candidate |
| `snmp_test` | `ios.snmp` | schema-only | candidate |
| `snmpcommunity_test` | `ios.snmpcommunity` | self-assertion:1 | candidate |
| `snmpgroup_test` | `ios.snmpgroup` | self-assertion:1 | candidate |
| `snmphost_test` | `ios.snmphost` | self-assertion:1 | candidate |
| `snmpuser_test` | `ios.snmpuser` | self-assertion:1 | candidate |
| `version55_test` | `ios.version55` | schema-only | candidate; name-review |

### iosxe

| OVAL test | Provisional NG capability | Evidence | Disposition |
| --- | --- | --- | --- |
| `bgpneighbor_test` | `iosxe.bgpneighbor` | self-assertion:1 | candidate |
| `global_test` | `iosxe.global` | self-assertion:2 | candidate |
| `interface_test` | `iosxe.interface` | self-assertion:1 | candidate |
| `line_test` | `iosxe.line` | self-assertion:2 | candidate |
| `routingprotocolauthintf_test` | `iosxe.routingprotocolauthintf` | self-assertion:1 | candidate |
| `section_test` | `iosxe.section` | self-assertion:1 | candidate |
| `snmpcommunity_test` | `iosxe.snmpcommunity` | self-assertion:1 | candidate |
| `snmpgroup_test` | `iosxe.snmpgroup` | self-assertion:1 | candidate |
| `snmphost_test` | `iosxe.snmphost` | self-assertion:1 | candidate |
| `snmpuser_test` | `iosxe.snmpuser` | self-assertion:1 | candidate |
| `version_test` | `iosxe.version` | self-assertion:5 | candidate |

### junos

| OVAL test | Provisional NG capability | Evidence | Disposition |
| --- | --- | --- | --- |
| `show_test` | `junos.show` | self-assertion:1 | candidate |

### linux

| OVAL test | Provisional NG capability | Evidence | Disposition |
| --- | --- | --- | --- |
| `apparmorstatus_test` | `linux.apparmorstatus` | self-assertion:1 | candidate |
| `dpkginfo_test` | `linux.dpkginfo` | self-assertion:3 | candidate |
| `inetlisteningservers_test` | `linux.inetlisteningservers` | self-assertion:3 | candidate |
| `kernelmodule_test` | `linux.kernelmodule` | self-assertion:3 | candidate |
| `partition_test` | `linux.partition` | production:64, self-assertion:3 | candidate |
| `rpminfo_test` | `linux.rpminfo` | production:68, self-assertion:3 | candidate |
| `rpmverifyfile_test` | `linux.rpmverifyfile` | self-assertion:3 | candidate |
| `rpmverifypackage_test` | `linux.rpmverifypackage` | self-assertion:4 | candidate |
| `selinuxboolean_test` | `linux.selinuxboolean` | self-assertion:3 | candidate |
| `selinuxsecuritycontext_test` | `linux.selinuxsecuritycontext` | production:2, self-assertion:7 | candidate |
| `sestatus_test` | `linux.sestatus` | self-assertion:3 | candidate |
| `systemdunitdependency_test` | `linux.systemdunitdependency` | self-assertion:3 | candidate |
| `systemdunitproperty_test` | `linux.systemdunitproperty` | production:40, self-assertion:10 | candidate |

### macos

| OVAL test | Provisional NG capability | Evidence | Disposition |
| --- | --- | --- | --- |
| `accountinfo_test` | `macos.accountinfo` | self-assertion:3 | candidate |
| `authorizationdb_test` | `macos.authorizationdb` | self-assertion:3 | candidate |
| `disabledservice_test` | `macos.disabledservice` | self-assertion:1 | candidate |
| `diskinfo_test` | `macos.diskinfo` | self-assertion:1 | candidate |
| `filevault_test` | `macos.filevault` | self-assertion:1 | candidate |
| `firmwarepassword_test` | `macos.firmwarepassword` | self-assertion:1 | candidate |
| `gatekeeper_test` | `macos.gatekeeper` | self-assertion:1 | candidate |
| `installhistory_test` | `macos.installhistory` | self-assertion:1 | candidate |
| `keychain_test` | `macos.keychain` | self-assertion:1 | candidate |
| `launchd_test` | `macos.launchd` | self-assertion:3 | candidate |
| `nvram512_test` | `macos.nvram512` | self-assertion:4 | candidate; name-review |
| `plist511_test` | `macos.plist511` | self-assertion:2 | candidate; name-review |
| `profiles_test` | `macos.profiles` | self-assertion:1 | candidate |
| `pwpolicy512_test` | `macos.pwpolicy512` | self-assertion:2 | candidate; name-review |
| `softwareupdate_test` | `macos.softwareupdate` | self-assertion:1 | candidate |
| `systemprofiler_test` | `macos.systemprofiler` | self-assertion:3 | candidate |
| `systemsetup_test` | `macos.systemsetup` | self-assertion:1 | candidate |

### panos

| OVAL test | Provisional NG capability | Evidence | Disposition |
| --- | --- | --- | --- |
| `config_test` | `panos.config` | self-assertion:1 | candidate |
| `version_test` | `panos.version` | self-assertion:1 | candidate |

### solaris

| OVAL test | Provisional NG capability | Evidence | Disposition |
| --- | --- | --- | --- |
| `package511_test` | `solaris.package511` | self-assertion:6 | candidate-reinstated; name-review |
| `package_test` | `solaris.package` | self-assertion:3 | candidate-reinstated |
| `patch54_test` | `solaris.patch54` | schema-only | candidate-reinstated; name-review |
| `smf_test` | `solaris.smf` | self-assertion:3 | candidate |
| `smfproperty_test` | `solaris.smfproperty` | self-assertion:3 | candidate |

### unix

| OVAL test | Provisional NG capability | Evidence | Disposition |
| --- | --- | --- | --- |
| `file_test` | `unix.file` | production:155, self-assertion:18 | candidate |
| `interface_test` | `unix.interface` | production:2, self-assertion:13 | candidate |
| `password_test` | `unix.password` | production:10, self-assertion:6 | candidate |
| `process58_test` | `unix.process58` | self-assertion:8 | candidate; name-review |
| `shadow_test` | `unix.shadow` | production:4, self-assertion:3 | candidate |
| `sshd_test` | `unix.sshd` | self-assertion:4 | candidate |
| `symlink_test` | `unix.symlink` | production:15, self-assertion:6 | candidate |
| `sysctl_test` | `unix.sysctl` | production:66, self-assertion:10 | candidate |
| `uname_test` | `unix.uname` | self-assertion:1 | candidate |

### windows

| OVAL test | Provisional NG capability | Evidence | Disposition |
| --- | --- | --- | --- |
| `appcmd_test` | `windows.appcmd` | self-assertion:14 | candidate |
| `appcmdlistconfig_test` | `windows.appcmdlistconfig` | production:1, self-assertion:16 | candidate |
| `auditeventpolicysubcategories_test` | `windows.auditeventpolicysubcategories` | production:143, self-assertion:1 | candidate |
| `cmdlet_test` | `windows.cmdlet` | production:22, self-assertion:6 | candidate |
| `file_test` | `windows.file` | production:4, self-assertion:14 | candidate |
| `fileeffectiverights53_test` | `windows.fileeffectiverights53` | production:32, self-assertion:7 | candidate; name-review |
| `group_sid_test` | `windows.group_sid` | self-assertion:6 | candidate |
| `lockoutpolicy_test` | `windows.lockoutpolicy` | production:14, self-assertion:1 | candidate |
| `ntuser_test` | `windows.ntuser` | production:5, self-assertion:20 | candidate |
| `passwordpolicy_test` | `windows.passwordpolicy` | production:14, self-assertion:7 | candidate |
| `registry_test` | `windows.registry` | production:298, self-assertion:15 | candidate |
| `regkeyeffectiverights53_test` | `windows.regkeyeffectiverights53` | self-assertion:7 | candidate; name-review |
| `service_test` | `windows.service` | production:3, self-assertion:5 | candidate |
| `sid_sid_test` | `windows.sid_sid` | production:2, self-assertion:6 | candidate |
| `sid_test` | `windows.sid` | self-assertion:6 | candidate |
| `user_sid55_test` | `windows.user_sid55` | production:1, self-assertion:13 | candidate; name-review |
| `userright_test` | `windows.userright` | production:92, self-assertion:47 | candidate |
| `wmi57_test` | `windows.wmi57` | production:55, self-assertion:5 | candidate; name-review |
| `wuaupdatesearcher_test` | `windows.wuaupdatesearcher` | self-assertion:9 | candidate |

### Windows publisher-extension provenance caveat

Upstream OVAL-Community v5.12.3 verification shows that several Windows Item types exist in the system-characteristics schema without matching Test/Object/State families in the official Windows definitions schema. This includes at least `cmdlet`, `ntuser`, `service`, `sid_sid`, `user_sid55`, and `appcmdlistconfig`.

Accordingly, these names SHALL NOT be treated as standard OVAL 5.12.3 definition-side capabilities solely because a system-characteristics Item exists or because production SCC content uses a publisher extension. Their exact extension provenance must be established separately. Native SCAP-NG capability research may continue, but the migration crosswalk must keep standard OVAL and publisher extensions distinct.

## Excluded/deprecated Test types

The complete deprecated/excluded inventory and rationale is maintained in the
research evidence file:

    research/iterations/002/decisions/oval-test-type-crosswalk.md

For specification purposes, an effectively deprecated/out-of-scope Test type:

- SHALL be recognized during source ingestion;
- SHALL be reported by exact OVAL family/Test name;
- SHALL NOT be silently converted to a different Capability;
- SHOULD identify a documented replacement where one exists;
- SHALL block conversion of the affected Definition until source remediation
  or an explicit standards decision permits another migration path.

This appendix will be regenerated as Capability naming and OVAL-governance
decisions stabilize.

<!-- spec-nav:start -->

---

**Specification navigation:** [← Previous: OVAL 5.12.3 to SCAP-NG Migration](oval-5.12.3-to-ng.md) · [Contents](../README.md) · [Next: Security Considerations →](../security/security-considerations.md)

<!-- spec-nav:end -->


## Publisher extension exclusion: `sqlext`

SCC/NIWC `sqlext_test`, `sqlext_object`, and `sqlext_state` appear
in locally augmented OVAL schemas but are absent from pinned upstream OVAL
5.12.3. They SHALL NOT be listed as standard OVAL-derived SCAP-NG capabilities.
The generic converter SHALL diagnose these as out-of-scope publisher-extension
constructs rather than silently emit schema-invalid standard OVAL.
Migration of the source SQL content to standard `sql512` is a separate
future content-maintenance effort; this specification does not claim that
`sqlext` and `sql512` are behaviorally interchangeable.

See
[OVAL-derived specification lessons](../../research/iterations/003/design/oval-derived-specification-lessons.md).
