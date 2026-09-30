# SCAP-NG development roadmap

Updated: 2026-09-30. [Open issues](https://github.com/vanderpol/scap-ng/issues?q=is%3Aissue+is%3Aopen) · [Completed issues](https://github.com/vanderpol/scap-ng/issues?q=is%3Aissue+is%3Aclosed) · [GitHub Actions](https://github.com/vanderpol/scap-ng/actions).

> **Tracking note:** These are **proposed milestone groups** denoted by title prefixes `[M0]` through `[M3]`. GitHub's native Milestones were **not created** because the available connected GitHub operations currently cannot create them. Never present the prefixes as native GitHub milestones. A future maintainer can create actual milestones and assign the issue numbers below.

## Phases and exit criteria

| Proposed milestone | Focus | Exit gate |
| --- | --- | --- |
| **M0 — Language-fidelity foundation** | OVAL 5.12.3 defaults, inherited attributes, variables, sets, cardinality, result propagation and regression corpus | Explicit semantic differences explained/fixed or recorded as blockers; reproducible source-pinned validation |
| **M1 — Full native benchmarks** | Split native benchmark/policy/assessment, source policy coverage, RHEL 9, Windows 11 and four-anchor reuse, manual questions/results | Complete reviewer handoffs on both primary benchmarks with provenance, links, diagnostics and clear nonblocking caveats |
| **M2 — Specification & authoring** | Normative language, JSON schemas, authoring tooling, reference conformance | Reviewed schemas/specification, usable content-author prototype and differential conformance scope |
| **M3 — Beta/1.0 & community transition** | Signed reproducible bundle, compatibility, scale testing, governance and transfer | Explicit owner release approval, tested distribution and planned transfer to OVAL Community with their authorization |

## Open work, grouped by proposed milestone

### M0 — language fidelity
- #7 — Fresh round-trip corpus baseline after state-entity existence fix.
- #8 — Complete pinned 5.12.3 XSD inheritance/default audit.
- #9 — Preserve resolved defaults and whether supplied explicitly or inferred in the semantic IR.
- #10 — Variable graphs, function composition, zero/multiple-value and external inputs.
- #11 — Sets, filters, state/test cardinality and evaluator result propagation.

### M1 — complete native benchmark sources
- #12 — Lock Rule / Policy / Assessment / applicability contracts.
- #13 — Full **RHEL 9** reviewer handoff. Full v003 generation exists; this issue tracks quality/semantic review gates, **not** generation alone.
- #14 — Full **Windows 11** reviewer handoff. Older iteration-001 257-rule conversion **does not** satisfy v003 native readiness.
- #19 — RHEL 9 / Oracle Linux 9 / Windows 11 / Windows Server 2025 reuse crosswalk.
- #20 — Manual questions, organization-specific inputs, check selectors and tailoring provenance.
- #21 — Compact results/JSONL, root cause, existence/nonexistence explanations, evidence caps.
- #22 — XCCDF benchmark/policy/profile/selector construct coverage and loss accounting.

### M2 — specification and authoring
- #6 — Pin OVAL XSD/Schematron and migrate assessor semantics into standards-ready specification text (preexisting issue; not duplicated).
- #23 — Versioned JSON schemas with schema-generated documentation.
- #24 — Content-authoring workflow prototype with source-to-Check Text/remediation navigation.
- #25 — Normative specification, glossary, SCAP 1.4 crosswalk and board-decision ledger.
- #26 — Reference evaluator and differential conformance testing once design stabilizes.

### M3 — beta, enterprise evidence, transition
- #27 — Beta release gates: signed bundle, reproducible packaging and compatibility.
- #28 — **OVAL Community transfer** readiness, governance, licensing, provenance, maintainers, rights and redirect/CI considerations. **Do not transfer without the owner's explicit authorization and receiving organization's acceptance.**
- #29 — Enterprise performance/offline work with quantified 100k+ host assumptions.

## Completed, evidence-backed historical issues

These were added after implementation and closed **only for the bounded work identified**, not as claims that SCAP-NG conversion is complete.

- #15 — Preserve explicit State entity `check_existence` through v003 native round trip and comparator; targeted CI regression.
- #16 — OVAL round-trip smoke and test workflow infrastructure.
- #17 — Initial complete RHEL 9 iteration-003 generation and publishing pipeline. **Full review readiness remains #13.**
- #18 — v003 native cleanliness, clean-room migration provenance separation and validation infrastructure. **Final contracts remain #12.**

## Status interpretation

- **Open:** not accepted complete, even if partial implementation exists.
- **Closed:** the bounded issue acceptance criteria have demonstrable code, artifact, tests or evidence linked inside the issue.
- **Blocked:** remain open, attach source-specific reason and unblock dependencies. Do not substitute a blanket “unsupported” or suppress a failing test.
- **Review-ready:** reserved for an independently verified full benchmark satisfying [the handoff gates](research/iterations/003/review/FULL-BENCHMARK-READINESS.md), not merely green CI or a generated zip.
- **Published beta / 1.0:** requires the owner's explicit release decision, regardless of issue closure.

## Operating practice

1. Each substantive converter feature belongs to an open issue, and its commit/test link is recorded in that issue.
2. A discovery from Self-Assertion or the production STIG corpus gets an issue or is added to the relevant open one; never conflate production migration coverage with language conformance evidence.
3. Each issue should contain source version, reproducer, expected semantics, actual results, provenance, acceptance criteria and CI evidence.
4. On success, close only the bounded delivered issue; keep broader fidelity/specification tasks open.
5. Avoid relying on labels/prefixes alone as proof of progress. Review [commits](https://github.com/vanderpol/scap-ng/commits/main/) and [CI](https://github.com/vanderpol/scap-ng/actions).
6. Maintain separate **hourly GitHub status reports** during active development and notify the user for full RHEL 9/Windows 11 handoffs when genuinely ready.

## Explicit deferrals and boundaries

- SCC `sqlext` stays outside this conversion scope until a source migration toward supported `sql512` is available.
- Deprecated OVAL tests are hard migration blockers unless subsequently reinstated by authoritative OVAL governance, as described in `AGENTS.md`.
- Do not silently repair publisher content bugs while claiming source equivalence.
- Do not leak original XCCDF/OVAL/OCIL/CPE XML IDs into executable iteration-003 native authoring source.
- The initial design effort emphasizes split policy/assessment; combined/Ansible-inspired variants remain comparison work, not the canonical v003 source.
