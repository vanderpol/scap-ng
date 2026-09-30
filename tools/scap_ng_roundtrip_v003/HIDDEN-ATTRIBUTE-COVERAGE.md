# OVAL hidden-attribute conversion coverage (2026-09-30)

This is a working conformance ledger, **not** a claim of full OVAL 5.12.3 equivalence. The pinned schema/XSD documentation and Self-Assertion cases are normative research inputs. Do not infer an OVAL default solely because Python's `dict.get` supplies one.

## Implemented in the v003 research reverse generator and semantic comparator

| OVAL construct | Effective semantics | Generator / comparator behavior | Evidence |
| --- | --- | --- | --- |
| Test `check_existence` | `at_least_one_exists` when omitted | Generator requires native fixture to state a value; comparator normalizes omission | Existing explicit semantics tests |
| State entity `check_existence` | `at_least_one_exists` when omitted | Generator emits supplied value only on a State entity; comparator normalizes omission, distinguishes `none_exist` | `test_explicit_semantics.py` |
| State `entity_check` | `all` when omitted | Generator preserves explicit value; comparator normalizes omission | Regression fixture |
| State `var_check` with `var_ref` | `all` under documented rules; not an XSD `default` | Generator preserves explicit value and rejects a `var_check` without its variable; comparator normalizes omission | Regression fixture |
| Test `state_operator` | `AND` when omitted | Generator preserves supplied value; comparator normalizes omission | Existing comparator |

**Important:** State entity existence is not Test existence. In particular, the two must never share an implementation key or have their attributes conflated. Object selector fields do not accept State `entity_check` or `check_existence`; malformed fixtures fail closed. The structural diff classifier cannot by itself prove semantic fidelity.

## Outstanding work (not yet certified)

1. Resolve all inherited attributes and attribute groups across the **complete** pinned 5.12.3 XSD corpus, including platform-family behavior types.
2. Audit explicit XSD defaults and documentation-only defaults separately, retaining the source file, line, owning type, inheritance path, and conditional applicability.
3. Add negative and positive Self-Assertion cases covering `behaviors`, object/entity state cardinality, variable zero/multiple-value behavior, mask behavior, record-field assertions, filter action, set operator, and error/unknown propagation.
4. Extend the **forward** SCAP 1.4 importer and canonical semantic IR to capture effective values plus whether each was explicit, inherited, or documented implicit; never guess defaults for an unrecognized type.
5. Regenerate a substantial pinned corpus and classify XML changes as (a) presentation-only, (b) proven default materialization, or (c) semantic differences requiring review. Preserve source issues rather than silently fixing them.
6. Run local unit tests, full XSD validation, Schematron and differential tests, and CI; commits alone are not proof of passing validation.

Keep schema defects and ambiguities in a separate upstream-issues ledger rather than relaxing the converter. Native SCAP-NG authored assessments stay free of legacy XML identifiers and serialization residue.
