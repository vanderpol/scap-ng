# 02 · RHEL 9 account-derived initialization files (complex) — complete before and after

**Review-only comparison. Neither version represents independently validated SCAP 1.4 scanner execution/evidence parity.**

[Back to all five complete examples](BEFORE-AFTER-REVIEW.md) · [Original pinned source](https://github.com/vanderpol/scap-ng-editor-sample-data/blob/99cbceae8d594c44cb509df95975ac1676a2b44a/focused-fixtures/source-backed/authoring/shared/assessments/linux/other/initialization-files-0740-less-permissive.assessment.yaml) · [Complete experimental YAML](comparisons/linux-initialization.research.yaml)

## What changed (without changing the underlying check)

- All three named account collections are included, so `for_each_source.in` resolves to a visible definition.
- `shared_objects` becomes `sources`; explicit `set.operator` + `operands` becomes a direct `difference` or `union`, without discarding the original one-operand union.
- The two permission Tests still have different collected-Item existence requirements, and all eight permission predicates remain visible.

**What to assess:** Can you identify the collected system data, source definitions, value/Item requirements and final evaluation without referring to another file?

## Complete assessments — side by side

Both columns include the **complete** original and proposed YAML; no checks, sources, Variables, or evaluation branches have been omitted. The view is intended for a wide desktop browser. If the table is wider than the viewport, scroll horizontally inside the rendered table. Standalone YAML links remain above.

<table>
<thead><tr><th align="left" width="50%">BEFORE — Current 0.4</th><th align="left" width="50%">AFTER — English-first research</th></tr></thead>
<tbody><tr>
<td valign="top" width="50%"><pre><code>assessment:
  id: ng.shared.linux-local-initialization-files-must-have-mode-0740-or-less-permissive
  version: 1
  assessment_title: Linux local initialization files must have mode 0740 or less permissive.
  mode: automated
  class: compliance
  purpose: assessment
  specification:
    id: scap-ng.pre-alpha.assessment
    version: 0.4.0
  tests:
    local-initialization-files-non-system-users-have-mode-0740-or-test:
      test_title: Local initialization files for non-system users have mode 0740 or less permissive.
      capability: unix.file
      object:
        capability: unix.file
        object_title: local initialization files of non-system users.
        set:
          operator: union
          operands:
          - object:
              capability: unix.file
              for_each:
                item: user
                in: only-non-system-users-uid-999-home-dirs-excluding-root-object
              select:
                directory:
                  from: user.home_dir
                name:
                  matches_regex: ^\.[^\s\.]+
              object_title: local initialization files of non-system users.
              filesystem: all
              traversal:
                max_depth: 1
                recurse: symlinks
            filters:
            - exclude:
                type:
                  require: at_least_one_exists_and_all_match
                  equals: directory
      states:
      - and:
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
        state_fields_require: at_least_one_exists_and_all_match
      reported_elements: all
      collected_items_require: may_be_absent_and_all_match
    local-initialization-files-root-have-mode-0740-or-less-permissive-test:
      test_title: Local initialization files for root have mode 0740 or less permissive.
      capability: unix.file
      object:
        capability: unix.file
        object_title: local initialization files of root user.
        set:
          operator: union
          operands:
          - object:
              capability: unix.file
              for_each:
                item: user
                in: only-root-users-uid-0-home-dirs-excluding-root-directory-object
              select:
                directory:
                  from: user.home_dir
                name:
                  matches_regex: ^\.[^\s\.]+
              object_title: local initialization files of root user.
              filesystem: all
              traversal:
                max_depth: 1
                recurse: symlinks
            filters:
            - exclude:
                type:
                  require: at_least_one_exists_and_all_match
                  equals: directory
      states:
      - and:
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
        state_fields_require: at_least_one_exists_and_all_match
      reported_elements: all
      collected_items_require: at_least_one_exists_and_all_match
  evaluate:
    all:
    - test: local-initialization-files-non-system-users-have-mode-0740-or-test
    - test: local-initialization-files-root-have-mode-0740-or-less-permissive-test
  shared_objects:
    users-username-object:
      capability: unix.password
      select:
        username:
          matches_regex: '[\w]+'
      object_title: Users with an username
    only-non-system-users-uid-999-home-dirs-excluding-root-object:
      capability: unix.password
      set:
        operator: difference
        operands:
        - object: users-username-object
          filters:
          - exclude:
              user_id:
                require: at_least_one_exists_and_all_match
                less_than: 1000
          - exclude:
              home_dir:
                require: at_least_one_exists_and_all_match
                equals: /
      object_title: only non-system users (uid&gt;999) home-dirs excluding root directory
    only-root-users-uid-0-home-dirs-excluding-root-directory-object:
      capability: unix.password
      set:
        operator: difference
        operands:
        - object: users-username-object
          filters:
          - exclude:
              user_id:
                require: at_least_one_exists_and_all_match
                greater_than: 0
          - exclude:
              home_dir:
                require: at_least_one_exists_and_all_match
                equals: /
      object_title: only root users (uid=0) home-dirs excluding root directory</code></pre></td>
<td valign="top" width="50%"><pre><code># EXPERIMENT ONLY; reconstructs the pinned Assessment exactly.
# Not normative SCAP-NG v0.4 or independently validated OVAL execution.
metadata:
  id: ng.shared.linux-local-initialization-files-must-have-mode-0740-or-less-permissive
  version: 1
  assessment_title: Linux local initialization files must have mode 0740 or less permissive.
  mode: automated
  class: compliance
  purpose: assessment
  specification:
    id: scap-ng.pre-alpha.assessment
    version: 0.4.0
sources:
  users-username-object:
    inspect: unix.password
    description: Users with an username
    where:
      username:
        matches_regex: '[\w]+'
  only-non-system-users-uid-999-home-dirs-excluding-root-object:
    inspect: unix.password
    description: only non-system users (uid&gt;999) home-dirs excluding root directory
    difference:
    - from: users-username-object
      exclude_if:
      - user_id:
          less_than: 1000
      - home_dir:
          is: /
  only-root-users-uid-0-home-dirs-excluding-root-directory-object:
    inspect: unix.password
    description: only root users (uid=0) home-dirs excluding root directory
    difference:
    - from: users-username-object
      exclude_if:
      - user_id:
          greater_than: 0
      - home_dir:
          is: /
checks:
  local-initialization-files-non-system-users-have-mode-0740-or-test:
    check: Local initialization files for non-system users have mode 0740 or less
      permissive.
    inspect: unix.file
    require:
      items_may_be_absent: true
      every_item_must_match:
        all_of:
        - setuid:
            is: false
        - setgid:
            is: false
        - sticky:
            is: false
        - group_write:
            is: false
        - group_execute:
            is: false
        - other_read:
            is: false
        - other_write:
            is: false
        - other_execute:
            is: false
        all_fields_must_exist: true
    report_elements: all
    gather:
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
  local-initialization-files-root-have-mode-0740-or-less-permissive-test:
    check: Local initialization files for root have mode 0740 or less permissive.
    inspect: unix.file
    require:
      at_least_one_item_exists: true
      every_item_must_match:
        all_of:
        - setuid:
            is: false
        - setgid:
            is: false
        - sticky:
            is: false
        - group_write:
            is: false
        - group_execute:
            is: false
        - other_read:
            is: false
        - other_write:
            is: false
        - other_execute:
            is: false
        all_fields_must_exist: true
    report_elements: all
    gather:
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
evaluate:
  all_of:
  - test: local-initialization-files-non-system-users-have-mode-0740-or-test
  - test: local-initialization-files-root-have-mode-0740-or-less-permissive-test</code></pre></td>
</tr></tbody>
</table>


## Your review

- Which syntax would you prefer when writing this exact check from scratch?
- Are any named sources, collection operations or cardinality requirements still hard to understand?
- Does the new grammar look consistent with the other examples?

**Evidence:** The previous [six-STIG structural research run](https://github.com/vanderpol/scap-ng/actions/runs/38934771985) reconstructed the published complete generated sample; it did not prove live scanner results.
