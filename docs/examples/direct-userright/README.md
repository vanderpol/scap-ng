# Direct 0.4.0 representative automated-subset examples

Actual converter output from the pinned original Windows Server 2025 SCAP 1.4 package.
These are Assessments, not a complete Benchmark or six-STIG release.

- ordinary-acquisition: [The Windows Server 2025 "Access this computer from the network" user right must only be assigned to the Administrators, Authenticated Users, and Enterprise Domain Controllers groups on domain controllers.](the-windows-server-2025-access-this-computer-from-the-network-user-rig-39c0aa50.assessment.yaml) · [JSON](the-windows-server-2025-access-this-computer-from-the-network-user-rig-39c0aa50.assessment.json)
- source-filter-variable: [Windows Server 2025 must have orphaned security identifiers (SIDs) removed from user rights.](windows-server-2025-must-have-orphaned-security-identifiers-sids-remov-9b66082d.assessment.yaml) · [JSON](windows-server-2025-must-have-orphaned-security-identifiers-sids-remov-9b66082d.assessment.json)
- shared-acquisition: [The Windows Server 2025 "Deny log on as a service" user right on domain-joined member servers must be configured to prevent access from highly privileged domain accounts. No other groups or accounts must be assigned this right.](the-windows-server-2025-deny-log-on-as-a-service-user-right-on-domain-b642b95e.assessment.yaml) · [JSON](the-windows-server-2025-deny-log-on-as-a-service-user-right-on-domain-b642b95e.assessment.json)

[Manifest](manifest.json) records original Benchmark/Rule/Definition IDs, dependency hashes, converter SHA and validation, compilation and independent proof outcomes.
Examples retain their exact original Variable quantifiers and collection boundaries. Source fidelity does not establish that the original policy check is effective.

Regenerate into a new directory from the pinned converter commit:

```bash
PYTHONPATH=tools python tools/v04_direct_authoring_examples.py --capability windows.userright --output /tmp/direct-authoring-examples
```

Use PyYAML 6.0.3 and jsonschema 4.25.1; see the [developer guide](../../developer/DIRECT-V04-CONVERTER.md). The command revalidates/proves/compiles the entire supported subset and the selected closed wrapper. Generated files are not edited by hand. Signature trust and scanner equivalence are not claimed.
