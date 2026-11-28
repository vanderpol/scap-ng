# Issue #87 qualification checkpoint

The canonical baseline is `58918a32bfa241dcafb16eecfed5931dad076100`. The
single active schema is 0.4.1 at `cc5eac4bfd89f2f5a5df30b7ecc1be59527c5876`,
with family SHA-256 `dc650646a24e727e68de242027cca3058683accc531f07bf6ace217609755b24`.

| Metric | Baseline | With canonical supplement |
| --- | ---: | ---: |
| Active native capabilities with a structural capability Assessment | 101/101 | 101/101 |
| Nondeprecated mapped OVAL 5.12.3 Test families with source content | 97/99 | 99/99 |
| Native capabilities linked to a source Test | 99/101 | 101/101 |
| Source Definitions | 167 | 196 |
| Source Tests | 799 | 828 |
| Additional native Assessments | 0 | 6 |
| Additional policy documents | 0 | 6 |
| Additional invalid Assessment and manual Result documents | 0 | 2 |

Two additional active native mappings retain deprecated OVAL Solaris source
Tests, `package_test` and `package511_test`. Both are already present in
Self-Assertion. Twelve nondeprecated OVAL Test declarations have no
canonical 0.4.1 mapping and remain outside the active native denominator.
The after counts combine the five canonical XML additions with the pinned
upstream corpus. [Coverage and qualification matrix](coverage.json) records the exact
consumer revisions, source pins and remaining gaps.

The separate [ESXi V2R5 qualification](../experimental/esxi/stig/README.md)
pins the October 2026 DISA archive. It accounts for 76 manual checks,
including 48 candidate projections and 28 held checks. Three typed
experimental Tests have separate expectations and current RI admission
diagnostics.

The [YAML file-content boundary suite](../oval-self-assertion/yaml-boundaries/README.md)
adds eight dedicated OVAL Definitions and two native Assessments. UNIX
OpenSCAP reproduced all four selected boundary outcomes. The pinned
converter emitted the same native Test payloads for both platforms.

## Exact schema value occurrences

The [enum and const occurrence audit](schema-value-occurrences.json) records
each value at its canonical JSON Pointer, its public entry-point reachability,
and the first matching published corpus document in each qualification scope.
It instruments the same JSON Schema dialect and checks every selected
document against the ordinary validator. Active, experimental and draft
transport witnesses appear in separate columns in the receipt.

The audit observes individual enum and const comparisons during validation.
An observed value may belong to an alternative that fails another
constraint. These counts provide a structural starting point for authoring
coverage. Semantic, converter and scanner receipts retain their own counts.

| Measure | Published documents before adding the manual Result variants | With all six manual Results |
| --- | ---: | ---: |
| Reachable enum and const occurrences | 345 | 345 |
| Values at reachable occurrences | 850 | 850 |
| Reachable values matched by active documents | 136 | 143 |
| Reachable values matched by experimental documents | 60 | 60 |
| Reachable values matched by draft transport documents | 27 | 27 |
| Reachable values without a match in any scope | 685 | 678 |

Matches can overlap across scopes. The local gate regenerates the audit in
check mode and rejects stale receipts.

## Local regression commands

From the canonical repository root with `requirements-dev.txt` installed:

