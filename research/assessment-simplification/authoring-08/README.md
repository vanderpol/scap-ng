# Authoring locality and OVAL-feature usage census

**Status:** quantitative research checkpoint, 2026-10-06. No schema or accepted
language change.

## Question

Is SCAP-NG still difficult to read primarily because faithful OVAL-style
Objects, States, Variables and Tests are authored as separate named graph nodes,
even when those nodes are used only once?

This pass measures the current faithfully converted YAML before normalization.
It is an authoring-topology study, not a claim that every structurally local
graph can already be rewritten without an equivalence proof.

## Production sample

Pinned NIWC source revision:
`8c8e5dff860af6b1290ee9273a282db24278f8d5`.

Representative Board conversion workflow:
https://github.com/vanderpol/scap-ng/actions/runs/37518894481

Benchmarks:

- RHEL 9
- Oracle Linux 9
- Windows 11
- Windows Server 2025
- Apache 2.4 UNIX Server
- Apache Tomcat 9

The six benchmarks contain 1,565 Rules. 1,355 Rules reference OVAL automation;
210 do not. Tomcat 9 has no OVAL-automated Rules in this pinned package.

Feature metrics below analyze **1,350 generated automated Assessment YAML files**
from the six pre-normalization conversion artifacts. The five-file difference
from the 1,355 Rules with OVAL reflects reuse/conversion identity and is not
treated as five missing Rules.

## Primary result: named Object/State nodes are usually not reused

Across the 1,350 automated Assessments:

- 2,257 Objects
- 1,704 States
- 451 Variables
- 2,051 Tests

Reference topology:

| Node | Exactly one reference | Exactly one Test consumer |
| --- | ---: | ---: |
| Objects | 2,161 / 2,257 = **95.75%** | 1,744 / 2,257 = **77.27%** |
| States | 1,535 / 1,704 = **90.08%** | 1,462 / 1,704 = **85.80%** |
| Variables | 355 / 451 = **78.71%** | n/a |

Only about 4.3% of Objects and 7.3% of States are actually referenced more than
once. Therefore top-level naming/reference syntax is usually not buying reuse.

The most common Object consumer is a Test only (1,783 Objects). The most common
State consumer is a Test only (1,545 States). Object graph/set use and
Object-to-Variable extraction are important, but they are the minority shapes.

## Assessment-level locality

A deliberately conservative structural classifier found:

- **53.11%** are the simplest form: one Test, one Object, zero or one State,
  no Variables/Sets/Filters and a direct `evaluate: test`.
- **77.63%** have Test-local Object/State references, no internal sharing and
  no Variables/Sets/Filters. These are strong candidates for an inline
  collection + expectation authoring form.
- **83.19%** use no Variables, Sets or Filters at all.
- only **12.00%** contain any reused Object, State or Variable node.

These percentages establish structural locality only. A future compiler still
needs exact semantic tests for any promoted inline grammar.

## Tests and expectations are usually small

Of 2,051 Tests:

- 637 (**31.06%**) reference no State;
- 1,241 (**60.51%**) reference exactly one State;
- 173 (**8.43%**) reference two or more States.

Therefore **91.57% of Tests use zero or one State**.

Of 1,704 States:

- 1,369 (**80.34%**) contain one predicate;
- another 282 contain two predicates;
- **96.89%** contain one or two predicates.

This strongly supports an authoring shape where the expectation is local to the
check rather than a separately named State by default.

## Boolean evaluation is usually shallow

Assessment evaluation roots:

- direct Test: 976 (**72.30%**)
- `all`: 249
- `any`: 120
- `not`: 5

**95.48%** of Assessment evaluate trees have depth <= 2.

A task/check-oriented language therefore does not need to expose an OVAL-like
criteria graph for most content. A direct check plus shallow `all`/`any`
composition covers the overwhelming majority of current converted shapes.

## Variables and function algebra are a minority

Assessment-level feature use:

- any Variable: **9.26%**
- any Variable function: **5.11%**
- any Set: **8.15%**
- any Filter: **2.07%**
- direct Object-field projection Variable: **2.07%** of Assessments
- shellcommand capability: **5.85%** of Assessments

451 Variables occur in the sample. 355 (78.71%) are referenced once.

Observed Variable expression roots include:

- concat: 205
- regex_capture: 77
- literal: 62
- direct values/Object extraction: 35
- merge: 34
- unique: 16
- split: 10
- count: 10
- arithmetic: 2

Nested-function counting raises regex_capture to 117 and unique to 22.

### Apache is a major complexity concentration

The 22 Apache 2.4 automated Assessments are only **1.63%** of the 1,350-file
sample, but all 22 use shellcommand, Variables and Variable functions.

They contain:

- 282 / 451 Variables = **62.53%** of all Variables in the sample;
- 163 / 205 concat occurrences = **79.51%**;
- 102 / 117 regex_capture occurrences = **87.18%**;
- 33 / 34 merge occurrences = **97.06%**;
- 16 / 22 unique occurrences = **72.73%**.

This is direct evidence that a very small content family can drive a
disproportionate amount of language/dataflow complexity.

It does **not** prove that those Apache checks should simply become arbitrary
shell commands. Several perform configuration/include discovery, and project
policy deliberately preserves filesystem searching/traversal in native scanner
capabilities. The result instead argues for revisiting the observation method:
inline authoring, reusable Apache observation helpers, or revised checks may be
better than carrying the full source graph forward.

Excluding Apache 2.4, only **3.54%** of the remaining automated Assessments use
Variable functions.

## Capability concentration

