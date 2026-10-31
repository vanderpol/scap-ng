# Owner-contract reconciliation — draft workstream (#255/#268)

Authority: [owner handoff](https://github.com/vanderpol/scap-ng/pull/268#issuecomment-6543913744),
[Decisions 1–28](v04-owner-final-decisions-20261031.md),
[default crosswalk](v04-editor-defaults-oval-crosswalk-20261031.md).
Initial refs: main `956bf093f0e05123abc744f32a8584a55425a3b8`, draft
`a5a7fc08c98968dc32c449307fc5c65e6f2b9c1b`.

## Initial mechanical checkpoint

The read-only audit covers all **100** version-local mappings and generates
all 100 capability schemas without changing them. It records old native names,
producer tokens, direct native example/fixture drift, source locations, applicable
owner decisions and expected corrections. Eleven capability names still carry
numeric source-era suffixes. Source QNames remain original, independently of
native naming. One generated contract differs from the old parity lock; no
fingerprint or 4,258-proof baseline was rebased.

The audit distinguishes current example drift from pinned historical fixture
content: the latter must stay preserved or be explicitly migrated to a **new**
copy. Finding native drift in an old proof snapshot is not authority to rewrite
it or inherit its proof status. Seven producer token occurrences need source-key
versus native-value classification before editing; string search alone does not
establish a semantic defect. This first inventory is partial: it does not yet
classify every nested fixture container, all consumer reference paths, or resolve
all occurrence-specific XSD restriction overrides. Counts and limits are retained
in [the checkpoint JSON](v04-owner-reconciliation-checkpoint-20261031.json).

A repeatable full machine inventory is produced by:

```bash
python tools/audit_v04_owner_reconciliation.py --output NEW_REPORT.json
PYTHONPATH=.:tools python -m unittest -q tools.test_audit_v04_owner_reconciliation
```

The output names every inspected mapping, source declaration/XPath/line/hash,
consumer capability, old field, expected form, impact and correction/review status.
The tool never converts a corpus or activates editor defaults. Full reports stay
in the task workspace/evidence; the source tree keeps the executable audit and
compact conclusions.

## Default inventory correction

There are exactly **five annotated hideable controls**, including one paired
field_requirement (two scalar members). This is six scalar values, **not six
annotations**. Decision 7 already authorizes displaying/hiding serialized
`items_satisfying: every`; no new vote is needed. Missing required YAML remains
invalid regardless of a JSON Schema default.

The earlier 204-declaration count is real but needs a precise description:
**189 attribute defaults +15 element defaults** across the eleven definition
XSDs carrying defaults. The fifteen are Windows PE-header State elements, not
fifteen extra authoring knobs for the supported capability set. Element defaults
apply to an existing empty element; they do not create an absent optional entity.
Across all pinned XSDs (including results/system characteristics), there are
281 declarations. QName reachability associates 122 declarations with supported
Test/Object/State source graphs, with inherited/overridden-use caveats retained.
A reachable declaration is not an approved NG editor default.

Source OVAL omitted filesystem scope is `all`; the approved new-authoring editor
suggestion is `local`, explicitly serialized. Source `defined` is `same`. Windows
omitted FileBehaviors recurse is `directories`; Unix/independent is
`symlinks and directories`. Scope, recursion switch/type, and max depth are
separate. Unbounded native depth is `unlimited`; no recurse:none grammar or
implicit scanner defaults are introduced.

## Coordination, tests and remaining work

Implementation is isolated on the existing registered draft branch/worktree.
[Coordination notes](https://github.com/vanderpol/scap-ng/pull/268#issuecomment-6544052191)
link #260. Main's interrupted source-proof notes remain preserved under
`/workspace/reconciliation-268-20261031/`; no main checkout edits were discarded.
No new corpus run, immutable evidence rewrite, release/tag or PR merge.

Focused baseline **81/81 PASS** (9.323s); new audit tests **5/5 PASS** (1.422s).
These are local schema/audit checks, not complete converter compatibility,
source-equivalence proof or scanner conformance. The branch remains draft.
Next: correct accepted native producer/compiler drift, add focused source-backed
Linux/Windows positives and negative omissions/old aliases, complete exact
schema-path/type/enum/default crosswalk and A/B proposals only for materially
unapproved choices. Preserve source-effective values and the separate all_exist
reference-model hold. Observe existing CI for exact commits; no duplicate full
suite and no premature current/default catalog lock.
