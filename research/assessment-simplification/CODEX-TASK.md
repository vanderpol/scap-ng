# Codex task: discover simpler, equally accurate Assessment authoring

Owner instruction: 2026-10-02 (America/New_York). This is exploratory R&D,
not an instruction to replace the current SCAP-NG design or rewrite production
content. Expected usage: **potentially expensive**, with many staged iterations.
Correctness and useful discoveries take priority over elapsed time.

## Mission

Find generalizable ways for humans to author, understand and maintain complex
Assessments while retaining equally accurate testing. Study the actual STIG
requirement and Check Text, then the complete published OVAL/NG dataflow. Explore
unfamiliar methods and new capabilities or language primitives when justified.
Do not assume that shorter YAML, a renamed OVAL node, a template, or a single
large script is a substantive simplification.

Use the 12 pinned cases in `samples/` as an initial investigation set. Propose
small before/after mockups with an explicit semantic contract and adversarial
examples. A valuable outcome can be a reasoned rejection: some complexity may
be necessary or belong in a collector rather than the language.

## Receiving-session preflight

1. Read root `AGENTS.md`, `START-HERE.md`, `docs/repository-policy.json`,
   `docs/repository-map.md`, `research/iterations/003/design/CURRENT-DESIGN.md`,
   `transition/README.md` and `transition/decisions.md`. Read the linked evaluation
   semantics, native capability clean-break design, and current v0.1.0 schemas.
2. Report the checkout commit and identify differences since the sample build.
   Current architecture is Benchmark → Rule → selected Assessment; do not restore
   separate Policy files, old Collection vocabulary, or archived generators.
3. Read `sample-manifest.json` and `README.md`. Verify the file hashes. Samples
   are unchanged build snapshots and research inputs, not normative grammar.
4. Verify access to the pinned NIWC source, OVAL 5.12.3 schemas/documentation,
   OVAL Community Self-Assertion content and this repository. Resolve source
   access failures without substituting a different STIG revision. Do not infer
   source defects merely from an unsupported or unfamiliar construct.
5. Reproduce applicable baseline authoring/schema/semantic checks using maintained
   entry points. Record existing failures and version drift before making changes.
   Baseline bugs or newer vocabulary updates must remain separate from proposed
   simplifications. Do not regenerate using historical pipelines.

## Scope and authority

Preserve the accepted architecture and existing designs. Future capabilities,
syntax and semantics proposed here are explicitly **experimental** until reviewed.
Do not change the normative schema, lossless converter, accepted assessment
bindings, or production check behavior merely to make a research mockup validate.
Research fixtures and narrowly scoped offline semantic models are in scope;
a general reference scanner, deployments and target-system changes are not.

Publish coherent research checkpoints directly to main during pre-alpha. Keep
R&D outside `review/current/`; that directory is the sole external review target.
Do not freeze a review iteration or publish a Board vote without coordination.
Only one session should own this technical workstream. Check existing current
work and coordinate rather than overlapping edits. Update the handoff at each
checkpoint so another session can resume without reconstructing chat history.

## Establish three separate contracts for each case

A. **Policy intent**: requirement, exact Check Text/procedure, discussion,
applicability, exceptions, organizational inputs and manual judgment.
B. **Published implementation**: effective OVAL semantics and existing generated
NG graph, including dependencies and effective defaults.
C. **Proposed method**: exact behavior, inputs, outputs, supported environments,
assumptions, failures and required new collector/language features.

Write a plain-language statement and truth conditions for A and B before C.
If A and B disagree, explain the discrepancy. A faithful simplification of B and
an improved implementation of A are distinct experiments. Never label an intent
correction as lossless equivalence. A title, remediation paragraph or shell
command alone is not a sufficient statement of the requirement.

The packet's manual Assessment `procedure` preserves the generated Check Text;
its Rule preserves requirement and discussion. Compare them with pinned original
XCCDF to recover whitespace, selectors, applicability and exact source linkage.
Retrieve original OVAL through the maintained splitter/parser and include complete
reachable dependency closure. Record definition/test/object/state/variable IDs
in evidence, not in proposed executable native syntax. Original XML and generated
NG are two views of the same inherited logic, not independent truth oracles.

## Study all semantics the selected graph uses

