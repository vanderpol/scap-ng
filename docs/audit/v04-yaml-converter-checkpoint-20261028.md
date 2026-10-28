# YAML converter checkpoint — source-preserving bounded support

Tracking: [#251](https://github.com/vanderpol/scap-ng/issues/251), with design
coordination in [#255](https://github.com/vanderpol/scap-ng/issues/255).

The existing direct converter now admits the approved
`independent.yamlfilecontent` mapping for proved constructs. Activation increases
from 47 to **48/51** mappings in the approved Independent/Linux/UNIX/Windows
scope (**48/100** globally). No new normative syntax, capability mapping,
schema, generator, compiler, scanner, editor or 0.3 implementation is changed.
The owner canonical-function checkpoint `3b00b469727700e428f433d88c89b408669348f2`
is retained, including its default grammar and opt-in migration probe.

## Source evidence and implementation

[Five original OpenSCAP documents and supporting inputs](../../tests/fixtures/v04-direct-yaml/README.md)
are pinned byte-for-byte to `099cd84a0fa23c0e5d748e4e577c900c9b280623`.
All **51 original Tests** are XSD/Schematron-valid and nondeprecated.
**45/51** convert, validate, compile and match independently decoded typed
acquisition/State/Variable terms. Every converted Assessment also passes native
compiled-bundle schema, graph, integrity and exact-program verification in a
constructed packaging wrapper; no production Benchmark/Rule proof is inferred.

The shared engine owns mapped selectors, source dependencies, typed operands,
Variable matching, record cardinality, Sets and ordered Filters. A small helper
adds YAML-specific acquisition guards and decodes OVAL's caret transport names
into the actual YAML record key identity required by the existing mapping.
Source/native proof readers decode independently and import no renderer helper.
The source files, source IDs, provenance and failure identities remain intact.
No queries are executed or replaced with synthetic Items while converting.

Six Tests remain explicitly unsupported:

- Array Tests 2/4/5 use deferred `split`, covered by the grouped function contract.
- Content Tests 2/3/4 require `object_component` projection of Object 1's `value`
  record member `yaml` into local string Variable `oval:0:var:1`. This is different
  from already-supported State record fields containing Variable references.
  The native projection contract has Object/field, with no established separate
  record-member selector. Returning the record or guessing a dotted field path
  would change meaning or introduce grammar. Preserve this pinned counterexample
  for #255; no fallback or source repair is used.

The consolidated gap report includes these six cases with their own cohort
and denominator: three unsupported OVAL operations and three Variable/collection
representation limitations. The 803-Test Self-Assertion and NIWC production
Rule denominators are unchanged.

## Verification and preservation

Commands are run with `PYTHONPATH=.:tools` from the checkout root.

- Combined YAML/diagnostic/canonical Variable/expanded-proof suite: **50 tests,
  zero failures/errors/skips** after merging the owner checkpoint.
- YAML compiled-package regression after adding per-Assessment bundle checks:
  **8 tests, zero failures/errors/skips**, 45 original compiled packages verified.
- Hash/process58/special-datatype/cmdlet/Windows-proof/diagnostic suite:
  **39 tests, zero failures/errors/skips** before the additive report regression.
- Explicit-datatype/user-rights and regenerated-contract suites: **9 tests,
  zero failures/errors/skips**, including all 39 previously proved Server 2025
  user-rights Rules.
- Updated diagnostic suite: **7 tests, zero failures/errors/skips**.
- All **100** regenerated capability contracts match the reviewed parity hashes;
  no baseline changes, 141 selectors and 694 State entries retained.
- Self-Assertion: **521/710** configured Tests compiled and typed-term proved;
  **519/803** original Tests additionally source-valid/nondeprecated. All 521
  previous proof identities, source/native terms and program hashes retained;
  zero mismatches.
- Six primary sources: **1,012/1,396** OVAL Rules remain proved/compiled. All 1,012
  previous program hashes retained; no new primary Rule admitted. Counts remain
  RHEL 270, Oracle 265, Windows 11 228 and Server 2025 249. DNS and Apache retain
  their existing source/representation blockers.

Exact published-head maintained regression and workflow conclusions are recorded
in the #251 handoff after CI; they are not inferred from focused tests.

These proofs concern typed semantic terms and compiled operands. They do not
establish YAML parser/probe execution, YAML type/null/nonfinite-value handling,
platform file acquisition, offline roots, scanner-runtime equivalence, full
applicability or release readiness. Functions awaiting coordinated production
activation, incomplete aggregation, IEEE-32 (#218) and dynamic invocation fan-out
remain separate obligations. The remaining three inactive platform capabilities
are SSHD (nil/default-path schema dependency), RPMverifyfile (deprecated original
examples) and SQL512 (valid pinned original-source evidence still missing).
