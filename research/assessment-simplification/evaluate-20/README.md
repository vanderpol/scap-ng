# Evaluate / criteria placement research

**Status:** research only; tracked by #167.

## Question

SCAP-NG currently requires every automated Assessment to have both named
`tests` and a separate root `evaluate` expression. Source presentation
guidance places `evaluate` last.

This research asks:

1. is a separate `evaluate` node necessary for every Assessment?
2. can simple Test composition be authored more locally?
3. when a real decision tree exists, should `evaluate` remain first-class?
4. if retained, is it more useful near the top as an executable summary or at
   the bottom after its component definitions?

## Representative production census

Pinned NIWC revision:
`8c8e5dff860af6b1290ee9273a282db24278f8d5`.

Measured automated Rule Assessments:

| Measure | Count | Percent |
| --- | ---: | ---: |
| Assessments | 1,350 | 100% |
| One Test + trivial `evaluate: {test: ...}` | **976** | **72.3%** |
| Flat Test-only logical operator | 308 | 22.8% |
| Evaluate depth > 2 | **61** | **4.5%** |
| Repeated Test references in tree | 21 | 1.6% |
| Unreferenced Tests | 0 | 0% |

Maximum observed evaluate depth: **5**.
Maximum observed evaluate nodes: **30**.

Workflow:
https://github.com/vanderpol/scap-ng/actions/runs/37617521723

The corpus therefore supports two conclusions at once:

- a first-class composition tree is genuinely needed for some Assessments;
- the required separate root pointer is ceremony for most ordinary one-Test
  Assessments.

## What Ansible suggests

Ansible does not maintain a separate criteria registry.

- `when` is attached to the task it governs;
- a `when` on a block is inherited by tasks in that block;
- `ansible.builtin.assert` keeps its Boolean expressions beside the assertion.

Official references:
- https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_conditionals.html
- https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_blocks.html
- https://docs.ansible.com/projects/ansible-core/stable-2.22/collections/ansible/builtin/assert_module.html

The useful lesson is **locality of decision logic**, not Ansible's result
semantics. Ansible conditionals are procedural/Boolean and do not replace
OVAL/NG six-state aggregation.

## Candidate directions to compare

### A. Keep current explicit root

```yaml
tests:
  ssh-root-disabled:
    ...

evaluate:
  test: ssh-root-disabled
```

Advantage: one uniform grammar.

Cost: redundant indirection in roughly 72% of the representative corpus.

### B. Implicit single-Test root

If an automated Assessment contains exactly one Test and no explicit
`evaluate`, that Test is the Assessment root.

This removes ceremony without inventing new Boolean semantics.

Open question: whether omission would violate the project's preference against
hidden behavior. One alternative is for authoring tools to accept the compact
form while canonical scanner content materializes the root explicitly.

### C. Local/nested composition

Allow logical composition to own/nest Test definitions directly where Test
identity does not need independent reuse.

This mirrors the broader Object/State locality research but has a higher bar:
Test Results have important independent identity/evidence and a Test may appear
more than once in an evaluate tree.

### D. Keep first-class evaluate only when composition exists

A hybrid authoring surface could make a single Test the obvious root while
retaining explicit `evaluate` for multi-Test/dependency composition.

## Placement

If `evaluate` remains first-class, placing it **near the top after metadata
and inputs/dependencies** deserves comparison with the current bottom placement.

Top placement reads as an executable summary:

```text
Assessment identity
inputs/dependencies
evaluate        <- what determines the result
Tests           <- referenced implementation
local Objects/States
```

Bottom placement reads implementation-first:

```text
Assessment identity
Objects/Variables/States/Tests
evaluate        <- final composition
```

Neither order is semantic. Human review should compare representative complex
files after Object/State locality, because locality may materially change which
order is easiest to understand.

## Safety boundary

Do not replace a real `all/any/one/odd/not` tree with procedural task ordering
or `when` merely because Ansible makes that syntax familiar.

Any proposed compact form must preserve:

- six-state aggregation;
- Test identity and Test Results;
- repeated Test references;
- dependency-result leaves;
- negation;
- evidence/provenance;
- source-order lineage where needed for migration.

## Next

1. Render representative one-Test, flat-all/any, repeated-Test, and deeply
   nested examples in the candidate presentations.
2. Measure readability after consumer-local Object/State transformations.
3. Determine whether implicit single-Test root belongs in authored syntax only
   or canonical executable syntax.
4. Prepare one concise #167 review packet with recommendation and counterexample.
