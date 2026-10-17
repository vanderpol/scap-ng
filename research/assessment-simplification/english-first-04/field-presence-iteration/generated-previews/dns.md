# Auditor preview — The validity period for the Resource Record Signatures (RRSIGs) covering a zone's DNSKEY RRSet must be no less than two days and no more than one week.

**Machine-generated research explanation from complete parsed YAML.** No live result, new normative policy or scanner-equivalence proof.

**Assessment ID:** `SV-259345.automated` · **Checks:** 5 · **Evaluate leaves:** 5

[Revised full YAML](../dns.revised.research.yaml) · [Original source YAML](../../canonical-operators/dns.canonical.research.yaml)

## What is observed?

### Named source `list-all-forward-lookup-zones-object`

**Inspector:** `independent.shellcommand`
**Collection configuration:**

~~~yaml
shell: powershell
command: Get-DnsServerZone | Where-Object {$_.ZoneType -notin @('Forwarder') -and
  $_.ZoneName -notin @('TrustAnchors') -and (-Not $_.IsAutoCreated) -and (-Not($_.IsReverseLookupZone))}
  | ForEach-Object {$_.ZoneName}
error_if_exit_status_not_0: false
error_if_stderr_exists: false
~~~


**Variable graph:** 3 declarations (full expressions in source YAML).
- `command-get-issigned-setting-each-forward-lookup-zone-variable`
- `command-get-list-dns-key-signature-validity-periods-zone-signing-variable`
- `command-get-list-dns-key-signature-validity-periods-key-signing-variable`

## What must exist and match?

### DNS server is caching only (there are no forward or reverse lookup zones)

**Check ID:** `dns-server-caching-only-there-no-forward-or-reverse-lookup-test` · **Inspector:** `independent.shellcommand`

- **Root Item existence:** `at_least_one`
- **Matching root Items:** `all`
**Original collect (not reconstructed):**

~~~yaml
shell: powershell
command: Get-DnsServerZone | Where-Object {$_.ZoneType -notin @('Forwarder') -and
  $_.ZoneName -notin @('TrustAnchors') -and (-Not $_.IsAutoCreated)} | ForEach-Object
  {$_.ZoneName}
error_if_exit_status_not_0: false
error_if_stderr_exists: false
~~~


**Explicit field, record and State scopes:**

- No additional field-presence/record/group policy is explicitly displayed.

**Full requirement subtree (candidate wording):**

~~~yaml
items: at_least_one
matching_items: all
stdout_line:
  no_values_exist: true
  source_comparison:
    equals: ''
~~~

### All forward lookup zones (if any) are integrated with Active Directory

**Check ID:** `all-forward-lookup-zones-if-any-integrated-active-directory-test` · **Inspector:** `independent.shellcommand`

- **Root Item existence:** `at_least_one`
- **Matching root Items:** `all`
**Original collect (not reconstructed):**

~~~yaml
shell: powershell
command: Get-DnsServerZone | Where-Object {$_.ZoneType -notin @('Forwarder') -and
  $_.ZoneName -notin @('TrustAnchors') -and (-Not $_.IsAutoCreated) -and -Not($_.IsReverseLookupZone)
  -and (-Not $_.IsDsIntegrated)} | ForEach-Object {$_.ZoneName}
error_if_exit_status_not_0: false
error_if_stderr_exists: false
~~~


**Explicit field, record and State scopes:**

- No additional field-presence/record/group policy is explicitly displayed.

**Full requirement subtree (candidate wording):**

~~~yaml
items: at_least_one
matching_items: all
stdout_line:
  no_values_exist: true
  source_comparison:
    equals: ''
~~~

### All forward lookup zones are DNSSEC signed

**Check ID:** `all-forward-lookup-zones-dnssec-signed-test` · **Inspector:** `independent.shellcommand`

- **Root Item existence:** `at_least_one`
- **Matching root Items:** `all`
**Original collect (not reconstructed):**

~~~yaml
shell: powershell
command:
  variable: command-get-issigned-setting-each-forward-lookup-zone-variable
error_if_exit_status_not_0: false
error_if_stderr_exists: false
~~~


**Explicit field, record and State scopes:**

