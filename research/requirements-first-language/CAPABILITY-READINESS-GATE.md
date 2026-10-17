# Requirements-first candidate B — capability readiness gate

**Research only · 17 October 2026 · issue #235.** This is a development checklist, **not a bake-off**, a release plan, or acceptance of a new SCAP-NG specification. Keep the OVAL-derived candidate A unchanged and continue on GitHub main. Do not create parallel release branches or publish a 0.4-B normative version.

## Decision and ordering

**Do not compare A and B as competing specifications until B reaches broadly comparable functional capability and coverage.** A's current six-STIG OVAL-derived conversion research is much more extensive than B's eight native fixture examples. A bake-off now would be misleading.

Build **B** first; A remains the source-compatibility reference. The goal is **equivalent scope of problems solved**, **not the same implementation model, number of native expressions, YAML keys, or internal Test/Object/State syntax**. Compiler-owned source compatibility operations are legitimate if source meaning is preserved and their amount and auditability are visible.

No weighted authorability/readability scoring or selecting a winner before the gate below. Intermediate tests and source comparisons are **engineering validation of B**, not an A-versus-B bake-off.

**First verified corpus engineering milestone:** The [six-STIG source-accounting CI](https://github.com/vanderpol/scap-ng/actions/workflows/research-b-six-stig-source-import.yml) has already processed the published 0.3 six-stream authoring ZIP. The B-only [feature census](contract-candidate/corpus/feature-inventory.md) confirms which Test capability families actually dominate each platform, rather than assuming sample Assessments are representative. No native conversion/evaluation parity is claimed. Raw SCAP 1.4 XML import still needs its own gate.

**First executable native source-shape pilots (not parity):** [Linux /var/tmp must exist and Chrony cmdport 0](contract-candidate/FIRST-SOURCE-BACKED-NATIVE-PILOT.md) now use native requirements backed by exact source Assessment specimens from the six-stream 0.3 authoring cohort. A bounded read-only textfile regex collector is tested with actual temporary files, explicit observed Items and incomplete/error status. These remain examples of B-native *policy shapes*, not verified OVAL Test/State/Object conversion. Structural coverage is six streams; executable source-equivalence coverage remains unproved.

## Capability criteria for B

| Area | Comparable-capability readiness criterion | Current B evidence / gap |
| --- | --- | --- |
| Complete source cohort | Inventory and account for every Assessment, Test, source dependency and Rule association in the same six source STIGs: RHEL 9, Oracle Linux 9, Windows 11, Windows Server 2025, Windows DNS and Apache | **Partial — six-stream structural accounting passed**, with 1,567 Rules, 2,395 distinct referenced Assessments, and 2,958 choice bindings from the published 0.3 authoring ZIP. [Source accounting](contract-candidate/corpus/source-accounting.md) and [capability inventory](contract-candidate/corpus/feature-inventory.md). Still need raw SCAP 1.4 XML source coverage, assessment semantics and fully executable B. |
| Conversion workflow | Repeatable importer from the full SCAP 1.4 cohort to B's native authoring where equivalent, and explicit compiler-owned compatibility IR where not; fail-closed conversion of unsupported constructs | **Partial — full six-stream authoring ZIP importer**, with fail-closed missing references/duplicate IDs and nonexecutable source capsules. [Implementation](../../tools/research_b_full_corpus_import.py). Native rewriting, executable compatibility IR and raw SCAP 1.4 conversion remain open. |
| Core test/evidence semantics | Typed resources, selection, existence and matching, complete/partial/error acquisition, Items, fields, records and per-source aggregation with all **six** result outcomes | **Partial**; B has a small fixture evaluator and an OVAL Test-level compatibility dispatcher only. |
| Control flow | AND/OR, conditionals with defined unknown/else rules, nested correlated populations, loops, typed values and version comparisons | **Partial**; native groups and DNS child correlation work in fixtures, generic conditional/foreach coverage is open. |
| Reuse and scaling | Shared collections/assessments, consistent path references, cross-benchmark acquisition reuse and explicit caching/identity scope | **Open**; experimental provider contracts only. |
| Platform sources | Linux paths/mounts and recursive filesystem traversal, Windows registry/WMI/accounts/user rights, DNS zone/key groups and Apache config/runtime source distinctions | **Partial**; actual Linux mountinfo, limited static Apache and structured synthetic DNS fixtures, no production Windows providers or proven source parity. |
| Human/manual/organizational policy | Manual checks, automated/manual selection, organizational input with provenance, benchmark/rule/applicability integration | **Open** in the candidate B compiler; legacy research sketches are not executable B support. |
| Schema and authoring | Complete versioned grammar/provider catalog, strict typing, field/operation and relation checking, meaningful diagnostics and auditor-readable previews | **Partial**; B compiler/prototypes exist but not a complete standalone editor or authoring contract. |
| Results and evidence | Benchmark-linked rule outcomes, six-result assessments, decisive reason, completeness/limits, provenance and bounded evidence/reporting | **Open** as an integrated B results implementation. |
| Verification | Source identifiers retained; automated positive/negative fixtures for all important source feature families, source-parity discrepancies tracked, CI runnable, no silent source loss | **Partial**; semantic counterexamples proven but end-to-end source parity remains unverified. |

**Readiness is not a demand for identical performance, identical source-conversion percentages into native syntax, or a complete production scanner.** Both candidates can use unimplemented scanner features as long as they are compared at a genuinely matched level of specification, compiler, validation, provider-contract and source coverage; all unproven semantics must be transparent. A native-plus-compatibility representation is allowed, but B must **actually support it**, not merely propose it.

## Development order before the bake-off

1. Finish B's normative-quality **research grammar, field/provider contracts, error/results semantics**, strict compiler and tests.
2. Make B support representative complex Linux, Windows, DNS and Apache patterns with source-pinned fixtures, genuine error/unknown/cardinality/record identity checks and compatible IR operations.
3. Build B's **repeatable full RHEL 9 source importer and coverage inventory**, including source-compatible fallback and a ledger for any unsupported features. This is a B implementation and correctness test, **not** a bake-off.
4. Extend B's importer and capability contracts to Windows 11 and the other four STIGs, tracking all missing native, compatibility and source behaviors.
5. Review this gate, identify significant capability disparities and **develop B further** until B can reasonably address the same source cohort and feature families as A.

Only **after** comparable capability is demonstrated should the project create a separate, controlled A/B bake-off measuring auditor comprehension, authorability, complexity, correctness, development cost, reuse, performance characteristics and operational reporting against the **same frozen source content**. Candidates may remain research labels **0.4-A and 0.4-B**; neither is necessarily the eventual release labeled 0.4.0.

## Stop/go for the next work iteration

**Go now:** B grammar/catalog/IR and six-benchmark import/coverage engineering, with source-compatible A as a reference and fallback.

**Not authorized yet:** competitive A/B scoring, announcing a winning specification, freezing v0.4.0, merging experimental B syntax into A's normative schema, or claiming verified lossless conversion without execution tests.
