# Reviewer triage — Gemini excerpt and ChatGPT first-read (17 Oct 2026)

**Issue #235. User-supplied reviewer outputs.** Neither normative language decision nor runtime parity proof.

## Limits

- Gemini submission covers Samples A–F and scenarios, then stops at the header **Part 3: Design Stress Test**. Actual Part 3 has not been provided.
- ChatGPT reviewer disclosed **prior SCAP-NG context**. Treat as careful restricted-input first reading, not a fully independent blind review.
- The packet headings reveal A = required, B = optional, C = explicit empty, D = existence; its samples A/B/E intentionally omit mandatory current-prototype if_empty and D uses unapproved require_at_least_one. Scores concern the experiment, not a passing source file or a proven implementation.

## Cross-review agreement

| Area | Gemini | ChatGPT | Implication |
| --- | --- | --- | --- |
| where / must / every with actual resources | Understandable | Understandable | Retain clean scoped resource checks |
| Complete zero selected A/B | Cannot determine | Cannot determine | Identical syntax cannot represent conflicting existence policies |
| C/D | Explicit qualifiers clarify zero | Positive existence clearer than evaluator if_empty | Test affirmative counts |
| Missing and inaccessible fields | Cannot determine | Cannot determine; unreadable selector can conceal qualifying Item | Need status and typed selector contract |
| Incomplete collection | Cannot determine | Incomplete is not complete empty; violation may be decisive | Six-state/evidence sufficiency is not author boilerplate |
| Nested E | Bindings and provider uncertain | Shared directory, aliases, traversal and identity ambiguous | Versioned provider + lexical references |
| F Windows alternatives | Low confidence, deep logic tiring | Medium confidence; logic understood, principal evidence uncertain | Named alternatives and inspectable checks |
| Status | No actual Part 3 received | Complete report | Do not infer missing Gemini recommendations |

## New high-value reviewer observations

1. What is empty? A successful source enumeration with zero raw Items vs a successful source enumeration containing Items but zero matches after where. The language must name the population and preserve source completeness.
2. An unreadable selector field must not silently discard an Item as a known nonmatch.
3. The prototype currently overloads none: zero selected resources when no must is given; zero matching must predicates otherwise. Exactly-one likewise needs a fixed selection vs satisfaction counting rule. Neither should be implicit.
4. A two-user shared directory is a direct adversarial test of scoped references; following a per-user reference is not just substituting a string.
5. The word under must have specified recursion, symlink and boundary semantics, not merely an attractive English name.
6. Heading "optional population" provided context the YAML did not. Next blind trial must anonymize headings, paths, titles and result hints where practical.

## Falsifiable alternative A: affirmative minimum count

~~~yaml
require:
  each: linux.mounts
  where:
    mount_point: {equals: /home}
  minimum_resources: 1
  must:
    mount_options: {contains: nosuid}
~~~

A known-complete zero fails only when minimum_resources requires one or more. Without it, each applies to the existing selected population, so zero known-complete Items passes. That must be an explicit documented meaning of each, not an inferred scanner default.

## Falsifiable alternative B: required singleton resource

~~~yaml
require:
  resource: linux.mount
  at: /home
  must:
    mount_options: {contains: nosuid}
~~~

A typed provider would explicitly identify that single mount and its absence status. Risk: cardinality and namespaces get silently hidden inside a provider.

## Falsifiable alternative C: policy sentence plus source mapping

Human policy can read like a sentence while the actual machine contract separately specifies versioned typed selection, identity, field/record grouping and collection statuses. **Free text is not executable policy**; require a typed structured representation.

## Decision gates

Compare required /home mount absent -> Fail versus optional guest accounts absent -> Pass, both on complete populations. Also try 2 Items/one match, missing and unreadable selector attributes, incomplete collection with a decisive failure, no observed Items under incomplete, shared home directories, exactly-one selected vs exactly-one compliant, and whole-State mixed WMI records. Do not call shorter source-level sketches equivalent to old SCAP 1.4 without an actual provider contract and regression counterexamples.

**Tentative:** trial affirmative resource counts and inspectable typed providers. Keep original candidate, revised variants and source mapping independent until review. Do not change normative 0.4 schema or claim scanner parity.
