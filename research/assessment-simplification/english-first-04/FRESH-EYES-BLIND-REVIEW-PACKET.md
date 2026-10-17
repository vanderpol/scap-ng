# SCAP-NG: blind comprehension packet

**For a first-time security auditor or an independent model session.** You do not need to know OVAL or SCAP-NG. Do not open project documentation or search for definitions until you finish answering. You are being asked whether these excerpts are understandable **as written**. A truthful 'cannot determine' is better than inventing semantics.

## Task

For each excerpt, answer in ordinary English: (1) what information is collected, (2) what must happen to pass, (3) what happens if nothing is returned, (4) what happens if multiple Items or values disagree, and (5) whether an unreadable/missing field or collection error is distinguishable from a definite failure. For every answer give a confidence of High/Medium/Low and mark any terms you could not interpret without instructions. Where snippets omit data acquisition, say so rather than assuming how it works.

### A — Linux /home

```yaml
inspect: linux.partition
where:
  mount_point: {matches_regex: '.*\/home'}
require:
  items: at_least_one
  match: all
  mount_options: {at_least_one_value_equals: nosuid}
```

Additional question: if a selected partition has mount options `rw,nosuid`, does it pass? If two partitions are selected and only one has `nosuid`, does the check pass?

### B — Windows computer role

```yaml
from: windows-wmi57-object
require:
  items: at_least_one
  match: all
  states:
    or:
      - result:
          records: at_least_one
          match: all
          domainrole: {equals: '1'}
      - result:
          records: at_least_one
          match: all
          domainrole: {equals: '3'}
```

Additional question: suppose a single computer-system Item includes two records: DomainRole `1` and DomainRole `3`. Does the check pass? How sure are you, and why?

### C — Apache optional configuration field

```yaml
require:
  items: at_least_one
  match: all
  stdout_line:
    when_present_matches_regex: '\s*KeepAlive On'
```

Additional question: do zero collected command Items and one collected command Item with no `stdout_line` have the same result?

### D — Account-derived Linux files

```yaml
require:
  items: if_present
  match: all
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
    presence: all
```

Additional question: can this check pass with zero matching files? If one file is found and it lacks the `setuid` field, is the result necessarily a pass, failure or something else? What does `presence: all` apply to?

### E — Full result combination (seven named checks)

```yaml
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
```

This is a compact illustrative renaming of the real seven-Test Windows decision tree; original Test IDs are longer. Additional question: how many distinct ways can this Assessment pass? Does the syntax tell you how unknown/error results combine?

## Final independent verdict

Without consulting anyone's intent: Would you endorse this language for (a) security authors, (b) reviewing auditors, (c) scanner implementers? Score each 1–5, name the three most confusing lines, and suggest **one deletion rather than a rename** wherever possible. Do not assume source reconstruction proves scan-result correctness.

**Reviewer safeguard:** This is a deliberately truncated packet, not complete runnable YAML. Excerpts alone may not specify missing/error handling. Mark genuinely unanswerable questions as 'undetermined' rather than extrapolating defaults. The independent reviewer should submit answers *before* seeing the source-grounded interpretation or any prior project discussion.