Trace every dependency, including external inputs, nested functions, Object
components, variables-of-variables, States behind Filters, Sets, and extended
Definitions. No arbitrary three-layer language-depth limit is allowed. Distinguish
valid expressive depth from explicit implementation resource budgets.

Account for item correlation and record fields; Cartesian versus per-item
function behavior; typing and comparisons; regex dialect and anchoring; order,
duplicates and empty values; Object collection flags/completeness; existence,
item/state/variable quantifiers; Boolean operators and negation; filter defaults,
filter placement and application before enclosing Set operators; relative
complement; and error/unknown/not-evaluated/not-applicable behavior. Cover masking,
record data, early termination and bounded evidence where relevant. Preserve
forward references and meaningful shared Object boundaries. Do not approximate
unimplemented semantics with a successful result.

Evaluate applicability with ordinary authored assessments. No scanner `os_info`
magic, command exit-status guesses, or CPE-name-only applicability. Preserve
supported features even if rare. Effectively deprecated Tests stay conversion
blockers, with governance reinstatements respected. Keep Rule policy `role`
separate from the technical Assessment truth domain.

## Shellcommand boundary — owner requirement

Shellcommand is a legitimate candidate for some checks, especially structured
administrative queries or focused inspection through supported utilities. It
SHALL NOT become the primary assessment mode or a shortcut for filesystem
scanning. Do not replace native file selection/traversal with `find`, recursive
shell/PowerShell directory enumeration, or scripts that attempt to recreate
scanner filesystem scope and exclusion rules. Native scanners know how to identify
and exclude remote filesystems and can use their own traversal efficiencies.

Keep native file traversal, mount boundaries/exclusions, recursion depth,
symlink/junction handling, unreadable paths and collection completeness explicit.
An existing source script that performs traversal is an inherited baseline,
not endorsement of that method. Discovery or a supported configuration query
is different from filesystem scanning; state that boundary in each proposal.

For every command-based candidate specify executable/interpreter, supported
versions, required privilege, arguments/typed inputs and safe quoting, exit codes,
stderr, timeout, output completeness, locale/encoding, stable machine-readable
output, record correlation and failure handling. No command-string interpolation
of arbitrary organizational input; no environment-dependent output parsed as an
unexamined Boolean. Prove that a shorter script has not merely hidden complexity.
Prefer a native typed collector when it provides clearer semantics and scope.

## Research method — staged, repeatable iterations

Start with **RHEL9 SV-258179** and **Apache UNIX Server SV-214228**. They expose
contrasting audit-rule regex repetition and command/configuration dataflow.
Complete a readable semantic explanation, one mockup and a counterexample set
for each before widening to all 12 cases. Then include the native-filesystem
control **RHEL9 SV-257889**, followed by Windows ACL and DNS row-correlation cases.

For each case:

1. Map intent and complete baseline graph. Explain why it is complex; distinguish
   necessary semantics, OVAL serialization workarounds, source defects, shared
   boilerplate, missing collector support and accidental authoring complexity.
2. Define a baseline matrix: relevant system situations and expected outcomes,
   decisive evidence, missing/unreadable resources and partial collection.
3. Explore at least two materially different methods when justified: existing
   primitives composed more clearly, a new reusable capability/primitive, typed
   structured dataflow, or a bounded command query. Include a reasonable
   no-change alternative. Ideas such as parsed audit records, effective
   configuration, row-correlated predicates or reusable typed selections are
   hypotheses, not mandated features or pre-approved syntax.
4. Mock up complete small Assessment examples in clearly labeled proposal files.
   Preserve Test/Object/State/Variable roles where needed, without forcing empty
   wrapper nodes. Show required Rule binding/context changes separately, if any.
   Explain each invented field and its exact meaning. Do not call it accepted NG.
5. Specify each new feature independently of the STIG: acquired Item/record type,
   selection, comparison, quantifier, ordering, Set/Filter interaction,
   multiplicity/correlation, result propagation, collection status and budgets.
   Decide whether complexity belongs in a general language primitive, a reusable
   domain collector, a library pattern or an authoring tool. Avoid a universal
   special-purpose `compliant: true` collector that hides policy decisions.
