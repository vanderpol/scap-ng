# SCAP-NG 0.2.0 Board review content

Status: **six-case converter pilot; pending human review**.

## View the sample content

If you only want to see what SCAP-NG Assessment content looks like, start here. **Refined NG** is the human-review form. **Mechanical NG** is the direct converter output before presentation cleanup. **Source XML** is the pinned SCAP 1.4/OVAL evidence used for comparison.

| Sample | Refined NG Assessment | Mechanical NG | Source XML | Explanation |
| --- | --- | --- | --- | --- |
| Family | [`family.assessment.yaml`](content/family.assessment.yaml) | [mechanical](mechanical/family.assessment.yaml) | [OVAL XML](sources/family.xml) | [overview](examples/family.md) |
| UNIX file | [`unix-file.assessment.yaml`](content/unix-file.assessment.yaml) | [mechanical](mechanical/unix-file.assessment.yaml) | [OVAL XML](sources/unix-file.xml) | [overview](examples/unix-file.md) |
| Windows registry | [`registry.assessment.yaml`](content/registry.assessment.yaml) | [mechanical](mechanical/registry.assessment.yaml) | [OVAL XML](sources/registry.xml) | [overview](examples/registry.md) |
| Directory filter | [`directory-filter.assessment.yaml`](content/directory-filter.assessment.yaml) | [mechanical](mechanical/directory-filter.assessment.yaml) | [OVAL XML](sources/filter.xml) | [overview](examples/directory-filter.md) |
| Windows process query | [`windows-process-query.assessment.yaml`](content/windows-process-query.assessment.yaml) | [mechanical](mechanical/windows-process-query.assessment.yaml) | [OVAL XML](sources/windows-process-query.xml) | [overview](examples/windows-process-query.md) |
| Symlink resolution | [`symlink-resolution.assessment.yaml`](content/symlink-resolution.assessment.yaml) | [mechanical](mechanical/symlink-resolution.assessment.yaml) | [OVAL XML](sources/symlink-resolution.xml) | [overview](examples/symlink-resolution.md) |

For a fast review, open a **Refined NG Assessment** first, then compare it with the adjacent **Source XML**. The explanation pages describe the selected OVAL scope, expected outcomes, and why each case was chosen.

### Frequency-oriented examples

The six-case pilot above was chosen for semantic coverage, not prevalence. To make the review set more representative of real DISA content, three additional native 0.2.0 examples are now derived from the pinned SCAP 1.4 Self-Assertion corpus and emphasize commonly encountered capability families:

| Capability | Native Assessment | Why it is here |
| --- | --- | --- |
| `independent.textfilecontent54` | [`textfilecontent54.assessment.yaml`](content/textfilecontent54.assessment.yaml) | Text-file content checks are among the most common patterns in the current NIWC/DISA corpus. |
| `linux.rpminfo` | [`rpminfo.assessment.yaml`](content/rpminfo.assessment.yaml) | Common Linux package-presence/version metadata pattern. |
| `unix.sysctl` | [`sysctl.assessment.yaml`](content/sysctl.assessment.yaml) | Common UNIX/Linux kernel-parameter pattern. |

The existing UNIX file and Windows registry cases are also representative high-frequency families. The Windows process/WMI example remains because it exercises correlated-record semantics; it should be read as a useful semantic stress case, not as evidence that process queries themselves are common DISA checks.

### Key language-feature examples

Capability frequency alone is not sufficient for Board review. Real SCAP content also depends on Variables, Sets, filters, quantifiers, multi-step dataflow, applicability, explicit reporting controls, and manual assessment. The [Assessment feature sample index](FEATURE-SAMPLES.md) is the authoritative inventory; this table highlights the most useful non-trivial examples:

