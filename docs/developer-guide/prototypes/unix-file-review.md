# `unix.file` prototype: STOP/GO reviewer sheet

**Reported result: FAIL. STOP expansion. Jack makes the GO decision.**
The artifact is a hand-authored, source-checked prototype; no independent human
review or implementation qualification is claimed. The ratings below are the
author's evidence-based comparison, not an automated score or self-certified pass.

## Baseline and comparison

Baseline is actual pinned OVAL 5.12.3:
[file Object/State](https://github.com/OVAL-Community/OVAL/blob/2f140ee5c5dd1ed9606fcd5afc301f6baeb48706/oval-schemas/unix-definitions-schema.xsd#L134-L462),
[file Item](https://github.com/OVAL-Community/OVAL/blob/2f140ee5c5dd1ed9606fcd5afc301f6baeb48706/oval-schemas/unix-system-characteristics-schema.xsd#L59-L270),
[Item error handling](https://github.com/OVAL-Community/OVAL/blob/2f140ee5c5dd1ed9606fcd5afc301f6baeb48706/oval-schemas/oval-system-characteristics-schema.xsd#L250-L262),
and [collection flags and their evaluation chart](https://github.com/OVAL-Community/OVAL/blob/2f140ee5c5dd1ed9606fcd5afc301f6baeb48706/oval-schemas/oval-system-characteristics-schema.xsd#L275-L327).
The [claim ledger](unix-file-comparison.json) narrows those references to each
selector, field, behavior, status and example, with preserved/changed/unresolved
dispositions. Linux/POSIX references describe OS APIs, not native SCAP-NG policy.

| Criterion | Rating | Evidence and remaining gap |
| --- | --- | --- |
| Technical specificity | better | Guide's field-to-acquisition table names members, all twelve permission masks, direct numeric IDs and proposed timestamp extraction. OVAL supplies field meanings/units but no equally explicit per-field POSIX call/mask map. Native meaning beyond shape is still marked proposed. |
| Implementer utility | equivalent | Guide's collection path can be coded as an experimental Linux adapter without opening OVAL. It cannot yet specify an approved native collector: D-type, D-time, D-permissions and D-errors remain choices. OVAL already has explicit time units and Item/entity error guidance. Additional API detail does not demonstrate superior conforming-implementation utility. |
| Field completeness for the chosen subset | equivalent | All 21 chosen fields have native and OVAL field references. OVAL already explains those fields; native vocabulary/units/permission interpretation are not fully adopted. This is not coverage of all 23 capability fields or dynamic target conditions. |
| Acquisition instructions | better | Numbered parent-descriptor/one-component query, final-link guard, failure-buffer prohibition and race limits make the proposed Linux path concrete. OVAL file_test mentions stat-like metadata but does not provide this bounded acquisition sequence. No wider UNIX or containment guarantee follows. |
| Error semantics | worse | OVAL ItemType distinguishes identification errors from entity errors, and FlagEnumeration includes a Test-result chart. The prototype's errno-to-native examples are unadopted and intentionally cannot supply native propagation rules. Concrete diagnostics do not close that contract gap. |
| Worked examples | better | Three end-to-end Object → declared OS observation → illustrative Collection/Item examples use native names and structurally valid fragments. The compared file XSD sections have entity descriptions/directory examples, not equivalent populated native payloads. These are explanatory fixtures, not execution evidence. |

Ratings are not averaged. Better formatting, API references and examples do not
compensate for a missing contract needed to implement emitted values/statuses.
Overall superiority for a native scanner implementer has therefore **not been
demonstrated**. A favorable technical-specificity rating is not permission to
call the prototype qualified or proceed to another capability.

## Can a developer implement it?

- **Experimental subset: yes**, using the guide's explicitly proposed Linux
  profile and the three declared fixtures. The recipe covers literal equality,
  explicit `filesystem: all`, no traversal and regular files only.
- **Approved native subset/full capability: no.** Jack/native-contract review
  must first resolve emitted type tokens, timestamp units/precision, raw mode
  interpretation and error/status propagation. No implementation or native
  scanner execution was performed to validate those choices.

OVAL still explains more than the prototype covers: size; ACL presence and the
unsupported-ACL source convention; other file types; directory/null selection;
recursion direction/depth/defaults and filesystem restrictions; shared Set/Filter,
entity-check and collection-flag semantics. The ledger identifies these omissions;
they are not silently supplied from OVAL. Link-target selection, mount/namespace
boundaries, partial observations and race/retry behavior also remain unresolved.

## Review disposition

Recommend stopping this documentation approach/expansion at this prototype.
Keep the existing research unchanged. Review [the guide](unix-file-scanner.md),
[examples](unix-file-examples.json) and unresolved choices in the ledger before
any new work. This submission neither approves a native policy nor claims that
schema-valid examples are correct scanner results.

Acceptance checks are source-pointer/hash and schema-fragment checks, including
negative missing-Item/error-diagnostic cases. They cannot establish the rubric's
GO decision. After publication and CI reporting, work **stops** pending Jack's
explicit review under [#35](https://github.com/vanderpol/scap-ng/issues/35).
