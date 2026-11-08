# Documentation production receipt

The unix.file-only rendering path is replaced for production documentation by
one schema-discovering renderer. All **104 capability families** now have
proposed schema-owned field descriptions and generated references. Historical
PRs #39/#41/#44 and their artifacts are preserved. This work is stacked on
PR #44 at `b1bdefa6bc07f5e78db7951be92cef9e8414d1df`.

[Reference and platform indexes](reference/README.md) ·
[Regenerate and maintain](../proposed-schema/README.md) ·
[Exact command receipt](evidence/documentation-production/shared-expansion-checks.json) ·
[Coverage](reference/coverage.json) · [Gaps](reference/gaps.jsonl) ·
[Duplicate-text inventory](reference/duplicate-descriptions.json).

## Actual coverage

| Measure | Result |
| --- | ---: |
| Capability families processed / reference pages | 104 / 104 |
| Complete draft field-description coverage | 102 capabilities |
| Partial draft field-description coverage | 2 capabilities |
| Documented capability field routes | 1,858 / 1,866 (99.57%) |
| Unique description owners used by capability routes | 794 |
| Shared/core named schema nodes documented | 2,872 / 3,020 (95.10%) |
| Basic shared-reference nodes documented | 1,378 / 1,449 (95.10%) |
| Remaining shared-node description gaps | 148 |
| Basic / advanced / platform reference pages | 139 / 139 / 15 |
| Generated files, including help and ledgers | 300 |
| Earlier editorial acceptances preserved exactly | 46 |
| Earlier semantic holds / withheld foreach | 9 / 1 |

Routes count Object, Item and Require contexts, including reused meanings.
They are not distinct prose owners or independent scanner contracts. Core totals
include named definitions and repeated conditional constraints; the separate
basic-reference count avoids presenting internal constraint annotations as
complete author-facing documentation. The annotation-only owner library is
excluded from these coverage denominators.

**No capability is declared fully runtime-qualified by this exercise.** The 104
unresolved-contract records mean full collection/evaluation behavior has not
been independently qualified here, not that this work discovered 104 defects.
New source-derived sentences are draft proposals; prior editorial approval is
identified separately. The 148 remaining shared gaps stay visible rather than
being filled with field-name boilerplate. When no safe wording is established,
the ledger explicitly withholds a proposal instead of inventing behavior.

## Ten-capability qualification

The same generic renderer and checks cover this diverse set and all 104
capabilities. A field-text pass does not remove semantic holds.

| Capability | Documented routes | Held/unresolved field routes |
| --- | ---: | ---: |
| independent.shellcommand | 21/21 | 0 |
| independent.textfilecontent | 28/28 | 0 |
| linux.partition | 24/24 | 0 |
| linux.rpminfo | 22/22 | 0 |
| linux.systemdunitproperty | 11/11 | 0 |
| unix.file | 56/56 | 0 |
| windows.file | 48/48 | 0 |
| windows.registry | 22/22 | 2 |
| windows.service | 28/28 | 0 |
| windows.wmi.query | 10/10 | 0 |

Checks cover mapped and native inline fields, nested traversal, explicit shared
owners, schema references, metadata associations, distinct Require alternatives,
field occurrences versus array bounds, and inappropriate legacy terminology.
The tests also add a new capability/result field without changing renderer code.

## Source and integration review

Descriptions live in `proposed-schema/documentation/*.schema.json` and its
capability schemas. The renderer reads neither OVAL XSDs, mapping JSON nor
editorial worksheets to obtain prose. It discovers role/schema relationships,
then emits compact tables, advanced constraints and exact-context help.
Item and Require refer to one field-meaning definition. Shared operators and
reference markers use explicit links to shared description owners.

The native 0.4.0 validation trees are preserved, with proposed resource IDs in a
nonrelease namespace. Passive documentation links add no datatype restriction,
required parameter, new capability implementation or scanner default. Mapping
datatype and parameter declarations are labeled separately from assertions.
The original JSON Schema types, enums, defaults and structural alternatives
remain authoritative. Defaults are never presented as scanner fallbacks.

