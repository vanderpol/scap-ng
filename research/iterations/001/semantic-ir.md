# SCAP-NG Faithful Semantic Intermediate Representation

**Iteration:** 001  
**Status:** Architecture requirement / research design

SCAP-NG conversion should interpret SCAP 1.4 semantics once. The front end ingests datastream/XCCDF/OVAL/OCIL/CPE content and creates one faithful semantic intermediate representation (IR). Human YAML variants and canonical JSON are renderings of that IR, not independent languages.

```text
SCAP 1.4
   |
parse + resolve + source accounting
   |
faithful semantic IR
   |
   +--------------------+--------------------+
   |                    |                    |
original NG YAML   Ansible-inspired YAML   canonical JSON
   \                    |                    /
    +---------- compile/equivalence --------+
                         |
                 canonical NG semantics
```

## Conservative interpretation

The converter derives semantics supported by the source. It does not invent author intent.

When deterministic interpretation is not justified:

```yaml
migration:
  status: requires_review
  reason: ambiguous_policy_semantics
```

## IR concepts

The IR should represent benchmark/profile membership, policy text, applicability, manual Check Content, typed parameters, evidence requests, typed observations, deterministic derived values, Boolean expressions, quantifiers/cardinality, comparison operations, completeness/error semantics, result-explanation identifiers, provenance, and migration status.

A separate source-accounting tree preserves every SCAP 1.4 element/reference for loss accounting.

Deprecated OVAL tests are a deliberate exception to native semantic lowering: the IR may record them for diagnostics and provenance, but a definition referencing a deprecated OVAL 5.12.3 test is marked `unsupported: deprecated_oval_test` and is not rendered as SCAP-NG. The source SCAP 1.4 content must first be upgraded to supported OVAL.

## Renderer equivalence

For a successful conversion of one IR object:

```text
render(original YAML) -> compile -> digest A
render(Ansible YAML)  -> compile -> digest B
render(canonical JSON)-> compile -> digest C

A == B == C
```

Presentation differences are excluded from the semantic digest. Policy/applicability/collection/derivation/assertion semantics are included.

## Typed namespaces

The IR must distinguish parameters, collected evidence, derived values, and local quantifier bindings even when human-friendly aliases look similar.

Example:

```text
parameter.minimum_length
evidence.auditd_config
derive.log_directory
item.file
```

Renderers may shorten names only when aliases are deterministic and collision-free.

## Implemented OVAL coverage

The current parser has produced faithful IR for 1,333 standalone OVAL rule documents from RHEL 9, Oracle Linux 9, Windows 11, and Windows Server 2025.

The IR explicitly models:

- criteria AND/OR and negation;
- test and extended-definition references;
- test `check`, `check_existence`, and state-operator metadata;
- object, state, and variable reference graphs;
- set object references and filters;
- entity operation/datatype/variable metadata;
- fixed-point dependency edges;
- static variable evaluation when exact;
- lossless preservation of platform-specific nodes.

### Variable/function completeness checklist

The vendored OVAL 5.12.3 schema defines the following component/function set:

- `object_component`
- `variable_component`
- `literal_component`
- `arithmetic`
- `begin`
- `concat`
- `count`
- `end`
- `escape_regex`
- `glob_to_regex`
- `merge`
- `regex_capture`
- `split`
- `substring`
- `time_difference`
- `unique`

The target-independent evaluator now covers the full OVAL 5.12.3 ComponentGroup/function surface listed above, including `glob_to_regex`, `merge` ordering modes, `regex_capture`, and `time_difference` when the inputs are deterministic. A `time_difference` expression whose semantics require the evaluator's current time remains explicitly runtime-dependent rather than being assigned a fabricated static value.

Target-dependent variables are not flattened to a generic unresolved marker. Each variable has an explicit evaluation plan. Static plans carry exact values, external-input plans carry typed inputs, runtime-context plans identify dependencies such as current time, and target-dependent plans preserve the complete expression AST plus referenced objects, variables, and function operations.

The OVAL Community SCAP Self-Assertion corpus is now a separate conformance evidence source. At the pinned revision, all 144 OVAL documents across the available platform directories parse successfully with zero unresolved OVAL references. The platform-agnostic subset contains 195 variables: 194 resolve exactly offline and one remains intentionally runtime-time-dependent. Its offline verification executes 308 tests (224 true, 83 false, one unknown), with 44 definitions matching their documented expected results; one definition requires current-time context and one requires a real platform family collector.

This does **not** mean every OVAL 5.12.3 platform collector has been implemented. The schema catalog defines a substantially larger platform test/object/state surface than the Self-Assertion corpus exercises. Platform-specific payloads remain losslessly modeled in the IR, and collector/native-lowering semantics are tracked separately from structural import correctness.

### Faithful normalization versus policy review

The RHEL 9 `SV-258179` case demonstrated why the IR must precede simplification. The source contains 24 tests but only 22 unique conditions. The faithful native normalization preserves those 22 conditions and separately reports the apparent 24-cell matrix as a review candidate.

## Specification exit criterion

Before finalizing SCAP-NG:

- the pinned NIWC public corpus is source-accounted;
- every in-scope assessment maps to IR or an explicitly approved exception;
- every definition that still references a deprecated OVAL test is reported as source-remediation debt and excluded from successful NG conversion until its SCAP 1.4 source is updated;
- retained authoring renderers cover the same IR corpus;
- renderer round-trips have equivalent semantic digests;
- representative differential execution reproduces source applicability/outcome/error semantics.
