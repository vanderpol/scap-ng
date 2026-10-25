# Eight-Assessment original-source/package pilot — #251

2026-10-25. Started from synchronized `main` at reviewed checkpoint
`40c1d198d82cf009650e940d812cd799bc5fd9aa`. Authority: [owner-approved pilot](https://github.com/vanderpol/scap-ng/issues/251#issuecomment-6392094407).

**Result: four PROVED, four UNVERIFIABLE/UNSUPPORTED; zero MISMATCH and zero
PROVED_WITH_EXPLICIT_APPROVED_NORMALIZATION.** Exact packaged-graph coverage is
**4/883 = 0.453001%**, with **879/883 still unverified**. This bounded static
converter/compiler proof does not certify the six packages, a scanner, publisher
trust, complete OVAL conformance or whole-Rule policy/applicability semantics.
No production converter/compiler, schema, specification or release gate changed.
No original source, migrated authoring or native package was regenerated or edited.

## Eight fixed selections and outcomes

The eight selections were frozen in `CASES` before comparison. None was replaced
when proof failed. D/T/O/S/V counts include the **complete transitive original
Definition closure**, including extended Definitions, Variables and their
Object/Filter/Set dependencies; counts are per case, not deduplicated corpus totals.

| Case | Platform / packaged Rule | D/T/O/S/V | Outcome | First proof limitation |
| --- | --- | --- | --- | --- |
| 1 | rhel_9 / SV-257889 | 2/2/5/5/2 | UNVERIFIABLE/UNSUPPORTED | source family proof unavailable: {http://oval.mitre.org/XMLSchema/oval-definitions-5#unix}file_test |
| 2 | oracle_linux_9 / SV-271844 | 1/1/1/1/0 | UNVERIFIABLE/UNSUPPORTED | absence carries comparison/attributes; source-specific review required |
| 3 | ms_windows_11 / SV-253254 | 2/1/1/2/0 | PROVED | All reachable source/package terms and compiled operands matched |
| 4 | ms_windows_server_2025 / SV-278001 | 1/5/4/5/3 | PROVED | All reachable source/package terms and compiled operands matched |
| 5 | ms_windows_server_dns / SV-259345 | 1/5/6/5/3 | PROVED | All reachable source/package terms and compiled operands matched |
| 6 | apache_server_2-4_unix_server / SV-214228 | 1/4/9/4/18 | UNVERIFIABLE/UNSUPPORTED | source function proof unavailable: regex_capture |
| 7 | rhel_9 / SV-258179 | 7/24/24/0/17 | UNVERIFIABLE/UNSUPPORTED | source family proof unavailable: {http://oval.mitre.org/XMLSchema/oval-definitions-5#independent}textfilecontent54_test |
| 8 | ms_windows_11 / SV-253260 | 2/6/4/2/0 | PROVED | All reachable source/package terms and compiled operands matched |

All exact Benchmark/Rule/Assessment identities, member and authoring paths,
program and Assessment hashes, original XCCDF check alternatives/catalog routes,
Definition/Test/Object/State/Variable IDs, dependency edges and node hashes are
in [results.json](v04-eight-assessment-pilot/results.json). The result retains
all original checks: default/automated copies resolve to the same OVAL check,
while OCIL/manual alternatives are recorded separately. No distinct OVAL check
or Definition extension was silently dropped. Full original XML member hashes
are in that file. Minimal complete original dependency extractions and exact
packaged Assessment/program snapshots are in
[regression fixtures](../../tests/fixtures/v04-source-package-pilot/).
These are comparison fixtures, not newly converted or standalone XSD-conformant
OVAL documents; their nodes match the original closure fingerprints.

## Independent method and proof limits

`v04_source_package_semantics.py` reads original XML directly; it imports no
converter, exporter, compiler, prior lowering oracle or scanner. A second reader
interprets the exact packaged native graph. Both yield explicit typed semantic
terms for acquisition parameters; dynamic command dependencies and ordered concat;
constant-value arrays; scalar/record comparison datatype and operation; expected
value, field/record and Item quantifiers; State combination; and complete
AND/OR/NOT result structure. Test IDs are bound through that complete result tree,
not title similarity. Referenced shared Objects and Variables are resolved;
missing/cyclic references and unaccounted native declarations block proof.

Only sole-child AND/OR identity wrappers are removed. No two-valued Boolean
simplifications, conditional rewrites or truth-table repairs are applied.
OVAL `int` → native `integer`, registry hive/type spellings and WMI WQL → query
are representational mappings from the existing approved capability contracts.
They do not change the comparison domain. Comparator datatypes are compared
separately from Variable datatypes. OVAL defaults (including omitted var_check
meaning all) come directly from vendored 5.12.3 schemas/documentation, not the
converter's defaults. Unsupported families/functions/attributes fail closed.

Each accepted term is compared with the exact compiled Test operands, source
hashes, opcode and independently reconstructed result program. Every selected
bundle's complete member inventory, CRCs and member hashes is checked, and all
six immutable bundle SHA-256 values match the previous independent acceptance.
The entire 4,012-document authoring graph must equal the union of those pinned
packages. ZIP timestamp differences are allowed only for the reconstruction
container; authoring documents and all native package bytes must match.

The proof is **static preservation of approved collection/comparison/result
contracts**, with unresolved/error/unknown evidence remaining symbolic inputs to
unchanged operators. It is not evaluation of a host or implementation of an
OVAL/NG scanner. Collection error flags, function order and missing dependencies
are retained and tested. Existing source-backed collection/error/unknown and
nonexistent-Item regressions remain mandatory. No assumption of actual complete
collection, successful commands or two-valued evidence was added.

Deliberate negatives change selectors, Item quantifiers, State operators,
Boolean structure, record fields, expected arrays, function order, comparison
datatypes, collection error flags and dependencies. Selector/quantifier mutations
also update program operands and hashes consistently: internal compilation checks
pass while independent original-source comparison rejects the forgery. Separate
negatives reject altered compiled operands/result instructions and source hashes.

Proof limitations are explicit. RHEL file/password Sets/Filters/iteration and
textfilecontent54 behavior/pattern Variables need additional independent proof
rules; this audit does not classify those existing packages as incorrect.
Apache regex_capture/merge/discovery functions are similarly unverified.
Oracle SV-271844 retains the original `stderr_line check_existence="none_exist"
operation="pattern match">.*` counterexample. Its approved **archive migration**
exception is not independently proved original-source equivalence. RHEL's 16
approved all_exist normalizations remain source-pinned and conditional under the
existing contract; this pilot applies **no normalization**, broadens no admission
and does not suppress the original nonexistent-Item counterexample.

## Current coverage overlay

[results-coverage.csv](v04-eight-assessment-pilot/results-coverage.csv) preserves
all 2,433 migration inventory rows and updates exactly the four proved automated
identities with case/Assessment/program proof hashes. All other rows remain
unverified. [results.json](v04-eight-assessment-pilot/results.json) records its
SHA-256, the immutable baseline inventory hash, proof-method hash and exact
883 denominator. The earlier dated package-acceptance ledger remains historical;
this overlay is the current pilot coverage handoff. Standalone source proofs
and archive validity are not counted as exact packaged proof.

| Ownership namespace | Unique automated denominator | Proved exact graphs |
| --- | ---: | ---: |
| RHEL 9 | 57 | 0 |
| Oracle Linux 9 | 41 | 0 |
| Windows 11 | 93 | 2 |
| Windows Server 2025 | 110 | 1 |
| Windows DNS | 21 | 1 |
| Apache 2.4 UNIX | 23 | 0 |
| Shared library | 538 | 0 |
| Total | **883** | **4** |

The six packages contain 561/631/648/559/579/595 automated program instances
(Apache/Windows 11/Server 2025/DNS/Oracle/RHEL), each including the 538 shared
Assessments. Repeated shared-package instances are not extra unique identities
or automatic proof transfer.

## Source pins and reproduction

Original signed NIWC SCAP ZIPs are unchanged at revision
`8c8e5dff860af6b1290ee9273a282db24278f8d5`, `Current/` paths recorded in the
source ledger. Original ZIP SHA-256:

| Platform | SHA-256 |
| --- | --- |
| rhel_9 | `70aa6a16221df2c53b094b11b48b16aca1f6d7147c11123b655659ca7711dbb5` |
| oracle_linux_9 | `6733abd693380b43b2350c2692775e4ff902f895f16899db97b34fecf7fba74d` |
| ms_windows_11 | `e4b8d55b58aa80124bd0974977af4c7f7bde35c748e2940e02857419292d8c3d` |
| ms_windows_server_2025 | `2f46264b5fa21c8a033236121794ebe372314bf7458dac0aca4f81179fe7ece0` |
| ms_windows_server_dns | `f674b67e74acbd3037093d50e33dc20765bd9d45a6c9ed2be5d463d009a6c6b8` |
| apache_server_2-4_unix_server | `8894123788ba415373625eaecdbbd834f190668697803c3319393c11889f1b80` |

Reuse the immutable review archives and exact native bundle hashes documented in
[package acceptance](v04-package-acceptance.md). The maintained archive adapter
can reconstruct missing artifacts; this pilot reused existing pinned artifacts
and did not run conversion/rebaseline across the six STIGs. For an independent
reproduction use the hash-locked Python environment from that report:

```bash
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH=.:tools:tools/scap_upconvert_v003:tools/scap_ng_roundtrip_v003
python tools/audit_v04_eight_assessment_pilot.py \
  --inputs-dir /path/to/original-six-zips --bundles-dir /path/to/pinned-bundles \
  --authoring-json /path/to/current.json.zip --report /tmp/pilot/results.json
python tools/test_v04_source_package_semantics.py
python -m unittest test_scap_converter_core test_v04_native_bundle_compiler \
  test_v04_package_consumer test_v04_public_validator test_v04_source_package_semantics
python tools/run_current_tool_regressions.py --report /tmp/pilot/mandatory.json
```

The mandatory command uses the 23 checksum-pinned source bindings and vendored
OVAL XSD link established exactly as in `rebaseline-smoke.yml`. The pilot command
is deterministic and read-only for inputs. `--fixtures-dir` optionally extracts
all eight original closures/native snapshots for fixture regeneration; it never
invokes the production converter. Full-source acquisition and exact per-file
pins remain available in the original package-acceptance source ledger.

## Validation and publication

Focused converter/compiler/independent-consumer/public-validator/pilot tests:
**52 passed**, including **19 new pilot tests**. Complete mandatory suite:
**2,942 tests in 144.414 s, zero failures/errors, one unchanged optional research
corpus skip**; the reviewed baseline selected 2,923 methods, with zero removed
and nineteen added. Repeated separate-process pilot runs produced byte-identical
results and coverage CSV. Result SHA-256:
`268cbf6185b6217ed262eb5d5b6e49d8a727385de9c8de806183604a6d8ca64c`;
coverage CSV SHA-256:
`b2770e2e04c494c358f670906da96c1904be6272d079daa47a6592ce5b837090`.
Repository preservation passed (34,242 baseline paths);
Markdown sample guards: **4 passed**. Navigation audit retains the same three
pre-existing Board heading links and 39 historical broken links; no new broken
links were added. Hosted CI conclusions follow publication. No tests
were removed, skipped or demoted. No full 883 sweep or six-STIG generation ran.

## Ordered scale-up recommendation — requires pilot review first

1. **Low effort/risk:** review this proof vocabulary, source traces and four
   exact successes; then authorize additional literal registry/shell/WMI graphs
   within this proven structural subset. Retain source/program hashes per case.
2. **Moderate effort/risk:** extend independent typed function proofs for Apache
   regex_capture/merge/unique/discovery and RHEL textfilecontent54 defaults and
   behavior. Add boundary/error/unknown and collection-status counterexamples
   before counting new cases. Do not assume shared converter admission is proof.
3. **Higher effort/risk:** independently prove RHEL file/password Set/Filter/
   for_each boundaries and the exact approved all_exist normalization, retaining
   the original OVAL nonexistent-Item counterexample and conditional status.
4. **Owner review before semantic repair:** decide any proposed elevation of
   Oracle's archive exception to an original-source equivalence claim using the
   exact original counterexample. No new decision is needed merely to leave it
   unverified. Future true divergences must retain minimal source-backed examples
   and stop the affected proof path; do not repair package semantics in the audit.
5. After explicit pilot review, authorize batches with fixed manifests, per-case
   outcomes and unchanged 883 denominator; retain unsupported/unverified records
   until independently proved. Do not start that full audit automatically.

No scanner, signing/trust or release-scope decision was made here. Issue writes
remain blocked by the previously observed `Post "https://api.github.com/graphql":
Forbidden`; this committed report is the #251 handoff without repeated attempts.
