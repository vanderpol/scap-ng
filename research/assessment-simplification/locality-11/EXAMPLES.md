# Locality examples

> **RESEARCH ONLY — NOT VALIDATED 0.3.0 SOURCE**

These examples use real Rules from the production workflow. They illustrate the
layout idea only; explicit quantifiers and other semantic fields have
intentionally not been simplified.

## RHEL 9 SV-257785 — private Object and State

Requirement: disable the x86 Ctrl-Alt-Delete sequence.

The faithful graph has one Object, one State, and one Test. Neither component is
reused. The research form keeps everything at the point of use:

```yaml
tests:
  test-ctrl-alt-del-target-unit-masked:
    test_title: The ctrl-alt-del.target unit is masked.
    capability: unix.symlink

    object:
      capability: unix.symlink
      select:
        full_path:
          value: /etc/systemd/system/ctrl-alt-del.target
          operation: equal
          datatype: string

    check_existence: some
    check: all

    states:
      - capability: unix.symlink
        state:
          field: canonical_path
          value: /dev/null
          operation: equal
          datatype: string
          match: all
          existence: some

    reported_elements: all

evaluate:
  test: test-ctrl-alt-del-target-unit-masked
```

No semantic shorthand was introduced. The reader simply no longer has to jump
from Test -> Object section -> State section.

## RHEL 9 SV-257794 — shared State stays shared

Requirement: enable `init_on_free=1` in both the BLS options and
`/etc/default/grub`.

The two collection Objects are private and inline. The same comparison State is
used by both Tests, so it remains named:

```yaml
states:
  state-independent-textfilecontent54:
    capability: independent.textfilecontent54
    state:
      field: subexpression
      value: '(^|\\s)init_on_free=1(\\s|$)'
      operation: match
      datatype: string
      match: all
      existence: some

tests:
  test-bls-options-contain-init-on-free-1:
    capability: independent.textfilecontent54
    object:
      # BLS collection lives here because only this Test uses it.
      capability: independent.textfilecontent54
      select: ...
    states:
      - state-independent-textfilecontent54

  test-grub-cmdline-linux-arguments-in-etc-default-grub-contain-init:
    capability: independent.textfilecontent54
    object:
      # /etc/default/grub collection lives here.
      capability: independent.textfilecontent54
      select: ...
    states:
      - state-independent-textfilecontent54
```

This is the desired boundary: **inline the two private Objects; do not duplicate
the shared State.**

## Windows Server 2025 SV-278111 — private registry Object and State

Requirement: File Explorer shell protocol must run in protected mode.

```yaml
tests:
  test-turn-off-shell-protocol-protected-mode-set-disabled:
    test_title: "'Turn off shell protocol protected mode' is set to 'Disabled'"
    capability: windows.registry

    object:
      capability: windows.registry
      select:
        hive:
          operation: equals
          datatype: string
          value: HKEY_LOCAL_MACHINE
        key:
          operation: equals
          datatype: string
          value: SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer
        name:
          operation: equals
          datatype: string
          value: PreXPSP2ShellProtocolBehavior

    check_existence: any_exist
    check: all

    states:
      - capability: windows.registry
        state:
          all:
            - field: type
              value: reg_dword
              operation: equals
              datatype: string
              entity_check: all
              entity_existence: at_least_one_exists
            - field: value
              value: 0
              operation: equals
              datatype: integer
              entity_check: all
              entity_existence: at_least_one_exists

    reported_elements: all
```

Again, this is essentially current SCAP-NG with less indirection—not an Ansible
module abstraction.

## Windows Server 2025 SV-278028 — complex dataflow stays named

The FTP system-drive Rule is useful because it prevents the proposal from
degenerating into "inline everything."

Its transformed Assessment still has Assessment-scoped Objects such as:

```yaml
objects:
  get-website-bindings-filter-applied-ones-that-include-ftp-object:
    capability: windows.appcmd
    ...

  get-boot-drive-object:
    capability: independent.environmentvariable58
    ...

  get-program-files-directory-object:
    capability: independent.environmentvariable58
    ...

variables:
  update-variable:
    expression:
      concat:
        - ...
        - values:
            object: get-website-bindings-filter-applied-ones-that-include-ftp-object
            field: identifier
        - ...

  boot-drive-forward-slash-added-variable:
    expression:
      concat:
        - values:
            object: get-boot-drive-object
            field: value
        - ...
```

Those Objects stay named because Variables depend on them.

The shellcommand Objects used only by their individual Tests move inline:

```yaml
tests:
  test-if-site-includes-root-drive-this-finding:
    capability: independent.shellcommand

    object:
      capability: independent.shellcommand
      collect:
        shell: powershell
        command:
          variable: update-variable
        pattern: ''
        error_if_exit_status_not_0: false
        error_if_stderr_exists: false

    check_existence: none
    check: all
    reported_elements: all
```

That is precisely the behavior this research is trying to test: uncomplicated
private mechanics stay local; reusable dataflow nodes remain visible as a graph.
