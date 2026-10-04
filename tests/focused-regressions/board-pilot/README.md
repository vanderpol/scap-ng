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
Assessment: integer local Variable `a` references `b`, and `b` references `a`.
A direct Variable Test consumes `a`. The settled dependency-graph requirement
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
