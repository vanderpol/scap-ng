# Proposed SCAP-NG reference

Generated from proposed JSON Schemas; 0.4.0 remains frozen. Field-description coverage does not establish complete scanner contracts.

Field-route totals count Object, Item and Require contexts, including reused meanings. Unique description owners are reported separately. Shared gaps count exact named-schema nodes, including repeated conditional constraints; they are not a count of distinct missing language features.

| Measure | Count |
| --- | ---: |
| capabilities | 104 |
| fully field documented | 102 |
| partial capabilities | 2 |
| fields discovered | 1866 |
| fields documented | 1858 |
| missing capability descriptions | 8 |
| unresolved native contracts | 104 |
| shared description gaps | 172 |
| capability pages | 104 |
| shared pages | 35 |
| advanced pages | 139 |
| description owners | 2120 |
| duplicate text groups | 171 |
| capability unique description owners | 794 |
| preserved semantic holds | 9 |
| preserved withheld definitions | 1 |
| shared fields discovered | 3057 |
| shared fields documented | 2885 |
| shared basic fields discovered | 1466 |
| shared basic fields documented | 1395 |

## [aix](platforms/aix.md)

- [aix.fileset](capabilities/aix.fileset.md): 11/11 field routes; native contract unresolved.
- [aix.fix](capabilities/aix.fix.md): 11/11 field routes; native contract unresolved.

## [asa](platforms/asa.md)

- [asa.line](capabilities/asa.line.md): 7/7 field routes; native contract unresolved.
- [asa.version](capabilities/asa.version.md): 10/10 field routes; native contract unresolved.

## [esx](platforms/esx.md)

- [esx.host_account](capabilities/esx.host_account.md): 13/13 field routes; native contract unresolved.
- [esx.host_advancedsetting](capabilities/esx.host_advancedsetting.md): 7/7 field routes; native contract unresolved.
- [esx.host_service](capabilities/esx.host_service.md): 13/13 field routes; native contract unresolved.
- [esx.host_vib](capabilities/esx.host_vib.md): 13/13 field routes; native contract unresolved.

## [file](platforms/file.md)

- [file.hash](capabilities/file.hash.md): 19/19 field routes; native contract unresolved.

## [independent](platforms/independent.md)

- [independent.environmentvariable](capabilities/independent.environmentvariable.md): 10/10 field routes; native contract unresolved.
- [independent.family](capabilities/independent.family.md): 4/4 field routes; native contract unresolved.
- [independent.shellcommand](capabilities/independent.shellcommand.md): 21/21 field routes; native contract unresolved.
- [independent.sql](capabilities/independent.sql.md): 19/19 field routes; native contract unresolved.
- [independent.textfilecontent](capabilities/independent.textfilecontent.md): 28/28 field routes; native contract unresolved.
- [independent.unknown](capabilities/independent.unknown.md): 2/2 field routes; native contract unresolved.
- [independent.xmlfilecontent](capabilities/independent.xmlfilecontent.md): 20/20 field routes; native contract unresolved.
- [independent.yamlfilecontent](capabilities/independent.yamlfilecontent.md): 22/22 field routes; native contract unresolved.

## [ios](platforms/ios.md)

- [ios.bgpneighbor](capabilities/ios.bgpneighbor.md): 7/7 field routes; native contract unresolved.
- [ios.global](capabilities/ios.global.md): 5/5 field routes; native contract unresolved.
- [ios.interface](capabilities/ios.interface.md): 41/41 field routes; native contract unresolved.
- [ios.line](capabilities/ios.line.md): 7/7 field routes; native contract unresolved.
- [ios.routingprotocolauthintf](capabilities/ios.routingprotocolauthintf.md): 16/16 field routes; native contract unresolved.
- [ios.section](capabilities/ios.section.md): 9/9 field routes; native contract unresolved.
- [ios.snmpcommunity](capabilities/ios.snmpcommunity.md): 13/13 field routes; native contract unresolved.
- [ios.snmpgroup](capabilities/ios.snmpgroup.md): 19/19 field routes; native contract unresolved.
- [ios.snmphost](capabilities/ios.snmphost.md): 13/13 field routes; native contract unresolved.
- [ios.snmpuser](capabilities/ios.snmpuser.md): 17/17 field routes; native contract unresolved.

## [iosxe](platforms/iosxe.md)

- [iosxe.bgpneighbor](capabilities/iosxe.bgpneighbor.md): 7/7 field routes; native contract unresolved.
- [iosxe.global](capabilities/iosxe.global.md): 5/5 field routes; native contract unresolved.
- [iosxe.interface](capabilities/iosxe.interface.md): 41/41 field routes; native contract unresolved.
- [iosxe.line](capabilities/iosxe.line.md): 7/7 field routes; native contract unresolved.
- [iosxe.routingprotocolauthintf](capabilities/iosxe.routingprotocolauthintf.md): 16/16 field routes; native contract unresolved.
- [iosxe.section](capabilities/iosxe.section.md): 9/9 field routes; native contract unresolved.
- [iosxe.snmpcommunity](capabilities/iosxe.snmpcommunity.md): 13/13 field routes; native contract unresolved.
- [iosxe.snmpgroup](capabilities/iosxe.snmpgroup.md): 19/19 field routes; native contract unresolved.
- [iosxe.snmphost](capabilities/iosxe.snmphost.md): 13/13 field routes; native contract unresolved.
- [iosxe.snmpuser](capabilities/iosxe.snmpuser.md): 17/17 field routes; native contract unresolved.
- [iosxe.version](capabilities/iosxe.version.md): 12/12 field routes; native contract unresolved.

