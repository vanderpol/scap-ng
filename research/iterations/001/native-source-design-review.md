# Native SCAP-NG Source Design Review

**Status:** active design checkpoint  
**Decision:** pause benchmark expansion and large-scale regeneration until the
native authoring source is understandable, concise, and agreed.

## Why this checkpoint exists

The fidelity-first conversion proved that real SCAP 1.4 content can be parsed,
accounted for, and lowered into a common semantic model across Linux and
Windows.

It also exposed a problem: the generated YAML remains too close to the source
XCCDF/OVAL/OCIL representation. It is large, mechanically detailed, and can be
misread as the intended long-term SCAP-NG authoring experience.

That is not acceptable as a basis for a new specification.

The next phase therefore optimizes for **native author comprehension and
maintainability**, while preserving the semantic fidelity work as migration
evidence.

## Freeze

Until this review is complete:

- do not add more benchmark families merely to increase coverage;
- do not treat fidelity-first converted YAML as candidate normative syntax;
- do not optimize for 100% corpus rendering volume;
- do not let legacy XCCDF/OVAL/OCIL structures dictate the native source model;
- keep the four-anchor conversion workflow manual-only;
- continue preserving the canonical semantic IR and migration provenance.

## Review corpus

Use a deliberately small set of representative rules.

### Linux

1. **RHEL 9 simple rule — SV-257777r1155676**
   - ordinary Linux assessment;
   - useful baseline for readability and file size.

2. **RHEL 9 complex rule — SV-258179r1155601**
   - multiple definitions/tests/objects/variables;
   - known duplicate source semantics;
   - useful stress case for Boolean logic, collection reuse, and complex
     variable/data flow.

### Windows

3. **Windows 11 simple rule — SV-253273r1051040**
   - ordinary Windows assessment;
   - baseline for registry/security-policy style content.

4. **Windows 11 merge rule — SV-253363r971535**
   - registry multi-string collection;
   - target-dependent `object_component`;
   - OVAL `merge`;
   - strong example for deciding whether NG needs a simpler typed collection /
     join operation.

5. **Windows 11 concat rule — SV-253340r958434**
   - target-dependent registry collection;
   - `object_component`;
   - `regex_capture`;
   - `concat`;
   - file effective-rights collection;
   - strong example for simplifying data-flow expressions without weakening
     semantics.

6. **Windows manual rule**
   - choose one current Windows 11 rule whose automated path is absent or
     intentionally manual;
   - use it to define an NG-native manual procedure without OCIL runtime
     concepts.

7. **Windows applicability example**
   - use the Windows Member Workstation platform;
   - express native platform/applicability semantics without XCCDF/CPE/OVAL
     runtime references.

## Required views for each automated review rule

For each rule, maintain four side-by-side artifacts:

1. **Original SCAP 1.4 source**
   - XCCDF rule/check;
   - standalone OVAL closure;
   - provenance.

2. **Faithful semantic IR**
   - exact machine-understood meaning;
   - source identifiers allowed;
   - used as the migration/conformance reference.

3. **Proposed native NG source**
   - hand-designed for human authors;
   - no XCCDF/OVAL/OCIL runtime concepts;
   - meaningful NG-local names;
   - concise typed data flow;
   - only semantic detail necessary to produce deterministic results.

4. **Resolved canonical semantics**
   - machine-normalized form used to prove that the compact native source means
     the same thing as the faithful IR.

The authoring source does **not** need to expose every detail of the resolved
canonical form.

## Native source design goals

A content author reading one assessment should be able to answer quickly:

- What is being collected?
- What values are derived?
- What condition is being tested?
- What result causes pass/fail/not-applicable/error?
- What parameters may vary?
- What other rules reuse this assessment?
- What platform is it applicable to?

The answer should not require understanding OVAL object/state/test identifiers.

### Prefer intent over source mechanics

Prefer concepts such as:

    collect:
      system_root:
        windows.registry:
          hive: HKLM
          key: SOFTWARE\Microsoft\Windows NT\CurrentVersion
          value: SystemRoot

over constructs that expose:

    source_object_id: oval:...
    source_namespace: ...
    query:
      - kind: element
        ...

### Use meaningful local names

Prefer:

    system_root
    event_log_path
    unauthorized_trustees

instead of:

    oval:mil.disa.stig.win:obj:20000015
    oval:mil.disa.stig.win:var:25334001

Source IDs remain available in migration provenance.

### Make data flow explicit but compact

