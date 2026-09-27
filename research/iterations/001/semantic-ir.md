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

## Specification exit criterion

Before finalizing SCAP-NG:

- the pinned NIWC public corpus is source-accounted;
- every in-scope assessment maps to IR or an explicitly approved exception;
- retained authoring renderers cover the same IR corpus;
- renderer round-trips have equivalent semantic digests;
- representative differential execution reproduces source applicability/outcome/error semantics.
