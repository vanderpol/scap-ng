# Known-result reported-element examples

Draft 0.2.0 reporting feature, intended for the complete vendor corpus in #128.
`ownership.assessment.yaml` compares numeric UID while requesting owner name.
It describes `/fixture/config`; it must not be interpreted as permission to
scan a real target. `cases.json` supplies synthetic collected Items, complete
field-use lineage and six control choices. `expected-results/field-selections.json`
provides the independently specified expected selections. These are representation/
projection fixtures, not collector conformance.

Run:

```
PYTHONPATH=tools python tools/test_reported_elements.py
python tools/reported_elements.py project --assessment tests/reported-elements-0.2.0/ownership.assessment.yaml --observations tests/reported-elements-0.2.0/cases.json --output work/reported-items.json
python tools/reported_elements.py generate --mapping schema/v0.1.0/capability-mappings/unix.file.json --output work/unix-file-reporting.schema.json
```

See [the reporting contract](../../transition/reported-elements-2026-10-03.md).
The projection's marker and source completeness distinguish deliberate field
selection from collection failure or evidence truncation. Selection does not
replace redaction or the complete authoritative Assessment Result.
