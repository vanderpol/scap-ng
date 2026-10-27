# Pinned SCAP 1.4 OVAL Test Content coverage — #251

BASE_SHA: `8834539967d1dcc5939bf90240e9e05bcf938b81` · SCHEMA_VERSION: `0.4.0`.
RESULT_SHA and exact-head CI are recorded in the [machine report](v04-oval-test-corpus.json).

The entire `OVAL-Community/SCAP-Self-Assertion` collection at
`e3538595c5083b9c34d937a81d319234df9bbfaa` is inventoried, including ZIP-contained
OVAL definitions and support/reference XML. All **154 original file blobs** were
independently checked against the GitHub Git tree. The tracked [pin manifest](../../tests/fixtures/v04-oval-corpus-pin.json)
hashes every file; changed, extra or missing inputs fail before conversion.

**159 XML documents / 145 OVAL documents / 803 Tests**, with **168 Definitions,
643 Objects, 611 States and 267 Variables**. Every Test has a file-scoped recursive
dependency inventory; zero unresolved/wrong-kind/cyclic dependency diagnostics.
Inventory follows unsupported nodes instead of stopping at the first capability.
The other 14 XML documents are support/reference data, not silently dropped Tests.

The unchanged generic direct converter attempts all **190 Tests** belonging to
its 15 enabled capabilities. **145 convert, 144 validate and compile, 127 pass
independent source-term comparison**. Forty-five fail conversion, one generated
identifier fails schema validation, six compiled cases exceed the proof reader,
and eleven compiled comparisons differ. All **613 other Tests** are inventoried
as mapped-but-not-enabled (608) or unmapped reference (5), without enabling them.
This pass took **15.38 seconds** locally (including closure probes and proof checks).


| Enabled capability | Tests | Converted | Valid / compiled | Source-proved |
| --- | ---: | ---: | ---: | ---: |
| independent.environmentvariable58 | 14 | 10 | 10 | 10 |
| independent.shellcommand | 11 | 11 | 11 | 11 |
| independent.textfilecontent54 | 21 | 2 | 2 | 2 |
| windows.appcmd | 14 | 11 | 10 | 10 |
| windows.appcmdlistconfig | 16 | 15 | 15 | 14 |
| windows.auditeventpolicysubcategories | 1 | 0 | 0 | 0 |
| windows.cmdlet | 6 | 3 | 3 | 3 |
| windows.fileeffectiverights53 | 7 | 5 | 5 | 4 |
| windows.lockoutpolicy | 1 | 0 | 0 | 0 |
| windows.ntuser | 20 | 15 | 15 | 13 |
| windows.passwordpolicy | 7 | 6 | 6 | 6 |
| windows.registry | 15 | 10 | 10 | 0 |
| windows.service | 5 | 5 | 5 | 5 |
| windows.userright | 47 | 47 | 47 | 47 |
| windows.wmi.query | 5 | 5 | 5 | 2 |

The [machine report](v04-oval-test-corpus.json) lists every observed capability,
exact unsupported diagnostics and per-Test affected counts, including independent
closure blockers concealed by earlier failures. The full inventory artifact keeps
all 803 Test closures, original node hashes/references, source/native mismatch
terms and compiled-program hashes. The workflow uploads it rather than committing
bulk generated content.

Findings requiring follow-up, without manufacturing proof:

- One appcmd Variable with a punctuation-only source comment yields an invalid
  identifier stem; schema validation rejects it. Exact original IDs are recorded.
- Eight Registry source-reader comparisons retain original `HKEY_*` State values
  while native uses its enum values; three WMI57 comparisons retain source `wql`
  versus native `query`. These are diagnosed reader-term gaps, **not proofs of
  equivalence or established converter semantic defects**. Six nil-selector cases
  are explicitly unverifiable. No comparison normalization was added here.
- Conversion blockers include unapproved `all_exist`, nonnegative policy limits,
  unsupported behaviors/metadata fields, acquisition comparisons, Variable casts
  and a Unix process58 dependency. Exact messages and counts remain visible.

The 127 proofs span Windows (114), Unix (6), Linux (3), macOS (2) and Solaris (2).
The last four groups exercise already-enabled platform-independent capabilities;
they do not add macOS or other platform-specific capability support. All macOS
43 Tests and all other out-of-scope material remain pinned regression/reference
inputs. Existing separate macOS source proofs are retained.

These are **synthetic single-Test Assessments**, not original XCCDF Rules or
complete Definition proofs. They use the unmodified public schema/capability
validator and maintained Assessment-program compiler; an independent consumer
compares compiled operands. No complete Benchmark packages are built, no payload
is executed, no external Variable is supplied, and no scanner result is claimed.
An audit job completing means the measurement completed; it does not promote
unsupported/unproved cases into acceptance. The 249/0/42 Windows Rule ledger,
all source inputs, approved schemas and existing conversion outputs are unchanged.

Reproduce (Python 3.12; PyYAML 6.0.3, jsonschema 4.26.0, lxml 6.0.2):

```sh
git clone https://github.com/OVAL-Community/SCAP-Self-Assertion.git /tmp/scap-self-assertion
git -C /tmp/scap-self-assertion checkout e3538595c5083b9c34d937a81d319234df9bbfaa
PYTHONPATH=tools python -m unittest test_v04_oval_test_corpus -v
python tools/audit_v04_oval_test_corpus.py \
  --source-root /tmp/scap-self-assertion/SCAP_1.4/OVAL_Test_Content \
  --output /tmp/oval-corpus-coverage.json
```

Ten focused regressions cover real source conversion/compile/proof, complete
inventory despite unsupported nodes, scoped IDs, broken/cyclic references,
missing Variables, duplicate IDs, unbound collection input, ZIP payload safety,
deprecated-WMI rejection and unproved-count separation. Hosted mandatory results
and artifact links are finalized after the implementation push. The preceding
[source-gate checkpoint](v04-generator-trigger-reconciliation.md) is fully green.

Maintenance: `OvalDocument` indexes each file once and reuses the converter's
version-neutral reference methods; `closure` inventories every edge;
`check_conversion` records distinct stages; `summarize` groups exact diagnostics.
Change capability support in the converter only with its separate source-backed
tests. Do not change this audit's admission list or normalize proof terms to raise
counts. No new capability-specific converter branch or production change is made.

NEXT_ENGINEERING_OBJECTIVE: repair and independently test the identified generic
identifier/proof-reader gaps, then resume parity-preserving native generator
decoupling. Cross-platform source content now provides a repeatable fast breadth
measurement before further capability expansion.
