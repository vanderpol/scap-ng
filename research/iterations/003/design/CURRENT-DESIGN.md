# Current SCAP-NG design

**Authoritative working-design checkpoint.** Historical experiments, generated trees, old proposal prose, and dated transition notes do not override this file. Material decisions should be reflected here when accepted by the project owner.

**Current status:** SCAP-NG 0.3.0 is the active pre-alpha development line. SCAP-NG 0.2.0 remains the frozen earlier review baseline at `7cd8b1242d7fb4a2eb9b5f49c7ec3f48b2dd622d`.

## Architecture

- Compliance/vulnerability content uses **Benchmark → Rule → Assessment**. There is no separate Policy object/file.
- A Rule owns requirement/policy metadata, applicability references, named Assessment choices/selectors, and the default choice.
- An Assessment owns the automated or manual evaluation method.
- Rule policy disposition (including current `role` handling for informational use) is separate from Assessment technical truth.

## Profiles, Tailoring, Parameters, and input

- Benchmark membership enables Rules by default.
- Publisher Profiles are subtractive: they may disable Rules and do not re-enable ancestor-disabled Rules.
- External Tailoring may enable/disable existing Rules and choose among publisher-provided Assessment choices.
- Tailoring SHALL NOT replace Assessment implementations or override publisher Parameter values.
- Delegated organization-specific values use typed Organizational Input. A materially different requirement needs distinct policy identity.
- Tailoring provenance should identify purpose, creator/modifier/authorizer, dates, organization, and authorization reference/status.

## Native Assessment vocabulary

- Use **Assessment, Test, Object, State, Variable, and Item** where those concepts remain semantically aligned with OVAL.
- `evaluate` is the native replacement for OVAL `criteria/criterion`.
- Typed `*_title` metadata replaces generic OVAL `comment` presentation where appropriate.
- **Object** is authored resource selection/acquisition. **Collection** is the runtime act of evaluating an Object and producing Items plus status/completeness; it is not an authored synonym for Object.
- A Test may consume another first-class node directly when that is the natural semantic source; `variable.value` is the established example and does not require an artificial Object wrapper.
- Test, Object, and State/predicate capabilities remain independently typed where those nodes exist.
- Source/presentation mapping order has no execution meaning; forward references are valid. Recommended authored section order is metadata, `objects`, `variables`, `states`, `tests`, `evaluate`.

## Variables, Sets, Filters, and dataflow

- Variables may reference named Objects, other Variables, or contain private embedded resource selection where supported.
- Lossless conversion preserves meaningful shared Object boundaries and Variable dependency graphs; it does not duplicate a shared source Object merely for convenience.
- Sets, Filters, object/variable components, functions, existence/cardinality, datatypes, comparisons, records, and dependency behavior must retain their effective semantics.
- Source identity remains available in migration provenance so distinct source nodes are not merged merely because payloads happen to match.

## Applicability and conditionals

- Applicability is explicit authored assessment logic, not hidden scanner OS/domain-role classification.
- CPE/platform identifiers are naming/mapping metadata unless backed by executable applicability logic.
- Source-authored conditional scheduling is supported where defined.
- General unrestricted IF/ELIF/ELSE authoring is not the current direction.
- Existing Boolean OVAL logic SHALL NOT be automatically rewritten as conditional execution merely because it appears equivalent; six-state outcomes, collection, evidence, and scheduling can differ.

## OVAL/SCAP migration

