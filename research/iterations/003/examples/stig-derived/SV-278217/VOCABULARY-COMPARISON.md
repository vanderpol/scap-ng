# SV-278217 — Vocabulary experiment: NG/OVAL-lineage vs Ansible-inspired

**Board discussion exhibit only; no SCAP-NG schema change.** Both variants are research-only YAML, neither is valid current 0.3 syntax, and the Ansible-inspired version is **not an Ansible playbook**. Both describe the **same real Windows Server 2025 STIG requirement**, [SV-278217](README.md): `HKLM\SYSTEM\CurrentControlSet\Control\Lsa\RestrictAnonymous` exists as `REG_DWORD = 1`.

Read these in two separate views rather than placing distracting annotations in the YAML:
- [**A — NG/OVAL-lineage terms**](vocabulary-oval.research.yaml)
- [**B — Ansible-inspired action words**](vocabulary-ansible.research.yaml)

## Controlled substitution — nothing else changes

| NG/OVAL-lineage A | Ansible-inspired B | Identical meaning |
| --- | --- | --- |
| `tests` | `checks` | Named checks in the Assessment |
| `object` | `target` | Collected registry item selector |
| `select` | `where` | Selection predicates |
| `states` | `assertions` | Expected-state predicates |
| `expect` | `assert` | Container for type and value expectations |
| `evaluate` | `verify` | Final evaluation expression |
| `test` | `check` | Reference to the same named check |

**Historical precision:** `tests`, `object`, and `states` follow established OVAL concepts, but this is **not an OVAL vocabulary specimen**. `evaluate` is SCAP-NG's replacement for OVAL `criteria`; `expect` is newly proposed in the readability experiment and has no claimed OVAL lineage; `select` is NG authoring terminology. We must not misrepresent those two proposed source variants as strict OVAL versus Ansible dialects. The experiment is *current NG/OVAL-lineage terminology versus Ansible-inspired alternatives*, with speculative syntax in both.

**Unchanged in both:** `assessment`, `capability: windows.registry`, `hive`, `key`, `name`, `equals`, `type`, `value`, `match`, `existence`, `reported_elements`, and `one_or_more`. None of these have been removed or defaulted. Both require the same item's registry type to be DWORD and integer value to be 1; absence, mismatched type, mismatched value and collection failure retain the same outcome expectations in [the parent example](README.md).

This experiment deliberately **does not** change nesting, move predicates into code strings, add Jinja, invent Ansible collection modules, or fold multiple requirements together. `target`, `where`, `assertions`, and `verify` are *authoring vocabulary inspired by automation tools*—not claims of exact Ansible keywords or execution compatibility.

## Board question

Which terminology better communicates a real check to a new author *without misleading existing OVAL authors about semantics*? Focus on comprehension and conceptual accuracy, not shorter YAML. Possible outcomes: keep familiar OVAL terms, adopt specific substitutions, or retain a mixed vocabulary. A vocabulary vote does **not** imply changing the 0.3 schema; any proposed change would need a separate impact analysis and migration plan.

**Non-negotiable:** If a rename introduces ambiguity (for example, Ansible `when` and inventory semantics differ from assessment applicability), do not adopt it merely because it sounds modern.
