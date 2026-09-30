# Current SCAP-NG design — authoritative authoring checkpoint

Owner reconfirmation: 2026-09-30. Read this file before selecting a generator, preparing examples, or claiming review readiness. Earlier conversation summaries, generated trees and superseded design prose do not override these decisions. Update this record when the owner changes a decision.

## Settled owner direction

- Architecture: **Benchmark → Rule → Assessment** for compliance and vulnerability content. There is no separate Policy object/file. Rule owns requirement/assertion metadata and named Assessment selections/defaults; Assessment owns the evaluation method.
- Benchmark membership enables every Rule. Publisher Profiles are subtractive only: they MAY disable Rules and SHALL NOT expose `enabled_rules` or re-enable ancestor-disabled Rules. A Profile SHALL expose `disabled_rules`, including `[]` when it disables no additional Rules. Empty lists preserve the supported-data-elements convention and never re-enable ancestor-disabled Rules. External Tailoring MAY enable/disable existing Benchmark Rules, including restoring a publisher-disabled Rule, refine permitted Parameters and choose among existing named Rule Assessment selections. It SHALL NOT replace bindings or implementations; Organizational Input cannot select Tests. See `specification/policy/profiles-and-tailoring.md`; source Profile XML description wrappers SHALL NOT appear in native descriptions.
- Authored Assessment selections use explicit YAML paths relative to the referring Rule. Preserve selector identity, aliases and default-versus-explicit provenance. Compiled resolution uses explicit manifest bindings; never guess filenames.
- Native automated evaluation nodes are **Tests**. Use `tests`, `test_title`, `test-` IDs and explicit Test references.
- Native acquisition nodes are **Collections**, corresponding to OVAL Objects. Use Collection terminology in native output; retain OVAL Object terminology only in source parsing/provenance. Named/reusable Collections remain first-class.
- Assessment source presentation SHOULD place metadata first, then `collections` → `variables` → `tests` → `evaluate`, omitting absent sections. This is a readability/output convention, not execution order: mapping key order SHALL NOT affect reference resolution; forward references remain valid. Sequence order retains its meaning where defined, such as function arguments. Our generators consistently follow this recommendation; `tools/check_current_authoring_contract.py` checks generated review presentation in CI. An order warning does not make an otherwise valid authored Assessment semantically invalid.
- Variables SHALL support **both** references to existing named Collections and Collections embedded privately within the Variable. This is an agreed working-design requirement. Formal Board ratification is tracked separately; it does not remove either form from our working model.
- Converted source SHALL preserve meaningful named Collection boundaries and Variable dependencies. Do not duplicate a shared source Object inline at every use. Embedded Collections are supported for native authoring; they SHALL NOT be used to erase shared source references during lossless conversion.
- Variables can consume Collection fields or other Variables. Named intermediates and the complete graph through sets/filter States/functions must survive conversion. Source identity must remain in provenance so distinct source nodes are not merged merely because payloads match.
- Native Assessments have no `deprecated` attribute. Effectively deprecated source Tests are blockers; they do not become native runtime flags.
- Capability is declared at Test level for its directly used Collection/State contract; mismatches fail. Do not silently mix types. For a Collection used only by Variables, the owner selected capability declaration on the Variable as the working prototype direction (2026-09-30). Exact grammar and formal Board ratification remain pending; do not treat this as an approved standard or infer type from filenames/IDs.
- Pre-alpha: publish completed, appropriately tested work directly to `main` without routine permission requests. The owner authorized current-design full RHEL9 review generation on 2026-09-30. Historical publishing workflows remain held; use the new source-driven full review entry point.

## Converter delivery and stability requirement

Owner direction, 2026-09-30: once conversion reaches stability, provide the exact
maintained converter and instructions for running it on the owner's Windows
development computer. Windows portability is an implementation requirement now,
not a late packaging task. The converter is the executable expression of the
working NG design; source syntax, documented semantics and regression fixtures
must evolve together. One documented entry point must reproduce the reviewed
output from pinned original SCAP input. See
[converter stability and Windows delivery](converter-stability-and-windows.md).

