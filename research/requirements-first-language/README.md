# Requirements-first SCAP-NG — fresh-start auditor language

**17 October 2026. Research only. Not an adopted 0.4 standard, scanner, or lossless conversion proof.**

**[Typed DNS zone/key fixture evidence](../../tools/research_dns_zone_key_evidence.py)** is now paired with a [versioned provider contract](providers/windows.dns.zone_signing_evidence.v0.1.yaml) and [negative tests](../../tools/test_research_dns_zone_key_evidence.py) for real distinctions between zone IDs, key kinds, partial evidence and Days*24+Hours typing. These use supplied structured fixtures, not Windows APIs; source semantics remain gated.

**[New DNS source counterexample](DNS-SOURCE-SEMANTIC-AUDIT-2026-10-17.md)** — the original AD-integrated check allows **zero forward zones** when its required command Item has no violating stdout values. The earlier native sample incorrectly required a forward zone, which can change a reverse-only DNS server's outcome. [Pinned DNS source checks](../../tools/test_research_dns_source_contract.py) prove the five-command, three-OR-alternative, separate key-State structure. **Not** source-parity proof.

**[Apache four-command source audit and tested static configuration provider](APACHE-SOURCE-PROVIDER-AUDIT-2026-10-17.md)** — the original uses four independently required shellcommand Items, two distinct config file source populations, 18 derived Variables, and optional compared fields which **do not** waive root Item existence. [Read-only Apache source-evidence collector](../../tools/research_provider_apache_directives.py), [provider v0.1 manifest](providers/apache.config_directives.v0.1.yaml), [fixture tests](../../tools/test_research_provider_apache_directives.py), and [original-source contract tests](../../tools/test_research_apache_source_contract.py). The collector preserves file/line evidence and incomplete status; it does not evaluate Apache effective settings or establish SCAP 1.4 parity.

**[Latest — real Linux initialization-files source audit](LINUX-INIT-FILES-AUDIT-2026-10-17.md)** — the source requires one file in the **combined root-derived file population**, not one file per root user; an octal `0644` file fails despite being numerically less than `0740`. Exhaustive tests confirm a typed 12-bit `only_these_bits: '0740'` operation matches the eight original Boolean flag predicates for complete modes. [Source-conscious candidate](experiments/linux-init-global-population.yaml) and [4,096-mode/source test](../../tools/test_research_linux_init_permissions.py). The [streamed read-only account-home file provider](../../tools/research_provider_linux_account_files.py), its [versioned contract](providers/linux.files_from_account_homes.v0.1.yaml), and [isolated real-filesystem tests](../../tools/test_research_provider_linux_account_files.py) now exercise per-account provenance, partial results and bounded scanning. They do **not** prove original OVAL traversal/field parity.

**[Start here — short current decision summary](DECISION-SUMMARY.md)** and **[third-pass typed-resource-first examples](IDEAL-AUDITOR-AUTHORING-THIRD-PASS.md)**. Neither is an adopted normative grammar. The simple resource form and the population form are being tested against the same evidence and evaluation contract.

**[NEW: provider contract and outcome counterexample gate](PROVIDER-CONTRACT-GATE.md)** — the leading native authoring alternatives are tested against [synthetic typed evidence](../../tools/research_requirements_first_evidence.py), including partial collection, unreadable selection fields, exactly-one semantics, duplicate uniqueness and mixed Windows WMI records. **[Real Linux mountinfo provider v0.1](../../tools/research_provider_linux_mounts.py)** now collects typed read-only observations from the process mount namespace; its [versioned provider manifest](providers/linux.mounts.v0.1.yaml) explicitly describes identity, selected scope, completion, field types and parity limitations. [Linux provider tests](../../tools/test_research_provider_linux_mounts.py) include a real GitHub Actions runner collection smoke test. This is **not** a source-faithful conversion of the original OVAL linux.partition capability, and it does not prove Apache/DNS providers exist. The validator also no longer admits the unimplemented one_matching quantifier.

**[User-supplied Gemini/ChatGPT first-read comparison](REVIEW-TRIAGE-GEMINI-CHATGPT-2026-10-17.md)** — both flagged missing existence and provider contracts; ChatGPT disclosed prior context, and Gemini Part 3 is not yet received. [Affirmative existence experiment](experiments/affirmative-presence-candidate.md) compares optional `each` with a positive `minimum_resources` constraint against a named-singleton alternative. None of these variants is adopted. The research grammar now rejects ambiguous `none` combined with `must`.

