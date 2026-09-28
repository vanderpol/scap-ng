# SCAP-NG Applicability Design Review and Game Plan

**Status:** active design proposal for native-source review

## Core principle

SCAP-NG applicability is **content-authored assessment logic**.

Anything that can be expressed by the NG assessment language may be used to
determine applicability. Applicability does not use a weaker language and does
not rely on scanner-provided platform opinions such as a normalized
`os_info` record.

The scanner implements collection/evaluation capabilities. The content author
decides what collected evidence means.

## Why this is required

Review of the published four-anchor STIG content shows that applicability is
not merely operating-system identification.

RHEL 9 applicability logic includes conditions such as:

- BIND installed;
- NFS mounts configured / no NFS mounts configured;
- IPv6 enabled;
- Libreswan installed;
- BIOS boot vs UEFI boot;
- FIPS state;
- kernel dumps enabled;
- Postfix installed;
- autofs installed;
- GNOME/session presence;
- bare-metal vs virtual-machine characteristics.

The current RHEL applicability closure uses package, text-file, sysctl, file,
and shell-command collection semantics plus Boolean composition and negation.

Windows Server 2025 applicability includes conditions such as:

- standalone server vs domain member vs domain controller;
- Server Core vs non-Core installation;
- FTP feature installed;
- OpenSSH Server installed.

The current Windows Server applicability closure uses WMI, registry, and
PowerShell/cmdlet collection semantics plus Boolean composition.

Windows 11 also has explicit applicability assessments, but its current
published applicability closure is blocked by an effectively deprecated OVAL
`user_test`. That is source-remediation debt, not a reason to introduce
scanner-side platform inference into NG.

These examples demonstrate that applicability is general executable logic.

## Proposed native model

### Platform is a named policy concept

A platform definition provides a reusable name and optional external aliases:

    platform:
      id: windows11-member-workstation
      title: Windows 11 domain member workstation
      aliases:
        - scheme: cpe
          value: cpe:...

The alias is metadata. It does not produce a result.

### Platform points to an applicability assessment

    platform:
      id: windows11-member-workstation
      assessment: platform.windows11-member-workstation

The referenced object is an ordinary NG assessment.

### Applicability assessment uses normal NG assessment capabilities

Conceptually:

    assessment:
      id: platform.windows11-member-workstation

      collect:
        domain_role:
          windows.wmi:
            namespace: root\cimv2
            query: SELECT DomainRole FROM Win32_ComputerSystem

        product_name:
          windows.registry:
            hive: HKLM
            key: SOFTWARE\Microsoft\Windows NT\CurrentVersion
            value: ProductName

      assert:
        all:
          - domain_role.value == 3
          - product_name.value matches '^Windows 11'

The exact syntax is still under design. The important rule is that these are
ordinary collector/evaluator constructs, not special scanner intelligence.

### Rules reference platform names

    rule:
      id: ...
      applies_to:
        - windows11-member-workstation
      assessment: ...

The scanner evaluates the named platform assessment and then determines whether
the rule is applicable.

## New or obscure platforms

A content author must be able to define applicability for a new platform
without a scanner vendor first adding a platform recognizer.

For example, a Linux Mint or custom-distribution author might use ordinary NG
collectors to inspect:

- `/etc/os-release`;
- vendor release files;
- package-manager metadata;
- installed packages;
- kernel/version facts exposed through low-level collectors;
- filesystem markers;
- configuration values;
- any other collector already supported by the assessment language.

If those collectors are already supported by a scanner, the new platform
content can run immediately. The scanner does not need a release that adds
"Linux Mint recognition."

If the assessment needs a collector the scanner does not implement, the scanner
reports the missing capability. It must not guess applicability.

## Capability negotiation

Every assessment, including applicability assessments, should have
deterministically discoverable required capabilities.

Conceptually:

    requires:
      - windows.registry
      - windows.wmi

or these requirements may be derived automatically from the assessment source.

Before execution a scanner can report:

- supported;
- unsupported collector/capability;
- unsupported language feature/version.

This separates two questions:

1. **Can the scanner execute this applicability assessment?**
2. **Does this target satisfy the applicability assessment?**

Failure of (1) must never be silently converted into false for (2).

## Result model

Applicability should probably use the normal NG result algebra rather than an
artificial Boolean-only evaluator.

At minimum the design must distinguish:

- assessment succeeds and condition is true -> **applicable**;
- assessment succeeds and condition is false -> **not applicable**;
- required collection/evaluation cannot complete -> **applicability unknown/error**.

An error or unsupported capability must not become "not applicable", because
that could hide rules that should have run.

The precise mapping of NG assessment result states to policy processing remains
a source-design question to settle.

## Composition

Applicability may require arbitrary assessment logic:

- AND / OR / NOT;
- existence/cardinality checks;
- collection filters;
- reusable sub-assessments;
- variables and derived values;
- string/regex/numeric/version operations;
- sets and multi-value processing;
- parameters;
- platform-specific collectors;
- future assessment-language features.

There should be no separate applicability expression language that has less
power than assessments.

## Reuse

Named applicability assessments should be reusable across:

- many rules in one benchmark;
- multiple profiles;
- multiple benchmarks;
- related operating systems/products.

A policy may also need a concise inline applicability form for a one-off simple
condition, but that form should compile to the same assessment semantics.

## CPE's role

CPE remains useful for:

- standardized naming;
- catalog lookup;
- interoperability metadata;
- mapping old SCAP content during conversion.

CPE does **not** determine applicability by itself.

If an NG platform carries a CPE alias, the executable truth still comes from
the associated NG applicability assessment.

## Source conversion

For SCAP 1.4 migration:

    CPE language / XCCDF platform
        -> referenced OVAL inventory definition(s)
        -> faithful semantic IR
        -> native NG applicability assessment
        -> named NG platform

Original CPE/XCCDF/OVAL identifiers remain migration provenance, not runtime
dependencies.

## Near-term review plan

Before regenerating full benchmarks:

1. Reconstruct several existing RHEL applicability conditions as concise native
   NG assessments:
   - package installed;
   - NFS mounts;
   - IPv6 enabled/disabled;
   - BIOS/UEFI;
   - FIPS;
   - virtual vs bare metal.

2. Reconstruct several Windows conditions:
   - workstation/member role;
   - domain controller;
   - Server Core;
   - optional Windows feature installed.

3. Add one hypothetical new/obscure Linux distribution example based only on
   ordinary collectors such as `/etc/os-release`.

4. Verify that the same assessment syntax used for compliance rules is
   sufficient for every applicability case.

5. Identify any OVAL applicability semantics that cannot be expressed cleanly.
   Fix the general assessment language rather than adding platform-specific
   scanner magic.

6. Decide the applicability result/error mapping and capability-negotiation
   contract.

7. Only after these examples are understandable to existing SCAP authors,
   regenerate the larger four-anchor source trees.

## Design test

A useful acceptance test for the future specification is:

> Can a content author define a previously unknown operating system, product,
> role, feature, or configuration-based applicability condition using only the
> documented NG assessment language and collectors already supported by a
> scanner?

If yes, the scanner does not need special knowledge of that platform.

If no, the applicability design is too scanner-dependent.