## Open or not yet implemented

- Exact Rule choice field names (`assessment_choices`, `default_assessment_choice`) are review proposals.
- Complete `collection`/`collection_title` and `assertion` vocabulary migration, including the final item/state quantifier syntax, is unfinished.
- Named Collection graph conversion and reverse consumption now have a tested prototype (`collection_graph=True`), including source identity and Variable references. It is integrated into the complete pinned RHEL9 Rule/Benchmark research renderer; compiled package/signature and broader consumer integration remain unfinished. Variable-side capability declaration is the selected prototype direction; `collection_capabilities` is prototype grammar, with Board approval pending.
- Formal Board review of embedded Collections and colocated Filters remains pending. Both named-reference and embedded-Collection Variable forms are required in the working design, not optional pending implementation choices.
- Full runtime equivalence is unproven. Round-trip and source-reference checks alone do not establish evaluator equivalence.

## Collection/dataflow checkpoint

[Source-generated sample](../review/collection-dataflow-source-sample/README.md):
selected Assessment output from 25 RHEL 9 Rules, converted from the pinned
original ZIP. This is a tested dataflow prototype, not a full Benchmark compiler.
Source graph sharing, Variable chains and private embedded native-authoring
Collections have regression coverage. All 42 Variable-bearing RHEL 9 cases
compare equal through the new graph/reverse path; 23 sample automated outputs
also regenerate omni-schema-valid OVAL. Runtime conformance, complete Rule/Profile
rendering were outside this slice. Windows/Linux graph and local-ZIP regressions subsequently passed; full-source review evidence is tracked separately below.

## Full RHEL9 checkpoint

[Current full review](../review/rhel9-current-full/README.md) uses the pinned original package, not old rendered YAML: 445 Rules, 11 Profiles, 418 automated and 445 manual Assessments, 18 source-driven applicability conditions. All 4,895 Rule/Profile selection comparisons match. Automated/applicability definition round trips and pinned omni-schema checks pass. Relative Rule paths, source selectors/defaults, shared manual questionnaire aliases, grouping and native presentation/cleanliness are checked. The exact research CLI is `tools/scap_upconvert_v003/convert_full_review.py`; Windows/Linux full-package CI evidence is recorded with the review. This is not finalized grammar, compiled packaging or runtime conformance.

## Current artifact status

`review/test-vocabulary-slice` is **incomplete**, despite its passing narrow naming/path tests. It still contains older `collect`/`object_title`/capability duplication and has no Variable/Collection dependency example. It SHALL NOT be described as a completed current-design slice.

`source/split-rule-assessment/rhel9-full` is historical generated baseline data, not current native syntax. `source/split-policy-assessment/rhel9-full` is a superseded architecture experiment. Neither tree is an automatic source of current authoring decisions.

## Required working procedure

1. Read this record and repository instructions. Resolve conflicts in favor of the latest explicit owner instruction, update this record, and mark older prose superseded before generating examples.
2. Inspect the selected script's input/output contract and consumers. Use pinned original SCAP input and faithful IR for lossless changes; do not normalize a stale rendered tree and call it a fresh conversion.
3. Add focused regressions for the actual feature under review. Variable work must include named Collection extraction, shared references, variable-to-variable dependencies, sets/filters and negative references/cycles. Do not use a no-variable slice as evidence for variable support.
4. Run `tools/check_current_authoring_contract.py` on proposed review output. Resolve reported violations before calling that output ready. A blocked report is a valid checkpoint, not a pass.
5. Record source pin, exact commands, results, unresolved blockers and coverage limits. Publish coherent checkpoints on main. Explain narrowly what is proved.
6. Before reviewer handoff, compare both generator output and consumer behavior against every settled decision above. Run a full round trip after the accepted source grammar is implemented end-to-end.

Provenance: **Evidence/Audit** of owner decisions and observed regressions; no external redesign proposal supersedes the established model.
