# Proven foreach cases in Ansible-inspired authoring form

> **RESEARCH ONLY — NOT AN ACCEPTED SCAP-NG DESIGN**
>
> These examples reuse the exact production candidates from the foreach v1
> semantic proof. They exist to compare three representations of the same
> requirement:
>
> 1. faithful OVAL/NG dependency graph;
> 2. proven narrow NG `for_each` modernization; and
> 3. more aggressive Ansible-inspired local authoring.
>
> The third representation is not schema-valid SCAP-NG and is not a conversion
> commitment.

Pinned foreach proof:
`research/assessment-simplification/foreach-07/PRODUCTION-PROOF.md`

Production mapping workflow:
https://github.com/vanderpol/scap-ng/actions/runs/37535587118

## 1–2. RHEL 9 SV-257889 — two home-directory projections

Requirement:

> All RHEL 9 local initialization files must have mode 0740 or less permissive.

The source Rule contains two proven foreach candidates:

- non-system-user home directories -> initialization files;
- root-user home directory -> initialization files.

The faithful graph creates separate password Objects, projects `home_dir`
through local Variables, feeds those Variables into File Object path selectors,
then evaluates the combined File populations.

### Research authoring sketch

```yaml
check:
  all:
    - for_each:
        user:
          password:
            username:
              matches: '[\\w]+'
            exclude:
              - user_id: {less_than: 1000}
              - home_dir: /
      file:
        directory: user.home_dir
        name:
          matches: '^\\.[^\\s\\.]+'
        recurse:
          depth: 1
          symlinks: follow
        exclude:
          type: directory
      expect:
        exists: any
        all:
          mode: no_more_permissive_than_0740

    - for_each:
        user:
          password:
            username:
              matches: '[\\w]+'
            exclude:
              - user_id: {greater_than: 0}
              - home_dir: /
      file:
        directory: user.home_dir
        name:
          matches: '^\\.[^\\s\\.]+'
        recurse:
          depth: 1
          symlinks: follow
        exclude:
          type: directory
      expect:
        exists: one_or_more
        all:
          mode: no_more_permissive_than_0740
```

### Required semantic lowering

The shorthand must retain:

- the original password Set/filter semantics;
- `home_dir` projection from complete source Items;
- ObjectComponent zero-Item/missing-field error behavior;
- one combined target File population per source account class;
- the source `any_exist` versus `at_least_one_exists` distinction;
- Test `check=all`;
- the original permission-State meaning, not merely an octal string shortcut;
- source Item/value provenance.

It must **not** become one Test verdict per user.

## 3. RHEL 9 SV-258105 — shadow-derived usernames into password Items

Requirement:

> RHEL 9 passwords must have a 24 hours minimum password lifetime restriction
> in /etc/shadow.

One proven foreach candidate is:

```
textfilecontent54(/etc/shadow)
  -> captured username (subexpression)
  -> local Variable
  -> unix.password username selector
  -> filtered password Item population
  -> none_exist Test
```

The Rule also has a second independent local Variable that extracts the
`nobody` UID from `/etc/passwd`. That Variable is **not** part of the proven
foreach rewrite and must remain semantically visible.

### Research authoring sketch

```yaml
check:
  let:
    nobody_uid:
      from:
        text:
          path: /etc/passwd
          pattern: '^nobody:[^:]*:([0-9]+):'
        capture: 1
        datatype: int

  all:
    - text:
        path: /etc/shadow
        pattern: '^root:[^:]*:[^:]*:0*:'
      expect:
        exists: none

    - for_each:
        shadow_entry:
          text:
            path: /etc/shadow
            pattern: '^([^:]*):[^:]*:[^:]*:0*:'
      password:
        username: shadow_entry.capture[1]
        exclude:
          - user_id: {less_than: 1000}
          - user_id: nobody_uid
      expect:
        exists: none
```

### Why this example matters

This is more revealing than a home-directory loop. The source Item is a text
match, the projected field is a capture/subexpression, and the target is a
typed password/account collector.

The authoring layer can still read naturally, but the compiler must preserve:

- all matching captures, not just the first;
- string datatype on the projected username;
- the target equality / at-least-one Variable-match semantics;
- the independent `nobody_uid` value and its own status/cardinality;
- target password filters;
- `none_exist` on the final combined population.

## 4. RHEL 9 SV-257890 — interactive-user home directories

Requirement:

> All RHEL 9 local interactive user home directories must have mode 0750 or
> less permissive.

The proven graph projects `home_dir` from filtered password Items into the
File Object path selector.

### Research authoring sketch

```yaml
check:
  for_each:
    user:
      password:
        username:
          matches: '.*'
        exclude:
          - login_shell: {matches: '^.*nologin.*$'}
          - user_id: {less_than: 1000}
          - user_id: 65534

  file:
    path: user.home_dir
    self: true

  expect:
    exists: any
    all:
      mode: no_more_permissive_than_0750
```

`self: true` is only placeholder research vocabulary for the source File
Object's nil filename semantics. The experiment should decide whether a clearer
portable term exists.

Again, this is collection expansion into one File population, not an
independent pass/fail result for each user.

## 5. Solaris 11 x86 SV-216074 — .Xauthority under account home directories

Requirement:

> All .Xauthority files must have mode 0600 or less permissive.

The proven production candidate is:

```
unix.password Object
  -> home_dir ObjectComponent
  -> local Variable
  -> unix.file path selector, var_check=at least one
  -> one combined File population
  -> any_exist / all File Test
```

### Research authoring sketch

```yaml
check:
  for_each:
    user:
      password:
        username:
          matches: '.*'

  file:
    directory: user.home_dir
    name: .Xauthority

  expect:
    exists: any
    all:
      mode: no_more_permissive_than_0600
```

The pinned source was re-extracted after mapping the candidate to SV-216074.
It confirms:

- source Password Object selector: `username pattern_match ".*"`;
- projected field: `home_dir`;
- target File selector: projected path + literal filename `.Xauthority`;
- Test: `check_existence=any_exist`, `check=all`;
- State: `suid=false`, `sgid=false`, `uexec=false`, and all group/other
  read/write/execute bits false.

Therefore `mode: no_more_permissive_than_0600` is acceptable in this
research sketch only if the compiler expands it to those exact source
permission predicates rather than inventing a different numeric-mode contract.

Source-evidence workflow:
https://github.com/vanderpol/scap-ng/actions/runs/37536228383

## What these five cases suggest

All five proven v1 bindings become easier to read when the source collection,
binding, target collection, and expectation are kept in one local block.

That does **not** imply the underlying semantic concepts disappear. The
compiler/IR still needs:

- source Object identity and collection status;
- typed projected field/value sets;
- Variable-equivalent cardinality/status where required for migration;
- target Object aggregation;
- Test existence and item quantifiers;
- State/entity comparison semantics;
- provenance and evidence boundaries.

The research question is therefore not whether these concepts exist. It is
whether the normal author must name and cross-reference every one of them.

## Negative foreach cases remain important

The Ansible-inspired experiment must also render the foreach v1 rejected cases,
especially:

- one projected value feeding multiple target Objects (fan-out);
- helper/intermediate target Objects;
- `var_check=all`;
- derived `concat` / Cartesian-product expressions;
- several independent multi-valued sources.

If the simple language becomes difficult precisely at those boundaries, that is
useful evidence about the smallest practical authoring standard rather than a
reason to hide the complexity.
