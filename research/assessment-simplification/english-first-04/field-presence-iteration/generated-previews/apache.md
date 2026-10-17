# Auditor preview — The Apache web server must limit the number of allowed simultaneous session requests.

**Machine-generated research explanation from complete parsed YAML.** No live result, new normative policy or scanner-equivalence proof.

**Assessment ID:** `SV-214228.automated` · **Checks:** 4 · **Evaluate leaves:** 4

[Revised full YAML](../apache.revised.research.yaml) · [Original source YAML](../../canonical-operators/apache.canonical.research.yaml)

## What is observed?

### Named source `gather-unique-apache-http-installation-paths-object`

**Inspector:** `independent.shellcommand`
**Collection configuration:**

~~~yaml
shell: bash
command: ps -e -o command --no-headers | grep -e httpd -e apache2 | sort | uniq
pattern: ^\/\S+(\/httpd|\/apache2)\s*
error_if_exit_status_not_0: false
error_if_stderr_exists: false
~~~


**Variable graph:** 18 declarations (full expressions in source YAML).
- `apache-base-install-directories-unix-variable`
- `httpd-root-apachectl-v-variable`
- `filepath-httpd-root-variable`
- `server-config-file-apachectl-v-variable`
- `relative-server-config-file-variable`
- `filepath-http-conf-file-variable`
- `shell-command-check-all-include-include-optional-files-variable`
- `all-included-conf-files-from-include-refernces-in-httd-conf-variable`
- `merged-included-conf-files-from-include-refernces-in-httd-conf-variable`
- `httpd-conf-merged-included-conf-files-from-include-refernces-in-variable`
- `shell-command-check-keepalive-in-httpd-conf-all-include-conf-variable`
- `apache-path-httpd-or-apache2-variable`
- `command-gather-httpd-apache2-list-all-loaded-configuration-files-variable`
- `all-loaded-configuration-filepaths-variable`
- `merged-list-all-loaded-config-files-variable`
- `shell-command-check-keepalive-in-all-loaded-conf-files-variable`
- `shell-command-check-maxkeepaliverequests-in-httpd-conf-all-include-conf-variable`
- `shell-command-check-maxkeepaliverequests-in-all-loaded-conf-files-variable`

## What must exist and match?

### Verify that KeepAlive directive is defined, and configured to On in httpd.conf/apache2.conf or included conf files

**Check ID:** `verify-that-keepalive-directive-defined-configured-on-in-httpd-conf-test` · **Inspector:** `independent.shellcommand`

- **Root Item existence:** `at_least_one`
- **Matching root Items:** `all`
**Original collect (not reconstructed):**

~~~yaml
shell: bash
command:
  variable: shell-command-check-keepalive-in-httpd-conf-all-include-conf-variable
pattern: .+
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
  matches_regex: \s*KeepAlive On
~~~

### If the KeepAlive directive is defined in other loaded configuration files, verify it is configured to On

**Check ID:** `if-keepalive-directive-defined-in-other-loaded-configuration-files-verify-test` · **Inspector:** `independent.shellcommand`

- **Root Item existence:** `at_least_one`
- **Matching root Items:** `all`
**Original collect (not reconstructed):**

~~~yaml
shell: bash
command:
  variable: shell-command-check-keepalive-in-all-loaded-conf-files-variable
pattern: .+
error_if_exit_status_not_0: false
error_if_stderr_exists: false
~~~


**Explicit field, record and State scopes:**

- `require.stdout_line`: explicit local FIELD presence `may_be_absent`.

**Full requirement subtree (candidate wording):**

~~~yaml
items: at_least_one
matching_items: all
stdout_line:
  presence: may_be_absent
  matches_regex: \s*KeepAlive On
~~~

### Verify that MaxKeepAliveRequests is defined and is configured to 100 or greater httpd.conf/apache2.conf or included conf files

**Check ID:** `verify-that-maxkeepaliverequests-defined-configured-100-or-greater-httpd-conf-test` · **Inspector:** `independent.shellcommand`

- **Root Item existence:** `at_least_one`
- **Matching root Items:** `all`
**Original collect (not reconstructed):**

~~~yaml
shell: bash
command:
  variable: shell-command-check-maxkeepaliverequests-in-httpd-conf-all-include-conf-variable
pattern: MaxKeepAliveRequests (\d+)
error_if_exit_status_not_0: false
error_if_stderr_exists: false
~~~


**Explicit field, record and State scopes:**

- No additional field-presence/record/group policy is explicitly displayed.

**Full requirement subtree (candidate wording):**

~~~yaml
items: at_least_one
matching_items: all
subexpression:
  greater_than_or_equal: 100
~~~

### If the MaxKeepAliveRequests directive is defined in other loaded configuration files, verify it is configured to 100 or greater

**Check ID:** `if-maxkeepaliverequests-directive-defined-in-other-loaded-configuration-files-verify-test` · **Inspector:** `independent.shellcommand`

- **Root Item existence:** `at_least_one`
- **Matching root Items:** `all`
**Original collect (not reconstructed):**

~~~yaml
shell: bash
command:
  variable: shell-command-check-maxkeepaliverequests-in-all-loaded-conf-files-variable
pattern: MaxKeepAliveRequests (\d+)
error_if_exit_status_not_0: false
error_if_stderr_exists: false
~~~


**Explicit field, record and State scopes:**

- `require.subexpression`: explicit local FIELD presence `may_be_absent`.

**Full requirement subtree (candidate wording):**

~~~yaml
items: at_least_one
matching_items: all
subexpression:
  presence: may_be_absent
  greater_than_or_equal: 100
~~~


## How could the Assessment pass?

The structural AND/OR tree below is read from parsed YAML. It is not procedural IF/ELSE, and no actual outcome is calculated.

- **ALL of these child checks (AND)**:
  - `verify-that-keepalive-directive-defined-configured-on-in-httpd-conf-test` — Verify that KeepAlive directive is defined, and configured to On in httpd.conf/apache2.conf or included conf files
  - `if-keepalive-directive-defined-in-other-loaded-configuration-files-verify-test` — If the KeepAlive directive is defined in other loaded configuration files, verify it is configured to On
  - `verify-that-maxkeepaliverequests-defined-configured-100-or-greater-httpd-conf-test` — Verify that MaxKeepAliveRequests is defined and is configured to 100 or greater httpd.conf/apache2.conf or included conf files
  - `if-maxkeepaliverequests-directive-defined-in-other-loaded-configuration-files-verify-test` — If the MaxKeepAliveRequests directive is defined in other loaded configuration files, verify it is configured to 100 or greater

**Evaluate references:** 4 occurrences of 4 named checks, all accounted for.

## What remains unverified?

- **No system evidence** was collected or evaluated.
- Missing field, missing root Item, read error and incomplete collection are different.
- Repeated field values, nested WMI records and root Items have separate quantifiers.
- Field-presence and matching-label aliases are research-only; runtime equivalence remains open.
- OVAL AND(False,Error) can be False, while OR(True,Error) can be True.
- For command flags, dependent sources, typing and evidence rules, inspect the complete YAML.

[Generic six-state result ledger](SEMANTIC-BOUNDARY-LEDGER.md).
