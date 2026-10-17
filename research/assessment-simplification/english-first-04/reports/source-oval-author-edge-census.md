# Original-source OVAL rare-feature ownership vs six-STIG native authoring

**Research only.** Input pinned NIWC `scap-content-library` revision
`8c8e5dff860af6b1290ee9273a282db24278f8d5` and exact native six-STIG r3 SHA-256 `03d64157ee295b81defe6f96cf7a3123410010ef4422d76bf5b7bb3ddbf30c9d`.

Direct original OVAL source: **2140** Test identities in six original STIG archives.
Curated native authoring: **1375** Tests in **872** automated Assessments.
They are different populations: source archives contain OVAL content not necessarily selected into native authoring.

## Original OVAL Test origin and existence usage

| Original ID namespace | at_least_one_exists | all_exist | any_exist | none_exist | only_one_exists |
| --- | ---: | ---: | ---: | ---: | ---: |
| DISA | 1237 | 356 | 116 | 101 | 8 |
| NIWC/NAVWAR | 268 | 5 | 5 | 40 | 4 |

## Selected native authoring modes (different denominator)

| Existence mode | Native Test occurrences |
| --- | ---: |
| `all_exist` | 201 |
| `any_exist` | 71 |
| `at_least_one_exists` | 993 |
| `none_exist` | 103 |
| `only_one_exists` | 7 |

## Native Test source-ID linkage check

Original OVAL Test comments and original existence modes can provide
candidate matches, **not verified source identities**.
| Candidate quality | Native Test count |
| --- | ---: |
| `mixed_author_candidates` | 14 |
| `multiple_same_author_candidates` | 112 |
| `single_original_test_id_candidate` | 1249 |

## Original rare Test examples by original author


### DISA:all_exist

