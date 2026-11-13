# First five capability example pairs

Ten complete, reusable YAML fixtures demonstrate one Pass/Fail pair each for unix.file, windows.registry, independent.shellcommand, linux.rpminfo and windows.service. This is the bounded batch authorized after issue #42's original unix.file pilot; further capability expansion waits for owner review.

Each fixture contains a full native Assessment (including inline Object, Require and evaluate), an explicit successful collection result, linked typed Items, an expected technical result, a teaching Pass/Fail label and a concise reason. Values are synthetic. **All ten expectations remain native-evaluator-unverified.** See [runtime availability and proof requirements](EVALUATION.md).

- [Canonical fixture files](../../examples/paired/v0.4.1/)
- [Exact syntax/proof ledger](validation.json)
- [Local test and reproducibility evidence](test-evidence.json), including resolved test-setup failures
- [OVAL documentation quality table](OVAL-QUALITY.md) and [source audit ledger](oval-documentation-quality.json)
- [unix.file reference](../reference/capabilities/unix.file.md#examples), [Registry](../reference/capabilities/windows.registry.md#examples), [shellcommand](../reference/capabilities/independent.shellcommand.md#examples), [RPM](../reference/capabilities/linux.rpminfo.md#examples), [service](../reference/capabilities/windows.service.md#examples)

The proposed capability schemas explicitly reference fixture paths and SHA-256 digests through passive `x-doc-examples` annotations. The fixtures reference one immutable 0.4.1 schema-family pin. The existing generalized renderer loads these files, validates their native fragments and renders the Examples sections. Editor metadata contains links and hashes, not separately maintained example bodies. The documentation manifest binds all eleven inputs; offline consumers reject missing or changed fixtures.

With Python 3.12 and `requirements-dev.txt` installed:

```sh
python tools/generate_documentation.py
python tools/audit_documentation_fidelity.py
python tools/check_documentation_examples.py
python tools/generate_documentation.py --check
python tools/audit_documentation_fidelity.py --check
python tools/check_documentation_examples.py --check
python -m unittest discover -s tests -v
```

To maintain an example, edit its canonical YAML, update its schema annotation's digest and regenerate. Preserve the 0.4.1 schema pin; historical 0.4.0 fixtures remain archived and are not migrated. The loader rejects wrong capability associations, duplicate YAML keys/Item IDs, unlinked Items, stale/missing inputs, missing native syntax and unsupported proof labels. Additional primitive payload checks qualify these examples; they add no restrictions to the frozen result schema and do not evaluate Require.

No frozen schema bytes, existing descriptions, semantic holds, compiler behavior, production pins or previous evidence receipts are changed. The stack base is draft PR #47 at `7e27c23e53fdfdf018fa483a24b857462992b109`. No merge requested.
