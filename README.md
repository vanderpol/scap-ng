# SCAP-NG

SCAP-NG is a pre-alpha successor to SCAP 1.4 focused on preserving supported
assessment meaning while making security content easier to author, review,
implement, execute, package, and consume.

## Core objectives

1. Preserve meaning through migration.
2. Make authoring and review substantially simpler.
3. Make semantics explicit and predictable.
4. Scale through safe reuse of content and collected facts.
5. Produce smaller, more useful results.
6. Cover the complete policy lifecycle.
7. Be trustworthy, interoperable, and governable.
8. Reduce implementation complexity and enable efficient execution.

See the [full objectives](specification/objectives.md) and
[objective-to-issue traceability](OBJECTIVES.md).

## Start here

- **Specification:** [specification/README.md](specification/README.md)
- **Real-world examples:** [Benchmark and Rule policy](specification/examples/README.md) · [technical Assessments](specification/examples/assessments.md) · [result fixtures](specification/examples/0.3.0/results/README.md)
- **0.4 pre-alpha preview:** [Example-led technical overview](research/assessment-simplification/compact-authoring-04/ASSESSMENT-REVIEW-OVERVIEW.md) · [deeper authoring/semantics review](research/assessment-simplification/compact-authoring-04/ASSESSMENT-REVIEW-TECHNICAL.md)
- **Current review:** [review/current/README.md](review/current/README.md)
- **0.3.0 schema:** [schema/v0.3.0/](schema/v0.3.0/)
- **Six complete STIGs:** [One native authoring ZIP](https://github.com/vanderpol/scap-ng/releases/download/v0.3.0-six-stig-typed-operators-5796d016b12f/scap-ng-0.3-six-stig-authoring.zip) · [six compiled scanning bundles](https://github.com/vanderpol/scap-ng/releases/tag/v0.3.0-six-stig-typed-operators-5796d016b12f)
- **Open issues / 0.3 work:** [GitHub issues](https://github.com/vanderpol/scap-ng/issues)
- **Governance and published votes:** [board/README.md](board/README.md)


## Six-STIG authoring and scanning downloads

The [current owner-reviewed **SCAP-NG 0.3 six-STIG prerelease**](https://github.com/vanderpol/scap-ng/releases/tag/v0.3.0-six-stig-typed-operators-5796d016b12f)
contains **one native authoring ZIP** (all six STIGs and shared Assessments),
plus **six separately compiled `.scapng` packages**—one each for RHEL 9,
Oracle Linux 9, Windows 11, Windows Server 2025, Windows Server DNS, and
Apache HTTP Server 2.4 (UNIX).

**[Download the complete native authoring ZIP](https://github.com/vanderpol/scap-ng/releases/download/v0.3.0-six-stig-typed-operators-5796d016b12f/scap-ng-0.3-six-stig-authoring.zip)**
· [open the six compiled bundles](https://github.com/vanderpol/scap-ng/releases/tag/v0.3.0-six-stig-typed-operators-5796d016b12f).

The native Rules select Assessments by logical ID, use a single explicit
publisher default, and avoid redundant datatype declarations for ordinary
literal comparisons. The authoring compiler expands rare typed operations,
such as `version_greater_than_or_equal`, to the original OVAL-compatible
typed canonical comparison. Source migration remains faithful: Variables,
Inputs, arrays and ambiguous values retain explicit types. **4,532 of 5,267
authored datatype fields (86%)** were removable in this conservative
six-STIG authoring presentation.

**Verified build property:** The CI release gate compiled all six content
bundles independently from the older fully typed source and new concise
source, and verified matching SHA-256 hashes for every resulting `.scapng`
file. The older source-only candidate/faithful downloads remain in GitHub
release history as evidence, but are no longer the recommended review entry
point.

**Status:** Experimental pre-alpha content, neither DISA-issued nor OVAL
Board-ratified. Compilation identity proves identical scanner-facing
content—not that an independent scanner has executed OVAL 5.12.3
Self-Assertion successfully. The special-float migration coverage gap
is tracked in [#218](https://github.com/vanderpol/scap-ng/issues/218).
See the [current review](review/current/README.md),
[Assessment examples](specification/examples/assessments.md),
and [OVAL Board A/B/C/D discussion](https://github.com/vanderpol/scap-ng/discussions/213).

## Architecture

SCAP-NG uses **Benchmark → Rule → Assessment**. Native automated Assessments
retain useful OVAL concepts such as Test, Object, local typed State predicates, Variable, and Item while
removing legacy serialization and packaging machinery where it is not
semantically required. Distribution uses modular source compiled into a
self-contained manifest-based package.

**Status:** pre-alpha. Green CI, schema validation, conversion evidence, human
acceptance, and Board ratification are distinct states.
