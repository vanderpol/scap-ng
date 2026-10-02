# Decision register and history coverage — initial recovery, 2026-10-02

Status: **initial reconciliation, not exhaustive**. Current repository authority was inspected directly; conversation retrieval returned partial summaries, sometimes noisy or conflicting. Dates on reconstructed entries are not independently verified unless linked to a dated repository record or directly visible owner message.

Authority order: latest explicit owner instruction → maintained current design/specification after reconciliation → validated implementation evidence. Historical proposals and assistant completion claims do not establish current acceptance or correctness.

## Current decisions and durable pointers

| Topic | Requirement / decision | Authority and limit |
| --- | --- | --- |
| Architecture | Benchmark → Rule → selected Assessment. Separate Policy files are superseded. | Inspected CURRENT-DESIGN and AGENTS. |
| Selection | Rule owns named Assessment selections, aliases and default/explicit provenance. | CURRENT-DESIGN; exact field names remain review proposals. |
| Authoring references | Explicit relative YAML Assessment paths; no hand-maintained assessment index. | CURRENT-DESIGN; Sept 30 retrieved owner acceptance. |
| Packaged resolution | Logical IDs resolved through an authoritative manifest; storage path is not semantic identity. Manifest must not duplicate selector/default policy. | CURRENT-DESIGN; package-container-and-manifest.md. |
| Container | Current preferred deterministic ZIP, .scapng extension. | CURRENT-DESIGN; preference is not proof current implementation passes. |
| Short paths | Content-generation directory names must be short: base benchmark ID or less, avoiding Windows unzip problems. | Visible Oct 2 project conversation summary. |
| Native capabilities | Clean break from OVAL schemas; preserve semantics without reproducing XML names, hidden defaults, hierarchy, deprecated values or workarounds. | CURRENT-DESIGN; native-capability-clean-break.md. |
| Vocabulary | Assessment, Test, Object, State, Variable, Item; Collection means runtime Object execution, not an authored Object synonym. | CURRENT-DESIGN Oct 1 checkpoint; supersedes earlier Collection prose. |
| Evaluation tree | evaluate replaces criteria/criterion; retain arbitrarily nested Boolean logic. | CURRENT-DESIGN; retrieved Oct 1 owner instruction. |
| Titles | Typed test_title/object_title/state_title/variable_title replace generic comment. | CURRENT-DESIGN; retrieved owner correction. |
| Readability order | Metadata, objects, variables, states, tests, evaluate; omit absent sections. SHOULD presentation convention, not execution order. Forward references work independently. | CURRENT-DESIGN; older collections→variables→tests ordering superseded. |
| Resource nodes | Objects remain reusable acquisitions where appropriate; they are not mandatory wrappers for every Test source. variable.value can directly reference a Variable. | CURRENT-DESIGN. |
| Capability typing | Test, Object and State/predicate declare compatible capabilities independently; explicitly resolve references; reject mismatches rather than coercing or inventing nodes. | CURRENT-DESIGN; supersedes earlier inheritance/single-declaration proposals. |
| Variables | Support named Object references and private embedded resource selections. Preserve shared original boundaries and variable dependencies. | CURRENT-DESIGN; embedded forms remain Board-review topic but required working design. |
| Depth | No arbitrary three-layer language limit; distinguish valid nesting from implementation resource budgets. | Earlier decision recovery; #38. |
| Complete graph | Resolve definitions, Tests, Objects, States, Variables, sets, filters, object/variable components and functions. | AGENTS; #10/#11 status requires fresh issue verification. |
| Defaults | Preserve effective behavior and default-versus-explicit provenance from authoritative semantics/schema. Never invent required source Test check. | AGENTS; decision-recovery record; #9. |
| Sets/filters | Preserve nesting, relative complement, flags and filter-before-enclosing-set semantics. | AGENTS; assessment-evaluation-semantics.md. |
| Records | Record data used by WMI, cmdlet and other tests must be captured and tested. | Visible Oct 1 owner message; recent WMI implementation still needs current validation. |
| Publisher Profiles | Every member Rule enabled; publisher Profiles subtractive only; disabled_rules includes [] when empty; no enabled_rules/re-enabling ancestor-disabled Rules. | CURRENT-DESIGN and specification/policy/profiles-and-tailoring.md. |
| External Tailoring | May enable/disable existing Rules, restore publisher-disabled Rules and select existing named assessments; SHALL NOT override publisher Parameter values or replace implementations/bindings. | Oct 1 recovered owner correction supersedes Sept 30 value-refinement acceptance; current specification and corrected resolver enforce the restriction. |
| Tailoring provenance | Human-readable purpose; creator, modifier, authorizer, dates, organization, authorization reference/status; preserve draft nulls and result provenance. | CURRENT-DESIGN; visible Sept 30 owner request. |
| Organizational Input | Distinct from Tailoring; restricted typed state/value input; cannot choose Tests or inject commands. | CURRENT-DESIGN plus supplied project history; parameters-and-organizational-input.md. |
| Applicability | Ordinary content-authored assessment logic; no scanner-side os_info magic. CPE names alone never decide applicability. | AGENTS; platform-and-applicability.md. |
| Applicability bindings | Small native ID→Assessment registry; Rules refer to applicability IDs; no migrated CPE/OVAL structure. | AGENTS. |
| Benchmark structure | Profiles, meaningful/nested Groups and Parameters belong in benchmark.yaml. No separate profiles/groups/values/platforms/processing files in 003. | AGENTS. |
| Evidence separation | Conversion/normalization diagnostics, legacy graphs, skipped-source defects and lineage belong outside executable native content. Compiler excludes migration evidence by default. | CURRENT-DESIGN; visible Sept 30 owner feedback. |
| Result scope | Authored configuration and runtime evidence/result structure must stay within their correct boundaries. Schema fixes must be backed by durable semantic documentation and guards. | specification/results/result-schema-scope-audit.md; scope audit reported completed, cause requires reading linked audit. |
| Informational | Preserve policy/Rule role for now because informational is used; research assessment-native informational separately. | Visible Oct 1 owner messages; do not treat proposed future replacement as removal approval. |
| Feature retention | Port capabilities used by real content or SCAP 1.4 validation content unless a compelling, explicitly documented removal reason exists. Rarity alone is insufficient. | Visible Oct 1 owner instruction. |
| Deprecated Tests | Effective deprecation blocks conversion with precise diagnostics. No automatic replacement or native deprecated flag; governance reinstatements matter. | AGENTS; Solaris exceptions and accesstoken/userright example documented there. |
| Source defects | Diagnose/account for source-invalid paths and exclude them according to documented quarantine behavior; do not silently repair semantics or label unsupported valid OVAL a source defect. | Visible Sept 30 owner direction; #46 and linked evidence require current issue verification. |
| Fidelity | Semantic equivalence, not byte-identical XML. Explain native-induced diff noise. Syntax, round trip and reference closure do not prove evaluator correctness. | AGENTS; retrieved Sept 30 owner acceptance. |
| Corpus separation | Pinned NIWC production corpus = migration evidence; OVAL Self-Assertion = language conformance evidence. Never combine claims/statistics. | AGENTS. |
| Sources | Prefer authoritative OVAL schema/docs and Self-Assertion; older MITRE ovaldi is supplementary sanity evidence, not current-language proof. Do not treat OpenSCAP as normative validation authority. | Visible Oct 1 owner discussion; AGENTS evidence hierarchy. |
| Reference scanner | Build after source format stabilizes; compare old/new execution on same targets. Downstream of format/conversion work. | AGENTS. |
| Converter | Reusable general-purpose tools under tools; clean-room 003 under tools/scap_upconvert_v003 without importing old full converters; stable Windows delivery and instructions required. | AGENTS and CURRENT-DESIGN. |
| Signing | Simple vendor-friendly signed Benchmark Results required research; support non-AD Linux/Mac/Solaris deployments. Original XML signatures cannot authenticate converted bytes. | Visible Oct 1 discussion and retrieved signing note; exact trust/signature choices require current spec. |
| Scale/results | Enterprise scale 100k+ targets; smaller human-readable results retaining policy context; cap evidence records and support early termination. | Sept 27 retrieved owner scale requirement; iteration001 decision register and iteration002 result/evidence decision corroborate caps/termination. |
| Evidence cap example | First 50 failure records from potentially millions was illustrative, not a universal hard-coded limit. | Supplied project memory. |
| Four anchors | RHEL9, Oracle Linux9, Windows11, Windows Server2025; historical first demonstrations exclude Server2012, RHEL10 prototypes and experimental PostgreSQL. | Supplied history and partial Sept 28 retrieval; broader corpus research is distinct. |
| Reuse | Separate Check Text alignment from exact complete assessment-semantic equivalence; literal-abstracted shapes are parameterization candidates, not proven reuse. | AGENTS. |
| Formal spec | SHALL/SHOULD/MAY/SHALL NOT where appropriate; glossary, SCAP1.4 crosswalk, intentional divergences and retained/removed-feature ledger. | Supplied owner history; specification indexes exist and were enumerated. |
| Provenance | Ledger for substantial work; record adaptation/inheritance/common/evidence-audit classifications and uncertainty. | Retrieved Sept 25 owner acceptance; AGENTS. |
| External draft | Learn from coworker Claude redesign; do not replace accepted architecture. External draft proposals are not owner decisions. | Visible Sept 30 instruction; earlier decision recovery. |
| Workflow | Pre-alpha appropriately tested completed work directly to main; proceed on fixable bugs; seek direction for substantive unresolved semantic/design decisions. | AGENTS; retrieved Sept 30 owner direction. |
| Governance | Discussion distinct from frozen explicit vote proposals; preserve removed/deferred features for Board review. Test vote is not official ratification. | Visible project history and retrieved board publication discussion. |
| Reviewer handoff | Notify owner when full RHEL9/Windows11 content is independently reviewable; complete coverage, native cleanliness, resolved references, no unexplained loss. | Retrieved Sept 30 owner requirement; current readiness must be reverified. |
| Transition | Preserve as much history as possible in accessible GitHub records; attempt full conversation recovery before switching; retain return path to ChatGPT. | Direct Oct 2 owner instruction in this chat. |

