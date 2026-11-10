# Native semantic maintenance

Read [SCAP-NG 0.4 evaluation contracts](0.4-evaluation.md) and the [pinned compatibility matrix](0.4-compatibility.json). Existing requirements, newly approved Model A, unresolved rules and RI limitations are explicitly separate. The schema files are unchanged.

Each implementation increment must update these contracts/mappings and add positive/negative fixtures before claiming behavior complete. Review the original pinned OVAL XSD annotations and Self-Assertion XML; do not use source expectations as evaluator inputs. Keep exact pins and evidence in the linked separate canonical/RI draft PRs. `AGENTS.md` records the permanent requirement.

Dependencies: Python 3.12 with `requirements-dev.txt`; the Go 1.27.3 RI binary for execution proof.

```sh
python -m unittest discover -s tests -v
python tools/check_semantic_conformance.py
python tools/check_semantic_conformance.py --ri-binary /path/to/ri-evaluate --output /tmp/new-conformance-receipt.json
```

The first conformance command checks syntax only and reports zero executions. The last runs every full native fixture through the real compiled evaluator and checks independently supplied assertions afterward. Expected results never enter the engine. Outputs refuse overwrite. Source fixture updates require explicit review and a new immutable RI pin; do not update frozen schema files or relabel old receipts. An implementation must report unsupported features and proof limits rather than count them as passes.

[Supplied-evidence fidelity](0.4-evidence.md) and [semantic holds](0.4-semantic-holds.md) accompany the shared storage increment. Run `python tools/check_semantic_conformance.py --supplied-evidence --ri-binary /path/to/ri-evaluate --output /tmp/new-combined-receipt.json` for all 23 executable fixtures. Source example files remain immutable; the catalog references their hashes.

[Actual combined conformance execution](evidence/combined-conformance.json) and [qualification/pins](evidence/qualification.json) bind the 23 cases to compiled RI runtime producer `3e05fb8cdd2765d0d0a94f197795ad0513a97911`, independently of subsequent SQLite work. The canonical 129-test suite passed locally. Separate RI backend parity/100,001-Item evidence must be reviewed in the linked SQLite draft; it is not inferred from this syntax/equality receipt.

[Result simplification design](result-simplification-design.md) is an owner-review
proposal for a smaller interoperable production Result and a separate optional
diagnostic/evidence contract. It does not modify frozen 0.4.0 schemas or historical Results. The candidate
0.4.1 schema and fixtures are isolated under `proposed-schema/result-0.4.1/` and
`evidence/result-0.4.1/` for owner review.

The [0.4.1 candidate receipt](result-0.4.1-candidate.md) records the exact
candidate schema/sidecar pins and coordinated RI validation status. It is not a
release approval.
