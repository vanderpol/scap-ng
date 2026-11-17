# Core/shared documentation: Phase 1

**Inventory and wording proposals only. No schema edits or new runtime semantics are accepted.**

Pin: `63110e7762f4963d3e4d407e90b9fcfd9cfe86ad`; renderer dependency: PR #39 `f61fff037f18832aa04db140b3e3209dfddf7219`. All JSON inputs are enumerated in [schema-manifest.json](schema-manifest.json).

Discovered **35 schema documents** among 145 JSON inputs. Audited 7941 schema nodes, including 1953 public current-core/shared nodes. 43 generated capability definitions are explicit scope exclusions; no capability expansion is authorized.

Public prose owners are named properties/definitions and roots. Anonymous array/map/alternative schemas and guard overrides remain inventoried with their exact constraints; their containing public element owns explanatory prose, while named fields inside them remain public. Fields introduced only in conditional branches are included, rather than discarded as guard overrides. Curated branch notes are additional targeted findings.

Found **1580 deduplicated findings** at 1573 canonical proposal locations. Presence is not useful-quality approval. Structural-only/provisional proposals remain open for review; generic filler cannot close a gap.

[Batch 1 editorial receipt](EDITORIAL-REVIEW.md) · [Batch 2 pending review](EDITORIAL-REVIEW-2.md) · [Phase 1 wording inventory](CROSSWALK.md) · [two bounded previews](PILOTS.md) · [machine inventory](inventory.jsonl) · [gap register](gaps.jsonl) · [full crosswalk](crosswalk.jsonl) · [annotation patch](proposed-annotations.patch.json).

### Description presence

| Value | Count |
| --- | ---: |
| inherited | 53 |
| missing | 1587 |
| own | 313 |

### Useful-quality review state

| Value | Count |
| --- | ---: |
| missing | 1587 |
| present_not_semantically_reviewed | 358 |
| reviewed_deficient | 3 |
| reviewed_useful_with_specific_gap | 5 |

### Review decision kind

| Value | Count |
| --- | ---: |
| annotation_wording | 219 |
| editor_integration | 1 |
| native_basis_required_for_wording | 595 |
| runtime_contract | 6 |
| shared_annotation_binding | 752 |

### Proposal approval category

| Value | Count |
| --- | ---: |
| clarification_no_validation_change | 219 |
| editorial_only | 1 |
| normative_contract_decision_required | 1353 |

### Gap category

| Value | Count |
| --- | ---: |
| contradictory_description | 1 |
| missing_constraint_meaning | 9 |
| missing_description | 1557 |
| missing_editor_help_binding | 1 |
| missing_example | 4 |
| missing_scanner_error_semantics | 3 |
| unspecified_schema_contract | 3 |
| vague_description | 2 |

### Severity

| Value | Count |
| --- | ---: |
| high | 17 |
| low | 1 |
| medium | 1562 |

### Role

| Value | Count |
| --- | ---: |
| alternative | 1 |
| conditional_field | 83 |
| document_root | 7 |
| field | 1445 |
| shared_definition | 44 |

### Document family

| Value | Count |
| --- | ---: |
| assessment_core | 978 |
| expressions_variables | 19 |
| packaging | 21 |
| policy_applicability | 93 |
| results_evidence | 315 |
| shared_language | 154 |

## Actual language boundary

Active Variable forms: `literal`, `variable`, `values`, `concat`, `regex_capture`, `unique`, `count`, `split`, `substring`, `arithmetic`, `begin`, `end`, `merge`.

The broader canonical function-call migration document is inactive; its names are not active authoring/runtime support. The actual branch spelling is `else_if`, not `elseif`. Shared foreach helper definitions exist but have no Assessment reference path; they are not a demonstrated authored placement.

## Review priorities

1. Resolve concat casting/status/return obligations, regex dialect/status behavior, sorting edge cases and generic typed-value consistency before calling them editorial fixes.
2. Review the concrete shared reference/predicate/evaluation wording and two previews.
3. Triage remaining structural-only proposals by impact; they expose gaps and are not approved descriptions.
4. Verify exact editor-pack association separately. Offline $ref resolution is tested; live hover integration is not.

## Reproduce / gate

```sh
python tools/audit_schema_documentation.py
python tools/audit_schema_documentation.py --check
python -m unittest discover -s tests -v
```

The explicit baseline permits preexisting findings but rejects new/changed findings and stale output. Disappearing findings are reported, never automatically marked resolved. Update a baseline only as an explicit review action; no baseline rewrite occurs in normal generation.

**STOP for Jack's review. No Phase 2, merge, bulk annotations, editor repin or 104-capability expansion.**