## Historical evolution to retain

- 001 explored combined, split Policy/Assessment/binding and optional Ansible-inspired renderings with no Ansible dependency. Owner asked to freeze it as examples grew complex.
- 002 pursued concise OVAL-aligned authoring examples and separated policy/applicability/assessment concerns. Historical generated artifacts were considered suspect when old machinery leaked XML serialization.
- 003 restarts from pinned originals and current native decisions. Separate Policy objects were replaced by Rules. Authored Collection terminology was subsequently replaced by Object. Earlier evidence remains useful but does not override current contracts.
- Initial strict deprecated-test rule was refined to use effective governance status, preserving explicit reinstatements.
- Earlier relative-path authoring decisions coexist with logical-ID/manifest compiled resolution; neither implies scanner filename guessing.
- Earlier green census/schema/round-trip claims describe their pinned commits, not future changes. Preserve failed runs and corrected conclusions as lessons.

## Reconciliation additions — 2026-10-02

- Sept 30 Tailoring value-refinement acceptance was superseded by the Oct 1 instruction: evaluate publisher requirement X or use a distinct policy for Y. The worked resolver/examples were stale although the current Tailoring schema/spec already rejected values; both are now aligned. Publisher Profile values and delegated Organizational Input remain distinct.
- The source-boundary audit previously removed result from the property list but additionalProperties still accepted it. Actual instance rejection now guards Tests, Objects, States and Variables while allowing a WMI field named result inside a State payload.
- Rule role remains the working informational policy control; a future replacement must not be confused with approval to remove it.
- Owner Oct 2 clarification: suffix 54 means the OVAL 5.4 revision and 57 the OVAL 5.7 revision. Exact source families stay in mapping/provenance; reviewed native names may be simpler. The specification crosswalk now links all six reviewed mappings and does not claim textfilecontent54 has a reviewed native mapping.
- Original iteration001 decisions D-007/D-008 corroborate bounded evidence and invariant-verdict early termination; D-027 requires deterministic effective scoring weights. Exact mappings/denominators remain separately reviewed.
- Preserve stable identity separate from revision; typed generic identifiers, constrained publisher extensions and title-independent internal node IDs. See iteration002 identity-and-publisher-extensions.md and current specification.

