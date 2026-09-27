# SCAP 1.4 Corpus Conversion Tooling

This directory contains research tooling for the hard SCAP 1.4 forward-conversion requirement.

## Current tool

`scap14_corpus_convert.py` currently provides the **corpus-ingestion and semantic-accounting skeleton**:

- recursively finds XML and ZIP-contained XML;
- rejects unsafe ZIP traversal names;
- hashes every source;
- identifies SCAP component families;
- inventories XCCDF rules/profiles/check references;
- inventories OVAL definitions/tests/objects/states/variables;
- counts OVAL constructs and important semantic attributes;
- captures every XML element/attribute/text node into a semantic-accounting tree so unsupported syntax is not silently lost;
- extracts embedded datastream components;
- writes machine-readable reports;
- implements an ingestion gate and a deliberately failing native gate.

The native gate will remain red until native translators are wired into the harness.

That is intentional: the tool must measure actual migration completeness rather than report success because XML parsing worked.

## Example

```bash
python research/iterations/001/tools/scap14_corpus_convert.py \
  /path/to/public-corpus \
  --output-dir work/scap14-conversion \
  --gate ingest
```

Later, the pre-specification check should use:

```bash
python research/iterations/001/tools/scap14_corpus_convert.py \
  /path/to/pinned-public-corpus \
  --output-dir work/scap14-native-conversion \
  --gate native
```

## Planned translator layers

1. datastream/component-reference resolution;
2. XCCDF benchmark/profile/rule/policy conversion;
3. OVAL faithful semantic IR;
4. OVAL native translation registry;
5. OCIL/manual conversion;
6. CPE/applicability conversion;
7. original NG YAML renderer;
8. Ansible-inspired NG YAML renderer;
9. canonical NG compiler;
10. equivalence/differential harness.

The same semantic IR must feed both human-authoring renderers.
