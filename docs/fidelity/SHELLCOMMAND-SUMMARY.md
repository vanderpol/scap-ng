# Shellcommand: before and after

The [previous page](shellcommand-before.md) exposed field tables and unresolved contracts, but omitted most operational guidance. The [new page](../reference/capabilities/independent.shellcommand.md) starts with schema-owned purpose, safety guidance and contract boundaries, followed by compact Object/Item/Require sections. It prominently shows integer exit status and string output evidence. Shared Require grammar is linked once.

| Meaningful pinned-source topic | Treatment in the proposed schema/reference |
| --- | --- |
| Command purpose; interpreter, command and output pattern | Adapted to native Object and Require terminology. |
| Executable content, elevated privileges, responsibility to do no harm | Retained as prominent author guidance. The scanner's actual privilege level is not prescribed. |
| Robust commands; excessive STDOUT or STDERR | Adapted as bounded-output, predictable-command advice. No invented size limit. |
| Well-formed output | Retained as evidence-quality advice. Source line-to-Item rules remain withheld. |
| External executable dependencies | Retained as advice to prefer OS utilities and review dependencies. No new ban. |
| Trust and signing | Trust/integrity review is visible. OVAL's mandatory trusted-source/signing rule is explicitly historical and withheld as a native requirement. |
| STDOUT, STDERR and exit status | Existing native evidence fields and acquisition-control declarations remain visible. No new line splitting, status aggregation or default behavior is guaranteed. |
| One-liner only; no external or multiline script | Withheld: native command-form restrictions remain unresolved. |
| Default Bash | Withheld: an omitted interpreter has no approved native default contract. |
| One Item, line cardinality, empty output and `does not exist` | Withheld: native conventions are unresolved, and source Object/Item wording differs. |
| Pattern filtering, captures, greedy matching and capture order | Field purpose retained; unproved matching/evaluation mechanics remain in the semantic ledger. |
| Echoing shell/command/pattern verbatim | Withheld pending a native evidence contract. |
| Error flags, defaults and Item status propagation | Native parameter meanings remain documented; OVAL defaults and error propagation are withheld. |
| XML inheritance and Test/Object/State reference routing | Excluded boilerplate; actual JSON Schema relationships provide the native structure. |

The [complete comparison](SHELLCOMMAND-REVIEW.md) records every direct source statement and referenced ShellCommandBehaviors statement, with its identifier, disposition and destination or withholding rationale. The [crosswalk](crosswalk.jsonl) adds exact source/destination pointers and spans. Split statements can be independently retained or withheld; the short table groups topics for review without becoming a prose authority.

This is documentation reconciliation, not an execution test or scanner-equivalence claim. Mandatory trust/signing, command scope, default interpreter, output cardinality, empty output and error propagation still require native semantic decisions.