Field provenance pins OVAL Community 5.12.3 at
`2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, with file hashes and exact
source-field XPath pointers. The four retained experimental ESX capabilities
correctly identify their separate 6.0 new-Test source at
`5afcf590fb5d334687bfdc47f98716424cdb7f3d`; they are not relabeled as
5.12.3 or promoted to supported implementations. Source notices are preserved
in [third-party notices](THIRD-PARTY.md).

The review corrected examples of unsafe literal copying: WUA `is_hidden` and
`is_installed` legacy descriptions called them URLs; RPM capability/group
verification descriptions contained copy/paste mistakes; the configured SELinux
policy description referred to the currently loaded policy. Collection
parameters describe acquisition controls, and collected audit-policy/right
fields describe evidence rather than instructing scanners to change the system.

Identical text at 141 groups of distinct pointers is reported for review.
Identical wording alone does not establish identical semantics across capability
contexts. Existing approvals are preserved; shared Item/Require meanings and
shared grammar explanations already resolve to one owner.

## Gaps and decisions

- **Shellcommand:** collection metadata declares required parameters that the
  generic frozen Object grammar does not require or type-check. Positive syntax
  witnesses preserve this acceptance, including deliberately malformed parameter
  types; these are boundary tests, not recommended authoring examples. Execution,
  stdout/stderr splitting, empty output and unavailable interpreters are not
  silently specified.
- **Registry:** mappings describe hierarchy traversal, while the frozen Registry
  inline Object rejects `traversal`. The reference marks the parent and nested
  children as held. Views, inaccessible keys, value conversion and collection
  errors remain unproved.
- **UNIX File:** preserve the reviewed permission-bit meanings. Links/targets,
  filesystem boundaries, timestamp units, ACL interpretation and inaccessible
  entries remain separate contract questions.
- **Four missing field meanings / eight routes:** NTUSER
  `days_since_last_logon`, and Registry effective-rights `key_wow64_64key`,
  `key_wow64_32key`, `key_wow64_res`. Item and Require reuse these four owners.
  Exact pointers and bounded draft wording are in the gap ledger.

For NTUSER, alternatives include preserving legacy profile-load-time age and
active-session normalization, or specifying a native logon-event age. These
are different observations. Recommend an explicit native observation contract
before claiming either. For WOW64 flags, raw view-selection/access-mask flags
and granted effective rights are different concepts. Recommend deciding their
native representation explicitly and retaining the current unresolved status
until then. No change is implemented here.

Next safe documentation work should prioritize the public core/reporting fields
in the pointer ledger and review legacy-derived proposals, while semantic
owners resolve the nine existing holds. Do not expand the debt list to hide new
undocumented fields. Issue #42 paired examples remain the next phase; existing
schema example pointers remain available for a generic extension.

## Continued shared-language expansion

After the first tested publication, 427 additional named shared-schema nodes
received descriptions or explicit links to their description owners. This
covers Rule/Benchmark authoring, Organizational Inputs, manual procedures,
result identities, evidence locators, invocation traces, and manifest metadata.
Corresponding manual-result and Item-report fields reuse existing owners.

The remaining 148 gaps are scoped in the machine ledger: **48 inactive migration
nodes**, **27 nodes in a helper unreferenced by the Assessment schema**, and
**73 declared-schema nodes** involving held or insufficiently specified contracts.
The older helper's unreviewed OVAL-backend wording was removed from the proposed
schema and replaced by its verified structural scope. The frozen original is
unchanged. Help metadata carries context scope, with a regression test keeping
inactive/unreferenced help distinct from retained native concat syntax.

[Read the concrete decision packet](DOCUMENTATION-CONTRACT-DECISIONS.md) for
remaining completeness/counting, materialization, trace, package entry-point/size,
and capability-field questions. Recommendations are engineering proposals only.
The [first 106-test receipt](evidence/documentation-production/checks.json) remains
unchanged and bound to its earlier manifest; the current receipt is separate.

## Verification

The [machine receipt](evidence/documentation-production/shared-expansion-checks.json) records the
exact commands, return codes, package versions, code hashes, manifest hash and
output aggregate. **107 tests passed** using Python 3.12 with the exact
`requirements-dev.txt` dependencies: jsonschema 4.24.0, referencing 0.36.2,
PyYAML 6.0.3. The seven existing/new generation checks and `git diff --check`
passed. No alternate test runner was substituted.

All 35 proposed core assertion trees equal their frozen counterparts after URI
renaming and removal of verified passive documentation annotations. **170 syntax
witnesses** retain their expected results before and after: 115 accepted and 55
rejected. Two independent generation processes using hash seeds 1 and 99 produce
**byte-identical outputs for all 300 generated files**.

An intermediate full run failed two new output/manifest checks after output was
regenerated during that run. Subsequent stable-tree default and pinned runs
passed; the final receipt is from the pinned environment after regeneration.
Remote CI is reported on the PR for its actual head, not inferred from this
local receipt.

No scanner-runtime equivalence, live editor-host verification or release
readiness is claimed. No production schema pin, compiler behavior, frozen file,
Editor PR #36, release work or mandatory Benchmark transfer is changed. No editor
is installed. CI adds a read-only documentation check and no artifact uploads.
