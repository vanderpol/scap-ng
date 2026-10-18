# SCAP-NG 0.4-B six-STIG automated source blockers

**Source-shape inventory only; 0.4-B is NOT yet a complete converter.**
Counts below are distinct *unsupported automated Assessments* referencing
each capability/feature; a multi-Test Assessment may appear in multiple rows.

**Unsupported automated Assessments: 799**.

## Highest-volume capability families

| Source Test capability | Unsupported Assessments containing it |
| --- | ---: |
| independent.textfilecontent54 | 220 |
| windows.registry | 156 |
| independent.shellcommand | 88 |
| unix.file | 76 |
| windows.auditeventpolicysubcategories | 53 |
| windows.userright | 49 |
| linux.rpminfo | 38 |
| unix.sysctl | 33 |
| windows.wmi.query | 32 |
| linux.partition | 31 |
| linux.systemdunitproperty | 15 |
| windows.cmdlet | 15 |
| windows.fileeffectiverights53 | 13 |
| variable.value | 12 |
| windows.passwordpolicy | 9 |
| unix.password | 4 |
| windows.ntuser | 4 |
| unix.symlink | 3 |
| windows.file | 3 |
| windows.lockoutpolicy | 3 |
| windows.service | 3 |
| windows.sid_sid | 2 |
| linux.selinuxsecuritycontext | 1 |
| unix.interface | 1 |
| unix.shadow | 1 |
| windows.appcmdlistconfig | 1 |
| windows.user_sid55 | 1 |

## Complex-source feature markers

| Feature | Unsupported Assessments containing it |
| --- | ---: |
| states | 627 |
| multiple_tests | 248 |
| set_or_filter | 110 |
| shared_objects | 77 |
| variables | 77 |
| value_match | 60 |
| record | 39 |
| for_each | 7 |

## Per-stream capability matrix

### apache_server_2-4_unix_server

| Capability | Referenced unsupported Assessments |
| --- | ---: |
| independent.shellcommand | 22 |

### ms_windows_11

| Capability | Referenced unsupported Assessments |
| --- | ---: |
| windows.registry | 135 |
| windows.auditeventpolicysubcategories | 43 |
| windows.userright | 29 |
| windows.wmi.query | 15 |
| windows.cmdlet | 9 |
| independent.shellcommand | 7 |
| windows.passwordpolicy | 7 |
| windows.ntuser | 4 |
| windows.fileeffectiverights53 | 3 |
| windows.lockoutpolicy | 3 |
| windows.sid_sid | 2 |
| variable.value | 1 |
| windows.file | 1 |
| windows.service | 1 |
| windows.user_sid55 | 1 |

### ms_windows_server_2025

| Capability | Referenced unsupported Assessments |
| --- | ---: |
| windows.registry | 111 |
| windows.auditeventpolicysubcategories | 43 |
| windows.userright | 39 |
| windows.wmi.query | 24 |
| independent.shellcommand | 22 |
| windows.fileeffectiverights53 | 8 |
| independent.textfilecontent54 | 7 |
| windows.cmdlet | 7 |
| windows.passwordpolicy | 7 |
| windows.lockoutpolicy | 3 |
| windows.service | 2 |
| windows.appcmdlistconfig | 1 |
| windows.file | 1 |
| windows.ntuser | 1 |

### ms_windows_server_dns

| Capability | Referenced unsupported Assessments |
| --- | ---: |
| independent.shellcommand | 16 |
| variable.value | 2 |
| windows.fileeffectiverights53 | 2 |
| windows.userright | 2 |
| windows.auditeventpolicysubcategories | 1 |
| windows.file | 1 |

### oracle_linux_9

| Capability | Referenced unsupported Assessments |
| --- | ---: |
| independent.textfilecontent54 | 194 |
| unix.file | 64 |
| linux.rpminfo | 33 |
| unix.sysctl | 33 |
| linux.partition | 31 |
| linux.systemdunitproperty | 15 |
| variable.value | 9 |
| independent.shellcommand | 7 |
| unix.password | 4 |
| unix.symlink | 2 |
| linux.selinuxsecuritycontext | 1 |
| unix.interface | 1 |
| unix.shadow | 1 |

### rhel_9

| Capability | Referenced unsupported Assessments |
| --- | ---: |
| independent.textfilecontent54 | 194 |
| unix.file | 62 |
| linux.rpminfo | 35 |
| unix.sysctl | 33 |
| linux.partition | 31 |
| independent.shellcommand | 21 |
| linux.systemdunitproperty | 14 |
| variable.value | 9 |
| unix.password | 4 |
| unix.symlink | 3 |
| linux.selinuxsecuritycontext | 1 |
| unix.interface | 1 |
| unix.shadow | 1 |

This is a **development queue**, not a reason to discard infrequent OVAL
semantics. B may use proven native lowering or a correct compiler-owned
compatibility operation, but the resulting content must actually execute.
Original SCAP 1.4 XML/source parity and six-state scanner semantics
are independent gates, currently open.

The [machine-readable per-Assessment blockers](conversion-blockers.json)
retain source paths and IDs. Full census: [conversion-progress](conversion-progress.md).
Tracking: [#237](https://github.com/vanderpol/scap-ng/issues/237).
