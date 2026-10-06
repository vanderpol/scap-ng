# RHEL 9 Ansible-inspired feasibility checkpoint

> **RESEARCH ONLY — NOT AN ACCEPTED SCAP-NG DESIGN**
>
> These counts are exploratory classifications of existing production content.
> They do not change the 0.3.0 schema or establish a new authoring language.

## Automated Rule population

The current RHEL 9 diagnostic inventory contains **418 default-automated Rules**
and **27 default-manual Rules**.

Using only observed source features, the 418 automated Rules provisionally
partition as follows:

| Bucket | Rules | Percent |
| --- | ---: | ---: |
| Simple native | 207 | **49.5%** |
| Composed native | 106 | **25.4%** |
| Advanced structured/dataflow | 84 | **20.1%** |
| Existing shellcommand | 21 | **5.0%** |

The hierarchy used for this preliminary count is:

- existing shellcommand: Rule already reaches a shellcommand capability;
- advanced structured: otherwise uses Variables, Sets, Filters, or Variable functions;
- composed native: otherwise uses multiple Tests/States, Boolean composition, or negation;
- simple native: remaining automated Rules.

This is a **feature census, not conversion proof**. A Rule being in
`simple_native` does not prove the current straw-man syntax is sufficient, and
an `advanced_structured` Rule may still simplify dramatically.

## What the first real examples show

The initial real-RHEL examples are stored in `examples/`:

- SV-257790: single file collection + expectation;
- SV-257783: single systemd property + expectation;
- SV-257786: two local systemd checks under `all`;
- SV-257889: local-user -> home-directory -> initialization-file iteration;
- SV-257847: extracted audit directory reused by partition and fstab checks;
- SV-257823: existing command-oriented assessment.

The simple and composed examples suggest that the authoring surface can be much
more local than the current OVAL-like graph while still compiling to rigorous
semantic IR.

SV-257889 and SV-257847 are deliberately retained as stress cases. They test
whether `for_each` and local derived values can make genuine dataflow readable
without pretending the multi-value/Cartesian semantics do not exist.

## Manual-rule result

All 27 default-manual procedures were reviewed individually. Preliminary
classification:

| Manual bucket | Rules |
| --- | ---: |
| Deterministic automation candidate | **5** |
| Potentially automatable with better typed domain model | **7** |
| Requires organizational/external input or approved exception knowledge | **15** |

See `MANUAL-AUTOMATION-REVIEW.md`.

This is an important result: **shellcommand is not the primary missing feature
for manual automation**. Much of the remaining manual population is manual
because pass/fail depends on facts not present on the host.

## Current feasibility hypothesis

A plausible research target is therefore:

- make the ~75% simple+composed automated population read naturally using local
  module-like collection plus inline expectations;
- prove whether the ~20% dataflow population can be handled with a small number
  of readable constructs such as local bindings, foreach, and explicit
  composition;
- preserve command-oriented checks as commands where that is genuinely the
  clearest representation;
- use organizational input where the requirement depends on approved values or
  exceptions;
- leave genuinely human-judgment checks manual.

The next research step is **not** a schema change. It is to expand the
side-by-side sample and then attempt a complete 418-Rule syntactic
classification, recording the exact reason whenever the straw-man language is
insufficient.
