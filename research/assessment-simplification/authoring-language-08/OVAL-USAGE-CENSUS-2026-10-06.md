# Authoring locality and OVAL complexity census — 2026-10-06

**Status:** production-source research evidence; not a language decision.

This study asks a different question from SCAP 1.4 conversion completeness:

> How much of the complexity visible in OVAL/SCAP-NG authoring is required by
> real assessment semantics, and how much comes from graph-oriented
> serialization such as separately named Objects and States?

The result is intended to inform the next SCAP-NG authoring-language discussion,
including whether the primary human syntax should be substantially more
Ansible-like while a richer semantic IR remains available underneath.

## Production sample

Pinned NIWC Atlantic revision:

`8c8e5dff860af6b1290ee9273a282db24278f8d5`

Eight representative Current packages were measured:

- RHEL 9
- Oracle Linux 9
- Windows 11
- Windows Server 2025
- Solaris 11 x86
- Microsoft Windows Server DNS
- Apache 2.4 UNIX Server
- Apache Tomcat 9

Apache Tomcat 9 contributes no OVAL-backed automated Rules in this package, so
the quantitative OVAL population is **1,537 automated Rules** across the other
seven packages.

Workflow:
https://github.com/vanderpol/scap-ng/actions/runs/37525660271

The census tool is
`tools/measure_oval_authoring_complexity.py`.

## Main result: locality is a major opportunity

Across the 1,537 automated OVAL-backed Rules:

| Measure | Result |
| --- | ---: |
| Direct Test -> Object references used only once in the Rule closure | **88.5%** |
| Direct Test -> State references used only once in the Rule closure | **87.5%** |
| Rules with no Object/State reuse barrier inside the Rule closure | **82.8%** |
| Simple single-Test/local-component candidates | **51.8%** |
| Local-readable candidates allowing multiple Tests | **69.0%** |
| Rules with genuine dataflow complexity | **19.3%** |
| Rules with evaluation-structure complexity | **39.8%** |

This is strong evidence that separately naming every Object and State is often
not required for reuse. For most direct Test relationships, the Object or State
exists only to serve that Test.

That does **not** prove every such component should always be inlined. It does
show that an authoring language that requires all of them to live in separate
top-level maps imposes indirection in many cases where source reuse does not
require it.

## What “dataflow complexity” means here

A Rule is counted as dataflow-complex when its reachable OVAL graph uses one or
more of:

- Variables;
- Sets;
- Filters; or
- Variable functions.

Only **296 / 1,537 = 19.3%** of the representative automated Rules fall into
that category.

Observed Rule-level feature frequency:

| Feature | Rules | Percent |
| --- | ---: | ---: |
| Variable | 181 | 11.8% |
| Set | 130 | 8.5% |
| Filter | 85 | 5.5% |
| object_component | 138 | 9.0% |
| concat | 85 | 5.5% |
| regex_capture | 31 | 2.0% |
| variable_component | 27 | 1.8% |
| merge | 20 | 1.3% |
| unique | 22 | 1.4% |
| split | 11 | 0.7% |
| count | 8 | 0.5% |
| arithmetic | 2 | 0.1% |
| substring | 1 | 0.1% |

So the full Variable/function machinery is important, but it is not the normal
case for most production Rules.

## Evaluation complexity is more common than dataflow complexity

The Rule-level evaluation surface is richer:

| Feature | Rules | Percent |
| --- | ---: | ---: |
| Multiple Tests | 472 | 30.7% |
| Multiple States on a Test | 174 | 11.3% |
| Nested criteria | 114 | 7.4% |
| Negation | 47 | 3.1% |
| Existence-only Test | 396 | 25.8% |

This suggests that a simpler authoring language still needs a clean way to say
things such as:

- all of these checks;
- any of these checks;
- not this check;
- exactly/at-least/none existence requirements; and
- several expectations against one collected population.

It does **not** imply that authors need to see an OVAL-style Object/State/Test
graph to express those semantics.

## Extend-definition appears overwhelmingly to be authoring indirection

A refined structural classification of the same representative corpus found
**1,267** reachable `extend_definition` occurrences:

| Form | Occurrences |
| --- | ---: |
| Pure one-hop wrapper | **1,217 (96.1%)** |
| Multiple extends and no direct Test criteria | 16 |
| Extend plus direct Test criteria | 29 |
| Extend plus nested criteria | 5 |
| Negated extend | **0** |

This strongly supports treating `extend_definition` as source/publication
indirection rather than a first-class human-authoring requirement.

