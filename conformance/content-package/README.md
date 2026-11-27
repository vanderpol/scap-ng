# Canonical content package replay

The fixture assembles an unsigned 0.4.1 content package from the existing
canonical Benchmark, applicability catalog, two Rules and two Assessments.
The build reads [the source manifest](sources.json) and writes a new package
directory. It packages the explicitly specified compiled Rule fixture
metadata and does not implement a general compiler.

```sh
python conformance/tools/build_content_fixture.py "$PACKAGE_DIRECTORY"
python conformance/tools/replay_content_fixture.py --check \
  --ri-content "$RI_CONTENT" --ri-revision f39ac725b820353e6f6b8fc71af673c08857d895
```

RI installed the package and preserved its logical Benchmark identity.
The four negative replays reject modified bytes, a well-digested dangling
Rule reference, unsigned content under a signature requirement and an
unmanifested file. The [oracle](expected.json) states the acceptance and
rejection reasons independently of the captured [RI receipt](ri-receipt.json).
The local regression test ties the receipt to the exact manifest and
checks that the package retains each canonical source document.

The replay qualifies package admission in RI. Policy execution and
end-to-end scanner Results need a separate receipt.
[RI #196](https://github.com/vanderpol/scap-ng-ri/issues/196).
