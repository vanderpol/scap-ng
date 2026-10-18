# Blind DNS authoring review — named commands versus inline expressions

**October 18, 2026 · Unprimed comprehension/authoring research, issue [#235](https://github.com/vanderpol/scap-ng/issues/235).** This page gives the reviewer two **full** experimental renderings of the same pinned Windows DNS Assessment. **Neither is an accepted SCAP-NG 0.4 syntax or an executable representation.** Nothing below is proof of runtime behavior.

## Instructions to an independent reviewer

You are a security auditor, not a designer of this language. **Do not read the companion composition contract or the answer key until you have submitted your first response.** Assume no knowledge of OVAL or the repository. These are authoring proposals; you cannot assume the presence of a scanner. Read A and B independently, then compare.

For **each** sample, answer in ordinary language and mark each answer as **confident / ambiguous / unknowable from the YAML**. If a rule is ambiguous, offer two plausible interpretations rather than guessing its intended behavior.

1. Identify the exact source of the forward-zone names and the Test or Tests that use them.
2. Explain whether a zone list containing **zero, one, or two** distinct values causes one command, one command per zone, or one command containing a combined list. **Cite the line(s); do not infer loops from a plural name.**
3. Where is the string used to request `IsSigned` constructed? Where are the zone-signing and key-signing validity commands constructed? How many separate places must you open/scroll to understand all three?
4. Explain the difference between a successfully collected shell-command Item with **no stdout lines** and **no shell-command Item**. Are the two treated alike in these checks?
5. What happens when the zone list cannot be collected, collection is incomplete, or a command emits stderr? Which behavior is explicit and what must be documented separately?
6. Identify the exact alternatives under the final `evaluate` tree. Must all signing checks pass in every branch?
7. You now need a fourth, similar command for a new signing-key attribute. Which sample can you author more accurately from scratch? What extra docs would you consult?
8. Name any metadata or provenance that became harder to locate or disappeared in either style.

**Score separately:** (i) ability to explain what the Assessment does, (ii) ability to author a new check, (iii) number of source-definition lookups, and (iv) guessed cardinality/error semantics. Then rank A/B, with two specific reasons. Shorter YAML is not automatically better.

## Sample A — full authored Assessment

```yaml
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
    description: The list of all forward and reverse lookup zones
    collect:
      shell: powershell
      command: Get-DnsServerZone | Where-Object {$_.ZoneType -notin @('Forwarder')
        -and $_.ZoneName -notin @('TrustAnchors') -and (-Not $_.IsAutoCreated)} |
        ForEach-Object {$_.ZoneName}
      error_if_exit_status_not_0: false
      error_if_stderr_exists: false
    require:
      at_least_one_item_exists: true
      every_item_must_match:
        stdout_line:
          no_values_exist: true
          source_comparison:
            is: ''
    report_elements: all
  all-forward-lookup-zones-if-any-integrated-active-directory-test:
    check: All forward lookup zones (if any) are integrated with Active Directory
    inspect: independent.shellcommand
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
    require:
      at_least_one_item_exists: true
      every_item_must_match:
        stdout_line:
          no_values_exist: true
          source_comparison:
            is: ''
    report_elements: all
  all-forward-lookup-zones-dnssec-signed-test:
    check: All forward lookup zones are DNSSEC signed
    inspect: independent.shellcommand
    description: The 'IsSigned' setting for each forward lookup zone
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
    report_elements: all
  all-forward-lookup-zones-have-dns-key-signature-validity-periods-test:
    check: All forward lookup zones have DNS key signature validity periods between
      two days and a week for their zone signing keys
    inspect: independent.shellcommand
    description: The list of DNS key signature validity periods for the zone signing
      keys
    collect:
      shell: powershell
      command:
        variable: command-get-list-dns-key-signature-validity-periods-zone-signing-variable
      error_if_exit_status_not_0: false
      error_if_stderr_exists: false
    all_state_fields_exist: true
    require:
      at_least_one_item_exists: true
      every_item_must_match:
        all_states:
        - stdout_line:
            at_least: 48
        - stdout_line:
            at_most: 168
    report_elements: all
  all-forward-lookup-zones-have-dns-key-signature-validity-periods-2-test:
    check: All forward lookup zones have DNS key signature validity periods between
      two days and a week for their key signing keys
    inspect: independent.shellcommand
    description: The list of DNS key signature validity periods for the key signing
      keys
    collect:
      shell: powershell
      command:
        variable: command-get-list-dns-key-signature-validity-periods-key-signing-variable
      error_if_exit_status_not_0: false
      error_if_stderr_exists: false
    all_state_fields_exist: true
    require:
      at_least_one_item_exists: true
      every_item_must_match:
        all_states:
        - stdout_line:
            at_least: 48
        - stdout_line:
            at_most: 168
    report_elements: all
evaluate:
  any_of:
  - test: dns-server-caching-only-there-no-forward-or-reverse-lookup-test
  - test: all-forward-lookup-zones-if-any-integrated-active-directory-test
  - all_of:
    - test: all-forward-lookup-zones-dnssec-signed-test
    - test: all-forward-lookup-zones-have-dns-key-signature-validity-periods-test
    - test: all-forward-lookup-zones-have-dns-key-signature-validity-periods-2-test
```

## Sample B — full authored Assessment

```yaml
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
    description: The list of all forward and reverse lookup zones
    collect:
      shell: powershell
      command: Get-DnsServerZone | Where-Object {$_.ZoneType -notin @('Forwarder')
        -and $_.ZoneName -notin @('TrustAnchors') -and (-Not $_.IsAutoCreated)} |
        ForEach-Object {$_.ZoneName}
      error_if_exit_status_not_0: false
      error_if_stderr_exists: false
    require:
      at_least_one_item_exists: true
      every_item_must_match:
        stdout_line:
          no_values_exist: true
          source_comparison:
            is: ''
    report_elements: all
  all-forward-lookup-zones-if-any-integrated-active-directory-test:
    check: All forward lookup zones (if any) are integrated with Active Directory
    inspect: independent.shellcommand
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
    require:
      at_least_one_item_exists: true
      every_item_must_match:
        stdout_line:
          no_values_exist: true
          source_comparison:
            is: ''
    report_elements: all
  all-forward-lookup-zones-dnssec-signed-test:
    check: All forward lookup zones are DNSSEC signed
    inspect: independent.shellcommand
    description: The 'IsSigned' setting for each forward lookup zone
    collect:
      shell: powershell
      command:
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
      error_if_exit_status_not_0: false
      error_if_stderr_exists: false
    require:
      at_least_one_item_exists: true
      every_item_must_match:
        stdout_line:
          exactly_one_is: 'True'
    report_elements: all
  all-forward-lookup-zones-have-dns-key-signature-validity-periods-test:
    check: All forward lookup zones have DNS key signature validity periods between
      two days and a week for their zone signing keys
    inspect: independent.shellcommand
    description: The list of DNS key signature validity periods for the zone signing
      keys
    collect:
      shell: powershell
      command:
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
      error_if_exit_status_not_0: false
      error_if_stderr_exists: false
    all_state_fields_exist: true
    require:
      at_least_one_item_exists: true
      every_item_must_match:
        all_states:
        - stdout_line:
            at_least: 48
        - stdout_line:
            at_most: 168
    report_elements: all
  all-forward-lookup-zones-have-dns-key-signature-validity-periods-2-test:
    check: All forward lookup zones have DNS key signature validity periods between
      two days and a week for their key signing keys
    inspect: independent.shellcommand
    description: The list of DNS key signature validity periods for the key signing
      keys
    collect:
      shell: powershell
      command:
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
      error_if_exit_status_not_0: false
      error_if_stderr_exists: false
    all_state_fields_exist: true
    require:
      at_least_one_item_exists: true
      every_item_must_match:
        all_states:
        - stdout_line:
            at_least: 48
        - stdout_line:
            at_most: 168
    report_elements: all
evaluate:
  any_of:
  - test: dns-server-caching-only-there-no-forward-or-reverse-lookup-test
  - test: all-forward-lookup-zones-if-any-integrated-active-directory-test
  - all_of:
    - test: all-forward-lookup-zones-dnssec-signed-test
    - test: all-forward-lookup-zones-have-dns-key-signature-validity-periods-test
    - test: all-forward-lookup-zones-have-dns-key-signature-validity-periods-2-test
```

---

**STOP. Freeze the first-read answers before any context, answer key, machine conversion report or preference from the project author is disclosed.** A reviewer must not be counted as “passed” merely for selecting the design that is shorter or that the project team prefers. No independent review responses have been collected at publication.
