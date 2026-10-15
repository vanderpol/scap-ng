# SCAP-NG roadmap

Updated: October 15, 2026. **0.3.0 remains the active pre-alpha release checkpoint**;
0.2.0 is historical and does not require rebuilding as a 0.3 gate.

## Now — finish the 0.3 checkpoint

The [first full 65-source active-0.3 pipeline](https://github.com/vanderpol/scap-ng/actions/runs/37838382899)
**succeeded** on `799d083`: 61 supported generated benchmark packages, four
known nonstandard SQL-extension source blockers, schema and semantic checks,
graph checks, normalization, compilation and test signing.
The [follow-up run](https://github.com/vanderpol/scap-ng/actions/runs/37846666574)
covers subsequent Organizational Input and Result changes and must pass
independently. The [six-benchmark regression](https://github.com/vanderpol/scap-ng/actions/runs/37849528026)
and [current documentation audit](https://github.com/vanderpol/scap-ng/actions/runs/37849528014)
have passed at the later documentation checkpoint.

Finish the final full-corpus gate, reconcile any real correctness failures,
and obtain owner acceptance. Then publish a durable, checksum-identified
review/prerelease package; an expiring Actions ZIP is not the final release
asset. Keep the [release issue](https://github.com/vanderpol/scap-ng/issues/191)
as the single authoritative release checklist.

No new 0.3 feature design is required. Shared Observation and changes to
`evaluate` are deferred; see the
[scope boundary](specification/deferred-after-0.3.md).

## 0.4 — single authoring-language draft (research in progress)

The project-owner-directed [0.4 scope and validation gates](research/assessment-simplification/compact-authoring-04/0.4-SCOPE-AND-RELEASE-GATES.md) propose **one standard human-readable Assessment grammar**, including direct State field names (`owner_uid:` rather than `field: owner_uid`), explicit human-language `require` semantics, typed comparator keys, nested Windows record fields, and preservation of existing Object/State literal arrays and `value_match`. No hidden optional compact dialect and no unrelated `evaluate` redesign.

[Three-benchmark source reconstruction](https://github.com/vanderpol/scap-ng/actions/runs/38737558392) demonstrated representation for all **921** default-automated Linux/Windows Rules; [focused draft syntax validation](https://github.com/vanderpol/scap-ng/actions/runs/38740807220) passed on **942** automated/applicability Assessment fragments. These proofs justify a **draft**, not an approved normative version. Next: finalize readable names and edge outcomes, build a full independent `schema/v0.4.0/` snapshot with capability validation, and run the maintained six-anchor suite before a version checkpoint.

No SCAP-NG scanner exists yet. Implementation/scanner parity is a **later milestone**, not a condition for drafting or adopting authoring syntax. Keep the current 0.3 release and Board vote unchanged until a distinct promotion decision. [Owner research tracking #227](https://github.com/vanderpol/scap-ng/issues/227).

## Next — independent implementation and conformance

Build and exercise a reference evaluator/scanner, compare actual vendor
execution against independently reviewed oracles, and test collected Item
semantics, redaction, evidence retention, signing, caching, offline operation
and enterprise-scale performance. Full automated Self-Assertion
generation/execution/comparison is targeted at 1.0
([#206](https://github.com/vanderpol/scap-ng/issues/206)).

## Later — governance and standards

Stabilize trust and packaging profiles, vendor-facing conformance material,
versioned releases, and the standards path.

[Core objectives](specification/objectives.md) ·
[Current review](review/current/README.md) ·
[Draft specification](specification/README.md) ·
[Issues](https://github.com/vanderpol/scap-ng/issues)
