# 0.4 human authoring: `concat` is not `merge`

**18 October 2026 · Language research [#235](https://github.com/vanderpol/scap-ng/issues/235) / [#227](https://github.com/vanderpol/scap-ng/issues/227). Not a normative 0.4 change or proof of NG runtime parity.**

## An actual OVAL 5.12.3 source requirement

The **official OVAL 5.12.3 Core Definition element dictionary** [ConcatFunctionType](https://oval-community-guidelines.readthedocs.io/en/v5.12.3/oval-schema-documentation/oval-definitions-schema.html#concatfunctiontype) and [MergeFunctionType](https://oval-community-guidelines.readthedocs.io/en/v5.12.3/oval-schema-documentation/oval-definitions-schema.html#mergefunctiontype) explicitly distinguish two value-collection operations.

| Source operation | OVAL 5.12.3 effect | What a new author must not assume |
| --- | --- | --- |
| **concat** | Concatenates ordered components; if a component supplies multiple values, produces a **collection of combined strings**. Several multi-valued components expand by their **Cartesian product**. | It does **not** silently join every value into one command argument |
| **merge** | Takes one or more value components and combines the values into **one string**, with optional delimiter. | It does **not** produce a separate string for every input value |

For two literal zone values `east.example` and `west.example`, and one prefix/suffix pair, the **OVAL concat semantics** produce the two string values:

```text
concat("Get-DnsServerZone -Name ", ["east.example", "west.example"], " | ...")
  -> [
       "Get-DnsServerZone -Name east.example | ...",
       "Get-DnsServerZone -Name west.example | ..."
     ]

merge(["a.conf", "b.conf"], delimiter=" ")
  -> "a.conf b.conf"
```

With *two* multi-valued components (2 x 3), concat produces **six combinations**, not two or three. These are examples of **computed Variable values**, not a promise of six collected shell-command Items or of any scanner invocation count.

Official source, **Core Definition 5.12.3**, pages/sections: [ObjectComponentType](https://oval-community-guidelines.readthedocs.io/en/v5.12.3/oval-schema-documentation/oval-definitions-schema.html#objectcomponenttype), [FunctionGroup](https://oval-community-guidelines.readthedocs.io/en/v5.12.3/oval-schema-documentation/oval-definitions-schema.html#functiongroup), [ConcatFunctionType](https://oval-community-guidelines.readthedocs.io/en/v5.12.3/oval-schema-documentation/oval-definitions-schema.html#concatfunctiontype), [MergeFunctionType](https://oval-community-guidelines.readthedocs.io/en/v5.12.3/oval-schema-documentation/oval-definitions-schema.html#mergefunctiontype).

## What this changes in our existing readability research

The [complete DNS SV-259345 Assessment](FULL-04-dns.md) has three separate `concat` expressions, each using `values.object: list-all-forward-lookup-zones-object`, `field: stdout_line`, between constant string fragments. **The source OVAL-like intent is expansion over source values, not a scalar join.** It was correct to warn that a novice must not *infer* execution behavior from the YAML, but our review answer key can now name the OVAL value expansion behavior explicitly. The remaining open question is the **OVAL-to-native-0.4 collection/variable-instance correspondence**, not whether OVAL concat has multi-value semantics.

The [complete Apache SV-214228 Assessment](FULL-05-apache.md) has separate `merge` operations that build a **single command argument string of many configuration paths** (with source-specific delimiter/sort/order). This is fundamentally different from iterating a list of DNS names to construct multiple possible command strings.

A shorter 0.4 source language that renames both functions `combine`, hides `merge` inside `gather`, or treats a multi-valued `concat` as one string **would lose essential author-visible meaning**.

## Still unresolved: source status and cardinality

The same official 5.12.3 text also defines source-status propagation for concat. It says a component that does not exist affects concat's result, and includes a precedence chart for **Error, Complete, Incomplete, Does Not Exist, Not Collected, Not Applicable**. [ObjectComponentType](https://oval-community-guidelines.readthedocs.io/en/v5.12.3/oval-schema-documentation/oval-definitions-schema.html#objectcomponenttype) further distinguishes **no collected Object Items** and **a missing field on a collected Item**; both require proper reporting rather than substituting an empty text value. These are **Variable/component status categories**, not automatically Assessment Test result values.

An author-facing `for_each` could be a clearer spelling for *some* one-list expansion patterns, but per-collected-Item iteration is not always equivalent to per-`stdout_line`-value expansion (one Item can have zero, one or multiple same-name entities). Nor does OVAL's value expansion by itself determine how many provider instances are collected or which incomplete/failed commands produce results.

## Two conceptual operators to test — no adopted keyword yet

**Option A, retain OVAL-aligned terms:** keep `concat` and `merge`, but show their multi-value/cardinality behavior in every capability editor, validator diagnostic and compact authoring reference.

**Option B, make intent explicit in source:** distinguish **“construct each combination of source values”** from **“join values into one text”** with deliberate readable notation. Do **not** choose `each`, `join`, `for_each`, `transform` or `merge` spelling until real readers can predict the two-value and zero-value cases accurately from complete syntax. The exact Cartesian-product and result-status behavior must remain defined, not a pretty implied loop.

### Focused reader exercise (not yet run with independent reviewers)

Given the complete [DNS inline candidate](FULL-04-dns-INLINE-COMMAND-CANDIDATE.md), present `stdout_line = ["east.example", "west.example"]`. Ask **how many constructed command *strings*** result, which data flow created them, and whether the number of **executed commands** is actually specified by this source. Then present the full Apache `merge` with two file paths. Incorrectly answering “one joined DNS command string” or “two separately merged Apache command strings” exposes the semantic confusion. A correct reviewer can still say runtime command **execution** and absent/incomplete source handling need separate specification.

## Design constraint to carry into any 0.4 grammar decision

**One authoring language should represent both collection-of-strings and single joined-string transformations without hidden defaults.** Retaining OVAL terminology is acceptable if readers understand it; changing the labels is acceptable only with an independently verified exact value/status mapping and better human comprehension. There is no owner approval, no new native syntax and no compiler work in this research finding.
