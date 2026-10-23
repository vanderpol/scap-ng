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
```

The current implementation calls the established semantic IR parser and
`scap_upconvert_v003` source/language lowering plus its 0.3 capability
alignment. A distinct 0.4 projection reuses the verified flat-Object and
requirement transformations, validates the Test through the native 0.4
compiler, and checks source-exact agreement with the independently developed
original-OVAL importer (normalized to final flat-Object syntax).

**Supported in this checkpoint:** one direct
`independent.shellcommand` PowerShell presence Test with a single `include`
Filter, or one direct `windows.registry` value-equality Test with its
original `only one` item quantifier. These are the two existing pilot fixtures,
not an expansion of the language-coverage denominator. All other shapes
must error, including Sets, Variable references, nested criteria, unsupported
Filters and unmatched Test/State semantics. The legacy broad 0.3 importer
remains available to avoid destroying existing source support while verified
0.4 adapters are added.

The CLI writes a single standalone Assessment authoring document. It **does
not** create a full Benchmark/Rule graph or an executable `.scapng` bundle.
Run source-to-native differential tests and versioned compiler checks before
raising coverage claims. The evidence JSON explicitly marks `scanner_parity`
and `full_oval_coverage` false.

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
