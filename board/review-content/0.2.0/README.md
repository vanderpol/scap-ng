# SCAP-NG 0.2.0 Board review content

Status: **six-case converter pilot; pending human review**.

This small Board checkpoint package proves a bounded conversion path and seeds
native conformance content. It is SCAP-NG Assessment content; XML files are pinned
source evidence. No schema feature, editor, broad conversion or live collector is
part of this pilot. Machine validation does not make a sample accepted.

Starting checkout: clean `/workspace/scap-ng`, `main`,
`345d8de7436adbba15cf0fe546684dbc4ba8ef5d`. Frozen technical baseline:
`7cd8b1242d7fb4a2eb9b5f49c7ec3f48b2dd622d`. The newer checkout's existing maintenance
commits remain. Self-Assertion source is pinned to
`e3538595c5083b9c34d937a81d319234df9bbfaa`, verified locally and through GitHub.

## Six converted review cases

| Sample / explanation | Source within `SCAP_1.4/OVAL_Test_Content/` | Selected OVAL scope | Review value / expected outcomes |
| --- | --- | --- | --- |
| [Family](examples/family.md) | `agnostic/ind-def_family_test.xml` | complete MITRE `def:95` | Singleton Object removal, regex Variable; true/false/error/unknown |
| [UNIX file](examples/unix-file.md) | `unix/unix-def_file_test.xml` | NAVWAR `def:1`, `tst:9` | Exact file selection, existence/completeness and linked evidence; true/false/error/unknown/not_applicable |
| [Registry](examples/registry.md) | `windows/win-def_registry_test.xml` | MITRE `def:38`, `tst:1020` | Hive mapping, case-insensitive State, exactly one satisfying Item; true/false/error |
| [Directory filter](examples/directory-filter.md) | `unix/oval-def_set-unix.xml` | MITRE `def:276`, `tst:451` | Variable-backed operand EXCLUDE, distinct `one` quantifiers; true/false/error/unknown |
| [Windows process query](examples/windows-process-query.md) | `windows/win-def_wmi57_object_test.xml` | complete MITRE `def:10` | Correlated records, integer boundary and field status; true/false/error/unknown |
| [Symlink resolution](examples/symlink-resolution.md) | `unix/unix-def_symlink_test.xml` | complete NAVWAR UNIX `def:1` | Four-Test graph, negated existence, canonical target; true/false/error/unknown |

MITRE and NAVWAR are the upstream identifier namespaces; tables abbreviate IDs
only for reading. [Provenance](provenance/) keeps exact full IDs, versions, source
namespaces/comments, whole-file/extract hashes and original source URLs. WMI is
Windows Management Instrumentation; its fixed query uses WQL, WMI Query Language.

For each case follow [manifest](manifest.json): source extract →
`mechanical/<name>.assessment.yaml` → `content/<name>.assessment.yaml` →
`expected/<name>.json` → explanation/provenance. Directory filter reuses
`sources/filter.xml`. Three selected-criterion cases are explicitly **fragments**,
not equivalent to their complete multi-Test source Definitions. Three complete
Definitions preserve their whole executable closure.

## Conversion fidelity first

[Conversion plan](conversion-plan.json) records six source selections, converter
baseline/component hashes, explicit mapping calls, and a stable local naming plan
keyed by original OVAL ID. The thin [adapter](../../../tools/convert_board_pilot_v02.py)
uses the existing project libraries in this order:

1. `lower_definition(..., collection_graph=True)` performs semantic translation.
2. Existing OVAL reverse emission/comparator checks the selected intermediate
   closure against the source. This gate is not scanner equivalence.
3. `align_assessment_vocabulary` supplies native Object/State/Test registries.
4. `apply_ready_capability_mappings` applies reviewed automatic mappings.
   UNIX file and registry additionally use existing `apply_capability_mapping`
   calls **only for these compact cases**. Their global automatic readiness flags
   remain false; this does not certify every file/registry source shape.
5. Reference-only naming uses exact source identities, avoiding generated
   placeholder/truncated labels and allocation-order names. It changes no
   predicate, selector, function, quantifier or criteria.
6. Strict 0.2.0 schemas, capability semantics and authoring contracts validate both
   mechanical and refined files. Native refinement shortens titles and replaces
   Constant `expression.literal` with the already supported `value` form. An
   executable-graph comparison verifies that these refinements change no meaning.

