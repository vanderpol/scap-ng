# Gemini independent review — Phase 2: semantics, source preservation and correction log

**Only send AFTER Gemini's Phase 1 response has been saved unchanged.** This is the supplemental contract and real source challenge for [Phase 1](GEMINI-NATIVE-AUTHORING-PHASE1.md). It is research evidence, not an approved SCAP-NG specification.

--- BEGIN SECOND MESSAGE FOR GEMINI ---

You completed a cold first-read of a new native YAML assessment language. Now I am supplying the provisional interpreter contract and selected **original source Assessment** facts. Keep your initial answers frozen and produce an explicit correction ledger. Do not pretend that this is OVAL-compatible execution.

### Native proposed semantics (only for newly authored policies)

- Each checks every selected Item. A verified complete zero selected Items is acceptable unless minimum_resources requires more. Count selected Items **after where**, not only compliant Items. Unreadable or incomplete selection is not verified empty.
- minimum_resources: 1 requires at least one selected Item in the collection where it is written. It does not automatically apply per outer user, per command, or per zone unless it is written at that boundary.
- A named resource is required and uniquely identified by typed acquisition inputs; duplicate provider identity is an evidence error, not an instruction to select one passing value.
- Fields under must must be present and satisfy their operators. An explicitly confirmed absent field fails a required property; an omitted/unreadable/unknown field does not silently become compliant. Unreadable evidence can yield Error; unknown/partial evidence may yield Unknown.
- The typed source status is separate from the policy result: complete, incomplete, error, not collected, not applicable. A known violation can settle a universal check despite incomplete collection, but a partially observed all-compliant population does not pass.
- Boolean all and any use standard decisive aggregation: for example False AND Error is False; True OR Error is True. A key collection has its own completion status; each child key must bear the identity of the parent DNS zone.
- POSIX only_these_bits on four-digit octal mask 0740 means no bit outside that mask is present (bitwise subset), **not** a numeric <= 0740 comparison.
- Provider names are provisional. On Linux, the mountinfo collector reads only the current mount namespace. Apache static Includes are read without Apache runtime effective-config evaluation. Windows DNS keys come from structured synthetic fixtures, not actual PowerShell collection. This contract does NOT promise any native provider is source-equivalent to a particular OVAL test.

### Original SCAP 1.4-derived source graph facts to challenge migration

**Linux local initialization files:** Two original file Tests joined by AND. Non-system user-derived file set allows zero file Items but each selected file must satisfy eight Boolean permission flags. Root-derived file Test requires **at least one Item across the UNION of qualifying root home directory files**, not one per root user. Both require all eight specified fields present. Object acquisition includes user Set difference and file traversal of depth 1 with symlink behavior.

**Windows 11 remote-logon assignment:** WMI DomainRole source has two distinct complete-State alternatives: all nested DomainRole records equal 1 OR all records equal 3 for a member-role branch. A typed abstraction must not treat a mixed [1,3] record set as satisfying one of those complete alternatives. Similar grouping applies to standalone alternatives.

**Apache:** Original source uses **four separate shellcommand Tests**, each with an at_least_one Item existence requirement, ANDed together. Two check KeepAlive and two MaxKeepAliveRequests. One pair discovers primary config and direct Include files; another pair discovers files from the Apache DUMP_INCLUDES runtime command. The "other loaded config files, if defined" Test uses optional compared stdout/subexpression entities but DOES NOT waive the source's shellcommand Item existence. All source shellcommands explicitly disable automatic Error on nonzero exit and stderr. There are 18 derived Variables.

**DNS:** Original source has five shellcommand Tests in three OR branches: (1) caching-only/no nonexcluded forward or reverse zone **stdout_line values** in a required command Item, (2) AD integration/no violating forward-zone values in a required command Item, and (3) signed-zone AND of signed output and two distinct key-type validity-hour Tests. All five command Tests require >=1 Items. Signing source output uses exactly one string True and the two separate >=48 and <=168 State comparisons. Zone- and key-signing keys are collected by distinct derived PowerShell commands, which can convert exceptions into string 0. A reverse-only server may satisfy the "all forward zones integrated, if any" branch even though caching-only fails.

### Review tasks

1. Compare the FIRST-READ predictions with the native contract. For each changed prediction, quote your original answer and give the exact rule that changed it.
2. Identify examples where the stated native policy is simpler and still precise, as distinct from examples where simple native policy has lost one of the original collection, record, command, Item or State requirements. Produce one explicit counterexample for each claimed loss.
3. Critique the architectural compromise: ONE human authoring language for native policies, but one versioned internal typed IR/evaluator that must also support more complex, compiler-generated source-compatibility operations. Does it avoid the OVAL-in-YAML authoring failure, or merely conceal unavoidable complexity? List practical mitigation steps.
4. Give a CONDITIONAL GO/NO-GO on (a) native authoring usability and (b) lossless SCAP 1.4 forward conversion as a single standard. Do not conflate them.
5. Propose the smallest set of real providers, schema guarantees and additional tests that could invalidate your optimistic conclusion. Include a new content-authoring exercise a novice should perform without being given sample answers.

Do not claim you tested a real Windows host, Apache runtime, or source equivalence. Your analysis is limited to the supplied source facts and provisional contracts.

--- END SECOND MESSAGE FOR GEMINI ---
