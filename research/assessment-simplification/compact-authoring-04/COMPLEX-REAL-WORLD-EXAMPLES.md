# SCAP-NG 0.4 — three substantial real-world Assessment examples

**Technical pre-alpha preview.** These are drawn from the [pinned six-STIG r3 authoring source](https://github.com/vanderpol/scap-ng/releases/tag/v0.4.0-joval-meeting-preview-20261015-r3). Start with the [shorter example-led overview](ASSESSMENT-REVIEW-OVERVIEW.md); use this page to see how one-grammar authoring behaves in **real multi-Test logic and dynamic collections**, not just trivial comparisons.

**Source integrity:** Each fenced block is a **verbatim, contiguous YAML excerpt** from its linked complete Assessment. Metadata and certain declarations are omitted *between* blocks for readability, so **the excerpts are not independently valid Assessment files**. Follow the links for the complete source. The unchanged r3 archive is a **candidate validated as authoring**, not independently compiled or scanner-tested 0.4.

## 1. Windows 11 — seven Tests, domain-role alternatives, and shared collection

[Complete native Assessment — SV-253495](https://github.com/vanderpol/scap-ng-editor-sample-data/blob/main/focused-fixtures/source-backed/authoring/ms_windows_11/assessments/automated/SV-253495.automated.yaml)

**What the Rule asks:** configure the *Deny log on through Remote Desktop Services* user right to prevent unauthorized remote logon. The Test graph distinguishes domain-joined, standalone, and an `Everyone` alternative.

**What the example proves:** multiple Tests using the same `windows.wmi.query` and `windows.userright` Objects; independent record/member requirements; different field and collected-Item cardinalities; and an explicit `any` of `all` branches. The actual shared Object declarations appear after `evaluate` in the linked complete Assessment.

```yaml
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
```

**Slang-inspired improvement:** the author's checks use typed capability fields and local expectations, with `evaluate` expressing the combination instead of distributing criteria references through separate OVAL XML entities. **Remaining friction:** Test and Object capability declarations can repeat; named Test identifiers and relatively long cardinality phrases remain. Do not replace the source Boolean tree with unproven procedural `if/else`: its six-state behavior differs for certain guard outcomes.

## 2. Windows Server DNS — zone discovery, runtime Variables, and a compound acceptance rule

[Complete native Assessment — SV-259345](https://github.com/vanderpol/scap-ng-editor-sample-data/blob/main/focused-fixtures/source-backed/authoring/ms_windows_server_dns/assessments/automated/SV-259345.automated.yaml)

**What the Rule asks:** restrict DNSSEC RRSIG validity periods for the relevant DNS zones. The author must discover zones and query the signing-key periods rather than compare a single fixed scalar.

**Dynamic inputs:** these real local Variables construct commands using the collected forward-lookup-zone names. Replacing them with a guessed literal, one Boolean check, or a synthetic `for_each` is *not* demonstrated to be lossless.

```yaml
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
```

**Five Tests and the final decision:** caching-only and integrated-zone alternatives precede a combined DNSSEC-signed and two-key-period requirement. The distinct `stdout_line` existence/matching requirements include `none_exist`, `only_one_exists_and_matches`, and a two-bound State comparison.

```yaml
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
```

**Slang-inspired improvement:** collection, concrete field comparisons, explicit presence requirements, and `any`/`all` composition are visible in one Assessment. **Remaining friction:** source-faithful command construction is still complicated, and the defined shared `list-all-forward-lookup-zones-object` remains outside this excerpt. A simplified-looking alternative must account for zero zones, unknown/error collection and values emitted per zone.

## 3. Apache 2.4 (UNIX) — configuration discovery and four interdependent checks

[Complete native Assessment — SV-214228](https://github.com/vanderpol/scap-ng-editor-sample-data/blob/main/focused-fixtures/source-backed/authoring/apache_server_2-4_unix_server/assessments/automated/SV-214228.automated.yaml)

**What the Rule asks:** constrain simultaneous session handling using the `KeepAlive` and `MaxKeepAliveRequests` settings across the main Apache configuration and discovered included files.

**Acquisition and Variable dataflow:** these are **three separate fragments** copied from the larger Variables graph. One extracts a discovered installation directory; another builds the config path; another derives a command from the merged set of configuration files. The full Assessment has further prerequisite Variables; they are not elided from the linked source.

```yaml
    apache-base-install-directories-unix-variable:
      title: Apache base install directories (unix)
      kind: local
      datatype: string
      expression:
        regex_capture:
          value:
            values:
              object: gather-unique-apache-http-installation-paths-object
              field: stdout_line
          pattern: (^\/.+\/)httpd|(^\/.+/)apache2
```

```yaml
    filepath-http-conf-file-variable:
      title: Filepath to http conf file
      kind: local
      datatype: string
      expression:
        concat:
        - variable: filepath-httpd-root-variable
        - literal:
            value: /
            datatype: string
        - variable: relative-server-config-file-variable
```

```yaml
    shell-command-check-keepalive-in-httpd-conf-all-include-conf-variable:
      title: shell command to check KeepAlive in httpd.conf and all Include conf files
      kind: local
      datatype: string
      expression:
        concat:
        - literal:
            value: 'grep -iHn ''^\s*KeepAlive'' '
            datatype: string
        - variable: httpd-conf-merged-included-conf-files-from-include-refernces-in-variable
```

**Four real Tests and explicit aggregation:** required primary directives, optional included-file directives, and minimum numerical limits have distinct field requirements. All four Tests must pass.

```yaml
  tests:
    verify-that-keepalive-directive-defined-configured-on-in-httpd-conf-test:
      test_title: Verify that KeepAlive directive is defined, and configured to On in httpd.conf/apache2.conf or included
        conf files
      capability: independent.shellcommand
      object:
        capability: independent.shellcommand
        object_title: Gather all KeepAlive data from httpd and all Include conf files
        collect:
          shell: bash
          command:
            variable: shell-command-check-keepalive-in-httpd-conf-all-include-conf-variable
          pattern: .+
          error_if_exit_status_not_0: false
          error_if_stderr_exists: false
      states:
      - stdout_line:
          require: at_least_one_exists_and_all_match
          matches_regex: \s*KeepAlive On
      reported_elements: all
      collected_items_require: at_least_one_exists_and_all_match
    if-keepalive-directive-defined-in-other-loaded-configuration-files-verify-test:
      test_title: If the KeepAlive directive is defined in other loaded configuration files, verify it is configured
        to On
      capability: independent.shellcommand
      object:
        capability: independent.shellcommand
        object_title: Gather all KeepAlive data from all loaded conf files
        collect:
          shell: bash
          command:
            variable: shell-command-check-keepalive-in-all-loaded-conf-files-variable
          pattern: .+
          error_if_exit_status_not_0: false
          error_if_stderr_exists: false
      states:
      - stdout_line:
          require: may_be_absent_and_all_match
          matches_regex: \s*KeepAlive On
      reported_elements: all
      collected_items_require: at_least_one_exists_and_all_match
    verify-that-maxkeepaliverequests-defined-configured-100-or-greater-httpd-conf-test:
      test_title: Verify that MaxKeepAliveRequests is defined and is configured to 100 or greater httpd.conf/apache2.conf
        or included conf files
      capability: independent.shellcommand
      object:
        capability: independent.shellcommand
        object_title: Gather all MaxKeepAliveRequests data from httpd and all Include conf files
        collect:
          shell: bash
          command:
            variable: shell-command-check-maxkeepaliverequests-in-httpd-conf-all-include-conf-variable
          pattern: MaxKeepAliveRequests (\d+)
          error_if_exit_status_not_0: false
          error_if_stderr_exists: false
      states:
      - subexpression:
          require: at_least_one_exists_and_all_match
          greater_than_or_equal: 100
      reported_elements: all
      collected_items_require: at_least_one_exists_and_all_match
    if-maxkeepaliverequests-directive-defined-in-other-loaded-configuration-files-verify-test:
      test_title: If the MaxKeepAliveRequests directive is defined in other loaded configuration files, verify it
        is configured to 100 or greater
      capability: independent.shellcommand
      object:
        capability: independent.shellcommand
        object_title: Gather all MaxKeepAliveRequests data from all loaded conf files
        collect:
          shell: bash
          command:
            variable: shell-command-check-maxkeepaliverequests-in-all-loaded-conf-files-variable
          pattern: MaxKeepAliveRequests (\d+)
          error_if_exit_status_not_0: false
          error_if_stderr_exists: false
      states:
      - subexpression:
          require: may_be_absent_and_all_match
          greater_than_or_equal: 100
      reported_elements: all
      collected_items_require: at_least_one_exists_and_all_match
  evaluate:
    all:
    - test: verify-that-keepalive-directive-defined-configured-on-in-httpd-conf-test
    - test: if-keepalive-directive-defined-in-other-loaded-configuration-files-verify-test
    - test: verify-that-maxkeepaliverequests-defined-configured-100-or-greater-httpd-conf-test
    - test: if-maxkeepaliverequests-directive-defined-in-other-loaded-configuration-files-verify-test
```

**Slang-inspired improvement:** named, typed checks and local field operators remain visible even in a complex Assessment. **Remaining friction:** dynamic multi-step discovery is not magically reduced to one `resource/select/expect` expression; local Variable graphs and shell commands are substantial here. Reducing or caching collectors is a separate optimization that needs source and runtime proof.

## What to evaluate across all three

| Design question | What the source demonstrates |
| --- | --- |
| Does a Test express its entire expectation? | Named Test titles and co-located native field comparisons, though shared and runtime acquisitions can be elsewhere |
| Can collections be reused? | Shared named Objects in Windows and DNS; collection/Variable reuse in Apache |
| Can an author compose real checks? | Windows nested `any/all`; DNS `any` with `all`; Apache `all` |
| Do cardinalities remain explicit? | Collected Items, field values, and nested Windows record members can require different quantities |
| Is modernization automatically complete? | **No.** Dynamic Variables, repeated capability declarations, title cleanup, and certain potential `for_each`/conditional rewrites remain open |
| Is this SLANG? | **No.** It responds to the schema-constrained, resource-first *authoring goals* described in [Discussion #213](https://github.com/vanderpol/scap-ng/discussions/213#discussioncomment-18935232) without adopting Slang's grammar or assuming its conversion semantics |

**Most useful reviewer feedback:** identify one place where the syntax obscures the collected resource, the expected value, or a decisive reason for the result. Supply an OVAL/STIG source case and expected outcome. We should improve the grammar only when an explicit proof preserves its six-state, collection and evidence meaning. [Grammar/vocabulary #227](https://github.com/vanderpol/scap-ng/issues/227) · [semantics #229](https://github.com/vanderpol/scap-ng/issues/229) · [title guidance #234](https://github.com/vanderpol/scap-ng/issues/234).

