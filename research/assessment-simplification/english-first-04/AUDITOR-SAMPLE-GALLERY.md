# Auditor-first SCAP-NG: six real patterns

**Experimental 0.4 grammar — not normative.** Each block below is an **excerpt**, not a standalone executable Assessment. Read the linked full YAML on `github.com`; every full Assessment linked here is among the 871 complete dictionaries reconstructed exactly from the pinned six-STIG source. This is not independent OVAL scanner/evidence proof.

## 1. RHEL — mount the home filesystem with nosuid

```yaml
check: /home is mounted with the nosuid option.
inspect: linux.partition
where:
  mount_point:
    matches_regex: .*\/home
require:
  items: at_least_one
  every_item:
    mount_options:
      at_least_one_value_is: nosuid
```

**Meaning:** find the partitions matching the original `/home` regex; at least one must exist and every selected partition must have `nosuid` among its option values. The source regex is wider than an exact mount-point comparison, so an importer must not silently replace it.

[Full RHEL mount YAML](auditor-candidate/linux-home.auditor.research.yaml)

## 2. Windows 11 — deny Remote Desktop logon to Guests

```yaml
sources:
  windows-userright-object:
    inspect: windows.userright
    where:
      userright:
        equals: SE_DENY_REMOTE_INTERACTIVE_LOGON_NAME
checks:
  deny-log-on-through-remote-desktop-services-guests-test:
    check: Deny log on through Remote Desktop Services - Guests
    inspect: windows.userright
    from: windows-userright-object
    require:
      items: at_least_one
      at_least_one_item:
        trustee_name:
          equals_ignoring_case: Guests
```

**Meaning:** inspect that specific user right, and require at least one Item identifying Guests. *At least one matching* is not the same as *every Item matching*.

[Full Windows YAML — includes seven Tests and WMI role alternatives](auditor-candidate/windows-wmi-rights.auditor.research.yaml)

## 3. Windows — records with whole-State alternatives

```yaml
check: The system is a non-DC domain-joined Windows server or workstation
inspect: windows.wmi.query
from: windows-wmi57-object
require:
  items: at_least_one
  every_item:
    any_of:
      - result:
          at_least_one_record_exists: true
          every_record:
            domainrole: {is: '1'}
      - result:
          at_least_one_record_exists: true
          every_record:
            domainrole: {is: '3'}
```

**Meaning:** use the declared WMI query, retain two **whole-record** alternatives. Replacing them with a simple membership comparison is not generally equivalent when multiple records exist.

[Full Windows WMI YAML](auditor-candidate/windows-wmi-rights.auditor.research.yaml)

## 4. Windows DNS — collect command results, enforce both bounds

```yaml
inspect: independent.shellcommand
collect:
  shell: powershell
  command:
    variable: command-get-list-dns-key-signature-validity-periods-zone-signing-variable
  error_if_exit_status_not_0: false
  error_if_stderr_exists: false
all_state_fields_exist: true
require:
  items: at_least_one
  every_item:
    all_states:
      - stdout_line: {at_least: 48}
      - stdout_line: {at_most: 168}
```

**Meaning:** the named Variable constructs the source command. Every Item must meet both 48-hour and 168-hour limits. The full Assessment retains three command Variables and five Tests.

[Full DNS YAML](auditor-candidate/dns.auditor.research.yaml)

## 5. Apache — required Item, optional field comparison

```yaml
inspect: independent.shellcommand
collect:
  shell: bash
  command:
    variable: shell-command-check-keepalive-in-all-loaded-conf-files-variable
  pattern: .+
  error_if_exit_status_not_0: false
  error_if_stderr_exists: false
require:
  items: at_least_one
  every_item:
    stdout_line:
      when_present_matches_regex: \s*KeepAlive On
```

**Meaning:** Item existence and the *when-present* field comparison are different requirements. The full Assessment retains the original Apache configuration discovery graph of 18 Variables.

[Full Apache YAML](auditor-candidate/apache.auditor.research.yaml)

## 6. Linux — collect initialization files derived from each account

```yaml
inspect: unix.file
gather:
  union:
    - from:
        inspect: unix.file
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
        - type: {is: directory}
require:
  items: may_be_absent
  every_item:
    all_of:
      - setuid: {is: false}
      - setgid: {is: false}
      # Six more permissions are required in the complete Assessment.
    all_fields_must_exist: true
```

**Meaning:** for each qualifying account, collect matching files under that user's home directory; omit directory Items; evaluate eight permissions on every remaining Item. Missing files are allowed in this branch, but the separate root-user branch has a different existence requirement. The `union` is preserved from the real source, not added for decoration.

[Full Linux derived-file YAML](auditor-candidate/linux-files.auditor.research.yaml)

## Security-auditor acceptance criteria

A reviewer must be able to identify **which data is collected, how Items are selected, what happens when no Items are returned, which Items/field values must match, and how multiple Tests combine**. If any distinction requires guesswork, more language work is needed. Do not rewrite a `none_exist` violation-query + filter as an ordinary `every_item` test without preserving the original error behavior: [counterexample research](https://github.com/vanderpol/scap-ng/blob/main/research/assessment-simplification/violation-query-14/README.md).

**Candidate and verification:** [auditor-first language and proof](AUDITOR-FIRST-CANDIDATE.md); [five complete before/after comparison pages](BEFORE-AFTER-REVIEW.md). No vocabulary is fixed until semantics and auditor usability are satisfactory.
