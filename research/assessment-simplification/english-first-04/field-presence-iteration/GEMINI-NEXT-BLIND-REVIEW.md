# Independent Gemini review — revised SCAP-NG Assessment language

Give this document ALONE to a fresh Gemini conversation without prior reviews, rationale, or answer keys. This is a research-only authoring candidate, not approved SCAP-NG 0.4 syntax. Be a first-time security auditor, a skeptical compiler engineer, and a novice author, in sequential passes. Do not summarize intentions, flatter the design, or invent undocumented defaults and scanner capabilities.

Complete four phases IN ORDER. Preserve your original blind answers unchanged after source inspection. If a source is inaccessible, explicitly say so rather than inventing its contents.

## Phase 1: Blind comprehension — DO NOT BROWSE SOURCES YET

For every case give the expected result from Pass / Fail / Error / Unknown / Not Applicable / Not Evaluated / Cannot infer, confidence High/Medium/Low, and the line of YAML supporting the answer. Unknown or incomplete result truth tables must not be guessed.

### A. RHEL partition selection versus repeated mount-option values

~~~yaml
inspect: linux.partition
where:
  mount_point: {matches_regex: '.*\/home'}
require:
  items: at_least_one
  matching_items: all
  mount_options:
    at_least_one_value_equals: nosuid
~~~

A1: complete collection with zero selected partitions. A2: one selected partition with options rw and nosuid. A3: two selected partitions, only one has nosuid. A4: duplicate identical partitions. A5: incomplete collection with one compliant selected partition. A6: how would selection of /home/users differ from /home? What does where select compared with matching_items and field-value matching?

### B. Windows WMI root Items and nested records

~~~yaml
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
~~~

One root Item unless stated otherwise. B1: records [1]. B2: [3]. B3: [1,3]. B4: [1,1]. B5: no records. B6: missing domainrole. B7: unreadable record. B8: two root Items whose complete record populations differ. Explain whether OR combines whole States, separate records, or root Items. Would membership in [1,3] preserve this original requirement? Identify what the excerpt cannot tell you.

### C. Windows logon-right trustee matches

~~~yaml
from: windows-userright-object
require:
  items: at_least_one
  matching_items: at_least_one
  trustee_name: {case_insensitive_equals: Guests}
~~~

C1: zero trustee Items. C2: Guests and Administrators. C3: only Administrators. C4: one valid Guests and one unreadable name. C5: duplicate Guests. C6: can you tell which exact Windows user right is queried? Are item existence and matching genuinely independent or needlessly redundant?

### D. Linux user-derived initialization files

~~~yaml
require:
  items: if_present
  matching_items: all
  field_presence: required
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
~~~

D1: complete, zero selected files. D2: one file with all eight fields false. D3: one field true. D4: missing setuid field. D5: unreadable setuid. D6: two files, one violates the requirement. D7: incomplete collection. D8: a separate root-user branch requires at least one Item; does this excerpt cover it? Which fields does the policy apply to? Does it accidentally imply every possible filesystem field must exist? What about nested records?

### E. Apache required command Item, optional output field

~~~yaml
require:
  items: at_least_one
  matching_items: all
  stdout_line:
    presence: may_be_absent
    matches_regex: '\s*KeepAlive On'
~~~

E1: zero command Items. E2: one Item with no stdout_line field. E3: line with KeepAlive On. E4: KeepAlive Off. E5: two Items, one matching and one not. E6: unreadable stdout. E7: failed command or incomplete output. What does may_be_absent apply to? Does it permit an unreadable value? Can this one check prove compliance with the entire Apache Assessment?

### F. Windows DNS two States and explicit field existence

~~~yaml
require:
  items: at_least_one
  matching_items: all
  field_presence: required
  states:
    and:
      - stdout_line: {greater_than_or_equal: 48}
      - stdout_line: {less_than_or_equal: 168}
~~~

F1: value 24. F2: 72. F3: 200. F4: stdout_line missing. F5: unreadable. F6: repeated values 72 and 200. F7: incomplete collection. F8: one comparison error, the other definitively false. Does field_presence cover both State branches? Can you prove a range shorthand is equivalent? What is assumed about numeric-looking text?

### G. Seven checks and the three complete Windows alternatives

~~~yaml
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
~~~

G1: count the top-level alternatives. G2: are they ordered procedural conditions? G3: suppose one alternative is definitively True, another Error. G4: one child Unknown and others False. G5: would descriptive names for these alternatives require new executable authoring syntax or could they be generated from the same tree? G6: what must be learned from the multi-state specification rather than the excerpt alone?

### New authoring tests — still no source browsing

