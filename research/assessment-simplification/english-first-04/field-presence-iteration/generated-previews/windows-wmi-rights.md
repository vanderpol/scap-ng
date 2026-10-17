# Auditor preview — WN11-UR-000090 - The "Deny log on through Remote Desktop Services" user right on Windows 11 workstations must be configured to prevent access from highly privileged domain accounts and local accounts on domain systems and unauthenticated access on all systems.

**Machine-generated research explanation from complete parsed YAML.** No live result, new normative policy or scanner-equivalence proof.

**Assessment ID:** `SV-253495.automated` · **Checks:** 7 · **Evaluate leaves:** 8

[Revised full YAML](../windows-wmi-rights.revised.research.yaml) · [Original source YAML](../../canonical-operators/windows-wmi-rights.canonical.research.yaml)

## What is observed?

### Named source `windows-wmi57-object`

**Inspector:** `windows.wmi.query`
**Collection configuration:**

~~~yaml
namespace: root\cimv2
query: SELECT DomainRole FROM win32_computersystem
~~~

### Named source `windows-userright-object`

**Inspector:** `windows.userright`
**Original selector:**

~~~yaml
userright:
  equals: SE_DENY_REMOTE_INTERACTIVE_LOGON_NAME
~~~


## What must exist and match?

### The system is a non-DC domain-joined Windows server or workstation

**Check ID:** `system-non-dc-domain-joined-windows-server-or-workstation-test` · **Inspector:** `windows.wmi.query`

- **Root Item existence:** `at_least_one`
- **Matching root Items:** `all`
- **Named source reference:** `windows-wmi57-object`

**Explicit field, record and State scopes:**

- `require.states`: OR combines whole child expressions, not value membership.
- `require.states.or[0].result`: nested record existence `at_least_one`, matching `all` (not root Items).
- `require.states.or[1].result`: nested record existence `at_least_one`, matching `all` (not root Items).

**Full requirement subtree (candidate wording):**

~~~yaml
items: at_least_one
matching_items: all
states:
  or:
  - result:
      records: at_least_one
      matching_records: all
      domainrole:
        equals: '1'
  - result:
      records: at_least_one
      matching_records: all
      domainrole:
        equals: '3'
~~~

### Deny log on through Remote Desktop Services - Local account

**Check ID:** `deny-log-on-through-remote-desktop-services-local-account-test` · **Inspector:** `windows.userright`

- **Root Item existence:** `at_least_one`
- **Matching root Items:** `at_least_one`
- **Named source reference:** `windows-userright-object`

**Explicit field, record and State scopes:**

- No additional field-presence/record/group policy is explicitly displayed.

**Full requirement subtree (candidate wording):**

~~~yaml
items: at_least_one
matching_items: at_least_one
trustee_name:
  matches_regex: ^(?i)(NT Authority\\)?Local account$
~~~

### Deny log on through Remote Desktop Services - Guests

**Check ID:** `deny-log-on-through-remote-desktop-services-guests-test` · **Inspector:** `windows.userright`

- **Root Item existence:** `at_least_one`
- **Matching root Items:** `at_least_one`
- **Named source reference:** `windows-userright-object`

**Explicit field, record and State scopes:**

- No additional field-presence/record/group policy is explicitly displayed.

**Full requirement subtree (candidate wording):**

~~~yaml
items: at_least_one
matching_items: at_least_one
trustee_name:
  case_insensitive_equals: Guests
~~~

### Deny log on through Remote Desktop Services - Domain Admins

**Check ID:** `deny-log-on-through-remote-desktop-services-domain-admins-test` · **Inspector:** `windows.userright`

- **Root Item existence:** `at_least_one`
- **Matching root Items:** `at_least_one`
- **Named source reference:** `windows-userright-object`

**Explicit field, record and State scopes:**

- No additional field-presence/record/group policy is explicitly displayed.

**Full requirement subtree (candidate wording):**

~~~yaml
items: at_least_one
matching_items: at_least_one
trustee_name:
  matches_regex: ^(?i)(.+\\)?Domain Admins$
~~~

