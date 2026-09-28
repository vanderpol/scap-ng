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
  - oracle-linux9: xccdf_mil.disa.stig_rule_SV-271636r1091620_rule — OL 9 must enforce password complexity by requiring that at least one special character be used.
  - rhel9: xccdf_mil.disa.stig_rule_SV-258109r1045220_rule — RHEL 9 must enforce password complexity by requiring that at least one special character be used.
- **2 instances across 2 benchmarks** — oracle-linux9, rhel9
  - oracle-linux9: xccdf_mil.disa.stig_rule_SV-271552r1092524_rule — OL 9 must audit all uses of the userhelper command.
  - rhel9: xccdf_mil.disa.stig_rule_SV-258208r1045409_rule — RHEL 9 must audit all uses of the userhelper command.
- **2 instances across 2 benchmarks** — windows-server-2025, windows11
  - windows-server-2025: xccdf_mil.disa.stig_rule_SV-278095r1180991_rule — Windows Server 2025 network selection user interface (UI) must not be displayed on the logon screen.
  - windows11: xccdf_mil.disa.stig_rule_SV-253378r958478_rule — The network selection user interface (UI) must not be displayed on the logon screen.
- **2 instances across 2 benchmarks** — oracle-linux9, rhel9
  - oracle-linux9: xccdf_mil.disa.stig_rule_SV-271742r1091938_rule — OL 9 debug-shell systemd service must be disabled.
  - rhel9: xccdf_mil.disa.stig_rule_SV-257786r1044834_rule — RHEL 9 debug-shell systemd service must be disabled.
- **2 instances across 2 benchmarks** — windows-server-2025, windows11
  - windows-server-2025: xccdf_mil.disa.stig_rule_SV-278189r1182305_rule — The Windows Server 2025 "Enable computer and user accounts to be trusted for delegation" user right must not be assigned to any groups or accounts on domain-joined member servers and stand-alone or nondomain-joined systems.
  - windows11: xccdf_mil.disa.stig_rule_SV-253496r958726_rule — The "Enable computer and user accounts to be trusted for delegation" user right must not be assigned to any groups or accounts.
- **2 instances across 2 benchmarks** — oracle-linux9, rhel9
  - oracle-linux9: xccdf_mil.disa.stig_rule_SV-271596r1091500_rule — OL 9 must allocate audit record storage capacity to store at least one week's worth of audit records.
  - rhel9: xccdf_mil.disa.stig_rule_SV-258155r1045300_rule — RHEL 9 must allocate audit record storage capacity to store at least one week's worth of audit records.
- **2 instances across 2 benchmarks** — oracle-linux9, rhel9
  - oracle-linux9: xccdf_mil.disa.stig_rule_SV-271523r1091281_rule — OL 9 must check the GPG signature of locally installed software packages before installation.
  - rhel9: xccdf_mil.disa.stig_rule_SV-257821r1015077_rule — RHEL 9 must check the GPG signature of locally installed software packages before installation.
- **2 instances across 2 benchmarks** — oracle-linux9, rhel9
  - oracle-linux9: xccdf_mil.disa.stig_rule_SV-271608r1091536_rule — OL 9 must implement certificate status checking for multifactor authentication (MFA).
  - rhel9: xccdf_mil.disa.stig_rule_SV-258123r1134923_rule — RHEL 9 must implement certificate status checking for multifactor authentication.
- **2 instances across 2 benchmarks** — oracle-linux9, rhel9
  - oracle-linux9: xccdf_mil.disa.stig_rule_SV-271726r1091890_rule — OL 9 must not be configured to bypass password requirements for privilege escalation.
  - rhel9: xccdf_mil.disa.stig_rule_SV-258118r1050789_rule — RHEL 9 must not be configured to bypass password requirements for privilege escalation.
- **2 instances across 2 benchmarks** — oracle-linux9, rhel9
  - oracle-linux9: xccdf_mil.disa.stig_rule_SV-271635r1137691_rule — OL 9 must require a boot loader superuser password.
  - rhel9: xccdf_mil.disa.stig_rule_SV-257787r1184288_rule — RHEL 9 must require a boot loader superuser password.
