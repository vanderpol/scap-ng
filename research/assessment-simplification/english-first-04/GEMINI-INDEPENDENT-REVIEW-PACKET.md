# Independent Gemini review packet — SCAP-NG Assessment authoring v2

**Copy the entire contents of this file into a new Gemini conversation with no SCAP-NG history or custom project memory. Do not supply other project notes, prior critiques, answer keys, or the author's intended interpretation.** This is an answer-free external review request. Gemini must not assume that the syntax is correct merely because the examples are source-based. **Do not read adjacent repository files before completing Part 1.**

## Instructions to the independent reviewer

You are assessing an *experimental*, pre-alpha authoring format intended for security administrators and for eventual use in a guided editor. It is **not** adopted SCAP-NG v0.4 syntax, and the YAML excerpts are not complete executable files. You have not participated in designing it.

**Goal:** Identify incorrect, confusing, ambiguous, overly nested, or semantically dangerous constructs. Prefer pointing to a specific counterexample over giving a preference score. Do not flatter the design. Your task is **not** to rubber-stamp a spec, infer hidden defaults, or invent compliant scanner behavior when it is unspecified.

Complete the evaluation in two clearly separated parts **in order**:

- **Part 1 (blind):** Read only the exact excerpts and questions below. **No internet, repository browsing, OVAL glossary, prior conversation, or neighboring review documents.** Answer from the YAML *as a first-time reader*. For every result prediction label your confidence **high/medium/low** and distinguish **pass, fail, indeterminate, or cannot infer from excerpt**. If error/unknown/not-applicable behavior cannot be inferred, write exactly that rather than assuming.
- **Part 2 (adversarial technical review):** Only after completing Part 1, open the five full source-linked Assessment files provided near the end. Check whether the proposed wording accurately maps to all of the original checks, collection dependencies, cardinalities, record alternatives and result paths. Read only the five linked YAML files; **do not open prior review rationale, design advice, or answer keys**. Flag every claim that the excerpt does *not* establish or any semantics that seem to have changed. If you cannot open a file, flag that limitation; do not invent its contents.

You may use internal multiple critical perspectives (auditor, schema implementer, guided-editor user, malicious edge-case designer). They are **not** independent outside reviewers, so say so. Present unresolved questions and counterexamples as failures of this review, not as evidence of correctness.

---

# Part 1 — Blind reading of authoring excerpts

For each case answer in plain English: (1) what type of data is being selected or inspected, when shown, (2) how many root data Items must exist, (3) how many of them must match, (4) how missing, duplicate, disagreeing, or unreadable data affects the result, if ascertainable, and (5) which exact YAML terms you could not understand confidently.

### A. Linux filesystem partitions