## Deferred / unresolved decisions to keep visible

Consult current design, specification/migration/legacy-feature-disposition.md and Board records before treating any item as settled:
assessment-native informational or runtime notapplicable; capability deprecation lifecycle; thin/full legacy result disposition; AND short-circuit versus full evaluation and diagnostic evidence; final field/quantifier wording; schema version scope; suffixes such as 511; embedded Objects/Filters Board ratification; multi-Benchmark publication; refine-value retention; precise result-signing trust/distribution contract; resource budgets and executable evaluator equivalence.

Do not silently remove a supported feature because a Board proposal is pending.

## Uploaded source inventory requiring accessible-file verification

Visible project history identifies:
- SCAP_Redesign_Discussion_Draft_08-12-2026.docx (external proposal, not acceptance).
- SCAP_1.4_Self_Assertion_Checklist.xlsx.
- RHEL-9-NC_SCC-5.16_DEV1-8511_OVAL-Results_RHEL_9_STIG2-002.009.013.zip.
- WIN2025-NC_SCC-5.16_DEV1-8511_OVAL-Results_Windows_Updates1-001.001.zip.
- SCAP_1.4_Sample_Windows_Results.zip.

Their presence in past ChatGPT/Library activity does not establish receiving-session access. No files were downloaded, inspected or republished in this initial transition pass. Verify permissions and avoid publishing sensitive scan data to a public repository without appropriate authorization.

