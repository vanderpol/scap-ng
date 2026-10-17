# DISA versus NIWC/NAVWAR OVAL source attribution

**Verified 17 October 2026 — research only.** This records the **original OVAL element IDs**, not the normalized SCAP-NG Assessment IDs or the organization that packaged the content.

## Verified ID examples

| OVAL element | DISA source | NIWC/NAVWAR source |
| --- | --- | --- |
| Definition | `oval:mil.disa.stig.defs:def:230325` | `oval:navy.navwar.niwcatlantic.scc:def:28103700001` |
| Test | `oval:mil.disa.stig.unix:tst:23032500` | `oval:navy.navwar.niwcatlantic.scc:tst:28103700002` |
| Object | `oval:mil.disa.stig.unix:obj:20000016` | `oval:navy.navwar.niwcatlantic.scc:obj:28103700005` |
| State | `oval:mil.disa.stig.unix:ste:20000017` | `oval:navy.navwar.niwcatlantic.scc:ste:28103700012` |
| Variable | `oval:mil.disa.stig.defs:var:23032500` | `oval:navy.navwar.niwcatlantic.scc:var:28103700016` |

Sources:
- DISA: [RHEL9 SV-257889 preserved source graph](https://github.com/vanderpol/scap-ng/blob/main/research/assessment-simplification/evidence/rhel_9/SV-257889/graph.json) — **2 Definitions, 2 Tests, 5 Objects, 5 States, 2 Variables** in the example closure.
- NIWC/NAVWAR: [RHEL10 SV-281037 original OVAL XML](https://github.com/vanderpol/scap-ng/blob/main/research/iterations/003/evidence/roundtrip-source-oval/U_RHEL_10_SV-281037-oval.xml) — **1 Definition, 3 Tests, 7 Objects, 4 States, 3 Variables** in the preserved XML.
- Reproducible [namespace verification script](https://github.com/vanderpol/scap-ng/blob/main/tools/research_04_source_oval_origin.py), [passing CI](https://github.com/vanderpol/scap-ng/actions/runs/39029699446).

## Critical project-owner source lineage clarification

For the NIWC enhanced SCAP 1.4 data used by this project, **DISA SCAP 1.3 content is carried forward without modifying the imported DISA check logic**. New SCAP 1.4/OVAL 5.12.3 authoring features can therefore appear in NIWC-added content but must not be expected in inherited DISA-origin definitions just because the enclosing NIWC package is labeled SCAP 1.4.

This is the owner's corpus-specific process statement, **not independently established by a complete bitwise comparison of all DISA 1.3 inputs with all SCAP 1.4 releases**. The namespace verifier demonstrates the original source ID convention, not full unchanged-content lineage.

## Research implications

1. **Classify original OVAL element IDs** individually: Definition (`def`), Test (`tst`), Object (`obj`), State (`ste`) and Variable (`var`). Root Definition and referenced reusable elements can have mixed provenance. Separate their identity and lineage.
2. Do not derive source authorship from an NIWC release ZIP, a Benchmark's product name, the package generator, or a normalized SCAP-NG Assessment ID. Preserving explicit source-to-native mapping is necessary after cleaning published authoring files.
3. **Do not infer author preference from legacy feature absence.** The earlier [201-Test `all_exist` `item_creation` census](reports/all-exist-item-creation.md) found 132 `textfilecontent54` cases using `all_object_elements_fullfilled` and three `ntuser` cases using `key_and_name_exist`. These frequencies must not be presented as evidence that authors considered and rejected `filepath_exists` or `every_ntuser` without splitting the Test population by original source ownership.
4. The public curated six-STIG authoring ZIP is intentionally missing original-Oval source/provenance engineering sidecars. A **joined original OVAL XML/IDs dataset** is required to report original-DISA versus NIWC frequency across all 201 Tests; the current 201-Test native report **does not have that per-Test attribution**.
5. Separate two valid goals: **faithful SCAP 1.3/1.4 import** and **better native SCAP-NG authoring**. We can prohibit native phantom absent Items and prefer actual underlying-resource Items as a deliberate new design, but a change to the Item population or six-state results is not a lossless conversion unless proven.
6. Preserve `all_exist` source meaning and special cases until differential provenance-aware testing establishes the correct lowering. Expected resource identities remain distinct from matched collected Items.

For provenance modeling, see [draft content authorship guidance](https://github.com/vanderpol/scap-ng/blob/main/specification/assessment/draft-0.3.0-content-authorship.md). This page introduces no normative schema or change to DISA or NIWC source content.
