> **Temporary hold:** Do not start this task until the 0.2.0 version-promotion reconciliation completes and a new exact-main freeze SHA is recorded. The former a0fe3abf checkpoint is semantic/integration evidence, not the final authoring-schema baseline.

# Codex task: SCAP-NG 0.2.0 content development and conformance corpus

Status: **READY TO USE**.

Frozen 0.2.0 technical baseline:
`a0fe3abf8605b97b0f637a9f9403c31bb329b47f`.

Freeze evidence: [0.2.0-freeze-record-2026-10-03.md](0.2.0-freeze-record-2026-10-03.md).

Start from that exact semantic baseline. A later documentation-only descendant
does not change the frozen technical meaning unless an explicitly authorized
post-freeze semantic change is recorded.

This task is intentionally detailed. It is content/conformance development, not language redesign and not editor development.

Related: #50 canonical conformance corpus, #128 complete feature/test-content inventory, #131 new OVAL 6.0 Test review. Read [the handoff checkpoint](handoff-0.2.0-content-development-2026-10-03.md) before beginning.

## 1. Establish the exact baseline

Work in `vanderpol/scap-ng`.

Before modifying anything:

- verify repository, branch and exact commit SHA;
- confirm the frozen semantic baseline is `a0fe3abf8605b97b0f637a9f9403c31bb329b47f`; if working from a later descendant, verify that intervening commits are documentation/handoff-only or are explicitly authorized post-freeze changes;
- read every applicable `AGENTS.md`;
- read `START-HERE.md`;
- read `research/iterations/003/design/CURRENT-DESIGN.md`;
- read the current glossary, specification, requirements index, transition decisions and 0.2.0 checkpoint;
- read Issues #50, #128 and #131 plus newer issues referenced by the checkpoint;
- read the maintained capability-coverage matrix and provenance requirements.

Report any contradiction between the frozen checkpoint and current repository before changing content.

Do not start by modifying schemas.

Historical iteration-001 and early iteration-002 generated content is evidence, not current architecture.

## 2. Objective

Create a substantial trustworthy SCAP-NG corpus that:

- demonstrates the finalized 0.2.0 design;
- provides independent known-result conformance fixtures;
- validates SCAP 1.4 forward conversion;
- exposes schema/converter/evaluator defects;
- exercises real production-backed security content;
- becomes the evidence base for later scanner/reference-implementation work;
- becomes the practical input set for a future SCAP-NG editor.

**Content comes before editor development.**

Do not build the editor in this task.

## 3. Preserve the current architecture

SCAP-NG is not OVAL serialized as JSON.

Preserve current architecture and terminology:

- Benchmark → Rule → selected Assessment;
- Rules own selections/defaults and policy meaning;
- Assessments describe evaluation;
- Objects/Variables/States/Tests/evaluate form the assessment graph;
- collected Items represent target observations;
- results explain outcomes and evidence;
- manual assessment remains first-class where automation is inappropriate;
- Organizational Input supplies controlled values, not executable choices;
- applicability is ordinary authored assessment logic, not scanner magic;
- native content excludes legacy XML namespaces/IDs/hrefs/serialization residue;
- deprecated OVAL Tests do not become native SCAP-NG capabilities unless explicitly reinstated by governance.

Preserve meaningful SCAP 1.4 semantics without reproducing XML structure.

## 4. Evidence sources and their roles

Use three complementary content sources.

### Minimal native fixtures

Create small intentionally designed Assessments/Benchmarks that isolate one semantic feature or interaction at a time.

These are the primary semantic conformance cases because their expected outcomes can be reasoned independently.

### OVAL Community SCAP Self-Assertion

Use the repository-pinned `OVAL-Community/SCAP-Self-Assertion` SCAP 1.4 OVAL test corpus for language-conformance evidence.

Pin exact source revision. Keep Self-Assertion logically/statistically separate from production migration evidence.

### Published production SCAP/STIG content

Use pinned published production content for migration/integration evidence.

Priority demonstration platforms:

- RHEL 9
- Oracle Linux 9
- Windows 11
- Windows Server 2025

Use Apache, DNS and other platforms/applications where they add a distinct capability or complexity problem.

Do not use full STIG conversion as a substitute for focused semantic proof.

## 5. Validation order

Use this order:

1. minimal single-feature fixtures;
2. small combinations of related features;
3. Self-Assertion cases;
4. representative production rules;
5. larger converted benchmarks;
6. full benchmark/corpus integration.

Resolve simple semantic failures before trusting large aggregate results.

