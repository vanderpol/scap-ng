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
