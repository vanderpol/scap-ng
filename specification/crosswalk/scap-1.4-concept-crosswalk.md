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
| Platform | XCCDF platform + CPE applicability + OVAL inventory logic | explicit named Platform bound to ordinary Assessment logic; Platform/Inventory Assessment MAY also emit standardized product identifiers such as CPE into target inventory |
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

## CPE inventory compatibility note

SCAP 1.4 uses OVAL inventory definitions to determine whether a product is
present and associates those inventory checks with CPE names. SP 800-126r4
further uses the resulting target CPE set as input to CPE/XCCDF applicability.

SCAP-NG preserves the product-inventory half of that behavior:

    Platform/Inventory Assessment -> observed product -> target inventory CPE

SCAP-NG intentionally does not make the emitted CPE an implicit input to Rule
selection or applicability. CPE-based applicability, if standardized later,
would be an explicit separate capability/profile.

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


## Check-selection compatibility note

SCAP-NG **check selector** is the semantic successor to XCCDF selectable
`check` alternatives and their selector-driven refinement/tailoring behavior.
The governing policy exposes named alternatives; effective policy selects one;
the selected alternative resolves to an Assessment Method.

This preserves the ability for legacy content or tailoring to select, for
example, a manual alternative in place of an automated check without requiring
the Benchmark Rule to reference an implementation directly.

Missing requested selectors are resolution errors, not requests for default
fallback. Stage-1 migration preserves this behavior losslessly or reports a
conversion blocker.


## Assessment-class compatibility

SCAP-NG preserves the OVAL definition-class distinction as Assessment
`class`.

| SCAP-NG class | OVAL analog | Status |
| --- | --- | --- |
| `compliance` | OVAL `compliance` | retained |
| `vulnerability` | OVAL `vulnerability` | retained |
| `patch` | OVAL `patch` | retained |
| `inventory` | OVAL `inventory` | retained |
| `miscellaneous` | OVAL `miscellaneous` | retained |
| `information` | none | candidate only; requires OVAL Board / SCAP-NG governance approval |

SCAP-NG adds a separate Assessment `purpose` concept so that the same
Assessment semantics may be invoked for ordinary evaluation or applicability
without changing the Assessment's class.

<!-- spec-nav:start -->

---

**Specification navigation:** [← Previous: Security Considerations](../security/security-considerations.md) · [Contents](../README.md) · [Next: SP 800-126r4 Concept Review for SCAP-NG →](sp800-126r4-concept-review.md)

<!-- spec-nav:end -->
