# 0.4-A static source-dataflow census — October 18, 2026

**RESEARCH_NOT_EXECUTABLE.** This is a graph and source-path audit, not an OVAL six-state runtime proof, scanner instruction plan or released 0.4 specification. Tracking: [#240](https://github.com/vanderpol/scap-ng/issues/240), [#232](https://github.com/vanderpol/scap-ng/issues/232), [#239](https://github.com/vanderpol/scap-ng/issues/239).

## Reproducible integrated gate

[Exact-head CI run 39139469580 — PASS](https://github.com/vanderpol/scap-ng/actions/runs/39139469580) validated the integrated YAML/JSON → base 0.4-A research-authoring path, complete lossless source-envelope IR v0.2 roundtrip, its Draft 2020-12 research schema, **ten** standalone dataflow graph cases, **three** independent census fixtures, and 19 complete IR adversarial cases.

Run the exact research-only census after generating the verified base archive and the IR:

    python tools/v04_a_dataflow_census.py --ir /path/to/a-lossless-ir.json --out-report /path/to/a-dataflow-census.json --assert-six

The census independently decodes and checks the entire IR before reporting any totals. This stage uses six frozen STIG authoring sets and does not run the 65-source release gate.

## Distinct six-STIG source observations

| Measure | Count | Meaning |
| --- | ---: | --- |
| Authored source documents | 4,001 | Parsed source docs, including policy/manual |
| Automated Assessments | 872 | Distinct files, not repeated benchmark occurrences |
| Named Tests | 1,375 | Distinct automated Test nodes |
| Rule Assessment choice links | 2,958 | Includes automated and manual alternatives |
| Named Variables | 377 | Distinct declarations across automated Assessments |
| Named shared Objects | 91 | Distinct declarations across automated Assessments |
| Variable references | 455 | Literal source-reference occurrences, not unique values |
| Object acquisition references | 201 | Literal source-reference occurrences, not unique collections |
| for_each sites | 8 | Source collection-expansion sites, **not** per-Item Tests |
| Set sites | 162 | Ordered Set source AST locations |
| Filter sites | 190 | Ordered include/exclude Filter AST locations |
| Selector projection sites | 8 | Explicit from-alias source binding sites |

All counters are derived from the *base-grammar staged* source AST and retain source paths. They must not be confused with converted source OVAL graph counts, shared per-Benchmark repetitions, or runtime executions.

## Real source anchors recovered by the census

- **Oracle Linux 9 / SV-271791.automated:** Filter witness at authoring/oracle_linux_9/assessments/automated/SV-271791.automated.json.
- **Shared Linux initialization-file modes:** for_each source and from-selector projection witness at authoring/shared/assessments/linux/other/initialization-files-0740-less-permissive.assessment.json.
- **Shared Windows root certificate store:** Set witness at authoring/shared/assessments/windows/registry/dow-root-ca-trusted-root-store.assessment.json.

Those paths are logical paths inside the immutable/research package, not guaranteed tracked paths on main. The CI step summary includes the exact audit report's representative source IDs and paths.

## What was implemented

The [A source-dataflow index](../../../tools/v04_a_dataflow_index.py) preserves named Test/Object/Variable identities, source hashes, repeated reference edges, collection and foreach-source dependencies, and exact Set/Filter/selector lexical locations. It checks missing references and cycles in the combined named Object+Variable source graph, independently of Assessment truth-dependency graphs. The [research IR v0.2](../../../tools/v04_a_lossless_ir.py) embeds this index with every complete source AST, so the independent decoder can verify dataflow indexing was not forged or lost.

The graph's deterministic dependency-first ordering is **not** a scanner schedule. It does not evaluate Variable operators, create repeated Test outcomes for foreach loops, reorder Sets, push filters to collection, or infer completeness/error/unknown/not_applicable behavior.

## Next engineering boundaries

1. Verify correlated for_each alias scope and source Item lineage (including inherited aliases) without changing Assessment truth; keep actual field type and status conformance a separate gate.
2. Produce independent six-valued tests for variable/collection dependency errors, partial Items, Set include/exclude and nested for_each; no expected results from the implementation under test.
3. Only after explicit grammar and version policy acceptance in #227/#232, promote compiler instructions into a separate native executable packaging gate. Never rename this research ZIP or IR as a signed/scannable bundle.

**Do not use green structural source tests as a scanner equivalence claim.**
