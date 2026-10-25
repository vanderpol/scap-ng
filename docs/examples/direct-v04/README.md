# Direct 0.4.0 representative automated-subset examples

Actual converter output from the pinned original Windows Server 2025 SCAP 1.4 package.
These are Assessments, not a complete Benchmark or six-STIG release.

- inline-registry: [Windows Server 2025 must prevent the display of slide shows on the lock screen.](windows-server-2025-must-prevent-the-display-of-slide-shows-on-the-loc-da1e140a.assessment.yaml) · [JSON](windows-server-2025-must-prevent-the-display-of-slide-shows-on-the-loc-da1e140a.assessment.json)
- shared-object: [The Windows Server 2025 required legal notice must be configured to display before console logon.](the-windows-server-2025-required-legal-notice-must-be-configured-to-di-c6314f08.assessment.yaml) · [JSON](the-windows-server-2025-required-legal-notice-must-be-configured-to-di-c6314f08.assessment.json)
- system-audit-policy: [Windows Server 2025 must be configured to audit Account Logon - Credential Validation successes.](windows-server-2025-must-be-configured-to-audit-account-logon-credenti-7a4eb1d5.assessment.yaml) · [JSON](windows-server-2025-must-be-configured-to-audit-account-logon-credenti-7a4eb1d5.assessment.json)
- multiple-tests: [Windows Server 2025 permissions for the system drive root directory (usually C:\) must conform to minimum requirements.](windows-server-2025-permissions-for-the-system-drive-root-directory-us-40e5f4bd.assessment.yaml) · [JSON](windows-server-2025-permissions-for-the-system-drive-root-directory-us-40e5f4bd.assessment.json)
- nested-set: [Windows Server 2025 must have the DoW Root Certificate Authority (CA) certificates installed in the Trusted Root Store.](windows-server-2025-must-have-the-dow-root-certificate-authority-ca-ce-acebd595.assessment.yaml) · [JSON](windows-server-2025-must-have-the-dow-root-certificate-authority-ca-ce-acebd595.assessment.json)
- variable-dependencies: [Windows Server 2025 Active Directory SYSVOL directory must have the proper access control permissions.](windows-server-2025-active-directory-sysvol-directory-must-have-the-pr-1ec1fc0c.assessment.yaml) · [JSON](windows-server-2025-active-directory-sysvol-directory-must-have-the-pr-1ec1fc0c.assessment.json)

[Manifest](manifest.json) records original Benchmark/Rule/Definition IDs, dependency hashes, converter SHA and validation, compilation and independent proof outcomes.
The nested Set example has no nonempty Filters; none is independently proved in the current subset.

Regenerate into a new directory from the pinned converter commit:

```bash
PYTHONPATH=tools python tools/v04_direct_authoring_examples.py --output /tmp/direct-authoring-examples
```

Use PyYAML 6.0.3 and jsonschema 4.25.1; see the [developer guide](../../developer/DIRECT-V04-CONVERTER.md). The command revalidates/proves/compiles the entire supported subset and the selected closed wrapper. Generated files are not edited by hand. Signature trust and scanner equivalence are not claimed.
