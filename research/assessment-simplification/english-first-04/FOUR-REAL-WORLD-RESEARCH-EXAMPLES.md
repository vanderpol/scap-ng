# English-first Assessment research — four real complex examples

**October 16, 2026. Research only; NOT SCAP-NG 0.4 syntax, a normative proposal, or a scanner.** The goal is to see whether a security administrator can read source-backed checks without OVAL expertise *while* preserving every source Object, State, Item requirement, Variable and Boolean group.

**[Download the four complete experimental YAML Assessments and verification JSON](https://github.com/vanderpol/scap-ng/actions/runs/38913249970/artifacts/12051575856)** (passing pinned-source CI run). Workflow artifacts include `english-first-04-complete-examples/*.research.yaml` plus the source-comparison report. The translator [source](../../../tools/research_english_first_04_complex.py) reversibly converts each *whole* pinned Assessment back to its unmodified 0.4 preview structure and rejects unsupported mutations. **Structural equality is not a six-state scanner or original OVAL execution proof.** Full files, not the abbreviated excerpts below, are the actual research output.

## 1. Linux — account-derived file permissions

Real source: [RHEL9 SV-257889 shared Assessment](https://github.com/vanderpol/scap-ng-editor-sample-data/blob/99cbceae8d594c44cb509df95975ac1676a2b44a/focused-fixtures/source-backed/authoring/shared/assessments/linux/other/initialization-files-0740-less-permissive.assessment.yaml). **Two complete Tests, three shared collections**. The original uses password-account Sets, filters, `for_each` from users to files, filesystem/traversal controls, eight permission predicates, and separate optional/nonoptional file populations.

```yaml
# Readable excerpt — original collection and requirement structure preserved
check: Local initialization files for non-system users have mode 0740 or less permissive.
inspect: unix.file
gather:
  inspect: unix.file
  combine:
    union:
      - from:
          inspect: unix.file
          for_each_source:
            item: user
            in: only-non-system-users-uid-999-home-dirs-excluding-root-object
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
  every_collected_item:
    all_of:
      - setuid:
          is: false
      - setgid:
          is: false
      # six additional source predicates in the complete YAML
    all_fields_must_exist: true
```

**What succeeds:** source account→file projection, Set union/filter and eight-field check are representable in one reversible YAML tree; the root-user Test separately requires at least one file.

**Still awkward:** `for_each_source` and `every_collected_item` are different operations, and the shared Set/difference/filters remain verbose; no scanner has proved actual traversal behavior.

## 2. Windows 11 — Remote Desktop rights depend on domain role

Real source: [Windows 11 SV-253495](https://github.com/vanderpol/scap-ng-editor-sample-data/blob/99cbceae8d594c44cb509df95975ac1676a2b44a/focused-fixtures/source-backed/authoring/ms_windows_11/assessments/automated/SV-253495.automated.yaml). **Seven real Tests and two shared collections.** WMI `DomainRole` records distinguish standalone from non-DC domain-joined systems; user-right assignment checks require *some* matching collected Items; the Assessment uses an OR of three alternatives.

```yaml
# Readable excerpt — WMI record Test, plus the separate user-right Test
sources:
  windows-wmi57-object:
    inspect: windows.wmi.query
    collect:
      namespace: root\cimv2
      query: SELECT DomainRole FROM win32_computersystem
checks:
  system-non-dc-domain-joined-windows-server-or-workstation-test:
    check: The system is a non-DC domain-joined Windows server or workstation
    inspect: windows.wmi.query
    gather:
      source: windows-wmi57-object
    require:
      at_least_one_item_exists: true
      every_collected_item:
        any_of:
          - result:
              at_least_one_record_exists: true
              every_record:
                domainrole:
                  is: '1'
          - result:
              at_least_one_record_exists: true
              every_record:
                domainrole:
                  is: '3'
  deny-log-on-through-remote-desktop-services-guests-test:
    check: Deny log on through Remote Desktop Services - Guests
    inspect: windows.userright
    gather:
      source: windows-userright-object
    require:
      at_least_one_item_exists: true
      some_collected_item:
        trustee_name:
          equals_ignoring_case: Guests
```

**What succeeds:** native WMI collection, explicit record/field scope, Windows user-right selectors, all seven Test definitions and their exact named-Test Boolean composition reconstruct without collapsing alternatives.

**Critical counterexample:** two WMI records holding `domainrole=1` and `domainrole=3` do **not** behave like a single `domainrole in ['1','3']` predicate under the original OR-of-whole-States. The research suite rejects that tempting but lossy rewrite. The phrase `some_collected_item` also deserves another author readability round.

## 3. Windows Server DNS — dynamic zone names and three passing alternatives

Real source: [DNS SV-259345](https://github.com/vanderpol/scap-ng-editor-sample-data/blob/99cbceae8d594c44cb509df95975ac1676a2b44a/focused-fixtures/source-backed/authoring/ms_windows_server_dns/assessments/automated/SV-259345.automated.yaml). **Five Tests, three local command-building Variables, one shared zone collection**.

```yaml
# Excerpt: an actual command populated from the source Variable graph
check: All forward lookup zones are DNSSEC signed
inspect: independent.shellcommand
gather:
  inspect: independent.shellcommand
  collect:
    shell: powershell
    command:
      variable: command-get-issigned-setting-each-forward-lookup-zone-variable
    error_if_exit_status_not_0: false
    error_if_stderr_exists: false
require:
  at_least_one_item_exists: true
  every_collected_item:
    stdout_line:
      exactly_one_is: 'True'

# Assessment evaluation (other four named checks defined in full YAML):
evaluate:
  any_of:
    - test: dns-server-caching-only-there-no-forward-or-reverse-lookup-test
    - test: all-forward-lookup-zones-if-any-integrated-active-directory-test
    - all_of:
        - test: all-forward-lookup-zones-dnssec-signed-test
        - test: all-forward-lookup-zones-have-dns-key-signature-validity-periods-test
        - test: all-forward-lookup-zones-have-dns-key-signature-validity-periods-2-test
```

**What succeeds:** all five Tests, full dynamic command Variables and OR/AND graph reconstruct exactly. Numeric signature validity checks retain both 48-hour minimum and 168-hour maximum. An absence-only stdout Test retains its otherwise redundant source comparator rather than silently deleting it.

**Still awkward:** the command `variable` reference is readable only after opening the `metadata.variables` expression graph in the full file. We have *not* proved that replacing it with a simpler per-zone `for_each` would preserve execution, multiplicity, or result status.

## 4. Apache UNIX — required vs optional settings across included files

Real source: [Apache SV-214228](https://github.com/vanderpol/scap-ng-editor-sample-data/blob/99cbceae8d594c44cb509df95975ac1676a2b44a/focused-fixtures/source-backed/authoring/apache_server_2-4_unix_server/assessments/automated/SV-214228.automated.yaml). **Four Tests and 18 local Variables**, including installation discovery and `Include`/`IncludeOptional` configuration processing.

```yaml
# Excerpt of the optional KeepAlive Test
check: If the KeepAlive directive is defined in other loaded configuration files, verify it is configured to On
inspect: independent.shellcommand
gather:
  inspect: independent.shellcommand
  collect:
    shell: bash
    command:
      variable: shell-command-check-keepalive-in-all-loaded-conf-files-variable
    pattern: .+
    error_if_exit_status_not_0: false
    error_if_stderr_exists: false
require:
  at_least_one_item_exists: true
  every_collected_item:
    stdout_line:
      when_present_matches_regex: '\s*KeepAlive On'

# The full file retains two required and two optional/config-context Tests,
# plus the entire source discovery/variable graph and all_of evaluation.
```

**What succeeds:** exact presence requirements for required versus optional config fields are kept distinct; shell parameters, stderr/exit settings, regex capture, four Tests, 18 Variables, shared discovery and `all_of` reconstruct.

**Still awkward:** the dependency graph is not yet expressed in natural language; shortening it to `load Apache config` would lose important discovery semantics and provenance without further proof.

## What this evidence does—and does not—say

| Gate | Current evidence |
| --- | --- |
| Actual source reconstruction | **PASS** — all four *complete* Assessment dictionaries, including Variables, Objects, State/Item requirements and named-Test evaluation trees, round-trip exactly |
| Negative source constraints | **PASS** — unsupported Set operators, missing Item requirements and unrecognized predicates rejected |
| Exact original OVAL runtime outcomes | **NOT PROVEN** — no independent SCAP-NG 0.4 scanner or six-state system-evidence parity |
| Human comprehension | **NOT YET TESTED** — especially `some_collected_item`, `any_of` whole-State scope, and source-derived Variables |
| Official v0.4 grammar / new signed bundle | **NOT CHANGED** — existing review releases remain immutable |

**Research judgment:** this goes significantly farther than one-line examples: a *single reversible research format* now represents four genuinely complex Assessment graphs, but its readability is uneven. The next design task is to make account/file and dynamic command acquisition human-readable without silently erasing Items, statuses, Variables, or evidence. Do not ask reviewers to approve this grammar yet.

Tracking: [#235 research](https://github.com/vanderpol/scap-ng/issues/235) · [#229 semantic conformance](https://github.com/vanderpol/scap-ng/issues/229) · [Source compiler and full YAML artifact workflow](https://github.com/vanderpol/scap-ng/actions/workflows/research-english-first-04.yml).
