# 0.4-B textfile content source patterns

**Research census of the six converted 0.3 STIGs; not verified raw SCAP 1.4 semantics.**
The same Assessment may contain many Test nodes. All counts below count
Tests, not distinct Assessments, except where explicitly labeled.

**Referenced automated Assessments using textfile content:** 263
**Textfile Test nodes:** 435

## Observed State shapes

| Shape | Test nodes |
| --- | ---: |
| none | 246 |
| subexpression/pattern_match/one_or_more/all/string | 78 |
| subexpression/equals/one_or_more/all/string | 38 |
| multiple | 26 |
| subexpression/equals/one_or_more/all/other | 13 |
| subexpression/greater_than_or_equal/one_or_more/all/other | 13 |
| text/pattern_match/one_or_more/all/string | 8 |
| subexpression/less_than/one_or_more/all/other | 5 |
| subexpression/less_than_or_equal/one_or_more/all/other | 4 |
| subexpression/not_equal/one_or_more/all/other | 2 |
| subexpression/case_insensitive_equals/one_or_more/all/string | 1 |
| text/pattern_match/one_or_more/all/other | 1 |

## Test Item-existence modes

| Shape | Test nodes |
| --- | ---: |
| one_or_more | 268 |
| all | 129 |
| optional | 17 |
| none | 16 |
| one | 5 |

## Test Item-match modes

| Shape | Test nodes |
| --- | ---: |
| all | 412 |
| one_or_more | 19 |
| none | 4 |

## Literal regex capture group counts

| Shape | Test nodes |
| --- | ---: |
| 1 | 103 |
| 0 | 84 |
| unknown | 82 |
| 7 | 65 |
| 6 | 39 |
| 4 | 26 |
| regex_unrecognized | 19 |
| dynamic | 9 |
| 3 | 4 |
| 5 | 4 |

## Direct one-Test Assessment opportunities

| Shape | Test nodes |
| --- | ---: |
| False | 269 |
| True | 166 |

## Assessment-level Variable dependencies

| Shape | Test nodes |
| --- | ---: |
| False | 388 |
| True | 47 |

## Shared-Object dependencies

| Shape | Test nodes |
| --- | ---: |
| False | 399 |
| True | 36 |

## Embedded foreach dependencies

| Shape | Test nodes |
| --- | ---: |
| False | 433 |
| True | 2 |

## Top correlated patterns

