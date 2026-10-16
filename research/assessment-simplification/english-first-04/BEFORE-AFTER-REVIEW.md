# SCAP-NG 0.4 — before/after authoring review

**For design feedback · 16 October 2026 · Pre-alpha experiment, NOT approved 0.4 syntax**

**The decision question:** *Is the proposed English-first form more consistent and easier to write from scratch than the current 0.4 preview, without compromising source meaning?*

Start with the two Linux and Windows samples below; then examine DNS and Apache. **The small extracts on this page illustrate the difference; use the links to review complete Assessments with every Test, source, Variable and evaluation tree.** Both versions are normal GitHub files, accessible on a restricted github.com network without downloading Actions artifacts.

**How these pairs were produced.** The **before** files are the unchanged, pinned 0.4 r3 source examples. The **after** files are the complete research-only compact English-first representations generated from those same Assessments. The converter reconstructed the original complete source dictionaries exactly for all four in the passing six-STIG run [38932589417](https://github.com/vanderpol/scap-ng/actions/runs/38932589417) (871/872 total). That is **source-structure identity, not proof of SCAP 1.4 runtime, collection evidence, or six-state scanner equivalence**.

| Real assessment | Before: complete current 0.4 | After: complete experimental English-first |
| --- | --- | --- |
| **RHEL 9 — SV-257889** local initialization-file permissions | [View 0.4 source](https://github.com/vanderpol/scap-ng-editor-sample-data/blob/99cbceae8d594c44cb509df95975ac1676a2b44a/focused-fixtures/source-backed/authoring/shared/assessments/linux/other/initialization-files-0740-less-permissive.assessment.yaml) | [View full English-first version](comparisons/linux-initialization.research.yaml) |
| **Windows 11 — SV-253495** Remote Desktop deny-rights | [View 0.4 source](https://github.com/vanderpol/scap-ng-editor-sample-data/blob/99cbceae8d594c44cb509df95975ac1676a2b44a/focused-fixtures/source-backed/authoring/ms_windows_11/assessments/automated/SV-253495.automated.yaml) | [View full English-first version](comparisons/win11-role-rights.research.yaml) |
| **Windows Server DNS — SV-259345** zone signing | [View 0.4 source](https://github.com/vanderpol/scap-ng-editor-sample-data/blob/99cbceae8d594c44cb509df95975ac1676a2b44a/focused-fixtures/source-backed/authoring/ms_windows_server_dns/assessments/automated/SV-259345.automated.yaml) | [View full English-first version](comparisons/dns-zone-signing.research.yaml) |
| **Apache 2.4 UNIX — SV-214228** loaded config directives | [View 0.4 source](https://github.com/vanderpol/scap-ng-editor-sample-data/blob/99cbceae8d594c44cb509df95975ac1676a2b44a/focused-fixtures/source-backed/authoring/apache_server_2-4_unix_server/assessments/automated/SV-214228.automated.yaml) | [View full English-first version](comparisons/apache-keepalive.research.yaml) |

## 1. RHEL 9 — account-derived file inspections

*Hard question: where does the account collection come from, and could you define it yourself?* The source first collects accounts, subtracts excluded accounts, then inspects each user's home directory. **Neither version infers filtering rules from an ID.**

**Before — original 0.4 source excerpt**

~~~yaml
shared_objects:
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
~~~

**After — generated English-first excerpt, same required filters**

~~~yaml
sources:
  only-non-system-users-uid-999-home-dirs-excluding-root-object:
    inspect: unix.password
    difference:
      - from: users-username-object
        exclude_if:
          - user_id:
              less_than: 1000
          - home_dir:
              is: /
~~~

The complete after file still defines `users-username-object`; shows a one-operand `union` for per-user `unix.file` discovery, its `for_each_source.in` reference, filesystem traversal and `exclude_if` filter; and retains the two distinct Item-count requirements and all eight file-permission conditions. **Do not judge this from the compact snippet alone.**

**Authoring question:** Is `sources` + `difference` + `for_each_source` predictable, or should collections have a different placement/name?

## 2. Windows 11 — record-scoped, role-dependent rights

*Hard question: do the rules express separate Items, States and WMI records without conflating their matching requirements?*

**Before — original 0.4 Guest user-right Test excerpt**

~~~yaml
deny-log-on-through-remote-desktop-services-guests-test:
  test_title: Deny log on through Remote Desktop Services - Guests
  capability: windows.userright
  object: windows-userright-object
  states:
    - trustee_name:
        require: at_least_one_exists_and_all_match
        case_insensitive_equals: Guests
  reported_elements: all
  collected_items_require: at_least_one_exists_and_some_match
~~~

**After — generated English-first Guest Test excerpt**

~~~yaml
deny-log-on-through-remote-desktop-services-guests-test:
  check: Deny log on through Remote Desktop Services - Guests
  inspect: windows.userright
  require:
    at_least_one_item_exists: true
    at_least_one_item_matches:
      trustee_name:
        equals_ignoring_case: Guests
  report_elements: all
  from: windows-userright-object
~~~

The complete pair includes all **seven named Tests**, their WMI `DomainRole` record alternatives and the **three branches** of the final evaluation. Joining the WMI alternatives into a simple `domainrole in [1, 3]` check could **change semantics**, so the after retains two whole-State alternatives.

**Authoring question:** Is the separate `from` reference discoverable? Would you know when to write `every_item_must_match` versus `at_least_one_item_matches`?

## 3. Windows Server DNS — derived command inputs

*Hard question: do you understand where the generated PowerShell commands come from?*

**Before — original 0.4 Test acquisition excerpt**

~~~yaml
capability: independent.shellcommand
object:
  capability: independent.shellcommand
  object_title: The 'IsSigned' setting for each forward lookup zone
  collect:
    shell: powershell
    command:
      variable: command-get-issigned-setting-each-forward-lookup-zone-variable
    error_if_exit_status_not_0: false
    error_if_stderr_exists: false
~~~

**After — generated English-first Test acquisition excerpt**

~~~yaml
inspect: independent.shellcommand
collect:
  shell: powershell
  command:
    variable: command-get-issigned-setting-each-forward-lookup-zone-variable
  error_if_exit_status_not_0: false
  error_if_stderr_exists: false
~~~

The complete before and after versions both retain **three command-building Variables**, the shared forward-zone collection, **five Tests**, and their OR/AND evaluation tree. A reader must still trace the Variable expression referencing the zone collection's `stdout_line`.

**Authoring question:** Is moving `collect` next to `inspect` an improvement if it leaves the Variable graph difficult to author?

## 4. Apache UNIX — required and optional configuration

*Hard question: can you trace the discovery of loaded configuration files and understand required versus optional directive checks?*

**Before — original 0.4 optional KeepAlive State**

~~~yaml
states:
  - stdout_line:
      require: may_be_absent_and_all_match
      matches_regex: \s*KeepAlive On
reported_elements: all
collected_items_require: at_least_one_exists_and_all_match
~~~

**After — generated English-first optional KeepAlive requirement**

~~~yaml
require:
  at_least_one_item_exists: true
  every_item_must_match:
    stdout_line:
      when_present_matches_regex: \s*KeepAlive On
report_elements: all
~~~

Both complete versions retain **18 local Variables** and four Tests. The reference audit reports an **Apache prerequisite chain of up to 10 edges**—preserving the graph has not made its authoring easy.

**Authoring question:** Does `when_present_matches_regex` express the rule clearly, and how would you prefer to reuse the deep configuration-discovery graph?

## The feedback most useful for the 0.4 decision

Please judge **the complete before/after files**, not just line counts. In particular:

1. **Readability:** which version makes each check's intention clearer?
2. **Consistency:** could you predict where to put `inspect`, `where`, `collect`, `from`, `gather`, `difference` and `union`?
3. **Authorability:** if handed a new DISA check, which version could you write without copying an existing assessment?
4. **Missing clarity:** what references, source graph steps or quantifiers still need an explanatory paragraph?
5. **Decision:** adopt the complete approach, adopt selected improvements to 0.4, or keep researching?

**Current recommendation: keep researching, not adopt yet.** Complete 0.4 source-structure reversibility is promising, but direct authorability, user comprehension and independent SCAP 1.4 result/evidence equivalence remain unproven. Track findings under [#235](https://github.com/vanderpol/scap-ng/issues/235). Supporting [technical census](reports/README.md) is evidence, not the decision memo.
