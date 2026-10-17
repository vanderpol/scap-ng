# 03 · Windows 11 Remote Desktop deny-rights (WMI and multiple alternatives) — complete before and after

**Review-only research. The after version is experimental and is not approved 0.4 syntax or independent OVAL scanner-conformance evidence.**

[Back to all five complete examples](BEFORE-AFTER-REVIEW.md) · [Original pinned source](https://github.com/vanderpol/scap-ng-editor-sample-data/blob/99cbceae8d594c44cb509df95975ac1676a2b44a/focused-fixtures/source-backed/authoring/ms_windows_11/assessments/automated/SV-253495.automated.yaml) · [Full generated research YAML](comparisons/win11-role-rights.research.yaml)

## What changed (and what did not)

- Two named Windows sources remain fully defined: the WMI domain-role query and the user-right selector.
- All seven Tests remain visible and the assessment's three logical alternatives stay separate in `evaluate`.
- The `every_item_must_match` versus `at_least_one_item_matches` wording preserves the distinction between collected Item counts and per-State field matching.

**Authoring question:** Can you tell why the domain-role check requires *whole-record/State* alternatives instead of a single membership comparison?

## Before — complete existing 0.4 Assessment

Full source including metadata, Tests, shared Objects, Variables (where used), source selectors and evaluate tree. Nothing omitted.

```yaml
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
  tests:
    system-non-dc-domain-joined-windows-server-or-workstation-test:
      test_title: The system is a non-DC domain-joined Windows server or workstation
      capability: windows.wmi.query
      object: windows-wmi57-object
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
      test_title: Deny log on through Remote Desktop Services - Local account
      capability: windows.userright
      object: windows-userright-object
      states:
      - trustee_name:
          require: at_least_one_exists_and_all_match
          matches_regex: ^(?i)(NT Authority\\)?Local account$
      reported_elements: all
      collected_items_require: at_least_one_exists_and_some_match
    deny-log-on-through-remote-desktop-services-guests-test:
      test_title: Deny log on through Remote Desktop Services - Guests
      capability: windows.userright
      object: windows-userright-object
      states:
      - trustee_name:
          require: at_least_one_exists_and_all_match
          case_insensitive_equals: Guests
      reported_elements: all
      collected_items_require: at_least_one_exists_and_some_match
    deny-log-on-through-remote-desktop-services-domain-admins-test:
      test_title: Deny log on through Remote Desktop Services - Domain Admins
      capability: windows.userright
      object: windows-userright-object
      states:
      - trustee_name:
          require: at_least_one_exists_and_all_match
          matches_regex: ^(?i)(.+\\)?Domain Admins$
      reported_elements: all
      collected_items_require: at_least_one_exists_and_some_match
    deny-log-on-through-remote-desktop-services-enterprise-admins-test:
      test_title: Deny log on through Remote Desktop Services - Enterprise Admins
      capability: windows.userright
      object: windows-userright-object
      states:
      - trustee_name:
          require: at_least_one_exists_and_all_match
          matches_regex: ^(?i)(.+\\)?Enterprise Admins$
      reported_elements: all
      collected_items_require: at_least_one_exists_and_some_match
    system-standalone-windows-server-or-workstation-test:
      test_title: The system is a standalone Windows server or workstation
      capability: windows.wmi.query
      object: windows-wmi57-object
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
      test_title: Deny log on through Remote Desktop Services - Everyone
      capability: windows.userright
      object: windows-userright-object
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
  shared_objects:
    windows-wmi57-object:
      capability: windows.wmi.query
      object_title: null
      collect:
        namespace: root\cimv2
        query: SELECT DomainRole FROM win32_computersystem
    windows-userright-object:
      capability: windows.userright
      select:
        userright:
          equals: SE_DENY_REMOTE_INTERACTIVE_LOGON_NAME
      object_title: null
```

## After — complete generated English-first research Assessment

Full experimental version, including metadata, named sources, checks, local Variables, requirements and evaluate tree. Nothing omitted.

```yaml
# EXPERIMENT ONLY; reconstructs the pinned Assessment exactly.
# Not normative SCAP-NG v0.4 or independently validated OVAL execution.
metadata:
  id: SV-253495.automated
  version: 2
  assessment_title: WN11-UR-000090 - The "Deny log on through Remote Desktop Services"
    user right on Windows 11 workstations must be configured to prevent access from
    highly privileged domain accounts and local accounts on domain systems and unauthenticated
    access on all systems.
  mode: automated
  class: compliance
  purpose: assessment
  specification:
    id: scap-ng.pre-alpha.assessment
    version: 0.4.0
sources:
  windows-wmi57-object:
    inspect: windows.wmi.query
    description: null
    collect:
      namespace: root\cimv2
      query: SELECT DomainRole FROM win32_computersystem
  windows-userright-object:
    inspect: windows.userright
    description: null
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
    report_elements: all
  deny-log-on-through-remote-desktop-services-local-account-test:
    check: Deny log on through Remote Desktop Services - Local account
    inspect: windows.userright
    from: windows-userright-object
    require:
      at_least_one_item_exists: true
      at_least_one_item_matches:
        trustee_name:
          matches_regex: ^(?i)(NT Authority\\)?Local account$
    report_elements: all
  deny-log-on-through-remote-desktop-services-guests-test:
    check: Deny log on through Remote Desktop Services - Guests
    inspect: windows.userright
    from: windows-userright-object
    require:
      at_least_one_item_exists: true
      at_least_one_item_matches:
        trustee_name:
          equals_ignoring_case: Guests
    report_elements: all
  deny-log-on-through-remote-desktop-services-domain-admins-test:
    check: Deny log on through Remote Desktop Services - Domain Admins
    inspect: windows.userright
    from: windows-userright-object
    require:
      at_least_one_item_exists: true
      at_least_one_item_matches:
        trustee_name:
          matches_regex: ^(?i)(.+\\)?Domain Admins$
    report_elements: all
  deny-log-on-through-remote-desktop-services-enterprise-admins-test:
    check: Deny log on through Remote Desktop Services - Enterprise Admins
    inspect: windows.userright
    from: windows-userright-object
    require:
      at_least_one_item_exists: true
      at_least_one_item_matches:
        trustee_name:
          matches_regex: ^(?i)(.+\\)?Enterprise Admins$
    report_elements: all
  system-standalone-windows-server-or-workstation-test:
    check: The system is a standalone Windows server or workstation
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
                is: '0'
        - result:
            at_least_one_record_exists: true
            every_record:
              domainrole:
                is: '2'
    report_elements: all
  deny-log-on-through-remote-desktop-services-everyone-test:
    check: Deny log on through Remote Desktop Services - Everyone
    inspect: windows.userright
    from: windows-userright-object
    require:
      at_least_one_item_exists: true
      at_least_one_item_matches:
        trustee_name:
          equals_ignoring_case: Everyone
    report_elements: all
evaluate:
  any_of:
  - all_of:
    - test: system-non-dc-domain-joined-windows-server-or-workstation-test
    - test: deny-log-on-through-remote-desktop-services-local-account-test
    - test: deny-log-on-through-remote-desktop-services-guests-test
    - test: deny-log-on-through-remote-desktop-services-domain-admins-test
    - test: deny-log-on-through-remote-desktop-services-enterprise-admins-test
  - all_of:
    - test: system-standalone-windows-server-or-workstation-test
    - test: deny-log-on-through-remote-desktop-services-guests-test
  - test: deny-log-on-through-remote-desktop-services-everyone-test
```

## What to tell us

- Can you trace the complete logic without opening a missing definition?
- Is the after version easier to write from scratch, or merely shorter?
- Where does the vocabulary or nesting remain inconsistent?

**Structural evidence:** [The six-STIG run 38934771985](https://github.com/vanderpol/scap-ng/actions/runs/38934771985) reconstructed the original full Assessment dictionaries using this research representation. This does not establish SCAP 1.4 runtime/evidence equivalence.