```sh
bash conformance/check.sh
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
  Four UNIX probes selected Definition 101. Empty mapping and missing
  YAMLPath returned false with an Object flag of does not exist. Malformed
  and unreadable files returned error at the Definition, Test and Object
  levels. Native collection behavior remains open.
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
  are useful for comparison. The [sample audit](studio-sample-audit.json)
  checks 18 pinned documents against the current schema. All nine positive
  Assessments and four policy documents were admitted, and three syntax
  negatives were rejected. The two semantic negatives were schema-valid and
  remain unqualified by the limited canonical semantic gate. The normative
  fixtures, independent oracle and current source manifest live here.
- Four OVAL 6.0 ESXi mappings are experimental. Sixteen additional XSD Test
  families remain proposal-only. Case qualification stays separate from
  active 0.4.1 coverage. The [experimental fixture](../experimental/esxi/README.md)
  covers four typed comparisons. [Canonical #86](https://github.com/vanderpol/scap-ng/issues/86).

Full canonical discovery passed all 244 baseline tests. The standalone
documentation-fidelity check failed on a stale CPE-era manifest and passed
after regeneration from the existing generator. The reported six canonical
failures do not reproduce as a set on this baseline. The recent hosted
failures occur at generated-documentation checks. Replaying all nine
standalone checks locally passed after the fidelity refresh. The inspected
hosted records contain no list matching the reported six unittest failures.

Issue #87 remains open. Continue with YAMLFileContent empty/malformed and
permission/status oracles, shared dependency and policy/Result interactions,
per-occurrence coverage and consumer replay receipts.

## Upstream Self-Assertion replay

The production converter replayed the complete pinned upstream census with
the current schema. It emitted 167 schema-valid Definition Assessments and
accounted for 799 Tests. The independent source parity checker ran its
defined comparison checks successfully on 162 Definitions and retained
five explicit holds for `merge`, `time_difference`, Input typing and two
collected-field datatype resolutions. The companion
[upstream receipt](upstream-converter-audit.json) preserves source and native
hashes, exact identities, family counts and each diagnostic.
[Tools #128](https://github.com/vanderpol/scap-ng-tools/issues/128).

## Result package fixture

The [unsigned Result package fixture](../result-package/README.md) connects
two targets, two Benchmark Results and two Assessment invocations. Local
checks distinguish byte integrity and same-target execution identity from
schema admission. Studio's exact-pin metadata pack admitted all six
documents. Existing RI Result assembly tests passed independently of the
fixture. Scanner generation and package verification remain unqualified.

The [canonical content package replay](../content-package/README.md) builds
from the same YAML sources. RI accepted the exact package and rejected
four separately controlled integrity, reference and signature-policy
mutations. This evidence concerns content admission.

The [pinned merge witness](../variable-merge/README.md) adds independent
evidence for one of the five upstream parity holds. It checks exact
XSD-derived options, source and native Variable identities, and all four
RI Test leaves. Both order mutations produced the independently expected
results. The general Tools parity check remains open.

The [pinned time_difference witness](../variable-time-difference/README.md)
independently recalculates 29 source State values and passes each in direct
RI Test evaluation. The original clock-dependent Test also returns false,
false and true at one second below, exactly at and one second above its
threshold. The Object-backed case returned all 16 matching product
values. Assessment rollup and the general Tools parity hold remain open.

The [Studio model receipt](studio-converter-holds.json) covers the exact
converted YAML for all five parity holds, with each file checked against
the production replay digest. The exact-pin metadata pack admitted all
five documents. All five passed open/save, scalar edit, reopen and undo.

The [pinned external Variable witness](../variable-external-input/README.md)
checks Definition 562 with its companion OVAL bindings. All 18 direct RI
Test evaluations matched the independent source expectations. The missing,
empty, wrong-type and nonmatching binding controls distinguish missing
evidence, invalid evidence and a valid false comparison. Full policy enforcement and rollup
remain open.

The [collected datatype receipt](collected-datatype-holds.json) identifies
the exact macOS HOME and Solaris package-version projections. Both OVAL
System Characteristics fields and both native mappings permit multiple
datatypes. The current converter trace retains the original Variable
declaration tokens. Choosing a native type requires typed collector
evidence and may require an approved compatibility rule. The production
parity holds remain in place.

The [manual response lifecycle](../manual-lifecycle/README.md) adds a
canonical Benchmark and Rule for the existing manual Assessment. All six
choices appear in the RI workbook. Import admits four completed outcomes,
preserves an answer across a revision with the same question and marks
the answer stale when the procedure changes. Actual Benchmark policy and
Result emission remain held on this VM.

The [native Variable function replay](../variable-function-replay/README.md)
separates nine reproducible authoring contradictions from the earlier
report of six unidentified failures. The baseline Tests used `value_match:
every` against distinct expected operands. The corrected suite retains the
independent expected values, adds exact sequence comparisons and passes
all 24 direct RI function Tests plus 20 projection controls. A matching
repair to the two alias interaction Tests preserves the intended false
cardinality leaf and restores the expected two matching values.

The [ordered conditional replay](../conditional-replay/README.md) uses
the production report-side reducer at RI revision ca4fabfe. Eleven of
15 scenarios matched the independent outcome and branch expectations.
Four cases record exact status or canonical trace disagreements. Actual
branch acquisition remains unqualified.
[RI #309](https://github.com/vanderpol/scap-ng-ri/issues/309).