- \`oval:mil.disa.stig.ind:tst:230345\`: check /etc/security/faillock.conf for the even_deny_root setting; State refs=0, check=all
- \`oval:mil.disa.stig.ind:tst:23026400\`: Every /etc/yum.repos.d/*.repo:[{reponame}] has a gpgcheck set to 1.; State refs=1, check=all
- \`oval:mil.disa.stig.ind:tst:23026401\`: No /etc/yum.repos.d/*.repo:[{reponame}] has a gpgcheck set to 0.; State refs=1, check=none satisfy
- \`oval:mil.disa.stig.ind:tst:23029201\`: There is a separate file system configured for /var.; State refs=0, check=all
- \`oval:mil.disa.stig.ind:tst:23029401\`: There is a separate file system configured for audit data directory.; State refs=0, check=all

### DISA:any_exist

- \`oval:mil.disa.stig.ind:tst:23030001\`: If /boot is configured in /etc/fstab, it is configured with the nosuid option; State refs=1, check=all
- \`oval:mil.disa.stig.ind:tst:23030101\`: Device files are configured in /etc/fstab to use the nodev option.  Mounts on '/' are ignored.; State refs=1, check=all
- \`oval:mil.disa.stig.ind:tst:23030600\`: all nfs entries in /etc/fstab have noexec; State refs=1, check=all
- \`oval:mil.disa.stig.ind:tst:23031301\`: If core is set for any specific domains, it is set to 0.; State refs=1, check=all
- \`oval:mil.disa.stig.ind:tst:23034601\`: limits.conf and limits.d/*.conf:maxlogins is set to 10 or less for non-default domains; State refs=1, check=all

### DISA:only_one_exists

- \`oval:mil.disa.stig.ind:tst:23023700\`: /etc/pam.d/password-auth:password includes pam_unix.so sha512; State refs=0, check=all
- \`oval:mil.disa.stig.ind:tst:23024000\`: selinux is enforcing; State refs=1, check=all
- \`oval:mil.disa.stig.ind:tst:23024001\`: /etc/selinux/config:SELINUX=enforcing; State refs=1, check=all
- \`oval:mil.disa.stig.ind:tst:27401400\`: Defaults timestamp_timeout is configured to 0 in /etc/sudoers or /etc/sudoers.d.; State refs=1, check=all
- \`oval:mil.disa.stig.ind:tst:23023700\`: /etc/pam.d/password-auth:password includes pam_unix.so sha512; State refs=0, check=all

### NIWC/NAVWAR:all_exist

- \`oval:navy.navwar.niwcatlantic.scc.almalinux9:tst:301\`: The os-release file has CPE_NAME of almalinux:almalinux:9; State refs=1, check=all
- \`oval:navy.navwar.niwcatlantic.scc.rocky9:tst:201\`: The os-release file has CPE_NAME of rocky:rocky:9; State refs=1, check=all
- \`oval:navy.navwar.niwcatlantic.scc.linux:tst:102\`: The gnome-session package is installed. (DEB); State refs=0, check=all
- \`oval:navy.navwar.niwcatlantic.scc.linux:tst:102\`: The gnome-session package is installed. (DEB); State refs=0, check=all
- \`oval:navy.navwar.niwcatlantic.scc.windows:tst:25329301\`: The system must notify the user when a Bluetooth device attempts to connect.; State refs=1, check=all

### NIWC/NAVWAR:any_exist

- \`oval:navy.navwar.niwcatlantic.scc.rhel9os:tst:25824103\`: Verify no SHA1 algorithms are employed.; State refs=1, check=all
- \`oval:navy.navwar.niwcatlantic.scc.rhel9os:tst:25824104\`: Verify minimum hash values of 224.; State refs=1, check=all
- \`oval:navy.navwar.niwcatlantic.scc.rhel8:tst:27184401\`: Confirm interactive user's home directories exist.; State refs=1, check=all
- \`oval:navy.navwar.niwcatlantic.scc.windows:tst:25347601\`: Password Age Check: Verify all enabled local Administrator accounts passwords are less than 60 days old; State refs=1, check=all
- \`oval:navy.navwar.niwcatlantic.scc.windows:tst:27800403\`: Windows Domain Controller - Accounts must require passwords.; State refs=1, check=all

### NIWC/NAVWAR:only_one_exists

- \`oval:navy.navwar.niwcatlantic.scc.linux:tst:25777901\`: The system must display the Standard Mandatory DoD Notice and Consent Banner before granting local or remote access to the system via a command line user logon.; State refs=0, check=all
- \`oval:navy.navwar.niwcatlantic.scc.linux:tst:27145501\`: The system must display the Standard Mandatory DoD Notice and Consent Banner before granting local or remote access to the system via a command line user logon.; State refs=0, check=all
- \`oval:navy.navwar.niwcatlantic.scc.windows:tst:25326601\`: Review Installed OS via PowerShell; State refs=1, check=only one
- \`oval:navy.navwar.niwcatlantic.scc.windows:tst:25329601\`: Review the Windows time service configuration via PowerShell; State refs=1, check=only one

## Candidate origin of the 201 selected native all_exist Tests

The test title + existence mode yields exactly one original source Test ID
for the cases below, but **that is not an explicit converter lineage ID**.

| Candidate original author | Native Tests |
| --- | ---: |
| DISA | 198 |
| NIWC/NAVWAR | 3 |

## Seven native Test-level only_one_exists cases

Exactly one **existing Item** is distinct from exactly one **matching Item**.
Unverified joins use source Test comment and existence mode, not a converter ID.

| Native Assessment | Has State | Original Test ID candidate | Original check |
| --- | --- | --- | --- |
| \`authoring/ms_windows_11/assessments/automated/SV-253266.automated.yaml\` | True | \`oval:navy.navwar.niwcatlantic.scc.windows:tst:25326601\` | \`only one\` |
| \`authoring/ms_windows_11/assessments/automated/SV-253296.automated.yaml\` | True | \`oval:navy.navwar.niwcatlantic.scc.windows:tst:25329601\` | \`only one\` |
| \`authoring/shared/assessments/linux/files/defaults-timestamp-timeout-sudoers-etc-sudo.assessment.yaml\` | True | \`oval:mil.disa.stig.ind:tst:27401400\` | \`all\` |
| \`authoring/shared/assessments/linux/files/etc-pam-d-unix-so-sha512.assessment.yaml\` | False | \`oval:mil.disa.stig.ind:tst:23023700\` | \`all\` |
| \`authoring/shared/assessments/linux/files/system-display-standard-notice-consent-ba.assessment.yaml\` | False | \`oval:navy.navwar.niwcatlantic.scc.linux:tst:25777901, oval:navy.navwar.niwcatlantic.scc.linux:tst:27145501\` | \`all\` |
| \`authoring/shared/assessments/linux/other/use-linux-limits-on-s.assessment.yaml\` | True | \`oval:mil.disa.stig.ind:tst:23024000\` | \`all\` |
| \`authoring/shared/assessments/linux/other/use-linux-limits-on-s.assessment.yaml\` | True | \`oval:mil.disa.stig.ind:tst:23024001\` | \`all\` |

These seven should be reviewed for *actual resource duplication intent*;
replacing exact-one with at-least-one is not a lossless simplification.


## Source attribution for 201 native all_exist cases

The JSON contains each native Test with **source-ID candidates**, not proven
lineage. Cases where several original IDs share a comment, or none match,
require XCCDF Rule/Definition/source Test ID mapping. Do not infer author
statistics for those from filenames or NIWC packaging.

## Limitations and decision policy

- Counts of all original OVAL Tests include Tests not selected in the 0.4 native six-STIG authoring; never divide one source count by the other denominator.
- Source namespace establishes *identity prefix*, not a verified DISA 1.3 release byte-for-byte comparison.
- A native descriptive Test name can match several different source IDs; title-and-mode joins are candidates only; do not call them provenance-confirmed.
- Original XCCDF Rule→OVAL Definition→Test ID closure is required for a provable native assessment linkage; mixed-source dependencies must be reported independently.
- No OVAL feature is dropped in this report and no schema, runtime, importer or source benchmark was modified.

Any rare OVAL feature needs a separate human-value/semantic review:
retaining the capability to convert a source construct does not require
giving native content writers a corresponding new keyword. Mark unused
source features as candidates, not automatically obsolete.
