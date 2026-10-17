# Proposal: native Items represent existing resources, never invented missing Items

**Research-only proposal — Issue #235 (authoring grammar), Issue #229 (existence/results); no 0.4 normative change or scanner implementation.**
**17 October 2026.**

## Decision candidate

For native SCAP-NG acquisition, prohibit creating an Item with root `status: does_not_exist` merely because some portion of an Object selector can be resolved. A returned Item MUST correspond to a *genuinely observed existing resource at the capability's declared Item identity level*. This is not a ban on detecting absence.

- Missing selected resource: report the collection's absence/complete result or a failed explicitly expected identity, **not** a phantom Item.
- Existing selected resource with missing key, field, text match, etc.: report an **existing Item**, with absent nested property/field data when the capability's identity permits.
- Existing resource whose data cannot be read: keep error/unknown/incomplete information; do not transform access denial into absence.
- Requested resources in explicit arrays: preserve one expected-identity obligation per resource if the *requirement* says each must exist; do not infer that from `match all observed Items`.
- Source-import OVAL `item status='does not exist'`: retain source/provenance; fail closed until the importer can prove equivalent native absence/expected-identity/field evidence. Do **not** silently discard conflicting imported evidence.
- This requires coordinated changes to collected-Item **result contracts and scanner acquisition**, not only authoring keywords. Current 0.4 result schemas still allow root Item `does_not_exist`; this page records a change candidate.

## Why upstream OVAL 5.12.3 provides precedent

1. **Windows ntuser** Object behaviors `item_creation=every_ntuser` create a real Item for each applicable `ntuser.dat` even if the sought key/name does not exist. `key_and_name_exist` instead creates Items only for matching keys/names. The relevant `ntuser.dat` is the existing resource, and the missing setting is a field-level matter.
2. **Independent textfilecontent54** `item_creation=filepath_exists` creates Items for existing matching filepaths even if the requested pattern does not appear. `all_object_elements_fullfilled` creates Items only when filepath, pattern and instance requirements are met. XML has an analogous behavior.
3. OVAL Core System Characteristics says partial `does not exist` Items may optionally be emitted for debugging a partly satisfied Object; their optionality creates the `all_exist` versus `at_least_one_exists` uncertainty we want to avoid natively.

Upstream documentation:
- https://oval-community-guidelines.readthedocs.io/en/latest/oval-schema-documentation/windows-definitions-schema.html#ntuserbehaviors
- https://oval-community-guidelines.readthedocs.io/en/latest/oval-schema-documentation/independent-definitions-schema.html
- https://oval-community-guidelines.readthedocs.io/en/latest/oval-schema-documentation/oval-system-characteristics-schema.html

## Author-facing concepts — not adopted YAML syntax

**Question 1: Which resource is selected?** `inspect` and `where` identify the existing resource population, or `collect`/a typed nested reference does so.

**Question 2: How many collected Items must exist and match?** The compact `require.items` choice governs the collected Item population; `require.condition` contains the comparison. Do not require authors to understand `Item.status` or collector diagnostics to write basic checks.

**Question 3: Is every *specified expected identity* mandatory?** An explicit fixed list of seven audit-tool paths is *not* the same as all collected tools having UID 0. A separate typed expected-population requirement is needed if missing any named path is a violation. This is a distinct authoring intent; do not overload Test `all_exist` or introduce a hidden default.

### Four truth-preserving outcomes

| Scenario | Native intended observation | Requirement evaluation |
| --- | --- | --- |
| Selected resource absent, acquisition complete | Zero Items; collection absence/complete evidence | Required existence false; optional existence allowed; forbidden existence true |
| Existing `ntuser.dat` lacks requested value | An existing `ntuser` Item; property missing | Requirement for each relevant user's key/value fails, **not** a pass because no matched Item was created |
| Explicitly expected seven files, only six found | Six real Items plus one failed expected-identity obligation | `every expected path` fails; `all found Items match` may pass; do not conflate |
| Resource or field unreadable; collection incomplete | Error/unknown/incomplete and any real observed Items | Never reported as definite absence or automatic pass |

### Example: human intent distinguishes two audit tool requirements

> Every audit tool *found* must be owned by root, with at least one tool present.

This is different from:

> Each of these seven *named* audit tools must exist and be owned by root.

The source six-STIG `unix.file` audit-tool Object uses seven literal path alternatives with `value_match: one_or_more` and a Test `all_exist`. Native wording must not secretly upgrade that inherited source meaning into seven separate mandatory checks.

## Does removal of phantom Items eliminate Test `all_exist`?

**Not automatically.** The generic OVAL 5.12.3 existence truth table distinguishes `all_exist` from `at_least_one_exists` in at least three conditions:

| Item/status population | `at_least_one_exists` | `all_exist` |
| --- | --- | --- |
| One confirmed existing Item, no failures | true | true |
| One existing + one phantom `does_not_exist` | true | false |
| One existing + one `error` | true | error |
| One existing + one `not_collected` | true | unknown |

Banning *only* phantom `does_not_exist` Items resolves the second row, **not the third or fourth**. Native acquisition could instead represent a known existing Item with field-level error and an unresolved collection with collection-level status, but that broader restriction requires a separate design and conformance review.

Also, an incomplete Object population may produce different Test decisions depending on `check` and whether any partial observation is decisive; this requires independent result tests.

