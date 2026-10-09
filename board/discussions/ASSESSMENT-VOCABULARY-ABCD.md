<!-- scap-ng-discussion-id: ASSESSMENT-VOCABULARY-ABCD-20261009 -->

# Assessment authoring: A, B, C, or D?

**OVAL Board / content-author feedback — informal and nonbinding.**

SCAP-NG 0.3 substantially simplifies OVAL authoring. Before finalizing its vocabulary, we'd like your preference on **how a real automated Assessment should read**. All three illustrations express the same RHEL 9 STIG requirement: **`/home` must be mounted with `nosuid`**.

| | A — Current SCAP-NG 0.3 | B — Ansible-inspired | C — Inspection-oriented |
| --- | --- | --- | --- |
| Technical check | `tests` | `check` | `checks` |
| Obtain target Items | `object` | `collect` | `inspect` |
| Resource selector | `select` | `where` | `select` |
| Expected values | `states` (local typed predicates) | `expect` | `expect` |
| Count/quantify | `existence` / `match` | `require` | `items` / `field_values` |
| Result fields | `reported_elements` | `report` | `evidence` |

**[Compare the three complete YAML examples for the same STIG rule](https://github.com/vanderpol/scap-ng/blob/main/board/ASSESSMENT-VOCABULARY-DISCUSSION.md)** — the examples, differences, and migration constraints are all together on one page. You need not read the longer engineering research to vote.

### How to vote

Add **👍 to exactly one of the four option comments below**:

- **A — Keep current SCAP-NG / OVAL-aligned terms.**
- **B — Prefer the Ansible-inspired terms.**
- **C — Prefer the inspection-oriented terms.**
- **D — None of the above; use a different or hybrid design.**

Option **D** is an actual preference, **not** an abstention. Please comment briefly if something is missing or you'd combine pieces of A–C. Undecided? Comment without voting.

**What is and isn't being decided:** A is the real 0.3 authoring syntax (including direct embedded Test and Filter predicates). B/C are *research sketches* — neither is schema-valid nor demonstrated losslessly convertible. **Every candidate must ultimately retain lossless forward conversion from supported SCAP 1.4/XCCDF and OVAL 5.12.3, six-state technical outcomes, quantifiers, applicability, Variables/Sets/Filters, provenance and required evidence**; unsupported/deprecated constructs require explicit errors. A preference does not approve a new grammar or imply those proofs have passed.

**Feedback question:** Which wording would be easiest to author and review? If your answer implies changing 0.3, should we investigate now or after the 0.3 checkpoint?

**Implementation and evidence:** [vocabulary issue #207](https://github.com/vanderpol/scap-ng/issues/207) · [embedded-predicate / migration issue #208](https://github.com/vanderpol/scap-ng/issues/208) · [Board decision register #209](https://github.com/vanderpol/scap-ng/issues/209) · [architecture/conformance research #197](https://github.com/vanderpol/scap-ng/issues/197).

_This is a straw poll to inform the next standards discussion, not a ratification vote._