The remaining 50 occurrences still need semantic review before claiming that
100% can be erased mechanically. Even if their Boolean meaning must be
preserved in the semantic IR, nothing in this census shows that an NG author
needs to write an `extend_definition` construct. Their meaning may be better
rendered directly as ordinary `all` / `any` composition in a simplified
authoring layer.

## OVAL indirection is not the same thing as security-check complexity

`extend_definition` appears in **80.9%** of the measured Rules.

The first census incorrectly treated this as advanced authoring complexity.
That was misleading. In this production content, extend-definition frequently
acts as publication/reuse indirection between a product-specific Definition and
a shared Definition. The refined complexity metrics therefore report it
separately instead of treating it as evidence that the security requirement
itself needs a complex authoring form.

This distinction is important for SCAP-NG: a lossless migration IR may need to
understand source Definition composition without requiring the normal author to
write that structure.

## Existing shellcommand use is not rare

**188 / 1,537 = 12.2%** of the Rules reach at least one shellcommand Test.
There are 364 shellcommand Test occurrences in the measured dependency
closures.

This is evidence that command-oriented assessment is already an established
part of the NIWC production corpus. It is **not** evidence that every complex
graph should become a shell command. Native collectors remain valuable where
they provide scanner-aware acquisition semantics such as filesystem scope,
typed Items, collection status, and bounded evidence.

A later study should classify complex Rules into:

1. clearer as native structured collection/expectation;
2. clearer as a command-oriented check;
3. genuinely needs richer dataflow; and
4. content that should be redesigned rather than mechanically preserved.

## Platform variation

| Platform | Rules | Simple local single-Test | Local incl. multi-Test | Dataflow complex | No Object/State reuse barrier |
| --- | ---: | ---: | ---: | ---: | ---: |
| RHEL 9 | 418 | 55.7% | 72.5% | 20.8% | 89.0% |
| Oracle Linux 9 | 408 | 57.4% | 72.5% | 20.3% | 88.7% |
| Windows 11 | 246 | 50.0% | 69.9% | 10.2% | 78.0% |
| Windows Server 2025 | 261 | 53.6% | 74.3% | 8.4% | 80.1% |
| Solaris 11 x86 | 141 | 44.7% | 63.1% | 16.3% | 85.8% |
| Windows Server DNS | 41 | 7.3% | 14.6% | 82.9% | 26.8% |
| Apache 2.4 UNIX Server | 22 | 0.0% | 0.0% | 100.0% | 22.7% |

DNS and Apache are intentionally useful counterexamples. They show why SCAP-NG
still needs an advanced path even if the default authoring path is greatly
simplified.

## Preliminary authoring implication

The data supports testing an authoring model in which the common case reads
approximately as:

```yaml
check:
  collect:
    capability: unix.file
    directory: /etc
    name: sshd_config

  expect:
    owner_uid: 0
    group_id: 0
    mode:
      no_more_permissive_than: "0644"
```

rather than requiring the author to define and cross-reference three independent
top-level structures solely because the underlying evaluator internally has
Object/State/Test concepts.

Named reusable components could remain available when they are actually reused:

```yaml
collections:
  local-users:
    ...

checks:
  ...
```

The important architectural possibility is therefore:

```
human authoring language
    -> typed semantic IR
        -> collector/evaluator
```

The semantic IR can retain rigorous Object/State/Variable/Test-like distinctions
for conversion, proof, optimization, and result semantics without forcing the
normal authoring surface to expose all of them.

## Limits

These results should not be interpreted as “82.8% of OVAL can be deleted.”

- Reuse counts are measured **within each Rule dependency closure**. Cross-Rule
  source reuse is not yet included.
- “Single-use” is a locality signal, not proof that inlining always improves
  readability.
- The study measures OVAL graph structure, not scanner runtime complexity.
- It does not yet judge whether a complex Rule is a good shellcommand candidate.
- It does not compare concrete Ansible-like syntax against the current NG YAML
  line-by-line.
- It does not yet distinguish every form of ordinary collection behavior from
  author-visible complexity.
- Apache Tomcat 9 has no OVAL-backed automated Rules in the measured package.

## Next bounded study

Before changing the 0.3.0 language, use representative Rules from four buckets:

1. simple single-Test/local Object+State;
2. local multi-Test evaluation;
3. genuine Variable/Set/Filter dataflow;
4. DNS/Apache high-complexity graphs.

For each Rule, render three side-by-side representations:

- source OVAL graph;
- current SCAP-NG YAML;
- a deliberately Ansible-like `collect / expect / evaluate` form.

Then measure conceptual hops, named component count, lines, repeated metadata,
and whether the simplified form preserves all required result/evidence
semantics.

That comparison should be reviewed with DISA content developers and the OVAL
Board before broadening the 0.3.0 authoring grammar.