| Language feature | Native Assessment | What it demonstrates |
| --- | --- | --- |
| Variable-backed filter | [`directory-filter.assessment.yaml`](content/directory-filter.assessment.yaml) | Constant multi-value Variable, Variable reference in State comparison, `variable_match: one`, EXCLUDE filter, and Set semantics. |
| Complex Variable/filter dataflow | [`filter.assessment.yaml`](content/filter.assessment.yaml) | Object-component Variable, chained local Variables, arithmetic, Cartesian multi-values, nested union/intersection, and filtering. |
| Multi-value Variable functions | [`concat.assessment.yaml`](content/concat.assessment.yaml) | Constant Variables, Variable components, Cartesian concatenation, and quantified comparison of generated values. |
| Explicit Variable tests | [`constants.assessment.yaml`](content/constants.assessment.yaml) | Direct `variable.value` Tests, integer comparison, and multi-value quantification. |
| Set difference | [`set-difference.assessment.yaml`](content/set-difference.assessment.yaml) | Reusable Set subtraction with no hidden set behavior. |
| Multiple State aggregation | [`multi-state.assessment.yaml`](content/multi-state.assessment.yaml) | Two States with explicit `states_match: all`. |
| Intrinsic applicability | [`intrinsic-applicability.assessment.yaml`](content/intrinsic-applicability.assessment.yaml) | Assessment-level applicability separate from normal evaluation. |
| Explicit reporting projection | [`reported-elements.assessment.yaml`](content/reported-elements.assessment.yaml) | Explicit evidence field selection; omission is not a reporting default. |
| Manual Assessment | [`manual.assessment.yaml`](content/manual.assessment.yaml) | Native human determination without an OCIL workflow graph. |

These examples are intentionally more complex than the frequency-oriented capability examples. The review set should prove that SCAP-NG remains readable when the source logic is non-trivial, not merely that simple Tests serialize cleanly.

## What these six samples cover

- **Family:** singleton Object removal and regex Variable behavior.
- **UNIX file:** exact file selection, existence/completeness, and linked evidence.
- **Windows registry:** hive mapping, case-insensitive State comparison, and single-item satisfaction.
- **Directory filter:** Variable-backed EXCLUDE behavior and distinct `one` quantifiers.
- **Windows process query:** correlated records, integer boundaries, and field status.
- **Symlink resolution:** a four-Test graph, negated existence, and canonical target handling.

Three samples preserve complete source Definitions; three are intentionally selected fragments for focused review. Exact source IDs, versions, hashes, namespaces, and source URLs are retained under [provenance](provenance/).

## About this review set

This is a bounded six-case converter pilot for human/OVAL Board review. The YAML files are native SCAP-NG Assessment content; the XML files are pinned source evidence. Machine validation does not make a sample accepted, and this pilot does not by itself establish live collector or independent scanner equivalence.

Frozen technical baseline: `7cd8b1242d7fb4a2eb9b5f49c7ec3f48b2dd622d`. Self-Assertion source is pinned to `e3538595c5083b9c34d937a81d319234df9bbfaa`.

[Manifest](manifest.json) records the source → mechanical NG → refined NG → expected-result chain for each case.


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
The Board directory now also contains focused 0.2.0 feature samples. Treat [FEATURE-SAMPLES.md](FEATURE-SAMPLES.md) as the maintained inventory rather than relying on a hand-maintained file count here.

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

See [validation](validation.md), [coverage](coverage.json), and [questions](questions.md). Pinned source notices and [MITRE terms](sources/MITRE-terms.txt)
remain. Paths are short and descriptive; LF checkout rules preserve source hashes
on Windows. No single-letter/generic numbered native IDs or random filenames are
used. WMI/WQL, UNIX and SCAP/OVAL are established terms, not unexplained path codes.

## Human review gate

All six pilot cases remain `pending-review`. Review source fidelity, selected scope,
quantifiers, expected results, and evidence before considering canonical acceptance.
The separate 65-package conversion build is broader migration evidence; it does not
replace human review of these small examples or ratify any language decision. See the
[Board review page](../../README.md) for the current full-corpus artifact and
[MAINTAINING](../../../MAINTAINING.md) for acceptance/change discipline.
