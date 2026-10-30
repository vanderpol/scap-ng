# Generated SCAP-NG 0.4.0 authoring samples

These small, pinned samples come from original Windows Server 2025 SCAP 1.4
source through the isolated direct converter. Each directory links actual YAML
and structurally equivalent JSON, source provenance, and validation, compilation
and independent source-comparison evidence. They represent automated subsets,
not a complete Benchmark, six-STIG release or scanner-runtime equivalence.
For the complete 65-stream DRAFT and separately identified **internal layout prototype**,
smaller pinned candidate examples, and historical six-STIG ZIPs, use the
[0.4.0 downloads and Assessment samples index](../releases/0.4.0-downloads-and-samples.md).

- [Nested Sets, Filters, Variables and genuinely shared Objects](direct-file-rights/README.md).
- [NTUSER with ordered exclusion Filters and inline Registry acquisition](direct-ntuser/README.md).
- [IIS configuration with a string-valued requirement](direct-iis/README.md).
- [User rights, including original Variable matching and collection Filters](direct-userright/README.md).
- [WMI record requirements and shared acquisitions](direct-wmi/README.md).
- [OpenSSH text-file acquisition](direct-textfile/README.md).
- [Command collection-error controls](direct-command-behaviors/README.md).
- [Simple Registry, audit-policy without an Object, Boolean evaluation and dependency examples](direct-v04/README.md).
- [Historical cmdlet samples](direct-cmdlet/README.md): the UEFI/SV-278031 sample
  is withdrawn from current acceptance after finding an original-source datatype
  violation; its pinned files remain available as evidence.

Use each directory's exact regeneration command and pinned converter commit.
Counts in older manifests describe their own checkpoint; the
[engineering ledger](../audit/v04-engineering-ledger.md) and
[current source audit](../audit/v04-direct-remaining-primitives.md) record the latest
verified coverage and blocked cases. No original source normalization, production
replacement, signing/trust approval or release readiness is implied.
