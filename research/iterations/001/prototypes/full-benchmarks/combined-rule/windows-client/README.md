# Windows Client — combined rule with overlays

Seven policy rules live individually under `source/policy/rules/`.

Five automated rules are produced from reusable bases in `../../shared-rules/windows/` plus STIG-specific files under `source/automated/overlays/`. The client-specific Credential Guard rule and manual-only rule remain local under `source/automated/rules/`.

The package build resolves overlays into complete rules and verifies that their policy fields match the policy-only source exactly.
