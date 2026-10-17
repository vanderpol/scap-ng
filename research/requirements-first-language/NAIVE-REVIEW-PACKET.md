# SCAP-NG authoring language — clean-room first-read challenge

**Blind review packet. No answer key.** Designed for a **new ChatGPT conversation with no SCAP-NG/OVAL history**, or for a human auditor unfamiliar with this language. The candidate examples below are experimental, not an accepted specification. Do not send the adjacent research README or prior critique into the new chat until this first pass is frozen.

## Paste the following entire section into a brand-new ChatGPT conversation

--- BEGIN REVIEW INPUT ---

You are a security compliance auditor who has never encountered this YAML-like Assessment language. Do not assume it behaves like Python, OVAL, Ansible, or any other known language. Your only documentation is the samples below.

Your assignment is **not** to compliment the design or defend it. Explain, in ordinary language, what you can confidently infer. Whenever a rule is ambiguous, say **ambiguous** and show two plausible interpretations, including a case where those interpretations disagree. Do not invent scanner behavior, collection guarantees, implicit defaults, or a special result table.

First, read each sample without editing it. For each: (a) state the security requirement in one or two sentences, (b) identify what is selected vs what must be true, (c) answer the zero-result and multi-result questions below with **Pass / Fail / Cannot determine** and why, (d) name misleading or redundant syntax, and (e) give confidence High/Medium/Low.

### Sample A — required mount

~~~yaml
id: home-mount
require:
  every: linux.mounts
  where:
    mount_point: {equals: /home}
  must:
    mount_options: {contains: nosuid}
~~~

### Sample B — optional population

~~~yaml
id: guest-accounts
require:
  every: windows.accounts
  where:
    category: {equals: guest}
  must:
    enabled: {equals: false}
~~~

### Sample C — explicitly empty policy

~~~yaml
id: home-mount-explicit
require:
  every: linux.mounts
  where:
    mount_point: {equals: /home}
  must:
    mount_options: {contains: nosuid}
  if_empty: fail
~~~

### Sample D — requirement that the population exists

~~~yaml
id: home-mount-required
require:
  every: linux.mounts
  where:
    mount_point: {equals: /home}
  must:
    mount_options: {contains: nosuid}
  require_at_least_one: true
~~~

### Sample E — scoped nested relation

~~~yaml
id: home-file-ownership
require:
  every: linux.accounts
  as: user
  where:
    uid: {at_least: 1000}
  must:
    every: linux.files
    using:
      under: '$user.home_dir'
    must:
      owner: {equals: '$user.username'}
~~~

### Sample F — compound security alternatives

~~~yaml
id: login-policy
require:
  any:
    - all:
        - some: windows.user_right_assignments
          using: {right: SE_DENY_REMOTE_INTERACTIVE_LOGON_NAME}
          must:
            principal: {equals_ignore_case: Guests}
        - some: windows.user_right_assignments
          using: {right: SE_DENY_REMOTE_INTERACTIVE_LOGON_NAME}
          must:
            principal: {equals_ignore_case: LocalAccount}
    - some: windows.user_right_assignments
      using: {right: SE_DENY_REMOTE_INTERACTIVE_LOGON_NAME}
      must:
        principal: {equals_ignore_case: Everyone}
~~~

### First-read scenarios — answer for A through E

1. Scanner successfully finishes collection, finds **zero resources matching where**. Is the Assessment Pass, Fail, or ambiguous? Is it the same for A and B?
2. A single matching resource is found, all mentioned fields are present, and its values satisfy must. Result?
3. Three matching resources are found. Two satisfy must; one does not. Result?
4. Resources exist, but one required field is missing. Does missing have the same result as a field that is present but unequal?
5. Scanner cannot finish collection, returning partial resources. Is this the same as successfully finding zero resources?
6. In E, if no users match, what does every mean? If a user has no files, what does inner every mean? Is the user's identity reliably associated with its files?

### Design stress test — no expected answer

- Evaluate Samples C and D: do both fix the same ambiguity? Does either burden novice auditors? Could an editor safely infer what the author intends?
- Interpret **every**, **some**, **none**, and **exactly_one**. Which need a definition distinct from everyday English? Do zero results and errors affect each?
- Write a check meaning: 'The /home mount must exist and use nosuid', and a separate check meaning: 'If guest accounts exist, all must be disabled.' Try using the fewest concepts possible **without silently changing either requirement**.
- What collection or evidence-provider behavior must be defined before these checks can be trusted?
- Which parts of the language feel like asking authors to understand a scanner implementation rather than express a policy?
- Suggest a genuinely different, cleaner approach if you think these syntax shapes are fundamentally wrong; you are not required to keep YAML, or keep these exact terms.

Finally, score **first-read comprehension, policy intent transparency, empty/error semantics, authorability of nested checks, and implementation feasibility** from 1–5. Identify the **three most serious design defects** and which examples demonstrate each. If an answer is not determined by the text, say so rather than assuming the author intended your preferred behavior.

--- END REVIEW INPUT ---

## After saving the blind response

Only then give the reviewer the [full requirements-first proposal](README.md), the [ten complete research YAML examples](examples/), and the earlier source-backed OVAL examples if doing a second technical validation pass. Request a **correction log** that preserves initial interpretations, states evidence for changes, and distinguishes presentation misunderstandings from fundamental model problems.

**Interpretation warning:** One ChatGPT session reading both the blind input and the README after the fact is a useful **sequential self-correction**, not an independently trained model or statistical human usability sample. A fresh chat also does not guarantee a genuinely uninfluenced model, but avoids contamination from this particular conversation.
