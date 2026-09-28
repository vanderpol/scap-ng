# Full pinned NIWC corpus assessment reuse

Measured across all 65 individual published `*-signed.zip` benchmarks in the pinned NIWC `Current/` corpus.

This is a compact semantic-fingerprint survey. It does not generate three full YAML renderings for every benchmark.

## Exact assessment reuse

- Benchmarks: **65**
- XCCDF rules: **8892**
- Supported automated assessments: **7084**
- Unique exact technical assessments: **3413**
- Duplicate assessment maintenance units avoidable: **3671**
- Exact maintenance-unit reduction: **51.82%**
- Cross-benchmark exact-reuse groups: **1701**
- Cross-benchmark assessment instances in those groups: **5340**

## Rule mapping and parameterization

- Cross-benchmark identical Check Text groups: **1295**
- Unique semantic shapes after literal abstraction: **1593**
- Parameterization candidate reduction upper bound: **77.51%**

The parameterization figure is an upper bound only; it is not counted as proven reuse.

## Source-remediation debt

- Automated rules blocked by effectively deprecated tests: **155**
- http://oval.mitre.org/XMLSchema/oval-definitions-5#windows#accesstoken_test: **168** blocked-rule references
- http://oval.mitre.org/XMLSchema/oval-definitions-5#windows#user_test: **10** blocked-rule references
- http://oval.mitre.org/XMLSchema/oval-definitions-5#windows#wmi_test: **36** blocked-rule references

## Cost interpretation

The measured duplicate-unit count can be multiplied by organization-specific review/test hours, change frequency, and loaded labor rate. No universal labor assumptions are embedded in the evidence.

See `reuse-analysis.json` for fan-out distributions and the 100 largest cross-benchmark exact-reuse and Check-Text alignment groups.
