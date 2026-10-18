# B source shellcommand compatibility pilot

**Research · #237 · October 2026.** Compiles bounded *converted 0.3* source Assessments to fixture-only B IR. This is **not** a shell runner, original SCAP 1.4 parity, production scanner or signed bundle.

The pinned [Windows DNS SV-259417](contract-candidate/corpus/source-specimens/independent-shellcommand-dns-small-db533570bbca.source.yaml) uses a static PowerShell query for DNS response-rate limiting mode, a source Test requiring one or more command Items, and a State requiring stdout_line equal to `Enable`.

The [source lowerer](../../tools/research_b_source_shell_lowering.py) accepts only a single direct static command with explicit shell and error flags, plus one literal stdout_line equality State. It retains every query parameter and uses **compiler-owned** `compat_oval_shellcommand_state` IR; the auditor-facing B language is unchanged. It rejects local Variables, dynamic command expressions, extra regex/pattern collection, multi-Test and unsupported State operations.

The [offline adapter](../../tools/research_b_source_shell_snapshot.py) does **not** run commands or PowerShell. It receives externally acquired typed, query-identified Item records. Each Item retains repeated stdout_line and stderr_line arrays and exit_status, with explicit complete/incomplete/error/not-collected statuses. [The evaluator](../../tools/research_b_source_shell_evaluator.py) applies the pinned OVAL Test aggregation over Item-level State outcomes; it does **not** turn each stdout line into a separate Item.

| DNS source fixture observation | Result |
| --- | --- |
| Complete, one command Item with stdout `Enable` | true |
| Complete, same Item with stdout `Disable` | false |
| Complete, same Item with stdout `Enable` plus `Disable` | false |
| Complete, command Item with empty stdout array | false |
| Complete, zero command Items | false |
| Incomplete, one observed `Enable` Item | unknown |
| Incomplete, one observed `Disable` Item | false |
| Wrong command identity, malformed output, or duplicate Item identity | error |

The [source regression tests](../../tools/test_research_b_source_shell.py) also distinguish an empty output array from a **single empty string** in a real RHEL9 USBGuard specimen; those are different OVAL entity-existence inputs.

After initial CI integration the [six-STIG conversion ledger](contract-candidate/corpus/conversion-progress.md) reported **120 automated fixture IR lowerings, including two Windows DNS Assessments**, with 1,550 manual procedures and 725 automated Assessments still unsupported. **Verified original SCAP 1.4-equivalent scanner conversions remain zero**; consult the live ledger for later numbers.

## Why Apache remains a separate gate

All **22 Apache automated source Assessments** in the pinned six-stream cohort have local Variables. The selected [smallest Apache source specimen, SV-214273](contract-candidate/corpus/source-specimens/independent-shellcommand-apache-small-575d1e0ee9d2.source.yaml), discovers an executable path from an earlier process-list collection using regex capture, constructs a later command through string concatenation, collects Apache version text, and compares a captured version. Blindly replacing that dependency chain with one static command would be incorrect.

Next source-compatibility work must support **typed dependency resolution, variable cardinality, explicit shared collection acquisition identity and version operators**, with failure on unresolved references and prohibited hidden command execution. This should remain compiler-owned compatibility machinery unless a shorter native B form can independently prove equivalent source meaning. The [large Apache source specimen](contract-candidate/corpus/source-specimens/independent-shellcommand-1-3d964d126ca8.source.yaml) has five Tests and much deeper variable chains; that is an eventual stress test, not a first implementation shortcut.

The [CI gate](contract-candidate/corpus/source-runtime-ci.md) tracks the shell regression suite. No A/B bake-off before all six complete STIG streams can be converted and verified.
