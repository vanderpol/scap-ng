# Four-anchor SCAP-NG assessment reuse

Measured from the pinned NIWC SCAP 1.4 RHEL 9, Oracle Linux 9, Windows 11, and Windows Server 2025 benchmarks after conversion to the common canonical SCAP-NG semantic model.

## Measured exact reuse

- Generic automated assessment instances: **1331**
- Unique exact technical assessments: **804**
- Duplicate assessment definitions avoidable through exact reuse: **527**
- Exact maintenance-unit reduction in this four-benchmark sample: **39.59%**
- Cross-benchmark exact-reuse groups: **525**

## Rule alignment evidence

- Groups aligned by identical normalized Check Text: **9**
- Groups aligned by equivalent full OVAL semantics: **525**
- Total aligned cross-benchmark rule pairs: **530**
- Pairs supported by both Check Text and OVAL equivalence: **7**
- Check Text-only aligned pairs: **2**
- OVAL-equivalence-only aligned pairs: **521**

Check Text equality establishes policy alignment. Equivalent full OVAL semantics establishes alignment and exact automation-reuse evidence.

## Parameterization candidates

- Unique semantic shapes after abstracting literals: **400**
- Candidate duplicate definitions avoidable if every candidate is proven safely parameterizable: **931**
- Candidate reduction upper bound: **69.95%**

Parameterization numbers are an upper bound, not a reuse claim. Each candidate must be reviewed before being treated as one reusable assessment.

## Cost model

The report intentionally uses maintenance units rather than invented dollar assumptions. Organizations can apply their own review hours, change frequency, and loaded labor rate to the measured duplicate units avoided.

## Largest cross-benchmark exact-reuse groups

- **4 instances across 2 benchmarks** — oracle-linux9, rhel9
  - oracle-linux9: xccdf_mil.disa.stig_rule_SV-271800r1092112_rule — OL 9 /etc/gshadow file must be group-owned by root.
  - oracle-linux9: xccdf_mil.disa.stig_rule_SV-271802r1092118_rule — OL 9 /etc/gshadow file must be owned by root.
  - rhel9: xccdf_mil.disa.stig_rule_SV-257902r991589_rule — RHEL 9 /etc/gshadow file must be owned by root.
  - rhel9: xccdf_mil.disa.stig_rule_SV-257903r991589_rule — RHEL 9 /etc/gshadow file must be group-owned by root.
- **2 instances across 2 benchmarks** — oracle-linux9, rhel9
  - oracle-linux9: xccdf_mil.disa.stig_rule_SV-271450r1092466_rule — OL 9 must be configured to disable USB mass storage.
  - rhel9: xccdf_mil.disa.stig_rule_SV-258034r1051267_rule — RHEL 9 must be configured to disable USB mass storage.
- **2 instances across 2 benchmarks** — windows-server-2025, windows11
  - windows-server-2025: xccdf_mil.disa.stig_rule_SV-278111r1182065_rule — Windows Server 2025 File Explorer shell protocol must run in protected mode.
  - windows11: xccdf_mil.disa.stig_rule_SV-253398r991589_rule — File Explorer shell protocol must run in protected mode.
- **2 instances across 2 benchmarks** — oracle-linux9, rhel9
  - oracle-linux9: xccdf_mil.disa.stig_rule_SV-271797r1092103_rule — OL 9 /etc/group- file must be owned by root.
  - rhel9: xccdf_mil.disa.stig_rule_SV-257900r991589_rule — RHEL 9 /etc/group- file must be owned by root.
- **2 instances across 2 benchmarks** — oracle-linux9, rhel9
  - oracle-linux9: xccdf_mil.disa.stig_rule_SV-271488r1091176_rule — OL 9 must have the openssh-clients package installed.
  - rhel9: xccdf_mil.disa.stig_rule_SV-257980r1045016_rule — RHEL 9 must have the openssh-clients package installed.
- **2 instances across 2 benchmarks** — oracle-linux9, rhel9
  - oracle-linux9: xccdf_mil.disa.stig_rule_SV-271742r1091938_rule — OL 9 debug-shell systemd service must be disabled.
  - rhel9: xccdf_mil.disa.stig_rule_SV-257786r1044834_rule — RHEL 9 debug-shell systemd service must be disabled.
- **2 instances across 2 benchmarks** — oracle-linux9, rhel9
  - oracle-linux9: xccdf_mil.disa.stig_rule_SV-271483r1091161_rule — OL 9 networked systems must have and implement SSH to protect the confidentiality and integrity of transmitted and received information, as well as information during preparation for transmission.
  - rhel9: xccdf_mil.disa.stig_rule_SV-257979r958908_rule — All RHEL 9 networked systems must have and implement SSH to protect the confidentiality and integrity of transmitted and received information, as well as information during preparation for transmission.
- **2 instances across 2 benchmarks** — oracle-linux9, rhel9
  - oracle-linux9: xccdf_mil.disa.stig_rule_SV-271826r1092190_rule — OL 9 audit tools must have a mode of 0755 or less permissive.
  - rhel9: xccdf_mil.disa.stig_rule_SV-257887r991557_rule — RHEL 9 audit tools must have a mode of 0755 or less permissive.
