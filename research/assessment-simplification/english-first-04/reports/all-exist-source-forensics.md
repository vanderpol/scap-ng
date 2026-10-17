# Do authors really need Test all_exist?

**SCAP-NG 0.4 source-forensics only. Not an adopted syntax or a statement of original author intent.**

Pinned six-STIG source: 201 of 1375 named Tests in 872 unique automated Assessments.
127 State-free; 74 State-bearing.

## Capability distribution

| Capability | Tests |
| --- | ---: |
| `independent.textfilecontent54` | 132 |
| `unix.sysctl` | 26 |
| `windows.wmi.query` | 10 |
| `linux.rpminfo` | 7 |
| `windows.registry` | 6 |
| `unix.file` | 6 |
| `linux.partition` | 6 |
| `windows.ntuser` | 3 |
| `unix.password` | 2 |
| `unix.shadow` | 1 |
| `unix.symlink` | 1 |
| `variable.value` | 1 |

## Selected Object shape

| Shape | Test count |
| --- | ---: |
| `select+collect` | 140 |
| `select` | 44 |
| `collect` | 10 |
| `set` | 4 |
| `select+for_each` | 2 |
| `objectless_or_unresolved` | 1 |

## What population can the collector plausibly select?

These are **heuristics**, not semantic conclusions.

| Category | Tests |
| --- | ---: |
| `open_ended_match` | 134 |
| `fixed_literal_selection` | 46 |
| `collector_defined_population` | 10 |
| `dynamic_or_composed` | 8 |
| `explicit_multi_value_selection` | 2 |
| `not_determined` | 1 |

## Direct evidence of differing authoring choices

- `all_exist` Tests whose selected Object is also used by at-least-one Test(s): **8**
- `all_exist` Tests also found with the same Object and comparison body but different existence mode: **0**

These comparisons detect inconsistent or intentional vocabulary choices; neither proves that a source author copied a Test in error.

## Representative cases (full ledger in JSON)


### collector_defined_population

- `authoring/ms_windows_11/assessments/automated/SV-253259.automated.yaml` — `bitlocker-enabled-on-all-fixed-drives-test`: BitLocker must be enabled on all fixed drives.
- `authoring/ms_windows_11/assessments/automated/SV-253275.automated.yaml` — `internet-information-services-feature-not-installed-test`: 'Internet Information Services' feature is not installed
- `authoring/ms_windows_11/assessments/automated/SV-253275.automated.yaml` — `internet-information-services-hostable-web-core-feature-not-installed-test`: 'Internet Information Services Hostable Web Core' feature is not installed
- `authoring/ms_windows_11/assessments/automated/SV-253285.automated.yaml` — `windows-powershell-2-0-optional-feature-disabled-test`: Windows PowerShell 2.0 optional feature is disabled
- `authoring/ms_windows_11/assessments/automated/SV-253285.automated.yaml` — `windows-powershell-2-0-engine-optional-feature-disabled-test`: Windows PowerShell 2.0 Engine optional feature is disabled

### dynamic_or_composed

- `authoring/ms_windows_11/assessments/automated/SV-253425.automated.yaml` — `do-not-suggest-third-party-content-in-windows-spotlight-set-test`: 'Do not suggest third-party content in Windows spotlight' is set to 'Enabled'
- `authoring/ms_windows_11/assessments/automated/SV-253477.automated.yaml` — `turn-off-toast-notifications-on-lock-screen-set-enabled-test`: 'Turn off toast notifications on the lock screen' is set to 'Enabled'
- `authoring/shared/assessments/linux/accounts/interactive-users-dir-assigned-in.assessment.yaml` — `check-users-without-home-directory-not-defined-test`: check for users without a home directory not defined
- `authoring/shared/assessments/linux/accounts/interactive-users-dir-assigned-in.assessment.yaml` — `check-if-root-s-home-directory-not-defined-test`: check if root's home directory is not defined
- `authoring/shared/assessments/linux/files/audit-log-dirs-owned-by-root.assessment.yaml` — `audit-log-directories-owned-by-root-test`: audit log directories are owned by root

### explicit_multi_value_selection

- `authoring/shared/assessments/linux/files/audit-tools-mode-0755-less-permissive.assessment.yaml` — `audit-tools-have-mode-0755-or-less-permissive-test`: audit tools have a mode of 0755 or less permissive.
- `authoring/shared/assessments/linux/files/audit-tools-owned-by-root.assessment.yaml` — `audit-tools-owned-by-root-test`: audit tools are owned by root

### fixed_literal_selection

