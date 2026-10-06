# RHEL 9 default-manual automation triage

> **RESEARCH ONLY — INITIAL HUMAN TRIAGE, NOT AN AUTOMATION CLAIM**

RHEL 9 has 27 Rules whose default Assessment is manual in the diagnostic
inventory. Each procedure was read individually.

The purpose of this first pass is to avoid a misleading question such as
“contains a command, therefore shellcommand.” Many manual checks use commands
only to gather evidence and then require organizational approval, external
policy, or human classification.

## Provisional categories

### Strong host-local shellcommand candidates

These appear to have finding logic that is local to the assessed host and can
plausibly be expressed deterministically as a command-oriented assessment,
subject to exact-result proof:

| Rule | Why |
| --- | --- |
| SV-257932 | Detect incorrectly labelled device nodes; existing Check Text is already deterministic host-local commands with a documented exception. |
| SV-257937 | Determine active firewalld zones/targets and require deny-all/drop behavior. |
| SV-258028 | Compare dconf database modification times to keyfiles; current procedure already defines deterministic command logic. |
| SV-258096 | Verify pam_faillock presence/order, including included/substacked PAM configuration. A dedicated PAM parser may ultimately be better, but this is a plausible command-oriented candidate. |

**Initial count: 4 / 27.**

This is deliberately conservative. These four still require proof that exit,
stdout/stderr and error semantics can represent every branch of the Check Text.

### Strong structured-native candidates

These look more appropriate for typed collection than shell commands:

| Rule | Likely structured approach |
| --- | --- |
| SV-258044 | Enumerate local interactive users, inspect initialization files, compare umask. |
| SV-258052 | Enumerate interactive users and verify home directories exist. |
| SV-258053 | Join user primary GID to home-directory group ownership. |

**Initial count: 3 / 27.**

These are especially useful tests of whether `for_each` / local binding can
make a previously manual check clearer without shell scripting.

### Automation likely requires organizational or external input

A scanner can collect much of the evidence, but the finding decision depends on
information that is not inherent in host state:

- **SV-257778** — patch compliance depends on current Red Hat errata,
  organizational patch frequency and IAVA overrides.
- **SV-257879** — encryption may be satisfied outside the OS via approved
  hypervisor/storage mechanisms.
- **SV-257928** — world-writable directory owner may be an approved application
  account.
- **SV-257940** — requires site/program PPSM CLSA and prohibited CAL data.
- **SV-257945** — authoritative DOD time source needs an approved source set.
- **SV-257950** — IPsec tunnel authorization is an ISSO/organization fact.
- **SV-258040** — wireless use can depend on documented/approved hardware use.
- **SV-258047** — the scanner needs to know which accounts are temporary and
  their authorized lifetime/start point.
- **SV-258050** — paths outside the normal home/default set may be approved by
  the ISSO.
- **SV-258058** — authorized local account list is organizational input.
- **SV-258132** — alternate MFA / certificate mapping mechanisms may be
  organization-specific.
- **SV-258135** — approved integrity tool, schedule and designated recipients
  are partly organizational.
- **SV-258136**, **SV-258138**, **SV-258139** — AIDE is only one allowed file
  integrity implementation; alternate approved tools require capability/input
  modeling.

These may become excellent demonstrations of SCAP-NG organizational input
rather than shellcommand.

### Needs additional domain-model research before automation

- **SV-257857 / SV-257858 / SV-257859** — determining which configured file
  systems are “used with removable media” is the hard part; parsing mount
  options is trivial. Shellcommand alone would hide this ambiguity.
- **SV-258127** — discovering private keys and proving passphrase protection
  safely interacts with alternate MFA and potentially sensitive key material.
- **SV-258150** — requirement permits alternate logging packages and the Check
  Text includes a runtime test-message path; a logging capability may be safer
  than a side-effecting command.

## Initial result

At this stage, **7 / 27** manual Rules look like relatively strong host-local
automation candidates: 4 command-oriented and 3 structured-native.

That is **not** a final automation percentage. The other 20 are not “cannot be
automated”; many appear automatable if SCAP-NG supplies explicit
organizational input or richer domain capabilities. The point is that
shellcommand by itself should not be used to paper over missing policy inputs.

## Next proof step

For each of the seven strong candidates:

1. reconstruct the exact Check Text finding logic;
2. design the smallest readable research syntax;
3. lower it to explicit semantic IR;
4. enumerate pass/fail/error/not-applicable cases;
5. compare the result to the manual procedure;
6. reject the automation if any human decision has been silently guessed.

Only after that should this document report a confirmed automation count.
