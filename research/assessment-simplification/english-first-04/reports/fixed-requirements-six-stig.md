# Fixed requirement vocabulary — six-STIG sensitivity audit

**Research only — no proposed syntax is approved.**

The source is the same pinned six-STIG 0.4 r3 archive used by the English-first corpus audit.
This is **requirement-choice enum coverage**, not whole language coverage or scanner validation.

| Candidate dropdown size | Complete explicit modes / Tests | Complete explicit modes / Assessments |
| --- | ---: | ---: |
| basic | 1093/1375 (79.49%) | 685/872 (78.56%) |
| practical | 1319/1375 (95.93%) | 833/872 (95.53%) |
| exhaustive_vocabulary | 1374/1375 (99.93%) | 871/872 (99.89%) |

## Coverage by source folder

Folder 'shared' is not a seventh STIG. Its Assessments may be used in several streams.

| Source folder | Practical Test modes | Practical Assessments |
| --- | ---: | ---: |
| apache_server_2-4_unix_server | 47/57 | 18/23 |
| ms_windows_11 | 142/154 | 84/93 |
| ms_windows_server_2025 | 156/175 | 93/110 |
| ms_windows_server_dns | 53/53 | 21/21 |
| oracle_linux_9 | 57/57 | 41/41 |
| rhel_9 | 96/99 | 54/57 |
| shared | 768/780 | 522/527 |

## Frequent Item requirements

| Source requirement | Tests |
| --- | ---: |
| `at_least_one_exists_and_all_match` | 749 |
| `at_least_one_exists` | 156 |
| `all_exist` | 127 |
| `none_exist` | 103 |
| `all_exist_and_all_match` | 73 |
| `at_least_one_exists_and_some_match` | 67 |
| `may_be_absent_and_all_match` | 67 |
| `at_least_one_exists_and_only_one_matches` | 21 |
| `may_be_absent_and_none_match` | 3 |
| `only_one_exists_and_matches` | 3 |
| `only_one_exists_and_only_one_matches` | 2 |
| `only_one_exists` | 2 |
| `may_be_absent_and_some_match` | 1 |
| `all_exist_and_none_match` | 1 |

## Frequent explicit field/record requirements

| Source requirement | Occurrences |
| --- | ---: |
| `at_least_one_exists_and_all_match` | 747 |
| `at_least_one_exists_and_some_match` | 51 |
| `none_exist` | 42 |
| `may_be_absent_and_all_match` | 22 |
| `at_least_one_exists_and_none_match` | 22 |
| `only_one_exists_and_matches` | 22 |
| `may_be_absent_and_none_match` | 7 |
| `at_least_one_exists_and_only_one_matches` | 2 |

## Practical-vocabulary residual examples

