# Native 0.4 library maintenance

Workstream [#261](https://github.com/vanderpol/scap-ng/issues/261), advancing
O2/O4/O7/O8; downstream integration
[VS Code #3](https://github.com/vanderpol/scap-ng-vscode/issues/3).
This is non-normative maintenance tooling, separate from the frozen #260
candidate, original-source verification and final publication.

## Preflight and bounded implementation decision

Recovered clean main `f6990f426bacb295d3a5312f70ef39b7acc4e5ff` with its two
documentary workflows green. Frozen candidate `a5db02e1b` has maintained CI
3,331 selected /3,330 passed /one optional census skip. Published all-65 DRAFT:
65 Benchmarks, 8,892 Rules, 6,817 compiled native Assessments (4,258 static-proved,
2,559 unverified), 422 automated blockers and 1,653 manual/OCIL records.

The old `scap_ng_repo_normalizer.py` discovers `benchmark.yaml` plus sibling
directories, expects path-style links and fingerprints away selected metadata.
Its rewrite path promotes duplicates. It is unsuitable for directly normalizing
the new logical-ID 0.4 DRAFT, and its historical invocation remains unchanged.
The current native compiler accepts four cross-file kinds: Benchmark, Rule,
Assessment, applicability registry. It checks one closed Benchmark namespace;
`shared_objects` stay inside their Assessment. Profiles are embedded in Benchmark
documents; splitting them into new native files would require a contract change.

The new adapter will retain all native IDs/payloads, give private namespaces
human-readable library scope labels from native Benchmark titles, and keep
shared visibility limited to the already-supported corpus shared scope. A
generated catalog/index is discoverable cache/navigation, not an authored
path-reference requirement. Assessment-only folders remain usable without a
Benchmark. Physical paths locate source; authored links remain logical IDs.

Export writes a new destination atomically. Editable YAML goes under `content/`;
source/Rule ledgers and proof/provenance records go beside it under `records/`,
and generated index data under `metadata/`. No original ZIP/XML, compiled
diagnostic, generated JSON mirror or review HTML enters the editable tree.
Blocked/manual originals link to their immutable DRAFT provenance; they do not
receive invented native Assessments. No existing source, archive or proof is
rewritten. Exact/near reuse candidates are advisory only; this round performs
no cross-Assessment promotion, ID rewrite or consumer repointing.

## CLI and importable API

Python 3.12 with the repository's pinned PyYAML/jsonschema dependencies; no model
service, network or editor installation is needed. Both entry points use one
engine:

```bash
python tools/scap_ng_repo_normalizer.py v04 check /path/to/library/content
python tools/scap_ng_library_cli.py analyze /path/to/library/content
python tools/scap_ng_library_cli.py check /path/to/library/content --changed rules/example/changed.yaml
python tools/scap_ng_library_cli.py search /path/to/library/content --scope example --query timeout
python tools/scap_ng_library_cli.py search /path/to/library/content --kind assessment --status CONVERTED_UNVERIFIED
python tools/scap_ng_library_cli.py records /path/to/library/content --scope example --status MANUAL_OCIL_ONLY_PRESERVED
python tools/scap_ng_library_cli.py uses /path/to/library/content --scope example --kind assessment --id session-timeout-assessment
python tools/scap_ng_library_cli.py index /path/to/library/content --full
python tools/scap_ng_library_cli.py compile /path/to/library/content --scope example --output /tmp/new-example.scapng
python tools/scap_ng_library_cli.py census /path/to/library/content --near --max-pairs 100
```

`analyze`/`check` never write content or an index; stdout is JSON. `index` is
an explicit disposable-cache rebuild. `--changed` is the editor's complete
rename/change/deletion notification set, and reports validation scope honestly;
use periodic `--full` to reparse everything. Ordinary unchanged checks compare
file metadata and discover new/deleted YAML; incremental checks parse only the
notified documents. Cached `search`/`uses` are navigation queries, not fresh
full-census validation claims. Metadata is indexed by kind/ID/private scope and
exact version. Duplicate IDs, including local/shared shadows and unused
duplicates, are errors; private IDs in separate Benchmark namespaces are valid.
There is no newest-version, path-fallback or first-match resolution.

```bash
python tools/scap_ng_library_cli.py export-draft /path/to/completed-draft \
  --output /tmp/new-normalized-library
# Intentional full-65 acceptance only, using exact published ZIP bytes:
python tools/scap_ng_library_cli.py export-draft /path/to/completed-draft \
  --output /tmp/new-normalized-all65 --full-corpus-deliverable \
  --source-archive /path/to/all-65-revised-draft.zip
```

The full gate requires the pinned archive SHA256 and checks consumed source
files against its embedded digest inventory. It compares original native IDs,
payload hashes and compiled Assessment programs/operands, not new OVAL proof.
Profiles stay embedded. The existing generic `direct-slice` Benchmark ID is
preserved within each private namespace; human-readable title-derived navigation
labels disambiguate namespaces without changing execution or applicability.
Scope labels/paths are tooling locations, not replacements for logical native
IDs. Shared placement accepts only the existing global shared visibility.

The generated SQLite index lives beside `content/` in `metadata/`, never in
editable source. Standalone folders get isolated cache locations when explicitly
indexed; they need no catalog or Benchmark. API: `scap_ng_library.index.Library`,
`scap_ng_library.export.export_draft`, `scap_ng_library.transaction.apply_plan`.
`Library.compile_scope(scope)` adapts one selected eligible graph to the
unchanged native compiler. No normalizer code interprets OVAL or scanner results.

The index is genuinely disposable: a rebuild recovers frozen proof/warning
associations from durable `records/streams/` sidecars by scoped kind/ID and
rechecks current hashes. A modified Rule or Assessment cannot inherit the old
proof, and Rule navigation exposes an unverified selected-method dependency.
`records` lazily queries preserved originals by scope/ID/title/status, clearly
labels them non-editable records, and links their exact original archive member.
No metadata record becomes a native Assessment. A native standalone file named
`catalog.yaml` still dispatches by its content; only the exact generated catalog
format is treated as navigation metadata.
Declared Benchmark ownership survives file renames (including after cache
deletion) through exact imported document identities and durable source-owner
metadata. Ambiguous ownership fails closed. Physical filenames never replace
native IDs. Native authoring/compilation stays independent of the evidence
repository being online; original XML inspection uses the linked archive.

## Explicit presentation apply and editor contract

`analyze` returns `change_manifest`; applications may present its diff, then
pass that exact JSON object to `apply --plan FILE --write`. Without `--write`,
apply is preview-only. Apply emits a JSON-line `plan` event **before** any write,
then an `applied` event. It rejects stale files/manifests, semantic changes and
invalid references; validates a fresh staged source view; atomically replaces
each selected file and restores prior bytes on replacement/validation failure
or handled cancellation. Workspaces should serialize explicit apply with other
writers. Canonical YAML presentation may alter comments/quoting, visible in the
reviewed patch; this is never an implicit save operation. A no-op save/check
leaves every source byte untouched. A second canonical apply has no changes.

JSON report version: `scap-ng-library-report/1`. Diagnostics include file URI,
logical document ID/kind/scope, severity/code/reason, source JSON pointer, span
when the parser provides one, affected reverse consumers, proof/warning status,
and proposed change/patch when available. Source spans are zero-based; null
means unavailable, not line zero. Plan entries include before/after hashes and
replacement text. Changed source whose hash no longer matches a frozen proof
is reported `MODIFIED_UNVERIFIED`; it never inherits the old proof by filename.

Exit codes: 0 successful check/navigation/preview/apply, 1 graph diagnostics,
2 invocation/I/O/validation failure, 130 cancellation. SIGINT/SIGTERM cancel
without semantic promotion; export staging is removed and apply rolls back.
Editors should spawn the optional CLI with an argument array, use their managed
Python environment, show stderr/process failures including ENOENT as tool
unavailable, and keep ordinary native YAML editing available. Never silently
rewrite a TextDocument on save. No TypeScript implementation is included here.

Reuse census is a separate report. Exact candidates compare all native fields
except the top-level Assessment ID; near mode is opt-in and pair-budgeted.
Every candidate remains a proposal with field differences, source locations,
reverse users and source/program hashes. No fingerprint is used as proof to
merge, remove content or repoint consumers; platform, inputs, Variables/Set/
Filters, quantifiers, provenance and error/unknown contracts remain untouched.

`compile` emits a new derived package outside editable source through the
unchanged native compiler, without adding Benchmark requirements to standalone
Assessment authoring. Full bundles still require one selected Benchmark. Real
normalized RHEL 9 and Windows Server 2025 subsets were compiled and independently
package-verified: 415 and 257 unchanged program hashes, with 20 and 18 shared
Objects respectively. Package integrity and operand comparison establish no new
original-source proof, live scanner behavior or publisher authentication.

## Completed all-65 layout acceptance

One intentional acceptance consumed the exact published DRAFT archive and its
file-digest inventory; no original conversion or OVAL proof replay occurred.
All **65 streams /8,892 original Rules** remain accounted for: **4,258** retained
static proofs, **2,559** unverified native, **422** blocked automated and
**1,653** manual/OCIL. All **6,817** compiled Assessment program hashes/operands
and all **4,258** accepted source/authoring/program hash pairs are unchanged.
All **13,754 native YAML files are byte-identical** to the published source;
only their locations change. The editable tree contains 60 native Benchmarks,
60 applicability registries, 6,817 Rules and 6,817 Assessments. Five streams
without native candidates remain original-only catalog/ledger records, not
invented editable Benchmarks. Their publisher titles come from the exact
preserved source Benchmark component; no source-graph inference is performed.

Source-relative maximum/median paths were 215/187 characters; normalized
content-relative paths are 138/122. Example (same native ID/payload/program):

```text
Before (within the published source stream):
authoring/direct-slice/assessments/the-password-for-the-krbtgt-account-on-a-domain-must-be-reset-at-least-30452496-assessment.yaml

After (within content/):
assessments/local/microsoft-windows-server-2025-stig-scap-benchmar-3266ecf9/password-krbtgt-account-domain-reset-at-170dd99a.yaml
```

The full export took 705.84 seconds, peak RSS 279,924 KiB on the recorded Linux
environment. Opening/searching one scope of the real 13,754-document index took
0.059 seconds; a notified single-document check took 0.574 seconds and parsed
one file. A separate synthetic 100-stream/10,100-document index audit took
0.012 seconds for cached scope search and 0.433 seconds for a one-document
edit/check (82,256 KiB peak). Timings are observations, not universal budgets.
Reproduce the synthetic index audit explicitly with
`python tools/audit_v04_library_scale.py --output NEW_DIRECTORY`.

The separate reuse census found 404 ID-neutral structural candidate groups,
examined 100 opt-in near pairs, and found no unreferenced Assessment documents.
It performed zero promotions. Sharing still requires independent semantic,
platform/applicability/input/provenance review and an explicitly requested step.

Historical workflow caveat: changing the compatibility entry point triggered
the older #214 0.3 layout preview workflow. Run `41039515609` fails during its
existing source renderer/schema gate (1,567 rejected documents), before invoking
the normalizer. No schema/renderer/protected workflow was changed for #261.
The maintained regression and representative Board conversion workflows for
the engine checkpoint passed. This unrelated historical preview is not a
native 0.4 acceptance claim and was not weakened/reclassified to hide failure.
