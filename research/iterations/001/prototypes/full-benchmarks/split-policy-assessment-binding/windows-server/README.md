# Windows Server — split policy / assessment / binding

Seven individual policy rules live under `source/policy/rules/`. `source/automation/bindings.yaml` maps six rules to assessments.

Five assessments are reused from `../../shared-assessments/windows/`; the server-specific SMB signing assessment lives under `source/automation/assessments/`. The manual rule has no automated binding.
