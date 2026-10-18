# Windows 11 SV-253495 — complete lean third candidate

**18 October 2026 · Research issue [#235](https://github.com/vanderpol/scap-ng/issues/235) / [#227](https://github.com/vanderpol/scap-ng/issues/227). This is NOT valid accepted 0.4 syntax, not executable and not independently round-tripped.** The complete seven-Test candidate below is derived from the [pinned existing 0.4 and complete English-first comparison](FULL-03-win11-rights.md), not invented policy.

## Design hypothesis

**Declare each native collection once, reference it from checks, keep every Item/State/record requirement explicit, and leave the three-branch evaluate graph untouched.**

| Current 0.4 expression | Lean candidate | Evidence still required |
| --- | --- | --- |
| `shared_objects.<id>.capability` | `sources.<id>.inspect` | Explicit referenced native type resolves; no inferred defaults |
| `shared_objects.<id>.select` | `sources.<id>.where` | Same selector semantics and candidate population |
| `tests.<id>.test_title` | `checks.<id>.check` | Original title/provenance preserved |
| `tests.<id>.capability` and `object: <id>` | `checks.<id>.from: <id>` | Compiler must reject missing, ambiguous, wrong-capability source |
| Item `collected_items_require` | **Unchanged** | Item counts stay distinct from record/field counts |
| `states`, `states_match`, nested record/field `require` | **Unchanged** | Whole-State alternatives must not be flattened |
| `evaluate.any/all` | **Unchanged** | Three alternatives remain six-state Boolean, not procedural `if/else` |

The original `object_title: null` fields are deliberately not written in this human candidate. **Exact source AST reversal is unproved** until an explicit, validated metadata preservation rule exists. This omission does not authorize a hidden operational default.

## Full seven-Test candidate (all sources and evaluate)

```yaml
# EXPERIMENT ONLY, unsupported by normative 0.4 schema.
assessment:
  id: SV-253495.automated
  version: 2
  assessment_title: WN11-UR-000090 - The "Deny log on through Remote Desktop Services" user right on Windows 11 workstations
    must be configured to prevent access from highly privileged domain accounts and local accounts on domain systems
    and unauthenticated access on all systems.
  mode: automated
  class: compliance
  purpose: assessment
  specification:
    id: scap-ng.pre-alpha.assessment
    version: 0.4.0
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
      object_title: null  checks:
    system-non-dc-domain-joined-windows-server-or-workstation-test:
      check: The system is a non-DC domain-joined Windows server or workstation
      from: windows-wmi57-object
      states:
      - result:
          record:
            fields:
              domainrole:
                require: at_least_one_exists_and_all_match
                equals: '1'
            require: at_least_one_exists_and_all_match
      - result:
          record:
            fields:
              domainrole:
                require: at_least_one_exists_and_all_match
                equals: '3'
            require: at_least_one_exists_and_all_match
      reported_elements: all
      states_match: any
      collected_items_require: at_least_one_exists_and_all_match
    deny-log-on-through-remote-desktop-services-local-account-test:
      check: Deny log on through Remote Desktop Services - Local account
      from: windows-userright-object
      states:
      - trustee_name:
          require: at_least_one_exists_and_all_match
          matches_regex: ^(?i)(NT Authority\\)?Local account$
      reported_elements: all
      collected_items_require: at_least_one_exists_and_some_match
    deny-log-on-through-remote-desktop-services-guests-test:
      check: Deny log on through Remote Desktop Services - Guests
      from: windows-userright-object
      states:
      - trustee_name:
          require: at_least_one_exists_and_all_match
          case_insensitive_equals: Guests
      reported_elements: all
      collected_items_require: at_least_one_exists_and_some_match
    deny-log-on-through-remote-desktop-services-domain-admins-test:
      check: Deny log on through Remote Desktop Services - Domain Admins
      from: windows-userright-object
      states:
      - trustee_name:
          require: at_least_one_exists_and_all_match
          matches_regex: ^(?i)(.+\\)?Domain Admins$
      reported_elements: all
      collected_items_require: at_least_one_exists_and_some_match
    deny-log-on-through-remote-desktop-services-enterprise-admins-test:
      check: Deny log on through Remote Desktop Services - Enterprise Admins
      from: windows-userright-object
      states:
      - trustee_name:
          require: at_least_one_exists_and_all_match
          matches_regex: ^(?i)(.+\\)?Enterprise Admins$
      reported_elements: all
      collected_items_require: at_least_one_exists_and_some_match
    system-standalone-windows-server-or-workstation-test:
      check: The system is a standalone Windows server or workstation
      from: windows-wmi57-object
      states:
      - result:
          record:
            fields:
              domainrole:
                require: at_least_one_exists_and_all_match
                equals: '0'
            require: at_least_one_exists_and_all_match
      - result:
          record:
            fields:
              domainrole:
                require: at_least_one_exists_and_all_match
                equals: '2'
            require: at_least_one_exists_and_all_match
      reported_elements: all
      states_match: any
      collected_items_require: at_least_one_exists_and_all_match
    deny-log-on-through-remote-desktop-services-everyone-test:
      check: Deny log on through Remote Desktop Services - Everyone
      from: windows-userright-object
      states:
      - trustee_name:
          require: at_least_one_exists_and_all_match
          case_insensitive_equals: Everyone
      reported_elements: all
      collected_items_require: at_least_one_exists_and_some_match
  evaluate:
    any:
    - all:
      - test: system-non-dc-domain-joined-windows-server-or-workstation-test
      - test: deny-log-on-through-remote-desktop-services-local-account-test
      - test: deny-log-on-through-remote-desktop-services-guests-test
      - test: deny-log-on-through-remote-desktop-services-domain-admins-test
      - test: deny-log-on-through-remote-desktop-services-enterprise-admins-test
    - all:
      - test: system-standalone-windows-server-or-workstation-test
      - test: deny-log-on-through-remote-desktop-services-guests-test
    - test: deny-log-on-through-remote-desktop-services-everyone-test

```

## Questions for a first-time auditor

1. Where is the WMI DomainRole query declared? Where is the denied Remote Desktop user-right selected? Can you follow all seven checks to the **two named native sources** without guessing a capability?
2. Can you accurately identify all **three** top-level OR alternatives? Is the Everyone Test dependent on either DomainRole Test?
3. Why is trustee Item requirement `at_least_one_exists_and_some_match` different from the WMI Item rule `at_least_one_exists_and_all_match`? Find the additional nested record/field requirements.
4. Could you author an equivalent Assessment for a different user right without assuming an unstated `from` capability or field-presence default?
5. Which is easier to understand and to write: [current complete 0.4](FULL-03-win11-rights.md), its complete English-first after, or this lean candidate? Identify actual confusion points.

## Constraints and next gate

Seven repeated per-check capability declarations are gone, but **none of the seven real Tests, three OR alternatives or native WMI record requirements have been deleted**. That is exactly the kind of meaningful simplification to test: source reuse without hidden semantics.

**Unproved:** `from` type resolution as the sole check capability declaration, exact structural reversal of omitted null metadata, source matching/error behavior, first-time author comprehension, and original OVAL results. Do not change the accepted schema/converter based on this document. If a reviewer needs the same number of lookup hops or makes more population/record errors, reject the candidate rather than promote a shorter file.
