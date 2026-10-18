# Apache SV-214228 — full inline-command authoring candidate

**October 18, 2026 · Research for [#235](https://github.com/vanderpol/scap-ng/issues/235) and [#227](https://github.com/vanderpol/scap-ng/issues/227). NOT an adopted grammar, executable 0.4 Assessment, or scanner parity claim.** The [existing full before/after comparison](FULL-05-apache.md) contains the pinned source-backed original and the earlier English-first research file. This page adds a **complete third authoring candidate**, not an excerpt.

## The limited, testable hypothesis

Each of the 4 command Variables below is referenced **once**, as a check's `collect.command`. In this candidate, the *identical authored expression subtree* replaces that reference at the point of use. Its named Variable declaration is removed; **all other acquisition sources and Variables, shell literals, regex, collection flags, Item/field requirements, IDs and evaluate logic remain intact**.

| Source measure | Before (English-first) | Inline candidate |
| --- | ---: | ---: |
| Named local Variables | 18 | 14 |
| Nonblank/non-comment YAML lines | 335 | 310 |
| Single-use Variable lookups between check and command | 4 | 0 |

Eliminated **single-use names**, not their computations:

- `shell-command-check-keepalive-in-httpd-conf-all-include-conf-variable`
- `shell-command-check-keepalive-in-all-loaded-conf-files-variable`
- `shell-command-check-maxkeepaliverequests-in-httpd-conf-all-include-conf-variable`
- `shell-command-check-maxkeepaliverequests-in-all-loaded-conf-files-variable`

**Source integrity:** The derivation was mechanically checked for exactly one reference per substituted name, identical expression text and an exact reverse substitution back to the full original English-first YAML. The reverse check **retains original removed Variable declarations as a separate edit recipe**; the standalone candidate does **not** encode their `title`, `kind: local`, or `datatype: string` metadata. Therefore this is **not proven self-contained lossless lowering**, nor proof that `collect.command` today accepts inline `concat` or preserves runtime collection/evidence semantics. An accepted design would need explicit typing, error/completeness/provenance rules and a decision about declaration metadata.

## Complete Apache SV-214228 third candidate

```yaml
# EXPERIMENT ONLY: no 0.4 compiler/schema support is asserted.
# EXPERIMENT ONLY; reconstructs the pinned Assessment exactly.
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
    description: Gather all KeepAlive data from httpd and all Include conf files
    collect:
      shell: bash
      command:
        concat:
        - literal:
            value: 'grep -iHn ''^\s*KeepAlive'' '
            datatype: string
        - variable: httpd-conf-merged-included-conf-files-from-include-refernces-in-variable
      pattern: .+
      error_if_exit_status_not_0: false
      error_if_stderr_exists: false
    require:
      at_least_one_item_exists: true
      every_item_must_match:
        stdout_line:
          matches_regex: \s*KeepAlive On
    report_elements: all
  if-keepalive-directive-defined-in-other-loaded-configuration-files-verify-test:
    check: If the KeepAlive directive is defined in other loaded configuration files,
      verify it is configured to On
    inspect: independent.shellcommand
    description: Gather all KeepAlive data from all loaded conf files
    collect:
      shell: bash
      command:
        concat:
        - literal:
            value: 'grep -iHn ''^\s*KeepAlive'' '
            datatype: string
        - variable: merged-list-all-loaded-config-files-variable
      pattern: .+
      error_if_exit_status_not_0: false
      error_if_stderr_exists: false
    require:
      at_least_one_item_exists: true
      every_item_must_match:
        stdout_line:
          when_present_matches_regex: \s*KeepAlive On
    report_elements: all
  verify-that-maxkeepaliverequests-defined-configured-100-or-greater-httpd-conf-test:
    check: Verify that MaxKeepAliveRequests is defined and is configured to 100 or
      greater httpd.conf/apache2.conf or included conf files
    inspect: independent.shellcommand
    description: Gather all MaxKeepAliveRequests data from httpd and all Include conf
      files
    collect:
      shell: bash
      command:
        concat:
        - literal:
            value: 'grep -iHn ''^\s*MaxKeepAliveRequests'' '
            datatype: string
        - variable: httpd-conf-merged-included-conf-files-from-include-refernces-in-variable
      pattern: MaxKeepAliveRequests (\d+)
      error_if_exit_status_not_0: false
      error_if_stderr_exists: false
    require:
      at_least_one_item_exists: true
      every_item_must_match:
        subexpression:
          at_least: 100
    report_elements: all
  if-maxkeepaliverequests-directive-defined-in-other-loaded-configuration-files-verify-test:
    check: If the MaxKeepAliveRequests directive is defined in other loaded configuration
      files, verify it is configured to 100 or greater
    inspect: independent.shellcommand
    description: Gather all MaxKeepAliveRequests data from all loaded conf files
    collect:
      shell: bash
      command:
        concat:
        - literal:
            value: 'grep -iHn ''^\s*MaxKeepAliveRequests'' '
            datatype: string
        - variable: merged-list-all-loaded-config-files-variable
      pattern: MaxKeepAliveRequests (\d+)
      error_if_exit_status_not_0: false
      error_if_stderr_exists: false
    require:
      at_least_one_item_exists: true
      every_item_must_match:
        subexpression:
          when_present_at_least: 100
    report_elements: all
evaluate:
  all_of:
  - test: verify-that-keepalive-directive-defined-configured-on-in-httpd-conf-test
  - test: if-keepalive-directive-defined-in-other-loaded-configuration-files-verify-test
  - test: verify-that-maxkeepaliverequests-defined-configured-100-or-greater-httpd-conf-test
  - test: if-maxkeepaliverequests-directive-defined-in-other-loaded-configuration-files-verify-test
```

## First-read questions for security auditors

1. Where is the native collection declared, and where does each command obtain its variable-length input? Can you follow that without reading the original file?
2. What precisely does `concat` mean for zero, one and multiple `stdout_line` values? What is the string/array type of the derived command? **Say unknown if not defined.**
3. What happens when the upstream source reports an error or incomplete data? Does the check still run, fail, become unknown, or have no collected Item? **No behavior may be inferred from shell syntax alone.**
4. Identify the separate Item existence requirement and the field-value matching requirement in each check. Do not conflate a successful command yielding no stdout with a missing command Item.
5. State the complete Assessment's top-level `evaluate` logic. Did inlining accidentally change which checks must pass?
6. Would you prefer this *as source to write and review*, or named command Variables plus editor navigation? Specify at least one place in the YAML where your interpretation changes.

## Explicit limits and next experiment

This is a useful **bounded** authoring reduction of 25 non-comment lines and 4 unnecessary one-hop references, without a new pipeline language. It **does not solve** the remaining 14 named acquisition/Variable stages, particularly the two distinct configuration discovery paths. Deep nested expressions, repeated commands, unknown upstream error status and string/array interpolation are still real concerns.

Before choosing a standard: independently test human comprehension of this **full** file against the prior full source; define/verify the typed command-expression boundary, item lineage, zero/many/error outcomes and provenance; validate metadata recovery. No normative schema/converter changes or 65-STIG jobs are authorized by this experiment.
