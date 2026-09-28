# Platform, Applicability, and Compliance Roles

**Status:** working design decision for iteration 002

SCAP-NG should keep three concepts distinct even though all executable logic is
evaluated by the same assessment language.

## 1. Platform

A platform identifies the product or operating-system family/version that a
benchmark targets.

Examples:

    windows.11
    windows.server-2025
    rhel.9
    oracle-linux.9

A platform has an executable NG assessment that determines whether the target
is that platform. That assessment may use any normal NG capability required to
prove the identity.

A platform is **not** a role such as domain controller, member workstation,
GNOME installed, or FIPS enabled.

## 2. Applicability condition

An applicability condition is a reusable condition about a target that is
already within a platform population.

Examples:

    windows.member-workstation
    windows.domain-controller
    windows.server-core
    linux.gnome-installed
    linux.nfs-mounted
    linux.fips-enabled

These conditions are intentionally independent of a particular benchmark
version when the underlying test is reusable.

For example, `windows.member-workstation` may be implemented using WMI or
PowerShell semantics that are valid across multiple Windows releases. Windows
7, 8, 10, and 11 benchmarks can all reference the same applicability
assessment when its semantics are valid for those releases.

Likewise, `windows.domain-controller` can be reused by multiple Windows Server
benchmarks.

## 3. Compliance assessment

A compliance assessment determines whether a configuration requirement is
satisfied.

Examples:

    windows.password-expiration
    unix.grub-config-owned-by-root

Compliance assessments must not contain platform identity merely because a
benchmark happens to target that platform.

## Benchmark and rule composition

A benchmark names its platform:

    benchmark:
      id: windows11-stig
      platform: windows.11

Most rules inherit that platform automatically and need no applicability
syntax.

A rule adds only the additional condition that makes that rule relevant:

    rule:
      id: example-domain-rule
      when:
        - windows.member-workstation
      assessment: windows.example-setting

The effective applicability is:

    benchmark platform
    AND
    rule applicability conditions

Thus:

    Windows 11 benchmark + member-workstation rule
      -> windows.11 AND windows.member-workstation

and:

    Windows Server 2025 benchmark + domain-controller rule
      -> windows.server-2025 AND windows.domain-controller

The reusable role/configuration condition is not duplicated into each platform
definition.

## Repository organization

The source layout should make the distinction obvious:

    source/
      platforms/
        windows/
          11.yaml
          server-2025.yaml
        linux/
          rhel-9.yaml
          oracle-linux-9.yaml

      applicability/
        windows/
          member-workstation.yaml
          domain-controller.yaml
          server-core.yaml
        linux/
          gnome-installed.yaml
          fips-enabled.yaml
          nfs-mounted.yaml

      assessments/
        windows/
        unix/
        linux/

      benchmarks/
        windows11-stig/
        windows-server-2025-stig/
        rhel9-stig/
        oracle-linux9-stig/

These directories describe **authoring intent**, not different evaluator
languages. Platform assessments, applicability assessments, and compliance
assessments use the same NG assessment semantics and collector capabilities.

## Design consequence

Do not create composite pseudo-platforms such as:

    windows11-member-workstation
    windows-server-2025-domain-controller

unless an external interoperability requirement specifically needs such a
label.

Native policy should prefer explicit composition:

    windows.11
      AND windows.member-workstation

because it maximizes reuse and makes the source intent clear.
