# OVAL 5.12.3 Object behavior disposition for SCAP-NG 0.1.0

**Status:** current behavior-coverage checkpoint, 2026-10-02.  
**Authority:** fresh successful `Audit complete upstream OVAL 5.12.3 XSD semantics` run at commit `4021072`.

The authoritative audit found **36/36 named behavior types structurally resolved**, **44 behavior-element declarations**, all 44 optional, and no transitive-inheritance blockers. This table separates behavior-bearing source Objects that are part of the current reviewed native capability set from source families that are not currently claimed as native 0.1.0 capabilities.

For a row marked **mapped**, the corresponding capability mapping is the release-critical contract and SHALL disposition every non-deprecated behavior that can affect collection/results. A row marked **not-current** is not evidence that the source family is removed from OVAL; it means only that this repository does not currently claim a reviewed native 0.1.0 mapping for that Object family. Its migration/deprecation status remains governed by the capability crosswalk.

| Source schema | OVAL Object | Behavior type | 0.1.0 disposition |
| --- | --- | --- | --- |
| `esx-definitions-schema.xsd` | `patch56_object` | `esx-def:Patch56Behaviors` | **not-current** — no reviewed native 0.1.0 mapping claim |
| `esx-definitions-schema.xsd` | `patch_object` | `esx-def:PatchBehaviors` | **not-current** — no reviewed native 0.1.0 mapping claim |
| `esx-definitions-schema.xsd` | `visdkmanagedobject_object` | `esx-def:ViSdkManagedEntityBehaviors` | **not-current** — no reviewed native 0.1.0 mapping claim |
| `hpux-definitions-schema.xsd` | `patch53_object` | `hpux-def:Patch53Behaviors` | **not-current** — no reviewed native 0.1.0 mapping claim |
| `independent-definitions-schema.xsd` | `filehash_object` | `ind-def:FileBehaviors` | **not-current** — no reviewed native 0.1.0 mapping claim |
| `independent-definitions-schema.xsd` | `filehash58_object` | `ind-def:FileBehaviors` | **mapped** → `file.hash` |
| `independent-definitions-schema.xsd` | `ldap_object` | `ind-def:LdapBehaviors` | **not-current** — no reviewed native 0.1.0 mapping claim |
| `independent-definitions-schema.xsd` | `ldap57_object` | `ind-def:LdapBehaviors` | **not-current** — no reviewed native 0.1.0 mapping claim |
| `independent-definitions-schema.xsd` | `shellcommand_object` | `ind-def:ShellCommandBehaviors` | **mapped** → `independent.shellcommand` |
| `independent-definitions-schema.xsd` | `textfilecontent54_object` | `ind-def:Textfilecontent54Behaviors` | **mapped** → `independent.textfilecontent54` |
| `independent-definitions-schema.xsd` | `textfilecontent_object` | `ind-def:FileBehaviors` | **not-current** — no reviewed native 0.1.0 mapping claim |
| `independent-definitions-schema.xsd` | `xmlfilecontent_object` | `ind-def:XMLFileContentBehaviors` | **mapped** → `independent.xmlfilecontent` |
| `independent-definitions-schema.xsd` | `yamlfilecontent_object` | `ind-def:FileBehaviors` | **mapped** → `independent.yamlfilecontent` |
| `linux-definitions-schema.xsd` | `rpminfo_object` | `linux-def:RpmInfoBehaviors` | **mapped** → `linux.rpminfo` |
| `linux-definitions-schema.xsd` | `rpmverify_object` | `linux-def:RpmVerifyBehaviors` | **not-current** — no reviewed native 0.1.0 mapping claim |
| `linux-definitions-schema.xsd` | `rpmverifyfile_object` | `linux-def:RpmVerifyFileBehaviors` | **mapped** → `linux.rpmverifyfile` |
| `linux-definitions-schema.xsd` | `rpmverifypackage_object` | `linux-def:RpmVerifyPackageBehaviors` | **mapped** → `linux.rpmverifypackage` |
| `linux-definitions-schema.xsd` | `selinuxsecuritycontext_object` | `linux-def:FileBehaviors` | **mapped** → `linux.selinuxsecuritycontext` |
| `solaris-definitions-schema.xsd` | `packagecheck_object` | `sol-def:PackageCheckBehaviors` | **not-current** — no reviewed native 0.1.0 mapping claim |
| `solaris-definitions-schema.xsd` | `patch54_object` | `sol-def:PatchBehaviors` | **not-current** — no reviewed native 0.1.0 mapping claim |
| `unix-definitions-schema.xsd` | `file_object` | `unix-def:FileBehaviors` | **mapped** → `unix.file` |
| `unix-definitions-schema.xsd` | `fileextendedattribute_object` | `unix-def:FileBehaviors` | **not-current** — no reviewed native 0.1.0 mapping claim |
| `unix-definitions-schema.xsd` | `sccs_object` | `unix-def:FileBehaviors` | **not-current** — no reviewed native 0.1.0 mapping claim |
| `windows-definitions-schema.xsd` | `accesstoken_object` | `win-def:AccesstokenBehaviors` | **not-current** — no reviewed native 0.1.0 mapping claim |
| `windows-definitions-schema.xsd` | `file_object` | `win-def:FileBehaviors` | **mapped** → `windows.file` |
| `windows-definitions-schema.xsd` | `fileauditedpermissions53_object` | `win-def:FileAuditPermissions53Behaviors` | **not-current** — no reviewed native 0.1.0 mapping claim |
| `windows-definitions-schema.xsd` | `fileauditedpermissions_object` | `win-def:FileAuditPermissionsBehaviors` | **not-current** — no reviewed native 0.1.0 mapping claim |
| `windows-definitions-schema.xsd` | `fileeffectiverights53_object` | `win-def:FileEffectiveRights53Behaviors` | **mapped** → `windows.fileeffectiverights53` |
| `windows-definitions-schema.xsd` | `fileeffectiverights_object` | `win-def:FileEffectiveRightsBehaviors` | **not-current** — no reviewed native 0.1.0 mapping claim |
| `windows-definitions-schema.xsd` | `junction_object` | `win-def:FileBehaviors` | **not-current** — no reviewed native 0.1.0 mapping claim |
| `windows-definitions-schema.xsd` | `ntuser_object` | `win-def:NTUserBehaviors` | **mapped** → `windows.ntuser` |
| `windows-definitions-schema.xsd` | `peheader_object` | `win-def:FileBehaviors` | **not-current** — no reviewed native 0.1.0 mapping claim |
| `windows-definitions-schema.xsd` | `printereffectiverights_object` | `win-def:PrinterEffectiveRightsBehaviors` | **not-current** — no reviewed native 0.1.0 mapping claim |
| `windows-definitions-schema.xsd` | `registry_object` | `win-def:RegistryBehaviors` | **mapped** → `windows.registry` |
| `windows-definitions-schema.xsd` | `regkeyauditedpermissions53_object` | `win-def:RegkeyAuditPermissions53Behaviors` | **not-current** — no reviewed native 0.1.0 mapping claim |
| `windows-definitions-schema.xsd` | `regkeyauditedpermissions_object` | `win-def:RegkeyAuditPermissionsBehaviors` | **not-current** — no reviewed native 0.1.0 mapping claim |
| `windows-definitions-schema.xsd` | `regkeyeffectiverights53_object` | `win-def:RegkeyEffectiveRights53Behaviors` | **mapped** → `windows.regkeyeffectiverights53` |
| `windows-definitions-schema.xsd` | `regkeyeffectiverights_object` | `win-def:RegkeyEffectiveRightsBehaviors` | **not-current** — no reviewed native 0.1.0 mapping claim |
| `windows-definitions-schema.xsd` | `serviceeffectiverights_object` | `win-def:ServiceEffectiveRightsBehaviors` | **not-current** — no reviewed native 0.1.0 mapping claim |
| `windows-definitions-schema.xsd` | `sharedresourceauditedpermissions_object` | `win-def:SharedResourceAuditedPermissionsBehaviors` | **not-current** — no reviewed native 0.1.0 mapping claim |
| `windows-definitions-schema.xsd` | `sharedresourceeffectiverights_object` | `win-def:SharedResourceEffectiveRightsBehaviors` | **not-current** — no reviewed native 0.1.0 mapping claim |
| `windows-definitions-schema.xsd` | `sid_object` | `win-def:SidBehaviors` | **mapped** → `windows.sid` |
| `windows-definitions-schema.xsd` | `sid_sid_object` | `win-def:SidSidBehaviors` | **mapped** → `windows.sid_sid` |
| `windows-definitions-schema.xsd` | `wuaupdatesearcher_object` | `win-def:WuaUpdateSearcherBehaviors` | **mapped** → `windows.wuaupdatesearcher` |

## Release-critical mapped behavior families

Current mapped rows use explicit native contracts rather than hidden collector defaults:

- file and hierarchy traversal is represented by shared native traversal primitives and capability-specific applicability rules;
- `independent.shellcommand` materializes both error behaviors;
- `independent.textfilecontent54` materializes regex/item-creation behaviors;
- `independent.xmlfilecontent` now materializes `item_creation` in addition to shared traversal;
- `linux.rpminfo`, RPM verify capabilities, Windows NTUSER, SID/SID-SID, and Windows Update Searcher expose their behavior-affecting defaults explicitly;
- deprecated source behavior values (for example upward recursion and deprecated Windows view/group-expansion surfaces where applicable) are migration errors or documented removals rather than silent native options.

## Verification rule

A future capability mapping for any **not-current** row SHALL explicitly disposition its behavior type before the capability is marked reviewed. The maintained XSD audit SHALL remain the discovery authority; this document is a review ledger, not a replacement parser.

The mapped subset SHALL remain covered by focused schema/semantic fixtures and the maintained smoke/current-design/Self-Assertion regressions.
