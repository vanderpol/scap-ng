# 0.4-C — Should a derived value contain a private Object?

**19 October 2026 · issue #245 · research recommendation; not approved 0.4 syntax or an OVAL runtime parity claim.**

## Verdict: Yes, conditionally — but do not invent another Variable subsystem

An existing A/0.3-style `Variable.expression.values.object` can already contain a private acquisition. In the real Apache **SV-214268** source, a Variable uses a shell-command Object to read `stdout_line` and then regex-captures a path. This represents one human intent: **derive the Apache executable path from collected process output**. Authors should not need to manage an otherwise-unused Object name just to express that operation.

**Prefer the concept, not the name.** In the eventual single C frontend, a named *derived value* may own its private acquisition and transform. That acquisition remains a typed A-compatible Object in the one internal execution graph. **No second parser dialect, implicit default, hidden collector or extra scanner is justified.** This is a presentation/authoring hypothesis until source-backed lowering is independently proved.

For a private value, a proposed *read-only authoring view*, **not currently compiled C syntax**, would convey:

```yaml
derived_values:
  apache-executable-paths:
    description: Executable paths found in Apache process commands
    acquire: {capability: independent.shellcommand, collect: "(full original source command and flags)"}
    read_field: stdout_line
    transform: {regex_capture: "(original source expression)"}
    # One or many typed values; do not assume a singleton
```

The editor can display the `acquire` detail on demand, but it **must** preserve the exact command, shell, regex, error flags, source Item IDs, individual value provenance, result multiplicity, and intermediate error/unknown states. This is not license to replace shell discovery with an imagined Apache provider or reinterpret the source regex.

## Four author-facing shapes, one internal typed graph

1. **Simple literal or bound organizational input:** place it directly where consumed; do not manufacture a Variable.
2. **Private acquired derived value:** one named, described derived step may contain a typed Object + field extraction + transform. Do not invent a separate *shared* Object unless source reuse and collection identity warrant it.
3. **Reusable observation or derived value:** give it a meaningful stable identity; show who consumes it and its scope. Keep *collected Items* separate from *transformed values* and *Test truth*. A consumer with a different cardinality rule must not inherit someone else's outcome.
4. **Complex source graph:** Sets, include/exclude Filters, nested per-parent foreach, dynamic selectors, records and multi-branch Variables remain fully explicit in the typed compatibility graph. Present a guided summary, **not** an unproven flattening that alters eligible Items or six-state outcomes.

The key discriminator is **ownership of the evidence and its population**. An inline Object is private to the derived computation; a named shared Object can be referenced across checks. Content-equal collection descriptors do **not** automatically prove equivalent runtime acquisition or permission/snapshot scopes.

## Real counterexamples

- **Apache SV-214268:** the 19 source Variables include direct inline command readers *and* command strings built from other Variables. The latter must show their upstream dependencies; the source uses distinct main/included and runtime-loaded configuration file populations. Inlining all 19 would conceal or duplicate important work.
- **RHEL 9 SV-257889:** home directories are derived from two distinct account Sets with filters, and the two permission Tests have different absence/existence requirements. The eight permission bits do not justify collapsing Set/Filter selection or merging root and non-system-user populations.
- **Any Object reused in a Filter:** a filter determines Item membership before Test requirements are applied. Display-only abbreviations may be safe, but turning the filter into an assertion, or sharing a Filter State as if it were only a Test State, is not.
- **Multiple results, duplicates, missing fields, incomplete/error:** `read stdout_line` is a typed value sequence with provenance, not automatically one string or success. Reordering, deduplicating, or converting incomplete to complete-empty can change outcomes.

## Executable gate now in the repository

[Read-only scope audit](../../../tools/research_c_private_value_sources.py) validates A's source-dataflow graph, inventories private `values.object` acquisition nodes versus named-Object references, flags dynamic collection arguments and complex population constructs, preserves full source digests and Variable titles/types, and refuses tampered source views. The [focused tests](../../../tools/test_research_c_private_value_sources.py) include the pinned full 19-Variable Apache specimen and adversarial nested Set/Filter, shared-Object, dynamic-command, multi-source and changed-expression cases. The [C workflow](../../../.github/workflows/research-c-shared-engine.yml) runs those tests and reports actual Apache category counts.

**What this proves:** where a simpler primary authoring *view* can preserve every source reference and where it must expose a dependency. **What it does not prove:** native C compilation of this view, reductions in runtime commands, equivalence of the 19-Variable evaluation graph, complete SCAP 1.4 Set/Filter semantics, OVAL scanner results, or a new accepted language feature.

## Next meaningful experiment

Compare the private-derived-value view and the current A source for one real Apache Variable that owns an Object, then for a dynamic-command Variable with a nested Object. Require (1) exact source-object/variable/selector hashes and identity, (2) independent typed value outcomes on complete/empty/incomplete/error evidence, (3) unchanged downstream Test existence, matching and trace, and (4) a blind auditor explanation of which population supplies which value. If these checks fail, **keep the original explicit graph instead of adding syntactic sugar**.

**Recommendation:** retain *Objects contained within derived values* as a conditional first-class **C authoring convenience**, not a mandatory extra declaration or an automatic source optimizer. Do not promote without actual source-backed compilation and semantics proof.
