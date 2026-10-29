# Original Registry type and filtered-projection proof expansion

Under [#251](https://github.com/vanderpol/scap-ng/issues/251), the frozen compiled
cohort first pass proves 3,095 of 3,138 original primary Rules. Thirty-five valid,
nondeprecated cases expose bounded omissions in the independent readers. Seven
other originals are invalid and one uses deprecated content; those eight stay
rejected. The immutable all-65 DRAFT is unchanged.

## Existing contracts and concrete sources

- Chrome `SV-221558r960804`, Test `oval:mil.disa.stig.chrome:tst:240001`, has
  `type datatype="string" operation="equals" var_ref="oval:mil.disa.stig.chrome:var:10" var_check="at least one"`.
  The referenced constant contains `reg_dword`. The converter already emits a
  typed `['dword']` comparison with `value_match: one_or_more`; the reader formerly
  accepted only a direct literal. The corrected reader retains the ordered
  constant multiset, duplicate values and independent var_check.
- Windows 2012 DC `SV-226319r794546` has State `ste:458200` in namespace
  `oval:mil.disa.fso.windows`, with `<type>reg_multi_sz</type>`. The approved
  `windows.registry` mapping already declares `reg_multi_sz: multi_string`.
  The independent frozen alias table now reads this equality literal. The value
  predicate and its observed-value cardinalities are unchanged.
- IIS 8.5 Server `SV-214429r879717` projects paths through Registry Object
  `oval:navy.navwar.niwcatlantic.scc.ms.iis.8.5.server:obj:317`, with an ordered
  `include` Filter referencing `ste:312`. Both independent readers now retain
  that leaf Filter at collection scope, including when a Variable projects the
  Object. Existing generic Filter/state readers provide the semantics. The native
  authoring already contains the Filter; neither output nor compiler changes.

The [three compact original closures](../../tests/fixtures/v04-registry-type-proof/provenance.json)
retain all dependency identities from NIWC revision
`8c8e5dff860af6b1290ee9273a282db24278f8d5` and full ZIP/blob pins.
This implements existing approved constant folding, Registry type vocabulary and
Set/Filter behavior. It introduces no new assessment, population, permission,
source-datatype projection or scanner contract. Existing 0.4 rights predicates
are read unchanged; this is not 0.5 Windows permissions development.

Rejected alternatives: collapsing a constant array into scalar/OR loses duplicate
and quantifier semantics; treating multi_string as a scalar changes value
population; dropping the Registry Filter changes the projected directory set.
Unknown types, casts, local/computed type graphs, newly admitted non-equality
operations, malformed Filters and cycles remain fail-closed. No schema/mapping,
converter/compiler, scanner/editor or protected workflow is modified.

## Verification

- **61 focused/affected tests pass**, including eight new original-backed tests.
  The final eight-test rerun also passes. Original closures validate and are
  nondeprecated. All original Test terms compare, validate and compile. Tests
  retain duplicate constants and all four var_check quantifiers. Schema-valid
  type/multiset and Filter removal/action mutations fail independent source and
  compiled-operand comparison; malformed structures and cycles are rejected.
- Fresh selected-Rule acceptance proves all **35** target candidates, with exact
  frozen authoring and program identity. Four Windows 2012 DC, five member-server,
  25 Chrome and one IIS original Rule are covered. No new Rule is inferred merely
  from schema acceptance.
- Recomparison under both corrected readers preserves all **3,095** preceding
  new primary authoring/proof/source-term/native-term hashes. A separate canonical
  authoring audit also retains all 3,095 frozen authoring digests. All **523**
  preceding conformance four-hash records remain unchanged; coverage stays 523/713
  configured Tests (803 original Tests), separate from production Rules.
- Exact integration maintained/six-source CI follows publication. Older green
  CI is not claimed to verify this reader correction. No duplicate suite is
  dispatched, no 65-benchmark archive is regenerated, and no runtime equivalence
  is claimed.

An initial focused run exposed the native reader's corresponding Filter omission;
both independent sides were corrected rather than stripping source Filters.
Source trees are restored after temporary leaf reading, and cycle guards retain
collection/Variable dependency boundaries.

Local evidence is under `/workspace/proof-expansion-20261029/`: `batch-007/`
contains the final 35 accepted original Rules, `registry-retention.json` ties
3,095 retained proofs to both exact reader file hashes, and
`registry-conformance.json` retains the complete pinned conformance probe.

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tools python -m unittest \
  test_v04_registry_type_source_proof test_v04_source_package_semantics \
  test_v04_expanded_source_proof test_v04_direct_enum_variables \
  test_v04_direct_converter -v
```

Pending #255 contracts remain blocked. The residual eight original source
invalidity/deprecation cases are explicit input exclusions, not conversion bugs
silently repaired by this change.
