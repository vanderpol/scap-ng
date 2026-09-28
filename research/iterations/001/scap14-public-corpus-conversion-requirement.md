# SCAP 1.4 Public-Corpus Conversion Requirement

**Status:** Hard pre-specification requirement  
**Applies to:** SCAP-NG information model, migration model, and every supported human-authoring syntax

## Requirement

Before the SCAP-NG specification is considered ready to finalize, the project must demonstrate repeatable forward conversion of the declared public SCAP 1.4 corpus **after excluding definitions that still use deprecated OVAL tests as explicit source-remediation blockers**.

This is not satisfied by hand-converting representative examples. For iteration 001, the authoritative public corpus is the pinned NIWC Atlantic `scap-content-library/Current` tree recorded in `public-corpus-manifest.yaml`.

The demonstration must use an automated corpus converter and a versioned corpus manifest so an independent reviewer can rerun the same test.

## Public corpus definition

"All public content" must be operationally defined by a checked-in corpus manifest rather than by an open-ended Internet search.

Each corpus source must record, where applicable:

- publisher/repository;
- immutable source revision or download date;
- source path/URL;
- file digest;
- benchmark/datastream identity;
- SCAP version;
- acquisition notes.

The manifest may grow over time. A published conversion report is meaningful only relative to a specific manifest revision.

## Priority depth pass

Before attempting native conversion across the whole corpus, iteration 001 will develop and stress the semantic IR against four current published anchors:

- RHEL 9;
- Oracle Linux 9;
- Windows 11;
- Windows Server 2025.

RHEL 9 and Oracle Linux 9 are paired to quantify Linux cross-distribution reuse. Windows 11 and Windows Server 2025 are paired to quantify client/server reuse.

These priorities do not weaken the final all-benchmark gate.

## Conversion pipeline

```text
public SCAP 1.4 corpus
        |
        v
safe acquisition / extraction
        |
        v
SCAP document identification
        |
        v
faithful semantic intermediate representation
        |
        +-----------------------+
        |                       |
        v                       v
original NG YAML       Ansible-inspired NG YAML
        \                       /
         \                     /
          v                   v
             canonical NG model
                    |
                    v
           signed .scapng package
```

The authoring renderings are views of the same migrated semantics. They do not define separate runtimes.

## Required migration status

Every converted policy/check component receives one of:

- `exact_native`
- `exact_normalized`
- `legacy_compatible`
- `requires_review`
- `unsupported`

Statuses must be machine-readable and accompanied by construct-level reasons.

No construct may be silently discarded, replaced with a weaker check, or treated as compliant because conversion was incomplete.

### Deprecated OVAL test boundary

SCAP-NG intentionally excludes every OVAL test type whose effective status remains deprecated after accounting for later OVAL Community governance decisions. Historical `deprecated_info` is retained as provenance, but explicit reinstatement decisions override the raw 5.12 annotation for scope classification.

If a definition references an effectively deprecated OVAL test:

- conversion of that definition must stop with `unsupported` and reason `deprecated_oval_test`;
- the converter must identify the offending test type and supported replacement when documented;
- the converter must not automatically rewrite the test;
- the source SCAP 1.4 content must be updated and validated before conversion is retried.

These blockers are source-remediation requirements, not SCAP-NG specification blockers and not native-runtime coverage requirements. The corpus report must count and identify them separately. The support decision must also preserve evidence for any reinstatement override so reviewers can distinguish historical deprecation from current OVAL governance.

## Gates

### Gate 1 — corpus ingestion

Every declared corpus artifact must:

- be opened safely;
- be identified as datastream/XCCDF/OVAL/OCIL/CPE/other known SCAP content;
- have an immutable digest;
- have all embedded/referenced components inventoried;
- produce semantic-inventory output;
- report parse/reference/schema problems explicitly.

Passing this gate proves coverage of the corpus, not semantic conversion.

### Gate 2 — migration accounting

Every rule/check/definition in the corpus must receive a migration status and construct-level accounting.

The report must have:

- zero unaccounted definitions/checks;
- zero silently ignored XML constructs;
- counts by component type and OVAL platform/test type;
- counts by migration status;
- provenance linking every NG object to its SCAP 1.4 source.

### Gate 3 — native semantic coverage

Before specification finalization, configuration-assessment content should reach `exact_native` or `exact_normalized` across the declared corpus, except for narrowly documented exceptions explicitly accepted during standards review.

`legacy_compatible` is a migration safety valve, not evidence that the native language is complete.

Any remaining `requires_review` or `unsupported` construct is a specification blocker unless the standards group explicitly determines that the construct is out of scope. Definitions blocked specifically by `deprecated_oval_test` are already declared out of SCAP-NG scope and instead block conversion of that source content until the publisher updates it.

### Gate 4 — differential equivalence

Representative fixtures for every semantic construct family must compare original SCAP/OVAL and NG execution.

Compare:

- applicability;
- Pass/Fail/N/A/Error/other outcome;
- required evidence completeness;
- parameter behavior;
- decisive evidence;
- error propagation;
- boundary conditions.

Native conversion status must not be promoted solely because source files can be parsed or rendered.

## Authoring-syntax requirement

Both the original research YAML and the Ansible-inspired YAML experiment must be renderable from the same faithful semantic intermediate representation.

For a converted source case:

```text
SCAP 1.4
   -> semantic IR
       -> original YAML
       -> Ansible-inspired YAML

original YAML ------------\
                           > canonical semantics must match
Ansible-inspired YAML ----/
```

If one authoring syntax cannot represent a corpus construct that the other can, that is evidence against the incomplete syntax.

## Required reporting

The corpus converter should eventually produce, at minimum:

- `corpus-summary.json`
- `documents.json`
- `construct-inventory.json`
- `migration-status.json`
- per-source provenance
- per-definition conversion diagnostics
- authoring renderings when available
- canonical-semantic digests
- unresolved/blocking construct report

A human-readable summary may be generated from the same machine-readable data.

## Why this is a release criterion

SCAP-NG succeeds only if organizations can carry forward existing tested content.

A clean new language that requires the public SCAP corpus to be rewritten manually would impose unacceptable adoption cost and would discard much of the operational confidence accumulated in existing content.

The public-corpus conversion demonstration is therefore part of the evidence for the specification itself, not merely a post-standardization implementation project.