**[Answer-free naive ChatGPT review packet](NAIVE-REVIEW-PACKET.md)** asks an unfamiliar first-time reader to infer meaning from the samples, particularly contradictory empty-population interpretations, without an answer key. A separate **[internal counterexample and alternatives review](INTERNAL-EMPTY-POPULATION-REVIEW.md)** must be withheld until blind responses are saved. The current `if_empty` requirement is **not** promoted or removed pending evidence; this is a deliberate fresh attempt to avoid agreeing too quickly with the latest suggestion.
 Tracked in [#235](https://github.com/vanderpol/scap-ng/issues/235). Existing 0.3/0.4 schemas, compiled content and releases remain unchanged.

I revisited the August and October Claude redesign documents. Their strongest idea was **typed security-resource checks, composable requirements and lexically scoped iteration**, combined with evidence caps and clear organizational inputs. I had previously dismissed them as too simple. Simplicity is exactly what an authoring interface needs; the technical challenge is defining provider behavior without concealing mistakes.

## What an auditor writes

~~~yaml
id: native-linux-home-nosuid
title: The /home filesystem must disable setuid execution
require:
  every: linux.mounts
  where:
    mount_point: {equals: /home}
  must:
    mount_options: {contains: nosuid}
  if_empty: fail
~~~

The meaning: examine the selected mounted filesystems; every one must contain nosuid, and the requirement fails if there are no selected mounts after **successful complete acquisition**.

This is a **new native policy** that selects exact /home, not a lossless rewrite of the existing source selector .*\/home. The [source-regex version](examples/01-linux-home.yaml) remains separate. Never silently normalize the original selector.

**One small recursive language:** require; every/some/none/exactly_one to quantify typed security resources; where to select; using to configure acquisition; must for expectations and nested checks; all/any for boolean structure; as and scoped references for nested relationships; if_empty for an explicit complete-empty rule; manual and if for human/conditional checks. It has no authored Object → Test → State decomposition.

| Syntax | What an auditor means |
| --- | --- |
| every: resource | Every selected resource must satisfy its nested requirement |
| some: resource | At least one selected resource satisfies its nested requirement |
| none: resource | **Zero selected resources after where**; must is prohibited to avoid two conflicting meanings |
| exactly_one: resource | **Exactly one selected resource**, which also satisfies must; counts selected Items, not only compliant Items |
| where | Restrict the resources examined; distinct from acquisition |
| using | Inputs to the named typed evidence provider |
| must | Required properties or more nested security requirements |
| all / any | Combine full requirements, not per-record membership |
| as: user | Lexically bind the current resource for a nested check |
| if_empty | Explicit response to a **known complete zero** for every; not a rule about collection errors |

The model deliberately does not ask policy authors to express OVAL state operators, existence check families, variable graph internals or six-state aggregation in every file. Implementations must still handle actual absence, error, incomplete and unknown correctly, without hidden success defaults.

## Ten research examples

| Assessment | Direct sample | Evidence status |
| --- | --- | --- |
| Exact /home mount native rule | [Native](examples/10-native-home-policy.yaml) | New policy, not a source conversion |
| RHEL9 original /home regex | [Regex version](examples/01-linux-home.yaml) | Similar intent, source parity unproved |
| Windows Installer policy | [Registry](examples/02-windows-registry.yaml) | New typed registry check |
| Windows 11 deny Remote Desktop right | [Three paths](examples/03-windows-deny-rdp.yaml) | Mixed WMI record semantics unproved; cannot claim lossless conversion |
| Linux initialization files | [Dependent files](examples/04-linux-initialization-files.yaml) | Original Sets, field presence and collection flags not yet fully modeled |
| Apache KeepAlive and max requests | [Directives](examples/05-apache-directives.yaml) | Relies on unimplemented provider; original four-check graph is not yet preserved |
| Windows DNS zone signatures | [DNS](examples/06-windows-dns.yaml) | Relies on unimplemented zone/key provider and per-item correlation |
| Nested home-file ownership | [User-to-file](examples/07-nested-user-file-ownership.yaml) | Native example with lexical scope |
| Documented manual review | [Manual](examples/08-manual-assessment.yaml) | Requires assessor, date, POC and evidence |
| Conditional site time server | [Conditional](examples/09-conditional-time-source.yaml) | Site provenance and unknown branch explicit |

The [research validator](../../tools/research_requirements_first_04.py) and [adversarial tests](../../tools/test_research_requirements_first_04.py) check YAML structure, naming, known provider identifiers, lexical source references, nonempty all/any groups, explicit empty handling, and no silent OVAL-shaped fallback. This is **structural research validation only**. See [GitHub workflow](../../.github/workflows/research-requirements-first-04.yml) for CI.

## Where the hard work goes

An auditor-facing provider name is not a magic scanner implementation. Each typed provider must have an inspectable, versioned contract:

1. **Exact resource identity and inputs:** platforms, units, field types, selectors, collector permissions, configured aliases, and scope of cached results.
2. **Cardinality and provenance:** item identifiers, multi-valued fields, nested records, source path/line, ownership of nested relations and stable grouping.
3. **Collection statuses:** complete, incomplete, error, not collected, not applicable; absent field vs absent item; ordering and safe failure behavior.
4. **Evidence limits:** traversal caps, timeouts, partial indicators, deterministic results and scanner-controlled samples.
5. **Source migration:** a verifiable mapping from original content; publish non-equivalence counterexamples instead of silently changing the STIG.

**Hardest providers to prove:** Windows computer roles must preserve the distinction between two complete WMI record-State alternatives and per-record membership (mixed DomainRole [1,3] must not silently pass). Apache loaded directives must faithfully resolve loaded and included configs, precedence and duplicate directives, including original four-check behavior if claimed equivalent. DNS must preserve command-derived zone/key relationships and the original two separate lower/upper State comparisons, including repeated values. Linux dependent files must preserve original Set difference, root-vs-non-system populations, missing attributes and recursive traversal behavior.

The original SCAP 1.4 conversion remains a nonnegotiable project goal. **A short native policy is NOT the automatic converted form until source-level equivalence is proved.** Whether a separate internal compatibility execution mode is unavoidable is an explicit architecture question, not a reason to expose OVAL authoring to human auditors again.

## Self-critique across repeated passes (same assistant, not independent auditors)

| Challenge | Outcome |
| --- | --- |
| Does one simple check look clean? | Yes; but that alone is a trivial test |
| Are nested relations natural to author? | Named user/file binding is simpler than positional variable arrays; still needs provider field schema |
| Are zero resources dangerous? | Yes. Mandatory if_empty for every; root-account branch was fixed to fail when no root account is found |
| Can Windows WMI be flattened into a typed role? | **Not proven.** Mixed nested records are a major lossless conversion risk |
| Is Apache actually converted by a two-property check? | **No.** That check assumes a nontrivial, unimplemented loaded-config provider |
| Is DNS actually converted by one between range? | **No.** The real source uses distinct bound States and complex command Variables |
| Can field absence safely use a generic default? | **No.** Versioned provider and predicate contracts must define absence separately from unreadable and incomplete |
| Does a low line count prove anything? | **Only how much authors type.** It does not measure interpreter complexity or source-equivalent coverage |
| Does using generic all/any recreate OVAL? | No; necessary logic is not the problem. The problematic authoring burden is the Object/State/Test/Variable evaluator pipeline |

Five source-backed earlier YAML lengths compared with these new sketches: RHEL 30 versus 10 lines; Windows 130 versus 37; Linux files 138 versus 47; Apache 334 versus 17; DNS 177 versus 35. **Those numbers are not fair functional equivalence comparisons**, because provider implementation and real source cardinalities remain open.

## Research verdict

**Keep the requirements-first, typed-resource approach as the leading greenfield language candidate.** It is the first direction that lets an auditor write a normal policy without being trained in OVAL decomposition.

**Block normative adoption** until we prove typed provider contracts against actual source-level Windows, Linux, Apache and DNS counterexamples; synthetic partial/unknown/error behavior; and a credible plan for source-faithful SCAP 1.4 conversion. Do not task an editor implementation with a guessed provider contract. There is no need for another cosmetic synonym vote.

**Next iteration:** build the minimum provider contract and synthetic evidence fixtures for Linux mounts, Windows WMI role, Apache loaded directives, and DNS zones/keys; re-run cold reading against one fully backed complex example.
