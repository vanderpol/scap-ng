# B source specimens — six-stream capability implementation

**Unmodified source semantics have NOT been proven. These are preserved
parsed YAML research specimens from the earlier published 0.3
authoring archive, not source SCAP 1.4 XML and not executable 0.4-B.**

Specimens span common families from the complete six-stream corpus;
small and larger documents exercise different conversion complexity.

| Family | Source Assessment | Referencing streams | Tests | Source specimen |
| --- | --- | --- | ---: | --- |
| independent.shellcommand | SV-214268.automated | apache_server_2-4_unix_server | 5 | [independent-shellcommand-1-3d964d126ca8.source.yaml](independent-shellcommand-1-3d964d126ca8.source.yaml) |
| windows.wmi.query | SV-253265.automated | ms_windows_11 | 1 | [windows-wmi-query-0-a5018a53e0f6.source.yaml](windows-wmi-query-0-a5018a53e0f6.source.yaml) |
| windows.registry | SV-253274.automated | ms_windows_11 | 5 | [windows-registry-1-2db73c819346.source.yaml](windows-registry-1-2db73c819346.source.yaml) |
| windows.registry | SV-253291.automated | ms_windows_11 | 1 | [windows-registry-0-de183f784659.source.yaml](windows-registry-0-de183f784659.source.yaml) |
| windows.registry/nested_state_all | SV-253358.automated | ms_windows_11 | 1 | [windows-registry-state-all-0fef40d33c90.source.yaml](windows-registry-state-all-0fef40d33c90.source.yaml) |
| windows.userright | SV-253495.automated | ms_windows_11 | 7 | [windows-userright-1-39dad4df5336.source.yaml](windows-userright-1-39dad4df5336.source.yaml) |
| independent.shellcommand | SV-258038.automated | rhel_9 | 1 | [independent-shellcommand-0-365f46522e9e.source.yaml](independent-shellcommand-0-365f46522e9e.source.yaml) |
| windows.wmi.query | SV-278001.automated | ms_windows_server_2025 | 5 | [windows-wmi-query-1-c3af977226de.source.yaml](windows-wmi-query-1-c3af977226de.source.yaml) |
| independent.textfilecontent54 | ng.shared.etc-chrony-conf-cmdport-option-is-set-to-0 | oracle_linux_9, rhel_9 | 1 | [independent-textfilecontent54-0-4c14428014be.source.yaml](independent-textfilecontent54-0-4c14428014be.source.yaml) |
| independent.textfilecontent54 | ng.shared.linux-must-audit-all-uses-of-the-setxattr-fsetxattr-lsetxattr-removexatt | oracle_linux_9, rhel_9 | 24 | [independent-textfilecontent54-1-48fa5787cc44.source.yaml](independent-textfilecontent54-1-48fa5787cc44.source.yaml) |
| linux.partition | ng.shared.linux-must-use-a-separate-file-system-for-the-system-audit-data-path | oracle_linux_9, rhel_9 | 2 | [linux-partition-1-d9f2e60f478b.source.yaml](linux-partition-1-d9f2e60f478b.source.yaml) |
| windows.userright | ng.shared.lock-pages-in-memory-none | ms_windows_11, ms_windows_server_2025 | 1 | [windows-userright-0-d35c0612bfc5.source.yaml](windows-userright-0-d35c0612bfc5.source.yaml) |
| linux.partition | ng.shared.var-tmp-is-mounted | oracle_linux_9, rhel_9 | 1 | [linux-partition-0-88d5c4811f61.source.yaml](linux-partition-0-88d5c4811f61.source.yaml) |

**Source limitations:** the original OVAL Test/State/Object/Variable
semantics, shared source references, provider statuses and scanner
results are not established by preserving a YAML document.
This B-only specimen set enables implementation research; it is
not an A/B bake-off or a claim of any native conversion rate.

