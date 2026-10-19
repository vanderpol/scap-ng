# External authoring-language comparison gate — SCAP-NG 0.4-C and SLANG

**19 October 2026 · issue #245 · Preparation criterion, not an invitation sent or an accepted design decision.**

## When the project owner should invite David Solins

**Not yet for the formal comparison.** The current first review pack contains eight source-compiled OVAL Self-Assertion Definitions, dominated by small checks. Those do not challenge the language strengths or trade-offs meaningfully. Invite him **when the first meaningful complex family converts into a genuinely compilable 0.4-C Assessment with source-conserving behavior and a counterexample suite**—do **not** wait for every one of the 785 original OVAL Tests to be converted, and do **not** wait for 0.4-C to be frozen. His critical feedback is more valuable while changes are still practical.

### Objective readiness gate

- **Required example 1 — original OVAL full Set/Filter/Variable dependency closure:** at least one actual pinned OVAL 5.12.3 Self-Assertion Definition containing a nested Set or Filter and a runtime-dependent Variable, translated to readable C authoring, lowered back to source-compatible typed IR, preserving original comments/source IDs and membership/collection semantics. An explicit *compatibility fallback alone does not qualify* as a full C authoring conversion.
- **Required example 2 — complex multi-Test conditional requirement:** at least one actual STIG assessment with genuine OVAL AND/OR evaluation or role-based alternatives, grounded original source, readable C `require` tree and confirmed per-Test identities. The existing Windows Server/Windows 11 multi-Test source-backed prototypes can become the example after their source and compiler equivalence gates are complete.
- **Required example 3 — causal acquisition + derived values:** an Apache/DNS/Unix original with an observation that depends on collected values to drive a further collection; show source command/selector and value multiplicity; avoid hiding dynamic dependencies inside misleading scalar syntactic sugar.
- **Counterexamples:** complete/empty/incomplete/error/unknown/not-applicable; source `check_existence`, `check`, `entity_check`, `var_check`; Set Filter include/exclude membership, nested refs, and any unsupported source constructs explicit. Preserve all original source titles and test comments. Show independently justified expected outcomes; *source round-trip success is not scanner parity*.
- **One concise blind-reading packet:** side-by-side original OVAL XML/logic, source-equivalent 0.4-C, and a space for a **genuine SLANG translation supplied or checked by its author**. Never fabricate SLANG syntax from superficial similarity. Give the reviewer the same semantics and the same source example; include the explicit behavior table, authoring-size/readability dimensions, provenance and evaluation boundary claims.
- **Reviewer questions:** Which constructs does SLANG make clearer? Which C pieces are unnecessarily verbose or hide dependencies? Are presence, matching, cardinality, correlation, and shared evidence obvious without separate documentation? Which cases are genuinely inexpressible? What should be kept as typed internal OVAL compatibility versus surfaced to authors?

## Process

Track the gate and independently reproduced examples under [#245](https://github.com/vanderpol/scap-ng/issues/245). On passing, recommend to the owner: **“This is ready for David Solins to compare with SLANG.”** Do not contact or schedule external reviewers without owner action. This is an **informal critique invitation**, not a Board standards vote, and **not** a request to choose a winner before real evidence exists. Share an accessible GitHub read-only page rather than an expiring CI ZIP. Continue 0.4-C research after creating this gate; no new owner decision is needed for present implementation.

**Current checkpoint:** [First source-backed native C review](C-REVIEW-START-HERE-2026-10-19.md) offers eight small original OVAL Test conversions and research prototypes for more complex cases; source-compatible A roundtrip covers 162/167 original Self-Assertion Definitions. Complex Set/Filter/Variable C authoring and source/evaluation parity do **not** yet pass the above formal comparison gate.
