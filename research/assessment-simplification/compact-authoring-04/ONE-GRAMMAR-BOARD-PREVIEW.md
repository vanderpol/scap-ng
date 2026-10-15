# SCAP-NG 0.4: one authoring language — proposed, not adopted

**Decision proposed:** Replace indirect State `field:/value:/operation:` wrappers with **actual field names and comparator verbs**, and replace `existence:/match:` with **one documented, human-readable `require:` vocabulary**. Do not add a second dialect or implicit defaults. Authoring would compile to fully explicit NG, retaining the original semantics.

## Examples from real STIGs (excerpts)

**RHEL 9 /home must be mounted nosuid (SV-257851)**

```yaml
states:
  - mount_options:
      equals: nosuid
      require: at_least_one_exists_and_some_match
require: at_least_one_exists_and_all_match
```

**Only one entry may exist, and it must match**

```yaml
require: only_one_exists_and_matches
```

A Test with **no State** says `require: only_one_exists`. The two meanings must not be conflated.

**Windows 11 record (SV-253264, Antivirus)**

```yaml
states:
  - value:
      record:
        require: at_least_one_exists_and_some_match
        fields:
          productstate:
            bitwise_and: 4096
            require: at_least_one_exists_and_all_match
```

Both record and record-field requirement scopes are preserved.

## Measured first pass on full authoring content

| Published 0.3 benchmark | Automated-by-default Rules represented in one proposed grammar | Verified Assessment files |
| --- | ---: | ---: |
| RHEL 9 | **417 / 417** | 423 |
| Windows 11 | **245 / 245** | 251 |
| Server 2025 | **259 / 259** | 268 |
| **Total** | **921 / 921** | **942** |

**930/942** Assessment files reproduced the *exact original parsed 0.3 source*. The remaining **12** contained State-free Tests whose original `match` choice is never consulted in the pinned OVAL reference result model. Normalizing that inert setting has model-level proof but **not live scanner parity**, so this distinction is explicit in the report. [Complete compiler proof](https://github.com/vanderpol/scap-ng/actions/runs/38737558392).

**Complex features were not bypassed.** The strict single-grammar CI also converted **154** Object Set filter entries (RHEL9 62, Win11 43, Server2025 49) to `include:/exclude:` actions over field-name predicates. Windows WMI/cmdlet collectors have **59** separate `selection_match:` properties (31 Win11, 28 Server2025) without a corresponding existence field; these are **not** incorrectly turned into `require`. All round-tripped source-exactly. `value_match:` for static arrays remains a third independent cardinality domain.

**No new shell-command or manual fallback was needed** for the syntax experiment. Existing shell-command content remains intact. Original Rules, manual alternatives, applicability, and static Object arrays continue to be supported.

## Critical evidence about the outliers

The [OVAL six-valued truth-table test](https://github.com/vanderpol/scap-ng/actions/runs/38734873333) proves that:
- `only_one_exists` **cannot** be replaced by `only_one_matches` (two collected Items, one passes).
- `none_exist` **cannot** be replaced by `none_match` (a present Item may fail a comparison).
- `none_match` is aggregate-equivalent to `all_match` on a **truly complemented predicate** over nonempty results, but there is **no automatic safe inverse of regex, WMI and all native operators**, and error/unknown must remain intact.
- Missing fields in Windows record comparisons may yield **error**; flattening records would not be equivalent.
- One RHEL 9 source Test combines `none_exist` with a State. The proposed grammar **preserves the State and exact source semantics**; whether the State is removable remains a separate vendor-evaluator research question.

## What needs a standards decision

The proof shows **representation is feasible**. It does *not* show the first set of natural-language labels is optimal. The prototype covers all 20 possible original `existence × match` pairs with one `require` enum, including rare cases, but a 20-phrase glossary is not automatically easy to learn. The Board should pick a concise, truthful naming scheme and a single *complete* JSON Schema, with autocomplete and strict rejection of illegal combinations.

**Recommendation:** Standardize **one grammar**, not two; retain native typed checks for unusual/negative cases instead of making them manual/shell. Approve the language only after schema validation, full 65-source conversion, and scanner differential tests for zero/error/unknown/incomplete outcomes.

[Full vocabulary/design research](HUMAN-VERBIAGE-PROPOSAL.md) · [Tracking issue #227](https://github.com/vanderpol/scap-ng/issues/227)
