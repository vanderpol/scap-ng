# 05 · Apache UNIX configuration discovery and optional directives — complete before and after

**Review-only research. The after version is experimental and is not approved 0.4 syntax or independent OVAL scanner-conformance evidence.**

[Back to all five complete examples](BEFORE-AFTER-REVIEW.md) · [Original pinned source](https://github.com/vanderpol/scap-ng-editor-sample-data/blob/99cbceae8d594c44cb509df95975ac1676a2b44a/focused-fixtures/source-backed/authoring/apache_server_2-4_unix_server/assessments/automated/SV-214228.automated.yaml) · [Full generated research YAML](comparisons/apache-keepalive.research.yaml)

## What changed (and what did not)

- The full 18-variable discovery graph, source Objects, four Tests and final `evaluate.all_of` are included.
- The `when_present_*` requirements distinguish optional State fields from required fields without dropping source Item cardinality.
- The deepest Apache dependency chain reaches ten edges: this example should expose rather than conceal that authorability problem.

**Authoring question:** Would you prefer an explicit reusable `discover Apache configuration` source, and can you tell exactly how it would preserve the existing command/collection behavior?

## Complete assessments — side by side

Both columns include the **complete** original and proposed YAML; no checks, sources, Variables, or evaluation branches have been omitted. The view is intended for a wide desktop browser. If the table is wider than the viewport, scroll horizontally inside the rendered table. Standalone YAML links remain above.

<table>
<thead><tr><th align="left" width="50%">BEFORE — Current 0.4</th><th align="left" width="50%">AFTER — English-first research</th></tr></thead>
<tbody><tr>
<td valign="top" width="50%"><pre><code>assessment:
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
  shared_objects:
    gather-unique-apache-http-installation-paths-object:
      capability: independent.shellcommand
      object_title: Gather unique apache http installation paths
      collect:
        shell: bash
        command: ps -e -o command --no-headers | grep -e httpd -e apache2 | sort | uniq
        pattern: ^\/\S+(\/httpd|\/apache2)\s*
        error_if_exit_status_not_0: false
        error_if_stderr_exists: false</code></pre></td>
<td valign="top" width="50%"><pre><code># EXPERIMENT ONLY; reconstructs the pinned Assessment exactly.
# Not normative SCAP-NG v0.4 or independently validated OVAL execution.
metadata:
  id: SV-214228.automated
  version: 2
  assessment_title: The Apache web server must limit the number of allowed simultaneous
    session requests.
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
      title: shell command to check MaxKeepAliveRequests in httpd.conf and all Include
        conf files
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
    check: Verify that KeepAlive directive is defined, and configured to On in httpd.conf/apache2.conf
      or included conf files
    inspect: independent.shellcommand
    require:
      at_least_one_item_exists: true
      every_item_must_match:
        stdout_line:
          matches_regex: \s*KeepAlive On
    report_elements: all
    description: Gather all KeepAlive data from httpd and all Include conf files
    collect:
      shell: bash
      command:
        variable: shell-command-check-keepalive-in-httpd-conf-all-include-conf-variable
      pattern: .+
      error_if_exit_status_not_0: false
      error_if_stderr_exists: false
  if-keepalive-directive-defined-in-other-loaded-configuration-files-verify-test:
    check: If the KeepAlive directive is defined in other loaded configuration files,
      verify it is configured to On
    inspect: independent.shellcommand
    require:
      at_least_one_item_exists: true
      every_item_must_match:
        stdout_line:
          when_present_matches_regex: \s*KeepAlive On
    report_elements: all
    description: Gather all KeepAlive data from all loaded conf files
    collect:
      shell: bash
      command:
        variable: shell-command-check-keepalive-in-all-loaded-conf-files-variable
      pattern: .+
      error_if_exit_status_not_0: false
      error_if_stderr_exists: false
  verify-that-maxkeepaliverequests-defined-configured-100-or-greater-httpd-conf-test:
    check: Verify that MaxKeepAliveRequests is defined and is configured to 100 or
      greater httpd.conf/apache2.conf or included conf files
    inspect: independent.shellcommand
    require:
      at_least_one_item_exists: true
      every_item_must_match:
        subexpression:
          at_least: 100
    report_elements: all
    description: Gather all MaxKeepAliveRequests data from httpd and all Include conf
      files
    collect:
      shell: bash
      command:
        variable: shell-command-check-maxkeepaliverequests-in-httpd-conf-all-include-conf-variable
      pattern: MaxKeepAliveRequests (\d+)
      error_if_exit_status_not_0: false
      error_if_stderr_exists: false
  if-maxkeepaliverequests-directive-defined-in-other-loaded-configuration-files-verify-test:
    check: If the MaxKeepAliveRequests directive is defined in other loaded configuration
      files, verify it is configured to 100 or greater
    inspect: independent.shellcommand
    require:
      at_least_one_item_exists: true
      every_item_must_match:
        subexpression:
          when_present_at_least: 100
    report_elements: all
    description: Gather all MaxKeepAliveRequests data from all loaded conf files
    collect:
      shell: bash
      command:
        variable: shell-command-check-maxkeepaliverequests-in-all-loaded-conf-files-variable
      pattern: MaxKeepAliveRequests (\d+)
      error_if_exit_status_not_0: false
      error_if_stderr_exists: false
evaluate:
  all_of:
  - test: verify-that-keepalive-directive-defined-configured-on-in-httpd-conf-test
  - test: if-keepalive-directive-defined-in-other-loaded-configuration-files-verify-test
  - test: verify-that-maxkeepaliverequests-defined-configured-100-or-greater-httpd-conf-test
  - test: if-maxkeepaliverequests-directive-defined-in-other-loaded-configuration-files-verify-test</code></pre></td>
</tr></tbody>
</table>


## What to tell us

- Can you trace the complete logic without opening a missing definition?
- Is the after version easier to write from scratch, or merely shorter?
- Where does the vocabulary or nesting remain inconsistent?

**Structural evidence:** [The six-STIG run 38934771985](https://github.com/vanderpol/scap-ng/actions/runs/38934771985) reconstructed the original full Assessment dictionaries using this research representation. This does not establish SCAP 1.4 runtime/evidence equivalence.