- **2 instances across 2 benchmarks** — oracle-linux9, rhel9
  - oracle-linux9: xccdf_mil.disa.stig_rule_SV-271820r1092172_rule — OL 9 /var/log directory must have mode 0755 or less permissive.
  - rhel9: xccdf_mil.disa.stig_rule_SV-257885r1044953_rule — RHEL 9 /var/log directory must have mode 0755 or less permissive.
- **2 instances across 2 benchmarks** — oracle-linux9, rhel9
  - oracle-linux9: xccdf_mil.disa.stig_rule_SV-271867r1092313_rule — OL 9 must log IPv4 packets with impossible addresses by default.
  - rhel9: xccdf_mil.disa.stig_rule_SV-257961r1155730_rule — RHEL 9 must log IPv4 packets with impossible addresses by default.
- **2 instances across 2 benchmarks** — oracle-linux9, rhel9
  - oracle-linux9: xccdf_mil.disa.stig_rule_SV-271483r1091161_rule — OL 9 networked systems must have and implement SSH to protect the confidentiality and integrity of transmitted and received information, as well as information during preparation for transmission.
  - rhel9: xccdf_mil.disa.stig_rule_SV-257979r958908_rule — All RHEL 9 networked systems must have and implement SSH to protect the confidentiality and integrity of transmitted and received information, as well as information during preparation for transmission.
- **2 instances across 2 benchmarks** — windows-server-2025, windows11
  - windows-server-2025: xccdf_mil.disa.stig_rule_SV-278200r1181306_rule — The Windows Server 2025 setting Domain member: Digitally encrypt or sign secure channel data (always) must be configured to Enabled.
  - windows11: xccdf_mil.disa.stig_rule_SV-253438r958908_rule — Outgoing secure channel traffic must be encrypted or signed.
- **2 instances across 2 benchmarks** — oracle-linux9, rhel9
  - oracle-linux9: xccdf_mil.disa.stig_rule_SV-271594r1208724_rule — OL 9 must be configured so that successful/unsuccessful uses of the umount system call generate an audit record.
  - rhel9: xccdf_mil.disa.stig_rule_SV-258215r1155611_rule — Successful/unsuccessful uses of the umount system call in RHEL 9 must generate an audit record.
- **2 instances across 2 benchmarks** — oracle-linux9, rhel9
  - oracle-linux9: xccdf_mil.disa.stig_rule_SV-271566r1092552_rule — OL 9 must audit all uses of the kmod command.
  - rhel9: xccdf_mil.disa.stig_rule_SV-258195r1045370_rule — RHEL 9 must audit all uses of the kmod command.
- **2 instances across 2 benchmarks** — oracle-linux9, rhel9
  - oracle-linux9: xccdf_mil.disa.stig_rule_SV-271506r1091230_rule — OL 9 must have the fapolicy module installed.
  - rhel9: xccdf_mil.disa.stig_rule_SV-258089r1045179_rule — RHEL 9 fapolicy module must be installed.
- **2 instances across 2 benchmarks** — windows-server-2025, windows11
  - windows-server-2025: xccdf_mil.disa.stig_rule_SV-278032r1180802_rule — Windows Server 2025 must have Secure Boot enabled.
  - windows11: xccdf_mil.disa.stig_rule_SV-253257r1210281_rule — Secure Boot must be enabled on Windows 11 systems.
- **2 instances across 2 benchmarks** — oracle-linux9, rhel9
  - oracle-linux9: xccdf_mil.disa.stig_rule_SV-271782r1184213_rule — OL 9 local initialization files must have mode 0740 or less permissive.
  - rhel9: xccdf_mil.disa.stig_rule_SV-257889r1184302_rule — All RHEL 9 local initialization files must have mode 0740 or less permissive.

See assessment-reuse.json for all exact groups, parameterization candidates, rule mappings, and the organization-specific cost formulas.

See reuse-views/ for the same measured exact reuse rendered as combined shared-rule overlays, split assessment bindings, and Ansible-inspired shared assessments.
