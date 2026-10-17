# 0.4-B scanner-facing JSON research boundary

**17 October 2026 · engineering pilot · #235 · not a normative 0.4 release.** This is **not an A/B bake-off**. One authored language eventually wins; this experiment asks what a scanner must execute if B is selected. Legacy SCAP 1.4 import is an input-conversion problem, not an invitation to expose OVAL Object/State/Test as a second B authoring language.

## Concrete files

- [Research JSON encoder/decoder](../../../tools/research_b_compiled_ir.py) converts a validated B Assessment AST into deterministic JSON with an explicit version, typed provider catalog/evidence-contract version, source-kind classification, semantic root, and SHA-256 corruption check.
- [Regression tests](../../../tools/test_research_b_compiled_ir.py) load all ten current native B examples, compare fixture outcomes across JSON decoding, exercise all six OVAL result values for a pre-evaluated compatibility Test, show mixed native/compatibility logical evaluation, and reject version, digest, and unknown-operation mutations.
- [Existing shared fixture dispatcher](../../../tools/research_native_contract_evaluator.py) interprets native B nodes and delegates narrow OVAL Test-level aggregation to the pinned [OVAL 5.12.3 reference tables](../../../tools/oval_result_truth_tables.py).
- [Full six-STIG scope gate](../CAPABILITY-READINESS-GATE.md): 1,567 Rules and 2,395 distinct referenced Assessments already source-accounted, but no claim of executable migration.

## Intended boundary (one scanner, not two authored languages)

~~~text
Human-authored B YAML  -> B compiler ---+
                                        +--> versioned B execution IR JSON --> B evaluator --> Assessment Results
SCAP 1.4 source XML -> importer/lowerer-+
                    (source-compatible operations where needed)
~~~

The **outer package** (Benchmark, Rule references, Profiles, bundle manifest/signature, applicability/policy, results) should remain independent of the internal authored syntax. Its existing draft specifies compiled canonical JSON; this experiment does **not** alter that normative package structure or A's draft schema.

The **executable Assessment IR** is intentionally not a copy of A's OVAL-derived authoring schema. The compiler owns internal compatibility operations; scanner vendors must implement their defined behavior, but auditors are not expected to write them. Even if the same scanner can dispatch both kinds of operation, it is **not** evidence that two independent engines or two accepted authoring languages are required.

## Why the boundary matters

The source [Windows 11 SV-253291](corpus/source-specimens/windows-registry-0-de183f784659.source.yaml) has a source existence requirement of `one_or_more`, an Item-State matching requirement of `one`, and a textual State value `'0'`; its converted source does not specify the WOW64 registry view.

The native B named registry provider instead requires **one logical resource** and currently a typed integer value and explicit view. A research compatibility Test aggregating two already-computed Item-State results `[true,false]` with OVAL `only one` yields **true**, while B's native named-singleton form rejects two Items as a provider-identity **error**. Those are **different contracts**. This example is a boundary demonstration, **not** a proven interpretation or conversion of the original SCAP 1.4 XML, which must be checked separately.

Thus merely converting the original Test into B's short native expression can silently change compliance results. A correct importer must either prove source equivalence for a specific class or retain an inspectable, versioned compatibility operation.

## First source-shaped execution over *observed* Items

The [state-free textfile source lowerer](../../../tools/research_b_source_textfile_lowering.py) accepts only the exact converted 0.3 source Test shape of [the shared Chrony `cmdport 0` Assessment](corpus/source-specimens/independent-textfilecontent54-0-4c14428014be.source.yaml). It rejects source States, different Item checks, additional collection options, nontrivial instance selectors and composite evaluation instead of guessing. The lowerer emits a **compiler-owned** `compat_oval_provider_existence` operation, not authored B syntax.

The existing [read-only textfile collector](../../../tools/research_provider_textfile_matches.py) supplies **actual typed, identified match Items**, not precomputed OVAL Test outcomes. The common B fixture dispatcher evaluates the source Test's existence using the pinned OVAL reference table. The [regression suite](../../../tools/test_research_b_source_textfile_lowering.py) creates real temporary files and proves the following intentionally divergent case:

| Observed source | Native B `exists` | Imported source Test (OVAL reference) |
| --- | --- | --- |
| Complete, one or more matches | true | true |
| Complete, zero matches | false | false |
| **Incomplete, one observed matching Item** | **true** (witness is decisive) | **unknown** (incomplete source Test) |
| Incomplete, zero matches | unknown | unknown |

**This is not a scanner parity claim.** Python regex, UTF-8 decoding, `filesystem: all`, `item_creation`, OVAL Item flags and full original SCAP 1.4 source XML remain unverified. The table demonstrates why one native B shorthand cannot be substituted for a seemingly equivalent imported source Test without checking the exact outcome domain and completeness contract. The source compatibility node runs with the **same typed collection result** and evaluator dispatcher, avoiding a second authored language.

## Proven and missing

**Implemented in research:** deterministic JSON encoding/decoding, contract/version/corruption checks, AST structural validation, mixed native and pre-evaluated compatibility aggregation plus a bounded source-state-free Test consuming observed Items, tests against pinned source Assessment structures, and explicit separation of native vs compiler-only input.

**NOT implemented:** complete generic source lowering or scanner parity; signed scanner bundle integration, independent JSON Schema conformance, real OVAL XML-to-B lowering, executable legacy Object collection, State and Variable evaluation, per-record/field cardinality, six-state full B runtime, actual Windows registry scanning, full source-equivalent evidence acquisition, reusable cross-host cache, results packaging, or parity on the six STIGs. The SHA-256 field is a **corruption check, not an authenticity signature**. The compatibility Test values here are *pre-evaluated*, not collected from a host.

## Next B development gate

1. Bring a **real source Object/State/Item** through explicit B compatibility IR, without supplying already evaluated Item results, and preserve all six source outcomes.
2. Prove per-source Item and nested field cardinality under complete/incomplete/error evidence, starting with Windows registry and WMI, while the high-volume Linux textfile family continues.
3. Evolve the scanner execution contract only from verified source behavior. Build the same six-stream native-or-compatibility coverage ledger before anyone evaluates A versus B authorability or implementation cost.

Track future A ergonomics separately in [#236](https://github.com/vanderpol/scap-ng/issues/236). No changes to candidate A here.
