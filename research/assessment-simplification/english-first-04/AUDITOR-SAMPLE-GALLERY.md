# Auditor-first SCAP-NG: six real source-backed patterns

**Latest experimental authoring presentation; NOT approved v0.4 syntax or scanner-equivalence evidence.** These are excerpts from complete, **source-structurally reversible** six-STIG Assessments. [Read the full proof, limitations and the one rejected source](consistent-quantifiers/report.md). Original source acquisition, collection flags, missing-field rules and final evaluate trees remain in the linked complete files; omission from an excerpt does not make them optional.

**One consistent rule:** `items` counts collected Items; `match` says how many must satisfy the predicate. Records use `records` and the same `match` choices (`all`, `at_least_one`, `exactly_one`, `none`). A `states.and/or` groups **whole States**; `fields.and/or` groups **fields inside a State**. No `scope:` or `condition:` wrapper, and no `some` synonym.

## 1. RHEL 9 — `/home` must use nosuid

```yaml
inspect: linux.partition
where:
  mount_point: {matches_regex: '.*\/home'}
require:
  items: at_least_one
  match: all
  mount_options: {at_least_one_value_is: nosuid}
```

At least one selected partition exists; every selected partition has `nosuid` among its mount options. The source regex is preserved instead of silently tightening it to `/home` equality. [Complete RHEL Assessment](consistent-quantifiers/linux-home.consistent.research.yaml).

## 2. Windows 11 — Guests must have a deny-logon right

```yaml
from: windows-userright-object
require:
  items: at_least_one
  match: at_least_one
  trustee_name: {equals_ignoring_case: Guests}
```

At least one Item must exist and at least one must match the Guests identity; **not every trustee Item must be Guests**. The named source restricts which user right is collected. [Complete seven-Test Windows Assessment](consistent-quantifiers/windows-wmi-rights.consistent.research.yaml).

## 3. Windows 11 — WMI DomainRole, two whole-State alternatives

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
          domainrole: {is: '1'}
      - result:
          records: at_least_one
          match: all
          domainrole: {is: '3'}
```

The outer `states.or` means **either entire record-comparison alternative** must hold for an Item; it does *not* change the record-level rules or mean that each record may freely have role `1` or `3`. For records `[1,3]`, neither `match: all` branch succeeds. [Complete Windows Assessment](consistent-quantifiers/windows-wmi-rights.consistent.research.yaml).

## 4. Windows DNS — signature-validity lower and upper bounds

```yaml
require:
  items: at_least_one
  match: all
  states:
    and:
      - stdout_line: {at_least: 48}
      - stdout_line: {at_most: 168}
```

The original Assessment contains two bound States and constructs PowerShell commands from collected zone names. This excerpt omits the actual collector, command Variable and **an inherited field-presence rule**, all retained in the complete source. [Complete DNS Assessment](consistent-quantifiers/dns.consistent.research.yaml).

## 5. Apache — required Item with an optional field comparison

```yaml
require:
  items: at_least_one
  match: all
  stdout_line:
    when_present_matches_regex: '\s*KeepAlive On'
```

The Item must exist; the `stdout_line` comparison applies **when that field is present**. These are distinct requirements. Apache's actual multi-file command/Variable discovery graph is still needed. [Complete Apache Assessment](consistent-quantifiers/apache.consistent.research.yaml).

## 6. Linux — account-dependent initialization files

```yaml
require:
  items: if_present
  match: all
  fields:
    and:
      - setuid: {is: false}
      - setgid: {is: false}
      # Six other permission fields in the source
    presence: all
```

The non-system-user branch permits no matching files, but when files exist every Item must satisfy eight required field comparisons. The separate root-account branch instead requires `items: at_least_one`. The complete file retains user-derived collection, Set operations, directory exclusion and source references. [Complete Linux Assessment](consistent-quantifiers/linux-files.consistent.research.yaml).

## Proof boundary and remaining authoring cleanup

The latest conversion structurally reconstructs **871/872 complete automated Assessments (1,374/1,375 Tests)**. It is not independently proved to reproduce original OVAL six-state runtime and evidence behavior. It deliberately preserves legacy `all_exist` source distinctions, and rejects the contradictory bootloader Test with an attached State.

Some **other** old field-presence controls remain in the generated complete files, notably a top-level `all_state_fields_exist: true` in DNS and field-level `no_values_exist: true` elsewhere. These are *semantically meaningful legacy requirements*, not proof they should remain Boolean flags in the final authoring language. They require their own reversible rewrite rather than being silently deleted.

**Review standard:** an auditor should understand acquisition, Item and record cardinality, missing data, field value matching, and complete `and`/`or` group semantics without memorizing special inheritance rules. [Research task #235](https://github.com/vanderpol/scap-ng/issues/235).