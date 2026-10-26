# Pinned current-source acceptance fixtures

The XML files are unchanged original OVAL Self-Assertion inputs from
revision `e3538595c5083b9c34d937a81d319234df9bbfaa`. The Windows 11 ZIP is the
unchanged NIWC SCAP 1.4 input, not the October 21 generated source-preview archive.
[Provenance and hashes](provenance.json) identify their original paths and refs.
WMI57 reuses the existing original XML under
[v04-absence-only](../v04-absence-only/provenance.json).
`historical-sv278028.json` is separately identified archived native authoring used
to test explicit Object/Filter migration. It is not original OVAL evidence.

Run from the repository root with Python 3.12, PyYAML 6.0.3, jsonschema 4.26.0
and lxml 6.0.2:

```bash
PYTHONPATH=tools python -m unittest test_v04_current_source_acceptance -v
PYTHONPATH=tools python tools/prove_v04_current_bluetooth_source.py --output /tmp/bluetooth-current
```

The second command emits generated YAML/JSON, the unchanged-node original OVAL
dependency closure, independent term comparison, negative controls, compilation
and consumer evidence. A miniature Benchmark/Rule wrapper is explicitly synthetic;
it does not establish complete Windows 11 Benchmark/Profile equivalence.
The published historical archive is not an input to this process.