The 2,051 Tests are dominated by a small number of observation types:

| Capability | Tests | Share |
| --- | ---: | ---: |
| independent.textfilecontent54 | 795 | 38.8% |
| windows.registry | 292 | 14.2% |
| unix.file | 155 | 7.6% |
| windows.auditeventpolicysubcategories | 143 | 7.0% |
| independent.shellcommand | 132 | 6.4% |
| windows.userright | 92 | 4.5% |
| linux.rpminfo | 68 | 3.3% |
| unix.sysctl | 66 | 3.2% |
| linux.partition | 64 | 3.1% |
| windows.wmi.query | 54 | 2.6% |

This resembles a module/task ecosystem more than a need for authors to manipulate
a general graph in every check.

## What this says about Ansible-like authoring

The useful Ansible analogy is **locality**, not copying Ansible syntax literally.

Ansible normally gives the author a task with:

- one module/action;
- its arguments beside it;
- a local loop/condition when needed;
- registered Variables only when output must be reused;
- roles/includes for real reuse.

A corresponding SCAP-NG authoring model could make the common form:

```yaml
check:
  capability: unix.file
  select:
    path: /etc
    filename:
      matches: '^cron.*'
  traverse:
    direction: down
  expect:
    existence: one_or_more
    every:
      group_id: 0
```

instead of requiring separate Object, State and Test IDs plus a one-node
`evaluate` wrapper.

A plain scalar such as `group_id: 0` can have a specification-defined meaning
of typed equality because the capability schema fixes the field type. That is an
intrinsic grammar rule, not an unspecified hidden default. Non-equality
comparisons remain explicit.

Named reusable Objects/observations, expectations and Variables should remain
available, but the measurements suggest they should be the **escape/reuse form**,
not the mandatory common form.

## Example from the production conversion

RHEL 9 SV-257927 currently expands a straightforward rule into separate
`objects`, `states`, `tests` and `evaluate` sections:

- select cron files under `/etc`;
- require at least one;
- require every selected Item to have `group_id == 0`.

The security meaning is naturally one local check. The graph nodes add identity
and indirection but no reuse in that Assessment.

A Windows registry example shows the same pattern: select one registry value,
allow the missing case according to the original existence semantics, and require
its type/value. Keeping the selector and expectation together reads much closer to
the STIG requirement.

## Reuse belongs at a different level

The normalized six-benchmark Board build reduced 2,962 referenced Assessment
instances to 2,415 exact Assessment definitions, avoiding 547 duplicate
definitions (**18.47% reduction**).

That is useful reuse, but it is mostly **whole-Assessment reuse across policy
content**, not evidence that every internal Object/State should be globally
named.

This suggests two different design layers:

1. task-local collection/expectation for ordinary authoring;
2. named reusable Assessment/observation components when actual reuse exists.


## Raw OVAL cross-check

The converted-YAML census was cross-checked against exact per-Rule OVAL
closures generated from the same pinned six NIWC packages.

Workflow:
https://github.com/vanderpol/scap-ng/actions/runs/37526567764

Across **1,355 OVAL-backed Rules**:

- Variables: **9.30%**
- Variable functions: **5.17%**
- Sets: **8.12%**
- Filters: **4.80%**
- ObjectComponent: **6.57%**
- VariableComponent: **1.85%**
- entity `var_ref`: **8.34%**
- multiple Tests: **27.38%**
- criteria depth greater than 2: **0.37%**
- shellcommand Test: **6.05%**

The close agreement with the converted-YAML percentages is important: the
small complex tail is present in the source OVAL itself rather than being
created by the converter.

Raw per-platform function use is also highly skewed. Apache 2.4 has 22
OVAL-backed Rules and all 22 use Variables, Variable functions,
ObjectComponent/VariableComponent and shellcommand. By contrast:

| Benchmark | Variables | Functions | Sets | Filters |
| --- | ---: | ---: | ---: | ---: |
| RHEL 9 | 10.05% | 4.07% | 10.77% | 5.02% |
| Oracle Linux 9 | 9.31% | 3.68% | 10.78% | 5.39% |
| Windows 11 | 4.07% | 2.85% | 5.69% | 4.07% |
| Windows Server 2025 | 5.36% | 3.45% | 2.68% | 4.60% |
| Apache 2.4 UNIX Server | 100% | 100% | 0% | 0% |

This does not mean every Rule without a Variable function is trivial. It does
show that preserving the full OVAL function/dataflow language for every author
would make the common case pay for features concentrated in a small minority.

## Current conclusion

The initial data supports the owner's intuition: external Object/State placement
is probably one of the largest reasons current NG still feels OVAL-like.

The bigger problem is not only names. Current source also exposes:

- `operation + datatype + value` predicate boilerplate where capability typing
  could provide a smaller explicit shorthand;
- a separate Test and `evaluate` node even when one Test is the entire policy;
- one-use Variables used as dataflow plumbing;
- graph composition as the default mental model rather than a local
  observe/select/expect task.

A much more Ansible-like **authoring surface** can therefore plausibly cover the
majority of real content while compiling to the rigorous semantic graph.

The raw OVAL cross-check now confirms the feature-frequency measurements, but
this census still does **not** establish a percentage of OVAL that a smaller
standard may safely refuse. The next classification should assign every
automated Rule to the minimum *authoring* feature needed: local task, shallow
composition, local loop/binding, Set/exclusion, reusable observation,
function/dataflow, or content redesign/review candidate. That classification,
not raw XML feature presence alone, is the appropriate basis for a proposed
90/95/99-percent migration target.
