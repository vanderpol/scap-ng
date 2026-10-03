# Bounded Codex task plan: 0.2.0 vendor test content

Status: future implementation task after the 0.2.0 contract is finalized.
Owner asked about suitability on 2026-10-03. Expected effort: moderate per bounded
feature group; potentially expensive for the exhaustive corpus. No automatic
delegation is scheduled. #128 owns the complete feature inventory; #131 owns
capability gaps/new-Test review. Provenance: Evidence/Audit and Common task plan.

## Receiving task

Work in vanderpol/scap-ng. Verify checkout/branch/SHA and read AGENTS, START-HERE,
repository boundaries, CURRENT-DESIGN, transition decisions, glossary, current
specification/schema checkpoint and the relevant live issue. Use finalized 0.2.0
contracts, not historical syntax or an assumed ratified proposal. Keep new-test
capabilities and existing 5.12.3 fixes distinct; do not adopt unrelated 6.0 changes.

Choose one declared feature/capability group from the maintained coverage matrix.
Pin original OVAL Community SCAP 1.4 Self-Assertion content using the corpus
manifest and verify each selected case's source and expected semantics. Treat
published STIG content separately as migration evidence. Convert supported cases
and add original native cases for coverage gaps, intentional divergences and
NG-only features. Do not restore deprecated constructs or legacy XML identifiers
inside executable NG source. Record adapted/common/evidence provenance.

Create small sample Benchmarks and standalone Assessments with expected-results
files and platform/context prerequisites. Include meaningful valid/invalid,
pass/fail, absence/error/unknown/not-evaluated/not-applicable, incompleteness,
redaction, multi-value and dependency/interaction cases. Cover the chosen group's
Benchmark/Rule selection, Profiles, Tailoring and Organizational Input interactions
where relevant; publisher requirements cannot be changed by Tailoring values.
For descriptive metadata, test the representation contract without pretending it
changes runtime truth. For callbacks/mock observations, label outcomes synthetic.

Derive each oracle from pinned normative/source semantics and independent
reasoning; never generate expected results solely from the implementation being
tested. Explain technical versus policy outcomes, exact executed/skipped paths,
required evidence/provenance, statuses/completeness and expected validation errors.
Schema validation, round-trip comparison, recorded scheduling and live-target
conformance are separate evidence. Do not claim a scanner exists or acquired data
was independently verified when only supplied observations were evaluated.

Add requirement→content→oracle→command→evidence traceability and explicit coverage
status. Resolve source versus implementation defects before altering expected
results. Track unresolved semantics with a reproducer/issue and continue other
independent cases; do not invent an answer or silently omit the case. Keep draft
Board-dependent cases visibly experimental until their final disposition.

Run focused conformance/schema/reference checks and maintained relevant regression
commands. Record exact tested commit, CI results and remaining limitations. Publish
one coherent group under the authorized repository workflow. Do not merge bulk
historical branches, alter stabilized schema/converter semantics merely to make a
fixture pass, or claim that this group completes #128's full inventory.

Owner follow-up: notify when ready and provide verbose instructions that produce
a useful deliverable. A readiness-only hourly notification watch is configured;
it does not perform repository development or delegate automatically. Publish an
explicit ready/finalized working checkpoint with exact schema/specification commit,
CI evidence and blocker disposition before sending the final copy-and-paste task.
