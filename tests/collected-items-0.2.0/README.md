# Known-result collected Item examples

These are synthetic, platform-independent **result representation** fixtures for
the experimental 0.2.0 slice, not executable benchmark or target collector tests.
`cases.json` includes each expected validation result. Validation includes JSON
Schema and `context_errors`; both are required. Nothing here changes 0.1.0.

Run `PYTHONPATH=tools python tools/test_collected_item_contract_v02.py` from the
repository root. Generate all 99 experimental capability Item contracts with
`python tools/collected_item_contract_v02.py --output work/collected-items-0.2.0`.

See [the checkpoint](../../transition/collected-items-2026-10-03.md) for semantics,
source evidence, candidate dispositions and remaining target-test requirements.
These cases are inputs to the complete vendor-facing test-content initiative
tracked in #128; they do not claim complete feature coverage.
