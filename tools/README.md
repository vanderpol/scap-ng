# SCAP-NG tooling

**Human operators:** start with [Human-runnable SCAP-NG tools](HUMAN-RUNNABLE-SCRIPTS.md). It documents supported commands, examples, inputs/outputs, safety boundaries, and historical/research-only entry points.

Start with the [current design](../research/iterations/003/design/CURRENT-DESIGN.md). Tool location or an old passing test does not establish current native syntax.

## Maintained entry points

The table below is the short list. The [human-runnable tools guide](HUMAN-RUNNABLE-SCRIPTS.md) is the complete operator catalog.

| Task | Entry point | Status |
| --- | --- | --- |
| Convert a pinned SCAP package for full source review | `scap_upconvert_v003/convert_full_review.py` | Current research CLI; [Windows/local instructions](scap_upconvert_v003/README.md) |
| Generate current corpus review content | `generate_niwc_current_review.py` | Fresh original SCAP input; retained source accounting |
| Current native round-trip census | `scap_ng_roundtrip_v003/roundtrip_corpus_v003.py` | Representation evidence; runtime equivalence unproven |
| Validate native schemas | `validate_native_json_schemas.py` | Structural validation |
| Audit generated authoring vocabulary | `check_current_authoring_contract.py` | Naming/structure guard; not semantic equivalence |
| Normalize exact Assessment duplicates | `scap_ng_repo_normalizer.py` | Dry run by default; explicit rewrite to a separate output tree |
| Compile resolved content bundles | `scap_ng_content_compiler.py` | Packaging/signing experiment; not a released scanner |
| Verify repository preservation/boundaries | `audit_repository_layout.py --check` | Baseline paths, historical bytes and workflow gates |

Reusable OVAL/SCAP semantic inputs include `oval_semantic_ir.py`, `scap14_rule_splitter.py`, `scap14_benchmark_ir.py`, result truth tables, source-default/catalog helpers and validation utilities. Current code still uses these helpers. Preserve them when reviewing older renderers that also import them.

## Historical reproduction

`scap14_to_scapng.py`, `build_scapng_from_converted_source.py`, older combined/split-policy renderers, Ansible-inspired renderers, and the original `scap_upconvert_v003/run_local.py` reproduce earlier experiments. They are retained, but are not the novice entry point or the current native generator. Historical CI generation requires a manual `allow_historical` opt-in; three superseded v003 publishing jobs remain held.

The [dependency report](../docs/audit/dependencies.json) lists every workflow, its status, direct script paths and the static current import closure. [Inventory classifications](../docs/audit/repository-inventory.tsv.gz) are conservative: unreferenced tooling is retained for review, not declared safe to delete.

Historical tool instructions can be recovered verbatim from the [before-cleanup commit](https://github.com/vanderpol/scap-ng/blob/9751ef0e5ae43ab728876969ff59dad538a101f0/tools/README.md). [Lossless rebaseline and future relocation procedure](../docs/lossless-rebaseline.md).
