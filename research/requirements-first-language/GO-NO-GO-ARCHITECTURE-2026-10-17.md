# SCAP-NG requirements-first authoring — evidence-led go/no-go

**17 October 2026. Research recommendation, NOT adopted v0.4.0 normative specification or release.** Issues #235 (auditor authoring) and #229 (lossless OVAL semantics). All work on main.

## Decision: GO for a native authoring pilot; NO-GO for directly replacing source-compatible conversion

**GO — requirements-first native authoring language as the leading human-written candidate.** Eight complete native research files now compile into ONE typed recursive AST for named singleton resources, optional or required populations, all/any conditions, and nested parent-scoped DNS signing-key checks. Fixture execution tests cover complete empty vs unknown/incomplete, source errors vs policy violation, cardinality, provider acquisition identity, duplicate Items, source-independent bitmasks, selected vs compliant Items and parent-child misassociation. Linux mountinfo can be actually read on a CI Linux host. A read-only Apache static configuration collector and a synthetic Windows DNS zone/key normalizer feed the SAME native AST. Deterministic auditor explanations are generated from the tested AST and published on GitHub main.

**NO-GO — claiming this simple native AST is already a lossless converter for arbitrary SCAP 1.4-derived OVAL content.** None of the five pinned research source Assessments has scanner-verified native-equivalent end-to-end six-state behavior. The original source reveals mismatches with obvious shorter rewrites:

| Original source sample | Difficult source-specific requirement | Current native lowering |
| --- | --- | --- |
| RHEL /home | Literal source regex, repeated option entities and original completeness semantics | Native real mount provider works; source equivalence NOT proved |
| Windows user right / WMI | Whole-State OR across grouped WMI DomainRole records; mixed [1,3] must not become per-value membership | Synthetic grouping proof only; no real WMI collection or source-conformant lowering |
| Linux account-derived initialization files | Global union of root-derived files, field presence, OVAL Set/difference/traversal and eight permission flags | Complete 12-bit permission-mode equivalence proven; source collector/evaluator parity NOT proved |
| Apache session limits | Four distinct required shellcommand Item populations, 18 derived Variables, two distinct config discovery routes, optional subfields and explicit error flags | Typed static Include provider and new two-directive policy, NOT a proven reduction of original four Tests |
| Windows DNS validity | Five shellcommand Tests, zero output values vs shell Item existence, key type and zone grouping, separate State bounds, source exception conversion to string 0 | Structured zone/key fixture normalizer and native nested rule, NOT source-equivalent |

**Current parity evidence:** verified end-to-end native source parity on the five pinned cases: **0 / 5**. This is a report of missing proof, NOT a claim that all five cannot ever be converted.

## How to avoid recreating OVAL as the human authoring standard

Use **one auditor-facing authoring language**, not two competing human syntaxes. Keep one **versioned, typed internal evaluation IR** and one results model. Both compiler inputs lower into that IR:

1. **New human-authored requirements:** a direct typed resource, or a clearly scoped collection with an optional positive minimum and explicit MUST predicates. The language should be no more complex than necessary to express the actual security intent; e.g. a numeric POSIX permission-mask operation instead of eight separate OVAL Boolean fields.
2. **Forward-imported SCAP 1.4 content:** the converter must faithfully retain any unusual Items/States, entity cardinality, derived collection dependency, record grouping, command flags and exact six-state results. Those compatibility details live in internal typed IR nodes and provenance, **not in the normal auditor authoring syntax**.
3. **Same scanner evaluator/results:** source-compatible IR and native IR must use the same typed evidence/provenance mechanisms and decisive-result contract where the semantics match. Compatibility-specific IR operations must be explicitly versioned and tested, not silently rewritten to simpler native operations.

A single IR/evaluator is the **preferred target architecture, not implemented today**. The source-compatible lowering and full six-state runtime do not exist. It is also not guaranteed every OVAL operation can be represented by the native authoring subset; that is intentional. If needed, a converted Assessment may carry compiler-generated compatibility nodes that auditors can inspect in a read-only explanation. An editor should not invite humans to hand-author those nodes.

**Important fallback:** keep current 0.3/0.4 OVAL-aligned source-compatible work unchanged until the common IR and converter show parity. If the shared evaluator/IR cannot preserve source semantics at reasonable cost, we must preserve the existing source-compatible execution design rather than sacrifice mandatory forward conversion or quietly mark content compatible.

## Why this qualifies as more than wordsmithing

The measurable engineering evidence is not YAML line count:

- The same strict compiler AST accepts **eight** native examples, including both a named required singleton and nested correlated zone-key sets; errors are not hidden as false success.
- New native expression of permission-bit containment matches the eight original boolean fields across **all 4,096 POSIX 12-bit modes**, under the explicit complete-bitmask assumption.
- The Linux file collector was changed to stream/bound evidence instead of sorting entire directories. The Apache source collector preserves raw file and line identities and fails closed for unsupported conditional includes, macros, duplicate includes, limits and config loops. Structured DNS fixture evidence retains separate key types and correlation and refuses absent-key default Pass.
- Native result and collection tests exercise error/unknown, complete empty, partially observed violations, provider identity and cardinality differences. These are fixtures and prototyped collectors, NOT full host-scan or original OVAL parity tests.
- The generated auditor prose is produced from the same compiled AST; it was challenged and corrected for unclear "selected resources" wording.

## Gates before promoting this to normative v0.4 or tasking a full editor

| Required gate | Status |
| --- | --- |
| Eight real native policies compile to one typed AST with negative validation | PASS, research |
| Selected population, positive minimum, nested parent/key ownership and partial results tested | PASS, synthetic |
| One native provider reads actual Linux host data with identity/coverage | PASS, limited Linux mount namespace |
| A reusable Apache source provider and structured DNS zone/key prototype | PASS for fixture-defined subsets; NOT runtime-effective/scanner parity |
| Native reader can AUTHOR and correctly explain unfamiliar complex requirements | OPEN — no truly independent authoring test |
| Full native six-state evaluator, including not evaluated/not applicable/manual/org-input provenance | OPEN — current evaluator is only a research subset |
| Complete versioned typed-provider catalog, platform coverage and caching | OPEN |
| SCAP 1.4 conversion through single internal IR with source-level parity fixtures | BLOCKED/OPEN — verified 0/5 |
| Per-benchmark conversion metrics and all six reference STIGs assessed | OPEN |
| One scanner implementation (Windows/Linux/macOS) and source/native result parity | OPEN |

**Current recommendation:** proceed with the **native authoring plus compatibility IR** architecture, but DO NOT freeze syntax as normative 0.4, deprecate source-compatible mechanisms, present a short native Apache/DNS check as a verified conversion, or build an opinionated GUI editor yet. Define the common IR and six-state outcome/evidence contracts next. Apply this pilot to all six STIGs before concluding the architecture scales.

## When to invoke Gemini

An additional independent review is now useful **only if** it is blinded to the internal judgment, sees the real authoring YAML, provider contracts and adversarial examples, and is asked to author a new policy and find false equivalence, not merely to score keywords. The previous ChatGPT review was context-aware and remains an internal feedback loop. Review conclusions cannot substitute for scanner parity tests.
