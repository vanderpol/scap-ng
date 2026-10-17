# Is check-level Item existence too complicated?

**SCAP-NG 0.4 research — 17 October 2026. Not a syntax decision.**

The project owner raised the key question: why does an Assessment Test need `all_exist` or `any_exist` when most checks seem to require **at least one Item** or **no Items**? Why should a "no Items" check carry a State comparison? This review tests that instinct against the pinned [six-STIG census](reports/english-first-04-existence-audit.json) and the vendored **OVAL 5.12.3** definitions, common and results schemas. It separates **Test Item existence**, **per-Item State matching**, and **State field/entity existence**; mixing them is a major source of confusion.

## Grounded population: all 1,375 named Tests from 872 native Assessments

| Source Test existence policy | Source Tests | State-bearing | State-free | Auditor interpretation |
| --- | ---: | ---: | ---: | --- |
| `at_least_one_exists` | **993** | 837 | 156 | Find at least one selected Item |
| `all_exist` | **201** | 74 | 127 | The unclear one; see schema contradiction below |
| `none_exist` | **103** | **1 invalid/contradictory** | **102** | Find no Items |
| `any_exist` | **71** | 71 | 0 | Item may be absent; if present, State constraints apply |
| `only_one_exists` | **7** | 5 | 2 | Find exactly one Item |
| **Total** | **1,375** | **987** | **388** | Source definitions, not independent scanner execution evidence |

**Important distinction:** the [current auditor-first translator](AUDITOR-FIRST-CANDIDATE.md) reconstructs **871/872 Assessments and 1,374/1,375 Tests**. The final Test above is a known `none_exist` with attached State anomaly, not counted as a successful translation. These mode counts derive from all raw Test definitions in the same pinned source; duplicated logic across STIGs can affect how often a mode appears.

## Keep three different questions separate

1. **Does anything exist?** Source selector/Object → collected Items → `check_existence`. The compliance requirement might need zero, one or more, exactly one, or allow missing Items.
2. **Do the found Items match?** Only relevant for a State-bearing Test. For example, every selected mount must have `nosuid`. At least one found Item does **not** imply every Item matches.
3. **Does a field/value exist within each found Item?** The `mount_options`, `stdout_line`, `stderr_line`, registry `value`, and WMI record fields have their **own** existence/matching rules. A Test can have an existing shell-command Item while `stderr_line` is required to be absent; requiring zero **Items** would be wrong.

A separate corpus scan counted **42 explicit State-field `none_exist` declarations**, in addition to 20 optional-all-match field declarations and 106 Test-level inherited `state_fields_require=at_least_one_exists_and_all_match` declarations. These are **not** Test-level Item existence requirements; the field census counts explicit nested `require` occurrences in source State trees rather than unique Tests.

### 1. None exist: the owner's instinct is correct

A Test that prohibits a file/service/setting need only select the prohibited data and require **no selected Items**:

```yaml
# illustrative requirement only; object selector remains required elsewhere
require:
  items: none
```