## [junos](platforms/junos.md)

- [junos.show](capabilities/junos.show.md): 7/7 field routes; native contract unresolved.

## [linux](platforms/linux.md)

- [linux.apparmorstatus](capabilities/linux.apparmorstatus.md): 16/16 field routes; native contract unresolved.
- [linux.dpkginfo](capabilities/linux.dpkginfo.md): 16/16 field routes; native contract unresolved.
- [linux.inetlisteningservers](capabilities/linux.inetlisteningservers.md): 25/25 field routes; native contract unresolved.
- [linux.kernelmodule](capabilities/linux.kernelmodule.md): 9/9 field routes; native contract unresolved.
- [linux.partition](capabilities/linux.partition.md): 24/24 field routes; native contract unresolved.
- [linux.rpminfo](capabilities/linux.rpminfo.md): 22/22 field routes; native contract unresolved.
- [linux.rpmverifyfile](capabilities/linux.rpmverifyfile.md): 61/61 field routes; native contract unresolved.
- [linux.rpmverifypackage](capabilities/linux.rpmverifypackage.md): 25/25 field routes; native contract unresolved.
- [linux.selinuxboolean](capabilities/linux.selinuxboolean.md): 10/10 field routes; native contract unresolved.
- [linux.selinuxsecuritycontext](capabilities/linux.selinuxsecuritycontext.md): 39/39 field routes; native contract unresolved.
- [linux.sestatus](capabilities/linux.sestatus.md): 12/12 field routes; native contract unresolved.
- [linux.systemdunitdependency](capabilities/linux.systemdunitdependency.md): 8/8 field routes; native contract unresolved.
- [linux.systemdunitproperty](capabilities/linux.systemdunitproperty.md): 11/11 field routes; native contract unresolved.

## [macos](platforms/macos.md)

- [macos.accountinfo](capabilities/macos.accountinfo.md): 19/19 field routes; native contract unresolved.
- [macos.authorizationdb](capabilities/macos.authorizationdb.md): 10/10 field routes; native contract unresolved.
- [macos.disabledservice](capabilities/macos.disabledservice.md): 6/6 field routes; native contract unresolved.
- [macos.diskinfo](capabilities/macos.diskinfo.md): 27/27 field routes; native contract unresolved.
- [macos.filevault](capabilities/macos.filevault.md): 4/4 field routes; native contract unresolved.
- [macos.firmwarepassword](capabilities/macos.firmwarepassword.md): 4/4 field routes; native contract unresolved.
- [macos.gatekeeper](capabilities/macos.gatekeeper.md): 8/8 field routes; native contract unresolved.
- [macos.installhistory](capabilities/macos.installhistory.md): 11/11 field routes; native contract unresolved.
- [macos.keychain](capabilities/macos.keychain.md): 9/9 field routes; native contract unresolved.
- [macos.launchd](capabilities/macos.launchd.md): 9/9 field routes; native contract unresolved.
- [macos.nvram](capabilities/macos.nvram.md): 7/7 field routes; native contract unresolved.
- [macos.plist](capabilities/macos.plist.md): 13/13 field routes; native contract unresolved.
- [macos.profiles](capabilities/macos.profiles.md): 6/6 field routes; native contract unresolved.
- [macos.pwpolicy](capabilities/macos.pwpolicy.md): 19/19 field routes; native contract unresolved.
- [macos.softwareupdate](capabilities/macos.softwareupdate.md): 6/6 field routes; native contract unresolved.
- [macos.systemprofiler](capabilities/macos.systemprofiler.md): 10/10 field routes; native contract unresolved.
- [macos.systemsetup](capabilities/macos.systemsetup.md): 40/40 field routes; native contract unresolved.

## [panos](platforms/panos.md)

- [panos.config](capabilities/panos.config.md): 7/7 field routes; native contract unresolved.
- [panos.version](capabilities/panos.version.md): 14/14 field routes; native contract unresolved.

## [solaris](platforms/solaris.md)

- [solaris.package.ips](capabilities/solaris.package.ips.md): 24/24 field routes; native contract unresolved.
- [solaris.package](capabilities/solaris.package.md): 15/15 field routes; native contract unresolved.
- [solaris.smf](capabilities/solaris.smf.md): 17/17 field routes; native contract unresolved.
- [solaris.smfproperty](capabilities/solaris.smfproperty.md): 15/15 field routes; native contract unresolved.

## [unix](platforms/unix.md)

