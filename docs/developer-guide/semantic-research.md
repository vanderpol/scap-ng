# Phase 2 semantic contract research

**Disposition: recommendations for owner review, not adopted semantics.** All
0.4.0 schema bytes and acceptance/rejection behavior remain frozen. The accepted
shared model projects this research into separate platform pages; it does not
turn recommendations into validation or scanner requirements.

[Generated index](../generated/developer-contract-research-index.md) links the
eight reviews. Each distinguishes native facts, pinned legacy observations,
historical converted Objects, recommendations, compatibility impacts and
proposed expected results. [Research records](../metadata/developer-guide-semantic-research.json)
are the single source for those generated views.

## Evidence and its limits

| Evidence | Exact identity / result | What it establishes |
| --- | --- | --- |
| Frozen native contracts | 145 JSON files; aggregate `63a61b3eb0ca95790721699f5e63b6f5a16b146660b9545a437519b508351db5` | Native structure, declared metadata and recorded semantic rules; not collector execution |
| OVAL 5.12.3 | Commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`; eight XSD files / 39 element or behavior inventories | Legacy implementation research and cryptographic provenance, not automatic native adoption |
| Published 65-stream preview | Evidence commit `7dc17f0982cdb5b17281f8f8e4373dbd87f86f58`; ZIP SHA-256 `a01ea589501bf8a53e5df68e50ca9478f19543d2bd3844546667fde743c28d8c` | 6,817 automated Assessment files in the actual historical snapshot; no grammar upgrade or new source proof |
| Original signed sources | NIWC commit `8c8e5dff860af6b1290ee9273a282db24278f8d5`, `Archive/2026_Q3`; selected ZIP/XML hashes checked against pinned source traces | Original test/object/state dependencies for the chosen specimens; not per-Test scanner equivalence |
| Structural examples | Eight research Assessments validate against local frozen resources | Syntax acceptance only; example setup, recommendations and semantic decisions remain prerequisites |
| Schema probes | 28 explicit positive/negative cases checked in portable tests | Existing schema boundaries, including permissive acceptance; no semantic validator or collector proof |
| OS witnesses | 12 bounded POSIX process/file observations; raw byte/exit/error observations checked independently | Local OS behavior only, not a SCAP-NG evaluator or OVAL oracle |
| Proposed runtime vectors | 91 fixture cases | Reviewable expected results and unresolved scenarios; **not executed by a native scanner** |

The [OVAL inventory](../metadata/developer-guide-oval-audit.json) extends the
original three-pilot subset (six files / 15 nodes) without changing those
identities. It adds Windows file/service, Linux RPM/partition and independent
text-file annotations. Paraphrases are separate from native requirements;
complete licensed XSD prose is not redistributed.

The [content audit](../metadata/developer-guide-content-audit.json) preserves
member hashes, Object/Require fragments and original dependency identities.
The smallest specimen and, where present, a traversal specimen are selected
reproducibly. A specimen's source nodes are its Rule's matching-capability
dependency closure, **not** an asserted one-to-one correspondence between each
native Test and each original node. No converted content, source OVAL, manual
Assessment or historical proof receipt was edited. The snapshot has no
non-automated Assessment files; source/manual alternatives are not reclassified.

## Immediate decision packets

### Shellcommand: binding and execution-status contract

The discrepancy is structural versus semantic: generic Object validation
accepts missing shell/command/flags and malformed values, while the capability
mapping requires explicit parameters. Keep frozen acceptance. Recommend a
closed, reviewed future binding that checks resolved parameter values before
execution, preserving explicit imported defaults and allowed references.
An alternative is continuing semantic-only diagnostics; silently tightening
0.4 is not an option in this task.

Recommend one execution Item after successful launch even when stdout is empty,
with exit status and stderr retained. Distinguish zero bytes, one empty line,
nonmatching filtered lines and duplicate lines. Each explicit error flag acts
independently. Missing interpreter, denied launch, timeout, truncation and failed
decoding/comparison need diagnosed failure paths; none should manufacture
successful absence. The exact Item/field/collection/Test propagation table,
line/encoding contract, capture association and execution context require owner
adoption. Source Object/Item prose conflicts and cannot resolve that choice.

### Registry: traversal, views, values and failures

The native mapping names hierarchy traversal, but its closed Object schema
rejects the property. A real preserved specimen requests source downward
unlimited traversal, represented historically as `max_depth: null`. Keep that
specimen and frozen rejection; future traversal syntax must use the current
explicit depth vocabulary and pass a separate grammar/version decision.

Recommend explicit target-view identity/provenance rather than scanner-process
bitness or unqualified view union. The removed source `windows_view` has no
native replacement contract. Value decisions must specify exact integer ranges,
timestamp units, binary codec, multi-string cardinality and expansion errors.
Recommend lossless FILETIME/unsigned evidence and retained raw strings, but
these remain proposals. Empty multi-string and unsupported/failed expansion
must not be conflated with a missing key or value. Complete absence and access
denial require different collection evidence and cannot share an absence success.

### UNIX file: selection, boundaries and metadata

The authored `filepath/path/filename` versus collected `full_path/directory/name`
spelling difference is established; semantic rules still use the latter names.
Recommend direct link-object metadata, explicit traversal policy and cycle-safe
descent that preserves path aliases. Choose filesystem identity versus mount
instance explicitly for `same`; recommend filesystem identity, with unknown
`local` classification producing incomplete evidence rather than a guessed set.

Recommend integer UTC epoch seconds with inode-change semantics, and permission
bits distinct from effective ACL access. Unsupported ACL must not become false:
recommend `not_collected` plus diagnostic; legacy absent-entity treatment is a
separate alternative with different absence-predicate behavior. These unit,
link, boundary and ACL decisions require native review before qualification.
Permission denial, races and incomplete traversal cannot prove complete absence.

### Text-file continuation: no-match and field-identity contract

The native capability omits the historical `54` suffix and has explicit flags
and an exact `all_object_elements_fullfilled` enum spelling. Mapping alternatives
use migrated names; the current guide exposes source `selector_map` keys, and
the generic schema accepts both forms. Recommend a reviewed field binding rather
than name guessing. Recommend explicit no-match differences for the two
`item_creation` choices, retained match/capture identity and diagnosed read/regex
errors. Negative source instance positions and capture association require a
native contract; no source operation or index is normalized here.

The five continuation reviews are complete as **research**. Windows file still
needs case/reparse/view/time/resource-status fixtures; service needs identity,
flag/dependency populations and query-error fixtures; RPM needs package identity,
raw epoch/EVR/path completeness; partition needs target mount identity, units and
complete effective options. Existing adopted requirements, such as partition
option completeness and Windows per-directory case handling, remain in force.
Further adoption work remains under the platform playbook backlog (#3).

## Assessments, expected results and compatibility

The [eight example files](research-examples/) use current structured Item/field
requirements and explicit parameters. The partition example deliberately uses
`values_matching: one_or_more` for effective `nodev` membership: an unrelated
`rw` option must not make membership fail. Registry/UNIX/shell examples use every
selected Item/value where appropriate. RPM follows mapping `package_name`;
schema acceptance of source `name` is not alias approval.

The [vector ledger](../metadata/developer-guide-semantic-vectors.json) separates
28 measured schema acceptance cases from 91 **proposed** runtime expectations.
An outcome applies only to the referenced example and stated variant/fixture,
with complete evidence and the recommended contract assumed. `unresolved` is a
research label, not a seventh native outcome; it marks a missing contract or a
scenario requiring a different Requirement before execution. No vector is an
authoritative Assessment Result. Do not turn this ledger into a substitute
scanner or call successful schema validation equivalence.

Compatibility review must cover old selector/capability spellings, null versus
unlimited depth, explicit materialized flags, multiple values/Items, source
existence checks and imported view behavior. A future schema closure changes
acceptance; a unit, link or error-table decision can change results even without
a grammar edit. Historical preview tests and proofs remain historical. No
converter migration, pack repin, scanner change or production replacement is
implemented by this research. The separate description-audit recommendations
also remain unimplemented.

## Reproduction and execution boundaries

```sh
python tools/harvest_oval_developer.py /path/to/OVAL/oval-schemas --check
python tools/audit_developer_content.py /path/to/pinned-library.zip /path/to/niwc/Archive/2026_Q3 --check
python tools/run_developer_os_witnesses.py --output /tmp/developer-os-witnesses.json
python tools/generate_native_selector_schema.py --check
python tools/generate_docs.py --check
python -m unittest discover -s tests -v
```

OS observations are in [the witness receipt](../metadata/developer-guide-os-witnesses.json).
The launch-denial fixture checks a non-executable local file. A zero-mode file
can still be read by a privileged process; that observation is explicitly not
permission-denial proof. Windows acquisition, mount boundaries, ACL-unavailable
mapping, timeout/output policy and native scanner evaluation were not executed.
Portable CI uses local frozen schemas and committed fixtures only; it does not
download the corpus or retry artifact uploads. Platform execution and independent
scanner comparison remain future gates after owner decisions.
