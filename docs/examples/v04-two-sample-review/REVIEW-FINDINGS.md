# Findings from two complete Rule/Assessment authoring excerpts

**2026-10-30. Review-only, source-pinned SCAP-NG 0.4.0.**
Source/content blockers are tracked in [#265](https://github.com/vanderpol/scap-ng/issues/265);
the bounded inherited-field syntax work remains in [#264](https://github.com/vanderpol/scap-ng/issues/264).

## Immediate conclusions

| Severity | Finding | Evidence and action |
| --- | --- | --- |
| **Blocker for public-ready full Benchmark** | `direct-slice` is the same Benchmark ID in **all 60 native Benchmarks** in the 65-stream human-v2 archive. | The Windows 11 and RHEL 9 originals both use this identity. Give Benchmarks stable distinct logical IDs *from source provenance*, then check cross-Benchmark packaging. The sample slices have separate `*-authoring-review` IDs solely to compile independently. |
| **Blocker for deployed applicability** | The original 60 generated Benchmarks all have `fixture-platform` and `fixture-applicability`, with empty applicability conditions. | The sample retains these markers; a real publisher applicability contract is needed before this content is scanner-ready. Do not infer an OS applicability check from a STIG title. |
| **Confirmed cross-stream compilation blocker** | Even after giving the sample Benchmarks distinct IDs, combining the two four-file excerpts fails with `duplicate logical identity applicability/fixture-applicability`. | Compiler rejection independently reproduces the shared placeholder-ID defect. Resolve applicability identities and actual checks from source before composing multi-Benchmark bundles. |
| **Blocker for claiming complete STIG conversion** | The originals are labeled `[AUTOMATED PROTOTYPE SUBSET]`; only converted automated Rule/Assessment candidates appear in native authoring, while additional manual, blocked, and source-only Rules remain in separate records. | Never advertise the current 65-stream technical archive as complete, accepted Benchmark policy. Restore full source Rule/manual coverage in a separate release track. |
| **Authoring UX** | The Windows registry Test redundantly repeated two field quantifiers and an AND for one original OVAL State. | `SV-253475` candidate uses inherited `field_requirement` and one `fields` mapping, with exact inverse State/Test ledger. The schema already allowed this. |
| **Authoring UX** | The RHEL 9 `mount_options` Test has a single predicate and an explicit non-default `values_matching: one_or_more`. | Leave the local field controls explicit: Test-wide hoisting provides no readability benefit for one field. |
| **Authoring UX / source fidelity** | Full Rule `discussion` strings retain literal `<VulnDiscussion>`, `<FalsePositives>` and other XCCDF XML wrappers, many of them empty. | Strip wrappers only after a structured, lossless content-metadata mapping is reviewed. Preserve meaningful nonempty subfields in other Rule metadata/provenance. |
| **Authoring UX / schema** | Rule schema v0.4 requires numerous empty fields (`warnings: []`, `extensions: {}`, `references: []`, `remediation: {}`, `rationale: null` etc.). | Review which metadata fields may safely be omitted in human-authored Rules without changing compiler or Results semantics. Not altered in this sample. |
| **Authoring UX / stable IDs** | Private Test and Assessment logical IDs still embed long title-derived slugs and hash fragments despite clean `SV-...` filenames. | Review native identity conventions separately; never rename without updating Rule references, compilation, and migration provenance. |
| **Source logic review** | RHEL 9 `/home` selection uses the source-derived `.*\/home` regex without an end anchor. | Confirm original OVAL intent for nested/sibling paths; this sample preserves the source expression and makes no assumption that it only selects `/home`. |

## Reference and validation checks performed

- Both sample Rules point to the Assessment IDs that actually exist in their
  respective sample folders; no fabricated shared Assessment paths.
- Windows registry Object specifies hive, key and value name; Test checks
  DWORD type and integer value 1. Its original source trace shows exactly
  one State. No Windows registry predicates or quantifiers were discarded.
- RHEL 9 Test explicitly separates Item existence (`items_found`), Item
  matching (`items_satisfying`), and `mount_options` value matching.
- The sample Benchmarks each reference exactly their one Rule. Original
  Profile lists were removed because they cover the complete original
  converted subset, not one-Rule excerpts. This is **sample construction**,
  not a proposed lossless Benchmark normalization.
- Schema validation: **8 of 8** native YAML documents valid against 0.4.0.
- Native static package compilation: **2 of 2** isolated sample slices built.
- Combined sample compilation: **rejected as expected** by the current
  identity validator because both still use source-generated
  `fixture-applicability`; do not report combined-bundle readiness.
- Independent original OVAL/native term comparison for the compacting
  converter was previously tested on pinned Windows registry fixtures under
  [#264](https://github.com/vanderpol/scap-ng/issues/264). The specific
  Windows 11 source revision in this review is trace-bound but has **not**
  received a new independent whole-Rule six-state scanner proof.
- Scanner execution, actual system collection, publisher signing/trust,
  applicability execution, and OVAL Board review: **NOT VERIFIED**.

## Suggested sequence

1. Review the two linked Assessments and Rules with the owner; accept or
   adjust the one-State compact syntax and single-field exception.
2. Fix full-Benchmark identity and applicability separately from predicate
   compaction. Both are prerequisite to presenting a scanner-ready full STIG.
3. Review XCCDF Rule text normalization and required-empty-field policy.
4. Expand the approved syntax/source transformation to representative other
   Tests, including OR branches, record predicates, absence and Variables.
5. Publish a new **immutable** human-v3 archive after regenerated provenance,
   program hashes, statuses and links have been independently rechecked.
