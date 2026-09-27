# Windows Cross-STIG Assessment Reuse Prototype

Iteration 001 now includes two separate illustrative Windows STIG-like policies:

- **Windows Client** — rule IDs `NG-DEMO-WC-*`
- **Windows Server** — rule IDs `NG-DEMO-WS-*`

They intentionally use different policy rule IDs, titles, references, and in some cases thresholds while sharing equivalent technical assessment concepts.

This is not a claim that any real DISA rules are equivalent. The examples exist to test the SCAP-NG architecture.

## Shared assessment mappings

| Assessment | Windows Client rule | Windows Server rule | Reuse type |
|---|---|---|---|
| `demo.windows.password-policy-by-role` | `NG-DEMO-WC-001` | `NG-DEMO-WS-101` | Parameterized: client requires length 14; server requires length 15 |
| `demo.windows.platform-security-posture` | `NG-DEMO-WC-002` | `NG-DEMO-WS-102` | Exact technical assessment reuse |
| `demo.windows.defender-realtime` | `NG-DEMO-WC-003` | `NG-DEMO-WS-103` | Exact technical assessment despite differing policy title |
| `demo.windows.remote-registry-disabled` | `NG-DEMO-WC-004` | `NG-DEMO-WS-104` | Exact technical assessment despite differing policy title |
| `demo.windows.trusted-publisher-store` | `NG-DEMO-WC-006` | `NG-DEMO-WS-106` | Exact technical assessment reuse |

Benchmark-specific assessments:

- Client `NG-DEMO-WC-005` -> `demo.windows-client.credential-guard-when-vbs`
- Server `NG-DEMO-WS-105` -> `demo.windows-server.smb-signing-required`

Manual rules have no automated assessment.

## What the split model demonstrates

The shared technical definitions exist once under:

`split-policy-assessment-binding/shared-assessments/windows/`

Each benchmark has its own individual policy files and its own `bindings.yaml`. A binding gives the policy rule an assessment identity and parameters. The package builder resolves the referenced assessment into each self-contained distributable.

The scanner operator therefore still installs one complete benchmark package; shared authoring does **not** create a runtime dependency.

## What the combined model demonstrates

Each automated rule contains its assessment inline. The client and server rules can use the same assessment identity, but equivalent logic is physically repeated in separate rule files.

This is intentional. It exposes a central architectural tradeoff:

- the combined form gives a reviewer one complete rule file;
- cross-STIG technical reuse requires duplication, generation/templates outside the standard, or introducing a reference mechanism that begins to resemble the split architecture.

The crosswalk is research evidence. It is not a proposed runtime mapping file for the combined model.