## Coverage and next recovery passes

Inspected directly: AGENTS.md, CURRENT-DESIGN.md, Sept 30 decision recovery, root directory, specification file inventory and current Actions summaries. Full recursive repository enumeration was truncated; it cannot establish a complete file inventory.

Retrieved targeted summaries: project-wide recovery; earliest-through-Sept28; Sept29–Oct2. Retrieval returned partial evidence and unrelated draft extracts. recovered-notes.md preserves only project conversation-search portions, labeled as summaries. Some retrieved attributions/date labels appear reconstructed or inconsistent and require corroboration.

**Not yet achieved:** complete list of project conversations; verbatim transcript export; exhaustive decision coverage; detailed reconciliation of every specification/decision/issue; full upload/artifact retention; stable technical checkpoint; receiving-session verification.

Next passes: inspect iteration001/002 decision registers and lessons; read all current specification sections and relevant Board records; retrieve focused missing decisions (scale, cap/termination, signing, applicability, tailoring, runtime results); reconcile open/closed issues and test evidence; build a traceable requirement-to-record-to-test matrix; record irrecoverable gaps. Source exports, if supplied later, must be compared with this register rather than assumed redundant.

Provenance: Evidence/Audit. Memory-summary entries are explicitly weaker than inspected authoritative current records. This initial register must not be used to claim every conversation or key decision has been recovered.

## Preserved repository evidence

[source-index.json](source-index.json) inventories 68 committed design/specification/Board/instruction records at exact commit and blob hashes. This is a navigable historical pin, not a claim all entries have been independently reconciled. [issues-2026-10-02.json](issues-2026-10-02.json) preserves 47 non-PR issues and 191 comments as returned by the GitHub connector, including closed/superseded work. Discussion voting data and complete original conversation transcripts remain outside this archive.
