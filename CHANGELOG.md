# Changelog

This file summarizes material SCAP-NG changes by release. Each entry links to
the GitHub issue that explains the work. Research-only, deferred, and rejected
proposals are not listed as delivered features.

## 0.4.0 — Unreleased

- **2026-10-28:** Added bounded YAML acquisition and record conversion using
  the existing mapping, with byte-pinned OpenSCAP sources: 45/51 original Tests
  convert, compile and match independently decoded typed semantic terms.
  Preserve native YAML key identity and report six unsupported closures without
  inventing function or record-member projection syntax. This is converter
  coverage, not scanner-runtime equivalence
  ([#251](https://github.com/vanderpol/scap-ng/issues/251)).

- **2026-10-28:** Added a read-only original Variable-function contract and
  transitive dependency audit, including XSD/Schematron facts and source-valid
  examples masked by earlier conversion blockers. No new function syntax is
  enabled ([#251](https://github.com/vanderpol/scap-ng/issues/251),
  [#255](https://github.com/vanderpol/scap-ng/issues/255)).

- **2026-10-28:** Independently prove eight previously compiled Windows
  acquisition cases: nil selectors, NTUSER traversal and Item creation.
  All 521 compiled corpus programs remain unchanged; source-valid/nondeprecated
  proof coverage reaches 519/803 original Tests. This adds proof coverage,
  not scanner implementation ([#251](https://github.com/vanderpol/scap-ng/issues/251)).

- **2026-10-28:** Preserve closed enum Variable graphs through typed,
  consumer-specific translations without changing their shared generic string
  uses. Original registry Test 4000 now proves; all previous 512 corpus proofs
  and program hashes remain unchanged. Make dependency inventory stack safe
  while preserving source ordering and cycle diagnostics
  ([#251](https://github.com/vanderpol/scap-ng/issues/251)).

- **2026-10-28:** Extended shared direct conversion with approved typed
  version/EVR, binary and address comparisons plus integer bitwise operations.
  Original-source corpus term proofs increase from 406 to 512; all prior
  identities remain, with one explained function datatype-label correction.
  Two additional Windows 11 Rules pass the six-source primary gate
  ([#251](https://github.com/vanderpol/scap-ng/issues/251)).

- **2026-10-27:** Integrated the revised `file.hash` algorithm selector into
  direct conversion, including static lists, complement quantifiers and typed
  named projection Variables. Emit explicit datatypes for array/Variable
  predicates; retain all 39 Server 2025 user-rights Rules and individually
  document expected program-hash corrections. Preserve singleton acquisition
  inputs without introducing command/query array expansion. Scanner execution
  and arbitrary runtime enum normalization remain separate obligations
  ([#251](https://github.com/vanderpol/scap-ng/issues/251),
  [#255](https://github.com/vanderpol/scap-ng/issues/255)).

- **2026-10-27:** Updated the pre-alpha `file.hash` capability mapping to
  represent OVAL multi-algorithm Object selection through the existing typed
  selector/value-match grammar, with Object/State enum crosswalks and pinned
  positive/negative schema tests. Audited all 100 capability mappings against
  accepted 0.3/0.4 modernizations. At that schema-only checkpoint, `filehash58` converter admission
  and scanner semantics were unimplemented; explicit-array datatype enforcement
  awaited coordinated converter support
  ([#255](https://github.com/vanderpol/scap-ng/issues/255)).

- Extended direct conversion to seven ordinary capabilities and fixed unknown,
  preserving distinct logical and field/record controls, original source
  validity and all prior proof/program hashes
  ([#251](https://github.com/vanderpol/scap-ng/issues/251)).

- Corrected generated Object selector alternatives to remain mutually exclusive
  under `oneOf`, preserving Set restrictions; reviewed all 100 contracts and
  proved all eight original process Tests without dropping selectors
  ([#251](https://github.com/vanderpol/scap-ng/issues/251)).

- Added a verified mode to the existing direct conversion CLI, sharing original
  closure validity/proof/compilation gates with the six-source regression and
  packaging only independently proved primary subsets. Added shared file
  traversal, scalar behavior routing and RPM proof boundaries
  ([#251](https://github.com/vanderpol/scap-ng/issues/251)).

- Added shared direct Variable sources, named constant function collections and
  single-collection merge/unique conversion; inventory and independent proof
  now follow text Variable references without discarding unsupported predicates
  ([#251](https://github.com/vanderpol/scap-ng/issues/251)).

- Extended the existing direct converter to ten ordinary capability mappings
  using activation and independent proof data, with ten pinned original files
  and source/schema/compiler boundary regressions
  ([#251](https://github.com/vanderpol/scap-ng/issues/251)).

- Enabled five metadata-driven direct-converter capabilities and independent
  scalar proof contracts; measured all six original primary-source subsets with
  816 proved/compiled closures while preserving all 249 Server 2025 program hashes
  and explicit source/applicability blockers
  ([#251](https://github.com/vanderpol/scap-ng/issues/251)).

- Inventoried all original six-STIG Rule and applicability dependencies against
  pinned OVAL XSD/Schematron, separating source-invalid bindings from unsupported
  conversion and preserving non-repairing candidate evidence
  ([#251](https://github.com/vanderpol/scap-ng/issues/251)).

- Added a fast, hash-pinned inventory and direct-converter coverage audit of the
  complete SCAP 1.4 OVAL Test Content collection, preserving unsupported platforms
  and distinguishing conversion, validation, compilation and independent proof
  ([#251](https://github.com/vanderpol/scap-ng/issues/251)).

- Separated immutable Bluetooth archival reproduction from current original-SCAP
  acceptance; restored current grammar in five source-proof workflows while
  retaining their independent source assertions. Fixed deterministic indexing of
  record fields across typed-source serialization
  ([#251](https://github.com/vanderpol/scap-ng/issues/251)).

- **2026-10-25:** Enforced the reviewed flat Object contract in public validation
  and compiler preflight across Tests, shared Objects, Sets and nested Variable
  acquisitions. Historical migration now flattens nested Objects reversibly;
  current invalid authoring fails closed. Corrected explicit Registry hive
  equality in the source-backed adapter
  ([#251](https://github.com/vanderpol/scap-ng/issues/251)).

- **2026-10-25:** Expanded independent Linux/Apache proof rules and attempted a
  fixed 24-identity Windows batch. Exact proof coverage advances from 4/883 to
  24/883, including one explicitly conditional RHEL normalization proof;
  unsupported sources remain unverified ([#251](https://github.com/vanderpol/scap-ng/issues/251)).

- **2026-10-25:** Added an independent eight-Assessment original-source/package
  comparison pilot, source-pinned regression fixtures and proof-only coverage
  overlay. Four exact graphs proved; four remain unverified. This does not
  certify scanner execution or all 883 automated Assessments ([#251](https://github.com/vanderpol/scap-ng/issues/251)).

### Canonical authoring cleanup

- **2026-10-24:** Added a source-pinned, reversible six-STIG review-archive
  bridge to the current 0.4 `require` grammar. The owner approved removing
  the redundant `.*` comparator from the one Oracle Linux 9 SV-271844
  `stderr_line` absence requirement; original published OVAL bytes, identities,
  operand and rationale remain in a separate provenance report. All 4,012
  YAML and JSON documents pass current schemas, with negative source-mutation
  guards. This is not a fresh original-SCAP import, signed release, or scanner
  equivalence claim. [#233](https://github.com/vanderpol/scap-ng/issues/233)
  [#251](https://github.com/vanderpol/scap-ng/issues/251)

- **2026-10-24:** Integrated the owner-approved Test-level OVAL `all_exist` to
  `items_found: one_or_more` normalization under the versioned actual-Items
  collection contract. Admission is pinned to the proven RHEL 9 audit-syscall
  source; original source attributes/identities/hashes and explicit reason/scope
  remain in provenance. Mixed nonexistent-Item OVAL counterexamples remain
  different; error/incomplete/uncollected evidence is not treated as complete
  success. Field/record semantics are unchanged. Historical research now runs
  separately against its exact pinned toolchain with actual red diagnostics;
  current production/source/schema/compiler regressions remain mandatory.
  [#251](https://github.com/vanderpol/scap-ng/issues/251)

- Integrated the reviewed comparator-free field and record absence forms:
  `values_found: none` and `record: {records_found: none}`. Source-verified DNS
  and Gatekeeper absence now survives promotion and compilation without a
  fabricated empty-string comparison or matching count. Present empty values
  remain comparisons; nonempty ambiguous predicates reject. Added original-source
  and controlled-record XSD/inverse regressions, preserving error/uncollected
  distinctions and the separate unresolved Item-level population boundary.
  [#251](https://github.com/vanderpol/scap-ng/issues/251)
  [#248](https://github.com/vanderpol/scap-ng/issues/248)

- Repaired maintained capability-generator and Apache preview regression
  fixtures for the approved structured requirement/count vocabulary. Generated
  contracts now resolve version-local references correctly and enforce the
  uniform Test requirement for fixed-result capabilities. Explicit preview
  validation flattens historical Object wrappers before strict promotion,
  checking both inverses. Historical research and the source-backed Gatekeeper
  absence boundary remain visible in the full gate; no schema or scanner
  semantics changed.
  [#251](https://github.com/vanderpol/scap-ng/issues/251)
  [#248](https://github.com/vanderpol/scap-ng/issues/248)

- The direct registry converter now preserves multiple literal scalar OVAL
  States as structured Test `require.and/or`, retaining each State's complete
  field condition and the original Test/field operators. Original-source
  attestation rejects unsupported dynamic operands and quantifiers. Added a
  pinned Enterprise/EnterpriseS production-CLI, YAML and compiled-JSON regression;
  no schema change or scanner-parity claim.
  [#251](https://github.com/vanderpol/scap-ng/issues/251)
  [#248](https://github.com/vanderpol/scap-ng/issues/248)

- Integrated the existing 0.4 converter/upgrader, typed source IR and native
  compiler with explicit Item, field and record counts in the approved `require`
  grammar. Preserve complete logical alternatives, source ledgers, Sets/Filters,
  Variables and Object sharing; reject obsolete authored State forms and invalid
  quantifiers. Added three pinned Linux/Windows end-to-end cases and focused CI.
  Source OVAL `all_exist` population semantics remain separately audited; no
  scanner equivalence or 0.4.0 completion is claimed.
  [#251](https://github.com/vanderpol/scap-ng/issues/251)
  [#248](https://github.com/vanderpol/scap-ng/issues/248)

- Repaired CI fixture wiring for pinned AppArmor, environmentvariable58 and
  uname source tests. The condition-fields preview now reuses source-inverse
  restoration of the 11 missing Applicability dependencies in its strict typed
  compilation view, preserving all 4,001 raw documents and field-scope ledgers.
  [#248](https://github.com/vanderpol/scap-ng/issues/248)
  [#239](https://github.com/vanderpol/scap-ng/issues/239)
  [#232](https://github.com/vanderpol/scap-ng/issues/232)

- Repaired historical six-STIG preview validation/compilation by explicitly
  projecting legacy structured conditions and Object wrappers through the
  canonical generator. The pinned Apache `stdout_line` condition and named
  shell Object examples now validate under the active schema; original
  archives and source-inverse ledgers remain unchanged. Known missing shared
  Applicability dependencies are restored only in the compilation view from
  the immutable 0.3 source. Validators and graph closure stay strict.
  [#248](https://github.com/vanderpol/scap-ng/issues/248)
  [#239](https://github.com/vanderpol/scap-ng/issues/239)

- Canonical six-STIG generation now emits `evaluate.and/or/xor`, using the
  existing reversible migration while retaining legacy input compatibility.
  Private inline/local Objects omit null `object_title`, including nested Set
  operands; meaningful titles and named/shared Object contracts are preserved.
  The authoring guard rejects both obsolete output forms, with focused
  positive/negative tests and updated display vocabulary.
  [#248](https://github.com/vanderpol/scap-ng/issues/248)
  [#239](https://github.com/vanderpol/scap-ng/issues/239)

### Source-verified converter coverage

- Extended the shared mature 0.3-to-0.4 converter for the pinned original Linux
  `independent.environmentvariable58` Definition 354 and `unix.uname` Definition
  932. Preserve nil/integer selectors, comparisons, quantifiers, flat AND
  criteria, and the uname singleton/six-field State; reject unproved source or
  lowering changes. Focused differential, schema, bundle-integrity and coverage
  audit tests do not assert scanner execution parity.
  [#248](https://github.com/vanderpol/scap-ng/issues/248)
  [#232](https://github.com/vanderpol/scap-ng/issues/232)

### Developer toolchain release infrastructure

- Added a bounded Python 3.12 clean-extract smoke gate for the HEAD 0.4.0
  source toolchain. It verifies the ZIP/checksums, converts one pinned original
  OVAL family Definition using extracted tools, compiles and verifies its
  schema-valid Benchmark graph, and runs the extracted public CLI smoke test.
  Evidence is retained as CI artifacts; no release or scanner claim is made.
  [#232](https://github.com/vanderpol/scap-ng/issues/232)
  [#27](https://github.com/vanderpol/scap-ng/issues/27)

- Added explicit historical version-tag source reconstruction for older 0.3
  snapshots that predate the 0.4 developer-guide layout; source archives stay
  version-accurate and do not silently mix new scripts with old schemas.
  [#27](https://github.com/vanderpol/scap-ng/issues/27)

- Added an integrity-checked, deterministic source-toolchain archive builder,
  a read-only standalone verifier and focused tamper/missing-doc regression
  tests. A manual GitHub workflow can checkpoint the complete committed source,
  including the normative specification, schemas, developer guides, tooling
  and tests. This is a **candidate source snapshot** only; it is not an
  approved 0.4 release or scanner-conformance claim.
  [#27](https://github.com/vanderpol/scap-ng/issues/27)
  [#49](https://github.com/vanderpol/scap-ng/issues/49)
  [#232](https://github.com/vanderpol/scap-ng/issues/232)

### Native content compilation

- Extended the shared 0.3-derived converter with source-pinned AppArmor
  singleton integer-State support. The empty original Object remains implicit;
  Test existence/check and `loaded_profiles_count >= 0` remain source-exact.
  Source and lowering graph mutations fail closed. Focused schema/compiler
  tests compare against the independent original-OVAL oracle and graph.
  [#232](https://github.com/vanderpol/scap-ng/issues/232)
  [#248](https://github.com/vanderpol/scap-ng/issues/248)

- Added native bundle regression coverage for schema-valid manual Assessment
  alternatives: both independent authoring formats preserve the manual
  procedure/response and Rule choice without inventing an automated Test
  program. Incomplete manual responses fail native schema validation.
  [#232](https://github.com/vanderpol/scap-ng/issues/232)
- Extended the pinned real RHEL 9 OVAL-to-0.4 converter regression through
  schema-checked native `.scapng` construction and independent verification,
  including program/Test inventories and explicit non-scanner status. This
  closes a test gap between the version upgrader, typed authoring IR, and
  bundle compiler, without claiming semantic scanner parity.
  [#232](https://github.com/vanderpol/scap-ng/issues/232)
- Added a manual six-STIG release gate that compiles canonical YAML and JSON
  independently and rejects any difference in the resulting native `.scapng`
  bytes or their previously published immutable release hashes. It is not a
  routine push check, scanner conformance test, or new content release.
  [#232](https://github.com/vanderpol/scap-ng/issues/232)
- Added independently verifiable YAML-only and JSON-only native 0.4 authoring
  compilation, with a paired mode that compares independently compiled
  `.scapng` bytes. Invalid source, ambiguous references and incompatible
  version declarations fail closed. This is content compilation, not scanner
  execution. [#232](https://github.com/vanderpol/scap-ng/issues/232)
- Restored `.scapng` compilation for the native 0.4.0 authoring model,
  extending the earlier manifest-authoritative compiler architecture. Every
  automated Assessment now carries a separately compiled Test dispatch and
  six-state result-expression program, with canonical member hashes and
  independent program/source verification. Native source-exact Test shapes
  are preserved rather than guessed into simplified checks. The maintained
  three-STIG fast gate compiles RHEL 9, Windows 11 and Apache 2.4 UNIX;
  a deliberate six-STIG checkpoint reuses immutable JSON/YAML source inputs
  without rerunning their expensive original OVAL conversion. These are
  **content compilation** results, not live collector/scanner conformance or
  publisher signing evidence. [#232](https://github.com/vanderpol/scap-ng/issues/232)
  [#229](https://github.com/vanderpol/scap-ng/issues/229)
- Added optional detached-CMS signing and **externally anchored** verification
  for already-compiled native 0.4 `.scapng` bundles. Verification checks the
  signer, detached signature, manifest, exact compiled Test/Result programs,
  hashes and entire logical graph; no embedded certificate is implicitly
  trusted. Published six-STIG preview bundles remain unsigned until a real
  publisher signing identity and trust policy are supplied. This proves
  package authenticity only, not live scanner correctness.
  [#232](https://github.com/vanderpol/scap-ng/issues/232)

### Canonical authoring checkpoint

- Added a documented, read-only public CLI for inspecting the released six-STIG
  authoring set before human review. It verifies strict JSON/YAML inventory
  parity and reference closure, reports per-STIG counts and source-preserving
  review leads, and can pin the 4,012-document six-STIG baseline. Updated the
  review download page to point to the current compiled and authoring releases
  instead of the superseded October 20 source-only counts. Neither the tool
  nor its tests assert scanner or OVAL semantic equivalence.
  [#232](https://github.com/vanderpol/scap-ng/issues/232)
- Kept four superseded 0.4-A r3 research workflows available for explicit
  historical diagnostics but removed their automatic push triggers; their
  frozen source archive predates the 11 shared Applicability Assessment
  restorations. Active 0.4 tools remain covered by canonical fast checks.
  [#232](https://github.com/vanderpol/scap-ng/issues/232)
- Published source-invertible, native-schema-validated 0.4.0 JSON/YAML
  authoring for six STIGs (4,012 documents, 1,390 automated Tests), after
  restoring 11 omitted shared applicability Assessments from immutable 0.3
  source. Both formats, six deterministic source-only package manifests,
  original-OVAL requirement axes, and isolated CMS test signatures passed
  the full checkpoint. This historical source-only release predates the
  distinct native compiled-bundle checkpoint; scanner parity remains open.
  [#232](https://github.com/vanderpol/scap-ng/issues/232)
  [#251](https://github.com/vanderpol/scap-ng/issues/251)
- Split rapid 0.4 development regressions from deliberately triggered full
  six-STIG release builds. The routine integration sample validates pinned
  RHEL 9, Windows 11 and Apache 2.4 UNIX source packages without rerunning
  the complete YAML/JSON conversion for every edit.
  [#232](https://github.com/vanderpol/scap-ng/issues/232)

### Converter and authoring safeguards

- Reused previously audited 0.4 Boolean, string and integer OVAL datatype
  importers as independent lockstep oracles for the mature 0.3-backed core.
  Three pinned original Self-Assertion Definitions spanning **38 OVAL Tests**
  retain source literal lexemes, nested AND/NOT, typed State comparisons and
  per-Test quantifiers. Immutable source checksum and deliberately corrupted
  0.3 semantic graphs fail closed; other datatype suites remain outside the
  admitted source subset.
  [#232](https://github.com/vanderpol/scap-ng/issues/232)
  [#248](https://github.com/vanderpol/scap-ng/issues/248)

- Added a reproducible public native compiler CLI smoke gate using one
  schema-valid Benchmark/Rule/Assessment source package and independently
  serialized JSON/YAML authoring archives. Both CLI paths produce byte-for-byte
  identical verified `.scapng` bundles. The separate OVAL-to-Assessment
  converter still requires a Benchmark/Rule packaging handoff; no one-command
  raw OVAL-to-bundle workflow is claimed.
  [#232](https://github.com/vanderpol/scap-ng/issues/232)

- Extended source-attested empty singleton OVAL Object conversion to no-State
  presence-only Tests, reusing the single maintained 0.3-backed projector.
  Three pinned real macOS checks (FileVault, firmware password, profiles)
  receive explicit original-object migration crosswalks; original-source,
  existence-quantifier, missing-crosswalk and 0.3-drift regressions fail closed.
  [#232](https://github.com/vanderpol/scap-ng/issues/232)
  [#248](https://github.com/vanderpol/scap-ng/issues/248)

- Extended the established single-Test source-attested scalar-State adapter
  across flat multi-Test AND criteria without a parallel importer. Each
  original OVAL Test/Object/State pair is checked independently, including
  source-order and complete 0.3 reference closure, then compiled together.
  Immutable IOS and IOS XE line sources, negative Boolean/source mutations,
  and a deliberately corrupted 0.3 State are regression-checked. Multi-field
  States, shared Objects and scanner parity remain outside this proof.
  [#232](https://github.com/vanderpol/scap-ng/issues/232)
  [#248](https://github.com/vanderpol/scap-ng/issues/248)

- Incorporated two previously independent integer constant-Variable OVAL
  sources into the single maintained 0.3-backed converter: 2-Test literal
  matrices and 10-Test `var_check` enumeration/negated-criteria matrices.
  The executable 0.4 output is derived from the mature 0.3 graph, independently
  compared with immutable original OVAL imports, schema-checked and compiled;
  altered OVAL hashes, value literals or 0.3 `var_check` mappings fail closed.
  No generalized Variable or scanner-parity claim is implied.
  [#232](https://github.com/vanderpol/scap-ng/issues/232)
  [#248](https://github.com/vanderpol/scap-ng/issues/248)

- Added a source-attested multi-Test AND bridge to the single 0.4 converter.
  Two or more direct no-State OVAL Tests retain their separate native Test
  programs, ordered Boolean conjunction and source-exact Object selectors.
  Pinned IOS global content, a synthetic two-Test graph and mutations cover
  preservation and fail-closed OR/negation/State/shared-Object boundaries.
  [#232](https://github.com/vanderpol/scap-ng/issues/232)
  [#248](https://github.com/vanderpol/scap-ng/issues/248)

- Added source-attested singleton capability conversion to the maintained
  direct-Test bridge: a real empty original OVAL Object can be omitted when
  the 0.4 capability mapping explicitly declares that singleton and its
  original-object crosswalk. The pinned ASA version Test keeps its native
  version comparator, Test/State quantifiers and compiled source-exact check.
  Unexpected Object children and source lowering mutations fail closed.
  [#232](https://github.com/vanderpol/scap-ng/issues/232)
  [#248](https://github.com/vanderpol/scap-ng/issues/248)

- Extended the original-OVAL-attested direct-Test adapter to a singleton
  literal scalar State, preserving Test item quantifiers and State field
  existence/check boundaries in the native 0.4 compiler's source-exact Test
  form. The immutable AIX fileset original and deliberate invalid/mutated
  source and 0.3-lowering regressions are checked. Broader State composition
  and scanner-result parity remain outside the proven subset.
  [#232](https://github.com/vanderpol/scap-ng/issues/232)
  [#248](https://github.com/vanderpol/scap-ng/issues/248)

- Extended the maintained shared-source converter with a generic **direct
  Object-only Test** 0.4 adapter. The established 0.3 lowerer supplies the
  graph, and the adapter checks its Test identity, existence quantifier,
  selector mapping and scalar operation against original OVAL before compiling
  a native presence instruction. Synthetic mutation tests and three immutable
  ASA/IOS Self-Assertion examples are pinned in CI. Complex Tests remain blocked,
  and live scanner parity is not implied.
  [#232](https://github.com/vanderpol/scap-ng/issues/232)
  [#248](https://github.com/vanderpol/scap-ng/issues/248)

- Added a read-only, publicly runnable original-OVAL coverage auditor for
  the maintained converter. It counts mature 0.3 lowering and source-proven
  0.4 output separately per Definition, retains source hashes/diagnostics,
  and explicitly counts parse/deprecation blockers. Native acceptance also
  requires current schema and compiled Assessment program validation. Focused
  tests include both pinned Variable sources in CI. No scanner parity claim.
  [#232](https://github.com/vanderpol/scap-ng/issues/232)

- Added a second pinned Variable reuse path to the single-tree converter:
  Self-Assertion `independent.family_test` with an empty singleton Object,
  one regex constant Variable, `var_check=all`, and Test `at least one`.
  The 0.3 mapped graph is checked against the previously independent 0.4
  family importer, native schema/compiler and OVAL semantic round trip;
  mutations fail closed. This integrates an already-proven source case,
  without asserting generic regex/Variable coverage or scanner parity.
  [#232](https://github.com/vanderpol/scap-ng/issues/232)
  [#248](https://github.com/vanderpol/scap-ng/issues/248)

- Extended the single-tree 0.4 converter with the mature 0.3 lowering for a
  pinned four-Test `independent.variable_test` source. The 0.3 source graph
  provides both constant Variables, all four pairings, Test checks and State
  `var_check`; the adapter checks complete native output against an independent
  0.4 importer, passes schema/compiler tests, and regenerates semantically
  equivalent OVAL. CI pins original source revision and SHA256 and tests
  deliberately corrupted source and lowering. This is an integration of an
  already individually proven source case, not broader OVAL language coverage
  or live scanner parity. [#232](https://github.com/vanderpol/scap-ng/issues/232)
  [#248](https://github.com/vanderpol/scap-ng/issues/248)

- Added the first single-tree conversion integration entry point: actual 0.3
  semantic lowering and capability mapping feed final flat-Object 0.4 authoring,
  the current native Test compiler, and an independent original-OVAL differential
  gate. It proves two existing shellcommand/registry leaves and fails closed
  on unproved shapes; broad OVAL coverage and scanner parity remain open.
  Published a human-runnable developer runbook and fast regression workflow.
  [#232](https://github.com/vanderpol/scap-ng/issues/232)
  [#229](https://github.com/vanderpol/scap-ng/issues/229)

- Established a cross-version regression gate for the existing semantic OVAL
  intermediate representation using real Set/Filter, Variable-function and
  Boolean operator sources. It preserves previously supported parsing,
  effective-default and dependency behavior while the 0.3 lowering is
  consolidated into a native 0.4 renderer; it does not establish native
  conversion or scanner parity.
  [#232](https://github.com/vanderpol/scap-ng/issues/232)



- Updated the 0.4 authoring converter and typed source compiler for canonical
  `field_requirement` scopes and complete conditions. The compiler indexes
  nearest explicit field declarations; source-exact records, repeated fields,
  uncommon Test requirements and non-AND State operators retain diagnostics
  and inverse evidence. Added an original published RHEL9 OVAL → YAML/JSON →
  compiler trace. This does not establish executable scanner parity or finish
  six-STIG promotion. [#251](https://github.com/vanderpol/scap-ng/issues/251)

- Integrated the approved `field_requirement` grammar into the version-local
  Assessment schemas, with explicit Test/group/condition/field inheritance,
  complete-condition AND/OR/ONE/XOR, and implicit AND within `fields` maps.
  Rejects missing field scope and mixed legacy names on the canonical path;
  retains source-exact uncommon requirement and record fallbacks. Converter,
  compiler, editor and six-STIG promotion remain separate integration work.
  [#240](https://github.com/vanderpol/scap-ng/issues/240)
  [#248](https://github.com/vanderpol/scap-ng/issues/248)
  [#239](https://github.com/vanderpol/scap-ng/issues/239)

- Added source-verified Object-local Filters for the 28 unambiguous
  single-operand synthetic Set cases in the six-STIG authoring corpus,
  retaining eight provenance-ambiguous cases unchanged. Conversion requires
  pinned original OVAL source classification, exact reconstruction of the
  prior authored graph, and matching ordered Filter predicates. This is not
  a scanner-execution or six-state conformance claim.
  [#248](https://github.com/vanderpol/scap-ng/issues/248)
- Extended the source-gated Filter cleanup to **19 additional Test-local
  wrappers across 14 Assessment documents**, identifying their original OVAL
  Test `object_ref` rather than relying on title equality. Together with the
  first 28, this removes **47** converter-induced singleton wrappers from
  the canonical six-STIG authoring candidate. The remaining 31 Set instances
  are retained for genuine source Set semantics or further reference proof.
  An independent whole-corpus YAML/JSON inverse guard rejects any change
  outside the proven 19 sites. This is source reconstruction, not scanner
  execution parity. [#248](https://github.com/vanderpol/scap-ng/issues/248)
- Added version-local Filter validation and canonical YAML/JSON generation
  regression checks to reject disappearing/altered Filters and newly
  introduced synthetic one-operand Sets. Earlier published authoring archives
  remain immutable.
  [#248](https://github.com/vanderpol/scap-ng/issues/248)

## 0.3.0 — Unreleased

### Governance and review process

- Defined the SCAP-NG core objectives and bidirectional objective-to-issue
  traceability so release work can be evaluated against explicit project goals
  rather than feature novelty alone. [#174](https://github.com/vanderpol/scap-ng/issues/174)
- Simplified repository documentation and navigation, including a single active
  review entry point and clearer separation of specification, review,
  governance, and historical material. [#182](https://github.com/vanderpol/scap-ng/issues/182)
- Rebuilt the 0.3 examples surface as a reviewer-facing SCAP-NG feature tour,
  with embedded SCAP 1.4 comparisons and schema-validated 0.3 Scan, Benchmark,
  automated Assessment, bounded-evidence, and Manual Assessment Result examples.
  [#187](https://github.com/vanderpol/scap-ng/issues/187) [#128](https://github.com/vanderpol/scap-ng/issues/128)
- Established the specification as a prerelease/release artifact rather than a
  continuously edited design notebook; accepted changes are normalized into the
  specification at release checkpoints. [#180](https://github.com/vanderpol/scap-ng/issues/180)
- Required every new commit to reference a GitHub issue that records why the
  work exists. [#181](https://github.com/vanderpol/scap-ng/issues/181)
- Established this issue-linked release changelog process. [#181](https://github.com/vanderpol/scap-ng/issues/181)

### Language, schema, and results

- The 0.4 fast CI now enforces the native Result schemas' required, nonblank
  `summary` for both Rule Results and standalone Assessment Results. Top-level
  Rule Result `message` is not an alternate canonical field; earlier version
  snapshots remain unchanged. [#203](https://github.com/vanderpol/scap-ng/issues/203)
  [#205](https://github.com/vanderpol/scap-ng/issues/205)
- Made private Objects and States consumer-local and reserved `shared_objects:`
  for reusable/referenceable acquisition identity. [#165](https://github.com/vanderpol/scap-ng/issues/165)
- Standardized meaningful internal component IDs with required type suffixes
  (`-object`, `-state`, `-variable`, `-test`, `-input`) and schema
  enforcement. [#190](https://github.com/vanderpol/scap-ng/issues/190)
- Added native scalar/typed literal collections for exact removal of static
  Variable plumbing. [#188](https://github.com/vanderpol/scap-ng/issues/188)
- Added collection `for_each`, including correlated nested lineage semantics,
  while keeping Test/evaluate aggregation separate. [#164](https://github.com/vanderpol/scap-ng/issues/164) [#189](https://github.com/vanderpol/scap-ng/issues/189)
- Canonicalized 0.3 existence/match/comparison/filesystem vocabulary and shorter
  benchmark-local Assessment names. [#151](https://github.com/vanderpol/scap-ng/issues/151)
- Kept explicit named-Test + `evaluate` composition unchanged for 0.3; redesign
  is deferred. [#167](https://github.com/vanderpol/scap-ng/issues/167)
- Deferred shared Observation beyond normative 0.3 while retaining its production
  evidence for the next design cycle. [#166](https://github.com/vanderpol/scap-ng/issues/166)
- Kept one explicit `reported_elements` model and one canonical result contract;
  hidden reporting defaults and normative thin/full result profiles are out.
  [#125](https://github.com/vanderpol/scap-ng/issues/125) [#170](https://github.com/vanderpol/scap-ng/issues/170) [#177](https://github.com/vanderpol/scap-ng/issues/177)
- Renamed the expected-value quantifier to `value_match` in 0.3 for
  Variables, literal arrays and direct Organizational Inputs; preserved OVAL
  `var_check` meaning and independent observed `match`/`existence`.
  [#194](https://github.com/vanderpol/scap-ng/issues/194)
- Resolved native Rule, Assessment, dependency and applicability authoring
  references by logical ID at compilation; transitional source-path support
  remains for imported content. [#199](https://github.com/vanderpol/scap-ng/issues/199)
- Removed redundant `assessment_choices.default` from native 0.3 Rules; the required `default_assessment_choice` now names the actual publisher check, preserving Tailoring selection and manual-only checks. Frozen 0.2.0 is unchanged. [#217](https://github.com/vanderpol/scap-ng/issues/217)
- Added owner-approved 0.3 concise datatype authoring: native scalar literals
  omit redundant comparison types; specialized OVAL comparisons use explicit
  typed operators such as `version_greater_than_or_equal`, never `compare_as`.
  The compiler reconstructs canonical typed predicates before existing
  capability/schema validation and scanner bundle emission; variable/input
  contracts stay typed. Historical 0.2 is unchanged. Source-only six-STIG
  parity and separate OVAL runtime conformance remain explicit checkpoints.
  [#200](https://github.com/vanderpol/scap-ng/issues/200)
- Added typed compact Rule Result findings and Test-centered bounded
  Assessment evidence without claiming actual scanner results.
  [#203](https://github.com/vanderpol/scap-ng/issues/203) [#205](https://github.com/vanderpol/scap-ng/issues/205)
- Added schema-level restrictions, compiler linkage checks and typed policy
  freezing for direct expected-State Organizational Inputs. Native scanner
  evaluation conformance remains an open gate.
  [#193](https://github.com/vanderpol/scap-ng/issues/193)

## Earlier checkpoints

SCAP-NG 0.2.0 is the frozen earlier review baseline. Its exact technical state
and review material remain preserved in the repository; this changelog will not
retroactively invent issue linkage for historical commits.
