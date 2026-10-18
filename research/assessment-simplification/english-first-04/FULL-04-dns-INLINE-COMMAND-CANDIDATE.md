# DNS SV-259345 — full inline-command authoring candidate

**October 18, 2026 · Research for [#235](https://github.com/vanderpol/scap-ng/issues/235) and [#227](https://github.com/vanderpol/scap-ng/issues/227). NOT an adopted grammar, executable 0.4 Assessment, or scanner parity claim.** The [existing full before/after comparison](FULL-04-dns.md) contains the pinned source-backed original and the earlier English-first research file. This page adds a **complete third authoring candidate**, not an excerpt.

## The limited, testable hypothesis

Each of the 3 command Variables below is referenced **once**, as a check's `collect.command`. In this candidate, the *identical authored expression subtree* replaces that reference at the point of use. Its named Variable declaration is removed; **all other acquisition sources and Variables, shell literals, regex, collection flags, Item/field requirements, IDs and evaluate logic remain intact**.

| Source measure | Before (English-first) | Inline candidate |
| --- | ---: | ---: |
| Named local Variables | 3 | 0 |
| Nonblank/non-comment YAML lines | 184 | 163 |
| Single-use Variable lookups between check and command | 3 | 0 |

Eliminated **single-use names**, not their computations:

- `command-get-issigned-setting-each-forward-lookup-zone-variable`
- `command-get-list-dns-key-signature-validity-periods-zone-signing-variable`
- `command-get-list-dns-key-signature-validity-periods-key-signing-variable`

**Source integrity:** The derivation was mechanically checked for exactly one reference per substituted name, identical expression text and an exact reverse substitution back to the full original English-first YAML. The reverse check **retains original removed Variable declarations as a separate edit recipe**; the standalone candidate does **not** encode their `title`, `kind: local`, or `datatype: string` metadata. Therefore this is **not proven self-contained lossless lowering**, nor proof that `collect.command` today accepts inline `concat` or preserves runtime collection/evidence semantics. An accepted design would need explicit typing, error/completeness/provenance rules and a decision about declaration metadata.

## Complete DNS SV-259345 third candidate

```yaml
# EXPERIMENT ONLY: no 0.4 compiler/schema support is asserted.
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

## First-read questions for security auditors

1. Where is the native collection declared, and where does each command obtain its variable-length input? Can you follow that without reading the original file?
2. What precisely does `concat` mean for zero, one and multiple `stdout_line` values? What is the string/array type of the derived command? **Say unknown if not defined.**
3. What happens when the upstream source reports an error or incomplete data? Does the check still run, fail, become unknown, or have no collected Item? **No behavior may be inferred from shell syntax alone.**
4. Identify the separate Item existence requirement and the field-value matching requirement in each check. Do not conflate a successful command yielding no stdout with a missing command Item.
5. State the complete Assessment's top-level `evaluate` logic. Did inlining accidentally change which checks must pass?
6. Would you prefer this *as source to write and review*, or named command Variables plus editor navigation? Specify at least one place in the YAML where your interpretation changes.

## Explicit limits and next experiment

This is a useful **bounded** authoring reduction of 21 non-comment lines and 3 unnecessary one-hop references, without a new pipeline language. It **does not solve** the remaining 0 named acquisition/Variable stages, or the distinct handling of zone discovery and individual signing commands. Deep nested expressions, repeated commands, unknown upstream error status and string/array interpolation are still real concerns.

Before choosing a standard: independently test human comprehension of this **full** file against the prior full source; define/verify the typed command-expression boundary, item lineage, zero/many/error outcomes and provenance; validate metadata recovery. No normative schema/converter changes or 65-STIG jobs are authorized by this experiment.
