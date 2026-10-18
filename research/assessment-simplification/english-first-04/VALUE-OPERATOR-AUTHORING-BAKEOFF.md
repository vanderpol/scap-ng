# 0.4 value operators — explicit output cardinality, not prettier words

**18 October 2026 · Research #235 / #227 · 0.4 readability candidate, NOT approved grammar or executable Assessment.** This note tests a narrow vocabulary decision using the [complete DNS](FULL-04-dns.md) and [Apache](FULL-05-apache.md) sources. Nothing here modifies a schema, compiler, scanner, release or source Assessment. The complete alternatives remain on the linked pages; the short snippets here isolate only the value-construction question.

## Problem to solve

A first-time security auditor can see that a DNS command uses zone names, but may not know whether `concat` produces **one command string** or **multiple command strings**. Likewise, `merge` is ambiguous ordinary English: it can mean combining sets, joining strings or overwriting records. The same five-line input can mean a different security check if the collection cardinality is guessed.

Authoring clarity must distinguish **constructed values** from **collected Items** and from **Test outcomes**. The OVAL 5.12.3 [concat definition](https://oval-community-guidelines.readthedocs.io/en/v5.12.3/oval-schema-documentation/oval-definitions-schema.html#concatfunctiontype) and [merge definition](https://oval-community-guidelines.readthedocs.io/en/v5.12.3/oval-schema-documentation/oval-definitions-schema.html#mergefunctiontype) establish the source-function distinction. They do **not** alone establish how native 0.4 `independent.shellcommand` consumes those values.

## Real DNS case — three commands use the same discovered zones

All three original `concat` expressions in [DNS SV-259345](FULL-04-dns.md) place `values.object: list-all-forward-lookup-zones-object`, `field: stdout_line` between their original PowerShell prefix/suffix literals. The shortest one has this **exact source fragment**:

```yaml
# Current research representation: real IsSigned command expression
concat:
  - literal:
      value: 'try {Get-DnsServerZone -Name '
      datatype: string
  - values:
      object: list-all-forward-lookup-zones-object
      field: stdout_line
  - literal:
      value: ' | ForEach-Object {$_.IsSigned}} catch {}'
      datatype: string
```

**Candidate V1 — keep aligned vocabulary, improve documentation and nearby source visibility** (no new value operator):

```yaml
# Research illustration, not current accepted 0.4 syntax
command:
  concat:
    - 'try {Get-DnsServerZone -Name '
    - values:
        from: list-all-forward-lookup-zones-object
        field: stdout_line
    - ' | ForEach-Object {$_.IsSigned}} catch {}'
```

This retains OVAL's familiar `concat` operation but still requires an auditor to know its output is a collection when any component is multi-valued. The source reference shorthand and scalar-literal shorthand are **also proposals**, not existing accepted syntax. The current source does not define a `datatype`-free literal conversion contract here.

**Candidate V2 — name the output population**:

```yaml
# Research illustration, not current accepted 0.4 syntax
command_values:
  build_each_combination:
    - text: 'try {Get-DnsServerZone -Name '
    - values:
        from: list-all-forward-lookup-zones-object
        field: stdout_line
    - text: ' | ForEach-Object {$_.IsSigned}} catch {}'
```

`build_each_combination` is deliberately explicit about a **set of resulting strings**, not an implicit shell execution per zone. Its advantage is learnability; its disadvantage is a long and unfamiliar operator name plus a new `command_values` container. **Do not select it until a first-time author demonstrates improved comprehension.**

**Candidate V3 — string template with a named value input** (counterexample worth rejecting for now):

```yaml
# REJECT / DEFER, not executable
command_values:
  format:
    template: 'try {Get-DnsServerZone -Name {{zone}} | ForEach-Object {$_.IsSigned}} catch {}'
    inputs:
      zone:
        values:
          from: list-all-forward-lookup-zones-object
          field: stdout_line
```

Although visually compact, it introduces **escaping and placeholder collision rules** in literal shell/PowerShell text, and its notation does not say whether multiple inputs zip or form a Cartesian product. A templating layer that silently shell-escapes arguments would also change source semantics. **Do not add this complexity merely to eliminate a `concat` list.**

## Real Apache case — one joined argument string

The full [Apache SV-214228](FULL-05-apache.md) contains `merged-list-all-loaded-config-files-variable`, which uses the original `merge` function, a space delimiter and explicit order:

```yaml
# Original authored expression subtree (not a new stage)
merge:
  values:
    variable: all-loaded-configuration-filepaths-variable
  delimiter: ' '
  sort: document
  order: ascending
```

Two readable alternatives to examine in a blind first-read test:

```yaml
# V1: keep the existing OVAL-aligned operator and argument roles
merge:
  values:
    variable: all-loaded-configuration-filepaths-variable
  delimiter: ' '
  sort: document
  order: ascending
```

```yaml
# V2: explicit *one output string* intent (RESEARCH only)
join_values:
  from: all-loaded-configuration-filepaths-variable
  separator: ' '
  sort: document
  order: ascending
```

The V2 name/argument order may be easier to predict. But `join_values` must be proven to have the **same** source status, value ordering, string-conversion and provenance rules as `merge`. It must not be interpreted as a Set union, deduplication or per-file command.

## Expected answers at the **value** layer (not scanner/command counts)

| Test inputs | OVAL-source `concat` result | OVAL-source `merge` result |
| --- | --- | --- |
| One zone `east.example` + constant prefix/suffix | One constructed command string | Not applicable to the DNS command expression |
| Two zones `east.example`, `west.example` + constant prefix/suffix | **Two** command strings | Not applicable to the DNS expression |
| Two distinct value sources of 2 and 3 values | **Six** combinations, not a paired zip | Not applicable to the DNS expression |
| Apache paths `a.conf` and `b.conf`, delimiter a space | Not the authored Apache operation | **One** string `a.conf b.conf` (subject to the explicit sort/order rules) |
| Missing source Object Item, missing field, 0 values, incomplete/error/not-collected | Do **not** invent empty-string fallback; follow source component flags and OVAL status rules | Do **not** invent a successful blank config-file argument |
| One collected Item with two `stdout_line` values | Source-value expansion may yield **two strings** | A value merge yields **one** joined string |

**Critical distinction:** The constructed **value count** in this table is *not* a guarantee of equivalent scanner collector instances or effective Test outcomes. A `for_each` over collected Items is not automatically the same as `concat` over all same-name values on an Item. An unapproved shell quoting policy, per-zone implicit iteration or missing-data fallback would invalidate a lossless conversion claim.

## Decision filter — the simplest *correctly understood* operator wins

| Check | V1 `concat` / `merge` | V2 `build_each_combination` / `join_values` | V3 template |
| --- | --- | --- | --- |
| Captures distinction between many vs one output | **Yes, by normative external meaning** | **Yes, in the name** | **Ambiguous without a new expansion rule** |
| Compatible with existing OVAL terminology | Strong | Requires exact proven aliases | Weak without parser and quoting rules |
| Requires extra authoring wrappers | Not necessarily | Yes in the draft above | Yes; template and inputs |
| Safe for zero/many/error without new defaults | Only if documented result/component status remains | Only if **identical** mappings are proved | **Not yet** |
| Helps beginner predict resulting value count | Must be measured | Hypothesis, not evidence | Unknown |

**Provisional engineering preference: V1 as the control and V2 as the challenger. Defer V3.** The name itself is not the main goal: the scanner and editor must expose the value population, source flag and every downstream dependency, and an auditor must accurately explain both DNS and Apache.

### Reviewer task (not yet completed)

Before revealing the above table or OVAL definitions, show one DNS and one Apache operation and ask:

1. How many **computed values** do 0, 1, 2, and 2×3 source values yield? Distinguish uncollected from an empty-but-complete set.
2. How many **system commands** are executed? If the source does not specify, say so.
3. How does an upstream error, absent field or incomplete collection affect the result? Identify documented versus guessed behavior.
4. Can the author write another command using the same named source without guessing quoting/escaping, source typing or default aggregation?

Score wrong assumptions, lookup time and authoring correctness **separately** from preference. Compare against keeping V1 with an editor showing the expanded command/value graph. Nobody has independently reviewed these candidates yet; no canonical syntax is selected.
