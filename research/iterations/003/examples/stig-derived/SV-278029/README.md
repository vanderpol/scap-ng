# SV-278029 — Windows Server 2025 time source: an author-readable NG research sample

**Review status: READY FOR AUTHOR READABILITY REVIEW; NOT EXECUTABLE OR VERIFIED CONVERSION.**
Source: DISA Microsoft Windows Server 2025 STIG, **WN25-00-000440 / V-278029**, V1R3 DoW wording (check against pinned authoritative package for final freeze).
- [V1R3 published rule context](https://cyber.trackr.live/stig/Windows_Server_2025/1/3)
- [V1R1 full check wording](https://stigaview.com/products/winserv2025/v1r1/WN25-00-000440/)
- [V1R3 time-source rule mirror](https://www.tenable.com/audits/items/DISA_STIG_Microsoft_Windows_Server_2025_v1r3.audit%3Aa35fc0fcb9d2f649544323ef3a52566b)

**What this example proves:** the *human readability of a proposed native representation* of a real, conditional STIG check. **What it does not prove:** a working Windows collector, exact OVAL/SCAP 1.4 equivalence, semantic conformance, completed Organizational Input implementation, or actual Windows target evaluation.

## What the real Rule asks

- A domain-joined server **other than the domain controller holding the PDC Emulator role** must have Windows Time NTP Client `Type=NT5DS`.
- For other hosts (standalone/non-domain-joined and the **PDC Emulator**), where Windows Time Client `Type=NTP`, a configured `NtpServer` must identify an authorized DoW (formerly DoD) time source.
- The published text does **not clearly state** what constitutes a passing result for `Type` values other than `NTP` in the second branch. This unresolved branch must not be silently treated as pass.
- The source prescribes `w32tm /query /configuration` and `Get-ADDomain | FT PDCEmulator`. These reveal configuration/role, not evidence of successful live clock synchronization.

## Proposed NG authoring sketch — deliberately **NOT** current validated 0.3 YAML

The excerpt below is an *intent-level proposal* to judge readability. `collect`, `if`, `then`, `else`, `return`, `is_in`, and `observed` are **pseudocode** in this document. No claim is made that the existing 0.3 JSON Schema accepts them. Separate the policy inputs and collection contract from the conditional assessment.

```yaml
# PSEUDOCODE ONLY — not a schema-valid or executable Assessment
assessment: SV-278029.time-synchronization
inputs:
  authorized-time-sources-input:
    type: list<string>
    required: for-ntp-branch
    supplied_by: approved-organizational-input-set
collect:
  domain-joined: windows.domain.membership
  local-host: windows.host.identity
  pdc-emulator: windows.active-directory.pdc-emulator
  time-type: windows.time.ntp-client.type
  time-servers: windows.time.ntp-client.servers

evaluate:
  if: domain-joined and local-host != pdc-emulator
  then:
    require: time-type == NT5DS
  else:
    if: time-type == NTP
    then:
      require: time-servers is_in authorized-time-sources-input
    else:
      return: unknown  # source Check Text does not settle this branch
```

The branch must **not** be chosen using a failed PDC lookup or unknown domain membership. Such a case is `unknown` (or `error` for actual collector failure), not an arbitrary `else` selection. The exact quantifier for multiple configured NTP peers, hierarchy, aliases and flags needs source/policy validation. Likewise `is_in` is explanatory wording, not approved 0.3 `in` syntax.

## Organizational Input: reusable environment-level example

This is **illustrative policy data**, not a DoW-approved time source list. Fictitious `.example.test` hostnames must not be taken as authorization:

```yaml
# PSEUDOCODE; pending finalized author-generated Input Set template schema
organizational_input:
  id: example.enterprise-time-policy
  benchmark: Windows-Server-2025
  values:
    authorized_time_sources:
      - ntp-a.example.test
      - ntp-b.example.test
  provenance:
    organization: Example Organization
    supplied_by: Example Network Security Team
    authorization_status: approved
```

The publisher's Benchmark declares the required Parameter, the Rule binds it to `authorized-time-sources-input`, and the Assessment consumes it only in the NTP branch. The request explicitly binds the Input Set to the selected fleet context; it is not discovered by reading a host's current time sources. No per-host Benchmark fork is required for a common enterprise time policy. Validate every required provenance field and scope before execution.

## Example *expected* results to review (invented data; no scanner run)

| Host | Domain joined? | PDC Emulator? | Type | NtpServer | Expected interpretation |
| --- | --- | --- | --- | --- | --- |
| member-01 | Yes | No | NT5DS | irrelevant | **pass**: domain member uses NT5DS |
| member-02 | Yes | No | NTP | ntp-a.example.test | **fail**: this branch requires NT5DS |
| pdc-01 | Yes | Yes | NTP | ntp-a.example.test | **pass candidate**, conditional on approved set and peer parser semantics |
| standalone-01 | No | N/A | NTP | unauthorized.example.test | **fail**: source not approved |
| standalone-02 | No | N/A | NTP | ntp-a.example.test | **not_evaluated** if required approved Input Set absent |
| member-03 | Yes | Unknown | NTP | ntp-a.example.test | **unknown/error**: cannot safely choose a branch |
| standalone-03 | No | N/A | NT5DS | none | **unresolved**: second-branch non-NTP behavior not specified clearly enough to assert pass |

Example human result format, **not** validated result-schema output:

```text
Rule SV-278029 — FAIL
Host: member-02
Selected branch: Domain-joined, not PDC Emulator
Observed: NTP Client Type = NTP
Required: NTP Client Type = NT5DS
Reason: Windows Time configuration does not meet the domain-member requirement
```

## Open correctness gates before Board release

1. Pin the exact **authoritative** V1R3 DISA package/check revision and verify whether it is manual-only in original XCCDF/OCIL/OVAL; source editions differ in DoD/DoW wording.
2. Design and implement supported Windows collectors for **domain membership, authoritative local PDC identity, Windows Time Type, NtpServer parsed endpoints and flags**, with collector completeness and failures.
3. Define the complete decision table (including second branch non-NTP values and multi-server/list membership); seek human policy interpretation where Check Text is underdetermined, **without inventing requirements**.
4. Map native `if`/return syntax to actually supported 0.3 conditional semantics, or explicitly propose changes. Preserve six-state behavior. Resolve rule-level input binding, authorized context, missing input and provenance.
5. Produce a faithful **SCAP 1.4 XCCDF + OVAL mockup** with external values and criteria tree; label implementation and SCAP validation constraints accurately. Compare file count, node count, lines, reader comprehension and semantic parity.
6. Publish compiled, schema-validated, semantic-tested example and illustrative pass/fail/unknown results *only after the implementation succeeds*.

**Reviewer question:** Can a Windows administrator correctly explain the two branches and missing-input outcome from this sketch without knowing OVAL? If not, redesign the NG representation before Board submission.
