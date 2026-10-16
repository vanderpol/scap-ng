# English-first authoring consistency — working draft

**Research only, October 16, 2026. NOT approved 0.4 syntax or a second executable language.**
Tracking: [#235](https://github.com/vanderpol/scap-ng/issues/235) (lossless research), [#227](https://github.com/vanderpol/scap-ng/issues/227) (terms), [#229](https://github.com/vanderpol/scap-ng/issues/229) (six-state semantics).

## The authoring contract we are testing

**Readable is not sufficient: someone should be able to write a new Assessment without reverse-engineering an existing one.** A keyword should have one meaning, one place, and one canonical spelling.

| Meaning | Proposed single placement | What not to do |
| --- | --- | --- |
| What is being tested | `check` | Do not imply Test semantics from the prose title |
| Native data capability | `inspect` inside each check or named source | Do not duplicate `inspect` inside the same check's `gather` |
| Select system entities | `where` alongside `inspect` | Do not invent a selector for built-in Objectless collectors |
| Configure collection | `collect`, `filesystem`, `traversal` alongside `inspect` | Do not wrap ordinary collection in `gather.collect` |
| Refer to a named reusable source | `from: source-id` in a check; `from: source-id` inside a Set operand | Do not use a parallel `gather.source` convention |
| Construct a complex collection | `gather` alongside `inspect`, with direct `union`, `difference`, `intersection`, or `complement` | Do not nest `combine` before the operator |
| Expand a source into dependent items | `for_each_source` within the collection operand | Do not confuse acquisition iteration with requirement quantification |
| Evaluate what was collected | `require`, including explicit item and field cardinality | Do not silently turn some/all/only-one into one generic `match` |
| Combine named checks | `evaluate` with explicit `all_of` / `any_of` | Do not rewrite whole-State alternatives into per-record membership |

These are **placement conventions under investigation**, not a general authorization to omit source cardinality, collection flags, record boundaries, or result-status rules. Only capability-specific shorthands supported by an exact lowering contract may hide redundant detail.

## Same pattern, three levels of complexity

**1. Built-in system-wide collector** — no fabricated Object:

```yaml
check: "'Minimum password length' is set to at least '14' characters"
inspect: windows.passwordpolicy
require:
  min_passwd_len:
    at_least: 14
```

**2. Ordinary collected data** — selection/collection options appear beside the native inspector:

```yaml
check: All forward lookup zones are DNSSEC signed
inspect: independent.shellcommand
collect:
  shell: powershell
  command:
    variable: command-get-issigned-setting-each-forward-lookup-zone-variable
  error_if_exit_status_not_0: false
  error_if_stderr_exists: false
require:
  at_least_one_item_exists: true
  every_item_must_match:
    stdout_line:
      exactly_one_is: 'True'
```

The command Variable and its full original dependency graph must still be defined elsewhere in the complete Assessment. This excerpt alone is **not authorable or executable**.

**3. Named, derived collection** — explicit definition and reference, with the operand boundary visible:

```yaml
sources:
  users-username-object:
    inspect: unix.password
    where:
      username:
        matches_regex: '[\w]+'
  non-system-users:
    inspect: unix.password
    difference:
      - from: users-username-object
        exclude_if:
          - user_id:
              require: at_least_one_exists_and_all_match
              less_than: 1000
          - home_dir:
              require: at_least_one_exists_and_all_match
              equals: /

checks:
  non-system-user-initialization-files:
    check: Inspect local initialization file permissions
    inspect: unix.file
    gather:
      union:
        - from:
            inspect: unix.file
            for_each_source:
              item: user
              in: non-system-users
            where:
              directory:
                from: user.home_dir
              name:
                matches_regex: '^\.[^\s\.]+'
            filesystem: all
            traversal:
              max_depth: 1
              recurse: symlinks
          exclude_if:
            - type:
                is: directory
    require:
      items_may_be_absent: true
      every_item_must_match:
        # Eight source field predicates required; omitted in this illustration.
        setuid:
          is: false
```

The final snippet **illustrates placement and reference resolution**, not an exact complete source Assessment: it renames a source and omits seven predicates and other checks. The [source-backed full Linux assessment](FOUR-REAL-WORLD-RESEARCH-EXAMPLES.md#1-linux--account-derived-file-permissions) retains exact IDs and requirements. A parser must look up `non-system-users`; it cannot infer the filter from the name.

## Machine-verifiable acceptance gates

- **Round trip:** every admitted full Assessment must satisfy `expand(compact(to_human(source))) == to_human(source)` and `to_native(expand(...)) == source`. Preserve operand order, one-operand Sets, all filters, collection flags, Variables, named-Test graph, and metadata.
- **Reject ambiguity:** undefined named Set sources, simultaneous `from` and `gather`, competing Set operators, empty operands, and redundant `combine` wrappers must fail closed.
- **No false semantic proof:** structural inversion does **not** prove OVAL six-state runtime/evidence equivalence. The unresolved `none_exist` plus attached State edge case remains open.
- **Human authoring test:** supply novice content authors with a capability table and only this grammar; ask them to construct built-in, scalar, named-source, Set/foreach, and conditional/record assessments. Track whether they know the location of each property without copying an example.
- **Automated style/lint:** once the grammar stabilizes, validate canonical placement and source-reference resolution at compile time. JSON Schema can constrain structure; cross-references and semantic preservation need compiler tests.

**Evidence boundary:** The previously reported **871/872** full-Assessment structural reconstructions apply to the earlier English-first research. The direct-Set presentation change has been committed to [the research compact-layout script](../../../tools/research_english_first_04_compact_layout.py) with new guard cases. Do **not** quote 871/872 as newly rerun proof for that change until the pinned six-STIG workflow finishes successfully. Nothing here changes released 0.3 content, the pinned 0.4 review artifacts, or the scanner specification.

## Next decisions

1. Decide whether a one-operand union is retained as a direct unary Set operation in authoring or removed only when formally proven result/evidence equivalent. Source-structure inversion currently retains it.
2. Resolve exactly where to surface source definitions in a user-facing example; never leave a named `for_each_source.in` unexplained.
3. Prove full source-reference validation (including iteration inputs and source graph cycles), then conditional, record and Variable authorability; do not expand into a second fallback dialect.
