# RHEL 9 default-manual automation review

> **RESEARCH ONLY — NOT AN ACCEPTED SCAP-NG DESIGN OR AUTOMATION DECISION**

The current RHEL 9 inventory contains 27 Rules whose default Assessment is
manual. Their procedures were reviewed individually. This review is deliberately
conservative: a command appearing in Check Text does not make the requirement
safely automatable.

## Preliminary classification

### Deterministic automation candidates

These appear capable of automation without requiring an external approval list,
although the best implementation may be typed collection rather than
`shellcommand`.

| Rule | Preliminary direction | Why |
| --- | --- | --- |
| SV-257937 | structured or controlled command | firewalld state/zone target can be measured directly |
| SV-258028 | controlled command or file metadata | compare dconf DB/keyfile modification times; GNOME applicability still required |
| SV-258044 | structured foreach/text | inspect local interactive-user initialization files for umask |
| SV-258096 | structured PAM parser preferred | ordering plus include/substack semantics are deterministic but grep alone is incomplete |
| SV-258150 | controlled command / logging capability | cron logging can be tested, but active probe and alternate logging packages need careful semantics |

Count: **5 / 27** preliminary candidates.

### Potentially automatable with a better typed domain model

These are not good reasons to default to shell commands. The difficult part is
reliable system modeling or scanner-aware enumeration.

| Rule | Missing capability/domain knowledge |
| --- | --- |
| SV-257857 | identify removable-media-backed filesystems, then test `noexec` |
| SV-257858 | identify removable-media-backed filesystems, then test `nodev` |
| SV-257859 | identify removable-media-backed filesystems, then test `nosuid` |
| SV-257928 | enumerate local world-writable directories and compare ownership to approved/system accounts |
| SV-257932 | enumerate device files and SELinux labels, including legitimate device exceptions |
| SV-258052 | robustly identify local interactive users, including privileged-UID exceptions |
| SV-258053 | correlate interactive users, primary GID, and home-directory ownership |

Count: **7 / 27**.

### Requires organizational/external input or approved exception knowledge

A scanner can collect much of the evidence, but the Rule cannot be decided
correctly from host state alone without supplied policy/context.

| Rule | External knowledge needed |
| --- | --- |
| SV-257778 | organizational patch/update frequency and current applicable vendor security updates |
| SV-257879 | documented approved alternate data-at-rest encryption |
| SV-257940 | site/program PPSM CLSA/CAL authorization |
| SV-257945 | authoritative/approved DOD time sources |
| SV-257950 | approved/documented IP tunnels |
| SV-258040 | ISSO-approved wireless interfaces / applicability |
| SV-258047 | which accounts are temporary and their approved lifetime context |
| SV-258050 | ISSO-approved PATH exceptions |
| SV-258058 | authoritative list of approved local interactive accounts |
| SV-258127 | approved alternate multifactor authentication and private-key scope |
| SV-258132 | approved alternate multifactor authentication / certificate mapping method |
| SV-258135 | selected integrity product, required schedule, and notification target |
| SV-258136 | alternate approved integrity product and FIPS hashing configuration |
| SV-258138 | alternate approved integrity product and ACL verification |
| SV-258139 | alternate approved integrity product and xattr verification |

Count: **15 / 27**.

## Preliminary conclusion

The manual-rule review does **not** support a strategy of converting most manual
Rules to shell commands.

Only about five immediately look like deterministic automation candidates.
Another seven look more promising if SCAP-NG/scanners have better typed domain
models. The largest group—15 Rules—depends materially on organizational policy,
approval, exception, or implementation context.

That strengthens the case for organizational input as a first-class concept.
It also suggests that automation coverage should distinguish:

1. host state that can be measured;
2. organizational facts supplied to the assessment; and
3. genuinely human judgment.

A future study should test whether organizational input can safely convert some
of the 15 into deterministic automated checks without baking local policy into
the benchmark.
