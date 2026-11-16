# Core/shared documentation: Phase 1

**Inventory and wording proposals only. No schema edits or new runtime semantics are accepted.**

Pin: `d707aad6a916bb4e2e61767d836c681fc9d0084b`; renderer dependency: PR #39 `f61fff037f18832aa04db140b3e3209dfddf7219`. All JSON inputs are enumerated in [schema-manifest.json](schema-manifest.json).

Discovered **35 schema documents** among 145 JSON inputs. Audited 7902 schema nodes, including 1959 public current-core/shared nodes. 43 generated capability definitions are explicit scope exclusions; no capability expansion is authorized.

Public prose owners are named properties/definitions and roots. Anonymous array/map/alternative schemas and guard overrides remain inventoried with their exact constraints; their containing public element owns explanatory prose, while named fields inside them remain public. Fields introduced only in conditional branches are included, rather than discarded as guard overrides. Curated branch notes are additional targeted findings.

Found **1564 deduplicated findings** at 1562 canonical proposal locations. Presence is not useful-quality approval. Structural-only/provisional proposals remain open for review; generic filler cannot close a gap.

[Batch 1 editorial receipt](EDITORIAL-REVIEW.md) · [Batch 2 pending review](EDITORIAL-REVIEW-2.md) · [Phase 1 wording inventory](CROSSWALK.md) · [two bounded previews](PILOTS.md) · [machine inventory](inventory.jsonl) · [gap register](gaps.jsonl) · [full crosswalk](crosswalk.jsonl) · [annotation patch](proposed-annotations.patch.json).

### Description presence

| Value | Count |
| --- | ---: |
| inherited | 53 |
| missing | 1586 |
| own | 320 |

### Useful-quality review state

| Value | Count |
| --- | ---: |
| missing | 1586 |
| present_not_semantically_reviewed | 373 |

### Review decision kind

| Value | Count |
| --- | ---: |
| annotation_wording | 208 |
| editor_integration | 1 |
| native_basis_required_for_wording | 1137 |
| shared_annotation_binding | 216 |

### Proposal approval category

| Value | Count |
| --- | ---: |
| clarification_no_validation_change | 209 |
| editorial_only | 0 |
| normative_contract_decision_required | 1353 |

### Gap category

| Value | Count |
| --- | ---: |
| missing_constraint_meaning | 8 |
| missing_description | 1555 |
| missing_editor_help_binding | 1 |

### Severity

| Value | Count |
| --- | ---: |
| high | 1 |
| medium | 1563 |

### Role

| Value | Count |
| --- | ---: |
| conditional_field | 83 |
| document_root | 7 |
| field | 1437 |
| shared_definition | 37 |

### Document family

| Value | Count |
| --- | ---: |
| assessment_core | 973 |
| expressions_variables | 13 |
| packaging | 21 |
| policy_applicability | 93 |
| results_evidence | 313 |
| shared_language | 151 |

## Actual language boundary

Active Variable forms: `literal`, `variable`, `values`, `time_difference`, `concat`, `regex_capture`, `unique`, `count`, `split`, `substring`, `arithmetic`, `begin`, `end`, `merge`.

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