- **2 instances across 2 benchmarks** — oracle-linux9, rhel9
  - oracle-linux9: xccdf_mil.disa.stig_rule_SV-271440r1092462_rule — OL 9 must be configured so that the graphical display manager is not the default target unless approved.
  - rhel9: xccdf_mil.disa.stig_rule_SV-257781r991589_rule — The graphical display manager must not be the default target on RHEL 9 unless approved.
- **2 instances across 2 benchmarks** — windows-server-2025, windows11
  - windows-server-2025: xccdf_mil.disa.stig_rule_SV-278126r1181084_rule — Windows Server 2025 Windows Remote Management (WinRM) client must not allow unencrypted traffic.
  - windows11: xccdf_mil.disa.stig_rule_SV-253417r958848_rule — The Windows Remote Management (WinRM) client must not allow unencrypted traffic.
- **2 instances across 2 benchmarks** — windows-server-2025, windows11
  - windows-server-2025: xccdf_mil.disa.stig_rule_SV-278180r1182286_rule — Windows Server 2025 must restrict unauthenticated Remote Procedure Call (RPC) clients from connecting to the RPC server on domain-joined member servers and stand-alone or nondomain-joined systems.
  - windows11: xccdf_mil.disa.stig_rule_SV-253383r971545_rule — Unauthenticated RPC clients must be restricted from connecting to the RPC server.
- **2 instances across 2 benchmarks** — oracle-linux9, rhel9
  - oracle-linux9: xccdf_mil.disa.stig_rule_SV-271664r1091704_rule — OL 9 must mount /var/tmp with the noexec option.
  - rhel9: xccdf_mil.disa.stig_rule_SV-257877r958804_rule — RHEL 9 must mount /var/tmp with the noexec option.
- **2 instances across 2 benchmarks** — oracle-linux9, rhel9
  - oracle-linux9: xccdf_mil.disa.stig_rule_SV-271642r1092593_rule — OL 9 must prevent code from being executed on file systems that are imported via Network File System (NFS).
  - rhel9: xccdf_mil.disa.stig_rule_SV-257855r1044936_rule — RHEL 9 must prevent code from being executed on file systems that are imported via Network File System (NFS).
- **2 instances across 2 benchmarks** — oracle-linux9, rhel9
  - oracle-linux9: xccdf_mil.disa.stig_rule_SV-271721r1091875_rule — OL 9 SSHD must accept public key authentication.
  - rhel9: xccdf_mil.disa.stig_rule_SV-257983r1045024_rule — RHEL 9 SSHD must accept public key authentication.
- **2 instances across 2 benchmarks** — windows-server-2025, windows11
  - windows-server-2025: xccdf_mil.disa.stig_rule_SV-278056r1180874_rule — Windows Server 2025 must be configured to audit Logon/Logoff - Account Lockout failures.
  - windows11: xccdf_mil.disa.stig_rule_SV-253313r991578_rule — The system must be configured to audit Logon/Logoff - Account Lockout failures.
- **2 instances across 2 benchmarks** — oracle-linux9, rhel9
  - oracle-linux9: xccdf_mil.disa.stig_rule_SV-271633r1091611_rule — OL 9 passwords must be created with a minimum of 15 characters.
  - rhel9: xccdf_mil.disa.stig_rule_SV-258107r1045218_rule — RHEL 9 passwords must be created with a minimum of 15 characters.
- **2 instances across 2 benchmarks** — oracle-linux9, rhel9
  - oracle-linux9: xccdf_mil.disa.stig_rule_SV-271752r1091968_rule — OL 9 must be configured so that the x86 Ctrl-Alt-Delete key sequence is disabled.
  - rhel9: xccdf_mil.disa.stig_rule_SV-257785r1044833_rule — The x86 Ctrl-Alt-Delete key sequence must be disabled on RHEL 9.
- **2 instances across 2 benchmarks** — oracle-linux9, rhel9
  - oracle-linux9: xccdf_mil.disa.stig_rule_SV-271655r1091677_rule — OL 9 must mount /tmp with the nosuid option.
  - rhel9: xccdf_mil.disa.stig_rule_SV-257868r958804_rule — RHEL 9 must mount /tmp with the nosuid option.
- **2 instances across 2 benchmarks** — windows-server-2025, windows11
  - windows-server-2025: xccdf_mil.disa.stig_rule_SV-278065r1180901_rule — Windows Server 2025 must be configured to audit Object Access - Removable Storage failures.
  - windows11: xccdf_mil.disa.stig_rule_SV-253323r991583_rule — The system must be configured to audit Object Access - Removable Storage failures.
- **2 instances across 2 benchmarks** — oracle-linux9, rhel9
  - oracle-linux9: xccdf_mil.disa.stig_rule_SV-271841r1092235_rule — OL 9 must log username information when unsuccessful logon attempts occur.
  - rhel9: xccdf_mil.disa.stig_rule_SV-258070r1045153_rule — RHEL 9 must log username information when unsuccessful logon attempts occur.

See assessment-reuse.json for all exact groups, parameterization candidates, rule mappings, and the organization-specific cost formulas.

See reuse-views/ for the same measured exact reuse rendered as combined shared-rule overlays, split assessment bindings, and Ansible-inspired shared assessments.