| Combined source shape | Test nodes | Example IDs |
| --- | ---: | --- |
| none \| one_or_more \| all \| 0 \| False | 49 | SV-271679.automated, SV-271679.automated, ng.shared.linux-bluetooth-must-be-disabled, ng.shared.linux-bluetooth-must-be-disabled |
| none \| all \| all \| 7 \| False | 40 | ng.shared.linux-must-audit-all-uses-of-the-chmod-fchmod-and-fchmodat-system-calls, ng.shared.linux-must-audit-all-uses-of-the-chmod-fchmod-and-fchmodat-system-calls, ng.shared.linux-must-audit-all-uses-of-the-chmod-fchmod-and-fchmodat-system-calls, ng.shared.linux-must-audit-all-uses-of-the-chmod-fchmod-and-fchmodat-system-calls |
| none \| all \| all \| 6 \| True | 30 | ng.shared.audit-invocations-of-usr-bin-chacl, ng.shared.audit-invocations-of-usr-bin-chage, ng.shared.audit-invocations-of-usr-bin-chcon, ng.shared.audit-invocations-of-usr-bin-chsh |
| none \| one_or_more \| all \| 7 \| False | 24 | ng.shared.linux-must-audit-all-uses-of-the-truncate-ftruncate-creat-open-openat-an, ng.shared.linux-must-audit-all-uses-of-the-truncate-ftruncate-creat-open-openat-an, ng.shared.linux-must-audit-all-uses-of-the-truncate-ftruncate-creat-open-openat-an, ng.shared.linux-must-audit-all-uses-of-the-truncate-ftruncate-creat-open-openat-an |
| subexpression/pattern_match/one_or_more/all/string \| one_or_more \| all \| 1 \| False | 22 | SV-257794.automated, SV-257794.automated, SV-270180.automated, SV-271734.automated |
| none \| all \| all \| 4 \| False | 16 | SV-258217.automated, SV-258217.automated, SV-258218.automated, SV-258218.automated |
| none \| one_or_more \| all \| unknown \| False | 15 | SV-271627.automated, SV-271627.automated, ng.shared.linux-must-configure-selinux-context-type-to-allow-the-use-of-a-nondefau, ng.shared.linux-must-mount-tmp-with-the-nodev-option |
| multiple \| one_or_more \| all \| 1 \| True | 13 | SV-257777.automated, ng.shared.deny-is-set-to-3-or-less-but-not-0-in-etc-security-faillock-conf, ng.shared.etc-audit-auditd-conf-disk-error-action-syslog-single-or-halt, ng.shared.etc-audit-auditd-conf-disk-full-action-syslog-single-or-halt |
| subexpression/equals/one_or_more/all/string \| one_or_more \| all \| 1 \| True | 13 | SV-258033.automated, SV-271597.automated, ng.shared.automaticloginenable-is-set-to-false-in-etc-gdm-custom-conf, ng.shared.core-dump-backtraces-are-disabled |
| none \| one_or_more \| all \| 0 \| True | 12 | SV-257835.automated, ng.shared.etc-aliases-contains-postmaster-root, ng.shared.etc-audit-audit-rules-e-2-option-is-present-and-is-the-last-line-in-the, ng.shared.etc-audit-audit-rules-f-2-option-is-present |
| subexpression/pattern_match/one_or_more/all/string \| one_or_more \| all \| 1 \| True | 12 | SV-271612.automated, ng.shared.all-local-interactive-user-accounts-are-assigned-a-home-directory-upon-c, ng.shared.etc-audit-auditd-conf-action-mail-acct-root, ng.shared.etc-audit-auditd-conf-admin-space-left-action-single |
| subexpression/pattern_match/one_or_more/all/string \| one_or_more \| all \| unknown \| True | 12 | SV-258091.automated, ng.shared.elevate-the-selinux-context-when-an-administrator-calls-the-sudo-command, ng.shared.etc-ssh-sshd-config-ignorerhosts-yes, ng.shared.etc-ssh-sshd-config-loglevel-verbose |
| none \| none \| all \| 0 \| False | 9 | ng.shared.linux-must-not-allow-blank-or-null-passwords, ng.shared.linux-must-not-allow-blank-or-null-passwords, ng.shared.linux-must-require-users-to-provide-a-password-for-privilege-escalation, ng.shared.linux-must-require-users-to-provide-a-password-for-privilege-escalation |
| none \| all \| all \| 4 \| True | 8 | SV-271527.automated, SV-271528.automated, SV-271529.automated, SV-271530.automated |
| none \| all \| all \| 6 \| False | 8 | ng.shared.linux-must-audit-all-uses-of-the-setxattr-fsetxattr-lsetxattr-removexatt, ng.shared.linux-must-audit-all-uses-of-the-setxattr-fsetxattr-lsetxattr-removexatt, ng.shared.linux-must-audit-all-uses-of-the-setxattr-fsetxattr-lsetxattr-removexatt, ng.shared.linux-must-audit-all-uses-of-the-setxattr-fsetxattr-lsetxattr-removexatt |
| none \| one_or_more \| all \| dynamic \| False | 8 | ng.shared.linux-must-audit-all-uses-of-the-setxattr-fsetxattr-lsetxattr-removexatt, ng.shared.linux-must-audit-all-uses-of-the-setxattr-fsetxattr-lsetxattr-removexatt, ng.shared.linux-must-audit-all-uses-of-the-setxattr-fsetxattr-lsetxattr-removexatt, ng.shared.linux-must-audit-all-uses-of-the-setxattr-fsetxattr-lsetxattr-removexatt |
| subexpression/equals/one_or_more/all/string \| one_or_more \| one_or_more \| 1 \| False | 8 | ng.shared.linux-ip-tunnels-must-use-140-3-approved-cryptographic-algorithms, ng.shared.linux-must-force-a-frequent-session-key-renegotiation-for-ssh-connection, ng.shared.linux-must-use-the-invoking-user-s-password-for-privilege-escalation-whe, ng.shared.linux-ssh-daemon-must-display-the-date-and-time-of-the-last-successful-a |
| subexpression/pattern_match/one_or_more/all/string \| one_or_more \| all \| regex_unrecognized \| False | 8 | ng.shared.linux-ssh-daemon-must-display-the-date-and-time-of-the-last-successful-a, ng.shared.linux-ssh-daemon-must-display-the-date-and-time-of-the-last-successful-a, ng.shared.linux-ssh-daemon-must-not-allow-generic-security-service-application-pro, ng.shared.linux-ssh-daemon-must-not-allow-generic-security-service-application-pro |
| subexpression/pattern_match/one_or_more/all/string \| optional \| all \| 1 \| False | 8 | SV-258241.automated, ng.shared.linux-must-mount-dev-shm-with-the-nodev-option, ng.shared.linux-must-mount-dev-shm-with-the-noexec-option, ng.shared.linux-must-mount-dev-shm-with-the-nosuid-option |
| subexpression/greater_than_or_equal/one_or_more/all/other \| one_or_more \| all \| 1 \| True | 6 | SV-271438.automated, ng.shared.etc-login-defs-fail-delay-4-or-greater, ng.shared.etc-login-defs-pass-min-days-1, ng.shared.the-boot-loader-specification-options-have-audit-backlog-limit-set-to-81 |
| multiple \| one_or_more \| one_or_more \| unknown \| False | 4 | SV-258146.automated, SV-258147.automated, SV-258148.automated, ng.shared.linux-must-be-configured-to-forward-audit-records-via-tcp-to-a-different |
| none \| all \| all \| 3 \| False | 4 | ng.shared.linux-must-audit-uses-of-the-execve-system-call, ng.shared.linux-must-audit-uses-of-the-execve-system-call, ng.shared.linux-must-audit-uses-of-the-execve-system-call, ng.shared.linux-must-audit-uses-of-the-execve-system-call |
| none \| all \| all \| 5 \| False | 4 | SV-258224.automated, SV-258224.automated, SV-258225.automated, SV-258225.automated |
| subexpression/equals/one_or_more/all/string \| one_or_more \| all \| unknown \| True | 4 | SV-271854.automated, SV-271856.automated, ng.shared.etc-ssh-sshd-config-or-etc-ssh-sshd-config-d-usepam-yes, ng.shared.etc-systemd-system-conf-ctrlaltdelburstaction-is-set-to-none |
| subexpression/less_than/one_or_more/all/other \| one_or_more \| all \| unknown \| True | 4 | ng.shared.at-least-one-lowercase-character-is-required, ng.shared.at-least-one-numeric-character-is-required, ng.shared.at-least-one-uppercase-character-is-required, ng.shared.passwords-contain-at-least-one-special-character |
| multiple \| one_or_more \| all \| regex_unrecognized \| True | 3 | SV-285319.automated, ng.shared.openssh-config-ciphers-correct-b36b1d5a, ng.shared.openssh-config-ciphers-correct-c618ef93 |
| multiple \| one_or_more \| all \| unknown \| True | 3 | ng.shared.etc-ssh-sshd-config-or-etc-ssh-sshd-config-d-clientaliveinterval-600, ng.shared.the-maximum-number-of-repeating-characters-is-limited-to-three-when-pass, ng.shared.the-maximum-number-of-repeating-characters-of-the-same-character-class-b |
| subexpression/equals/one_or_more/all/other \| one_or_more \| all \| unknown \| False | 3 | SV-258147.automated, ng.shared.linux-must-disable-core-dumps-for-all-users, ng.shared.linux-must-prohibit-the-use-of-cached-authenticators-after-one-day |
| subexpression/greater_than_or_equal/one_or_more/all/other \| one_or_more \| all \| unknown \| True | 3 | ng.shared.at-least-8-characters-must-change-when-passwords-are-changed, ng.shared.passwords-contain-at-least-four-character-classes, ng.shared.passwords-must-have-a-minimum-of-15-characters |
| subexpression/pattern_match/one_or_more/all/string \| one_or_more \| all \| regex_unrecognized \| True | 3 | SV-285315.automated, SV-285316.automated, SV-285323.automated |

[Machine-readable complete groups and source Test IDs](textfile-shapes.json).

Do not infer that a Python regex capture means lossless OVAL
textfilecontent54 semantics. Prioritize one-feature semantic gates
with original XML differential tests, not speculative YAML rewrites.
No A/B bake-off until all six content streams have comparable support.