## 6. Required coverage inventory

Maintain a machine-readable inventory mapping every finalized 0.2.0 normative feature to:

- specification/requirement;
- relevant schema/capability;
- minimal native fixture;
- converted source fixture where applicable;
- independent expected result/oracle;
- validation command;
- execution/conformance evidence;
- coverage status;
- remaining gaps.

Distinguish at least:

- structural schema coverage;
- semantic-validator coverage;
- known-result synthetic evaluation;
- converted-source coverage;
- collector/acquisition coverage;
- live-target execution coverage;
- migration/round-trip evidence.

A generated JSON Schema alone is not capability coverage.

Exercise, where finalized in 0.2.0:

- Tests, Objects, States and Variables;
- direct Variable testing and variable functions;
- Sets and Filters;
- existence/cardinality semantics;
- datatypes and operations;
- multi-valued observations;
- Test/State/entity comparison;
- conditional evaluation;
- all six technical outcomes;
- dependency invocation/reuse;
- manual Assessments;
- Organizational Input;
- Profiles, Tailoring and Parameters;
- applicability;
- shared collection;
- collected Item inclusion/materialization/import;
- completeness/bounded collection;
- redaction;
- reported elements;
- evidence lineage/provenance;
- result packaging and reference identity;
- unsupported capability handling;
- invalid-content validation.

## 7. Independent expected results

Every substantive fixture needs a known expected result.

Never create an oracle solely by running the implementation and saving its output.

Derive expected behavior from:

- finalized SCAP-NG specification;
- pinned source semantics where migrated;
- explicit project decisions;
- independent reasoning about the graph and observations.

Record expected:

- technical outcome;
- policy outcome when applicable;
- executed/skipped Tests;
- dependency executions;
- Items/evidence used;
- comparison lineage;
- completeness;
- reason codes;
- provenance;
- redaction behavior;
- effective Organizational Input where relevant.

Technical true/false is not universally equivalent to policy pass/fail.

## 8. Six-state domain and conditional behavior

Exercise meaningful cases for:

- true;
- false;
- error;
- unknown;
- not_evaluated;
- not_applicable.

For conditional evaluation, test guard/branch behavior across the full outcome domain and verify exactly what executes and what is skipped.

Do not revive automatic Boolean-to-conditional rewriting. That feature was explicitly rejected.

## 9. Collected Items and evidence

For Item-backed cases, expected results should identify:

- producing/selecting Object;
- target/context;
- source Assessment/execution for imported/materialized Items;
- completeness and caps;
- fields used in comparisons;
- fields used in Variable/Filter/selection logic;
- provenance;
- redaction.

Do not fabricate friendly explanatory fields that were not actually collected or derived under a defined contract.

Do not claim live acquisition conformance for supplied/mock observations.

## 10. Forward conversion rules

Forward conversion from SCAP 1.4 is mandatory.

When converting:

- preserve semantics, not XML shape;
- follow all required references/dependencies;
- preserve Variables, Filters and Sets accurately;
- preserve meaningful provenance;
- reject effectively deprecated Tests rather than reproducing them;
- keep source-invalid content distinct from converter/model/evaluator defects;
- never silently repair source content;
- never weaken a schema/oracle just to make a corpus green.

Every failure SHALL be triaged before a fix is accepted.

Use at least these categories:

1. source content defect;
2. converter defect;
3. SCAP-NG schema/model defect;
4. semantic-validator defect;
5. evaluator/test-harness defect;
6. collector/platform limitation;
7. unresolved specification question.

Add minimal reproducers and regression cases.

## 11. Native authoring quality

Alongside faithful converted content, create native SCAP-NG examples as a human author ideally would.

Prefer concise, understandable native forms while retaining exact semantics.

When historical OVAL complexity can be expressed more clearly using already-finalized SCAP-NG features, keep the faithful migration evidence and separately add the clearer native form.

Do not invent language features to make authoring prettier.

If finalized 0.2.0 cannot cleanly represent an important case, document the problem with a minimal reproducer and issue; do not silently extend the schema.

## 12. shellcommand

`shellcommand` is a legitimate capability where command execution itself is the appropriate security measurement.

It SHALL NOT become an escape hatch for migration complexity.

Do not replace native filesystem traversal/collection with shell commands where scanners need filesystem awareness, exclusions, completeness semantics or optimized collection.

Inputs and outputs must remain constrained and deterministic enough for trustworthy assessment.

## 13. Reuse across benchmarks