- No additional field-presence/record/group policy is explicitly displayed.

**Full requirement subtree (candidate wording):**

~~~yaml
items: at_least_one
matching_items: all
stdout_line:
  exactly_one_equals: 'True'
~~~

### All forward lookup zones have DNS key signature validity periods between two days and a week for their zone signing keys

**Check ID:** `all-forward-lookup-zones-have-dns-key-signature-validity-periods-test` · **Inspector:** `independent.shellcommand`

- **Root Item existence:** `at_least_one`
- **Matching root Items:** `all`
**Original collect (not reconstructed):**

~~~yaml
shell: powershell
command:
  variable: command-get-list-dns-key-signature-validity-periods-zone-signing-variable
error_if_exit_status_not_0: false
error_if_stderr_exists: false
~~~


**Explicit field, record and State scopes:**

- `require`: scalar-field policy `required` declared here; candidate lowering is not runtime proven.
- `require.states`: AND combines whole child expressions, not value membership.
- `require.states.and[0].stdout_line`: inherits `required` scalar-field policy if within its scope.
- `require.states.and[1].stdout_line`: inherits `required` scalar-field policy if within its scope.

**Full requirement subtree (candidate wording):**

~~~yaml
items: at_least_one
matching_items: all
field_presence: required
states:
  and:
  - stdout_line:
      greater_than_or_equal: 48
  - stdout_line:
      less_than_or_equal: 168
~~~

### All forward lookup zones have DNS key signature validity periods between two days and a week for their key signing keys

**Check ID:** `all-forward-lookup-zones-have-dns-key-signature-validity-periods-2-test` · **Inspector:** `independent.shellcommand`

- **Root Item existence:** `at_least_one`
- **Matching root Items:** `all`
**Original collect (not reconstructed):**

~~~yaml
shell: powershell
command:
  variable: command-get-list-dns-key-signature-validity-periods-key-signing-variable
error_if_exit_status_not_0: false
error_if_stderr_exists: false
~~~


**Explicit field, record and State scopes:**

- `require`: scalar-field policy `required` declared here; candidate lowering is not runtime proven.
- `require.states`: AND combines whole child expressions, not value membership.
- `require.states.and[0].stdout_line`: inherits `required` scalar-field policy if within its scope.
- `require.states.and[1].stdout_line`: inherits `required` scalar-field policy if within its scope.

**Full requirement subtree (candidate wording):**

~~~yaml
items: at_least_one
matching_items: all
field_presence: required
states:
  and:
  - stdout_line:
      greater_than_or_equal: 48
  - stdout_line:
      less_than_or_equal: 168
~~~


## How could the Assessment pass?

The structural AND/OR tree below is read from parsed YAML. It is not procedural IF/ELSE, and no actual outcome is calculated.

- **ANY of these child checks (OR)**:
  - `dns-server-caching-only-there-no-forward-or-reverse-lookup-test` — DNS server is caching only (there are no forward or reverse lookup zones)
  - `all-forward-lookup-zones-if-any-integrated-active-directory-test` — All forward lookup zones (if any) are integrated with Active Directory
  - **ALL of these child checks (AND)**:
    - `all-forward-lookup-zones-dnssec-signed-test` — All forward lookup zones are DNSSEC signed
    - `all-forward-lookup-zones-have-dns-key-signature-validity-periods-test` — All forward lookup zones have DNS key signature validity periods between two days and a week for their zone signing keys
    - `all-forward-lookup-zones-have-dns-key-signature-validity-periods-2-test` — All forward lookup zones have DNS key signature validity periods between two days and a week for their key signing keys

**Evaluate references:** 5 occurrences of 5 named checks, all accounted for.

## What remains unverified?

- **No system evidence** was collected or evaluated.
- Missing field, missing root Item, read error and incomplete collection are different.
- Repeated field values, nested WMI records and root Items have separate quantifiers.
- Field-presence and matching-label aliases are research-only; runtime equivalence remains open.
- OVAL AND(False,Error) can be False, while OR(True,Error) can be True.
- For command flags, dependent sources, typing and evidence rules, inspect the complete YAML.

[Generic six-state result ledger](SEMANTIC-BOUNDARY-LEDGER.md).
