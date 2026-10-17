# Auditor preview — Linux must prevent files with the setuid and setgid bit set from being executed on file systems that contain user home directories.

**Machine-generated research explanation from complete parsed YAML.** No live result, new normative policy or scanner-equivalence proof.

**Assessment ID:** `ng.shared.home-is-mounted-with-the-nosuid-option` · **Checks:** 1 · **Evaluate leaves:** 1

[Revised full YAML](../linux-home.revised.research.yaml) · [Original source YAML](../../canonical-operators/linux-home.canonical.research.yaml)

## What is observed?

No separately named source; checks use their native inspectors.


## What must exist and match?

### /home is mounted with the nosuid option.

**Check ID:** `home-mounted-nosuid-option-test` · **Inspector:** `linux.partition`

- **Root Item existence:** `at_least_one`
- **Matching root Items:** `all`
**Original where (not reconstructed):**

~~~yaml
mount_point:
  matches_regex: .*\/home
~~~


**Explicit field, record and State scopes:**

- No additional field-presence/record/group policy is explicitly displayed.

**Full requirement subtree (candidate wording):**

~~~yaml
items: at_least_one
matching_items: all
mount_options:
  at_least_one_value_equals: nosuid
~~~


## How could the Assessment pass?

The structural AND/OR tree below is read from parsed YAML. It is not procedural IF/ELSE, and no actual outcome is calculated.

- `home-mounted-nosuid-option-test` — /home is mounted with the nosuid option.

**Evaluate references:** 1 occurrences of 1 named checks, all accounted for.

## What remains unverified?

- **No system evidence** was collected or evaluated.
- Missing field, missing root Item, read error and incomplete collection are different.
- Repeated field values, nested WMI records and root Items have separate quantifiers.
- Field-presence and matching-label aliases are research-only; runtime equivalence remains open.
- OVAL AND(False,Error) can be False, while OR(True,Error) can be True.
- For command flags, dependent sources, typing and evidence rules, inspect the complete YAML.

[Generic six-state result ledger](SEMANTIC-BOUNDARY-LEDGER.md).
