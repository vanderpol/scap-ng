# Complete pinned OVAL Test Content coverage — #251

BASE_SHA: `8834539967d1dcc5939bf90240e9e05bcf938b81` · SCHEMA_VERSION: `0.4.0`.
RESULT_SHA: `f2d68bf2032bdee7819be425b58ccd224ef7145f`. Exact-head CI and checksums are in the
[machine report](v04-oval-test-corpus.json).

The complete `OVAL-Community/SCAP-Self-Assertion` collection at
`e3538595c5083b9c34d937a81d319234df9bbfaa` is inventoried, including ZIP-contained
OVAL and support XML. All **154 original file blobs** match the upstream Git tree.
The [pin manifest](../../tests/fixtures/v04-oval-corpus-pin.json) hashes every file;
missing, extra or changed inputs fail before conversion.

**159 XML documents / 145 OVAL documents / 803 Tests**, plus **168 Definitions,
643 Objects, 611 States and 267 Variables**. Every Test has its complete file-scoped
recursive reference graph; zero unresolved/wrong-kind/cyclic dependency diagnostics.
The other 14 XML documents remain identified support/reference data. The collection
contains 98 of 100 mapped identities; `independent.sql512` and
`independent.yamlfilecontent` have no fixtures.

Two measurements prevent confusing generic potential with production admission:

| Measurement | Test attempts | Converted | Valid / compiled | Source-proved |
| --- | ---: | ---: | ---: | ---: |
| Existing enabled converter: 15 mappings | 190 | 145 | 144 | 127 |
| Diagnostic generic visitor: 83 non-macOS mappings | 768 | 329 | 297 | 133 |

The second pass supplies approved mapping metadata to the **same unchanged
visitor**. It adds **zero conversion code, capability branches or production
admissions**. All 81 represented non-macOS mappings are attempted. **65** produce
at least one valid compiled case; **48** compile every available fixture Test;
only **four** prove every fixture Test. These are fixture measurements, not
certification of each capability's full OVAL language surface.

**439** probes fail conversion; **32** produce authoring rejected by current
schema/capability validation. Of **297** compiled probes, **153** exceed the
independent proof reader, **11** differ in comparison terms, and **133** prove.
No unexpected implementation exceptions occurred. Thirty macOS-specific Tests
and five unmapped IOS/Junos Tests remain reference-only. All 43 Tests in the macOS
directory are preserved; generic Unix/independent acquisitions in those files
are measured without implementing any macOS capability. Experimental/deferred
capabilities remain outside the supported-mapping probe.

The full pass, including the separate configured baseline, took **56.70
seconds** locally. The [machine report](v04-oval-test-corpus.json) gives successes,
exact observed diagnostics, paths and denominators **by every capability**.
After failure, each dependency is probed through its complete typed visitor;
calling a scalar helper outside its real context could falsely flag supported
cmdlet null inputs. The full hosted artifact retains all 803 closures, node hashes,
references, compiled/authoring hashes, and complete mismatch terms.

Findings remain visible:

- The configured baseline's appcmd Test `oval:navy.navwar.niwcatlantic.scc.test:tst:102`
  has a punctuation-only Variable comment, yielding invalid `-34d6e422-variable`.
- Other diagnostic schema failures involve RPM materialized defaults and
  process58/SID/update-search acquisition shapes. Nothing is silently repaired.
- Eight Registry comparisons retain original `HKEY_*` State values in the source
  reader versus native enums; three WMI57 comparisons retain `wql` versus native
  `query`. These are diagnosed reader-term gaps, **not equivalence proofs or
  established converter semantic defects**. Nil selectors and other unsupported
  proof rules remain explicitly unproved.
- The 34 Set-dependent Test closures are inventoried and attempted, but none
  compiles through this visitor: first failures are unsupported Variable Object
  `var_ref` (18), file acquisition `behaviors` (14), and `all_exist` (two).
  This does not imply that Set conversion itself is missing.
  Seventeen Filter-dependent closures yield eight compiled/two proved cases.
  Exact per-node diagnostics and Variable/dependency counts remain in evidence.
- Common observed blockers include Test-source shape, unapproved `all_exist`,
  acquisition behaviors/parameters, datatypes and Variable functions. Complete
  diagnostic strings are preserved rather than replacing them with generic labels.

These are **synthetic single-Test Assessments**, not original XCCDF Rule,
Definition, Profile or Benchmark proofs. The unmodified public validator checks
schema/capability contracts; the maintained Assessment-program compiler and an
independent consumer compare compiled operands. No full Benchmark packages,
support payload execution, external Variable bindings or scanner results are
claimed. The 249/0/42 Windows Rule ledger and 883-Assessment ledger are unchanged.
Audit completion means measurement completed, not that unsupported/unproved
probes passed acceptance. Existing mandatory source-proof obligations remain.

Reproduce (Python 3.12; PyYAML 6.0.3, jsonschema 4.26.0, lxml 6.0.2):

```sh
git clone https://github.com/OVAL-Community/SCAP-Self-Assertion.git /tmp/scap-self-assertion
git -C /tmp/scap-self-assertion checkout e3538595c5083b9c34d937a81d319234df9bbfaa
PYTHONPATH=tools python -m unittest test_v04_oval_test_corpus -v
python tools/audit_v04_oval_test_corpus.py \
  --source-root /tmp/scap-self-assertion/SCAP_1.4/OVAL_Test_Content \
  --output /tmp/oval-corpus-coverage.json
```

Twelve focused regressions cover original conversion/compile/proof, complete
inventory despite unsupported nodes, file-scoped IDs, broken/cyclic references,
missing Variables, duplicate IDs, collection pin enforcement, ZIP payload safety,
deprecated-WMI rejection, supported cmdlet nulls, unproved-count separation and
metadata probing without production admission. **All six triggered exact-head workflows pass** at the implementation SHA.
The downloaded [mandatory result](https://github.com/vanderpol/scap-ng/actions/runs/40433912422)
reports **3,102 tests, zero failures/errors, one existing skip**; no previous
maintained test IDs disappeared. The [corpus run](https://github.com/vanderpol/scap-ng/actions/runs/40433912398)
took **36.9 seconds** and its [complete inventory artifact](https://github.com/vanderpol/scap-ng/actions/runs/40433912398/artifacts/12703361578)
matches all local non-timing evidence. A post-restart run reproduces the same
results in 52.7 seconds. Exact environment versions, archive/JSON hashes,
all run links and selected-test digest are in the machine report. The preceding
[source-gate checkpoint](v04-generator-trigger-reconciliation.md) is fully green.

Maintenance: `OvalDocument` indexes each source once; `closure` inventories every
edge; `probe_mappings` selects approved diagnostic contracts; `check_conversion`
records distinct stages; `summarize` groups exact diagnostics. Production still
uses its unchanged `load_mappings` admission list. Never promote a probe merely
because it compiles, or normalize proof terms to raise counts. All original
source, schema and existing converter/compiler output is preserved.

NEXT_ENGINEERING_OBJECTIVE: use this fast breadth measurement while resuming
parity-preserving native schema-generator decoupling; prioritize shared Test-source,
acquisition-contract and independent-proof gaps before adding procedural branches.
