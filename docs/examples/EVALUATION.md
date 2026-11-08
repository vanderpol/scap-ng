# Evaluation status and limits

All ten cases are **illustrative expected outcomes, not native-evaluator-verified results**. The [validation ledger](validation.json) reports ten syntax-valid cases, zero native-verified cases and a null observed outcome for every case. Neither successful validation nor CI success upgrades this status.

The fixtures deliberately use one complete collection, one existing Item, existing primitive field values and explicit Item/field policies. Pass/Fail expectations follow the stated equality and are independently authored golden expectations; the generator does not calculate them. Each pair keeps the full authored Assessment identical and changes the relevant supplied value. This avoids guessing absence, unknown/error aggregation, recursion, registry views, RPM ordering, service state transitions or shell output splitting.

For these compliance teaching cases only, `true` is displayed as Pass and `false` as Fail. The frozen Result schema states that consuming Rules determine real policy outcomes. These examples do not establish host compliance or a universal technical-to-policy mapping.

## Available runtime investigation

| Component inspected | Observed scope | Why it cannot prove these examples |
| --- | --- | --- |
| This public schema/documentation repository at `7e27c23e53fdfdf018fa483a24b857462992b109` | Schemas, documentation generators and syntax witnesses | Contains no native Test/Require evaluator over collected Items. |
| Local canonical 0.4 result-plan backend, research snapshot `7e26f8da44a81ae96135eca837e611a3f99f9c28` | Supplied Test outcomes; explicitly excludes Test/State/Item/Variable collection | Feeding it the expected Test result would assume the result being proved. It was not used as evidence. |
| Local older expression/research runtimes | Older authoring contracts or candidate one-AST grammar; provider/Test evaluation supplied separately | Not qualified against the frozen native Object/Require/Item contract. No legacy adapter was invented. |
| Installed `scap-ng`, `scap-ng-scan`, `scap-ng-evaluate` commands | None found in the execution environment | No executable evaluator could be invoked. |

The investigation establishes availability in this run, not that no suitable evaluator exists elsewhere. It does not establish equivalence between the older research runtimes and current syntax.

To promote a case to verified, supply a qualified native evaluator that consumes the **complete fixture Assessment, collection result and Items**, pin its version/source and executable digest, record the exact input digest and observed technical result, and compare it with the independently authored expectation. Preserve diagnostic output and rejected/missing/error distinctions. Review that receipt before changing verification labels. A runtime consuming only supplied Test outcomes is insufficient.

## Capability boundaries

| Capability | Comparison demonstrated | Not established |
| --- | --- | --- |
| unix.file | Integer `owner_uid` equals 0 | Host collection, links, traversal, effective permissions or ACL behavior |
| windows.registry | Integer `value` equals 1 for a selected named value | Hive/view acquisition, access denial, expansion or missing-key behavior |
| independent.shellcommand | String `stdout_line` equals `"64"` | Execution, splitting/cardinality, STDERR/error aggregation or dependency availability |
| linux.rpminfo | String architecture equals `x86_64` | Package discovery, RPM EVR ordering or epoch normalization |
| windows.service | Startup configuration equals `SERVICE_DISABLED` | Current running state, service transitions or collection failures |

The shellcommand fixture targets a system with `sh` and `/usr/bin/getconf LONG_BIT`; the named utility is an explicit example dependency, not a guaranteed native facility. Both fixtures supply exit status 0 and one output field; the command is not executed. All Item provenance explicitly identifies synthetic documentation evidence.
