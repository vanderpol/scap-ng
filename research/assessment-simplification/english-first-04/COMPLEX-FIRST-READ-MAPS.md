# Complex Assessment first-read maps — source-backed, not a second grammar

**18 October 2026 · Readability research for [#235](https://github.com/vanderpol/scap-ng/issues/235) / [#227](https://github.com/vanderpol/scap-ng/issues/227).** Each outline is derived from the complete experimental source-backed after files. It is a **reader's explanation, not executable alternate authoring syntax**. The original full tests, Objects, Fields, names, multiplicities and `evaluate` expressions remain authoritative. No normative schema, source or compiler change.

## Windows 11 deny Remote Desktop logon — seven real Tests

[Read the complete 0.4 and complete English-first YAML](FULL-03-win11-rights.md). [Pinned source reference](https://github.com/vanderpol/scap-ng-editor-sample-data/blob/99cbceae8d594c44cb509df95975ac1676a2b44a/focused-fixtures/source-backed/authoring/ms_windows_11/assessments/automated/SV-253495.automated.yaml).

**What gets read from the system:** The WMI `win32_computersystem.DomainRole` record, and the principals granted the Windows user-right `SE_DENY_REMOTE_INTERACTIVE_LOGON_NAME`. These are **two different collection sources**; the seven Tests are not seven separate native providers.

**Which checks combine to satisfy the Assessment?** The authored `evaluate.any_of` has **three alternatives**, not a single procedural domain-role decision:

| Alternative | Requirements which must all be satisfied |
| --- | --- |
| Non-domain-controller domain-joined role | DomainRole **1 or 3**, plus denied Local account, Guests, Domain Admins, **and** Enterprise Admins |
| Standalone role | DomainRole **0 or 2**, plus denied Guests |
| Independent Everyone alternative | Denied **Everyone**; no explicit WMI role guard in this third branch |

**Important reading traps** (substantive, not editorial):

- The **Everyone alternative is an independent third OR branch**. An author who unconsciously rewrites the whole Assessment as a two-case `if domain-joined / else standalone` loses that original source structure.
- The two DomainRole State alternatives each contain a `result.record.fields.domainrole` predicate, with distinct record and record-field existence/matching scopes. Flattening both values to an unqualified list or applying `some` to the wrong Item/field population is unsafe.
- `at_least_one_item_matches` on Windows `trustee_name` is not the same as requiring every collected principal to match. **All** required named Tests in a branch must still satisfy that branch.
- `Guests` is a **reused Test** shared by the first two branches. The underlying source is not copied or silently changed.
- Errors and unknowns do not automatically mean `false`. This is OVAL six-state `any_of/all_of`, not ordinary short-circuit Boolean `if/else`.

**Human-readability test:** Without opening the YAML again, can the reviewer explain why an Everyone match can satisfy the third alternative even when a DomainRole Test is unknown? The precise result still depends on all six-state aggregation rules and the results of other alternatives; the goal is to find the actual independent OR branch rather than guess from the title.

## RHEL 9 — initialization dotfiles, two different Item-existence rules

[Read the two complete Assessment documents](FULL-02-linux-files.md). [Pinned source](https://github.com/vanderpol/scap-ng-editor-sample-data/blob/99cbceae8d594c44cb509df95975ac1676a2b44a/focused-fixtures/source-backed/authoring/shared/assessments/linux/other/initialization-files-0740-less-permissive.assessment.yaml).

<text>Note: The following is an **explanation of the exact sources**, not a claim that every name is a hard-coded system fact. The Object selectors and Set filters determine the membership.</text>

| Phase | Source or Test | Reader's required inference |
| --- | --- | --- |
| Acquire users | `users-username-object` | Collect candidate `unix.password` users matching the username selector |
| Choose non-system users | `only-non-system-users-uid-999-home-dirs-excluding-root-object` | Derive source by Set `difference`, excluding users below UID 1000 and users whose home directory is `/` |
| Choose root users | `only-root-users-uid-0-home-dirs-excluding-root-directory-object` | Separate Set difference, excluding UID greater than zero and `/` home directories |
| Expand candidate files | `unix.file` `for_each` with `directory.from: user.home_dir` | Collect dotfiles for each **collected source user**, not create a new compliance Test for each user |
| Restrict candidate Items | Set operand `exclude.type.equals: directory` | Exclude directories from each file source. Keep the authored one-operand union/Set structure for lossless source preservation until proven unnecessary |
| Check file permissions | Two named Tests, one per user category | Each requires eight predicates (`setuid`, `setgid`, `sticky`, group-write/execute, other-read/write/execute) to be `false` |

**The critical difference:** Non-system-user dotfiles use `collected_items_require: may_be_absent_and_all_match`; root-user dotfiles use `at_least_one_exists_and_all_match`. A readability rewrite which says merely *all dotfiles must comply* hides an important requirement about **how many matching Items may be absent**. Field existence is separately governed by `state_fields_require`.

The authored top-level `evaluate.all` requires both named Test outcomes. No inlined Boolean loop or blanket absence default is an acceptable simplification.

## Findings shared by both complex examples

**What helped:** explicit named collections with actual definitions; describing *which* population is quantified; showing top-level `evaluate` branches early in a review; links that resolve source IDs. **What did not:** renaming a Variable without shortening its dependency chain, burying collection behind `gather.union.from.inspect`, or converting `all/any` to presumed executable `if/else`.

**Candidate language direction to test, not yet to promote:** one author-facing location for **source acquisition**, one for **selected Item/field requirements**, and a visible **evaluation graph**. Keep `from` for reuse and distinguish filtered/reused sources from a new native `inspect`. When a Set actually has one operand, preserve its source semantics until independent evidence says it can be collapsed; do not require the author to understand the original OVAL graph to discover that fact.

**First-authoring experiment:** Give a novice a short capability table, ask them to express a two-category permissions check and a three-alternative role check; record when they confuse Test-result aggregation with Item, State-field, record, or Set quantification. The exercise will show whether the current syntax needs composition/reuse, scoped requirements, a clearer visible evaluation layout—or all three.

**Not demonstrated:** authored replacement YAML for these complex Assessments passing exact reversal, independent runtime collection/result parity, real novice comprehension results or a new accepted 0.4 grammar. These are the next research acceptance gates, not facts to infer from this document.
