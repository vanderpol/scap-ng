# Pinned OVAL time_difference witness

This fixture covers the 30 Tests in OVAL Self-Assertion Definition 580 at
the source pin in [expected.json](expected.json). The static baseline
comes from the independent RI issue 206 source oracle. The replay
recalculates those 29 expected seconds from the source date operands
using Python UTC date arithmetic and checks the original States.
For the Object-backed case, the two four-value operands yield
16 matching values in the RI result.

The remaining source Test uses a strict comparison against 86,400
seconds. Three fixed UTC clocks produce 86,399, 86,400 and 86,401
seconds, so the outcomes are false, false and true. The actual native
Assessment comes from the current converter replay. Expected values and
outcomes stay outside the RI request.

```sh
python conformance/tools/qualify_time_difference_fixture.py --check \
  --self-assertion /path/to/pinned/SCAP-Self-Assertion \
  --converted /path/to/converted/definition-580 \
  --ri /path/to/pinned/scap-ng-ri
```

The [receipt](ri-receipt.json) records the direct evaluator outcomes,
source and converted byte digests and exact revision pins. Assessment
rollup, arbitrary date inputs and general converter parity remain open.
The earlier RI qualification recorded 13 OpenSCAP disagreements with
static source expectations, preserved in its historical receipt.

- [RI source oracle](https://github.com/vanderpol/scap-ng-ri/blob/f39ac725b820353e6f6b8fc71af673c08857d895/docs/qualification/issue206/oracles/oval-time-difference-source-oracle.json)
- [Earlier RI and OpenSCAP receipt](https://github.com/vanderpol/scap-ng-ri/blob/f39ac725b820353e6f6b8fc71af673c08857d895/docs/qualification/issue206/oval-time-difference-current-main-v4-receipt-20261125.json)
- [Tools parity audit gap](https://github.com/vanderpol/scap-ng-tools/issues/128)
