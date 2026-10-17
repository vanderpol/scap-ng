# Gemini Phase 2 independent review — source-checked audit

**17 October 2026 · Issues #235 and #229.** Compare with the [frozen original Phase 1](GEMINI-NATIVE-PHASE1-RESPONSE-2026-10-17.md), the [Phase 1 analysis](GEMINI-NATIVE-PHASE1-AUDIT-2026-10-17.md), and the [Phase 2 review instructions](GEMINI-NATIVE-AUTHORING-PHASE2.md). Gemini's full Phase 2 response was supplied in the chat and assessed below.

## Result

**Conditional GO** for continued technical research into a requirements-first native authoring language plus compiler-owned compatibility IR. **NO-GO** for unaided novice authoring, normative 0.4 approval and any claim of proven lossless SCAP 1.4 forward conversion. Gemini's Phase 2 conditional GO on authoring after being shown the contract does **not** erase the Phase 1 failed authoring attempt.

## Correct the alleged correction ledger

Seven "Quoted First-Read Prediction" entries in Gemini Phase 2 are **not quotations from the preserved Phase 1 text**:

1. Phase 1 never claimed numeric <= 0740. It tried octal_equals and explicitly said simple equality was insufficient.
2. Phase 1 did not demand a file per root account. Its attempted YAML put a single minimum on the combined files population.
3. Phase 1 did not say an empty non-system-user set necessarily causes Error or Failure.
4. Phase 1 did not evaluate WMI DomainRole [1,3] at all.
5. Phase 1 did not claim Apache missing config is Not Applicable.
6. Phase 1 did not describe original DNS empty forward-zone results. The reviewed native DNS signing rule required at least one forward zone; that is a DIFFERENT policy than the original source's AD branch.
7. Phase 1 did not state the whole Boolean tree becomes Error or Unknown on any error. It explicitly marked error behavior uncertain.

These are new analyses of the **supplied Phase 2 facts**, not measured corrections to the actual first review. Preserve them as technical observations but **do not count them as independent validation of the source contracts**.

## Fix technical statements

- Microsoft's DomainRole mapping is 0 standalone workstation, 1 **member workstation**, 2 standalone server, 3 **member server**, 4 backup domain controller and 5 primary domain controller. Gemini's 1/3 parenthetical labels are incorrect; the all-1 OR all-3 grouping example remains a meaningful synthetic counterexample. https://learn.microsoft.com/en-us/dotnet/api/microsoft.powershell.commands.domainrole
- OVAL evaluation has SIX values: True, False, Error, Unknown, Not Evaluated, Not Applicable. The FIVE source collection flags (complete/incomplete/error/not collected/not applicable) are a separate layer. https://github.com/OVALProject/Language/blob/master/schemas/oval-results-schema.xsd
- False AND Error = False, True OR Error = True specify result aggregation, NOT guaranteed short-circuit execution. The research evaluator evaluates each child before aggregating. A future optimizer must separately specify when execution may be skipped and what audit evidence is preserved.
- Original Apache source shellcommand flags for nonzero exit/stderr were false, but stderr is **not thereby converted to stdout**; command streams, test Item existence, optional stdout entity values and errors are distinct.
- WMI mixed [1,3] must not be confused with proof that multi-homed computers actually produce multiple Win32_ComputerSystem records. This is a synthetic semantic falsifier, not observed prevalence.
- Mode 0100 indeed satisfies a 0740 permission-bit subset. That demonstrates the typed operator, not a corrected Phase 1 numeric assertion.

## Retain valid guidance

Expose a dumpable versioned IR with per-node evidence provenance, result reasons and original source mapping. Make provider manifests include identity and namespaces, typed field operations, relation joins, completion/error behavior, scope, API limitations, safe cache keys and platform applicability. Tie minima to exact counted populations. Compare source-compatible results in six-state fixtures and on real target collectors before migration claims.

## SSH novelty is an authorability test, not a ready-made provider

The suggested SSH policy is UNDER-SPECIFIED. A source-file requirement (the directives must be **explicitly written** as no) is not identical to an effective-configuration requirement (what sshd actually applies, including Include files and Match contexts). OpenSSH normally uses the FIRST obtained keyword value; context-specific Match blocks can override global values. An editor must ask whether the policy checks literal source declarations, effective settings for which user/connection, or both. See https://manpages.debian.org/unstable/openssh-server/sshd_config.5.en.html

A primary config mode 0400 **passes** only_these_bits: '0600' because it uses a subset of allowed bits, assuming the other constraints (including owner UID 0) hold. An empty optional Include directory is not necessarily an error. Missing **required** files or incomplete enumeration need explicit provider status. There is NO typed SSH provider in this research catalog; do not invent one and claim the language can run this check.

## Rival relationship notation A/B

The Phase 1 target/filter/constraints/sub_resources proposal omitted key-signing keys. It is not equivalent to the original nested DNS requirement. The [completed two-kind explicit-relation file](contract-candidate/explicit-dns-relations.yaml) and [strict transpiler](../../tools/research_native_relation_alternative.py) are a controlled experiment: reject undeclared joins, include BOTH key kinds and compare the EXACT resulting typed AST. Neither syntax is normative. A readability vote is useful only after this semantic identity test passes.

## Gates that still block release

A complete typed provider catalog, error/result semantics including Not Evaluated, genuine new-auditor authoring with validation guidance, a scoped SSH requirements exercise, and real source-specific full six-state conversion are NOT done. The common Test-level compatibility bridge proves feasibility of coexisting internal operations, not conversion of all Objects/States/Variables.

**Decision:** keep the existing source-compatible design as fallback and the new native authoring model as an engineering candidate; do not freeze normative 0.4 or treat Gemini's revised vote as usability proof.
