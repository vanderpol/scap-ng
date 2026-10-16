# 04 · Windows Server DNS RRSIG validity and zone discovery — complete before and after

**Review-only research. The after version is experimental and is not approved 0.4 syntax or independent OVAL scanner-conformance evidence.**

[Back to all five complete examples](BEFORE-AFTER-REVIEW.md) · [Original pinned source](https://github.com/vanderpol/scap-ng-editor-sample-data/blob/99cbceae8d594c44cb509df95975ac1676a2b44a/focused-fixtures/source-backed/authoring/ms_windows_server_dns/assessments/automated/SV-259345.automated.yaml) · [Full generated research YAML](comparisons/dns-zone-signing.research.yaml)

## What changed (and what did not)

- All three command-building Variables, the shared zone source, five Tests, and the original `evaluate` branches are shown—not just the DNSSEC signing Test.
- `inspect` and `collect` sit together rather than nesting a redundant `gather.inspect` for normal command collection.
- The powershell command expressions still rely on the zone-list collection. No unproven conversion to `for_each` is presented.

**Authoring question:** Could you write a fourth DNS command check from scratch using these definitions, or is the variable graph too opaque?

## Before — complete existing 0.4 Assessment

Full source including metadata, Tests, shared Objects, Variables (where used), source selectors and evaluate tree. Nothing omitted.

```yaml
assessment:
  id: SV-259345.automated
  version: 8
  assessment_title: The validity period for the Resource Record Signatures (RRSIGs) covering a zone's DNSKEY RRSet
    must be no less than two days and no more than one week.
  mode: automated
  class: compliance
  purpose: assessment
  specification:
    id: scap-ng.pre-alpha.assessment
    version: 0.4.0
  variables:
    command-get-issigned-setting-each-forward-lookup-zone-variable:
      title: The command to get the 'IsSigned' setting for each forward lookup zone
      kind: local
      datatype: string
      expression:
        concat:
        - literal:
            value: 'try {Get-DnsServerZone -Name '
            datatype: string
        - values:
            object: list-all-forward-lookup-zones-object
            field: stdout_line
        - literal:
            value: ' | ForEach-Object {$_.IsSigned}} catch {}'
            datatype: string
    command-get-list-dns-key-signature-validity-periods-zone-signing-variable:
      title: The command to get the list of DNS key signature validity periods for the zone signing keys
      kind: local
      datatype: string
      expression:
        concat:
        - literal:
            value: 'try {Get-DNSServerSigningKey -ZoneName '
            datatype: string
        - values:
            object: list-all-forward-lookup-zones-object
            field: stdout_line
        - literal:
            value: ' | Where-Object KeyType -eq ''ZoneSigningKey'' | ForEach-Object {$_.DnsKeySignatureValidityPeriod.Days
              * 24 + $_.DnsKeySignatureValidityPeriod.Hours}} catch {Write-Output ''0''}'
            datatype: string
    command-get-list-dns-key-signature-validity-periods-key-signing-variable:
      title: The command to get the list of DNS key signature validity periods for the key signing keys
      kind: local
      datatype: string
      expression:
        concat:
        - literal:
            value: 'try {Get-DNSServerSigningKey -ZoneName '
            datatype: string
        - values:
            object: list-all-forward-lookup-zones-object
            field: stdout_line
        - literal:
            value: ' | Where-Object KeyType -eq ''KeySigningKey'' | ForEach-Object {$_.DnsKeySignatureValidityPeriod.Days
              * 24 + $_.DnsKeySignatureValidityPeriod.Hours}} catch {Write-Output ''0''}'
            datatype: string
  tests:
    dns-server-caching-only-there-no-forward-or-reverse-lookup-test:
      test_title: DNS server is caching only (there are no forward or reverse lookup zones)
      capability: independent.shellcommand
      object:
        capability: independent.shellcommand
        object_title: The list of all forward and reverse lookup zones
        collect:
          shell: powershell
          command: Get-DnsServerZone | Where-Object {$_.ZoneType -notin @('Forwarder') -and $_.ZoneName -notin @('TrustAnchors')
            -and (-Not $_.IsAutoCreated)} | ForEach-Object {$_.ZoneName}
          error_if_exit_status_not_0: false
          error_if_stderr_exists: false
      states:
      - stdout_line:
          require: none_exist
          equals: ''
      reported_elements: all
      collected_items_require: at_least_one_exists_and_all_match
    all-forward-lookup-zones-if-any-integrated-active-directory-test:
      test_title: All forward lookup zones (if any) are integrated with Active Directory
      capability: independent.shellcommand
      object:
        capability: independent.shellcommand
        object_title: The list of all forward lookup zones that are not integrated with Active Directory
        collect:
          shell: powershell
          command: Get-DnsServerZone | Where-Object {$_.ZoneType -notin @('Forwarder') -and $_.ZoneName -notin @('TrustAnchors')
            -and (-Not $_.IsAutoCreated) -and -Not($_.IsReverseLookupZone) -and (-Not $_.IsDsIntegrated)} | ForEach-Object
            {$_.ZoneName}
          error_if_exit_status_not_0: false
          error_if_stderr_exists: false
      states:
      - stdout_line:
          require: none_exist
          equals: ''
      reported_elements: all
      collected_items_require: at_least_one_exists_and_all_match
    all-forward-lookup-zones-dnssec-signed-test:
      test_title: All forward lookup zones are DNSSEC signed
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
      states:
      - stdout_line:
          require: only_one_exists_and_matches
          equals: 'True'
      reported_elements: all
      collected_items_require: at_least_one_exists_and_all_match
    all-forward-lookup-zones-have-dns-key-signature-validity-periods-test:
      test_title: All forward lookup zones have DNS key signature validity periods between two days and a week for
        their zone signing keys
      capability: independent.shellcommand
      object:
        capability: independent.shellcommand
        object_title: The list of DNS key signature validity periods for the zone signing keys
        collect:
          shell: powershell
          command:
            variable: command-get-list-dns-key-signature-validity-periods-zone-signing-variable
          error_if_exit_status_not_0: false
          error_if_stderr_exists: false
      states:
      - stdout_line:
          greater_than_or_equal: 48
      - stdout_line:
          less_than_or_equal: 168
      reported_elements: all
      states_match: all
      state_fields_require: at_least_one_exists_and_all_match
      collected_items_require: at_least_one_exists_and_all_match
    all-forward-lookup-zones-have-dns-key-signature-validity-periods-2-test:
      test_title: All forward lookup zones have DNS key signature validity periods between two days and a week for
        their key signing keys
      capability: independent.shellcommand
      object:
        capability: independent.shellcommand
        object_title: The list of DNS key signature validity periods for the key signing keys
        collect:
          shell: powershell
          command:
            variable: command-get-list-dns-key-signature-validity-periods-key-signing-variable
          error_if_exit_status_not_0: false
          error_if_stderr_exists: false
      states:
      - stdout_line:
          greater_than_or_equal: 48
      - stdout_line:
          less_than_or_equal: 168
      reported_elements: all
      states_match: all
      state_fields_require: at_least_one_exists_and_all_match
      collected_items_require: at_least_one_exists_and_all_match
  evaluate:
    any:
    - test: dns-server-caching-only-there-no-forward-or-reverse-lookup-test
    - test: all-forward-lookup-zones-if-any-integrated-active-directory-test
    - all:
      - test: all-forward-lookup-zones-dnssec-signed-test
      - test: all-forward-lookup-zones-have-dns-key-signature-validity-periods-test
      - test: all-forward-lookup-zones-have-dns-key-signature-validity-periods-2-test
  shared_objects:
    list-all-forward-lookup-zones-object:
      capability: independent.shellcommand
      object_title: The list of all forward lookup zones
      collect:
        shell: powershell
        command: Get-DnsServerZone | Where-Object {$_.ZoneType -notin @('Forwarder') -and $_.ZoneName -notin @('TrustAnchors')
          -and (-Not $_.IsAutoCreated) -and (-Not($_.IsReverseLookupZone))} | ForEach-Object {$_.ZoneName}
        error_if_exit_status_not_0: false
        error_if_stderr_exists: false
```

## After — complete generated English-first research Assessment

Full experimental version, including metadata, named sources, checks, local Variables, requirements and evaluate tree. Nothing omitted.

```yaml
# EXPERIMENT ONLY; reconstructs the pinned Assessment exactly.
# Not normative SCAP-NG v0.4 or independently validated OVAL execution.
metadata:
  id: SV-259345.automated
  version: 8
  assessment_title: The validity period for the Resource Record Signatures (RRSIGs)
    covering a zone's DNSKEY RRSet must be no less than two days and no more than
    one week.
  mode: automated
  class: compliance
  purpose: assessment
  specification:
    id: scap-ng.pre-alpha.assessment
    version: 0.4.0
  variables:
    command-get-issigned-setting-each-forward-lookup-zone-variable:
      title: The command to get the 'IsSigned' setting for each forward lookup zone
      kind: local
      datatype: string
      expression:
        concat:
        - literal:
            value: 'try {Get-DnsServerZone -Name '
            datatype: string
        - values:
            object: list-all-forward-lookup-zones-object
            field: stdout_line
        - literal:
            value: ' | ForEach-Object {$_.IsSigned}} catch {}'
            datatype: string
    command-get-list-dns-key-signature-validity-periods-zone-signing-variable:
      title: The command to get the list of DNS key signature validity periods for
        the zone signing keys
      kind: local
      datatype: string
      expression:
        concat:
        - literal:
            value: 'try {Get-DNSServerSigningKey -ZoneName '
            datatype: string
        - values:
            object: list-all-forward-lookup-zones-object
            field: stdout_line
        - literal:
            value: ' | Where-Object KeyType -eq ''ZoneSigningKey'' | ForEach-Object
              {$_.DnsKeySignatureValidityPeriod.Days * 24 + $_.DnsKeySignatureValidityPeriod.Hours}}
              catch {Write-Output ''0''}'
            datatype: string
    command-get-list-dns-key-signature-validity-periods-key-signing-variable:
      title: The command to get the list of DNS key signature validity periods for
        the key signing keys
      kind: local
      datatype: string
      expression:
        concat:
        - literal:
            value: 'try {Get-DNSServerSigningKey -ZoneName '
            datatype: string
        - values:
            object: list-all-forward-lookup-zones-object
            field: stdout_line
        - literal:
            value: ' | Where-Object KeyType -eq ''KeySigningKey'' | ForEach-Object
              {$_.DnsKeySignatureValidityPeriod.Days * 24 + $_.DnsKeySignatureValidityPeriod.Hours}}
              catch {Write-Output ''0''}'
            datatype: string
sources:
  list-all-forward-lookup-zones-object:
    inspect: independent.shellcommand
    description: The list of all forward lookup zones
    collect:
      shell: powershell
      command: Get-DnsServerZone | Where-Object {$_.ZoneType -notin @('Forwarder')
        -and $_.ZoneName -notin @('TrustAnchors') -and (-Not $_.IsAutoCreated) -and
        (-Not($_.IsReverseLookupZone))} | ForEach-Object {$_.ZoneName}
      error_if_exit_status_not_0: false
      error_if_stderr_exists: false
checks:
  dns-server-caching-only-there-no-forward-or-reverse-lookup-test:
    check: DNS server is caching only (there are no forward or reverse lookup zones)
    inspect: independent.shellcommand
    require:
      at_least_one_item_exists: true
      every_item_must_match:
        stdout_line:
          no_values_exist: true
          source_comparison:
            is: ''
    report_elements: all
    description: The list of all forward and reverse lookup zones
    collect:
      shell: powershell
      command: Get-DnsServerZone | Where-Object {$_.ZoneType -notin @('Forwarder')
        -and $_.ZoneName -notin @('TrustAnchors') -and (-Not $_.IsAutoCreated)} |
        ForEach-Object {$_.ZoneName}
      error_if_exit_status_not_0: false
      error_if_stderr_exists: false
  all-forward-lookup-zones-if-any-integrated-active-directory-test:
    check: All forward lookup zones (if any) are integrated with Active Directory
    inspect: independent.shellcommand
    require:
      at_least_one_item_exists: true
      every_item_must_match:
        stdout_line:
          no_values_exist: true
          source_comparison:
            is: ''
    report_elements: all
    description: The list of all forward lookup zones that are not integrated with
      Active Directory
    collect:
      shell: powershell
      command: Get-DnsServerZone | Where-Object {$_.ZoneType -notin @('Forwarder')
        -and $_.ZoneName -notin @('TrustAnchors') -and (-Not $_.IsAutoCreated) -and
        -Not($_.IsReverseLookupZone) -and (-Not $_.IsDsIntegrated)} | ForEach-Object
        {$_.ZoneName}
      error_if_exit_status_not_0: false
      error_if_stderr_exists: false
  all-forward-lookup-zones-dnssec-signed-test:
    check: All forward lookup zones are DNSSEC signed
    inspect: independent.shellcommand
    require:
      at_least_one_item_exists: true
      every_item_must_match:
        stdout_line:
          exactly_one_is: 'True'
    report_elements: all
    description: The 'IsSigned' setting for each forward lookup zone
    collect:
      shell: powershell
      command:
        variable: command-get-issigned-setting-each-forward-lookup-zone-variable
      error_if_exit_status_not_0: false
      error_if_stderr_exists: false
  all-forward-lookup-zones-have-dns-key-signature-validity-periods-test:
    check: All forward lookup zones have DNS key signature validity periods between
      two days and a week for their zone signing keys
    inspect: independent.shellcommand
    require:
      at_least_one_item_exists: true
      every_item_must_match:
        all_states:
        - stdout_line:
            at_least: 48
        - stdout_line:
            at_most: 168
    report_elements: all
    all_state_fields_exist: true
    description: The list of DNS key signature validity periods for the zone signing
      keys
    collect:
      shell: powershell
      command:
        variable: command-get-list-dns-key-signature-validity-periods-zone-signing-variable
      error_if_exit_status_not_0: false
      error_if_stderr_exists: false
  all-forward-lookup-zones-have-dns-key-signature-validity-periods-2-test:
    check: All forward lookup zones have DNS key signature validity periods between
      two days and a week for their key signing keys
    inspect: independent.shellcommand
    require:
      at_least_one_item_exists: true
      every_item_must_match:
        all_states:
        - stdout_line:
            at_least: 48
        - stdout_line:
            at_most: 168
    report_elements: all
    all_state_fields_exist: true
    description: The list of DNS key signature validity periods for the key signing
      keys
    collect:
      shell: powershell
      command:
        variable: command-get-list-dns-key-signature-validity-periods-key-signing-variable
      error_if_exit_status_not_0: false
      error_if_stderr_exists: false
evaluate:
  any_of:
  - test: dns-server-caching-only-there-no-forward-or-reverse-lookup-test
  - test: all-forward-lookup-zones-if-any-integrated-active-directory-test
  - all_of:
    - test: all-forward-lookup-zones-dnssec-signed-test
    - test: all-forward-lookup-zones-have-dns-key-signature-validity-periods-test
    - test: all-forward-lookup-zones-have-dns-key-signature-validity-periods-2-test
```

## What to tell us

- Can you trace the complete logic without opening a missing definition?
- Is the after version easier to write from scratch, or merely shorter?
- Where does the vocabulary or nesting remain inconsistent?

**Structural evidence:** [The six-STIG run 38934771985](https://github.com/vanderpol/scap-ng/actions/runs/38934771985) reconstructed the original full Assessment dictionaries using this research representation. This does not establish SCAP 1.4 runtime/evidence equivalence.