- `authoring/ms_windows_11/assessments/automated/SV-253284.automated.yaml` — `sehop-turned-on-properly-configured-test`: SEHOP is turned on and properly configured
- `authoring/ms_windows_11/assessments/automated/SV-253293.automated.yaml` — `system-notify-user-when-bluetooth-device-attempts-connect-test`: The system must notify the user when a Bluetooth device attempts to connect.
- `authoring/ms_windows_11/assessments/automated/SV-253423.automated.yaml` — `turn-on-convenience-pin-sign-in-disabled-test`: 'Turn on convenience PIN sign-in' is 'Disabled'
- `authoring/ms_windows_server_2025/assessments/automated/SV-278208.automated.yaml` — `legal-notice-caption-dod-notice-consent-banner-test`: Legal Notice Caption - DoD Notice and Consent Banner
- `authoring/ms_windows_server_2025/assessments/automated/SV-278208.automated.yaml` — `legal-notice-caption-us-department-defense-warning-statement-test`: Legal Notice Caption - US Department of Defense Warning Statement

### not_determined

- `authoring/shared/assessments/linux/other/allocate-audit-at-least-one.assessment.yaml` — `audit-file-system-total-space-10gib-test`: Audit file system total space >= 10GiB

### open_ended_match

- `authoring/oracle_linux_9/assessments/automated/SV-271527.automated.yaml` — `audit-modifications-etc-sudoers-test`: Audit modifications to /etc/sudoers
- `authoring/oracle_linux_9/assessments/automated/SV-271528.automated.yaml` — `audit-modifications-etc-sudoers-d-test`: Audit modifications to /etc/sudoers.d/
- `authoring/oracle_linux_9/assessments/automated/SV-271529.automated.yaml` — `audit-modifications-etc-group-test`: Audit modifications to /etc/group
- `authoring/oracle_linux_9/assessments/automated/SV-271530.automated.yaml` — `audit-modifications-etc-gshadow-test`: Audit modifications to /etc/gshadow
- `authoring/oracle_linux_9/assessments/automated/SV-271531.automated.yaml` — `audit-modifications-etc-security-opasswd-test`: Audit modifications to /etc/security/opasswd

## A particularly revealing real-content example: audit tool paths

Two shared Linux Assessments — `audit-tools-mode-0755-less-permissive` and `audit-tools-owned-by-root` — 
select `unix.file` Items using a literal `full_path.equals` list of **seven** names with `value_match: one_or_more`,
while both Tests specify `all_exist`. The seven options are /sbin/auditctl, /sbin/aureport,
/sbin/ausearch, /sbin/autrace, /sbin/auditd, /sbin/rsyslogd and /sbin/augenrules.

**This does not automatically prove that all seven named files exist.** One existing selected file
can satisfy Test Item existence if the other six are not represented as partially missing Items.
A collection that optionally reports missing partial Items could yield a different result.
Therefore do not promote `all_exist` to an English expression such as 'all specified paths must exist'
without specifying whether the author meant discovered Items or an explicitly enumerated expected population.

A genuine requirement that *each enumerated file must exist* needs obligations scoped to each expected identity,
or an independently proven compiler lowering. Rewriting the published rule to that stronger form
would be an intentional compliance-policy change, not a lossless syntax simplification.


## Technical distinction that remains open

1. Under a complete collection of only existing Items, Test `all_exist` and `at_least_one_exists` agree: one or more exist.
2. When a complete collected Object references an existing Item and another Item marked does-not-exist, the common OVAL existence table returns false for `all_exist` but true for `at_least_one_exists`.
3. OVAL 5.12.3 says collectors MAY report optional partially matching, nonexistent Items. Some source selectors may expose those and some may not.
4. Incomplete and error collection flags require separate result propagation; neither mode alone proves all required objects have been inventoried.
5. In an Object using a variable or literal expected names, `all_exist` may express a meaningful fixed-resource obligation. Pattern-matched discovery does not specify a target count by itself.

**Working policy:** retain `all_exist` source-exact while investigating collection status and original source XML. Do not remove it from import support on the strength of a corpus percentage.

## Research limitations

- No author intent, copy/paste, mistake, or source OVAL XML choice inferred from converted YAML.
- Selector categories are structural heuristics, not proof of a fixed or enumerated runtime population.
- A shared folder is reused by multiple STIGs and is not a seventh STIG.
- No live collection or certified OVAL runtime semantics; do not normalize all_exist automatically.
- OVAL 5.12.3 common schema says Test all_exist is equivalent to at_least_one, but generic tables distinguish mixed Item statuses.
- 5.12.3 System Characteristics permit optional partial-match Items with status does not exist.
- The fixed items/condition proposal is not yet a fully proven grammar.
