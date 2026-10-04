# Board pilot minimal reproducers

Status: **pending-review**. Pinned upstream revision:
`e3538595c5083b9c34d937a81d319234df9bbfaa`. Each source XML retains one criterion and
its original complete node closure; accompanying provenance pins the whole
original file and local extract. Source notices apply; see the retained
[MITRE terms](../../../board/review-content/0.2.0/sources/MITRE-terms.txt).

## Binary/Boolean source disagreement

`binary-source.xml` retains Definition `oval:org.mitre.oval.test:def:620`,
Test `tst:833`, Object `obj:841`, State `ste:266`, and Variable `var:945`.
The Variable declares binary datatype but has lexical text `true`; the State
declares Boolean and expects true. Its title/description says always true.

Classification: **probable source content defect**, not a native-schema defect.
Expected semantics: typed binary values require valid binary lexical content;
an invalid value cannot establish the described true result. Do not use this
case as a Boolean or dependency equivalence oracle. Generic XSD string validity
alone does not establish datatype/evaluation validity. The regression preserves
the disagreement and invalid hex text; it does not claim execution in ovaldi.

Proposed question: did upstream intend `datatype="boolean"`? Correction belongs
in source content after human/upstream review. No implicit binary-to-Boolean
coercion is proposed for SCAP-NG.

## Strict native converter gap

`constant-source.xml` retains one valid integer Variable Test from Definition
`oval:org.mitre.oval.test:def:92`: 9 equals 9, so its independent result is true.

Classification: **converter limitation**, already consistent with the documented
legacy-converter bridge. The maintained lower/align/ready-mapping pipeline retains
`independent.variable` and its Object wrapper; merely setting specification 0.2.0
does not turn that output into valid native `variable.value` content. Strict
0.2.0 validation must reject the residual source capability. The regression
makes that rejection visible without enabling the legacy bridge or relaxing a schema.

Proposed future fix: implement/review complete direct-Variable source lowering,
typed constant normalization, and cross-node bindings before advertising a strict
0.2.0 converter path. The Board pilot manually transcribes the supported semantics
and records original IDs separately. No converter changes are made in this task.

## Native local Variable cycle

`variable-cycle.assessment.yaml` is an original native, schema-valid minimal
Assessment: integer local Variable `left-cycle-value` references `right-cycle-value`, and
`right-cycle-value` references `left-cycle-value`.
A direct Variable Test consumes `left-cycle-value`. The settled dependency-graph requirement
rejects static cycles before execution; there is no legitimate result to guess
by recursing, truncating the chain or treating it as an empty collection.

Classification: **semantic-validator defect/gap**. The current shared capability
semantic validator returns no diagnostic for this graph. The pilot regression
records that gap and independently rejects it with a test-only dataflow guard.
`pilot.dataflow_cycle` is a helper-local diagnostic, not a proposed normative
wire reason code. This reproducer is not an accepted Board sample.

Proposed follow-up: review a shared validator pass for local Object, Variable,
State/filter and Test references, including cross-kind cycles and missing
references. Shared code/schema fixes are outside this frozen content pilot.

Run the three focused regressions and Board samples with:

```sh
python tools/test_board_samples_v02.py
```

## Uncommented State naming

`symlink-name-source.xml` reduces the pinned symlink source to its working-link
criterion `tst:6`, Object `obj:6` and State `ste:6`; accompanying provenance keeps
exact original identities and hashes. The missing State comment causes the
maintained lower/align/mapping pipeline to produce `state-no-comment`, which does
not explain the canonical-target comparison. WMI comments also produce long,
truncated default names. Classification: **converter identifier-generation
limitation**, not a semantic/schema defect.

The six-case conversion adapter applies a deterministic naming plan keyed by
exact source IDs, producing `canonical-target-state` without changing the
comparison. This is a bounded presentation correction, not a global naming
algorithm or a second semantic converter. General automatic naming remains
unproven; source IDs/comments stay in separate provenance. The regression shows
both the default limitation and the readable pilot result:

```sh
python tools/test_board_conversion_v02.py
```

The current converter-first pilot does not count the earlier manually transcribed
constant/concat examples as mechanically converted. They remain supporting seeds;
the direct-Variable conversion gap above remains unresolved.
