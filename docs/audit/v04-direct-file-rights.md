# Direct Windows file-effective-rights proof — 2026-10-26

Continued under [#251](https://github.com/vanderpol/scap-ng/issues/251#issuecomment-6401652271)
after the [text-file checkpoint](v04-direct-textfile.md). No approved schema,
production converter/compiler, source fixture or release gate changed.

| Field | Verified result |
| --- | --- |
| BASE_SHA | `95ce4e72103a3c164ee8f3c35e39de4e7ce98d58` |
| RESULT_SHA | `6d7fdc0390282802258835157659094f6bace3ca` |
| IMPLEMENTED | Generic effective-rights acquisition, typed permission requirements and independent complete-closure proof |
| SOURCE_PROVED / COMPILED_UNPROVED / BLOCKED | **228 / 0 / 63** of 291 original Rules |
| CANDIDATES | All **eight** actual file-rights closures independently prove and compile |
| AUTHORING | 228 Assessments / 324 Tests; 200 inline Test Objects, 39 references to 15 genuinely shared Objects, 85 no-Object Tests, 127 compact Registry Object sites; deprecated grammar zero |
| TESTS / CI | 3,057 maintained tests, zero failures/errors, one existing skip; 62 related tests and 20 final publication checks pass; all five implementation-head hosted workflows PASS |
| NEXT | Original-source shell-command stderr/exit-status collection behavior; ten candidate closures |

**Source semantics.** The producer enables the versioned capability and reuses
generic Test, Object, Variable, Set and Filter visitors. File-backed leaf
acquisitions materialize original filesystem scope `all`, including full paths;
Sets retain scope on each operand. Both full-path/SID and directory/name/SID
forms retain their exact selectors and comparisons. Original omitted group
behavior includes the selected group SID without expanding members
(`include_group=true`, `resolve_group=false`), matching the approved native
direct-SID contract. Explicit expansion/view/traversal behavior and nilled
selectors remain outside this bounded implementation and fail closed.

The independent reader derives original fields/types and SID-selection defaults
from original OVAL XSD without importing producer mappings. Permission Booleans
require explicit original `datatype="boolean"`; omission and wrong types are
rejected, never inferred. False permission values remain comparisons against
existing fields, not field absence. Source Variable matching, Item existence,
AND/OR structure, default-exclude SID Filters and collection boundaries survive.

Five focused tests cover all eight real closures, public validation, exact
compilation and YAML/JSON equality; original SID defaults and dependencies;
permission/SID/Filter/Variable/scope/existence mutations; invalid source types,
fields and expansion behavior; and a controlled two-path relative complement
with ordered Filters on each operand. Swapping complement operands fails proof.
Controlled derivatives add no original Rule coverage. No access checks or group
membership evaluation were implemented or executed.

Public gates validate **458 JSON / 458 YAML documents**, compile 228 programs and
pass the separate package consumer. All **220** previous program hashes are
unchanged. The [machine packet](v04-direct-file-rights.json) records every new
original Rule/Definition/dependency, proof, compiled hash, exact command and
remaining blocker. Source ZIP/XML SHA-256 remain
`2f46264b5fa21c8a033236121794ebe372314bf7458dac0aca4f81179fe7ece0` /
`52b7918ea577095cb1c130589e5061c52ef4b12370ebb4ce84d2dfba68757440`.

Run `PYTHONPATH=tools python tools/test_v04_direct_file_rights.py -v`; see the
[developer guide](../developer/DIRECT-V04-CONVERTER.md) for extension contracts.
No `all_exist` normalization, schema redesign, scanner parity, signing/trust,
six-STIG rebaseline or production-release readiness is claimed.

Issue commenting remains blocked by the previous exact error
`Post "https://api.github.com/graphql": Forbidden`; no repeated retry was made.
The committed report and engineering ledger are the GitHub handoff.

The final publication helper selects distinct actual Assessments and omits an
ordinary category when the supported examples are all complex. Its correction
followed the full local suite; 20 final focused checks pass. It changes sample
selection only, not admission, authoring data or compiled programs.

[Actual pinned Set/Filter/Variable YAML examples](../examples/direct-file-rights/README.md),
published in `97a151f08`, retain original source identities and hashes in their
manifest. Exact implementation CI: [Current-design regression contracts](https://github.com/vanderpol/scap-ng/actions/runs/40313648725), [Markdown navigation and duplication audit](https://github.com/vanderpol/scap-ng/actions/runs/40313648752), [Commit issue reference](https://github.com/vanderpol/scap-ng/actions/runs/40313648754), [0.4.0 canonical authoring fast checks](https://github.com/vanderpol/scap-ng/actions/runs/40313648716), [Rebaseline smoke regression](https://github.com/vanderpol/scap-ng/actions/runs/40313648776).