6. Try to falsify the proposal. Use adversarial fixtures and offline comparisons,
   preserving all relevant outcomes and decisive evidence. Run existing tests
   appropriate to the changed research model. A mock interpreter sharing all its
   logic with its oracle is not independent equivalence evidence.
7. Record readability, semantic coverage, implementation burden and portability.
   Explain failures, revise or reject, and checkpoint before starting another
   wave. Carry discoveries across platforms; do not specialize blindly per Rule.

## Required challenge scenarios

- Audit: running versus persisted rules; 32/64-bit applicability; syscall lists
  split/combined/reordered; equivalent spelling and auid sentinels; missing rules,
  duplicate entries, comments and ambiguous patterns. Do not assume parsing makes
  every superficially similar audit rule equivalent.
- Files: zero/many users, UID boundaries, home paths, multiple mount types,
  remote filesystem exclusion, symlinks and junctions where supported, permission
  bits versus numeric comparisons, partial/unreadable traversal and empty Sets.
- Windows rights: effective versus explicit ACLs, deny/allow precedence,
  inheritance, group membership, local/domain identities, unknown principals,
  registry/path discovery, record correlation and inaccessible resources.
- DNS: per-zone/per-interface identity, heterogeneous good/bad zones, integrated
  versus non-integrated zones, record-type completeness, signing/time units,
  empty zone sets, classification inputs and command failures. Do not flatten
  rows into uncorrelated arrays that let one zone satisfy another zone's fields.
- Apache: multiple running installations, root/config discovery, includes and
  IncludeOptional, repeated directives, ordering/scope and VirtualHost contexts,
  defaults, absent directives, unreadable includes, and active versus on-disk
  configuration. An effective-config collector needs a documented interpretation
  of application semantics, not an unproven grep replacement.

Use pinned authoritative OVAL schema/docs and Self-Assertion for language behavior;
use product official documentation for proposed collector behavior. Older MITRE
ovaldi is supplementary sanity evidence for its supported version only. OpenSCAP
is not the normative truth source. Actual execution comparison on the same target
systems is required before claiming runtime equivalence; until then report a
hypothesis plus the evidence and limits. Do not require full runtime proof merely
to publish a clearly labeled useful research proposal.

## Deliverables and acceptance gates

Maintain one research index linking per-case dossiers. Each dossier includes:
source pin/link/hash; exact Rule and Check Text; baseline dependency explanation;
intent/implementation discrepancies; existing NG excerpt; at least one complete
proposed mockup; semantic contract; equivalence/counterexample matrix; fixture
results; portability/collector work; measurements; rejected alternatives; open
questions and confidence. Keep original snapshots immutable and changes separate.

Measure understandable improvements: author-visible nodes and references,
indirection depth, regex/command dependence, repeated policy predicates, places a
human must change, readability explanation and reviewer questions. Count lines
and bytes only as secondary metrics. Do not equate fewer nodes with better
correctness or scanner performance. Measure runtime cost separately when targets
exist; check batch/shared acquisition, bounded evidence and enterprise scale.

Classify every candidate: existing-language refactor; reusable pattern/tooling;
new collector; new language primitive; intentional policy correction; rejected;
or unresolved. Separate common mechanics from domain semantics. For promising
features, demonstrate reuse in another selected Rule and a counterexample before
recommending architecture changes. Synthetic cross-domain demonstrations must be
labeled as such rather than counted as production evidence.

Keep NIWC production migration evidence separate from Self-Assertion conformance
and original synthetic tests. Record provenance as Inherited, Adapted, Common or
Evidence/Audit. Store migration graphs and diagnostics outside executable content.
Add focused GitHub issues for findings needing implementation, semantic decisions
or publisher remediation; check for existing issues before creating duplicates.
Board decisions remain separately versioned yes/no Discussion proposals, not
ratification inferred from an issue, mockup or reaction count.

After each wave, commit coherent results to main and update the checkpoint with
completed cases, evidence, blockers and next bounded action. Continue autonomously
through the authorized research. Seek owner input for substantive unresolved
policy/semantic choices, unsupported source access or conflicting directions.
Time limits are not a reason to report an unsupported equivalence claim.

Success is a small set of demonstrably clearer, reusable proposals with honest
semantic limits—not a wholesale rewrite or an obligation to discover a new feature.