- [unix.file](capabilities/unix.file.md): 56/56 field routes; native contract unresolved.
- [unix.interface](capabilities/unix.interface.md): 18/18 field routes; native contract unresolved.
- [unix.password](capabilities/unix.password.md): 20/20 field routes; native contract unresolved.
- [unix.process](capabilities/unix.process.md): 34/34 field routes; native contract unresolved.
- [unix.shadow](capabilities/unix.shadow.md): 24/24 field routes; native contract unresolved.
- [unix.sshd](capabilities/unix.sshd.md): 10/10 field routes; native contract unresolved.
- [unix.symlink](capabilities/unix.symlink.md): 7/7 field routes; native contract unresolved.
- [unix.sysctl](capabilities/unix.sysctl.md): 7/7 field routes; native contract unresolved.
- [unix.uname](capabilities/unix.uname.md): 14/14 field routes; native contract unresolved.

## [variable](platforms/variable.md)

- [variable.value](capabilities/variable.value.md): 4/4 field routes; native contract unresolved.

## [windows](platforms/windows.md)

- [windows.appcmd](capabilities/windows.appcmd.md): 13/13 field routes; native contract unresolved.
- [windows.appcmdlistconfig](capabilities/windows.appcmdlistconfig.md): 16/16 field routes; native contract unresolved.
- [windows.auditeventpolicysubcategories](capabilities/windows.auditeventpolicysubcategories.md): 122/122 field routes; native contract unresolved.
- [windows.cmdlet](capabilities/windows.cmdlet.md): 25/25 field routes; native contract unresolved.
- [windows.file](capabilities/windows.file.md): 48/48 field routes; native contract unresolved.
- [windows.fileeffectiverights](capabilities/windows.fileeffectiverights.md): 59/59 field routes; native contract unresolved.
- [windows.group_sid](capabilities/windows.group_sid.md): 15/15 field routes; native contract unresolved.
- [windows.lockoutpolicy](capabilities/windows.lockoutpolicy.md): 10/10 field routes; native contract unresolved.
- [windows.ntuser](capabilities/windows.ntuser.md): 37/39 field routes; native contract unresolved.
- [windows.passwordpolicy](capabilities/windows.passwordpolicy.md): 16/16 field routes; native contract unresolved.
- [windows.registry](capabilities/windows.registry.md): 22/22 field routes; native contract unresolved.
- [windows.regkeyeffectiverights](capabilities/windows.regkeyeffectiverights.md): 46/52 field routes; native contract unresolved.
- [windows.service](capabilities/windows.service.md): 28/28 field routes; native contract unresolved.
- [windows.sid](capabilities/windows.sid.md): 11/11 field routes; native contract unresolved.
- [windows.sid_sid](capabilities/windows.sid_sid.md): 11/11 field routes; native contract unresolved.
- [windows.user_sid](capabilities/windows.user_sid.md): 21/21 field routes; native contract unresolved.
- [windows.userright](capabilities/windows.userright.md): 9/9 field routes; native contract unresolved.
- [windows.wmi.query](capabilities/windows.wmi.query.md): 10/10 field routes; native contract unresolved.
- [windows.wuaupdatesearcher](capabilities/windows.wuaupdatesearcher.md): 24/24 field routes; native contract unresolved.

## Shared grammar

- [applicability.schema](shared/applicability.md)
- [assessment-language.schema](shared/assessment-language.md)
- [assessment-result-set.schema](shared/assessment-result-set.md)
- [assessment-result.schema](shared/assessment-result.md)
- [assessment.schema](shared/assessment.md)
- [benchmark-result.schema](shared/benchmark-result.md)
- [benchmark.schema](shared/benchmark.md)
- [capability-common.schema](shared/capability-common.md)
- [collected-item.schema](shared/collected-item.md)
- [collection-result.schema](shared/collection-result.md)
- [entity-result.schema](shared/entity-result.md)
- [expression-invocation.schema](shared/expression-invocation.md)
- [expression-result.schema](shared/expression-result.md)
- [expression.schema](shared/expression.md)
- [field-result.schema](shared/field-result.md)
- [item-materialization.schema](shared/item-materialization.md)
- [item-report.schema](shared/item-report.md)
- [manual-assessment-result.schema](shared/manual-assessment-result.md)
- [manual-assessment.schema](shared/manual-assessment.md)
- [native-selector.schema](shared/native-selector.md)
- [organizational-input.schema](shared/organizational-input.md)
- [package-manifest.schema](shared/package-manifest.md)
- [reported-elements.schema](shared/reported-elements.md)
- [require-result.schema](shared/require-result.md)
- [result-package-manifest.schema](shared/result-package-manifest.md)
- [result-types.schema](shared/result-types.md)
- [rule-result.schema](shared/rule-result.md)
- [rule.schema](shared/rule.md)
- [scan-result.schema](shared/scan-result.md)
- [state-result.schema](shared/state-result.md)
- [tailoring.schema](shared/tailoring.md)
- [test-result.schema](shared/test-result.md)
- [variable-expression.schema](shared/variable-expression.md)
- [variable-function-expression.schema](shared/variable-function-expression.md)
- [variable-result.schema](shared/variable-result.md)
