# Unsigned result-package known result

Common synthetic content, adapted from the maintained conditional ownership
Assessment Result example. No target was scanned. `package-input.json` contains
one Scan, one Benchmark Result and one two-invocation Assessment Result set.
The conditional Assessment returns technical false; this compliance Rule records
policy fail. Policy interpretation is recorded, not computed by the package tool.

From the repository root:

```sh
PYTHONPATH=tools python tools/result_package_v02.py work/example.results.zip \
  --build-input tests/result-package-0.2.0/package-input.json \
  --assessments tests/assessment-results-0.2.0/content
```

The verification receipt must equal `expected-results/receipt.json`. The CLI
without `--build-input` verifies an existing ZIP. Without `--assessments`, it
checks schemas, integrity and execution references; with resolved sources it
also checks recorded expression scheduling. Neither mode proves acquisition,
State comparison truth, policy scoring, signer trust or target conformance.
The focused regression tests cover tampering, rehashed reference corruption,
unsafe ZIP members, resource limits, multiple invocation groups and scope guards.
