# Conditional authoring examples

> **RESEARCH ONLY — illustrative syntax, not accepted SCAP-NG.**

## Windows Server 2025 SV-278001

Requirement behavior in the source is role-sensitive: the expected
`HKEY_LOCAL_MACHINE\\SYSTEM` permissions differ for a Domain Controller and a
non-DC server.

A human-oriented representation could look approximately like:

```yaml
check:
  all:
    - registry:
        hive: HKEY_LOCAL_MACHINE
        key: SECURITY
      expect:
        permissions: windows_server_default

    - registry:
        hive: HKEY_LOCAL_MACHINE
        key: SOFTWARE
      expect:
        permissions: member_server_default

    - case:
        when:
          windows_role: domain_controller
        then:
          registry:
            hive: HKEY_LOCAL_MACHINE
            key: SYSTEM
          expect:
            permissions: domain_controller_default
        otherwise:
          registry:
            hive: HKEY_LOCAL_MACHINE
            key: SYSTEM
          expect:
            permissions: member_server_default
```

The names above are placeholders. The key point is that the role decision is
locally visible instead of encoded as an OR of two AND branches with one
positive and one negated role Test.

## RHEL 9 SV-258004

The source chooses how to check `KerberosAuthentication` depending on whether
the main sshd configuration includes `sshd_config.d`.

```yaml
check:
  case:
    when:
      sshd:
        includes: /etc/ssh/sshd_config.d/*.conf
    then:
      sshd:
        effective:
          KerberosAuthentication: "no"
    otherwise:
      text:
        path: /etc/ssh/sshd_config
        setting:
          KerberosAuthentication: "no"
```

Again, the syntax is speculative. This example is useful because it looks like
a true configuration-dependent branch, unlike the kernel-module examples below.

## RHEL 9 module-disable Rules: keep `any`

These branches represent alternative acceptable configuration locations rather
than a guard selecting exactly one requirement:

```yaml
check:
  any:
    - all:
        - text:
            path: /etc/modprobe.d/*
            contains: "install atm /bin/false"
        - text:
            path: /etc/modprobe.d/*
            contains: "blacklist atm"

    - all:
        - text:
            path: /etc/modprobe.conf
            contains: "install atm /bin/false"
        - text:
            path: /etc/modprobe.conf
            contains: "blacklist atm"
```

This is intentionally **not** rewritten as if/else.

## Migration caution

None of these examples authorizes automatic Boolean-to-conditional conversion.
A converter must retain the original six-state result behavior unless a
specific equivalence contract is proven.