- Faithful conversion does not infer Benchmark Group taxonomy by default.
- Conversion tools MAY expose explicit opt-in automatic grouping (currently `--auto-map-groups`) for editorial normalization.
- Automatic grouping SHALL use only high-confidence mappings; uncertain Rules remain ungrouped rather than being forced into a catch-all Group.
- Group membership SHALL NOT alter Rule applicability, selection, Assessment behavior, Parameters, scoring, remediation, or result semantics.
- Forward migration from SCAP 1.4 is mandatory.
- OVAL 5.12.3 is the current semantic migration baseline, with later authoritative corrections/reinstatements handled explicitly.
- OVAL 6 is used primarily to identify genuinely new Test/Object/State/Item semantics; it is not an intermediate runtime format.
- Features exercised by current published content or conformance content are preserved unless a compelling explicit disposition documents an equivalent replacement/removal.
- Effectively deprecated OVAL Tests are conversion blockers; native Assessments do not carry a `deprecated` runtime flag.
- Source defects are preserved/reported as source defects rather than silently repaired during equivalence conversion.
- Existing OVAL platform-family distinctions remain where collected-data/evaluation semantics materially differ.

## Native capability design

- Preserve semantics, not XML type hierarchies, wrapper elements, namespace mechanics, or historical serialization workarounds.
- Reuse shared native primitives for comparison, quantifiers, existence/cardinality, records, Sets/Filters, traversal, and result behavior rather than duplicating them per capability.
- Native capability names may remove obsolete historical numeric/version suffixes when reviewed semantics justify it; exact OVAL source identity remains in provenance.
- Publisher/vendor extensions must remain isolated and cannot silently redefine core behavior.

## Provenance and native-source cleanliness

- Executable native Benchmark/Rule/Assessment/Object content does not embed XCCDF/OVAL/OCIL/CPE XML IDs, namespaces, href graphs, converter diagnostics, parity traces, or skipped-source-defect records merely for migration traceability.
- Conversion/normalization evidence is emitted separately and may reference native logical IDs.
- Native content must remain executable without migration evidence.

## Results and evidence

- Results separate policy/Rule context from distinct Assessment executions and their Test/Object/Variable/Item evidence.
- Execution identity, dependency scheduling, provenance, completeness, and outcome rationale are explicit.
- Evidence caps or early termination may bound volume but must record completeness/truncation and must not change the normative verdict.
- Schema/representation validity, known-result evaluation, acquisition/collector conformance, live-target testing, migration equivalence, human acceptance, and Board ratification are separate evidence levels.

## Packaging

- Compiled content uses a manifest-authoritative logical object graph.
- The current preferred container is deterministic ZIP with the `.scapng` extension.
- Archive paths are storage locations, not semantic identity; logical IDs resolve through the manifest.
- Migration/normalization evidence is not packaged by default.
- Signing/trust profiles remain under development; self-signed demonstrations do not establish publisher trust.

## Frozen 0.2.0 review baseline

- The 0.2.0 schema meaning is frozen at `7cd8b1242d7fb4a2eb9b5f49c7ec3f48b2dd622d`; new semantic work belongs to 0.3.0.
- The six converter-produced Board cases under `board/review-content/0.2.0/` are pending human acceptance.
- ESX/VMware expansion and the two Kubernetes OVAL 6-only Tests are deferred pending recorded guidance/decisions.
- Full runtime equivalence remains unproven; round-trip/source-reference/schema checks alone do not establish scanner equivalence.
- Content/conformance work precedes editor development.

## Required working procedure

1. Start from current `main` and this design contract.
2. Use pinned original SCAP/OVAL input for conversion work; do not normalize stale generated output and call it a fresh conversion.
3. Reduce defects/ambiguities to small independently reasoned fixtures.
4. Run focused tests first, then the fast five-benchmark integration lane when appropriate.
5. Record source pins, commands, outcomes, limits, and human-review status.
6. Do not encode a materially ambiguous semantic choice merely because one implementation passes tests.
7. Use the full NIWC corpus only for intentional milestones/freezes/Board deliverables.

See [MAINTAINING.md](../../../../MAINTAINING.md) for the human acceptance process, [the 0.2.0 freeze record](../../../../transition/0.2.0-freeze-record-2026-10-04.md) for technical evidence, and [review/current](../../../../review/current/README.md) for current review questions.