It must **not** carry an `every_item` or other Item State predicate. The vendored [OVAL 5.12.3 definitions schema](https://github.com/vanderpol/scap-ng/blob/main/third_party/scap-1.4-schemas/oval_5.12.3/oval-definitions-schema.xsd) contains a Schematron rule forbidding a State reference in a `check_existence="none_exist"` Test. One converted Linux bootloader Test violates this pattern. Investigate its original OVAL XML and conversion provenance; do **not** silently drop its State or invent semantics.

The 102 ordinary State-free `none_exist` Tests include real **Windows SNMP service absence (SV-253276)** and **removal of .p12/.pfx files (SV-253280)**.

### 2. At least one exists: the common case

For the real RHEL `/home` mount test, keep **at least one selected partition**, and **every** selected partition must include a matching `nosuid` option:

```yaml
check: /home is mounted with the nosuid option.
inspect: linux.partition
where:
  mount_point:
    matches_regex: '.*\\/home'
require:
  items: at_least_one
  every_item:
    mount_options:
      at_least_one_value_is: nosuid
```

The source selector and Test Item requirement are separate. **Zero selected partitions must not pass**. The actual source regex is retained (it may match more than the literal `/home`).

For `at_least_one_item_matches` the [current reversible candidate](auditor-candidate/windows-wmi-rights.auditor.research.yaml) can state the combined requirement using that phrase, which explicitly requires a matching Item to exist.

### 3. Exactly one exists: unusual, but not redundant

Seven real Tests require `only_one_exists`. For example, Windows 11 **SV-253296** checks the Windows time service through PowerShell, and an RHEL-shared sudoers Test checks for a single configured timeout entry. If two selected Items are observed, `at_least_one` can pass whereas `exactly_one` must fail.

```yaml
# illustrative requirement only; collection and State retained in full source
require:
  items: exactly_one
  every_item:
    ...: ...
```

This should probably be a **rare, explicit authoring feature**, not a frequent mandatory declaration. The details matter for compliance checks requiring exactly one occurrence or configuration entry.

### 4. May be absent: optional configuration is real

All **71** native `any_exist` Tests have States. Examples include Windows 11 **SV-253377**: *if DevicePKInitEnabled exists, it is set to 1*; and **SV-253289**: *Secondary Logon is disabled or the service is uninstalled*. This is semantically different from requiring the Item to exist.

```yaml
# illustrative requirement only
require:
  items: may_be_absent
  every_item:
    value:
      is: 1
```

A future author might prefer `if_present` spelling. **Don't yet collapse this into `at_least_one` or simply delete it:** absence may be an allowed outcome, while any present values must still be evaluated. The pinned *generic reference* has an unresolved empty-State-aggregation corner when there are **zero** observed Items and the Test still has a State. A definitive `if_present` lowering requires test-level OVAL semantic and incomplete/error proof.

### 5. All exist: there is a genuine documentation tension

The **OVAL 5.12.3 `ExistenceEnumeration` prose** says `all_exist` at the *Test* level is equivalent to `at_least_one_exists`, because non-existent Items do not affect evaluation. This is **not** the same as the State-field scope: field `all_exist` checks whether every corresponding entity is present.

However, the **generic ExistenceEnumeration truth table** in that very same [common schema](https://github.com/vanderpol/scap-ng/blob/main/third_party/scap-1.4-schemas/oval_5.12.3/oval-common-schema.xsd) yields different outcomes if a collected Object has mixed Item status values. Our generic [OVAL reference model](https://github.com/vanderpol/scap-ng/blob/main/tools/oval_result_truth_tables.py) follows those general tables.

| Collected Item statuses | Test `at_least_one_exists` | Generic table `all_exist` |
| --- | --- | --- |
| Nothing found | False | False |
| One Item exists | True | True |
| Two Items exist | True | True |
| One exists; one is marked *does not exist* | **True** | **False** |
| One exists; one is marked *error* | **True** | **Error** |
| One exists; one is marked *not collected* | **True** | **Unknown** |

That is a real **source interpretation dispute**, not just a naming preference. A SCAP-NG implementation cannot silently normalize all 201 source Tests until we determine which semantics should apply to OVAL *Test* evaluation, rather than merely State entity existence. The 201 uses include 127 State-free Tests and 74 State-bearing Tests. Of these, **132** use `independent.textfilecontent54`, including ordinary file-content collection patterns. An example from Windows 11 **SV-253259** is "BitLocker must be enabled on all fixed drives": importantly, **the `every_item` matcher** imposes uniform compliance; the word "all" in `all_exist` alone does not show how many fixed drives the system should have.

**Candidate decision:** Remove `all_must_exist` from the *preferred auditor vocabulary only after a focused 201-Test equivalence audit resolves this disagreement*. Until then, keep source-exact import and explicit semantic distinctions fail-closed. Do not add another synonym merely to conceal uncertainty.

## Candidate user-facing simplification, conditional on proof

Most content authors should encounter **two ordinary existence choices** and a few targeted exceptions, rather than five equally prominent choices:

- **Required Items:** `items: at_least_one` plus `every_item` / `at_least_one_item_matches` / other explicit matching scope. No hidden default for empty populations.
- **Forbidden Items:** `items: none`, with **no State** at the Test level.
- **Exceptions when justified:** `items: exactly_one`, and `items: may_be_absent` with an explicit condition when present. `all_must_exist` remains **under investigation**, not a recommended word for ordinary content.

A shorthand like `at_least_one_item_matches: ...` is safe **only when its documented lowering includes existence of a matching Item**. We should not infer that plain `every_item` implies a nonempty set unless that semantics is explicitly adopted and checked. The preferred grammar should be **one syntax**; any normalizations must be semantically justified before removal of legacy attributes, not delegated to a second “pretty” language.

### Next proof gates

1. Trace the original OVAL XML and source versions for representative `all_exist` Test paths; clarify whether generic mixed-status Item states can actually occur in this Test scope. Run the results-schema six-state checks on complete, incomplete and error collections.
2. Verify *zero Items plus State* semantics for optional `any_exist`, including all-match, some-match and none-match; no vacuous pass without evidence.
3. Check that the seven `only_one_exists` Tests are genuinely requiring unique Items (not only unique matching State values). Keep the distinction between “one Item exists” and “one Item matches.”
4. Keep State **field** existence and record/variable quantifiers separate from Test Item existence.
5. On representative source-backed examples, ask an unfamiliar security auditor to explain the expected result for zero, one good, one bad, two good, mixed statuses and collection error, without reading OVAL vocabulary.

**Evidence:** [Full machine-readable census](reports/english-first-04-existence-audit.json) · [OVAL 5.12.3 source definitions](https://github.com/vanderpol/scap-ng/blob/main/third_party/scap-1.4-schemas/oval_5.12.3/oval-common-schema.xsd) · [Provenance issue #229](https://github.com/vanderpol/scap-ng/issues/229).
