# UNIX password generic capability increment — #251

Enabled `unix.password` through the existing generic visitor, with **zero new
capability-specific conversion algorithms**. The password-only measurement used
**16** enabled capabilities; the [combined batch](v04-direct-capability-batch.md)
now enables **20**.
The independent checker now reads password State fields from original 5.12.3 XSD
and normalizes only the synonymous primitive labels OVAL `int` / native `integer`.
Original type declarations and dynamic expression boundaries remain present.

Six complete primary OVAL Rule closures pass original XSD/Schematron, current
schema validation, independent source comparison and compiled-operand checks:

| STIG | Original Rules |
| --- | --- |
| RHEL 9 | SV-258046, SV-258059, SV-258105 |
| Oracle Linux 9 | SV-271630, SV-271831, SV-271845 |

All six original UNIX password Self-Assertion Tests also validate/compile/prove.
The configured fast corpus grows from **190 attempted / 144 compiled / 127 proved**
to **196 / 150 / 133**. The broader diagnostic corpus remains **297 compiled /
133 proved**; this is admission of an already-generic path, not invented semantic
coverage. Unresolved `all_exist`, missing capabilities and unproved closures stay
out of generated packages. No normative schema, scanner or historical artifact
changes. Applicability remains separately inventoried; these are primary source
proofs, not complete Rule/policy certification.

The two published-source subset bundles and source/compiled evidence are produced
by `verify_v04_unix_password.py`; selection follows dependency capabilities, not
Rule-ID branches. Committed fixtures contain complete original closures and
source ZIP/member/node hashes; CI regenerates and compares them against actual
pinned SCAP. Negative tests cover changed existence/type, foreign source fields
and forged compiled operands. Existing Windows coverage/program hashes remain
subject to their unchanged mandatory regression assertions.

[Actual RHEL YAML/JSON example](../examples/direct-unix-password/README.md) ·
[machine evidence](v04-unix-password.json).

Reproduce with the pinned six-source inputs:

```sh
PYTHONPATH=tools python -m unittest test_v04_direct_unix_password -v
python tools/verify_v04_unix_password.py \
  --inputs /path/to/pinned-niwc/Current --output /tmp/new-password-proof
```

Next: metadata-backed scalar proof rules for universal OS guards and ordinary
Linux/UNIX acquisition; shared file traversal and aggregation support. No
handwritten capability algorithm is needed when existing metadata suffices.
