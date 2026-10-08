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
- **Current review:** [review/current/README.md](review/current/README.md)
- **0.3.0 schema:** [schema/v0.3.0/](schema/v0.3.0/)
- **0.2.0 frozen schema:** [schema/v0.2.0/](schema/v0.2.0/)
- **Open issues / 0.3 work:** [GitHub issues](https://github.com/vanderpol/scap-ng/issues)
- **Governance and published votes:** [board/README.md](board/README.md)

## Architecture

SCAP-NG uses **Benchmark → Rule → Assessment**. Native automated Assessments
retain useful OVAL concepts such as Test, Object, State, Variable, and Item while
removing legacy serialization and packaging machinery where it is not
semantically required. Distribution uses modular source compiled into a
self-contained manifest-based package.

**Status:** pre-alpha. Green CI, schema validation, conversion evidence, human
acceptance, and Board ratification are distinct states.
