# Independent SCAP-NG readability test — raw authoring YAML vs auditor preview

**Research #235. Answer-free.** This is a usability comparison, not a new executable grammar or scanner validation.

Use separate fresh Gemini chats or unfamiliar auditors: one should read *only* full revised YAML, the other should read *only* the generated source-derived preview. The same Gemini chat comparing both is useful but is **not** two independent reviewers. Do not reveal the prior design feedback, results or reference truth tables until both first reads are saved.

**If Gemini cannot open a GitHub file, use github.com's Raw option, save it and attach it. Do not claim the source was checked when it was inaccessible.**

| Assessment | Full research YAML | Generated read-only auditor preview |
| --- | --- | --- |
| RHEL9 home nosuid | [YAML](linux-home.revised.research.yaml) | [Preview](generated-previews/linux-home.md) |
| Windows 11 WMI and denied RDP rights | [YAML](windows-wmi-rights.revised.research.yaml) | [Preview](generated-previews/windows-wmi-rights.md) |
| Linux account-dependent files | [YAML](linux-files.revised.research.yaml) | [Preview](generated-previews/linux-files.md) |
| Apache KeepAlive/MaxKeepAliveRequests | [YAML](apache.revised.research.yaml) | [Preview](generated-previews/apache.md) |
| Windows DNS signature validity | [YAML](dns.revised.research.yaml) | [Preview](generated-previews/dns.md) |

## Part 1 — first-time comprehension without other sources

For each Assessment: (1) identify exact inspected source(s), selectors, filters and dependent collection you can actually see; (2) distinguish root Items, nested records and repeated field values; (3) explain Item existence, Item matching and field presence; (4) reconstruct **all** passing OR/AND paths including repeated check references; (5) identify what cannot be known from only this artifact; (6) attempt to author a related new check from scratch and identify which pieces require documentation/editor guidance.

For each scenario use Pass / Fail / Error / Unknown / Not Applicable / Not Evaluated / **Cannot infer** and confidence High/Medium/Low. Do not invent collector errors, defaults, deduplication or numeric coercion.

Counterexamples:

- RHEL: zero selected partitions on complete collection; one partition with rw and nosuid; two mounts only one with nosuid; incomplete collection; whether the unanchored source regex selects a path /home/users.
- Windows: nested WMI records [1], [3], [1,3], and absent records; different root Items with different nested records; Guests and non-Guests, and all three final OR branches.
- Linux: non-system user files absent vs root user files absent; present Item with setuid absent/unreadable; one noncompliant file; incomplete dependent discovery.
- Apache: absent command Item vs absent stdout field; right/wrong stdout; nonzero exit status with error_if_exit_status_not_0 false; partial command output.
- DNS: values 24, 72, 200; two repeated stdout_line values *inside the same Item*; field absent/unreadable; one State error and another definitive false; incomplete collection.

**STOP here and preserve every raw answer and confidence.** Do not read the source-pack conclusions or table ledger first.

## Part 2 — source and six-state adjudication

Now provide the [offline evidence pack of ten complete original/revised YAML files](GEMINI-PHASE2-OFFLINE-SOURCE-PACK.md) and the [generated inherited OVAL truth-table scenarios](generated-previews/SEMANTIC-BOUNDARY-LEDGER.md). Recheck every prediction against the original source, collection error flags, whole-State grouping, field/record/value multiplicity and actual documented result semantics. Never overwrite blind answers.

Categorize every incorrect prediction as **wrong authored semantics**, **unclear YAML**, **misleading generated explanation**, **missing contract/runtime evidence**, or **incorrect reviewer assumption**. Only supported authored-language problems should trigger syntax changes; presentation errors should fix the generated preview. An incorrect reviewer assumption should not change scanner behavior.

## Required report

Return original blind responses, individual corrected responses, a raw-versus-preview comprehension comparison, new authoring attempts, severe counterexamples and a proposed minimal correction for each true defect. Separately score audited readability, new-author success, source fidelity, six-state handling and guided-editor usability. A single-model exercise is qualitative evidence, not an independent human usability sample.

**Do not declare 0.4 approved.** Missing-field/error semantics, original OVAL runtime parity and broader six-STIG conversion remain technical gates in [issue #229](https://github.com/vanderpol/scap-ng/issues/229).