1. Windows password policy: require at least one Item and every Item's minimum password length >=14, without assuming undocumented field existence.
2. Filesystem: require exactly one selected Item for a fixed path and check owner separately. Do not invent an exact-count operator unless you can justify its spelling.
3. Optional Windows registry value: if present it must match; unreadable must not be treated as absent.
4. Three named conditions: (A AND B) OR C, with explicit logic.
5. Linux dependent discovery: get non-system users, derive home directory for each, collect initialization files, check every collected file. Identify where collection references and source identity must be defined.

State which exercise you could actually author without documentation, and why. Identify five misleading or unnecessary constructs, or say no concrete evidence was found.

**STOP HERE. Preserve all original blind answers and confidence levels before continuing.**

## Phase 2: Investigate real complete source-backed YAML

Now open the five FULL revised research Assessments:

- https://github.com/vanderpol/scap-ng/blob/main/research/assessment-simplification/english-first-04/field-presence-iteration/linux-home.revised.research.yaml
- https://github.com/vanderpol/scap-ng/blob/main/research/assessment-simplification/english-first-04/field-presence-iteration/windows-wmi-rights.revised.research.yaml
- https://github.com/vanderpol/scap-ng/blob/main/research/assessment-simplification/english-first-04/field-presence-iteration/linux-files.revised.research.yaml
- https://github.com/vanderpol/scap-ng/blob/main/research/assessment-simplification/english-first-04/field-presence-iteration/apache.revised.research.yaml
- https://github.com/vanderpol/scap-ng/blob/main/research/assessment-simplification/english-first-04/field-presence-iteration/dns.revised.research.yaml

Compare to the five original research YAML files:

- https://github.com/vanderpol/scap-ng/blob/main/research/assessment-simplification/english-first-04/canonical-operators/linux-home.canonical.research.yaml
- https://github.com/vanderpol/scap-ng/blob/main/research/assessment-simplification/english-first-04/canonical-operators/windows-wmi-rights.canonical.research.yaml
- https://github.com/vanderpol/scap-ng/blob/main/research/assessment-simplification/english-first-04/canonical-operators/linux-files.canonical.research.yaml
- https://github.com/vanderpol/scap-ng/blob/main/research/assessment-simplification/english-first-04/canonical-operators/apache.canonical.research.yaml
- https://github.com/vanderpol/scap-ng/blob/main/research/assessment-simplification/english-first-04/canonical-operators/dns.canonical.research.yaml

Then, for truth-table claims only, consult the source evaluation contract at:
https://github.com/vanderpol/scap-ng/blob/main/specification/assessment/assessment-method.md
and source-selection/filter rules at:
https://github.com/vanderpol/scap-ng/blob/main/specification/assessment/selection-and-filters.md

For every proposed grammar improvement classify its fidelity as source-exact / source-plausible but runtime-unproven / changed source meaning / cannot verify. Verify full collection selectors, regexes, named Objects, exact Windows logon right, Windows whole-record States, Linux account populations and foreach, all four Apache checks and Variables, all five DNS checks and Variables, the full final evaluation tree, and original collection error flags.

Never invent a new typed collector to replace source complexity without designing and verifying it. Never infer generic six-state behavior from regular two-valued AND/OR. Do not mark a new YAML grammar normative or scanner-conformant merely because the existing five source files can be reconstructed.

## Phase 3: Design challenge

Can field_presence: required and local presence: may_be_absent express the source requirements precisely with a proven group/test/field precedence rule and record isolation? Is a shared Test-level required policy acceptable for an editor if the editor displays its effective value at each use site? Compare no-extra-wrapper inspect/where/require to nested select/assert over the COMPLETE source files, not just simple snippets. Distinguish meaningful simplification from renamed but lost collection graphs. Show improvements in YAML with intact exact source selectors, Variables and evaluate.

## Phase 4: Repeat critical reviews

Perform independent *perspectives* (auditor, novice author, implementer, six-state adversary) in at least three rounds; list issue -> change -> newly introduced risk. Those perspectives are not independent people or model sessions. Stop if two passes find no new vocabulary issues, but state clearly if technical semantics remain unproved.

## Required outputs

1. Original untouched blind answers A1–G plus all five authoring exercises, with confidence.
2. Source cross-check and corrections, referencing exact paths and counterexamples.
3. Defect table prioritized by potential false compliance results.
4. Revised YAML examples for all six patterns and the complete Windows evaluate tree; distinguish excerpts from full files.
5. Before/after complexity and fidelity critique, including where a simple-looking new capability is fictional.
6. Repeated-review log, open semantic/CI/editor test gates.
7. Verdict: retain/revise/reject candidate, separate scores for readability, authorability, whole-source fidelity, multi-state correctness, and editor usability.

Do not skip individual scenario predictions and replace them with a general architecture essay. A carefully demonstrated wrong-result counterexample is more useful than a favorable design score.
