# Semantic implementation requirement

For every RI capability implemented or modified, the same development increment must include:

1. Research of pinned OVAL 5.12.3 evaluation rules and edge cases.
2. Mapping to the exact canonical SCAP-NG 0.4 schema, distinguishing equivalent, intentionally different, unsupported and unresolved behavior.
3. Standalone normative native documentation in this repository; OVAL must not be required reading for implementers.
4. Executable conformance fixtures with positive and negative cases, and passing RI regressions.
5. An OVAL-to-native compatibility matrix with source pointers and exact schema pins.
6. A clear separation between language requirements and RI implementation limitations.

No language behavior is complete without these four deliverables: normative documentation, compatibility mapping, executable conformance tests and passing RI regressions. Coordinate separate linked draft PRs; preserve frozen schemas and all semantic holds. Escalate genuine specification conflicts. Do not merge or promote unapproved semantics. Store implementation/performance limits separately from language requirements.


### Execution authority and incomplete evidence (permanent)

- Normative SCAP-NG contracts must distinguish acquisition status, logical Object completeness, population completeness, evidence completeness, privilege context, visibility/namespace scope, evidence trust, and evaluation outcome. A successful syscall or returned Item is not a completeness guarantee.
- Root, restricted namespace, missing, denied, partial, symlink, mount-boundary, include, and kernel-visibility behavior must be explicitly specified or held; container/namespace root must not be described as host-wide authority.
- Apparent passes that require complete population evidence must not be asserted without sufficient completeness. Observed decisive failures may remain failures only where unseen evidence cannot reverse the condition.
- Any normative change in these areas requires coordinated frozen-schema/result review, standalone canonical documentation understandable without OVAL, pinned OVAL 5.12.3 compatibility research, positive/negative conformance fixtures, and linked RI regression tests. AGENTS.md does not approve new language or schema semantics; unresolved decisions belong in an owner-review document.
