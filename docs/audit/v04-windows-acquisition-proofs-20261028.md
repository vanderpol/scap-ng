# Independent Windows acquisition proofs

Continuation of [#251](https://github.com/vanderpol/scap-ng/issues/251) from
`8a3665b5717b028344142ee0d5447cd79ca0dbde`, whose nine workflows passed,
including 3,214 maintained tests (zero failures/errors, one existing skip).
This increment changes converter-specific independent proof readers and tests.
It changes no converter rendering, schema, mapping, generator, compiler,
scanner, editor, original source payload or 0.3 file.

## Original-source obligations

Eight source-valid original Tests already converted and compiled, but the
independent reader could not describe their acquisition:

| Original source | Tests | Preserved acquisition |
| --- | --- | --- |
| `win-def_appcmdlistconfig_test.xml` | 7 | Webserver configuration uses an explicitly nil identifier. |
| `win-def_fileeffectiverights53_test.xml` | 1244 | A nil filename selects the directory target alongside its trustee SID. |
| `win-def_ntuser_test.xml` | 1, 13 | Nil name retains the key acquisition rather than selecting an empty/default value name. |
| `win-def_ntuser_test.xml` | 7, 8 | Downward traversal retains depth 1 and unbounded depth respectively. |
| `win-def_ntuser_test.xml` | 26, 28 | `every_ntuser` retains collection population even when the selected key/name is missing. |

The [original fixtures](../../tests/fixtures/v04-windows-acquisition-proof/provenance.json)
are three byte-exact files from the existing pinned Self-Assertion revision.
Their eight **previously compiled program hashes are frozen in provenance**;
every program remains unchanged while its independent proof obligation is
now discharged. These are newly proved cases, not newly implemented collectors.

The [independent helper](../../tools/v04_windows_acquisition_source_proof.py)
accepts nil only at known acquisition positions, preserves its distinction
from an empty string or omitted selector, and reads NTUSER defaults and Item
creation choices directly from the original OVAL XSD. Traversal retains its
own hierarchy boundary. The native decoder checks Boolean parameter types and
retains actual Item creation and traversal values rather than assuming defaults.

The approved native mapping deliberately omits deprecated `windows_view`.
No such authoring field is added here. Explicit deprecated views, upward
recursion, unknown attributes, inappropriate nil positions and unsupported
constructs remain outside this proof extension. The original defaults are
pinned as source facts; this does not establish host scanner behavior.

## Verification and scope

Thirty-three focused regressions pass, including original XSD/Schematron and
nondeprecation, exact dependency/source hashes, native authoring validation,
compilation/operand retention, independent terms, nil/empty/missing distinctions,
changed collection population/depth and invalid native Boolean types. Existing
file-rights, interim acquisition, Set/Filter and expanded source-proof tests pass.

The full corpus now has **521/710 configured Tests converted, compiled and
independently term-proved**; **519/803 original Tests** additionally have valid,
nondeprecated closures. All preceding **513 proof identities and source/native
term hashes** remain unchanged. **All 521 previously compiled program hashes**
remain unchanged. There are zero mismatches or unexplained differences.
The eight new source identities and hashes are individually listed in the
[receipt](v04-windows-acquisition-proofs-20261028.json).

All six primary sources retain **1,012/1,396 OVAL Rule proofs** and every
previous program hash; no new primary Rule is admitted. Capability activation
remains **47/51** in scope and **47/100** globally. Exact published SHA and
mandatory hosted results are recorded in [issue #251](https://github.com/vanderpol/scap-ng/issues/251).

Remaining source-invalid examples are not repaired: original Schematron forbids
State references on `none_exist` Tests and requires Variable/entity datatypes to
agree. Those cases remain separately classified as invalid original source.
Schema acceptance, compilation and these typed-term proofs do not establish
scanner execution, full policy/applicability, publisher trust or release equivalence.

The [remaining contract handoff](v04-converter-remaining-contract-handoff-20261028.md)
pins the next source-backed authority question; no additional function syntax
is inferred from permissive schema/compile acceptance.
