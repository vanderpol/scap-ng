# English-first Assessment research — four real complex examples

**October 16, 2026. Research only; NOT SCAP-NG 0.4 syntax, a normative proposal, or a scanner.** The goal is to see whether a security administrator can read source-backed checks without OVAL expertise *while* preserving every source Object, State, Item requirement, Variable and Boolean group.

**For design review, start with the [complete before-and-after comparison pages](BEFORE-AFTER-REVIEW.md): all five examples display the entire original and proposed YAML directly in Markdown.** The abbreviated excerpts below are retained only as technical research notes.

**[Download the four complete experimental YAML Assessments and verification JSON](https://github.com/vanderpol/scap-ng/actions/runs/38913249970/artifacts/12051575856)** (passing pinned-source CI run). Workflow artifacts include `english-first-04-complete-examples/*.research.yaml` plus the source-comparison report. The translator [source](../../../tools/research_english_first_04_complex.py) reversibly converts each *whole* pinned Assessment back to its unmodified 0.4 preview structure and rejects unsupported mutations. **Structural equality is not a six-state scanner or original OVAL execution proof.** Full files, not the abbreviated excerpts below, are the actual research output.

**Working-draft authoring convention (not approved 0.4 syntax):** `inspect` names a capability and implicitly gathers ordinary data. `where` and `collect` sit beside it when needed. A check-level `from` references a named reusable source. Reserve `gather` for complex collection/Set composition, always alongside `inspect` rather than nested inside it. `union` already means combining operands; no additional `combine` wrapper is needed in the proposed spelling. **The shortened union excerpt below has not been verified by the converter.** The linked complete YAML remains the source-exact research artifact. Other compact layouts follow the [tested compact-layout experiment](../../../tools/research_english_first_04_compact_layout.py).

## Start with two short, readable source-backed checks

These are **research Test excerpts** (not independently runnable complete Assessments), included so a first-time reader can understand the intended order before examining the much larger four Assessments below. The pinned-source reconstructions are checked by [individual source inversion CI](https://github.com/vanderpol/scap-ng/actions/runs/38907309219) and the [full six-STIG native collector census](https://github.com/vanderpol/scap-ng/actions/runs/38909973142).

**Windows 11 — minimum password length, SV-253303**

~~~yaml
check: "'Minimum password length' is set to at least '14' characters"
inspect: windows.passwordpolicy
require:
  min_passwd_len:
    at_least: 14
~~~

Here the `windows.passwordpolicy` capability is the **actual built-in collector**; it does not require a manufactured Object or `where`. The narrowly verified native research operator also reconstructs its source field/Item cardinality and reporting controls, which are omitted from this human-facing excerpt.

**RHEL 9 — `/home` must use the `nosuid` mount option, SV-257851**

~~~yaml
check: /home is mounted with the nosuid option.
inspect: linux.partition
where:
  mount_point:
    matches_regex: '.*\/home'
require:
  mount_options:
    includes_value: nosuid
~~~

This is the early **capability-specific** typed macro. It lowers to the original per-partition **all selected Items must satisfy**, but per-partition `mount_options` **at least one observed option must equal `nosuid`**. The source regex can select mounts beyond exactly `/home`; it has deliberately **not** been tightened. [Pinned real source](https://github.com/vanderpol/scap-ng-editor-sample-data/blob/99cbceae8d594c44cb509df95975ac1676a2b44a/focused-fixtures/source-backed/authoring/shared/assessments/linux/other/home-mounted-nosuid-option.assessment.yaml).

**Readability warning:** Both compact examples are supported by a **narrow, source-specific research compiler contract**; they are not an approved global default that would let any other capability omit Item/State quantifiers. Exact Test structure does not independently prove live scanner six-state outcomes.

## 1. Linux — account-derived file permissions

Real source: [RHEL9 SV-257889 shared Assessment](https://github.com/vanderpol/scap-ng-editor-sample-data/blob/99cbceae8d594c44cb509df95975ac1676a2b44a/focused-fixtures/source-backed/authoring/shared/assessments/linux/other/initialization-files-0740-less-permissive.assessment.yaml). **Two complete Tests, three shared collections**. The original uses password-account Sets, filters, `for_each` from users to files, filesystem/traversal controls, eight permission predicates, and separate optional/nonoptional file populations.

```yaml
# Abbreviated authoring sketch: one original Set operand (not the whole Assessment)
check: Local initialization files for non-system users have mode 0740 or less permissive.
inspect: unix.file
gather:
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
  every_item_must_match:
    all_of:
      - setuid:
          is: false
      - setgid:
          is: false
      # six additional source predicates in the complete YAML
    all_fields_must_exist: true
```

**Where does the `for_each_source.in` name come from?** It is an exact reference to a named collection under `sources` in this same Assessment; the interpreter never parses the words in the identifier as filtering rules. To make the example understandable from scratch, here are the two required source definitions in the **same experimental English-first layout**:

```yaml
sources:
  users-username-object:
    inspect: unix.password
    where:
      username:
        matches_regex: '[\w]+'

  only-non-system-users-uid-999-home-dirs-excluding-root-object:
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
```

`difference` above is the proposed direct spelling for the original `set.operator: difference`; no extra `combine` layer is needed. The actual requirements exclude user IDs below 1000 and home directory `/`, retaining the source field-presence requirements. Each remaining account supplies `user.home_dir` for `for_each_source`. Titles and the rest of the Assessment are omitted here, so this is an explanatory excerpt, **not a standalone runnable file**. See the [complete pinned 0.4 source](https://github.com/vanderpol/scap-ng-editor-sample-data/blob/99cbceae8d594c44cb509df95975ac1676a2b44a/focused-fixtures/source-backed/authoring/shared/assessments/linux/other/initialization-files-0740-less-permissive.assessment.yaml).

**What succeeds:** source account→file projection, Set union/filter and eight-field check are representable in one reversible YAML tree; the root-user Test separately requires at least one file.

**Still under review:** `for_each_source` expands collection from users, whereas `every_item_must_match` evaluates the collected files. The real source contains a **one-operand union**; this excerpt keeps it visible rather than silently deleting the source operation. Removing that union or replacing `combine.union` with `gather.union` needs a fail-closed round-trip proof. No scanner has proved actual traversal behavior.

## 2. Windows 11 — Remote Desktop rights depend on domain role

Real source: [Windows 11 SV-253495](https://github.com/vanderpol/scap-ng-editor-sample-data/blob/99cbceae8d594c44cb509df95975ac1676a2b44a/focused-fixtures/source-backed/authoring/ms_windows_11/assessments/automated/SV-253495.automated.yaml). **Seven real Tests and two shared collections.** WMI `DomainRole` records distinguish standalone from non-DC domain-joined systems; user-right assignment checks require *some* matching collected Items; the Assessment uses an OR of three alternatives.

```yaml
# Abbreviated compact-layout excerpt; other five named Tests remain in the full YAML
sources:
  windows-wmi57-object:
    inspect: windows.wmi.query
    collect:
      namespace: root\cimv2
      query: SELECT DomainRole FROM win32_computersystem
  windows-userright-object:
    inspect: windows.userright
    where:
      userright:
        equals: SE_DENY_REMOTE_INTERACTIVE_LOGON_NAME
checks:
  system-non-dc-domain-joined-windows-server-or-workstation-test:
    check: The system is a non-DC domain-joined Windows server or workstation
    inspect: windows.wmi.query
    from: windows-wmi57-object
    require:
      at_least_one_item_exists: true
      every_item_must_match:
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
    from: windows-userright-object
    require:
      at_least_one_item_exists: true
      at_least_one_item_matches:
        trustee_name:
          equals_ignoring_case: Guests
```

**What succeeds:** native WMI collection, explicit record/field scope, Windows user-right selectors, all seven Test definitions and their exact named-Test Boolean composition reconstruct without collapsing alternatives.

**Critical counterexample:** two WMI records holding `domainrole=1` and `domainrole=3` do **not** behave like a single `domainrole in ['1','3']` predicate under the original OR-of-whole-States. The research suite rejects that tempting but lossy rewrite. The readable `at_least_one_item_matches` name retains the original *some-Item* requirement; it does not change the per-record or per-field quantifiers.

## 3. Windows Server DNS — dynamic zone names and three passing alternatives

Real source: [DNS SV-259345](https://github.com/vanderpol/scap-ng-editor-sample-data/blob/99cbceae8d594c44cb509df95975ac1676a2b44a/focused-fixtures/source-backed/authoring/ms_windows_server_dns/assessments/automated/SV-259345.automated.yaml). **Five Tests, three local command-building Variables, one shared zone collection**.

```yaml
# Shortened layout; the source Variable graph is still required
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

**Authoring dependency, not a magic identifier:** the `command-get-issigned-setting-each-forward-lookup-zone-variable` definition concatenates a PowerShell command with `stdout_line` values from the named `list-all-forward-lookup-zones-object`. The other two command Variables similarly use that same zone collection for ZoneSigningKey and KeySigningKey validity periods. An author must define the shared zone source and all three command expressions before referencing them in the five Checks. The [reference graph audit](../../../tools/research_english_first_04_references.py) now checks those names and detects cycles, but does not validate command behavior.

**Still awkward:** the command `variable` reference is readable only after opening the `metadata.variables` expression graph in the full file. We have *not* proved that replacing it with a simpler per-zone `for_each` would preserve execution, multiplicity, or result status.

## 4. Apache UNIX — required vs optional settings across included files

Real source: [Apache SV-214228](https://github.com/vanderpol/scap-ng-editor-sample-data/blob/99cbceae8d594c44cb509df95975ac1676a2b44a/focused-fixtures/source-backed/authoring/apache_server_2-4_unix_server/assessments/automated/SV-214228.automated.yaml). **Four Tests and 18 local Variables**, including installation discovery and `Include`/`IncludeOptional` configuration processing.

```yaml
# Shortened layout of the optional KeepAlive Test
check: If the KeepAlive directive is defined in other loaded configuration files, verify it is configured to On
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
  every_item_must_match:
    stdout_line:
      when_present_matches_regex: '\s*KeepAlive On'

# The full file retains two required and two optional/config-context Tests,
# plus the entire source discovery/variable graph and all_of evaluation.
```

**What succeeds:** exact presence requirements for required versus optional config fields are kept distinct; shell parameters, stderr/exit settings, regex capture, four Tests, 18 Variables, shared discovery and `all_of` reconstruct.

**Authoring dependency:** the source chain discovers Apache executable/install paths, derives `HTTPD_ROOT` and `SERVER_CONFIG_FILE`, finds included or loaded configuration files, and builds commands to inspect the required and optional directives. The 18 Variables are **not** interchangeable or one flat list. Their dependencies are now classified by the [graph audit](../../../tools/research_english_first_04_references.py); only a source-backed, reversible simplification could replace them.

**Still awkward:** the dependency graph is not yet expressed in natural language; shortening it to `load Apache config` would lose important discovery semantics and provenance without further proof.

## What this evidence does—and does not—say

| Gate | Current evidence |
| --- | --- |
| Actual source reconstruction | **PASS** — the linked four *complete* experimental Assessments, including Variables, Objects, State/Item requirements and named-Test evaluation trees, round-trip exactly. The proposed union simplification in this page is **not** part of that proof |
| Negative source constraints | **PASS** — unsupported Set operators, missing Item requirements and unrecognized predicates rejected |
| Exact original OVAL runtime outcomes | **NOT PROVEN** — no independent SCAP-NG 0.4 scanner or six-state system-evidence parity |
| Human comprehension | **NOT YET TESTED** — especially collected-Item vs record scope, `any_of` whole-State alternatives, and derived command Variables |
| Official v0.4 grammar / new signed bundle | **NOT CHANGED** — existing review releases remain immutable |

**Research judgment:** this goes significantly farther than one-line examples: a *single reversible research format* now represents four genuinely complex Assessment graphs, but its readability is uneven. The next design task is to make account/file and dynamic command acquisition human-readable without silently erasing Items, statuses, Variables, or evidence. Do not ask reviewers to approve this grammar yet.

Tracking: [#235 research](https://github.com/vanderpol/scap-ng/issues/235) · [#229 semantic conformance](https://github.com/vanderpol/scap-ng/issues/229) · [Source compiler and full YAML artifact workflow](https://github.com/vanderpol/scap-ng/actions/workflows/research-english-first-04.yml).