A complex derivation may need multiple operations, but the common case should
read like a typed data pipeline rather than a generic XML-expression AST.

Conceptual example:

    derive:
      application_log_path:
        concat:
          - ref: system_root.value
          - regex_capture:
              input: application_log_setting.value
              pattern: '^%.*%(.*)$'

This is only a design sketch. The review should determine exact syntax,
cardinality rules, and whether higher-level transforms can simplify this
further.

### Separate authoring syntax from evaluator semantics

The source language may provide concise forms, while the canonical semantic IR
expands them into explicit behavior for:

- zero/one/many collected values;
- ordering;
- uniqueness;
- missing values;
- datatype conversion;
- regular-expression cardinality;
- Boolean aggregation;
- collection errors;
- unknown/not-evaluated states.

Authors should not have to restate defaults that are stable and obvious, but
those defaults must be normative.

## Questions to settle before scaling again

### Policy

- What is the minimum required rule metadata?
- Which STIG/XCCDF metadata belongs as ordinary descriptive metadata?
- How are profiles and parameters represented?
- How does a policy rule bind to a reusable assessment?
- How are manual and automated alternatives represented?

### Applicability

**Working design rule:** applicability is ordinary NG assessment logic used in
an applicability role. Anything supported by the assessment portion of the
language is eligible for applicability.

The content author owns the determination. The scanner must not infer or
normalize a platform into an opinionated `os_info` object and thereby decide
what the target "is" on behalf of content.

A platform definition should therefore bind a human/standard identifier to an
explicit NG assessment. That assessment can use the same collectors,
derivations, predicates, existence/cardinality rules, Boolean logic, and error
semantics available to compliance assessments.

The scanner's responsibility is limited to stable, well-defined collection
capabilities. The content author combines those raw facts into applicability.

This preserves a key SCAP 1.4/OVAL property: content for a new, obscure, or
custom platform can be authored without waiting for scanner vendors to add a
special platform-recognition feature. For example, Linux Mint or a custom
distribution could be identified using ordinary file/package/kernel collectors
and authored logic over `/etc/os-release`, release files, package metadata, or
any other supported assessment evidence.

CPE may remain a standard identifier/dictionary name, but CPE alone does not
produce truth. A CPE/platform name used by policy must ultimately be backed by
explicit NG applicability assessment logic.

Questions still to settle:

- How are reusable platform definitions named and referenced?
- Should applicability assessments return strictly Boolean, or the normal NG
  result algebra with a defined conversion to applicable/not-applicable/error?
- How should multiple applicability assessments combine?
- Which common applicability patterns deserve concise authoring shortcuts
  without reducing the underlying assessment power?

### Collection

- What are the native collector capability names?
- Should common platforms expose typed fields rather than generic entity lists?
- How are collection cardinality and collection errors represented?

### Derivation / variables

- Which OVAL variable operations are genuinely necessary primitives?
- Which can be represented as ordinary typed transforms?
- Which common OVAL patterns deserve purpose-built NG syntax?
- Should `merge` mean collection flattening, string joining, or be split into
  distinct operations?
- Should `concat` operate only on scalars, with explicit mapping/reduction for
  collections?
- How should ordering and cartesian-product behavior be specified?
- Can object-component/variable-component disappear entirely in favor of normal
  references?

### Evaluation

- Can tests/states be collapsed into direct assertions for common cases?
- When is an explicit intermediate predicate useful?
- How are existence semantics expressed without reproducing OVAL's test model?
- How are multi-value predicates combined?

### Reuse

- What is the stable identity of a reusable assessment?
- What may policy overlays change?
- How are parameters typed?
- How does Git make reuse and provenance obvious?

### Manual checks

- What is the native manual procedure model?
- Do we need structured questions/answers, or is a procedure plus expected
  evidence sufficient for the initial spec?

## Exit criteria

Resume broad corpus generation only after we can take the review examples and
say all of the following:

- a human can understand the native source without learning XCCDF/OVAL/OCIL;
- simple rules are genuinely simple;
- complex rules are no more complex than their actual semantics require;
- legacy provenance is separate and clearly non-normative;
- all review examples round-trip to the faithful canonical semantics;
- reusable assessments are obvious in Git;
- the same semantics can be packaged without legacy runtime dependencies;
- the Board-facing source no longer looks like SCAP 1.4 serialized as YAML.

Only then should the converter regenerate the four anchors and expand to the
larger corpus.
