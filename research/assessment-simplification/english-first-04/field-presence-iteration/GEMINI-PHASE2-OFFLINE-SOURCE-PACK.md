# Gemini Phase 2 — complete offline source evidence pack

**SCAP-NG 0.4 research, 17 October 2026.** Supply this document to Gemini **only after preserving its Phase 1 blind predictions**. Gemini previously reported it could not open github.com files; this pack embeds the full *actual source and revised YAML* for five complete Assessments, so web access is unnecessary. It is an evidence pack, **not a new authoring proposal or endorsed answer key**.

**Reviewer task:** Read all 10 full YAML documents below (five original/revised pairs) and compare preserved selectors, Objects, Variables, Sets, foreach, checks, field/item/record quantifiers, collection error flags and final evaluate expression. For each difference specify: exact source-equivalent syntax change, unclear or unproved semantic equivalence, real source regression, or insufficient evidence. Identify prior incorrect blind guesses and update predictions **without overwriting the blind answers**. Validate that the documents represent whole Assessments, not just display excerpts. Do NOT invent collectors or assume six-state results from two-valued examples.

**Source URLs** originate in the public main branch of https://github.com/vanderpol/scap-ng . If the live repo could not be loaded, use the verbatim YAML here instead. The exact source-text reversal has been checked for each of these five pairs by [GitHub CI run 39050496910](https://github.com/vanderpol/scap-ng/actions/runs/39050496910), but that alone does **not** prove OVAL scanner result/evidence parity.

## RHEL 9 /home nosuid

### Original pinned canonical research Assessment

