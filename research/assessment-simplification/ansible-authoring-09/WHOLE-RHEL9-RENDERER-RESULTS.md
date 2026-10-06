# Whole-RHEL-9 mechanical local-authoring experiment

> **RESEARCH ONLY — NOT AN ACCEPTED SCAP-NG DESIGN OR CONVERTER**

A fail-closed research renderer was run over all 445 RHEL 9 Rules. The renderer
starts from the existing converted Assessment YAML and produces a speculative
local, Ansible-inspired form. It refuses structures it has not explicitly been
taught to preserve.

Tool: `tools/research_render_ansible_like.py`

## Progression

| Pass | Newly supported research form | Rendered | Coverage |
| --- | --- | ---: | ---: |
| 1 | Simple/composed local checks | 313 / 445 | 70.3% |
| 2 | Local multiple-State `any/all` | 330 / 445 | 74.2% |
| 3 | Simple union Sets as multiple collection sources | 371 / 445 | 83.4% |
| 4 | Local include/exclude Filters | **375 / 445** | **84.3%** |

Latest successful run:

https://github.com/vanderpol/scap-ng/actions/runs/37533285488

## Current fail-closed remainder

After pass 4:

| Reason | Rules |
| --- | ---: |
| Default manual | 27 |
| Variables present | **42** |
| Complement Set without Variable preflight | 1 |
| **Not rendered** | **70** |

Therefore the unresolved **automated** tail is only **43 / 445 = 9.7% of the
benchmark**, and 42 of those Rules are concentrated in the Variable/dataflow
problem.

## What this demonstrates

This does **not** prove that 84.3% of RHEL 9 has a final replacement syntax.

It does show that a very small set of human-facing ideas can mechanically
represent most of the currently converted benchmark without exposing the
author to top-level Object/State/Test graph plumbing:

- local typed collection;
- local expectations;
- ordinary `all / any / not` composition;
- several local collection sources combined as a union;
- local include/exclude filters; and
- explicit collection behavior where behavior matters.

The large coverage jump from 70.3% to 84.3% is important because no general
Variable language, expression language, shell fallback, or accepted-schema
change was added to obtain it.

## What this does not demonstrate

Rendering success is a serialization-shape test, not yet full source semantic
equivalence proof. Before any syntax could be proposed normatively, each
research construct would need:

1. a typed semantic lowering;
2. preserved collection/error/status behavior;
3. preserved existence/check/entity quantifiers;
4. source-to-research differential fixtures; and
5. review against original STIG intent.

The current renderer is intentionally one-way research tooling and SHALL NOT be
treated as a production converter.

## Next question

The next research target is the **42 Variable-bearing Rules**.

Instead of adding a general OVAL-like Variable subsystem to the human language,
classify those Rules by what the Variables are actually doing:

- projecting a field from collected Items;
- local `for_each` / binding;
- concatenating a local derived value;
- split/count/unique;
- small arithmetic;
- Variable chains;
- genuinely multi-source / Cartesian expression semantics.

The research question is whether most of those can be expressed as small local
authoring concepts such as `for_each`, `let`, or aggregate operations while
the compiler/semantic IR retains the full OVAL-equivalent behavior.

Only after that decomposition should the experiment consider a general
expression/Variable language.