This is orchestration and presentation of the maintained converter, not a second
semantic converter. No production converter or mapping-readiness flag changes.
Native files omit XML serialization wrappers; original identities remain separate.
No manual semantic correction or silent upstream compensation is made.

IDs communicate resource/dataflow roles: `process-query-object`,
`explorer-process-record-state`, `canonical-target-state`,
`excluded-directories-variable`. Repeated conversion, declaration reordering and
an unrelated Object produce the same named files/graphs. A fixed reviewed source
ID plan is proven for these six cases; a general automatic naming algorithm is
not claimed. Original numeric OVAL IDs are preserved verbatim as source identity.

## Existing supporting seeds

Four earlier examples are retained outside the six-case converter pilot, under
`supporting_examples` in the manifest. They are not newly converted outputs:

| Supporting example | Origin and purpose |
| --- | --- |
| [Constants](examples/constants.md) | Earlier manual source transcription; integer boundaries and direct Variable Test |
| [Concat](examples/concat.md) | Earlier manual source transcription; Variable components, Cartesian concat, quantifier scopes |
| [Owner filter](examples/filter.md) | Native inspiration; Object component, four-level Variable chain, arithmetic, nested Sets/filters |
| [Dependency](examples/dependency.md) | Native; platform guard, repeated dependency reuse and six guard states |

Direct `variable.value` Test conversion remains a documented gap, with a focused
reproducer. Keeping these seeds does not conceal that limitation or count them as
converter successes. The complex native Variable/filter chain remains reviewable.
There are ten native Assessment files in total: six active cases plus four seeds.

## Expected behavior and evidence

All observations are **synthetic**. Independently authored case tables establish
31 primary-case expectations and 17 supporting expectations. Results were reasoned
from source/specification contracts before executing the helper. Native boundary
variants are labeled and authored in fixtures; they are not Organizational Inputs
that change Tests or commands.

The bounded test helper computes only the used Variable functions, scalar/record
comparisons, Test aggregation, conditional scheduling and native Set/filter
selection from supplied selected Items. It acquires no resources or selectors,
resolves no actual links, runs no Windows query, and is not a general regex engine
or independent scanner. Provider lifecycle injection is labeled separately.

The [linked UNIX file Result](expected/unix-file.result-set.json) explains complete
collection and the equal typed values with Item/State/Test lineage. WMI cases show
which whole records match: two records with different failed fields cannot combine
into one success. All outcomes are technical Assessment results; miscellaneous
`true` is not a policy pass. No unnecessary Benchmark wrapper is added.

## Reproduce and validate

From the repository root, with Python, PyYAML, lxml and jsonschema installed:

```sh
python tools/convert_board_pilot_v02.py --source-root /path/to/pinned-self-assertion --check
python tools/convert_board_pilot_v02.py --source-root /path/to/pinned-self-assertion --output work/board-conversion
python tools/test_board_conversion_v02.py
python tools/test_board_samples_v02.py --report work/board-pilot-validation.json
python tools/validate_native_json_schemas.py board/review-content/0.2.0/mechanical --schema-dir schema/v0.2.0
python tools/validate_native_json_schemas.py board/review-content/0.2.0/content --schema-dir schema/v0.2.0
python tools/check_current_authoring_contract.py board/review-content/0.2.0/content
python tools/assessment_results_v02.py --assessments board/review-content/0.2.0/content --result-set board/review-content/0.2.0/expected/unix-file.result-set.json
```

`--source-root` verifies the exact upstream commit, full-file hashes and each
extract's unchanged nodes/criterion scope/complete dependency closure. Offline
`--check` uses committed extracts and compares regenerated bytes; CI runs the
full pinned-source check on Ubuntu and Windows. Output writes only six mechanical
and refined pairs, never expected results or the supporting seeds.

See [validation](validation.md), [coverage](coverage.json), [questions](questions.md)
and [handoff](handoff.md). Pinned source notices and [MITRE terms](sources/MITRE-terms.txt)
remain. Paths are short and descriptive; LF checkout rules preserve source hashes
on Windows. No single-letter/generic numbered native IDs or random filenames are
used. WMI/WQL, UNIX and SCAP/OVAL are established terms, not unexplained path codes.

## Human review gate

All cases remain `pending-review`. Review source fidelity, selected scope,
quantifiers, expected results and evidence before considering canonical acceptance.
**Stop at this pilot.** The next action is human review, not conversion of the
remaining corpus, STIGs or editor work. No language decision is ratified by a green
run. See the Board checkpoint, maintained content-development task and MAINTAINING.
