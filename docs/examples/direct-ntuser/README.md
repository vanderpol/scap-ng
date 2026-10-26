# Direct 0.4.0 representative automated-subset examples

Actual converter output from the pinned original Windows Server 2025 SCAP 1.4 package.
These are Assessments, not a complete Benchmark or six-STIG release.

- source-filter-variable: [Windows Server 2025 must preserve zone information when saving attachments.](windows-server-2025-must-preserve-zone-information-when-saving-attachm-739b74c3.assessment.yaml) · [JSON](windows-server-2025-must-preserve-zone-information-when-saving-attachm-739b74c3.assessment.json)

[Manifest](manifest.json) records original Benchmark/Rule/Definition IDs, dependency hashes, converter SHA and validation, compilation and independent proof outcomes.
Examples retain their exact original Variable quantifiers and collection boundaries. Source fidelity does not establish that the original policy check is effective.

Regenerate into a new directory from the pinned converter commit:

```bash
PYTHONPATH=tools python tools/v04_direct_authoring_examples.py --capability windows.ntuser --output /tmp/direct-authoring-examples
```

Use PyYAML 6.0.3 and jsonschema 4.25.1; see the [developer guide](../../developer/DIRECT-V04-CONVERTER.md). The command revalidates/proves/compiles the entire supported subset and the selected closed wrapper. Generated files are not edited by hand. Signature trust and scanner equivalence are not claimed.
