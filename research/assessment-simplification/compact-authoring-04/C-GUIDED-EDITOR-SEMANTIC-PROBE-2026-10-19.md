# C graphical editor feasibility — semantic projection probe

**19 October 2026 · research #245 only · experimental, not normative.** SCAP-NG 0.4-C is the sole development priority; do not modify the separate browser editor or promote C syntax while proving this research.

## What has actually been built

[Experimental Guided projection and edit adapter](../../../tools/research_c_guided_projection.py) and [focused regression tests](../../../tools/test_research_c_guided_projection.py) use the existing C `from / must / require` research grammar. They do **not** create a new C dialect, UI, source-preserving YAML writer or authoritative scanner.

The adapter projects each C Assessment into a **source card**, an explicit **Item-population requirement**, **same-Item field predicates**, and a separate **Assessment logic tree**. An editor can render these as a small form without asking the author to manipulate A's Object/State/Test wiring. Crucially, the projection does not imply that fields on different collected Items can satisfy one State, nor that an Assessment-level AND/OR is an Item quantifier.

It exposes bare `must` as **implicit_any_item with a warning and no Guided edit shortcut**. An auditor should choose explicit `any_item` or `every_item`; a shorter implicit form should not be accepted until independent first-read testing shows it is unambiguous. Advanced source-preserving requirement pairs stay viewable but locked for this restricted Guided prototype.

The patch proposal path handles bounded operations: renamed check identities (with updated Boolean references); an expected literal with preserved scalar type; item quantifier; source collection parameter; and root AND/OR. **Changing quantifiers, collection inputs or AND/OR requires explicit acknowledgement** because these are new policy, not harmless cosmetic edits. Patch proposals copy the original AST, refuse invalid or ambiguous edits, invoke the existing C compiler/source-compatibility adapter where supported, and return a new AST for external human diff review. The source YAML text is never mutated or claimed comment-preserved.

## Source-backed examples and negative cases

- [Two real Windows checks composed as new policy](c-two-windows-checks.research.yaml): WDigest `DWORD 0` on the **same Item**, WMI query for non-NTFS disks with `absent`, and two named Test results combined by AND. The composed C compiler preserves native Registry fields and pinned WMI source-compatibility lowering; editor projection is independent of Test execution.
- [DNS PowerShell RRL](c-short-windows-dns-rrl.research.yaml): explicit shell/interpreter, original command and error flags; editing expected stdout goes through the pinned A-compatible native field mapping. No collection execution is implied.
- Adversarial cases cover nonexistent Test references, bad generated IDs, duplicate rename targets, string `"0"` versus integer `0`, unsafe unacknowledged quantifier/source changes, WMI query drift, unpinned Registry type enum and ambiguous bare `must`.
- Research test functions include compiler-backed integration, but a committed test file is not evidence of a passing exact-head GitHub Actions run. Inspect [focused C workflow](../../../../.github/workflows/research-c-shared-engine.yml) at the tested SHA.

## Why this is plausibly easier than 0.4-A Graphical

An ordinary C check exposes:
1. **What am I inspecting?** Search a version-pinned native capability and complete its selector/collection arguments.
2. **What must be true?** Choose `present`, `absent`, `any_item`, `every_item`, or an advanced source-compatible quantifier, then select capability-defined fields and typed comparison inputs.
3. **How do checks combine?** A compact nested tree of named check references and AND/OR/NOT, with separate six-state execution elsewhere.

The native A-like Item, record, State, Variable, filter and dataflow hierarchy remains available through a detailed provenance/source panel. Do not hide an unsupported complex node and silently regenerate it on save. For a full editing product, generic recursive coverage remains mandatory rather than being replaced with a read-only YAML fallback.

## Remaining C decision gates

- Generalize the adapter beyond a bounded handful of capabilities while preserving source-exact field/value datatype, record correlation, per-parent `for_each`, filtering, Sets, nested conditional and organizational input semantics.
- Build a source-backed complex Windows/Linux Guided fixture with deeply nested same-record checks and shared observations; prove that a novice can correctly predict absent/partial/error behavior.
- Connect to a **single deterministic C compiler** and pinned A execution representation, preserving exact imported source graph/provenance. The current WMI branch explicitly uses a source-compatibility adapter and should not be mistaken for native A support.
- Independent native scanner and six-STIG parity gates remain open. This projection is authoring feasibility evidence only, not a substitute.
- **Separate editor development is on hold** while C research is the sole priority. Do not modify `vanderpol/scap-ng-editor` under this workstream.

**Provisional conclusion:** C's simple check/require mental model looks materially better suited to Guided authoring than exposing A's full Object/State/Test model, but complexity has not been eliminated until a deep nested case and complete reversible lowering prove it.
