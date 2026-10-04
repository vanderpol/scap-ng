# Pilot findings and questions for human review

Status: **pending-review**. Findings do not authorize semantic changes.

| Finding | Classification | Disposition / reproducer |
| --- | --- | --- |
| Direct Variable Tests remain `independent.variable` after automatic mapping and fail strict 0.2.0 | Converter limitation | `tests/focused-regressions/board-pilot/constant-source.xml`; earlier constant/concat manual seeds stay outside the six converter cases |
| UNIX file and registry are excluded from the batch automatic-ready list, but selected shapes pass explicit existing mapping calls | Converter capability readiness limitation | Plan records case-scoped calls; strict checks do not change readiness flags or certify all such source shapes |
| Symlink State with no comment becomes `state-no-comment`; long WMI comments produce truncated labels | Identifier-generation limitation | `tests/focused-regressions/board-pilot/symlink-name-source.xml`; pilot fixes only presentation through a deterministic source-ID plan, not a competing converter |
| Directory-filter comments imply three traversed directories and Windows paths, while UNIX Object selects one directory without recursion | Source content documentation defect | Small selected closure `sources/filter.xml`; actual selectors/values/behaviors preserved and source comments retained |
| Earlier dependency analog declares binary `true` but compares Boolean | Probable source content defect | `tests/focused-regressions/board-pilot/binary-source.xml`; no silent datatype correction or implicit coercion |
| Native local Variable cycle receives no core capability-semantic diagnostic | Semantic-validator defect/gap | `tests/focused-regressions/board-pilot/variable-cycle.assessment.yaml`; independent pilot guard rejects it, shared validator unchanged |

No schema defect or unclear capability rename was established for the six selected
closures. Supported mappings are used exactly, including the specifically reviewed
`wmi57_test` → `windows.wmi.query`; no other suffix normalization is inferred.
Deprecated Tests and ESX/deferred Kubernetes capabilities are absent.

Upstream source questions are separate from native language design. For the binary
case, `true` is not valid hexadecimal binary content; the proposed upstream question
is whether Boolean was intended. For the directory filter, should comments be fixed,
or was recursive selection intended? The conversion follows current executable
content. Neither question grants permission to repair upstream semantics silently.

The six cases passed intermediate source parity, strict validation, independent
synthetic known-result checks and stable-ID checks. These do not prove live collector
or independent scanner equivalence. Record missing-field behavior follows OVAL
5.12.3 `EntityStateFieldType` (missing expected field = error); it is not guessed from
implementation output. A record's fields remain correlated under the current native
specification. The fixed WMI query and scanner-native symlink collection are untested
on live targets.

Questions for human acceptance:

- Are the three complete Definitions and three expressly scoped criterion fragments
  suitable Board examples? Review exact source-to-native crosswalks and both forms.
- Corroborate the source/NG quantifiers: WMI `any` across records versus AND within
  each record; filter Variable `one` versus Object existence `one`; registry Test
  `one` versus existence `some`; symlink negations without States.
- Confirm the typed synthetic observations and independent result rationales,
  including WMI missing/uncollected fields and native duplicate-exclusion variants.
- Review the fixed source-ID naming plan and metadata-only native refinements.
  General automatic naming and broad file/registry converter readiness remain unproven.
- After this review gate, decide the scope of a separate converter task for direct
  Variable Tests, especially the retained concat/complex filter seeds. Do not expand
  this pilot merely because the six selected conversions are green.
- Review the shared local-dataflow diagnostic gap separately, and validate actual
  acquisition behavior on appropriate platform collectors when available.

No new normative requirement or yes/no semantic decision is proposed. No accepted
Board decision record is created by machine validation. All samples remain pending.
