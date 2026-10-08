# SCAP-NG 0.3 modernization review guide

This is the primary owner/Board authoring-review path for the stable 0.3 candidate.
It maps every accepted 0.3 modernization to real converted STIG content or, where
automatic conversion must remain fail-closed, to a production-derived native
authoring example.

When reading this file inside the generated review package, paths below are
relative to the package root.

**Provenance rule for Board examples:** Start with actual DISA STIG checks.
For each modernization, record the source Rule ID and legacy mechanism,
native representation, change achieved, and how semantic correctness was
verified. Native examples derived from real checks must remain identified
as *authored research*, not converter output. Hypothetical policy fixtures
are not evidence of newly automating a manual STIG Rule.

## Modernization coverage

| 0.3 decision | Production example | Review status |
| --- | --- | --- |
| Consumer-local Object/State | RHEL 9 SV-257923 | mechanically converted |
| Assessment-scoped `shared_objects` | RHEL 9 SV-258029 | mechanically converted |
| Typed static literal arrays | RHEL 9 SV-257923 | mechanically converted |
| `variable.value` instead of legacy Variable Object plumbing | RHEL 9 SV-258045 | mechanically converted |
| Simple collection `for_each` | RHEL 9 SV-258029 | mechanically converted |
| Correlated nested `for_each` | Windows Server DNS SV-259388 | production-derived native authoring; legacy PowerShell loop intentionally not guessed |
| Localized Set/Filter structure | Oracle Linux 9 SV-271608 | mechanically converted |
| Meaningful typed component IDs | all candidate trees; RHEL 9 SV-258029 is compact | mechanically converted/schema enforced |
| Explicit multi-Test `evaluate` | Windows Server DNS SV-259388 | mechanically preserved |
| Observation | measured only | deferred beyond normative 0.3; no syntax emitted |

## 1. Consumer-local components plus a genuinely shared Object

**RHEL 9 — SV-258029**

Artifact paths:

- `benchmarks/rhel9/faithful-authoring/assessments/automated/benchmark.rhel_9.SV-258029.automated.assessment.yaml`
- `benchmarks/rhel9/candidate-authoring/assessments/automated/SV-258029.automated.yaml`

The dconf database acquisition remains named as
`dconf-database-directories-object` because another collection must reference
it. The target text-file Object and State live directly at the Test because they
are private to that consumer. The boundary is intentional: local by default,
named when reuse/reference identity is real.

## 2. Static typed values without Variable plumbing

**RHEL 9 — SV-257923**

Artifact paths:

- `benchmarks/rhel9/faithful-authoring/assessments/automated/benchmark.rhel_9.SV-257923.automated.assessment.yaml`
- `benchmarks/rhel9/candidate-authoring/assessments/automated/SV-257923.automated.yaml`

The fixed system-library directory list is emitted directly as a typed literal
collection such as `[/lib, /lib64, /usr/lib, /usr/lib64]`. Source-equivalent
`variable_match` remains explicit. Only compile-time constants are folded;
genuine runtime/dataflow Variables remain named.

## 3. Direct Variable evaluation without a legacy Variable Object

**RHEL 9 — SV-258045**

Artifact paths:

- `benchmarks/rhel9/faithful-authoring/assessments/automated/benchmark.rhel_9.SV-258045.automated.assessment.yaml`
- `benchmarks/rhel9/candidate-authoring/assessments/automated/SV-258045.automated.yaml`

This real UID-uniqueness check keeps its meaningful computed Variables but
removes the OVAL Variable Object indirection. The Test uses capability
`variable.value` directly against the named computed value.

## 4. Runtime collection `for_each`

**RHEL 9 — SV-258029**

The same RHEL dconf example contains the proven automatic
ObjectComponent → Variable → selector rewrite. The candidate states the actual
collection intent directly:

```yaml
for_each:
  item: item
  in: dconf-database-directories-object
select:
  directory:
    from: item.directory
```

This expands one collection. It does not create one Test per Item or alter
Test/`evaluate` aggregation.

## 5. Nested `for_each`: production DNS use case, fail-closed conversion

**Windows Server DNS — SV-259388**

Artifact paths:

- `benchmarks/windows-server-dns/faithful-authoring/assessments/automated/benchmark.ms_windows_server_dns.SV-259388.automated.assessment.yaml`
- `benchmarks/windows-server-dns/candidate-authoring/assessments/automated/SV-259388.automated.yaml`

The legacy content collects forward zones, then embeds another loop in
PowerShell to enumerate A/AAAA hosts, construct FQDNs, resolve them, and count
RRSIG records. That production pattern motivated correlated nested collection
iteration.

The native 0.3 authoring shape is:

```yaml
shared_objects:
  forward-zones-object:
    capability: windows.dns.zone
    ...

  hosts-object:
    capability: windows.dns.record
    for_each:
      item: zone
      in: forward-zones-object
    select:
      zone:
        from: zone.name

  rrsig-responses-object:
    capability: windows.dns.query
    for_each:
      item: host
      in: hosts-object
    select:
      name:
        from: host.fqdn
      zone:
        from: zone.name
```

This demonstrates the accepted nested-`for_each` language requirement and its
correlated outer lineage. It is deliberately **not** substituted into the
converted candidate: the current converter cannot prove equivalence for
arbitrary PowerShell bodies, so SV-259388 remains faithful shellcommand content.
That is fail-closed migration working as intended.

## 6. Set and Filter semantics remain explicit

**Oracle Linux 9 — SV-271608**

Artifact paths:

- `benchmarks/oracle-linux9/faithful-authoring/assessments/automated/benchmark.oracle_linux_9.SV-271608.automated.assessment.yaml`
- `benchmarks/oracle-linux9/candidate-authoring/assessments/automated/SV-271608.automated.yaml`

The candidate localizes the two SSSD text-file acquisitions into the Test but
preserves their UNION/Object structure. SCAP-NG removes needless naming
indirection; it does not hide meaningful Set or Filter semantics.

## 7. Explicit `evaluate` where composition is real

**Windows Server DNS — SV-259388**

The candidate retains an `any` tree containing two direct Tests and one nested
`all` group. This is genuine decision structure for which explicit
`evaluate` remains useful.

For contrast, SV-271608 has a one-Test `evaluate` root. 0.3 deliberately keeps
one canonical composition model rather than adding a second implicit execution
form.

## 8. Meaningful component IDs

Use RHEL 9 SV-258029 and SV-258045 while reviewing naming. Named components use
descriptive kebab-case IDs with the appropriate type suffix (`-object`,
`-state`, `-variable`, `-test`, `-input`). Private inline components do
not receive artificial IDs merely to satisfy the convention.

## 9. Deferred Observation boundary

Observation is deliberately **not** rendered into the 0.3 candidate tree.
Scorecards report proven future reuse opportunities so the benefit remains
measurable, but no second cross-Assessment execution interface is added to 0.3.

## Inherited core features

Conditional evaluation, Organizational Input, explicit `reported_elements`,
manual Assessments/results, profiles/tailoring, applicability, packaging, and
compact results are part of the broader SCAP-NG design but are not new 0.3
modernization transformations. The
[examples tour](../../specification/examples/README.md) covers those separately.

## Then browse the complete trees

Each benchmark directory in the generated package contains:

- `SCORECARD.md` — structural modernization counts;
- `faithful-authoring/` — fidelity-first conversion;
- `candidate-authoring/` — currently proven exact/reversible automatic modernizations.

The complete trees verify that the examples above are not synthetic exceptions.
Raw engineering evidence, residual dumps, and migration-audit JSON are
intentionally excluded from the human-review package.
