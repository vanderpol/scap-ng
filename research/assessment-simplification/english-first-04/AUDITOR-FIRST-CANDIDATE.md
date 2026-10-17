# SCAP-NG 0.4 research: auditor-first authoring candidate

**Pre-alpha research proposal, not adopted 0.4 syntax.** This is a candidate for **the one SCAP-NG authoring language**, not a lossy presentation layer. Its source-structure fidelity is checked against the pinned [six-STIG corpus](reports/README.md). Original SCAP 1.4 run-time behavior, evidence output, and human usability still need independent proof.

## Recommendation

Keep a natural top-to-bottom workflow:

**Say what to check → identify the native data → select/collect it → state explicit requirements → combine named checks.**

Retain **`inspect`** and **`where`** *provisionally* because each has a clear, different job in real examples. They are not sacred names. `collect`, `from`, and Set inclusion/exclusion likewise express different kinds of source construction. Changing words without improving the author's ability to reason about a complete check is not an improvement.

The biggest verified clarity improvement so far is in `require`: separate **how many selected Items must exist** from **which Items must match the State condition**. Do not conflate Item cardinality with field/value cardinality.

## Simple real RHEL check (SV-257851)

```yaml
checks:
  home-mounted-nosuid-option-test:
    check: /home is mounted with the nosuid option.
    inspect: linux.partition
    where:
      mount_point:
        matches_regex: '.*\/home'
    require:
      items: at_least_one
      every_item:
        mount_options:
          at_least_one_value_is: nosuid
    report_elements: all

evaluate:
  test: home-mounted-nosuid-option-test
```

**Read it:** Inspect mounted Linux partitions; choose those whose mount point matches the **original source pattern**; at least one partition must exist; **every** selected partition must contain a `nosuid` option among its reported values. The source pattern is deliberately not silently rewritten to `equals: /home`, since that would be a semantic change. The field comparator now reads `at_least_one_value_is`, which describes **field-value** matching rather than Item matching. This is a reversible alias, not a new default or changed comparison.

The complete candidate retains Assessment metadata and any other required source structures, omitted **only from this editorial excerpt**. See [the full original and current English-first RHEL comparison](FULL-01-linux-home.md).

## Same requirement shape for complex checks

The following examples show real *excerpted* criteria. The complete source-linked candidate YAMLs are generated and independently source-inverted by the [auditor grammar proof](../../../tools/research_english_first_04_auditor_candidate.py). When verified and published on GitHub, use the five direct files linked below.

**Linux dependent collections and permissions (SV-257889).** Define the named non-system-user and root-account collections first. Then each file check describes its dependent per-user file collection before conditions. Preserve the otherwise unintuitive, original one-operand Set union, directory exclusions, eight permission fields, and two different existence rules.

```yaml
checks:
  local-initialization-files-non-system-users-have-mode-0740-or-test:
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
      items: may_be_absent
      every_item:
        all_of:
          - setuid: {is: false}
          - setgid: {is: false}
          # Six other required permission fields in the full Assessment
        all_fields_must_exist: true
```

**Windows 11 WMI / deny-rights (SV-253495).** A role query and shared user-right collection are named data sources. The following State alternatives must apply to the **whole record comparison**, not become one `domainrole in [1,3]` field predicate. Other deny-right checks use `at_least_one_item`, not `every_item`.

```yaml
checks:
  system-non-dc-domain-joined-windows-server-or-workstation-test:
    check: The system is a non-DC domain-joined Windows server or workstation
    inspect: windows.wmi.query
    from: windows-wmi57-object
    require:
      items: at_least_one
      every_item:
        any_of:
          - result:
              at_least_one_record_exists: true
              every_record:
                domainrole: {is: '1'}
          - result:
              at_least_one_record_exists: true
              every_record:
                domainrole: {is: '3'}
```

**Windows DNS (SV-259345).** First explain how source zone discovery feeds the three command-building Variables; only then evaluate the five command-based Tests. The signatures' 48-hour and 168-hour bounds are **two** separate States, with a final `any_of` three-branch decision. A compact signature check is:

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
  items: at_least_one
  every_item:
    stdout_line:
      exactly_one_is: 'True'