[GitHub file](https://github.com/vanderpol/scap-ng/blob/main/research/assessment-simplification/english-first-04/canonical-operators/linux-home.canonical.research.yaml)

```yaml
# RESEARCH ONLY — not normative 0.4, runtime/evidence parity not proven
metadata:
  id: ng.shared.home-is-mounted-with-the-nosuid-option
  version: 1
  assessment_title: Linux must prevent files with the setuid and setgid bit set from being executed on file systems
    that contain user home directories.
  mode: automated
  class: compliance
  purpose: assessment
  specification:
    id: scap-ng.pre-alpha.assessment
    version: 0.4.0
sources: {}
checks:
  home-mounted-nosuid-option-test:
    check: /home is mounted with the nosuid option.
    inspect: linux.partition
    description: null
    where:
      mount_point:
        matches_regex: .*\/home
    require:
      items: at_least_one
      match: all
      mount_options:
        at_least_one_value_equals: nosuid
    report_elements: all
evaluate:
  test: home-mounted-nosuid-option-test
```

### Revised readability candidate

[GitHub file](https://github.com/vanderpol/scap-ng/blob/main/research/assessment-simplification/english-first-04/field-presence-iteration/linux-home.revised.research.yaml)

```yaml
# RESEARCH ONLY — not normative 0.4, runtime/evidence parity not proven
metadata:
  id: ng.shared.home-is-mounted-with-the-nosuid-option
  version: 1
  assessment_title: Linux must prevent files with the setuid and setgid bit set from being executed on file systems
    that contain user home directories.
  mode: automated
  class: compliance
  purpose: assessment
  specification:
    id: scap-ng.pre-alpha.assessment
    version: 0.4.0
sources: {}
checks:
  home-mounted-nosuid-option-test:
    check: /home is mounted with the nosuid option.
    inspect: linux.partition
    description: null
    where:
      mount_point:
        matches_regex: .*\/home
    require:
      items: at_least_one
      matching_items: all
      mount_options:
        at_least_one_value_equals: nosuid
    report_elements: all
evaluate:
  test: home-mounted-nosuid-option-test
```

## Windows 11 WMI and deny-remote-logon user rights

### Original pinned canonical research Assessment

[GitHub file](https://github.com/vanderpol/scap-ng/blob/main/research/assessment-simplification/english-first-04/canonical-operators/windows-wmi-rights.canonical.research.yaml)

```yaml
# RESEARCH ONLY — not normative 0.4, runtime/evidence parity not proven
metadata:
  id: SV-253495.automated
  version: 2
  assessment_title: WN11-UR-000090 - The "Deny log on through Remote Desktop Services" user right on Windows 11
    workstations must be configured to prevent access from highly privileged domain accounts and local accounts
    on domain systems and unauthenticated access on all systems.
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
      items: at_least_one
      match: all
      states:
        or:
        - result:
            records: at_least_one
            match: all
            domainrole:
              equals: '1'
        - result:
            records: at_least_one
            match: all
            domainrole:
              equals: '3'
    report_elements: all
  deny-log-on-through-remote-desktop-services-local-account-test:
    check: Deny log on through Remote Desktop Services - Local account
    inspect: windows.userright
    from: windows-userright-object
    require:
      items: at_least_one
      match: at_least_one
      trustee_name:
        matches_regex: ^(?i)(NT Authority\\)?Local account$
    report_elements: all
  deny-log-on-through-remote-desktop-services-guests-test:
    check: Deny log on through Remote Desktop Services - Guests
    inspect: windows.userright
    from: windows-userright-object
    require:
      items: at_least_one
      match: at_least_one
      trustee_name:
        case_insensitive_equals: Guests
    report_elements: all
  deny-log-on-through-remote-desktop-services-domain-admins-test:
    check: Deny log on through Remote Desktop Services - Domain Admins
    inspect: windows.userright
    from: windows-userright-object
    require:
      items: at_least_one
      match: at_least_one
      trustee_name:
        matches_regex: ^(?i)(.+\\)?Domain Admins$
    report_elements: all
  deny-log-on-through-remote-desktop-services-enterprise-admins-test:
    check: Deny log on through Remote Desktop Services - Enterprise Admins
    inspect: windows.userright
    from: windows-userright-object
    require:
      items: at_least_one
      match: at_least_one
      trustee_name:
        matches_regex: ^(?i)(.+\\)?Enterprise Admins$
    report_elements: all
  system-standalone-windows-server-or-workstation-test:
    check: The system is a standalone Windows server or workstation
    inspect: windows.wmi.query
    from: windows-wmi57-object
    require:
      items: at_least_one
      match: all
      states:
        or:
        - result:
            records: at_least_one
            match: all
            domainrole:
              equals: '0'
        - result:
            records: at_least_one
            match: all
            domainrole:
              equals: '2'
    report_elements: all
  deny-log-on-through-remote-desktop-services-everyone-test:
    check: Deny log on through Remote Desktop Services - Everyone
    inspect: windows.userright
    from: windows-userright-object
    require:
      items: at_least_one
      match: at_least_one
      trustee_name:
        case_insensitive_equals: Everyone
    report_elements: all
evaluate:
  or:
  - and:
    - test: system-non-dc-domain-joined-windows-server-or-workstation-test
    - test: deny-log-on-through-remote-desktop-services-local-account-test
    - test: deny-log-on-through-remote-desktop-services-guests-test
    - test: deny-log-on-through-remote-desktop-services-domain-admins-test
    - test: deny-log-on-through-remote-desktop-services-enterprise-admins-test
  - and:
    - test: system-standalone-windows-server-or-workstation-test
    - test: deny-log-on-through-remote-desktop-services-guests-test
  - test: deny-log-on-through-remote-desktop-services-everyone-test
```

### Revised readability candidate

[GitHub file](https://github.com/vanderpol/scap-ng/blob/main/research/assessment-simplification/english-first-04/field-presence-iteration/windows-wmi-rights.revised.research.yaml)

```yaml
# RESEARCH ONLY — not normative 0.4, runtime/evidence parity not proven
metadata:
  id: SV-253495.automated
  version: 2
  assessment_title: WN11-UR-000090 - The "Deny log on through Remote Desktop Services" user right on Windows 11
    workstations must be configured to prevent access from highly privileged domain accounts and local accounts
    on domain systems and unauthenticated access on all systems.
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
    report_elements: all
  deny-log-on-through-remote-desktop-services-local-account-test:
    check: Deny log on through Remote Desktop Services - Local account
    inspect: windows.userright
    from: windows-userright-object
    require:
      items: at_least_one
      matching_items: at_least_one
      trustee_name:
        matches_regex: ^(?i)(NT Authority\\)?Local account$
    report_elements: all
  deny-log-on-through-remote-desktop-services-guests-test:
    check: Deny log on through Remote Desktop Services - Guests
    inspect: windows.userright
    from: windows-userright-object
    require:
      items: at_least_one
      matching_items: at_least_one
      trustee_name:
        case_insensitive_equals: Guests
    report_elements: all
  deny-log-on-through-remote-desktop-services-domain-admins-test:
    check: Deny log on through Remote Desktop Services - Domain Admins
    inspect: windows.userright
    from: windows-userright-object
    require:
      items: at_least_one
      matching_items: at_least_one
      trustee_name:
        matches_regex: ^(?i)(.+\\)?Domain Admins$
    report_elements: all
  deny-log-on-through-remote-desktop-services-enterprise-admins-test:
    check: Deny log on through Remote Desktop Services - Enterprise Admins
    inspect: windows.userright
    from: windows-userright-object
    require:
      items: at_least_one
      matching_items: at_least_one
      trustee_name:
        matches_regex: ^(?i)(.+\\)?Enterprise Admins$
    report_elements: all
  system-standalone-windows-server-or-workstation-test:
    check: The system is a standalone Windows server or workstation
    inspect: windows.wmi.query
    from: windows-wmi57-object
    require:
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
    report_elements: all
  deny-log-on-through-remote-desktop-services-everyone-test:
    check: Deny log on through Remote Desktop Services - Everyone
    inspect: windows.userright
    from: windows-userright-object
    require:
      items: at_least_one
      matching_items: at_least_one
      trustee_name:
        case_insensitive_equals: Everyone
    report_elements: all
evaluate:
  or:
  - and:
    - test: system-non-dc-domain-joined-windows-server-or-workstation-test
    - test: deny-log-on-through-remote-desktop-services-local-account-test
    - test: deny-log-on-through-remote-desktop-services-guests-test
    - test: deny-log-on-through-remote-desktop-services-domain-admins-test
    - test: deny-log-on-through-remote-desktop-services-enterprise-admins-test
  - and:
    - test: system-standalone-windows-server-or-workstation-test
    - test: deny-log-on-through-remote-desktop-services-guests-test
  - test: deny-log-on-through-remote-desktop-services-everyone-test
```

## Linux account-derived initialization-file permissions

### Original pinned canonical research Assessment

[GitHub file](https://github.com/vanderpol/scap-ng/blob/main/research/assessment-simplification/english-first-04/canonical-operators/linux-files.canonical.research.yaml)

```yaml
# RESEARCH ONLY — not normative 0.4, runtime/evidence parity not proven
metadata:
  id: ng.shared.linux-local-initialization-files-must-have-mode-0740-or-less-permissive
  version: 1
  assessment_title: Linux local initialization files must have mode 0740 or less permissive.
  mode: automated
  class: compliance
  purpose: assessment
  specification:
    id: scap-ng.pre-alpha.assessment
    version: 0.4.0
sources:
  users-username-object:
    inspect: unix.password
    description: Users with an username
    where:
      username:
        matches_regex: '[\w]+'
  only-non-system-users-uid-999-home-dirs-excluding-root-object:
    inspect: unix.password
    description: only non-system users (uid>999) home-dirs excluding root directory
    difference:
    - from: users-username-object
      exclude_if:
      - user_id:
          less_than: 1000
      - home_dir:
          is: /
  only-root-users-uid-0-home-dirs-excluding-root-directory-object:
    inspect: unix.password
    description: only root users (uid=0) home-dirs excluding root directory
    difference:
    - from: users-username-object
      exclude_if:
      - user_id:
          greater_than: 0
      - home_dir:
          is: /
checks:
  local-initialization-files-non-system-users-have-mode-0740-or-test:
    check: Local initialization files for non-system users have mode 0740 or less permissive.
    inspect: unix.file
    gather:
      description: local initialization files of non-system users.
      union:
      - from:
          inspect: unix.file
          description: local initialization files of non-system users.
          where:
            directory:
              from: user.home_dir
            name:
              matches_regex: ^\.[^\s\.]+
          filesystem: all
          traversal:
            max_depth: 1
            recurse: symlinks
          for_each_source:
            item: user
            in: only-non-system-users-uid-999-home-dirs-excluding-root-object
        exclude_if:
        - type:
            is: directory
    require:
      items: if_present
      match: all
      fields:
        and:
        - setuid:
            equals: false
        - setgid:
            equals: false
        - sticky:
            equals: false
        - group_write:
            equals: false
        - group_execute:
            equals: false
        - other_read:
            equals: false
        - other_write:
            equals: false
        - other_execute:
            equals: false
        presence: all
    report_elements: all
  local-initialization-files-root-have-mode-0740-or-less-permissive-test:
    check: Local initialization files for root have mode 0740 or less permissive.
    inspect: unix.file
    gather:
      description: local initialization files of root user.
      union:
      - from:
          inspect: unix.file
          description: local initialization files of root user.
          where:
            directory:
              from: user.home_dir
            name:
              matches_regex: ^\.[^\s\.]+
          filesystem: all
          traversal:
            max_depth: 1
            recurse: symlinks
          for_each_source:
            item: user
            in: only-root-users-uid-0-home-dirs-excluding-root-directory-object
        exclude_if:
        - type:
            is: directory
    require:
      items: at_least_one
      match: all
      fields:
        and:
        - setuid:
            equals: false
        - setgid:
            equals: false
        - sticky:
            equals: false
        - group_write:
            equals: false
        - group_execute:
            equals: false
        - other_read:
            equals: false
        - other_write:
            equals: false
        - other_execute:
            equals: false
        presence: all
    report_elements: all
evaluate:
  and:
  - test: local-initialization-files-non-system-users-have-mode-0740-or-test
  - test: local-initialization-files-root-have-mode-0740-or-less-permissive-test
```

### Revised readability candidate

[GitHub file](https://github.com/vanderpol/scap-ng/blob/main/research/assessment-simplification/english-first-04/field-presence-iteration/linux-files.revised.research.yaml)

```yaml
# RESEARCH ONLY — not normative 0.4, runtime/evidence parity not proven
metadata:
  id: ng.shared.linux-local-initialization-files-must-have-mode-0740-or-less-permissive
  version: 1
  assessment_title: Linux local initialization files must have mode 0740 or less permissive.
  mode: automated
  class: compliance
  purpose: assessment
  specification:
    id: scap-ng.pre-alpha.assessment
    version: 0.4.0
sources:
  users-username-object:
    inspect: unix.password
    description: Users with an username
    where:
      username:
        matches_regex: '[\w]+'
  only-non-system-users-uid-999-home-dirs-excluding-root-object:
    inspect: unix.password
    description: only non-system users (uid>999) home-dirs excluding root directory
    difference:
    - from: users-username-object
      exclude_if:
      - user_id:
          less_than: 1000
      - home_dir:
          is: /
  only-root-users-uid-0-home-dirs-excluding-root-directory-object:
    inspect: unix.password
    description: only root users (uid=0) home-dirs excluding root directory
    difference:
    - from: users-username-object
      exclude_if:
      - user_id:
          greater_than: 0
      - home_dir:
          is: /
checks:
  local-initialization-files-non-system-users-have-mode-0740-or-test:
    check: Local initialization files for non-system users have mode 0740 or less permissive.
    inspect: unix.file
    gather:
      description: local initialization files of non-system users.
      union:
      - from:
          inspect: unix.file
          description: local initialization files of non-system users.
          where:
            directory:
              from: user.home_dir
            name:
              matches_regex: ^\.[^\s\.]+
          filesystem: all
          traversal:
            max_depth: 1
            recurse: symlinks
          for_each_source:
            item: user
            in: only-non-system-users-uid-999-home-dirs-excluding-root-object
        exclude_if:
        - type:
            is: directory
    require:
      items: if_present
      matching_items: all
      field_presence: required
      fields:
        and:
        - setuid:
            equals: false
        - setgid:
            equals: false
        - sticky:
            equals: false
        - group_write:
            equals: false
        - group_execute:
            equals: false
        - other_read:
            equals: false
        - other_write:
            equals: false
        - other_execute:
            equals: false
    report_elements: all
  local-initialization-files-root-have-mode-0740-or-less-permissive-test:
    check: Local initialization files for root have mode 0740 or less permissive.
    inspect: unix.file
    gather:
      description: local initialization files of root user.
      union:
      - from:
          inspect: unix.file
          description: local initialization files of root user.
          where:
            directory:
              from: user.home_dir
            name:
              matches_regex: ^\.[^\s\.]+
          filesystem: all
          traversal:
            max_depth: 1
            recurse: symlinks
          for_each_source:
            item: user
            in: only-root-users-uid-0-home-dirs-excluding-root-directory-object
        exclude_if:
        - type:
            is: directory
    require:
      items: at_least_one
      matching_items: all
      field_presence: required
      fields:
        and:
        - setuid:
            equals: false
        - setgid:
            equals: false
        - sticky:
            equals: false
        - group_write:
            equals: false
        - group_execute:
            equals: false
        - other_read:
            equals: false
        - other_write:
            equals: false
        - other_execute:
            equals: false
    report_elements: all
evaluate:
  and:
  - test: local-initialization-files-non-system-users-have-mode-0740-or-test
  - test: local-initialization-files-root-have-mode-0740-or-less-permissive-test
```

## Apache KeepAlive and MaxKeepAliveRequests

### Original pinned canonical research Assessment

[GitHub file](https://github.com/vanderpol/scap-ng/blob/main/research/assessment-simplification/english-first-04/canonical-operators/apache.canonical.research.yaml)

```yaml
# RESEARCH ONLY — not normative 0.4, runtime/evidence parity not proven
metadata:
  id: SV-214228.automated
  version: 2
  assessment_title: The Apache web server must limit the number of allowed simultaneous session requests.
  mode: automated
  class: compliance
  purpose: assessment
  specification:
    id: scap-ng.pre-alpha.assessment
    version: 0.4.0
  variables:
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
    httpd-root-apachectl-v-variable:
      title: httpd_root to apachectl -V
      kind: local
      datatype: string
      expression:
        concat:
        - variable: apache-base-install-directories-unix-variable
        - literal:
            value: apachectl -V | grep -i 'httpd_root'
            datatype: string
    filepath-httpd-root-variable:
      title: Filepath to HTTPD_ROOT
      kind: local
      datatype: string
      expression:
        regex_capture:
          value:
            values:
              object:
                capability: independent.shellcommand
                object_title: Gather HTTPD_ROOT files via apachectl
                collect:
                  shell: bash
                  command:
                    variable: httpd-root-apachectl-v-variable
                  pattern: HTTPD_ROOT
                  error_if_exit_status_not_0: false
                  error_if_stderr_exists: false
              field: stdout_line
          pattern: ' -D HTTPD_ROOT="(.+)"'
    server-config-file-apachectl-v-variable:
      title: server_config_file to apachectl -V
      kind: local
      datatype: string
      expression:
        concat:
        - variable: apache-base-install-directories-unix-variable
        - literal:
            value: apachectl -V | grep -i 'server_config_file'
            datatype: string
    relative-server-config-file-variable:
      title: relative to SERVER_CONFIG_FILE
      kind: local
      datatype: string
      expression:
        regex_capture:
          value:
            values:
              object:
                capability: independent.shellcommand
                object_title: Gather SERVER_CONFIG_FILE files via apachectl
                collect:
                  shell: bash
                  command:
                    variable: server-config-file-apachectl-v-variable
                  pattern: SERVER_CONFIG_FILE
                  error_if_exit_status_not_0: false
                  error_if_stderr_exists: false
              field: stdout_line
          pattern: ' -D SERVER_CONFIG_FILE="(.+)"'
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
    shell-command-check-all-include-include-optional-files-variable:
      title: shell command to check for all Include and Include Optional files
      kind: local
      datatype: string
      expression:
        concat:
        - literal:
            value: 'grep -iEHn ''^\s*Include\s+|^\s*IncludeOptional\s+'' '
            datatype: string
        - variable: filepath-http-conf-file-variable
    all-included-conf-files-from-include-refernces-in-httd-conf-variable:
      title: All included conf files from Include refernces in httd.conf
      kind: local
      datatype: string
      expression:
        concat:
        - variable: filepath-httpd-root-variable
        - literal:
            value: /
            datatype: string
        - regex_capture:
            value:
              values:
                object:
                  capability: independent.shellcommand
                  object_title: Gather Include statements from httpd.conf
                  collect:
                    shell: bash
                    command:
                      variable: shell-command-check-all-include-include-optional-files-variable
                    pattern: \S+
                    error_if_exit_status_not_0: false
                    error_if_stderr_exists: false
                field: stdout_line
            pattern: \S+\s+(\S+)\s*
    merged-included-conf-files-from-include-refernces-in-httd-conf-variable:
      title: merged included conf files from Include refernces in httd.conf
      kind: local
      datatype: string
      expression:
        merge:
          values:
            variable: all-included-conf-files-from-include-refernces-in-httd-conf-variable
          delimiter: ' '
          sort: document
          order: ascending
    httpd-conf-merged-included-conf-files-from-include-refernces-in-variable:
      title: httpd.conf and merged included conf files from Include refernces in httd.conf
      kind: local
      datatype: string
      expression:
        concat:
        - variable: filepath-http-conf-file-variable
        - literal:
            value: ' '
            datatype: string
        - variable: merged-included-conf-files-from-include-refernces-in-httd-conf-variable
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
    apache-path-httpd-or-apache2-variable:
      title: Apache path to httpd or apache2
      kind: local
      datatype: string
      expression:
        regex_capture:
          value:
            values:
              object: gather-unique-apache-http-installation-paths-object
              field: stdout_line
          pattern: '(^\/.+\/httpd|^\/.+\/apache2) '
    command-gather-httpd-apache2-list-all-loaded-configuration-files-variable:
      title: command to gather httpd/apache2 list of all loaded configuration files
      kind: local
      datatype: string
      expression:
        concat:
        - variable: apache-path-httpd-or-apache2-variable
        - literal:
            value: ' -t -D DUMP_INCLUDES'
            datatype: string
    all-loaded-configuration-filepaths-variable:
      title: All loaded configuration filepaths
      kind: local
      datatype: string
      expression:
        unique:
          regex_capture:
            value:
              values:
                object:
                  capability: independent.shellcommand
                  object_title: Gather all loaded config files
                  collect:
                    shell: bash
                    command:
                      variable: command-gather-httpd-apache2-list-all-loaded-configuration-files-variable
                    pattern: ' \('
                    error_if_exit_status_not_0: false
                    error_if_stderr_exists: false
                field: stdout_line
            pattern: \(.*\) (/.*)
    merged-list-all-loaded-config-files-variable:
      title: Merged list of all loaded config files
      kind: local
      datatype: string
      expression:
        merge:
          values:
            variable: all-loaded-configuration-filepaths-variable
          delimiter: ' '
          sort: document
          order: ascending
    shell-command-check-keepalive-in-all-loaded-conf-files-variable:
      title: shell command to check KeepAlive in all loaded conf files
      kind: local
      datatype: string
      expression:
        concat:
        - literal:
            value: 'grep -iHn ''^\s*KeepAlive'' '
            datatype: string
        - variable: merged-list-all-loaded-config-files-variable
    shell-command-check-maxkeepaliverequests-in-httpd-conf-all-include-conf-variable:
      title: shell command to check MaxKeepAliveRequests in httpd.conf and all Include conf files
      kind: local
      datatype: string
      expression:
        concat:
        - literal:
            value: 'grep -iHn ''^\s*MaxKeepAliveRequests'' '
            datatype: string
        - variable: httpd-conf-merged-included-conf-files-from-include-refernces-in-variable
    shell-command-check-maxkeepaliverequests-in-all-loaded-conf-files-variable:
      title: shell command to check MaxKeepAliveRequests in all loaded conf files
      kind: local
      datatype: string
      expression:
        concat:
        - literal:
            value: 'grep -iHn ''^\s*MaxKeepAliveRequests'' '
            datatype: string
        - variable: merged-list-all-loaded-config-files-variable
sources:
  gather-unique-apache-http-installation-paths-object:
    inspect: independent.shellcommand
    description: Gather unique apache http installation paths
    collect:
      shell: bash
      command: ps -e -o command --no-headers | grep -e httpd -e apache2 | sort | uniq
      pattern: ^\/\S+(\/httpd|\/apache2)\s*
      error_if_exit_status_not_0: false
      error_if_stderr_exists: false
checks:
  verify-that-keepalive-directive-defined-configured-on-in-httpd-conf-test:
    check: Verify that KeepAlive directive is defined, and configured to On in httpd.conf/apache2.conf or included
      conf files
    inspect: independent.shellcommand
    description: Gather all KeepAlive data from httpd and all Include conf files
    collect:
      shell: bash
      command:
        variable: shell-command-check-keepalive-in-httpd-conf-all-include-conf-variable
      pattern: .+
      error_if_exit_status_not_0: false
      error_if_stderr_exists: false
    require:
      items: at_least_one
      match: all
      stdout_line:
        matches_regex: \s*KeepAlive On
    report_elements: all
  if-keepalive-directive-defined-in-other-loaded-configuration-files-verify-test:
    check: If the KeepAlive directive is defined in other loaded configuration files, verify it is configured to
      On
    inspect: independent.shellcommand
    description: Gather all KeepAlive data from all loaded conf files
    collect:
      shell: bash
      command:
        variable: shell-command-check-keepalive-in-all-loaded-conf-files-variable
      pattern: .+
      error_if_exit_status_not_0: false
      error_if_stderr_exists: false
    require:
      items: at_least_one
      match: all
      stdout_line:
        when_present_matches_regex: \s*KeepAlive On
    report_elements: all
  verify-that-maxkeepaliverequests-defined-configured-100-or-greater-httpd-conf-test:
    check: Verify that MaxKeepAliveRequests is defined and is configured to 100 or greater httpd.conf/apache2.conf
      or included conf files
    inspect: independent.shellcommand
    description: Gather all MaxKeepAliveRequests data from httpd and all Include conf files
    collect:
      shell: bash
      command:
        variable: shell-command-check-maxkeepaliverequests-in-httpd-conf-all-include-conf-variable
      pattern: MaxKeepAliveRequests (\d+)
      error_if_exit_status_not_0: false
      error_if_stderr_exists: false
    require:
      items: at_least_one
      match: all
      subexpression:
        greater_than_or_equal: 100
    report_elements: all
  if-maxkeepaliverequests-directive-defined-in-other-loaded-configuration-files-verify-test:
    check: If the MaxKeepAliveRequests directive is defined in other loaded configuration files, verify it is configured
      to 100 or greater
    inspect: independent.shellcommand
    description: Gather all MaxKeepAliveRequests data from all loaded conf files
    collect:
      shell: bash
      command:
        variable: shell-command-check-maxkeepaliverequests-in-all-loaded-conf-files-variable
      pattern: MaxKeepAliveRequests (\d+)
      error_if_exit_status_not_0: false
      error_if_stderr_exists: false
    require:
      items: at_least_one
      match: all
      subexpression:
        when_present_greater_than_or_equal: 100
    report_elements: all
evaluate:
  and:
  - test: verify-that-keepalive-directive-defined-configured-on-in-httpd-conf-test
  - test: if-keepalive-directive-defined-in-other-loaded-configuration-files-verify-test
  - test: verify-that-maxkeepaliverequests-defined-configured-100-or-greater-httpd-conf-test
  - test: if-maxkeepaliverequests-directive-defined-in-other-loaded-configuration-files-verify-test
```

### Revised readability candidate

[GitHub file](https://github.com/vanderpol/scap-ng/blob/main/research/assessment-simplification/english-first-04/field-presence-iteration/apache.revised.research.yaml)

```yaml
# RESEARCH ONLY — not normative 0.4, runtime/evidence parity not proven
metadata:
  id: SV-214228.automated
  version: 2
  assessment_title: The Apache web server must limit the number of allowed simultaneous session requests.
  mode: automated
  class: compliance
  purpose: assessment
  specification:
    id: scap-ng.pre-alpha.assessment
    version: 0.4.0
  variables:
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
    httpd-root-apachectl-v-variable:
      title: httpd_root to apachectl -V
      kind: local
      datatype: string
      expression:
        concat:
        - variable: apache-base-install-directories-unix-variable
        - literal:
            value: apachectl -V | grep -i 'httpd_root'
            datatype: string
    filepath-httpd-root-variable:
      title: Filepath to HTTPD_ROOT
      kind: local
      datatype: string
      expression:
        regex_capture:
          value:
            values:
              object:
                capability: independent.shellcommand
                object_title: Gather HTTPD_ROOT files via apachectl
                collect:
                  shell: bash
                  command:
                    variable: httpd-root-apachectl-v-variable
                  pattern: HTTPD_ROOT
                  error_if_exit_status_not_0: false
                  error_if_stderr_exists: false
              field: stdout_line
          pattern: ' -D HTTPD_ROOT="(.+)"'
    server-config-file-apachectl-v-variable:
      title: server_config_file to apachectl -V
      kind: local
      datatype: string
      expression:
        concat:
        - variable: apache-base-install-directories-unix-variable
        - literal:
            value: apachectl -V | grep -i 'server_config_file'
            datatype: string
    relative-server-config-file-variable:
      title: relative to SERVER_CONFIG_FILE
      kind: local
      datatype: string
      expression:
        regex_capture:
          value:
            values:
              object:
                capability: independent.shellcommand
                object_title: Gather SERVER_CONFIG_FILE files via apachectl
                collect:
                  shell: bash
                  command:
                    variable: server-config-file-apachectl-v-variable
                  pattern: SERVER_CONFIG_FILE
                  error_if_exit_status_not_0: false
                  error_if_stderr_exists: false
              field: stdout_line
          pattern: ' -D SERVER_CONFIG_FILE="(.+)"'
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
    shell-command-check-all-include-include-optional-files-variable:
      title: shell command to check for all Include and Include Optional files
      kind: local
      datatype: string
      expression:
        concat:
        - literal:
            value: 'grep -iEHn ''^\s*Include\s+|^\s*IncludeOptional\s+'' '
            datatype: string
        - variable: filepath-http-conf-file-variable
    all-included-conf-files-from-include-refernces-in-httd-conf-variable:
      title: All included conf files from Include refernces in httd.conf
      kind: local
      datatype: string
      expression:
        concat:
        - variable: filepath-httpd-root-variable
        - literal:
            value: /
            datatype: string
        - regex_capture:
            value:
              values:
                object:
                  capability: independent.shellcommand
                  object_title: Gather Include statements from httpd.conf
                  collect:
                    shell: bash
                    command:
                      variable: shell-command-check-all-include-include-optional-files-variable
                    pattern: \S+
                    error_if_exit_status_not_0: false
                    error_if_stderr_exists: false
                field: stdout_line
            pattern: \S+\s+(\S+)\s*
    merged-included-conf-files-from-include-refernces-in-httd-conf-variable:
      title: merged included conf files from Include refernces in httd.conf
      kind: local
      datatype: string
      expression:
        merge:
          values:
            variable: all-included-conf-files-from-include-refernces-in-httd-conf-variable
          delimiter: ' '
          sort: document
          order: ascending
    httpd-conf-merged-included-conf-files-from-include-refernces-in-variable:
      title: httpd.conf and merged included conf files from Include refernces in httd.conf
      kind: local
      datatype: string
      expression:
        concat:
        - variable: filepath-http-conf-file-variable
        - literal:
            value: ' '
            datatype: string
        - variable: merged-included-conf-files-from-include-refernces-in-httd-conf-variable
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
    apache-path-httpd-or-apache2-variable:
      title: Apache path to httpd or apache2
      kind: local
      datatype: string
      expression:
        regex_capture:
          value:
            values:
              object: gather-unique-apache-http-installation-paths-object
              field: stdout_line
          pattern: '(^\/.+\/httpd|^\/.+\/apache2) '
    command-gather-httpd-apache2-list-all-loaded-configuration-files-variable:
      title: command to gather httpd/apache2 list of all loaded configuration files
      kind: local
      datatype: string
      expression:
        concat:
        - variable: apache-path-httpd-or-apache2-variable
        - literal:
            value: ' -t -D DUMP_INCLUDES'
            datatype: string
    all-loaded-configuration-filepaths-variable:
      title: All loaded configuration filepaths
      kind: local
      datatype: string
      expression:
        unique:
          regex_capture:
            value:
              values:
                object:
                  capability: independent.shellcommand
                  object_title: Gather all loaded config files
                  collect:
                    shell: bash
                    command:
                      variable: command-gather-httpd-apache2-list-all-loaded-configuration-files-variable
                    pattern: ' \('
                    error_if_exit_status_not_0: false
                    error_if_stderr_exists: false
                field: stdout_line
            pattern: \(.*\) (/.*)
    merged-list-all-loaded-config-files-variable:
      title: Merged list of all loaded config files
      kind: local
      datatype: string
      expression:
        merge:
          values:
            variable: all-loaded-configuration-filepaths-variable
          delimiter: ' '
          sort: document
          order: ascending
    shell-command-check-keepalive-in-all-loaded-conf-files-variable:
      title: shell command to check KeepAlive in all loaded conf files
      kind: local
      datatype: string
      expression:
        concat:
        - literal:
            value: 'grep -iHn ''^\s*KeepAlive'' '
            datatype: string
        - variable: merged-list-all-loaded-config-files-variable
    shell-command-check-maxkeepaliverequests-in-httpd-conf-all-include-conf-variable:
      title: shell command to check MaxKeepAliveRequests in httpd.conf and all Include conf files
      kind: local
      datatype: string
      expression:
        concat:
        - literal:
            value: 'grep -iHn ''^\s*MaxKeepAliveRequests'' '
            datatype: string
        - variable: httpd-conf-merged-included-conf-files-from-include-refernces-in-variable
    shell-command-check-maxkeepaliverequests-in-all-loaded-conf-files-variable:
      title: shell command to check MaxKeepAliveRequests in all loaded conf files
      kind: local
      datatype: string
      expression:
        concat:
        - literal:
            value: 'grep -iHn ''^\s*MaxKeepAliveRequests'' '
            datatype: string
        - variable: merged-list-all-loaded-config-files-variable
sources:
  gather-unique-apache-http-installation-paths-object:
    inspect: independent.shellcommand
    description: Gather unique apache http installation paths
    collect:
      shell: bash
      command: ps -e -o command --no-headers | grep -e httpd -e apache2 | sort | uniq
      pattern: ^\/\S+(\/httpd|\/apache2)\s*
      error_if_exit_status_not_0: false
      error_if_stderr_exists: false
checks:
  verify-that-keepalive-directive-defined-configured-on-in-httpd-conf-test:
    check: Verify that KeepAlive directive is defined, and configured to On in httpd.conf/apache2.conf or included
      conf files
    inspect: independent.shellcommand
    description: Gather all KeepAlive data from httpd and all Include conf files
    collect:
      shell: bash
      command:
        variable: shell-command-check-keepalive-in-httpd-conf-all-include-conf-variable
      pattern: .+
      error_if_exit_status_not_0: false
      error_if_stderr_exists: false
    require:
      items: at_least_one
      matching_items: all
      stdout_line:
        matches_regex: \s*KeepAlive On
    report_elements: all
  if-keepalive-directive-defined-in-other-loaded-configuration-files-verify-test:
    check: If the KeepAlive directive is defined in other loaded configuration files, verify it is configured to
      On
    inspect: independent.shellcommand
    description: Gather all KeepAlive data from all loaded conf files
    collect:
      shell: bash
      command:
        variable: shell-command-check-keepalive-in-all-loaded-conf-files-variable
      pattern: .+
      error_if_exit_status_not_0: false
      error_if_stderr_exists: false
    require:
      items: at_least_one
      matching_items: all
      stdout_line:
        presence: may_be_absent
        matches_regex: \s*KeepAlive On
    report_elements: all
  verify-that-maxkeepaliverequests-defined-configured-100-or-greater-httpd-conf-test:
    check: Verify that MaxKeepAliveRequests is defined and is configured to 100 or greater httpd.conf/apache2.conf
      or included conf files
    inspect: independent.shellcommand
    description: Gather all MaxKeepAliveRequests data from httpd and all Include conf files
    collect:
      shell: bash
      command:
        variable: shell-command-check-maxkeepaliverequests-in-httpd-conf-all-include-conf-variable
      pattern: MaxKeepAliveRequests (\d+)
      error_if_exit_status_not_0: false
      error_if_stderr_exists: false
    require:
      items: at_least_one
      matching_items: all
      subexpression:
        greater_than_or_equal: 100
    report_elements: all
  if-maxkeepaliverequests-directive-defined-in-other-loaded-configuration-files-verify-test:
    check: If the MaxKeepAliveRequests directive is defined in other loaded configuration files, verify it is configured
      to 100 or greater
    inspect: independent.shellcommand
    description: Gather all MaxKeepAliveRequests data from all loaded conf files
    collect:
      shell: bash
      command:
        variable: shell-command-check-maxkeepaliverequests-in-all-loaded-conf-files-variable
      pattern: MaxKeepAliveRequests (\d+)
      error_if_exit_status_not_0: false
      error_if_stderr_exists: false
    require:
      items: at_least_one
      matching_items: all
      subexpression:
        presence: may_be_absent
        greater_than_or_equal: 100
    report_elements: all
evaluate:
  and:
  - test: verify-that-keepalive-directive-defined-configured-on-in-httpd-conf-test
  - test: if-keepalive-directive-defined-in-other-loaded-configuration-files-verify-test
  - test: verify-that-maxkeepaliverequests-defined-configured-100-or-greater-httpd-conf-test
  - test: if-maxkeepaliverequests-directive-defined-in-other-loaded-configuration-files-verify-test
```

## Windows DNS configuration and signature bounds

### Original pinned canonical research Assessment

[GitHub file](https://github.com/vanderpol/scap-ng/blob/main/research/assessment-simplification/english-first-04/canonical-operators/dns.canonical.research.yaml)

```yaml
# RESEARCH ONLY — not normative 0.4, runtime/evidence parity not proven
metadata:
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
sources:
  list-all-forward-lookup-zones-object:
    inspect: independent.shellcommand
    description: The list of all forward lookup zones
    collect:
      shell: powershell
      command: Get-DnsServerZone | Where-Object {$_.ZoneType -notin @('Forwarder') -and $_.ZoneName -notin @('TrustAnchors')
        -and (-Not $_.IsAutoCreated) -and (-Not($_.IsReverseLookupZone))} | ForEach-Object {$_.ZoneName}
      error_if_exit_status_not_0: false
      error_if_stderr_exists: false
checks:
  dns-server-caching-only-there-no-forward-or-reverse-lookup-test:
    check: DNS server is caching only (there are no forward or reverse lookup zones)
    inspect: independent.shellcommand
    description: The list of all forward and reverse lookup zones
    collect:
      shell: powershell
      command: Get-DnsServerZone | Where-Object {$_.ZoneType -notin @('Forwarder') -and $_.ZoneName -notin @('TrustAnchors')
        -and (-Not $_.IsAutoCreated)} | ForEach-Object {$_.ZoneName}
      error_if_exit_status_not_0: false
      error_if_stderr_exists: false
    require:
      items: at_least_one
      match: all
      stdout_line:
        no_values_exist: true
        source_comparison:
          equals: ''
    report_elements: all
  all-forward-lookup-zones-if-any-integrated-active-directory-test:
    check: All forward lookup zones (if any) are integrated with Active Directory
    inspect: independent.shellcommand
    description: The list of all forward lookup zones that are not integrated with Active Directory
    collect:
      shell: powershell
      command: Get-DnsServerZone | Where-Object {$_.ZoneType -notin @('Forwarder') -and $_.ZoneName -notin @('TrustAnchors')
        -and (-Not $_.IsAutoCreated) -and -Not($_.IsReverseLookupZone) -and (-Not $_.IsDsIntegrated)} | ForEach-Object
        {$_.ZoneName}
      error_if_exit_status_not_0: false
      error_if_stderr_exists: false
    require:
      items: at_least_one
      match: all
      stdout_line:
        no_values_exist: true
        source_comparison:
          equals: ''
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
      items: at_least_one
      match: all
      stdout_line:
        exactly_one_equals: 'True'
    report_elements: all
  all-forward-lookup-zones-have-dns-key-signature-validity-periods-test:
    check: All forward lookup zones have DNS key signature validity periods between two days and a week for their
      zone signing keys
    inspect: independent.shellcommand
    description: The list of DNS key signature validity periods for the zone signing keys
    collect:
      shell: powershell
      command:
        variable: command-get-list-dns-key-signature-validity-periods-zone-signing-variable
      error_if_exit_status_not_0: false
      error_if_stderr_exists: false
    all_state_fields_exist: true
    require:
      items: at_least_one
      match: all
      states:
        and:
        - stdout_line:
            greater_than_or_equal: 48
        - stdout_line:
            less_than_or_equal: 168
    report_elements: all
  all-forward-lookup-zones-have-dns-key-signature-validity-periods-2-test:
    check: All forward lookup zones have DNS key signature validity periods between two days and a week for their
      key signing keys
    inspect: independent.shellcommand
    description: The list of DNS key signature validity periods for the key signing keys
    collect:
      shell: powershell
      command:
        variable: command-get-list-dns-key-signature-validity-periods-key-signing-variable
      error_if_exit_status_not_0: false
      error_if_stderr_exists: false
    all_state_fields_exist: true
    require:
      items: at_least_one
      match: all
      states:
        and:
        - stdout_line:
            greater_than_or_equal: 48
        - stdout_line:
            less_than_or_equal: 168
    report_elements: all
evaluate:
  or:
  - test: dns-server-caching-only-there-no-forward-or-reverse-lookup-test
  - test: all-forward-lookup-zones-if-any-integrated-active-directory-test
  - and:
    - test: all-forward-lookup-zones-dnssec-signed-test
    - test: all-forward-lookup-zones-have-dns-key-signature-validity-periods-test
    - test: all-forward-lookup-zones-have-dns-key-signature-validity-periods-2-test
```

### Revised readability candidate

[GitHub file](https://github.com/vanderpol/scap-ng/blob/main/research/assessment-simplification/english-first-04/field-presence-iteration/dns.revised.research.yaml)

```yaml
# RESEARCH ONLY — not normative 0.4, runtime/evidence parity not proven
metadata:
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
sources:
  list-all-forward-lookup-zones-object:
    inspect: independent.shellcommand
    description: The list of all forward lookup zones
    collect:
      shell: powershell
      command: Get-DnsServerZone | Where-Object {$_.ZoneType -notin @('Forwarder') -and $_.ZoneName -notin @('TrustAnchors')
        -and (-Not $_.IsAutoCreated) -and (-Not($_.IsReverseLookupZone))} | ForEach-Object {$_.ZoneName}
      error_if_exit_status_not_0: false
      error_if_stderr_exists: false
checks:
  dns-server-caching-only-there-no-forward-or-reverse-lookup-test:
    check: DNS server is caching only (there are no forward or reverse lookup zones)
    inspect: independent.shellcommand
    description: The list of all forward and reverse lookup zones
    collect:
      shell: powershell
      command: Get-DnsServerZone | Where-Object {$_.ZoneType -notin @('Forwarder') -and $_.ZoneName -notin @('TrustAnchors')
        -and (-Not $_.IsAutoCreated)} | ForEach-Object {$_.ZoneName}
      error_if_exit_status_not_0: false
      error_if_stderr_exists: false
    require:
      items: at_least_one
      matching_items: all
      stdout_line:
        no_values_exist: true
        source_comparison:
          equals: ''
    report_elements: all
  all-forward-lookup-zones-if-any-integrated-active-directory-test:
    check: All forward lookup zones (if any) are integrated with Active Directory
    inspect: independent.shellcommand
    description: The list of all forward lookup zones that are not integrated with Active Directory
    collect:
      shell: powershell
      command: Get-DnsServerZone | Where-Object {$_.ZoneType -notin @('Forwarder') -and $_.ZoneName -notin @('TrustAnchors')
        -and (-Not $_.IsAutoCreated) -and -Not($_.IsReverseLookupZone) -and (-Not $_.IsDsIntegrated)} | ForEach-Object
        {$_.ZoneName}
      error_if_exit_status_not_0: false
      error_if_stderr_exists: false
    require:
      items: at_least_one
      matching_items: all
      stdout_line:
        no_values_exist: true
        source_comparison:
          equals: ''
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
      items: at_least_one
      matching_items: all
      stdout_line:
        exactly_one_equals: 'True'
    report_elements: all
  all-forward-lookup-zones-have-dns-key-signature-validity-periods-test:
    check: All forward lookup zones have DNS key signature validity periods between two days and a week for their
      zone signing keys
    inspect: independent.shellcommand
    description: The list of DNS key signature validity periods for the zone signing keys
    collect:
      shell: powershell
      command:
        variable: command-get-list-dns-key-signature-validity-periods-zone-signing-variable
      error_if_exit_status_not_0: false
      error_if_stderr_exists: false
    require:
      items: at_least_one
      matching_items: all
      field_presence: required
      states:
        and:
        - stdout_line:
            greater_than_or_equal: 48
        - stdout_line:
            less_than_or_equal: 168
    report_elements: all
  all-forward-lookup-zones-have-dns-key-signature-validity-periods-2-test:
    check: All forward lookup zones have DNS key signature validity periods between two days and a week for their
      key signing keys
    inspect: independent.shellcommand
    description: The list of DNS key signature validity periods for the key signing keys
    collect:
      shell: powershell
      command:
        variable: command-get-list-dns-key-signature-validity-periods-key-signing-variable
      error_if_exit_status_not_0: false
      error_if_stderr_exists: false
    require:
      items: at_least_one
      matching_items: all
      field_presence: required
      states:
        and:
        - stdout_line:
            greater_than_or_equal: 48
        - stdout_line:
            less_than_or_equal: 168
    report_elements: all
evaluate:
  or:
  - test: dns-server-caching-only-there-no-forward-or-reverse-lookup-test
  - test: all-forward-lookup-zones-if-any-integrated-active-directory-test
  - and:
    - test: all-forward-lookup-zones-dnssec-signed-test
    - test: all-forward-lookup-zones-have-dns-key-signature-validity-periods-test
    - test: all-forward-lookup-zones-have-dns-key-signature-validity-periods-2-test
```

## Existing specification contract excerpt

**This is not a six-state truth-table replacement**. The following is an excerpt from the current project's Assessment Method and points to the pinned OVAL 5.12.3 tables. Gemini should not improvise other default truth behavior. The source document is https://github.com/vanderpol/scap-ng/blob/main/specification/assessment/assessment-method.md .

```text

### Inherited result aggregation semantics

For OVAL-compatible migrated assessments, generic Boolean/result aggregation
SHALL preserve the OVAL 5.12.3 evaluation tables for `CheckEnumeration`,
`OperatorEnumeration`, and `ExistenceEnumeration`, including the precedence
and propagation of `true`, `false`, `error`, `unknown`, `not evaluated`,
and `not applicable`.

A conforming migration implementation SHALL NOT replace these multi-valued
semantics with ordinary two-valued Boolean logic. In particular, a decisive
`false` for an ALL/AND aggregation and a decisive `true` for an
AT-LEAST-ONE/OR aggregation may determine the result even when other inputs
are `error` or `unknown`, exactly as specified by the authoritative OVAL
tables.

Test/object existence aggregation SHALL remain a separate evaluation stage
from item-to-State satisfaction aggregation. `any_exist` is not synonymous
with `at_least_one_exists`; the inherited OVAL table intentionally permits
`any_exist` to evaluate true when zero matching objects exist and no
collection error prevents that conclusion.

The project's reference truth-table fixture is
`tools/oval_result_truth_tables.py` with conformance tests in
`tools/test_oval_result_truth_tables.py`. This helper is test evidence, not
the reference scanner itself.

### Collected-object flag control flow

For OVAL-compatible migrated assessments, the collected-object status/flag
SHALL affect Test result evaluation according to the pinned OVAL 5.12.3
Results schema:

- `error` produces Test `error`;
- `not collected` produces Test `unknown`;
- `not applicable` produces Test `not applicable`;
- `does not exist` is resolved solely from the Test existence mode:
  `none_exist` and `any_exist` produce true, while `all_exist`,
  `at_least_one_exists`, and `only_one_exists` produce false;
- `complete` evaluates existence first and evaluates item/State satisfaction
  only when existence is true;
- `incomplete` normally produces `unknown`, but a decisive false or true
  SHALL be preserved when the OVAL 5.12.3 rules establish the outcome despite
  incomplete collection.

In particular, incomplete collection SHALL produce false when
`none_exist` already has one or more existing items, when
`only_one_exists` already has more than one existing item, or when the item
check has already become decisively false. For an AT-LEAST-ONE item check,
one known satisfying item MAY produce true despite the incomplete collection.
Implementations SHALL NOT collapse all incomplete collections to `unknown`.

When a collected-objects section is present but no collected-object record
matches the referenced Object, the Test result SHALL be `unknown`. The
separate OVAL behavior for a System Characteristics document that omits the
entire collected-objects section requires item matching against system data and
remains a distinct evaluator conformance case.

### State entity and variable aggregation order

When a State entity references multiple Variable values and a collected Item
contains multiple corresponding entity instances, evaluation SHALL preserve
the OVAL 5.12.3 many-to-many aggregation order:

1. compare one system/item entity value against each Variable value;
2. combine those comparison results with the State entity's `value_match` (OVAL `var_check`);
3. repeat for each corresponding system/item entity instance;
4. combine the per-instance results with that State entity's `entity_check`;
5. combine distinct entity/predicate results inside the State using the
   State's own Boolean operator;
6. when a Test references multiple States, combine those State results for
   each item using the Test's `state_operator`; and
7. combine item results at the Test level using the Test's `check`.

These scopes SHALL remain independent. A producer or evaluator SHALL NOT
commute, merge or substitute `value_match` (OVAL `var_check`), `entity_check`, State operator,
`state_operator`, or Test `check` merely because a particular two-valued
example happens to produce the same result. Error/unknown/not-evaluated/not-
applicable propagation occurs at each aggregation layer.
```

## Required Phase 2 results

1. Full original vs proposed analysis for each of five pairs, including source paths and check IDs, *not* invented shorthand.
2. Correct previous blind mistakes about incomplete acquisition, missing fields, WMI mixed records, **value multiplicity inside one Item** vs multiple Items, OR and AND error precedence, original regex, and Apache disabled command error checks.
3. Distinguish `field_presence: required` under the Test's `require` from `presence: may_be_absent` at the Apache field and from original flags/field modes; call non-Boolean behavior **unproved** when it is.
4. State exactly which language improvements are supported by this source pack and which are merely stylistic.
5. If you propose changes, supply valid full YAML or accurate excerpt labels and check that no original expressions/sources were dropped.
6. Separate readability assessment from structural re-inversion proof and six-state evaluator proof.