**Provisional direction:** For new, fully observed native Items, `items: at_least_one` may subsume the ordinary Test `all_exist` case; retain an importer-only legacy distinction and any proven stronger semantics until error, incomplete and multi-value/Set/record cases are validated. Never collapse **State-field** `all_exist`, where a different scope is involved.

## Attribution and inherited SCAP 1.3 source — correction

The project owner confirmed that NIWC enhanced SCAP 1.4 packages import DISA SCAP 1.3 content without changes to DISA-authored checks. NIWC-authored additions are identified by their own OVAL namespace. The original `oval:mil.disa.stig...` versus `oval:navy.navwar.niwcatlantic...` Definition/Test/Object/State/Variable IDs have been [verified from original OVAL evidence](OVAL-SOURCE-PROVENANCE-BOUNDARY.md) and checked by [CI](https://github.com/vanderpol/scap-ng/actions/runs/39029699446).

Therefore **the 132 textfilecontent54 and three ntuser legacy `item_creation` values in the mixed 201-Test census must not be interpreted as authors intentionally avoiding the new OVAL 5.12.3 options**. NIWC's modern additions must be analyzed separately from unchanged inherited DISA content, using original source OVAL element IDs rather than native Assessment filenames. The curated six-STIG native ZIP does not retain all ID attribution evidence. This source-origin split remains a research gate before publishing author-behavior statistics.

## Source-backed results of the 201-Test follow-up (17 October 2026)

The pinned [201-Test existing-Item result-model audit](reports/all-exist-native-equivalence.md) passed in [GitHub Actions](https://github.com/vanderpol/scap-ng/actions/runs/39029016539):

| Distinct Test category | Count | What was proved |
| --- | ---: | --- |
| State-free Test `all_exist` | **127** | Under the research profile where **all returned root Items have status `exists`**, the local generic reference also agrees with `at_least_one_exists` for incomplete collection flags, as well as complete |
| State-bearing `all_exist` | **74** | Equivalent on complete real-Item-only collections; **not** necessarily equivalent on incomplete collections because the at-least-one form may return decisive false while the generic all-exist form remains unknown |
| Total | **201** | All equivalent on complete real-Item-only population; **not** unconditional OVAL migration equivalence |

The reference tested 3,132 bounded results combinations, with 206 observed differences all confined to incomplete, State-bearing cases in that restricted population. Root Item statuses `error` and `not_collected`, currently valid in existing results schemas, are separately relevant: a mixed existing/error population can still distinguish the two OVAL existence options. **Merely banning fabricated missing Items is insufficient** to prove every inherited result equal.

The [source `item_creation` census](reports/all-exist-item-creation.md) found all **132** `independent.textfilecontent54` Tests among the 201 use `all_object_elements_fullfilled`, and all **3** `windows.ntuser` Tests use `key_and_name_exist`. None use `filepath_exists` or `every_ntuser` respectively. These are **matching-dependent collection modes, not necessarily phantom Item creation**: they may emit no Item when a property does not match. Converting an Object to file/hive-level Items is a change to the Item population and must preserve original tests and evidence under a proven mapping.

An [experimental JSON Schema profile](native-existing-item.profile.schema.json), plus [validation cases](https://github.com/vanderpol/scap-ng/blob/main/tools/test_research_04_native_existing_item_profile.py), [passed in CI](https://github.com/vanderpol/scap-ng/actions/runs/39029351309). It demonstrates the **stronger** possible invariant: for *new native results*, an Item has a confirmed identity and root `status: exists`; missing fields retain their own `does_not_exist`/error/not-collected statuses, while missing/failed/incomplete collections retain collection-level status. That profile is **separate research**, not an approved replacement for the existing 0.4 Item/report contracts, which currently allow other root statuses.

This suggests an eventual single author-facing existence choice `at_least_one` for ordinary collected Item presence, **but no source Test is normalized automatically**. The importer must retain or explicitly lower the 74 legacy incomplete-State cases and all mixed-status meaning, and must separately represent each mandatory *expected identity* where policy requires all named resources to exist.

### What a prohibition must actually say

- **Forbidden:** invented absent root Item solely because an Object partially matched or a requested field was not found.
- **Required for new native Items:** the capability states its real Item identity, and the collector confirms that resource exists before reporting it as an Item.
- **Allowed and necessary:** missing property on a real Item; collection-level absence; error/incomplete/not-collected evidence; redaction without fabricating absence.
- **Not automatically forbidden:** legacy `item_creation` choices that simply restrict selection to fully matching existing resources. These are not themselves fictitious Items. Their correct native lowering still needs proof.
- **Not inferred:** all explicitly specified file names must exist. That remains a separate author requirement from all returned Items matching a State.

## Verification gate before a 0.4 normative decision

1. Confirm a capability-level identity for every Item type; `ntuser.dat` and text-file path semantics must be explicit.
2. Adjust the Item schema to prohibit root `does_not_exist` for native acquisitions, but preserve field/record absence and appropriate collection status.
3. Define an import transform for OVAL phantom Items with identity, partial evidence and six-result checks; report incompatible cases explicitly.
4. Differential-check *all 201 source Test `all_exist` occurrences*, including all observed capability/selection variants and original OVAL XML.
5. Independently test absence, multiple observed resources, multi-valued expected identities, incomplete/error/not-collected, item-versus-field scope, and union/difference.
6. Prove the results contract and one readable authoring grammar. Use blind security-auditor interpretation tests before selecting any key spelling.

**No conversion, source STIG, schema, compiler, or scanner behavior is changed by this proposal.**
