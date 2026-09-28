# OVAL 5.12.3 Test-Type to SCAP-NG Capability Crosswalk

**Status:** architecture review — provisional naming, no content conversion  
**Iteration:** 002  
**Source inventory:** vendored OVAL 5.12.3 schemas plus Iteration 001 OVAL governance/evidence ledger

## Scope of this review

This review is deliberately limited to **OVAL test types**.

It does not yet decide the native representation of OVAL Objects, States,
Variables, sets, filters, or variable functions. Those concepts will be
reviewed after the Board/project agrees on the test/capability surface.

The working hypothesis is:

> Supported OVAL platform-family test types are the strongest candidates for
> continuity into the SCAP-NG assessment language, even if the surrounding
> Object/State/Variable authoring model is later simplified.

## Naming rule under review

For a supported OVAL test:

    <oval-family>:<test-basename>_test

the provisional SCAP-NG capability name is:

    <oval-family>.<test-basename>

Examples:

    unix:file_test                 -> unix.file
    windows:registry_test          -> windows.registry
    linux:rpminfo_test             -> linux.rpminfo
    independent:textfilecontent54_test
                                   -> independent.textfilecontent54

The `_test` suffix is removed because the native construct is a capability,
not an XML Test element.

Historical numeric suffixes such as `53`, `54`, `55`, `57`, `58`,
`511`, and `512` are retained provisionally. Whether they remain in final
native names is an explicit Board decision; the mapping SHALL NOT silently
collapse semantically distinct generations before that decision.

## Disposition rules

- **candidate** — supported/in-scope OVAL test; proposed NG capability remains
  subject to semantic review.
- **candidate-reinstated** — marked deprecated in the 5.12.x schema but later
  OVAL governance restored support; treat as supported.
- **exclude-deprecated** — effectively deprecated and outside the current
  SCAP-NG native surface. Conversion should report source remediation rather
  than invent a native implementation.
- **name-review** — supported test whose historical numeric suffix needs an
  explicit naming decision.

No test in this document is considered fully approved merely because it is
listed as a candidate.

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
| independent | 18 | 11 | 7 |
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
| **Total** | **259** | **116** | **143** |

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
| `sqlext_test` | `independent.sqlext` | schema-only | candidate |
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

## Effectively deprecated / excluded inventory

These types remain in the crosswalk for source accounting but are not proposed
as native SCAP-NG capabilities in this pass.