- `authoring/apache_server_2-4_unix_server/assessments/automated/SV-214241.automated.yaml` — `verify-that-proxyrequests-directive-exists-not-configured-on-in-all-test`: Item `at_least_one_exists_and_all_match`, field modes `may_be_absent_and_none_match`; anomaly=False
- `authoring/apache_server_2-4_unix_server/assessments/automated/SV-214241.automated.yaml` — `if-proxyrequests-directive-exists-in-other-loaded-configuration-files-verify-test`: Item `at_least_one_exists_and_all_match`, field modes `may_be_absent_and_none_match`; anomaly=False
- `authoring/apache_server_2-4_unix_server/assessments/automated/SV-214243.automated.yaml` — `verify-that-addhandler-directive-exists-configured-stig-httpd-conf-apache2-test`: Item `at_least_one_exists_and_all_match`, field modes `may_be_absent_and_none_match`; anomaly=False
- `authoring/apache_server_2-4_unix_server/assessments/automated/SV-214243.automated.yaml` — `if-addhandler-directive-exists-in-any-loaded-configuration-verify-that-test`: Item `at_least_one_exists_and_all_match`, field modes `may_be_absent_and_none_match`; anomaly=False
- `authoring/apache_server_2-4_unix_server/assessments/automated/SV-214245.automated.yaml` — `apache-dav-module-not-enabled-test`: Item `at_least_one_exists_and_all_match`, field modes `at_least_one_exists_and_none_match`; anomaly=False
- `authoring/apache_server_2-4_unix_server/assessments/automated/SV-214245.automated.yaml` — `apache-dav-fs-module-not-enabled-test`: Item `at_least_one_exists_and_all_match`, field modes `at_least_one_exists_and_none_match`; anomaly=False
- `authoring/apache_server_2-4_unix_server/assessments/automated/SV-214245.automated.yaml` — `apache-dav-fs-module-not-enabled-2-test`: Item `at_least_one_exists_and_all_match`, field modes `at_least_one_exists_and_none_match`; anomaly=False
- `authoring/apache_server_2-4_unix_server/assessments/automated/SV-214246.automated.yaml` — `verify-listen-directive-not-configured-listen-on-0-0-0-test`: Item `at_least_one_exists_and_all_match`, field modes `may_be_absent_and_none_match`; anomaly=False
- `authoring/apache_server_2-4_unix_server/assessments/automated/SV-214251.automated.yaml` — `verify-that-sessioncookiename-directive-exists-configured-httponly-secure-not-domain-test`: Item `at_least_one_exists_and_all_match`, field modes `may_be_absent_and_none_match`; anomaly=False
- `authoring/apache_server_2-4_unix_server/assessments/automated/SV-214251.automated.yaml` — `if-sessioncookiename-exists-in-other-loaded-configurations-files-verify-it-test`: Item `at_least_one_exists_and_all_match`, field modes `may_be_absent_and_none_match`; anomaly=False
- `authoring/ms_windows_11/assessments/automated/SV-253266.automated.yaml` — `review-installed-os-via-powershell-test`: Item `only_one_exists_and_only_one_matches`, field modes ``; anomaly=False
- `authoring/ms_windows_11/assessments/automated/SV-253274.automated.yaml` — `network-access-let-everyone-permissions-apply-anonymous-users-set-disabled-test`: Item `at_least_one_exists_and_only_one_matches`, field modes ``; anomaly=False
- `authoring/ms_windows_11/assessments/automated/SV-253289.automated.yaml` — `secondary-logon-service-startup-type-disabled-or-service-uninstalled-test`: Item `may_be_absent_and_some_match`, field modes ``; anomaly=False
- `authoring/ms_windows_11/assessments/automated/SV-253291.automated.yaml` — `bluetooth-radio-turned-off-test`: Item `at_least_one_exists_and_only_one_matches`, field modes ``; anomaly=False
- `authoring/ms_windows_11/assessments/automated/SV-253296.automated.yaml` — `review-windows-time-service-configuration-via-powershell-test`: Item `only_one_exists_and_only_one_matches`, field modes ``; anomaly=False
- `authoring/ms_windows_11/assessments/automated/SV-253350.automated.yaml` — `camera-access-from-lock-screen-disabled-test`: Item `at_least_one_exists_and_only_one_matches`, field modes ``; anomaly=False
- `authoring/ms_windows_11/assessments/automated/SV-253363.automated.yaml` — `prioritize-ecc-curves-longer-key-lengths-first-nistp384-requirement-test`: Item `at_least_one_exists_and_only_one_matches`, field modes ``; anomaly=False
- `authoring/ms_windows_11/assessments/automated/SV-253370.automated.yaml` — `credential-guard-running-on-windows-11-domain-joined-systems-test`: Item `at_least_one_exists_and_only_one_matches`, field modes ``; anomaly=False
- `authoring/ms_windows_11/assessments/automated/SV-253446.automated.yaml` — `windows-dialog-box-title-legal-banner-configured-title-option-1-test`: Item `at_least_one_exists_and_only_one_matches`, field modes ``; anomaly=False
- `authoring/ms_windows_11/assessments/automated/SV-253446.automated.yaml` — `windows-dialog-box-title-legal-banner-configured-title-option-2-test`: Item `at_least_one_exists_and_only_one_matches`, field modes ``; anomaly=False
- `authoring/ms_windows_11/assessments/automated/SV-253446.automated.yaml` — `windows-dialog-box-title-legal-banner-configured-title-option-3-test`: Item `at_least_one_exists_and_only_one_matches`, field modes ``; anomaly=False
- `authoring/ms_windows_11/assessments/automated/SV-253446.automated.yaml` — `windows-dialog-box-title-legal-banner-configured-title-option-4-test`: Item `at_least_one_exists_and_only_one_matches`, field modes ``; anomaly=False

## Limits and decision rule

- Folder 'shared' is reused across benchmarks; source-folder coverage is not Rule coverage.
- This experiment inventories canonical enum modes; it does not validate the proposed items/condition YAML parser or actual readability.
- Explicit field requirement entries are counted; implicit scoped field inheritance and record/evaluate semantics need independent full-AST validation.
- Collector, Object, Set, variable, evidence, error and six-state runtime behavior are NOT established by enum coverage.
- Do not rewrite valid STIG source to raise a percentage. Isolate defects and differential-prove any changed semantics.

**98% is a review trigger, not permission to change valid results.**
Each residual needs a source-backed classification: bad source/converter, safe authoring abstraction, necessary vocabulary extension, or valid exception requiring explicit syntax.
