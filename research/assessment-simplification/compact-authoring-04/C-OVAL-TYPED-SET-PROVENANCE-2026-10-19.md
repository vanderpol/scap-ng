# 0.4-C — original seven-Test OVAL Set authoring with separate source provenance

**19 October 2026 · Research [#245](https://github.com/vanderpol/scap-ng/issues/245) · Original source conversion, not accepted schema or scanner execution parity.**

## What we tested and why

The Apache source proved a practical authoring improvement by moving compiler-owned original Test/Variable IDs, local kind/datatype tags and source graph fingerprints into a mandatory sidecar. **The second, independent source family now passes the same architectural test:** the actual original [OVAL Self-Assertion `unix/oval-def_set-unix.xml`, Definition 276](https://github.com/OVAL-Community/SCAP-Self-Assertion/blob/e3538595c5083b9c34d937a81d319234df9bbfaa/SCAP_1.4/OVAL_Test_Content/unix/oval-def_set-unix.xml), pinned to commit `e3538595c5083b9c34d937a81d319234df9bbfaa`.

The [experimental original-OVAL C authoring/compiler](../../../tools/research_c_oval_hybrid_provenance.py) generates **two separate YAML files**. The author-facing file has named `observations`, original nested Set/Filter operations and object acquisition configurations, four `expected_values` including explicit multi-value `value_match: one`, seven named `checks` containing clear `must` cardinality/matching requirements, and an explicit `require: and` tree. The source provenance companion retains all original 11 Object IDs, four State IDs, seven Test IDs, three source Constant Variable identities (with their descriptions), typed spec metadata and source SHA-256.

**The author-facing file has zero legacy Object, State or Test IDs.** Names come from the actual Check purpose or observed file path/recurse direction; collisions fail closed or receive a stable suffix rather than silently coalescing evidence.

## Verified actual original-OVAL test corpus proof

[Successful original-source GitHub workflow 39340665991](https://github.com/vanderpol/scap-ng/actions/runs/39340665991) checks out the pinned original OVAL XML, uses the independently maintained v003 lowering to produce original A source graph, projects the C authoring file and source provenance companion, **serializes both to YAML, reloads them**, and compiles them through the existing C inline-constant/must-to-A compiler without passing the original Assessment into the compiler.

The result is an **identical complete structured A source graph**:

| Original OVAL family | Independently recreated |
| --- | ---: |
| Tests | **7 / 7** |
| Objects | **11 / 11** |
| Nested Set Objects, UNION / INTERSECTION / COMPLEMENT | **7 / 7** |
| Source States, including Filter State references | **4 / 4** |
| Source constant Variables, including multi-value exactly-one matching | **3 / 3** |

Actual source statements/commands/regexes, recursive Object behaviors, Set operand order, Filter exclude operation and matching cardinalities are not simplified or silently normalized by this C authoring adapter. The independently tested compiler is an **authoring-to-IR converter**, not a new Set evaluator or a test of scanner behavior.

The [focused regression run](https://github.com/vanderpol/scap-ng/actions/runs/39340610348) passed **342 tests**, including source-binding omission/collision rejection, changed Filter membership and changed Test cardinality counterexamples, and YAML serialization.

## Measured authoring burden

| Same real original seven-Test OVAL source | Full inlined-hybrid | New author-facing split | Required provenance companion |
| --- | ---: | ---: | ---: |
| YAML lines | 328 | **298** | 50 |
| UTF-8 bytes | 14,057 | **9,627** | 3,319 |
| Original long Object IDs shown as authoring names | 11 | **0** | 11 |
| Original State IDs shown as authored references | 4 | **0** | 4 |
| Original Test IDs in authored checks | 7 | **0** | 7 |
| Authored constant Variable declarations | 0 | **0** | 3 original source identities retained |

Moving compiler-owned source IDs and descriptions away from the author yields **30 fewer authored lines and 4,430 fewer authored bytes (31.5%)** on this real nested-Set example. The sidecar is mandatory and explicit; total bytes of both files are **12,946**, down from 14,057 in the previous single YAML presentation. The additional file does **not** hide source meaning—the actual typed Set, Filter, and collection logic remains visible in the author's observations, and author changes deliberately compile into a different typed IR.

The GitHub Actions artifact in the verified run contains `c-hybrid/oval-set-seven-tests-author-only.research.yaml`, `c-hybrid/oval-set-seven-tests-provenance.research.yaml` and `c-hybrid/oval-set-seven-tests-provenance-proof.json`. Generated artifacts are temporary; the compiler, pins, source and this review page are durable in GitHub.

## Recommendation and limits

**GO for further 0.4-C authoring research on this architecture, not an immediate normative specification change.** Two meaningfully different real source families now support required provenance separation with exact graph reconstruction: (1) original seven-Test OVAL Sets/Filters/multi-value constants, and (2) original Apache five-Test/nineteen-runtime-derived-value command chains.

**Do not call it complete 0.4-C conversion yet.** The current native Self-Assertion compiler still handles **20 of 162** source-compatible Definitions, with 142 not yet natively converted; the complex seven-Test example uses this research adapter and is not added to that official native C count. The two special-purpose sidecar adapters need consolidation into one tested C grammar and compiler. Original OVAL scanner-result conformance—especially empty populations, unknown, error, not_applicable and Set/Filter matching—is **not proven** by source graph equality.

The next efficient work is to unify source-provenance resolution across the two C samples, then check the resulting authoring format on other source families (Windows registry/records, Linux file/permissions, version/IP typed comparisons), before Board review or external SLANG comparison. This approach **preserves OVAL's complex internal dataflow** while proving actual authoring reductions instead of simply calling Objects “observations.”