| Family | OVAL test | Reason |
| --- | --- | --- |
| aix | `no_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| android | `appmanager_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| android | `bluetooth_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| android | `camera_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| android | `certificate_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| android | `devicesettings_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| android | `encryption_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| android | `locationservice_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| android | `network_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| android | `password_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| android | `systemdetails_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| android | `telephony_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| android | `wifi_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| android | `wifinetwork_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| apache | `httpd_test` | 5.8 The httpd_test does not specify how to detect instances of httpd and cannot be reasonably specified to allow for products to detect all instances of httpd across platforms, packaging systems, and typical user compiled and configured installations. Without a proper definition of how to identify instances of httpd products will not reliably produce consistent assessment results because they will naturally utilize different approaches to locating instances of httpd which will lead to differences in the set of collected instances of https. This test has been deprecated and may be removed in a future version of the language. |
| apple_ios | `globalrestrictions_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| apple_ios | `passcodepolicy_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| apple_ios | `profile_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| asa | `acl_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| asa | `class_map_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| asa | `interface_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| asa | `policy_map_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| asa | `service_policy_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| asa | `snmp_group_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| asa | `snmp_host_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| asa | `snmp_user_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| asa | `tcp_map_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| catos | `line_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| catos | `module_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| catos | `version55_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| catos | `version_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. 5.5 Replaced by the version55_test. Due to the fact it's not clear on how to separate the CatOS version, it was decided that the catos_major_release, catos_individual_release, and catos_version_id entities would be combined into a new single entity catos_release. A new test was created to reflect these changes. See the version55_test. This test has been deprecated and will be removed in version 6.0 of the language. |
| esx | `patch56_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| esx | `patch_test` | 5.6 Replaced by the patch56_test. The deprecated patch_test has a bug where the patch name entity is defined as a string in the object yet is defined as an int in the state. Additional state entities have also been added to the new patch56_test. This test has been deprecated and will be removed in version 6.0 of the language. |
| esx | `version_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| esx | `visdkmanagedobject_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| freebsd | `portinfo_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| hpux | `getconf_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| hpux | `ndd_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| hpux | `patch53_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| hpux | `patch_test` | 5.3 Replaced by the patch53_test. The patch_name entity was removed from the patch_object element, and replaced with the swtype, area_patched, and patch_base entities, because the patch_name element can be constructed from the swtype, area_patched, and patch_base entities. Likewise, the patch_name entity was removed from the patch_state element for the same reason. Also, a behaviors entity was added to the patch_object to allow the object to match both the original patch and any superseding patches. A new test was created to reflect these changes. See the patch53_test. This test has been deprecated and will be removed in version 6.0 of the language. |
| hpux | `swlist_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| hpux | `trusted_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| independent | `environmentvariable_test` | 5.8 Replaced by the environmentvariable58_test. This object has been deprecated and may be removed in a future version of the language. |
| independent | `filehash_test` | 5.8 Replaced by the filehash58_test. This object has been deprecated and may be removed in a future version of the language. |
| independent | `ldap57_test` | 5.11.2 Use the original ldap_test. The ldap57_test suffers from ambiguity; it was never adequately specified, and it does not even seem possible to have structured data in the context of the enumerated LdaptypeTypes. Use the original ldap_test instead. This test has been deprecated and will be removed in version 6.0 of the language. |
| independent | `ldap_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| independent | `sql57_test` | 5.12 Replaced by the sql512_test. The sql512_test removes the connection string and replaces it with 'instance' and 'database' elements. This allows the application to perform any necessary steps to connect, and providing a simple method for content authors to determine which database(s) to query. This object has been deprecated and may be removed in a future version of the language. |
| independent | `sql_test` | 5.7 Replaced by the sql57_test. This test allows for single fields to be selected from a database. A new test was created to allow more than one field to be selected in one statement. See the sql57_test. This object has been deprecated and may be removed in a future version of the language. |
| independent | `textfilecontent_test` | 5.4 Replaced by the textfilecontent54_test. Support for multi-line pattern matching and multi-instance matching was added. Therefore, a new test was created to reflect these changes. See the textfilecontent54_test. This test has been deprecated and will be removed in version 6.0 of the language. |
| ios | `acl_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| ios | `router_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| ios | `snmpview_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| ios | `tclsh_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| ios | `version_test` | 5.5 Replaced by the version55_test. Additional IOS version components were added to the version_state in order to support a wider range of IOS version strings. Also, the major_release and train_number entities were removed from the version_state element. A new test was created to reflect these changes. See the version55_test. This test has been deprecated and will be removed in version 6.0 of the language. |
| iosxe | `acl_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| iosxe | `router_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| iosxe | `snmpview_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| junos | `version_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| junos | `xml_config_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| junos | `xml_show_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| linux | `iflisteners_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| linux | `rpmverify_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. 5.10 Replaced by the rpmverifyfile_test and the rpmverifypackage_test. The rpmverify_test was split into two tests to distinguish between the verification of the files in an rpm and the verification of an rpm as a whole. By making this distinction, content authoring is simplified and information is no longer duplicated across items. See the rpmverifyfile_test and rpmverifypackage_test. This test has been deprecated and will be removed in version 6.0 of the language. |
| linux | `slackwarepkginfo_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| macos | `corestorage_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| macos | `diskutil_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. 5.11.2 The diskutil_test has been deprecated. The underlying capability was rendered obsolete in MacOS X 10.11 (El Capitan), and then removed altogether from the platform in MacOS X 10.12 (Sierra). |
| macos | `inetlisteningserver510_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| macos | `inetlisteningservers_test` | 5.10 The inetlisteningservers_test has been deprecated and replaced by the inetlisteningserver510_test. The name of an application cannot be used to uniquely identify an application that is listening on the network. As a result, the inetlisteningserver510_object utilizes the protocol, local_address, and local_port entities to uniquely identify an application listening on the network. Please see the inetlisteningserver510_test for additional information. |
| macos | `nvram_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| macos | `plist510_test` | 5.11.2:1.0 Replaced by the plist511_test. This test references the plist_object which cannot express the context hierarchy required to differentiate between nodes with identical names. As a result, it is not possible to address a particular node when the order of their parent nodes is indeterminate. The plist511_test was added to address this deficiency. See the plist511_test. This test has been deprecated and may be removed in a future version of the language. |
| macos | `plist_test` | 5.10 Replaced by the plist510_test. This test references the plist_object which does not contain an instance entity. As a result, it is not possible to differentiate between two preference keys that have the same name using the plist_object. The plist510_test was added to address this deficiency. See the plist510_test. This test has been deprecated and may be removed in a future version of the language. |
| macos | `pwpolicy59_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| macos | `pwpolicy_test` | 5.9 Replaced by the pwpolicy59_test. The username, userpass, and directory_node entities in the pwpolicy_object, pwpolicy_state, and pwpolicy_item were underspecified and as a result their meaning was uncertain. A new test was created to resolve this issue. See the pwpolicy59_test. This test has been deprecated and may be removed in a future version of the language. |
| macos | `rlimit_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| netconf | `config_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| pixos | `line_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| pixos | `version_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| sharepoint | `bestbet_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| sharepoint | `infopolicycoll_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| sharepoint | `spantivirussettings_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| sharepoint | `spcrawlrule_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| sharepoint | `spdiagnosticslevel_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| sharepoint | `spdiagnosticsservice_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| sharepoint | `spgroup_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| sharepoint | `spjobdefinition510_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| sharepoint | `spjobdefinition_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. 5.10 Replaced by the spjobdefinition510_test. This test does not uniquely identify a single job definition. A new test was created to use displaynames, which are unique. See the spjobdefinition510_test. This test has been deprecated and will be removed in version 6.0 of the language. |
| sharepoint | `splist_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| sharepoint | `sppolicy_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| sharepoint | `sppolicyfeature_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| sharepoint | `spsite_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| sharepoint | `spsiteadministration_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| sharepoint | `spweb_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| sharepoint | `spwebapplication_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| solaris | `facet_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| solaris | `image_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| solaris | `isainfo_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| solaris | `ndd_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| solaris | `packageavoidlist_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| solaris | `packagecheck_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| solaris | `packagefreezelist_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| solaris | `packagepublisher_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| solaris | `patch_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. 5.4 Replaced by the patch54_test. The new test includes additional functionality that allows the object element to match both the original patch and any superseding patches. As a result of this new functionality, the patch_object was also expanded to include behaviors and version entities. See the patch54_test. This test has been deprecated and will be removed in version 6.0 of the language. |
| solaris | `variant_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| solaris | `virtualizationinfo_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| unix | `dnscache_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| unix | `fileextendedattribute_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| unix | `gconf_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| unix | `inetd_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| unix | `process_test` | 5.8 The process_test has been deprecated and replaced by the process58_test. The command line of a process cannot be used to uniquely identify a process. As a result, the pid entity was added to the process58_object. Please see the process58_test for additional information. |
| unix | `routingtable_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| unix | `runlevel_test` | 5.12.3 The runlevel_test has been deprecated because runlevel is obsolete. The runlevel_test may be removed in a future version of the language. |
| unix | `sccs_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. 5.10 The sccs_test has been deprecated because the Source Code Control System (SCCS) is obsolete. The sccs_test may be removed in a future version of the language. |
| unix | `xinetd_test` | 5.12.3 The xinetd_test has been deprecated because xinetd is obsolete. The xinetd_test may be removed in a future version of the language. |
| windows | `accesstoken_test` | 5.11 Replaced by the userright_test. This accesstoken_test suffers from scalability issues when run on a domain controller and should not be used. See the userright_test. This test has been deprecated and will be removed in version 6.0 of the language. |
| windows | `activedirectory57_test` | 5.11.1:1.2 Use the original activedirectory_test. The activedirectory57_test suffers from ambiguity; it was never adequately specified, and it does not even seem possible to have structured data in the context of the enumerated AdstypeTypes. Use the original activedirectory_test instead. This test has been deprecated and will be removed in version 6.0 of the language. |
| windows | `activedirectory_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| windows | `auditeventpolicy_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| windows | `dnscache_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| windows | `fileauditedpermissions53_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| windows | `fileauditedpermissions_test` | 5.3 Replaced by the fileauditedpermissions53_test. This test uses a trustee_name element for identifying trustees. Trustee names are not unique, and a new test was created to use trustee SIDs, which are unique. See the fileauditedpermissions53_test. This test has been deprecated and will be removed in version 6.0 of the language. |
| windows | `fileeffectiverights_test` | 5.3 Replaced by the fileeffectiverights53_test. This test uses a trustee_name element for identifying trustees. Trustee names are not unique, and a new test was created to use trustee SIDs, which are unique. See the fileeffectiverights53_test. This test has been deprecated and will be removed in version 6.0 of the language. |
| windows | `group_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. 5.11 Replaced by the group_sid_test. This test uses trustee names for identifying accounts on the system. Trustee names are not unique and the group_sid_test, which uses trustee SIDs which are unique, should be used instead. See the group_sid_test. This test has been deprecated and will be removed in version 6.0 of the language. |
| windows | `interface_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| windows | `junction_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| windows | `license_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| windows | `metabase_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| windows | `peheader_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| windows | `port_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| windows | `printereffectiverights_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| windows | `process58_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| windows | `process_test` | 5.8 The process_test has been deprecated and replaced by the process58_test. The command line of a process cannot be used to uniquely identify a process. As a result, the pid entity was added to the process58_object. Please see the process58_test for additional information. |
| windows | `regkeyauditedpermissions53_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| windows | `regkeyauditedpermissions_test` | 5.3 Replaced by the regkeyauditedpermissions53_test. This test uses a trustee_name element for identifying trustees. Trustee names are not unique, and a new test was created to use trustee SIDs, which are unique. See the regkeyauditedpermissions53_test. This test has been deprecated and will be removed in version 6.0 of the language. |
| windows | `regkeyeffectiverights_test` | 5.3 Replaced by the regkeyeffectiverights53_test. This test uses a trustee_name element for identifying trustees. Trustee names are not unique, and a new test was created to use trustee SIDs, which are unique. See the regkeyeffectiverights53_test. This test has been deprecated and will be removed in version 6.0 of the language. |
| windows | `serviceeffectiverights_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| windows | `sharedresource_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| windows | `sharedresourceauditedpermissions_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| windows | `sharedresourceeffectiverights_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| windows | `systemmetric_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| windows | `uac_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| windows | `user_sid_test` | 5.5 Replaced by the user_sid55_test. This test uses user and group elements that are incorrectly named. A new test was created to change the element names to their correct values which are user_sid and group_sid. See the user_sid55_test. This test has been deprecated and will be removed in version 6.0 of the language. |
| windows | `user_test` | 5.11 Replaced by the user_sid55_test. This test uses trustee names for identifying accounts on the system. Trustee names are not unique and the user_sid55_test, which uses trustee SIDs which are unique, should be used instead. See the user_sid55_test. This test has been deprecated and will be removed in version 6.0 of the language. |
| windows | `volume_test` | 5.12 This test has been deprecated due to lack of documented usage and will be removed in version 6.0 of the language. |
| windows | `wmi_test` | 5.7 Replaced by the wmi57_test. This test only allows for single fields to be selected from WMI. A new test was created to allow more than one field to be selected in one statement. See the wmi57_test. This test has been deprecated and may be removed in a future version of the language. |

## Questions to settle before deeper mapping

1. Is the OVAL family/test taxonomy the normative starting capability catalog
   for SCAP-NG?
2. Should the native term be **capability**, **test type**, **collector**, or
   another term? The current prototype uses capability.
3. Which historical numeric suffixes represent semantic distinctions that must
   remain visible in native names?
4. When an old and newer test generation differ, does NG admit only the
   corrected generation or define a clean new baseline name?
5. Should schema-only but currently supported tests enter the first NG
   specification immediately, or remain reserved until conformance evidence is
   available?
6. Should `independent.unknown` remain a real native capability? Its presence
   is intentionally flagged for specific review rather than accepted by
   inertia.
7. Should reinstated tests use their historical names exactly, or can a new NG
   baseline name remove a historical version suffix after semantics are fixed?

## Gate

Broad OVAL-to-NG content conversion remains paused.

The next review step is to take the supported candidate list family by family
and verify that the proposed capability preserves the test type's actual
collection/result contract. Only after the test surface is agreed should we
decide how Objects, States, Variables, and related OVAL scaffolding map into
native authoring.
