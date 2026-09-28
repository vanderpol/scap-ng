# SCAP 1.4 to SCAP-NG Concept Crosswalk

**Status:** informative compatibility crosswalk

This crosswalk identifies the closest SCAP 1.4 analog for current SCAP-NG
concepts and records deliberate divergences.

| SCAP-NG concept | Closest SCAP 1.4 analog | Relationship / intentional divergence |
| --- | --- | --- |
| Benchmark | XCCDF Benchmark | retained as policy container; executable implementation separated |
| Rule | XCCDF Rule | retained; stable identity separated from revision |
| Group | XCCDF Group | retained for meaningful organization; one-Rule wrappers discouraged |
| Profile | XCCDF Profile | retained; native Rule selection is subtractive delta only |
| Tailoring | XCCDF Tailoring | retained as external policy modification; exact Rule-selection powers still under design |
| Parameter | XCCDF Value | expanded to typed policy data with cleaner binding semantics |
| Organizational Input | interactive XCCDF Value + check-export + OVAL external variable | separated from Tailoring; restricted to expected-state data |
| Assessment Method | XCCDF check + OVAL/OCIL implementation | unified semantic successor |
| Manual Assessment | XCCDF Check Text / OCIL manual interaction | Check Text alone is sufficient; default result contract replaces need for questionnaire scaffolding |
| Automated Assessment | XCCDF check + OVAL Definition/Test/Object/State/Variable graph | cleaner native Assessment language; Stage-1 migration remains lossless |
| Capability | OVAL test/object family | portable collector/evaluation interface rather than XML Test element |
| Platform | XCCDF platform + CPE applicability + OVAL inventory logic | explicit named Platform bound to ordinary Assessment logic; no scanner magic |
| Rule applicability | XCCDF platform/refine applicability combinations | explicit reusable applicability conditions composed with Benchmark Platform |
| Applicability catalog | CPE dictionary / XCCDF platform references | explicit Benchmark-scoped ID-to-Assessment mapping |
| Assessment Request | no single direct analog | new run orchestration object |
| Compiled package | source data stream | preserves self-contained distribution goal without XML component container model |
| Result package | ARF + XCCDF TestResult + OVAL Results + asset identification | normalized common result model instead of nested component reports |
| Target identity | ARF AI / XCCDF target facts | retained and normalized with typed stable identifiers |
| Failure reason / decisive explanation | OVAL/XCCDF result graph + messages | standardized compact explanation rather than requiring reconstruction of full component results |
| Stable logical ID | XCCDF/OVAL IDs | retained conceptually; revision is no longer forced into logical identity |
| Publisher extension | XCCDF metadata / foreign namespaces | formal constrained extension surface |
| Historical provenance comments/report | source IDs embedded through component structure | preserved outside scanner semantics where possible |
| SIEM projection | custom post-processing of ARF/XCCDF results | explicit projection from canonical results; denormalization is consumer-specific |

## Important intentional departures

SCAP-NG does not intend to preserve the XCCDF/OVAL/OCIL component stovepipes as
runtime architecture.

SCAP-NG does not require OCIL questionnaire structure for Manual Assessments.

SCAP-NG does not require CPE to be the executable applicability mechanism.

SCAP-NG does not permit Organizational Input to alter collection or execution
semantics.

SCAP-NG does not use Profile positive-selection snapshots for native policy.

SCAP-NG does not require historical provenance to be carried into scanner
objects simply because content was converted from SCAP 1.4.

SCAP-NG does preserve the ability to migrate supported SCAP 1.4 behavior
losslessly before optional native refactoring.