### Deny log on through Remote Desktop Services - Enterprise Admins

**Check ID:** `deny-log-on-through-remote-desktop-services-enterprise-admins-test` · **Inspector:** `windows.userright`

- **Root Item existence:** `at_least_one`
- **Matching root Items:** `at_least_one`
- **Named source reference:** `windows-userright-object`

**Explicit field, record and State scopes:**

- No additional field-presence/record/group policy is explicitly displayed.

**Full requirement subtree (candidate wording):**

~~~yaml
items: at_least_one
matching_items: at_least_one
trustee_name:
  matches_regex: ^(?i)(.+\\)?Enterprise Admins$
~~~

### The system is a standalone Windows server or workstation

**Check ID:** `system-standalone-windows-server-or-workstation-test` · **Inspector:** `windows.wmi.query`

- **Root Item existence:** `at_least_one`
- **Matching root Items:** `all`
- **Named source reference:** `windows-wmi57-object`

**Explicit field, record and State scopes:**

- `require.states`: OR combines whole child expressions, not value membership.
- `require.states.or[0].result`: nested record existence `at_least_one`, matching `all` (not root Items).
- `require.states.or[1].result`: nested record existence `at_least_one`, matching `all` (not root Items).

**Full requirement subtree (candidate wording):**

~~~yaml
items: at_least_one
matching_items: all
states:
  or:
  - result:
      records: at_least_one
      matching_records: all
      domainrole:
        equals: '0'
  - result:
      records: at_least_one
      matching_records: all
      domainrole:
        equals: '2'
~~~

### Deny log on through Remote Desktop Services - Everyone

**Check ID:** `deny-log-on-through-remote-desktop-services-everyone-test` · **Inspector:** `windows.userright`

- **Root Item existence:** `at_least_one`
- **Matching root Items:** `at_least_one`
- **Named source reference:** `windows-userright-object`

**Explicit field, record and State scopes:**

- No additional field-presence/record/group policy is explicitly displayed.

**Full requirement subtree (candidate wording):**

~~~yaml
items: at_least_one
matching_items: at_least_one
trustee_name:
  case_insensitive_equals: Everyone
~~~


## How could the Assessment pass?

The structural AND/OR tree below is read from parsed YAML. It is not procedural IF/ELSE, and no actual outcome is calculated.

- **ANY of these child checks (OR)**:
  - **ALL of these child checks (AND)**:
    - `system-non-dc-domain-joined-windows-server-or-workstation-test` — The system is a non-DC domain-joined Windows server or workstation
    - `deny-log-on-through-remote-desktop-services-local-account-test` — Deny log on through Remote Desktop Services - Local account
    - `deny-log-on-through-remote-desktop-services-guests-test` — Deny log on through Remote Desktop Services - Guests
    - `deny-log-on-through-remote-desktop-services-domain-admins-test` — Deny log on through Remote Desktop Services - Domain Admins
    - `deny-log-on-through-remote-desktop-services-enterprise-admins-test` — Deny log on through Remote Desktop Services - Enterprise Admins
  - **ALL of these child checks (AND)**:
    - `system-standalone-windows-server-or-workstation-test` — The system is a standalone Windows server or workstation
    - `deny-log-on-through-remote-desktop-services-guests-test` — Deny log on through Remote Desktop Services - Guests
  - `deny-log-on-through-remote-desktop-services-everyone-test` — Deny log on through Remote Desktop Services - Everyone

**Evaluate references:** 8 occurrences of 7 named checks, all accounted for.
**Repeated references retained:** `deny-log-on-through-remote-desktop-services-guests-test` ×2

## What remains unverified?

- **No system evidence** was collected or evaluated.
- Missing field, missing root Item, read error and incomplete collection are different.
- Repeated field values, nested WMI records and root Items have separate quantifiers.
- Field-presence and matching-label aliases are research-only; runtime equivalence remains open.
- OVAL AND(False,Error) can be False, while OR(True,Error) can be True.
- For command flags, dependent sources, typing and evidence rules, inspect the complete YAML.

[Generic six-state result ledger](SEMANTIC-BOUNDARY-LEDGER.md).