```

**Apache HTTP Server (SV-214228).** Discovery/Include paths and 18 Variables must remain visible and testable. A directive that is mandatory has a different field presence rule from one evaluated only *when present*. The two `KeepAlive` Tests and two `MaxKeepAliveRequests` Tests must still be joined with `all_of`.

```yaml
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
  items: at_least_one
  every_item:
    stdout_line:
      when_present_matches_regex: '\s*KeepAlive On'
```

These are illustrations of one candidate grammar, **not complete executable Assessments**. All referenced source IDs must be declared by the complete file. Auditors should begin with a full Assessment, not a disconnected clause.

## Explicit keyword contract

| Term | Meaning | Must not be confused with |
| --- | --- | --- |
| `check` | Describes the security condition in ordinary words | A substitute for executable criteria |
| `inspect` | Chooses a native source capability, e.g., `linux.partition` | A predicate or compliance outcome |
| `where` | Native Object selection *before* observed Items are evaluated | Post-collection Set filters or `require` |
| `collect` | Native command/query/traversal arguments | The selection predicate |
| `from` | Reference to a previously defined source | An undeclared or guessed identifier |
| `gather` | Explicit composition of complex collection sources, Sets, dependent iteration | A redundant wrapper for every simple Object |
| `include_if`, `exclude_if` | Filter already collected Set Items | Pre-collection Object selection |
| Field comparators such as `at_least_one_value_is` | How many **values within one field** must meet a condition; separate from the Item count | `require.items` / `require.every_item` |
| `require.items` | Explicit Item existence rule: `at_least_one`, `exactly_one`, `none`, `may_be_absent`, or `all_must_exist` | Item matching or field matching |
| `require.every_item` / `at_least_one_item` / `exactly_one_item` / `no_item` | Scope over the selected Items, separate from their existence requirement | How many values of a field must match |
| `evaluate` | Combines named checks using explicit Boolean alternatives, conjunctions and conditions | An invented implicit AND/OR default |
| `report_elements` | Evidence disclosure behavior | A compliance test |

`require.items: none` is **not** synonymous with `require.no_item`. The former requires zero existing Items; the latter is a predicate requiring no selected Items to match, with a separate Item-existence policy.

The grammar recognizes **only the ten proven paired Item modes and five State-free modes**. An unmodeled pair is rejected; it is not guessed or assigned a default. It preserves nested State-field cardinality, WMI record grouping, Set operand order, error statuses, and command/Variable references.

## Proof and decision gates

- The pinned six-STIG archive contains **872 distinct automated Assessments**. Exact whole-Assessment source reconstruction is currently **871/872**, or **1,374 named Tests**, including the four large real-world examples. The proposed `require.items`/match structure is additionally tested by an independent reversible experimental transformer and nine intentional malformed-input guards.
- **The remaining bootloader anomaly is not a reason to invent more grammar.** The locally pinned **OVAL 5.12.3 definitions schema** includes a Schematron assertion that disallows a State reference when `check_existence=none_exist`. The one excluded SCAP-NG source Assessment has that contradictory combination. Verify the underlying original OVAL XML and conversion history, repair its provenance/converter if needed, and fail closed until then. Do **not** silently discard the extra State.
- Whole-source reconstruction is **not** independent OVAL scanner execution or six-state evidence parity; generic model agreement is only supporting evidence. Nor has any human authoring study proven the syntax easier to write.

### Complete research candidate YAML on GitHub

The workflow publishes five complete examples after the candidate passes its source-inversion tests. The link targets below are ordinary `github.com` files rather than download artifacts:

- [RHEL `/home`](auditor-candidate/linux-home.auditor.research.yaml)
- [RHEL dependent files](auditor-candidate/linux-files.auditor.research.yaml)
- [Windows WMI and user rights](auditor-candidate/windows-wmi-rights.auditor.research.yaml)
- [Windows DNS](auditor-candidate/dns.auditor.research.yaml)
- [Apache](auditor-candidate/apache.auditor.research.yaml)

**Current recommendation:** This is the strongest *source-reversible* auditor-facing candidate tested so far: predictable data-first order, distinct source/selector/filter roles, concise explicit Item existence and matching. Before selecting it for 0.4, get security auditors to **author two new checks from a one-page reference** without looking at existing examples, and validate actual OVAL 5.12.3 input/evidence semantics.
