# Generator-trigger source-gate reconciliation — #251

Base: `c92a563ee` (the recorded green six-workflow repair). The generator itself
is unchanged. Preflight found ten older red, still-triggered source/archive jobs;
their IDs and baseline outcomes remain in the
[preceding evidence packet](v04-current-source-acceptance.json).

Nine source jobs now use the same current-authoring/private-export-view boundary
as the repaired Windows proofs. Original XML hashes, all reverse-export assertions,
semantic comparisons, negative controls and cumulative-ledger replays remain.
The additional standalone proof set is **21 Definitions / 182 Tests**: eight
macOS/lockout/unknown singleton cases; two constant-Variable Definitions / 12 Tests;
ten datatype/entity Definitions / 158 Tests; and four original variable Test pairs.
The internal source adapters used by the maintained converter are unchanged;
explicit `convert_current` / `emit_current` entry points correct the Variable CLI.
The fixed-unknown proof retains its constant outcome and the source TestType
existence default while supplying the already-required structured authoring key.
No deprecated WMI source is admitted. These are retained standalone source proofs,
not additions to the 249-Rule direct subset or the packaged 883-Assessment ledger.

The immutable **4,001-YAML October 21** archive remains hash-pinned and reproduces
under snapshot `5ff36c8e2c7d18068e0d89255e047132e8ac6f97`; its original checks now
have a separately named opt-in archival workflow. Mandatory fixed-result negative
tests remain current. Current format coverage uses the **previously approved
4,012-document review migration**, from unchanged October 22 input hashes
`f481ff109b1f6abfda2d7f115e3140f4e82429517e4adc8cf9de00733180d8f5` (JSON) and
`d7a989c66f32c8ea7af4c6e3355847da2d39d23b82366ce3f323cd71d4a6c5c1` (YAML).
The existing Oracle exception still requires its exact original source hash and
shape. This replay produces review authoring only: **zero benchmark packages**,
no original-corpus conversion, no new normalization or release. It verifies
4,012 documents per format, parsed parity, 1,567 Rules, 883 automated and 1,550
manual Assessments, and six Benchmark/catalog pairs. It does **not** establish
original OVAL equivalence for those 883 Assessments.

That replay exposed another integration defect: structured preview Tests bypassed
Object Filter cardinality migration inside Variables. The real archived
`SV-278028` `update-variable` acquisition retained scalar `require` in its FTP
Filter, so current validation correctly rejected it. Explicit migration now uses
the existing grammar-owned Object visitor across Tests, Variables, shared Objects
and Sets. It processes acquisition subtrees once, is idempotent on current counts,
retains the comparison and Set/Filter position, and leaves literal records alone.
The pinned archived fixture, inverse/mutation checks and literal-record negative
regression cover this repair. The source fixture is labeled historical native
authoring, **not original OVAL evidence**. Current validators still reject the
unmigrated input; no automatic repair was added to validation or compilation.

Local results: **42 focused tests pass**, all additional source CLI gates pass,
historical 4,001-document validation passes, and all 4,012 current documents pass
in both formats with parsed parity. At implementation `8834539967d1dcc5939bf90240e9e05bcf938b81`, local and
downloaded hosted maintained results agree: **3,090 tests, zero failures/errors,
one existing skip**. All **24 triggered current workflows** passed, plus the
separate opt-in archival check. [Mandatory run](https://github.com/vanderpol/scap-ng/actions/runs/40421935855);
[all exact-head runs and artifact checksum](v04-generator-trigger-reconciliation.json).
The current-source prerequisite is satisfied; this does not establish release
readiness or original-source proof for the historical review migration.
All normative schema hashes remain unchanged. No original archive, source XML,
editor, scanner, corpus conversion, signing identity or release asset is changed.
The historical all_exist diagnostics and accepted Oracle exception remain
explicit migration provenance; they do not admit additional fresh-source cases.

Reproduction: existing `prove_v04_oval_*_source.py` CLIs and
`check_v04_oval_constant_variable_matrix.py` / `check_v04_oval_variable_datatype_suite.py`
use their original workflow arguments. The current format job records the exact
approved migration command and uploads both review archives plus its inverse/
exception report. Run `PYTHONPATH=tools python -m unittest
test_v04_current_source_acceptance test_v04_object_contract
test_v04_field_requirement_conversion test_v04_fixed_unknown_minimal
test_scap_converter_core -v` for the 42 focused checks.
