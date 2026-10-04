# Pilot findings and questions for human review

Status: **pending-review**. These findings do not authorize semantic changes.

| Finding | Classification | Disposition |
| --- | --- | --- |
| Dependency analog declares binary `true`, compares Boolean | Probable source content defect | Original minimal closure preserved under `tests/focused-regressions/board-pilot/`; do not silently change datatype |
| Filter analog comments imply three traversed directories, but executable Object selects one without recursion | Source content documentation defect | Preserve extract and explain actual selection; native filter sample is explicitly inspiration only |
| Native `a → b → a` local Variable cycle receives no core semantic diagnostic | Semantic-validator defect/gap | Minimal native reproducer; pilot-local guard rejects cycles without changing shared semantics |
| Legacy intermediate converter does not supply a strict native direct-Variable 0.2.0 authoring path | Converter limitation (documented legacy bridge) | Minimal constant-source reproducer; Board conversions are explicit manual transcriptions, no converter/schema edits |

Expected OVAL behavior follows typed Variable value and comparison contracts;
the dependency source's description “always true” is not an independent oracle.
The binary `true` text is not a valid hexadecimal binary value. The source XSD's
generic string content may not catch this semantic problem. The proposed upstream
question is whether the author intended Boolean; changing it is an upstream
content correction, not a Board decision to add coercion to native NG.

Questions remaining for acceptance:

- Confirm the five manual transcriptions, especially direct Variable Item/value
  aggregation, against the source closures and the frozen mappings.
- Confirm that the selected-criterion scope is suitable for the Board package;
  none of the three fragments claims complete source Definition equivalence.
- Independently corroborate collector defaults and acquisition behavior for
  exact file and registry selection. The pilot covers supplied observations only.
- Review and repair the shared local dataflow-cycle validation gap in a separate
  bounded task. Existing acyclic semantics apply; no new schema capability is needed.
- Decide when a strict native converter path should replace manual transcription;
  this is separate converter work after review, not permission to expand this pilot.

No new normative requirements or yes/no semantic decision are proposed here.
No accepted decision record is created by machine-green validation. Existing
post-freeze semantic authority remains unchanged.
