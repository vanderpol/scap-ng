# Maintaining and Evolving SCAP-NG

This is the short, human-auditable maintenance process for SCAP-NG.

The repository has extensive research history and broad CI coverage. Those are useful evidence, but they are not a substitute for a human understanding the language change being accepted.

## Core rule

**Machine-green does not mean human-accepted.**

A semantic language change is not accepted merely because schemas, converters, round-trip tests, Self-Assertion, or benchmark builds pass. Before a semantic change is treated as current design, a human reviewer must be able to understand what changed, why it changed, what existing semantics it affects, and what evidence supports it.

## Normal development loop

Use this order for ordinary work:

1. Start from current `main`.
2. Read `AGENTS.md`, `BRANCH-MANAGEMENT.md`, this file, `START-HERE.md`, and `research/iterations/003/design/CURRENT-DESIGN.md`.
3. Make one bounded change or one tightly related change set.
4. Create or update focused tests that demonstrate the intended semantics.
5. Run focused/schema/unit tests first.
6. Run the fast five-benchmark conversion regression when converter/schema behavior is affected.
7. Prepare the human review packet described below.
8. Human-review the change and its examples.
9. Only after human acceptance should the change be described as accepted current design.
10. Run broader milestone gates only when warranted.

Do not use the 65-package NIWC corpus as the normal edit/test loop.

## Human review packet for semantic changes

Every change that modifies the language, schema meaning, result semantics, capability semantics, or conversion semantics SHALL have a concise review record containing:

- **Change:** one-paragraph description of the behavior being changed.
- **Reason:** the problem or source requirement that requires the change.
- **Before:** a minimal old representation or behavior.
- **After:** a minimal proposed representation or behavior.
- **Semantic effect:** exactly what processors/authors must do differently.
- **Compatibility:** effect on existing 0.x content, converters, validators, and results.
- **Source evidence:** relevant OVAL/SCAP schema, specification, published content, Self-Assertion, issue, or owner decision.
- **Alternatives considered:** especially when an existing OVAL term or behavior is being renamed, removed, or simplified.
- **Tests:** focused positive, negative, and boundary cases.
- **Machine evidence:** exact commands/workflow runs used.
- **Human status:** `pending-review`, `accepted`, `rejected`, or `needs-revision`.
- **Reviewer/date:** recorded when a human decision is made.

A large generated diff is not a review packet.

## Minimal reproducer rule

When a benchmark, Self-Assertion case, converter, schema, or evaluator exposes a defect:

1. reduce the failure to the smallest fixture that still reproduces it;
2. record the exact expected behavior independently of the implementation;
3. fix the defect against that fixture;
4. keep the fixture permanently as a regression;
5. run focused validation;
6. run the fast integration set only if the affected surface warrants it;
7. defer any full-corpus confirmation until the next intentional deliverable/checkpoint.

The reproducer SHOULD contain only the minimum Rule/Assessment/Test/Object/State/Variable/result material required to demonstrate the issue. Do not preserve unrelated benchmark structure merely because it existed in the source.

If the reproducer cannot be made small without losing the failure, document why. That is itself useful evidence about hidden coupling or an architectural problem.

## Three levels of validation

### 1. Focused validation — normal inner loop

Use for every bounded change.

Examples:
- schema/meta-schema validation;
- semantic validator/unit tests;
- focused converter or round-trip reproducer;
- a small Self-Assertion case;
- direct expected-result fixtures.

Goal: fast diagnosis and understandable evidence.

### 2. Fast integration validation — normal pre-merge/pre-acceptance loop

Use the maintained **Fast five-benchmark conversion regression**.

Its purpose is to catch integration problems across several distinct real-world source types without waiting for the full corpus.

Current cases:
- Apache Tomcat 9;
- Windows 11;
- Windows Server DNS;
- Apache 2.4 UNIX Server;
- SQL Server 2022 Database as an expected publisher-extension blocker.

The set may evolve, but changes to the set must be deliberate and documented.

### 3. Full milestone validation — occasional confidence gate

Use the full NIWC Current corpus only when intentionally producing a durable deliverable/checkpoint, such as:
- an OVAL Board review checkpoint;
- a release or freeze candidate;
- another explicitly named content deliverable.

Do **not** run the 65-benchmark corpus merely because code, schemas, converter behavior, or documentation changed. Normal development uses focused tests plus the fast regression set.

The full-corpus workflow is intentionally manual-only. It provides broad confidence for a deliverable; it is not the primary way to understand or iterate on a language change.

## Review lifecycle

Review navigation has one active authority: [`board/README.md`](board/README.md) for the current external/Board review. Compact supporting summaries may live under `review/current/` without restating project status.

When a review cycle is formally completed, preserve the exact reviewed state under an immutable `review/iterations/NNN/` checkpoint with the source commit/tag and any durable external artifact URL/hash. Later corrections belong to a new review cycle; do not rewrite a completed review checkpoint. Large generated products should stay in CI/evidence storage rather than being recommitted merely for review.

## Version evolution

For a new schema version:

1. Copy forward the complete preceding version as required by `AGENTS.md`.
2. Establish the exact scope of the new version before broad implementation.
3. Implement semantic changes in small reviewable groups.
4. Require a human review packet for each semantic group.
5. Record explicit human acceptance before calling a design decision settled.
6. Keep unresolved questions visibly unresolved; do not silently encode an agent's preferred answer in schema.
7. After the bounded changes are accepted, run fast integration validation.
8. Before freezing the version, run the milestone gates against one exact technical SHA.
9. Record the freeze SHA and distinguish later documentation/process-only descendants.

## What agents may do without human acceptance

Agents may:
- investigate;
- draft alternatives;
- add tests that expose current behavior;
- repair obvious implementation/test harness defects when they do not change intended semantics;
- improve documentation;
- prepare review packets;
- implement an already accepted design decision;
- run validation and collect evidence.

Agents SHALL NOT independently convert a materially ambiguous design choice into accepted language semantics merely because one implementation passes tests.

When a genuine semantic choice has multiple defensible outcomes, stop the semantic decision and present the human review packet.

## Branch discipline

`main` is the authoritative current project state.

Branches are exceptional during the current pre-alpha phase. If a branch is used, record it immediately in `BRANCH-MANAGEMENT.md` and keep its status current. Accepted work must not remain stranded on an untracked branch.

## Evidence discipline

Keep these concepts separate:

- schema-valid;
- semantic-validator-valid;
- known-result/evaluator-conformant;
- migration-equivalent;
- collector/acquisition-conformant;
- live-target-tested;
- human-reviewed/accepted;
- Board-ratified.

No one status implies the others.

Large/exhaustive generated proof belongs in `vanderpol/scap-ng-evidence`, not in the maintained standards repository merely for convenience. Keep compact summaries, source pins, hashes/provenance, representative examples, and links in `scap-ng`. Before removing a generated/evidence tree from the active repository, record its source commit/path, copy it to a stable evidence-run location, verify bytes/hashes, update references, and run dependency/link/regression checks. Git history and the preserved pre-rebaseline tag remain recovery sources.

## 0.2.0 maintenance baseline

The frozen 0.2.0 technical baseline is recorded in:

`transition/0.2.0-freeze-record-2026-10-04.md`

Content/conformance development should challenge the frozen design with small independent cases. A discovered contradiction should produce a focused issue/review packet rather than an immediate broad redesign.

## If the process starts feeling opaque

Stop broad automation and return to:
1. one minimal example;
2. one source requirement;
3. one proposed representation;
4. one expected result;
5. one human review decision.

The language should remain understandable without depending on ChatGPT, Codex, or a large CI run to explain what it means.