\`\`\`yaml
inspect: linux.partition
where:
  mount_point: {matches_regex: '.*\/home'}
require:
  items: at_least_one
  matching_items: all
  mount_options: {at_least_one_value_equals: nosuid}
\`\`\`

Evaluate separately: **A1** no partitions are selected, with complete successful collection; **A2** one selected partition reports two options \`rw\` and \`nosuid\`; **A3** two partitions are selected, of which only one has \`nosuid\`; **A4** one partition exists, but its mount option field is unreadable; **A5** acquisition is incomplete.

### B. Windows WMI record alternatives

\`\`\`yaml
from: windows-wmi57-object
require:
  items: at_least_one
  matching_items: all
  states:
    or:
      - result:
          records: at_least_one
          matching_records: all
          domainrole: {equals: '1'}
      - result:
          records: at_least_one
          matching_records: all
          domainrole: {equals: '3'}
\`\`\`

Evaluate separately for **one collected root Item** with records: **B1** \`['1']\`, **B2** \`['3']\`, **B3** \`['1','3']\`, **B4** \`['1','1']\`, **B5** no records, **B6** one record with a missing DomainRole, **B7** an incomplete WMI response. Explain specifically which unit the \`or\` combines: *record values, whole record tests, or entire root Items*, or say you cannot determine.

### C. Windows Guests user right

\`\`\`yaml
from: windows-userright-object
require:
  items: at_least_one
  matching_items: at_least_one
  trustee_name: {case_insensitive_equals: Guests}
\`\`\`

Evaluate: **C1** no trustee Items, **C2** two Items (\`Guests\` and \`Administrators\`), **C3** two \`Administrators\` Items, **C4** one Item with missing trustee_name, **C5** two identical \`Guests\` Items. What is and is not implied by duplicates?

### D. Linux account-derived file permissions

\`\`\`yaml
require:
  items: may_be_absent
  matching_items: all
  fields:
    and:
      - setuid: {equals: false}
      - setgid: {equals: false}
      - sticky: {equals: false}
      - group_write: {equals: false}
      - group_execute: {equals: false}
      - other_read: {equals: false}
      - other_write: {equals: false}
      - other_execute: {equals: false}
    listed_fields_must_exist: true
\`\`\`

Evaluate: **D1** no files, all collection successful; **D2** one file with all eight fields set to false; **D3** one file with seven fields false, one true; **D4** one file lacks \`setuid\`; **D5** one file has unreadable \`setuid\`; **D6** one file passes and one fails. Which exact population is optional, and what does \`listed_fields_must_exist\` refer to? Identify anything that cannot be determined because acquisition is absent from this excerpt.

### E. Apache configuration command output

\`\`\`yaml
require:
  items: at_least_one
  matching_items: all
  stdout_line:
    when_present_matches_regex: '\s*KeepAlive On'
\`\`\`

Evaluate: **E1** no command Items; **E2** one command Item with no stdout_line field; **E3** one with \`KeepAlive On\`; **E4** one with \`KeepAlive Off\`; **E5** a command execution error. Is \`when_present\` about the whole Item, the stdout field, or an expected source configuration file? Does the snippet prove anything about the other Apache checks?

### F. Windows DNS signature-validity bounds

\`\`\`yaml
all_state_fields_exist: true
require:
  items: at_least_one
  matching_items: all
  states:
    and:
      - stdout_line: {greater_than_or_equal: 48}
      - stdout_line: {less_than_or_equal: 168}
\`\`\`

Evaluate: **F1** \`stdout_line: 24\`; **F2** \`stdout_line: 72\`; **F3** \`stdout_line: 200\`; **F4** absent \`stdout_line\`; **F5** unreadable or incomplete field; **F6** duplicate stdout values \`72\` and \`200\`. Can you infer what the inherited top-level \`all_state_fields_exist\` means and why it sits outside \`require\`? Is a comparison to numeric-looking text fully specified?

### G. Final logic for seven named Windows checks

\`\`\`yaml
evaluate:
  or:
    - and:
        - test: domain_joined_non_dc
        - test: deny_local_account
        - test: deny_guests
        - test: deny_domain_admins
        - test: deny_enterprise_admins
    - and:
        - test: standalone_computer
        - test: deny_guests
    - test: deny_everyone
\`\`\`

These are abbreviated *display IDs*, not authoritative source IDs. How many top-level OR alternatives are written? Can more than one alternative be satisfied at the same time? Is this a set of independent alternatives or an ordered if/else? What happens when one leaf is unknown, error, not-applicable, or not collected? Which questions are impossible to answer from the expression alone?

---

# Part 1B — Authorability and deletion test

Without reading outside docs, try to **write one original new Assessment fragment** in the same style: inspect a Windows password policy, require at least one collected Item, require every collected Item's \`min_passwd_len\` field to be at least 14, and identify any field-presence assumption you cannot justify. If you need more structural rules, explicitly say so; do not invent them silently.

Then try to express a more complex new requirement: collect filesystem Items and require **exactly one existing Item** with a specified path, independently of the Item's owner comparison. If the current syntax is insufficient or ambiguous, explain precisely why.

Rate these 1–5 with reasoning: (a) **readability as an auditor**, (b) **new content authorability**, (c) **schema implementability**. List your five most serious issues, sorted by semantic danger rather than cosmetic dislike. Suggest the **smallest possible deletion or simplification** for each; avoid adding synonyms, wrappers, or a second DSL unless truly necessary.

**STOP AND RECORD PART 1 ANSWERS BEFORE READING THE SOURCES.**

---

# Part 2 — Source-backed technical challenge

Now—and only now—compare your blind predictions with these **five complete, original source-reversible research YAML files**, on ordinary github.com:

1. [RHEL9 home nosuid complete](https://github.com/vanderpol/scap-ng/blob/main/research/assessment-simplification/english-first-04/canonical-operators/linux-home.canonical.research.yaml)
2. [Windows 11 WMI and rights, seven checks](https://github.com/vanderpol/scap-ng/blob/main/research/assessment-simplification/english-first-04/canonical-operators/windows-wmi-rights.canonical.research.yaml)
3. [Linux dependent initialization files](https://github.com/vanderpol/scap-ng/blob/main/research/assessment-simplification/english-first-04/canonical-operators/linux-files.canonical.research.yaml)
4. [Apache KeepAlive and MaxKeepAliveRequests](https://github.com/vanderpol/scap-ng/blob/main/research/assessment-simplification/english-first-04/canonical-operators/apache.canonical.research.yaml)
5. [Windows DNS signatures](https://github.com/vanderpol/scap-ng/blob/main/research/assessment-simplification/english-first-04/canonical-operators/dns.canonical.research.yaml)

These source files use some **different, older research keys**. Do *not* assume a key with a newer English name is semantically equivalent just because the names seem related. Treat \`matching_items\`, \`matching_records\`, \`may_be_absent\`, and \`listed_fields_must_exist\` in the blind excerpts as **unverified proposed rewrites**. Source structural reversibility of older representations is **not** scanner-result parity.

**Technical challenge:**

1. For each proposed rewrite, say whether the original source makes equivalence **proved**, **plausible but unproved**, or **false**. Quote the exact structural path/reference (not large excerpts). Say which six-state or missing-field case would distinguish non-equivalent spellings.
2. Check whether any excerpt omitted a behavior that would materially mislead an auditor about the **complete** Assessment: collection dependencies/Variables, filter/source type, root-vs-field-vs-record existence, original complete AND/OR tree, inherited presence rules, or error flags.
3. Check the Windows \`['1','3']\` nested record case against its **whole State grouping**, the root/non-system Linux population distinction, Apache optional stdout versus required Item, and DNS inherited field existence. Do not flatten record States or "simplify" source regex patterns without proving equivalence.
4. Identify the smallest sufficient counterexample for any rule you think is unsafe, including zero/duplicate Items, missing/absent fields, collection error, unknown, not-applicable, and incomplete data.
5. Evaluate whether a guided editor could permit **every proposed authoring control to map to exactly one compiler contract**. If not, identify the ambiguous control and what data the editor needs. Distinguish an editor *display label* from the one authoritative YAML schema.

## Required final response format

Provide the following sections, in order:

- **Blind Part 1 answers:** A1–G and Part 1B, preserving original confidence/uncertainty; do not retrospectively correct them.
- **Source cross-check:** corrections discovered only after opening the five files, each with a concrete reference.
- **Critical bugs or semantic hazards:** sorted by severity; exact scenario, predicted vs expected behavior, what source evidence supports that comparison. If authoritative six-state expectation is unavailable, label it *unproved*, not a found discrepancy.
- **Ambiguous or unnecessary keys:** what to remove or change, with minimal diff and justification; mark proposed changes untested.
- **Editor and novice-author verdict:** where authors would likely choose the wrong option and what UI explanation or typed selection is missing.
- **Go / revise / reject verdict:** explicitly distinguish *lexical readability*, *source reconstruction*, *six-state scanner semantics*, and *auditor comprehension*. Never merge their confidence.
- **Three most valuable next tests**, prioritizing counterexamples that could overturn your verdict.

**Do not aim to agree with the project. A justified “cannot determine” is a useful finding.**
