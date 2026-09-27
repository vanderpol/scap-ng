# Windows Cross-STIG Reuse Prototype

Iteration 001 includes two separate illustrative Windows STIG-like policies:

- **Windows Client** — rule IDs `NG-DEMO-WC-*`
- **Windows Server** — rule IDs `NG-DEMO-WS-*`

They intentionally use different policy rule IDs, titles, references, and in some cases thresholds while sharing equivalent technical assessment concepts.

This is not a claim that any real DISA rules are equivalent. The examples exist to test the SCAP-NG architecture.

## Shared technical concepts

| Technical concept | Windows Client rule | Windows Server rule | Reuse type |
|---|---|---|---|
| Password policy by role | `NG-DEMO-WC-001` | `NG-DEMO-WS-101` | Parameterized: client length 14; server length 15 |
| Platform security posture | `NG-DEMO-WC-002` | `NG-DEMO-WS-102` | Exact automation reuse |
| Defender real-time | `NG-DEMO-WC-003` | `NG-DEMO-WS-103` | Exact automation despite differing policy title |
| Remote Registry disabled | `NG-DEMO-WC-004` | `NG-DEMO-WS-104` | Exact automation despite differing policy title |
| TrustedPublisher certificate | `NG-DEMO-WC-006` | `NG-DEMO-WS-106` | Exact automation reuse |

Benchmark-specific automation:

- Client `NG-DEMO-WC-005` — Credential Guard when VBS applies.
- Server `NG-DEMO-WS-105` — SMB signing required.
- Manual rules intentionally have no automated logic.

## Split-model representation

The five shared technical assessments exist once under:

`split-policy-assessment-binding/shared-assessments/windows/`

Each STIG has its own policy files and `bindings.yaml`. The builder resolves referenced assessments into each self-contained distributable.

## Combined-model representation

The five reusable combined rule bases exist once under:

`combined-rule/shared-rules/windows/`

Each STIG has an overlay under:

`<benchmark>/source/automated/overlays/`

The overlay supplies STIG-specific identity/metadata and, when allowed by the shared rule, parameter values. It does not directly patch the assessment logic.

At build time the shared rule and overlay are resolved into a complete rule. The build verifies that the resolved policy fields exactly match the policy-only rule for that STIG.

This preserves one scanner-facing self-contained package while allowing the combined-rule candidate to demonstrate genuine cross-STIG reuse instead of artificial duplication.
