# NTUSER empty-State recovery

Continuation of [converter #251](https://github.com/vanderpol/scap-ng/issues/251)
from published `7acdf6d6f0995be1f310a69491fa81f6d7916767`.
[Machine-readable receipt](v04-ntuser-empty-state-recovery-20261029.json).

The recorded `/workspace/recovery-20261028/ntuser-candidate/` did not survive
this restart. This reconstructs the bounded correction from the pinned originals;
it does not claim recovery of that patch. Recovery files are now under
`/workspace/recovery-20261029/`.

## Original evidence and existing contract

NIWC revision `8c8e5dff860af6b1290ee9273a282db24278f8d5` contains Windows 10
`SV-220955r991589` and Server 2016 `SV-225069r991589`. Their original constant
Variables `oval:navy.navwar.niwcatlantic.scc.windows:var:22095502` and
`oval:navy.navwar.niwcatlantic.scc.windows:var:22506902` each contain one empty
string. The corresponding `ste:22095503` / `ste:22506903` compare NTUSER
`type` with `operation="equals"` and `var_check="at least one"`.

Both Objects preserve ordered exclusions: first disabled accounts, then the
empty type comparison. The remaining Test compares `value` to string `2`,
with original `check_existence="any_exist"` and `check="all"`.

The existing 0.4 NTUSER mapping explicitly includes the empty State lexical
value and documents `legacy_empty_registry_type_state`. The converter previously
rejected it because the Registry value crosswalk lists only real Registry types.
The correction admits the empty identity alias only for this annotated NTUSER
State type domain. No source, schema or mapping is changed. The independent
source reader separately reads the original typed constant operand rather than
consulting converter metadata.

Before: `unsupported enum comparison/value`.
After (second Object filter):

```yaml
exclude:
  type:
    equals: ['']
    datatype: string
    value_match: one_or_more
    values_found: one_or_more
    values_matching: every
```

This retains a comparison operand; it does not introduce a collected Item type,
replace the comparison with absence/status, drop the filter, reorder filters,
or claim that an empty string is an uncollected entity. Such rewrites would
change source semantics and are explicitly rejected by mutation tests.
The authority is the already committed mapping and standing #251 converter
scope, reiterated by the owner's 2026-10-29 resumption instruction; no new
normative decision is inferred.

## Verification

- 38 focused/affected tests pass, zero failures/errors/skips, including six new
  tests covering both original closures, literal/duplicate constant forms,
  all four Variable quantifiers, metadata/domain guards, casts/unknown values,
  comparator rejection and native operand/filter/order/quantifier mutations.
- Both extracted original closures pass original XSD/Schematron/semantic checks
  and are nondeprecated. The compact [fixtures](../../tests/fixtures/v04-ntuser-empty-state/provenance.json)
  preserve every original dependency node identity from the complete pinned ZIPs.
- Both complete original SCAP Rules pass the production acceptance path:
  original validity, native schema, independent typed terms, compiled operands,
  bundle and independent package consumer. Only these two Rules were selected
  from the two additional sources; no all-65 regeneration took place.
- The six-source gate passes with the same 1,072 primary proofs, 324 blocked
  automated and 171 manual/OCIL-only Rules. All 1,072 program hashes match the
  immutable verified evidence at `248895772`; the preceding enum checkpoint
  independently retained that same floor. The checked-in 1,055 floor also passes.
- All 523 preceding configured conformance Tests retain their authoring,
  source-term, native-term and program hashes. Coverage remains 523/713
  configured Tests (803 original Tests), with zero new conformance proofs.
- The maintained suite ran **3,279 tests: 3,278 passed, zero failures/errors,
  one existing skip**, in 1507.413 seconds on this local candidate. The
  receipt records the tested code/fixture/mapping hashes and skip identity.
  All nine exact-commit workflows at `f141efb07603e72a3982ffda87489da8f0d5c74f`
  subsequently passed. [Hosted maintained suite 40863822537](https://github.com/vanderpol/scap-ng/actions/runs/40863822537):
  3,279 run / 3,278 passed, zero failures/errors, one skip, 1,139.313 seconds;
  job 123413419074, artifact 12893188443. [Hosted six-source gate 40863826463](https://github.com/vanderpol/scap-ng/actions/runs/40863826463)
  retains all 1,072 proofs; job 123413430092, artifact 12892323743.
- Documentation audit reports no new broken links; an optional strict run
  reports three existing Board-discussion heading links and 39 historical
  links. The affected pages/targets are unchanged from the published base.
  The workflow itself reports these links without a strict failure gate.
- No scanner runtime equivalence or complete migration is claimed.

The extracted fixtures retain original component whitespace; only their pinned
XML tails produce whitespace-only `git diff --check` diagnostics. Other changed
paths pass that check.

An initial new assertion incorrectly expected `values_found: every`; the
source XSD defaults `check_existence` to `at_least_one_exists`. The assertion
was corrected to `one_or_more`, preserving existing converter behavior. The
final 38-test run passes; no production change was made to satisfy that assertion.

Reproduction:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tools python -m unittest \
  test_v04_ntuser_empty_state test_v04_direct_enum_variables \
  test_v04_direct_identity_enum_selectors test_v04_windows_acquisition_source_proof \
  test_v04_direct_registry_hive test_v04_converter_contracts \
  test_v04_native_schema_generation -v
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tools python tools/verify_v04_direct_scope.py \
  --inputs PINNED_SIX_ZIP_DIRECTORY --output NEW_EVIDENCE_DIRECTORY
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tools python tools/audit_v04_oval_test_corpus.py \
  --source-root PINNED_OVAL_TEST_CONTENT --output NEW_CONFORMANCE_REPORT.json
```

## Remaining boundaries

The published all-65 ledger was analyzed in place, without rerunning conversions.
Other primary guard classes remain: 30 multiple aggregation components, ten
ordered noninteger comparisons, eight nil cmdlet input datatype cases, two
acquisition comparison/type cases, and four Solaris attribute cases. These are
ledger counts, not source-valid unlock claims. Windows 10 `SV-220698` confirms
an untyped nil `parameters` input and typed nil `module_version`; this does not
authorize changing the record/default or module-version acquisition contract.
Float, functions, aggregation/population and import/export remain under their
existing decisions/#255. Unknown or invalid originals remain fail-closed.
