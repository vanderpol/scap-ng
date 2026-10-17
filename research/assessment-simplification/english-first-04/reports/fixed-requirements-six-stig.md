# Fixed requirement vocabulary — six-STIG sensitivity audit

**Research only — no proposed syntax is approved.**

The source is the same pinned six-STIG 0.4 r3 archive used by the English-first corpus audit.
This is **requirement-choice enum coverage**, not whole language coverage or scanner validation.

| Candidate dropdown size | Complete explicit modes / Tests | Complete explicit modes / Assessments |
| --- | ---: | ---: |
| basic | 1093/1375 (79.49%) | 685/872 (78.56%) |
| practical | 1319/1375 (95.93%) | 833/872 (95.53%) |
| practical_plus_two | 1358/1375 (98.76%) | 859/872 (98.51%) |
| practical_plus_three | 1368/1375 (99.49%) | 866/872 (99.31%) |
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

## Residual examples after adding two scoped choices

- `authoring/apache_server_2-4_unix_server/assessments/automated/SV-214241.automated.yaml` — `verify-that-proxyrequests-directive-exists-not-configured-on-in-all-test`: Item `at_least_one_exists_and_all_match`, field modes `may_be_absent_and_none_match`; anomaly=False
- `authoring/apache_server_2-4_unix_server/assessments/automated/SV-214241.automated.yaml` — `if-proxyrequests-directive-exists-in-other-loaded-configuration-files-verify-test`: Item `at_least_one_exists_and_all_match`, field modes `may_be_absent_and_none_match`; anomaly=False
- `authoring/apache_server_2-4_unix_server/assessments/automated/SV-214243.automated.yaml` — `verify-that-addhandler-directive-exists-configured-stig-httpd-conf-apache2-test`: Item `at_least_one_exists_and_all_match`, field modes `may_be_absent_and_none_match`; anomaly=False
- `authoring/apache_server_2-4_unix_server/assessments/automated/SV-214243.automated.yaml` — `if-addhandler-directive-exists-in-any-loaded-configuration-verify-that-test`: Item `at_least_one_exists_and_all_match`, field modes `may_be_absent_and_none_match`; anomaly=False
- `authoring/apache_server_2-4_unix_server/assessments/automated/SV-214246.automated.yaml` — `verify-listen-directive-not-configured-listen-on-0-0-0-test`: Item `at_least_one_exists_and_all_match`, field modes `may_be_absent_and_none_match`; anomaly=False
- `authoring/apache_server_2-4_unix_server/assessments/automated/SV-214251.automated.yaml` — `verify-that-sessioncookiename-directive-exists-configured-httponly-secure-not-domain-test`: Item `at_least_one_exists_and_all_match`, field modes `may_be_absent_and_none_match`; anomaly=False
- `authoring/apache_server_2-4_unix_server/assessments/automated/SV-214251.automated.yaml` — `if-sessioncookiename-exists-in-other-loaded-configurations-files-verify-it-test`: Item `at_least_one_exists_and_all_match`, field modes `may_be_absent_and_none_match`; anomaly=False
- `authoring/ms_windows_11/assessments/automated/SV-253266.automated.yaml` — `review-installed-os-via-powershell-test`: Item `only_one_exists_and_only_one_matches`, field modes ``; anomaly=False
- `authoring/ms_windows_11/assessments/automated/SV-253289.automated.yaml` — `secondary-logon-service-startup-type-disabled-or-service-uninstalled-test`: Item `may_be_absent_and_some_match`, field modes ``; anomaly=False
- `authoring/ms_windows_11/assessments/automated/SV-253296.automated.yaml` — `review-windows-time-service-configuration-via-powershell-test`: Item `only_one_exists_and_only_one_matches`, field modes ``; anomaly=False
- `authoring/ms_windows_server_2025/assessments/automated/SV-278090.automated.yaml` — `windows-server-virtualization-based-security-enabled-platform-security-level-configured-test`: Item `at_least_one_exists_and_only_one_matches`, field modes `at_least_one_exists_and_only_one_matches`; anomaly=False
- `authoring/ms_windows_server_2025/assessments/automated/SV-278090.automated.yaml` — `windows-server-virtualization-based-security-enabled-platform-security-level-configured-2-test`: Item `at_least_one_exists_and_only_one_matches`, field modes `at_least_one_exists_and_only_one_matches`; anomaly=False
- `authoring/rhel_9/assessments/automated/SV-258146.automated.yaml` — `streamdriverauthmode-not-set-in-module-block-advanced-syntax-test`: Item `may_be_absent_and_none_match`, field modes ``; anomaly=False
- `authoring/rhel_9/assessments/automated/SV-258147.automated.yaml` — `streamdrivermode-not-set-in-module-block-advanced-syntax-test`: Item `may_be_absent_and_none_match`, field modes ``; anomaly=False
- `authoring/rhel_9/assessments/automated/SV-258148.automated.yaml` — `streamdriver-not-set-in-module-block-advanced-syntax-test`: Item `may_be_absent_and_none_match`, field modes ``; anomaly=False
- `authoring/shared/assessments/linux/files/gpg-signature-enabled-software-repo.assessment.yaml` — `no-etc-yum-repos-d-repo-reponame-has-gpgcheck-set-test`: Item `all_exist_and_none_match`, field modes ``; anomaly=False
- `authoring/shared/assessments/linux/files/verify-boot-loader-root-admin-adminstrator.assessment.yaml` — `verify-boot-loader-password-not-set-root-admin-or-adminstrator-test`: Item `none_exist`, field modes ``; anomaly=True

