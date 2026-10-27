# Direct converter completion — original six-source requirements (#251)

Phase 1 is inventoried; implementation continues. Base:
`8a1df22219cbbb91ca1095ed8989e6e502423c37`. This checkpoint does not enable a
capability or promote a conversion. The [machine matrix](v04-six-source-requirements.json)
and [1,567-Rule index](v04-six-source-rules.csv) retain exact source IDs, required
capabilities, observed diagnostics and separate applicability requirements.

| Original STIG | Rules | OVAL-bearing | Manual/OCIL only | Declared Tests | Referenced Tests¹ | Invalid primary OVAL closures | Broken primary bindings |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| RHEL 9 | 445 | 418 | 27 | 673 | 639 | 2 | 0 |
| Oracle Linux 9 | 448 | 408 | 40 | 621 | 604 | 2 | 0 |
| Windows 11 | 257 | 246 | 11 | 353 | 345 | 3 | 0 |
| Windows Server 2025 | 291 | 261 | 30 | 372 | 359 | 2 | 0 |
| Windows Server DNS | 81 | 41 | 40 | 64 | 60 | 2 | 41 |
| Apache 2.4 | 45 | 22 | 23 | 57 | 56 | 0 | 22 |
| **Total** | **1,567** | **1,396** | **171** | **2,140** | **2,063** | **11** | **63** |

¹ Unique Test declarations in primary Rule closures, per STIG/component. Candidate
closures behind broken bindings are included as explicitly unbound evidence.
The 2,695 original Definition declarations also remain indexed. Counts are not
the 883 unique historical migrated Assessments and are not source-proof claims.

Inputs are the original six ZIPs at NIWC commit
`8c8e5dff860af6b1290ee9273a282db24278f8d5`; exact hashes are in the
[source lock](../../tests/fixtures/v04-direct-six-sources.json). OVAL components
are independently validated against unchanged 5.12.3 XSD and every embedded
Schematron pattern from core/common and their source families. Diagnostics retain
source node IDs and assertion text. Bad unused declarations remain component
findings; only reachable violations or component-wide errors invalidate a closure.
This is not a claim that an entire published datastream is schema-valid.

Both Apache and DNS publish a checklist catalog reference to a component ending
`-oval.xml`, while the corresponding component actually ends `-oval2.xml`. The
strict converter still rejects this. Inventory mode records the original broken
reference and matching Definition candidates without modifying the executable
catalog. Those 63 Rule bindings remain invalid; candidate graphs do not repair
or authorize conversion. The original ZIPs are unchanged.

Applicability is not silently omitted from requirements: original CPE dictionary
and CPE language trees, check bindings, negations, source graph references and
Rule/ancestor platform uses are separately recorded in the full artifact. For
example, OS guards require RPM information across both Linux STIGs and family
observation across both Windows STIGs. Those guards must be converted and proved
separately before claiming complete Rule/policy equivalence. The existing 249
Windows primary-Assessment proofs remain their original scope.

Priority evidence for primary closures (potential, **not guaranteed unlocks**):

- UNIX file: 127 source-valid, correctly bound Rules where it is the only
  missing enabled capability; RPM information: 66; sysctl: 66; partitions: 52;
  systemd properties: 29; UNIX password: eight.
- `variable.value` appears in 21 primary closures; five source-valid, bound Rules
  have no other missing capability. Its large standalone fixture population does
  not justify prioritizing it ahead of universal OS guards/file acquisition.
- Shared observed gaps include `all_exist` (232 primary Rule closures), file
  behaviors, Variable-source acquisition, merge/unique/count functions, typed
  acquisition parameters and nil selectors. Complete diagnostic strings and
  dependency IDs remain in the machine evidence. Unresolved `all_exist`, old WMI,
  other unmapped/deprecated source families and source-invalid shapes stay blocked.

Reproduce with Python 3.12, PyYAML 6.0.3, jsonschema 4.26.0 and lxml 6.0.2:

```sh
PYTHONPATH=tools python -m unittest test_v04_six_source_requirements -v
python tools/inventory_v04_six_source_requirements.py \
  --inputs /path/to/pinned-niwc/Current --output /tmp/six-requirements
```

The read-only `v04-direct-six-requirements` workflow checks out that exact source
revision and uploads complete node/edge, source-validity and applicability packets.
Nine new positive/negative regressions cover original XSD/Schematron, attribution,
strict rejection versus non-repairing inventory, scope and CPE reference fidelity.
No normative schema, existing converter output, compiler, scanner, release or
historical archive is changed. Conversion logic growth is zero; source loading
adds an explicit inventory-only flag. New validation/inventory code is separate
from conversion and imports no historical converter.

Next: finish deterministic native contract generation without the old generator,
then implement shared collection/function support and independent proof rules
according to this matrix. At `c1c124f58a45981a7cfe5678eb4206afd6baf75c`, all nine triggered workflows pass.
The downloaded [mandatory result](https://github.com/vanderpol/scap-ng/actions/runs/40484866700)
reports **3,111 tests, zero failures/errors, one existing skip**. The
[hosted six-source inventory](https://github.com/vanderpol/scap-ng/actions/runs/40484867055)
reproduces every local STIG summary. Artifact checksums and all CI links are in
the machine matrix. Work continues with native generation and shared handlers.
