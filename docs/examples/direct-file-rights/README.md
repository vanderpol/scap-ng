# Direct 0.4.0 representative automated-subset examples

Actual converter output from the pinned original Windows Server 2025 SCAP 1.4 package.
These are Assessments, not a complete Benchmark or six-STIG release.

- source-filter-variable: [Windows Server 2025 permissions for the Application event log must prevent access by nonprivileged accounts.](windows-server-2025-permissions-for-the-application-event-log-must-pre-c5ee49a5.assessment.yaml) · [JSON](windows-server-2025-permissions-for-the-application-event-log-must-pre-c5ee49a5.assessment.json)
- shared-acquisition: [Windows Server 2025 permissions for the Security event log must prevent access by nonprivileged accounts.](windows-server-2025-permissions-for-the-security-event-log-must-preven-71ba6bba.assessment.yaml) · [JSON](windows-server-2025-permissions-for-the-security-event-log-must-preven-71ba6bba.assessment.json)

[Manifest](manifest.json) records original Benchmark/Rule/Definition IDs, dependency hashes, converter SHA and validation, compilation and independent proof outcomes.
Examples retain their exact original Variable quantifiers and collection boundaries. Source fidelity does not establish that the original policy check is effective.

Regenerate into a new directory from the pinned converter commit:

```bash
PYTHONPATH=tools python tools/v04_direct_authoring_examples.py --capability windows.fileeffectiverights53 --output /tmp/direct-authoring-examples
```

Use PyYAML 6.0.3 and jsonschema 4.25.1; see the [developer guide](../../developer/DIRECT-V04-CONVERTER.md). The command revalidates/proves/compiles the entire supported subset and the selected closed wrapper. Generated files are not edited by hand. Signature trust and scanner equivalence are not claimed.