## Six-STIG source-folder coverage after third choice

The six STIGs share additional Assessments; the shared folder is not a seventh benchmark.

| Source folder | Tests covered | Assessments covered |
| --- | ---: | ---: |
| apache_server_2-4_unix_server | 57/57 (100.0%) | 23/23 (100.0%) |
| ms_windows_11 | 151/154 (98.1%) | 90/93 (96.8%) |
| ms_windows_server_2025 | 173/175 (98.9%) | 109/110 (99.1%) |
| ms_windows_server_dns | 53/53 (100.0%) | 21/21 (100.0%) |
| oracle_linux_9 | 57/57 (100.0%) | 41/41 (100.0%) |
| rhel_9 | 99/99 (100.0%) | 57/57 (100.0%) |
| shared | 778/780 (99.7%) | 525/527 (99.6%) |

## Remaining individual Tests after three choices

These are not reasons to rewrite a STIG merely to inflate a percentage.

- `authoring/ms_windows_11/assessments/automated/SV-253266.automated.yaml` — `review-installed-os-via-powershell-test`: `only_one_exists_and_only_one_matches`. Requires exactly one existing Item and exactly one matching Item; preserve unless collector cardinality is proven.
- `authoring/ms_windows_11/assessments/automated/SV-253289.automated.yaml` — `secondary-logon-service-startup-type-disabled-or-service-uninstalled-test`: `may_be_absent_and_some_match`. Optional population with some-match semantics; not equivalent to optional all-match if multiple Items exist.
- `authoring/ms_windows_11/assessments/automated/SV-253296.automated.yaml` — `review-windows-time-service-configuration-via-powershell-test`: `only_one_exists_and_only_one_matches`. Requires exactly one existing Item and exactly one matching Item; preserve unless collector cardinality is proven.
- `authoring/ms_windows_server_2025/assessments/automated/SV-278090.automated.yaml` — `windows-server-virtualization-based-security-enabled-platform-security-level-configured-test`: `at_least_one_exists_and_only_one_matches`. Requires at least one Item and exactly one matching Item; this source also needs distinct nested field cardinality.
- `authoring/ms_windows_server_2025/assessments/automated/SV-278090.automated.yaml` — `windows-server-virtualization-based-security-enabled-platform-security-level-configured-2-test`: `at_least_one_exists_and_only_one_matches`. Requires at least one Item and exactly one matching Item; this source also needs distinct nested field cardinality.
- `authoring/shared/assessments/linux/files/gpg-signature-enabled-software-repo.assessment.yaml` — `no-etc-yum-repos-d-repo-reponame-has-gpgcheck-set-test`: `all_exist_and_none_match`. Requires all-exist semantics plus zero matching Items; not a no-Items Test.
- `authoring/shared/assessments/linux/files/verify-boot-loader-root-admin-adminstrator.assessment.yaml` — `verify-boot-loader-password-not-set-root-admin-or-adminstrator-test`: `none_exist`. Contradictory source: none_exist Test with attached State; trace OVAL XML and converter before altering.

## Recommendation

The 98% overall mode-coverage target can be met with just two extra scoped choices,
but Windows 11 remains below 98% of its own source-folder Assessments after the third addition.
Keep rare valid semantics available through the SAME item/condition grammar, not a second source dialect.
Do not equate full enum coverage with proof of a shallow condition syntax for records,
Set filters, Variables, State alternatives, or six-state collection/evidence behavior.
Assess the five semantic residual classes above before standardizing labels.


## Limits and decision rule

- Folder 'shared' is reused across benchmarks; source-folder coverage is not Rule coverage.
- This experiment inventories canonical enum modes; it does not validate the proposed items/condition YAML parser or actual readability.
- Explicit field requirement entries are counted; implicit scoped field inheritance and record/evaluate semantics need independent full-AST validation.
- Collector, Object, Set, variable, evidence, error and six-state runtime behavior are NOT established by enum coverage.
- Do not rewrite valid STIG source to raise a percentage. Isolate defects and differential-prove any changed semantics.

**98% is a review trigger, not permission to change valid results.**
Each residual needs a source-backed classification: bad source/converter, safe authoring abstraction, necessary vocabulary extension, or valid exception requiring explicit syntax.
