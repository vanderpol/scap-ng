# Source-generated Collection and Variable review

**Status: tested dataflow prototype, not a complete Benchmark compiler or a finalized NG specification.**

This sample was converted directly from the pinned original RHEL 9 source ZIP. It was not made by rewriting earlier NG YAML. It includes Assessments selected from 25 Rules; some Rules share one source Definition across selectors. The source checks produced 23 distinct automated Assessments and manual alternatives. Source selectors are recorded in evidence.json; this step does not re-render complete Rules, Profiles or applicability.

## Start here

- [Shared Collection: dconf database names](assessments/automated/SV-258013.automated.assessment.yaml): a Test and a Variable explicitly consume the same named Collection. The derived Variable supplies another Collection selector.
- [Variable-only Collection and calculated values](assessments/automated/SV-258155.automated.assessment.yaml): a Variable declares the independent data-source capability; other operands reuse a Test-typed Collection.
- [Sets, filters and multiple Variables](assessments/automated/SV-257889.automated.assessment.yaml).
- [Multiple-State Test](assessments/automated/SV-257777.automated.assessment.yaml).
- [Source graph bindings and comparator results](evidence.json), [all 42 Variable-bearing source checks](all-variable-rules-check.json), [reverse omni-schema validation](reverse-schema-validation.json), and [vocabulary preflight](readiness.json).

## Working syntax

- Test IDs have `test-`; Collection and Variable IDs contain their type markers.
- Tests reference `collection: <named-id>`. Collections are declared once in `collections`.
- Variable expressions use `values: {collection: <named-id>, field: <item-field>}`; `record_field` remains available.
- A Variable can reference another Variable through `variable: <named-id>`. Existing function trees and intermediate Variable boundaries survive conversion.
- Test-associated Collection/State capability is declared once on the Test, including compatible descendants reached through sets.
- For an independently typed named source used only by Variables, the prototype puts `collection_capabilities: {<collection-id>: <capability>}` on its Variable. Consumers must agree. This exact mapping spelling is an implementation proposal for Board review.
- Native authors may instead embed a private Collection in `expression.values.collection`, with its capability on the owning Variable. The regression suite checks this form and rejects external references to private Collections. Source conversion preserves source Objects as named Collections rather than erasing sharing.
- `assertion.item_quantifier` still uses the existing value vocabulary. Its final name versus `state_match` remains an authoring decision, not a settled standard.

## Validation actually performed

- 13 new source-identity/dataflow regressions passed, including an embedded private Collection, distinct source Objects with identical payloads, shared references, depth-32 Variable chains, sets, filter-hidden dependencies, cycles and contradictory types.
- The existing 16-test Variable/filter/set depth suite passed with its original assertions retained; schema-import paths were made portable for Windows. Effective-attribute, State-entity and explicit-semantics suites also passed (26 tests). Total executed focused regressions: 55.
- All 42 Variable-bearing RHEL 9 cases compared equal after source → named graph → regenerated OVAL, with root-scoped ID-independent semantic comparison.
- All 23 automated Assessments in this selected sample compared equal and regenerated OVAL validated against the pinned omni-schema. The native vocabulary guard reported no violations across 48 Assessment YAML files.
- The 13 new graph/local-ZIP regressions and 16 retained depth/filter/set tests passed on both Windows and Linux in [CI run 36775088506](https://github.com/vanderpol/scap-ng/actions/runs/36775088506). The ZIP CLI test runs from another working directory using a synthetic package.
- No target execution, complete language conformance, full Benchmark regeneration, full real-package conversion on Windows or finalized JSON schema validation is claimed.
- Broader CI passed the OVAL smoke, Linux expansion, Windows expansion and Self-Assertion checks. Diverse-platform expansion still reports the NGINX source capability mismatch `unix.file!=independent.shellcommand`; that blocker is retained, not bypassed.

## Reproduce locally

Run from the repository root with Python and PyYAML/lxml installed. No network or GitHub credentials are needed. The output directory must be new or empty.

```powershell
python tools/scap_upconvert_v003/convert_collection_review.py `
  --input "C:/SCAP/U_RHEL_9_V2R9_STIG_SCAP_1-4_Benchmark-enhancedV13-signed.zip" `
  --sha256 70aa6a16221df2c53b094b11b48b16aca1f6d7147c11123b655659ca7711dbb5 `
  --rules-file research/iterations/003/review/rhel9-diagnostic-review/inventory.json `
  --output work/collection-review
```

This is a portable research entry point; the real RHEL 9 sample command has been executed on Linux. Windows CI passed the local-ZIP command regression with a synthetic package; the full real-package Windows run remains pending. It produces the focused Assessment review, not the promised future full converter handoff. The source checksum is verified before parsing. The script invokes the maintained source lowerer with `collection_graph=True`; no historical authoring generator main function is run.

Observed dependency versions: PyYAML 6.0.3; lxml 6.1.1.

## Implementation boundaries and provenance

`lower_definition` retains the historical renderer by default while the full compiler and its consumers are migrated; this review entry point explicitly uses the new source-graph path. The reverse emitter explicitly selects the new `tests` grammar and rejects a mixed `checks`/`tests` document. Existing baseline artifacts are not regenerated. Historical publishing workflows are held to prevent this source-lowerer checkpoint from triggering another stale-format full build.

Provenance: **Inherited** for pinned original NIWC source and existing source semantics; **Common** for source-ID memoization and reference/type guards; **Evidence/Audit** for independent comparator/omni-schema checks and fixtures. Source IDs are retained only in evidence graph bindings, not native Collection/Variable IDs. The local source archive matched the recorded NIWC pin and SHA-256.

The remaining work is complete Rule/Benchmark rendering, parser/schema finalization, agreed quantifier vocabulary, broader consumer migration and full-platform regression before a stable Windows handoff. Capability placement remains a separate Board question; both Variable source forms remain required.
