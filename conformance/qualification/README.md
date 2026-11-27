# Issue #87 qualification checkpoint

The canonical baseline is `58918a32bfa241dcafb16eecfed5931dad076100`. The
single active schema is 0.4.1 at `cc5eac4bfd89f2f5a5df30b7ecc1be59527c5876`,
with family SHA-256 `dc650646a24e727e68de242027cca3058683accc531f07bf6ace217609755b24`.

| Metric | Baseline | With canonical supplement |
| --- | ---: | ---: |
| Active native capabilities with a structural capability Assessment | 101/101 | 101/101 |
| Nondeprecated mapped OVAL 5.12.3 Test families with source content | 97/99 | 99/99 |
| Native capabilities linked to a source Test | 99/101 | 101/101 |
| Source Definitions | 167 | 188 |
| Source Tests | 799 | 820 |
| Additional native Assessments | 0 | 6 |
| Additional policy documents | 0 | 6 |
| Additional invalid Assessment and manual Result documents | 0 | 2 |

Two additional active native mappings retain deprecated OVAL Solaris source
Tests, `package_test` and `package511_test`. Both are already present in
Self-Assertion. Twelve nondeprecated OVAL Test declarations have no
canonical 0.4.1 mapping and remain outside the active native denominator.
The after counts combine the three canonical XML additions with the pinned
upstream corpus. [Coverage and qualification matrix](coverage.json) records the exact
consumer revisions, source pins and remaining gaps.

## Local regression commands

From the canonical repository root with `requirements-dev.txt` installed:

```sh
python conformance/tools/runner.py validate
python -m unittest discover -s tests -p 'test_issue87*.py'
python tools/audit_documentation_fidelity.py --check
```

The tests fail on missing or stale inventory entries, changed XML bytes, lost
source Test identities, divergent fixtures and incorrect expected outcomes.
The permanent local gate also runs as part of standard test discovery. The
conditional mutation distinguishes a missing fallback from valid authoring,
and the SQLite tests run queries against the disposable database independently
of the converter and RI.

For the converter replay, set `CANONICAL_SCHEMA_CHECKOUT` to a worktree at the
exact schema commit above. For the independent source checks, use the OVAL XSD pin and Self-Assertion pin
declared in [the source inventory](../oval-source-coverage.json). Use the OVAL
6.0 tag at `5afcf590fb5d334687bfdc47f98716424cdb7f3d`. Install `lxml` and
`saxonche` for the XML validation command. Use the ISO Schematron skeleton at
`77dcd36c53d12ed786c144ece3b2af7694abdc56`.

```sh
python conformance/tools/oval_source_audit.py --check --oval "$OVAL_5123" \
  --self-assertion "$SELF_ASSERTION" --oval6 "$OVAL_60"
python conformance/tools/validate_oval_supplement.py --oval "$OVAL_5123" \
  --schematron "$SCHEMATRON"
python conformance/tools/qualify_oval_conversion.py --check --converter "$CONVERTER" \
  --schema-root "$CANONICAL_SCHEMA_CHECKOUT/schema"
python proposed/issue86-esx-oval6/tools/validate.py
```

The [XML receipt](oval-supplement-validation.json) covers all three documents.
The [production converter receipt](oval-supplement-conversion.json) accounts
for every Definition and expected source Test ID, verifies emitted JSON/YAML
against the current schema and pins each output hash. Converter behavior
equivalence, true scanner outcomes and independent interoperability are still
open. The SQL512 rejection is tracked in [Tools #127](https://github.com/vanderpol/scap-ng-tools/issues/127).

## Consumer status

- Real UNIX OpenSCAP 1.4.2 collection matched eight of nine YAML-file-content
  Definitions. The Set/Filter discrepancy reproduced in isolation. The scanner
  advertises OVAL 5.11.1, so the replay uses the separately pinned 5.12.3 XSD
  and Schematron check. See [the normalized receipt](openscap-unix-yaml.json)
  and [canonical #132](https://github.com/vanderpol/scap-ng/issues/132).
  Four additional UNIX probes record observed empty-map, missing-path,
  malformed and unreadable behavior. They leave native collector expectations
  open until their status and authority rules are qualified.
- The RI evaluator unit suite and focused existing Profile, Tailoring and
  manual Result unit tests passed. The two guard-status Benchmark test cases
  stopped at VM filesystem admission, before evaluator execution.
  The same limit stopped direct canonical scheduler replay. The standalone RI
  evaluator rejects the valid `reported_elements: compared` setting. Changing
  only that setting in a diagnostic copy produced all four intended leaf
  results. See [the RI diagnostic receipt](ri-conditional-diagnostics.json)
  and [RI #196](https://github.com/vanderpol/scap-ng-ri/issues/196).
- Studio's current main passed 212 tests with its published metadata pack.
  A separately built candidate pack with the exact current schema exercised
  canonical Assessment model open/save/reopen/undo. Six new Assessment
  documents and 132 baseline active-only documents passed. Two additional
  baseline documents mix active and experimental Tests and were excluded
  from the active Studio qualification count. Graphical CRUD and extension
  host qualification remain open under [Studio #75](https://github.com/vanderpol/scap-ng-vscode/issues/75).
- The Studio sample repository contains overlapping ordered conditional and
  manual authoring examples pinned to an earlier 0.4.1 commit. These samples
  are useful for comparison. The normative fixtures, independent oracle and
  current source manifest live in the canonical repository.
- Four OVAL 6.0 ESXi mappings are experimental. Sixteen additional XSD Test
  families remain proposal-only. Case qualification stays separate from
  active 0.4.1 coverage. The [experimental fixture](../experimental/esxi/README.md)
  covers four typed comparisons. [Canonical #86](https://github.com/vanderpol/scap-ng/issues/86).

Full canonical discovery passed all 244 baseline tests. The standalone
documentation-fidelity check failed on a stale CPE-era manifest and passed
after regeneration from the existing generator. The reported six canonical
failures do not reproduce as a set on this baseline.

Issue #87 remains open. Continue with YAMLFileContent empty/malformed and
permission/status oracles, shared dependency and policy/Result interactions,
per-occurrence coverage and consumer replay receipts.
