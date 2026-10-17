# 0.4-B six-STIG feature coverage inventory

**Research-only corpus profile. Not native translation, not source-equivalent
execution, and not an A/B comparison.** Input: published SCAP-NG 0.3
six-STIG authoring archive, *not* raw SCAP 1.4 XML.

| Stream | Rules | Referenced Assessments | Test nodes |
| --- | ---: | ---: | ---: |
| apache_server_2-4_unix_server | 45 | 67 | 56 |
| ms_windows_11 | 257 | 502 | 356 |
| ms_windows_server_2025 | 291 | 550 | 373 |
| ms_windows_server_dns | 81 | 94 | 60 |
| oracle_linux_9 | 448 | 854 | 615 |
| rhel_9 | 445 | 861 | 649 |

**2395 distinct Assessment IDs** are
covered across six source streams; shared Assessments are counted once
globally but can appear in more than one stream's row.

## Capability names and structural markers by stream

Values below count **referenced Assessments with a marker key**, not
execution paths or runtime equivalence. Complete details, all discovered
capability names, source digests and representative IDs are in
[feature-inventory.json](feature-inventory.json).

### apache_server_2-4_unix_server

Test capability names: independent.shellcommand (56)

Key-presence markers: evaluate (22), existence (22), field (22), object (22), states (22), variable (22), variables (22)

### ms_windows_11

Test capability names: windows.registry (168), windows.auditeventpolicysubcategories (72), windows.userright (40), windows.wmi.query (21), independent.shellcommand (12), windows.cmdlet (12), windows.lockoutpolicy (7), windows.passwordpolicy (7), windows.fileeffectiverights53 (6), windows.ntuser (4), windows.file (2), windows.sid_sid (2)

Key-presence markers: evaluate (245), existence (245), field (235), states (233), object (193), fields (23), record (22), variable (9), variables (9), filter (1)

### ms_windows_server_2025

Test capability names: windows.registry (124), windows.auditeventpolicysubcategories (71), windows.userright (52), windows.wmi.query (33), independent.shellcommand (30), windows.fileeffectiverights53 (26), windows.cmdlet (10), independent.textfilecontent54 (7), windows.lockoutpolicy (7), windows.passwordpolicy (7), windows.file (2), windows.service (2)

Key-presence markers: evaluate (259), existence (259), field (249), states (247), object (206), fields (26), record (24), variable (9), variables (9), filter (3)

### ms_windows_server_dns

Test capability names: independent.shellcommand (49), windows.userright (4), variable.value (3), windows.fileeffectiverights53 (2), windows.auditeventpolicysubcategories (1), windows.file (1)

Key-presence markers: evaluate (21), existence (21), field (21), object (20), states (19), variable (15), variables (15)

### oracle_linux_9

Test capability names: independent.textfilecontent54 (388), unix.file (80), linux.rpminfo (33), unix.sysctl (33), linux.partition (32), linux.systemdunitproperty (21), variable.value (9), independent.shellcommand (8), unix.password (5), unix.shadow (2), unix.symlink (2), linux.selinuxsecuritycontext (1)

Key-presence markers: evaluate (406), existence (406), object (406), field (277), states (260), variable (21), variables (21), for_each (7)

### rhel_9

Test capability names: independent.textfilecontent54 (400), unix.file (73), linux.rpminfo (35), unix.sysctl (33), linux.partition (32), independent.shellcommand (26), linux.systemdunitproperty (19), unix.symlink (13), variable.value (9), unix.password (5), unix.shadow (2), linux.selinuxsecuritycontext (1)

Key-presence markers: evaluate (416), existence (416), object (416), field (287), states (271), variable (23), variables (23), for_each (7)

## Hard boundary

No assessed source here is marked native-converted or executable.
No source Test/State/Object/Variable semantic parity is asserted.
This inventory is a B development input: next implement the features
and compatibility IR families against pinned source fixtures before
claiming B's six-content-stream capability readiness.
The A/B bake-off remains postponed.
