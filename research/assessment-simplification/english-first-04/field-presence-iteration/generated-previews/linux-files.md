# Auditor preview — Linux local initialization files must have mode 0740 or less permissive.

**Machine-generated research explanation from complete parsed YAML.** No live result, new normative policy or scanner-equivalence proof.

**Assessment ID:** `ng.shared.linux-local-initialization-files-must-have-mode-0740-or-less-permissive` · **Checks:** 2 · **Evaluate leaves:** 2

[Revised full YAML](../linux-files.revised.research.yaml) · [Original source YAML](../../canonical-operators/linux-files.canonical.research.yaml)

## What is observed?

### Named source `users-username-object`

**Inspector:** `unix.password`
**Original selector:**

~~~yaml
username:
  matches_regex: '[\w]+'
~~~

### Named source `only-non-system-users-uid-999-home-dirs-excluding-root-object`

**Inspector:** `unix.password`
**Named Set difference:**

~~~yaml
- from: users-username-object
  exclude_if:
  - user_id:
      less_than: 1000
  - home_dir:
      is: /
~~~

### Named source `only-root-users-uid-0-home-dirs-excluding-root-directory-object`

**Inspector:** `unix.password`
**Named Set difference:**

~~~yaml
- from: users-username-object
  exclude_if:
  - user_id:
      greater_than: 0
  - home_dir:
      is: /
~~~


## What must exist and match?

### Local initialization files for non-system users have mode 0740 or less permissive.

**Check ID:** `local-initialization-files-non-system-users-have-mode-0740-or-test` · **Inspector:** `unix.file`

- **Root Item existence:** `if_present`
- **Matching root Items:** `all`
**Original gather (not reconstructed):**

~~~yaml
description: local initialization files of non-system users.
union:
- from:
    inspect: unix.file
    description: local initialization files of non-system users.
    where:
      directory:
        from: user.home_dir
      name:
        matches_regex: ^\.[^\s\.]+
    filesystem: all
    traversal:
      max_depth: 1
      recurse: symlinks
    for_each_source:
      item: user
      in: only-non-system-users-uid-999-home-dirs-excluding-root-object
  exclude_if:
  - type:
      is: directory
~~~


**Explicit field, record and State scopes:**

- `require`: scalar-field policy `required` declared here; candidate lowering is not runtime proven.
- `require.fields`: AND combines whole child expressions, not value membership.
- `require.fields.and[0].setuid`: inherits `required` scalar-field policy if within its scope.
- `require.fields.and[1].setgid`: inherits `required` scalar-field policy if within its scope.
- `require.fields.and[2].sticky`: inherits `required` scalar-field policy if within its scope.
- `require.fields.and[3].group_write`: inherits `required` scalar-field policy if within its scope.
- `require.fields.and[4].group_execute`: inherits `required` scalar-field policy if within its scope.
- `require.fields.and[5].other_read`: inherits `required` scalar-field policy if within its scope.
- `require.fields.and[6].other_write`: inherits `required` scalar-field policy if within its scope.
- `require.fields.and[7].other_execute`: inherits `required` scalar-field policy if within its scope.

**Full requirement subtree (candidate wording):**

~~~yaml
items: if_present
matching_items: all
field_presence: required
fields:
  and:
  - setuid:
      equals: false
  - setgid:
      equals: false
  - sticky:
      equals: false
  - group_write:
      equals: false
  - group_execute:
      equals: false
  - other_read:
      equals: false
  - other_write:
      equals: false
  - other_execute:
      equals: false
~~~

### Local initialization files for root have mode 0740 or less permissive.

**Check ID:** `local-initialization-files-root-have-mode-0740-or-less-permissive-test` · **Inspector:** `unix.file`

- **Root Item existence:** `at_least_one`
- **Matching root Items:** `all`
**Original gather (not reconstructed):**

~~~yaml
description: local initialization files of root user.
union:
- from:
    inspect: unix.file
    description: local initialization files of root user.
    where:
      directory:
        from: user.home_dir
      name:
        matches_regex: ^\.[^\s\.]+
    filesystem: all
    traversal:
      max_depth: 1
      recurse: symlinks
    for_each_source:
      item: user
      in: only-root-users-uid-0-home-dirs-excluding-root-directory-object
  exclude_if:
  - type:
      is: directory
~~~


**Explicit field, record and State scopes:**

- `require`: scalar-field policy `required` declared here; candidate lowering is not runtime proven.
- `require.fields`: AND combines whole child expressions, not value membership.
- `require.fields.and[0].setuid`: inherits `required` scalar-field policy if within its scope.
- `require.fields.and[1].setgid`: inherits `required` scalar-field policy if within its scope.
- `require.fields.and[2].sticky`: inherits `required` scalar-field policy if within its scope.
- `require.fields.and[3].group_write`: inherits `required` scalar-field policy if within its scope.
- `require.fields.and[4].group_execute`: inherits `required` scalar-field policy if within its scope.
- `require.fields.and[5].other_read`: inherits `required` scalar-field policy if within its scope.
- `require.fields.and[6].other_write`: inherits `required` scalar-field policy if within its scope.
- `require.fields.and[7].other_execute`: inherits `required` scalar-field policy if within its scope.

**Full requirement subtree (candidate wording):**

~~~yaml
items: at_least_one
matching_items: all
field_presence: required
fields:
  and:
  - setuid:
      equals: false
  - setgid:
      equals: false
  - sticky:
      equals: false
  - group_write:
      equals: false
  - group_execute:
      equals: false
  - other_read:
      equals: false
  - other_write:
      equals: false
  - other_execute:
      equals: false
~~~


## How could the Assessment pass?

The structural AND/OR tree below is read from parsed YAML. It is not procedural IF/ELSE, and no actual outcome is calculated.

- **ALL of these child checks (AND)**:
  - `local-initialization-files-non-system-users-have-mode-0740-or-test` — Local initialization files for non-system users have mode 0740 or less permissive.
  - `local-initialization-files-root-have-mode-0740-or-less-permissive-test` — Local initialization files for root have mode 0740 or less permissive.

**Evaluate references:** 2 occurrences of 2 named checks, all accounted for.

## What remains unverified?

- **No system evidence** was collected or evaluated.
- Missing field, missing root Item, read error and incomplete collection are different.
- Repeated field values, nested WMI records and root Items have separate quantifiers.
- Field-presence and matching-label aliases are research-only; runtime equivalence remains open.
- OVAL AND(False,Error) can be False, while OR(True,Error) can be True.
- For command flags, dependent sources, typing and evidence rules, inspect the complete YAML.

[Generic six-state result ledger](SEMANTIC-BOUNDARY-LEDGER.md).