For RHEL 9/Oracle Linux 9 and Windows 11/Server 2025, actively identify genuinely reusable Assessments.

Preserve independent Rule identities, applicability and policy provenance.

Do not infer technical reuse merely from similar titles/CCIs/test-family names. Reuse requires equivalent complete assessment semantics.

Use shared Assessments plus rule-specific policy metadata/overlays when equivalence is proven.

## 14. Platform/applicability correctness

Applicability must remain explicit authored logic.

Do not make workstation, member-server and domain-controller policies interchangeable merely because they share Windows primitives.

Do not rely on hidden scanner `os_info` classification.

CPE/platform identifiers alone do not establish applicability.

## 15. File/path organization

Keep paths short, stable and human-readable.

Do not abbreviate directories to meaningless one-character names or generate random filenames.

The owner previously encountered Windows extraction/path-length failures.

Follow the finalized 0.2.0 package conventions. Logical references must use SCAP-NG identity/reference rules, not filenames.

## 16. Provenance

Maintain repository provenance categories, including as appropriate:

- Adapted;
- Inherited;
- Common;
- Evidence/Audit.

Converted content must identify original benchmark/rule/Test and pinned revision.

Original native examples must be labeled as such and must not imply DISA/OVAL authorship.

## 17. Positive and negative content

For each coherent capability group, include high-information cases such as:

- valid minimal usage;
- invalid/malformed authoring;
- absent Items;
- multiple Items;
- unexpected datatypes;
- unavailable/redacted fields;
- incomplete collection;
- invalid Organizational Input;
- unsupported capability;
- dependency error/reuse;
- boundary/cardinality behavior;
- expected diagnostics.

Avoid hundreds of mechanically repetitive fixtures that prove no new semantic point.

## 18. CI and evidence

A content group is not complete until applicable:

- source provenance is pinned;
- schemas validate;
- semantic validation passes/fails as expected;
- references resolve;
- expected-result fixtures are verified;
- relevant compiler/package checks pass;
- Windows/Linux CI succeeds where applicable;
- exact commit and workflow evidence are recorded.

Synthetic observations must be labeled synthetic.

## 19. ESX and OVAL 6.0 scope

VMware ESX new-Test expansion is **deferred pending upstream guidance**.

Existing draft ESX work may remain as experimental evidence/regression content. Do not continue the ESX family merely to reduce an old “remaining OVAL 6 Tests” count.

For OVAL 6.0, inspect only genuinely **new Tests/capabilities** not represented in the 5.12.3 baseline.

Do not adopt unrelated OVAL 6.0 structural/core-language changes or downgrade existing 5.12.3-derived behavior.

Use the final 0.2.0 checkpoint's explicit disposition for the two Kubernetes new Tests.

## 20. Deliverables

Work in bounded coherent content groups.

Cumulative deliverables should include:

- canonical SCAP-NG 0.2.0 conformance corpus;
- minimal native semantic fixtures;
- converted Self-Assertion cases;
- substantial representative RHEL 9 content;
- substantial Oracle Linux 9 content;
- substantial Windows 11 content;
- substantial Windows Server 2025 content;
- representative application/platform cases as useful;
- known-good Assessment Results;
- known-good Benchmark/Rule Results where applicable;
- invalid fixtures with expected diagnostics;
- machine-readable capability/feature coverage;
- source/provenance records;
- migration evidence;
- defect reproducers/issues;
- explicit unsupported/untested cases;
- CI integration.

Update coverage after every coherent content group.

## 21. Future editor observations

Do not build the editor.

While authoring content, record useful editor requirements such as:

- repetitive patterns;
- common author mistakes;
- fields an editor can safely derive;
- cross-reference navigation needs;
- inline documentation needs;
- validation messages that are hard to understand;
- places where visual graph editing may help.

These are editor requirements/research evidence, not permission to add editor-specific language constructs.

The future authority order is:

**specification → implementation/reference guidance → conformance content → editor**.

## 22. Handoff back

A useful checkpoint back to the owner/ChatGPT must state:

- exact starting and ending commits;
- content groups completed;
- capability coverage gained;
- converted/native fixture counts and identities;
- expected-result coverage;
- CI evidence;
- defects found and dispositioned;
- unresolved blockers;
- untested runtime/platform requirements;
- recommended next content group.

Do not claim complete SCAP-NG conformance merely because current tests pass.

The target is a corpus sufficiently trustworthy and diverse to support converter validation, future reference-scanner work, specification refinement and later human-friendly editor design.
