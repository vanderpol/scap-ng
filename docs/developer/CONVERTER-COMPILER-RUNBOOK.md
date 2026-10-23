# Current 0.4 converter and compiler developer runbook

**Scope: October 23, 2026 pre-alpha integration checkpoint.** The supported
paths below are a bounded subset. No published full OVAL coverage or scanner
conformance is claimed.

## One source tree; historical releases are immutable

- Develop on `main`. Keep one current converter/upgrade path and one current
  native compiler. Isolated research branches are temporary; merge reviewed
  changes back to `main`. Never maintain a parallel live 0.3 source tree.
- Use [versioned source snapshots](../releases/TOOLCHAIN-RELEASES.md) from the
  exact release tag to reproduce an older output, including its specification,
  schemas, guides and test fixtures. A developer source snapshot is **not** a
  release declaration or an executable scanner-conformance certificate.
- Do not modify the normative release specification to make a conversion test
  pass. Capture genuinely ambiguous semantics for human review.

## Converter: preserved 0.3 functionality in a 0.4 entry point

From a repository checkout with Python 3.12 and pinned test dependencies
`lxml==6.1.1`, `PyYAML==6.0.3`, `jsonschema==4.25.1`:

```bash
python tools/scap_converter_core.py \
  --source-xml /path/to/original-oval-definitions.xml \
  --definition-id oval:example:def:1 \
  --output /tmp/assessment-0.4.json \
  --evidence /tmp/assessment-conversion-evidence.json

python tools/test_scap_converter_core.py -v
python tools/test_oval_semantic_core_preservation.py -v
# With the pinned source available (see below):
SCAP_NG_VARIABLE_SOURCE_XML=/path/to/ind-def_variable_test.xml \
  python tools/test_scap_converter_core_variable.py -v
SCAP_NG_FAMILY_SOURCE_XML=/path/to/ind-def_family_test.xml \
  python tools/test_scap_converter_core_family.py -v
```

The current implementation calls the established semantic IR parser and
`scap_upconvert_v003` source/language lowering plus its 0.3 capability
alignment. A distinct 0.4 projection reuses the verified flat-Object and
requirement transformations, validates the Test through the native 0.4
compiler, and checks source-exact agreement with the independently developed
original-OVAL importer (normalized to final flat-Object syntax).
The checkout must contain both `schema/v0.3.0/capability-mappings/supported/`
and `schema/v0.4.0/capability-mappings/supported/`. In particular the mature
0.3 mapper represents a direct shell Filter using an intermediate single
UNION Set operand; the 0.4 adapter admits that exact source-proven shape,
while real original OVAL Sets remain unsupported. Missing 0.3 mappings are
an error, never an implied conversion fallback.

**Supported in this checkpoint:** one direct
`independent.shellcommand` PowerShell presence Test with a single `include`
Filter, or one direct `windows.registry` value-equality Test with its
original `only one` item quantifier; **also** one pinned
`independent.variable_test` four-way source Definition
`oval:org.mitre.oval.test:def:538`. It contains four distinct AND-ed Test
bindings across two constant string Variables and preserves State `var_check`
separately from Test item quantifiers. The shared core uses the mature 0.3
graph as its executable source, checks it against the independently audited
native 0.4 implementation and regenerates OVAL for semantic comparison.
Also admitted: pinned `independent.family_test` Definition
`oval:org.mitre.oval.test:def:95`, which uses one regex constant Variable,
preserves State `var_check=all` and the Test `at least one` check, and has
independent 0.4 import/export and semantic round-trip proof.

For the Variable regression, retrieve only the immutable
[`e3538595` Self-Assertion source](https://github.com/OVAL-Community/SCAP-Self-Assertion/commit/e3538595c5083b9c34d937a81d319234df9bbfaa)
at `SCAP_1.4/OVAL_Test_Content/agnostic/ind-def_variable_test.xml` and
`SCAP_1.4/OVAL_Test_Content/agnostic/ind-def_family_test.xml`;
both regressions check their SHA256. The sources are fetched by the maintained
GitHub Actions test, not copied into the repository.

These four source-bound cases are **not** a general language-coverage claim;
both Variable cases already had independent 0.4 coverage prior to integration.
All other shapes must error, including genuine Sets, arbitrary Variable
references/function chains, arbitrary nested criteria, unsupported Filters
and unmatched Test/State semantics. The legacy broad 0.3 importer
remains available to avoid destroying existing source support while verified
0.4 adapters are added.

The CLI writes a single standalone Assessment authoring document. It **does
not** create a full Benchmark/Rule graph or an executable `.scapng` bundle.
Run source-to-native differential tests and versioned compiler checks before
raising coverage claims. The evidence JSON explicitly marks `scanner_parity`
and `full_oval_coverage` false.

## Count source coverage before choosing the next construct

Run the public read-only source audit against a pinned original OVAL corpus,
or a single original XML file:

```bash
python tools/audit_scap_converter_core_coverage.py \
  --source /path/to/original-oval-corpus \
  --report /tmp/oval-core-coverage.json
python tools/test_audit_scap_converter_core_coverage.py -v
```

The report contains every Definition's source hash and status, plus separate
counts for mature **0.3 source lowering** and **current source-proven 0.4
output**, including 0.3-lowerable cases blocked in the current core. Native
0.4 acceptance also requires schema validation and compiler program acceptance.
Malformed files and deprecated Definitions are counted separately; they are
never removed silently from the denominator. This is a converter coverage
inventory only, **not** a scanner parity or STIG benchmark completion report.
The dedicated CI converter regression tests the two pinned external Variable
Definitions through this reporting path as well as the direct conversion path.
For the full 167-Definition Self-Assertion source audit, manually trigger
`0.4 original OVAL core conversion coverage (manual)` in GitHub Actions. It
checks out the original repository at its immutable revision and uploads the
complete per-Definition report; this deliberately does not run on every push.

## Compiler: canonical 0.4 graph only

For a complete, closed native 0.4 authoring archive, compile independently
parsed JSON and YAML and require byte-for-byte native-bundle equality:

```bash
python tools/v04_native_bundle_compiler.py \
  --json-archive /path/to/canonical-authoring-json.zip \
  --yaml-archive /path/to/canonical-authoring-yaml.zip \
  --output-dir /tmp/compiled-scapng \
  --report /tmp/compiled-scapng-report.json
```

The compiler verifies native source graphs and compiled Test/result programs.
It does not execute a live scan; signing and publisher trust are separately
specified. Consult the [tool index](../../tools/HUMAN-RUNNABLE-SCRIPTS.md)
for source package and single-serialization development modes.

## Coverage evidence required before retiring 0.3 modules

For each newly supported construct, pin original OVAL and XCCDF sources;
assert exact field operations, existential/value quantifiers, criteria and
Filter/Set sequencing; test negative cases; compare source→0.4 and 0.4→OVAL;
run schema and native compiler checks. Record coverage numerator,
denominator, blocked cases and scanner-unproved cases separately. Retain the
old source-lowering path until its replacement demonstrably covers it.
