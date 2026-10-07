# SCAP 1.4 → SCAP-NG 0.3: key changes

**Status:** concise OVAL Board briefing for the forthcoming SCAP-NG 0.3 pre-alpha review checkpoint. Nothing here implies Board approval.

For examples, start with the [SCAP-NG feature tour](../specification/examples/README.md). For the active review package and build, use [review/current](../review/current/README.md). Detailed research remains linked from the relevant issues rather than duplicated here.

## Why SCAP-NG

SCAP-NG keeps useful SCAP 1.4 / OVAL assessment meaning while removing XML-era indirection that makes content difficult to author, debug, execute, and consume.

The migration rule remains simple: **supported SCAP 1.4 meaning must be preserved; unsupported or deprecated semantics are explicit blockers rather than guesses.**

## Major changes

- **Benchmark → Rule → Assessment.** Rules contain policy requirements and available Assessment choices. Automated and manual Assessments are standalone, independently valid units.
- **Objects and States are local when they are private.** Ordinary one-consumer acquisition/predicate structure is authored beside its semantic consumer instead of in large ID registries. Components stay named when identity/reuse is meaningful.
- **Named components are searchable and predictable.** Native 0.3 IDs use meaningful kebab-case names ending in their type: `-object`, `-state`, `-variable`, `-test`, and `-input`. JSON Schema enforces the convention.
- **Variables represent real runtime dataflow, not XML plumbing.** Fixed literals and simple private bindings can be expressed locally. Named Variables remain for genuine shared/chained runtime computation.
- **Collection iteration is explicit.** `for_each` expresses runtime expansion over collected Object data instead of ObjectComponent → Variable → target-Object plumbing or shell-script loops. Nested collected-data iteration is being finalized from real DNS production patterns.
- **Evaluation logic stays explicit.** Named Tests and `evaluate` preserve genuine multi-Test decision trees and the OVAL-derived result domain. Existing 0.2 `if/then/else` behavior is inherited; arbitrary Boolean OVAL criteria are not automatically rewritten as procedural conditionals.
- **Applicability is executable content, not scanner magic.** CPE/platform identifiers may be captured as inventory, but applicability comes from explicit assessment logic.
- **Organizational Input is typed policy data.** Organization-supplied expected values have explicit contracts/provenance and do not rewrite Tests or inject executable logic.
- **No hidden semantic defaults.** Choices that affect collection, comparison, evaluation, reporting, or results must be explicit or intrinsic to one narrowly specified construct.
- **Deprecated OVAL Tests are migration blockers.** They are not copied into NG with a runtime `deprecated` flag.
- **OVAL 5.12.3 is the primary migration semantic baseline.** Later corrections/new-Test work is reviewed explicitly.
- **Source defects are not silently repaired.** Migration and remediation are separate actions.
- **Packaging is native and manifest-based.** The SCAP datastream is replaced by a deterministic, integrity-bound SCAP-NG package; logical identity does not depend on archive paths.
- **Results are smaller and more useful.** Benchmark/Rule results provide compact counters and reasons; detailed Assessment results preserve decisive technical evidence without reproducing ARF/OVAL Results wholesale.
- **Evidence can be bounded without hiding incompleteness.** Result metadata distinguishes logical, population, and evidence completeness and records truncation/stop reasons.
- **Manual Assessments are first-class.** Manual procedures and results use the same Rule → Assessment lifecycle and record assessor/time/evidence information.
- **Profiles and Tailoring have narrower jobs.** Publisher Profiles are compact policy variations; local Tailoring is separate. Interactive scanner mutation of Tests is not part of the model.
- **Conformance is broader than JSON Schema.** Structural validation, semantic graph validation, known-result behavior, acquisition/collector conformance, migration equivalence, and independent scanner/live-target evidence are separate evidence layers.

## 0.3 modernization focus

The most important 0.3 authoring improvement is **locality**: eliminate named component indirection when a component is private, while retaining explicit identity when it is genuinely shared.

Current production evidence includes the full 65-package NIWC corpus and the maintained six-benchmark review set: RHEL 9, Oracle Linux 9, Windows 11, Windows Server 2025, Windows Server DNS, and Apache 2.4 UNIX Server.

The 0.3 checkpoint also includes or is finalizing:

- native component-ID suffix conventions;
- native static literal collections where lossless;
- runtime collected-data `for_each`, including nested iteration research from DNS;
- the final boundary for shared/referenceable Objects after locality;
- the disposition of shared Observation/data-provider reuse;
- concise root-cause and bounded-evidence results;
- SCAP 1.4 forward-conversion accounting and explicit blockers.

See the [0.3 agenda](https://github.com/vanderpol/scap-ng/issues/174) and [Board checkpoint gate](https://github.com/vanderpol/scap-ng/issues/191) for the exact status of open decisions.

## What the Board should review

Please focus on:

1. **semantic fidelity** — whether supported OVAL/SCAP 1.4 meaning is preserved;
2. **author readability** — whether the modernized Assessment makes the technical intent easier to understand and debug;
3. **interoperability** — whether any proposed simplification leaves scanner behavior ambiguous;
4. **results usefulness** — whether the result contract is compact without losing decisive evidence or completeness;
5. **missing production cases** — especially real content patterns that are not represented by the six-benchmark package or migration census.

0.2 is preserved for historical comparison, but it is no longer the active Board review target.
