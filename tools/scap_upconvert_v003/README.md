# SCAP 1.4 upconversion tools

The maintained human operator instructions live in
[Human-runnable SCAP-NG tools](../HUMAN-RUNNABLE-SCRIPTS.md).
That guide is the only supported command catalog; this page describes the
converter folder, not another procedure.

The conversion tool must preserve supported source meaning, retain pinned
source identities, and report deprecated/unsupported constructs instead of
silently accepting them. Conversion does not establish scanner-runtime
equivalence. Consult the [normative migration specification](../../specification/migration/scap-1.4-migration.md),
the [OVAL mapping](../../specification/migration/oval-5.12.3-to-ng.md),
and the [current review](../../review/current/README.md).

Historical `run_local.py` instructions and removed research-output paths
remain recoverable in Git history; they are not the current workflow.
