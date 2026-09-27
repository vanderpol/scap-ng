# RHEL 10 SV-281050 / SV-281053 normalization note

The two OVAL definitions have nearly identical local-variable, group-name lookup, and dynamic GID-comparison machinery.

Iteration 001 intentionally keeps them as **separate assessment identities** even though their prototype native representations are nearly identical.

Reason: similarity of implementation is not sufficient evidence of semantic equivalence. Before normalization into one shared assessment, differential fixtures should prove equivalent behavior for:

- no explicit `log_group`;
- explicit `root`;
- explicit resolvable non-root group;
- explicit unresolvable group;
- conflicting repeated directives;
- missing log file;
- wrong root GID;
- wrong configured-group GID.

This case is useful evidence for the rule that normalization/reuse follows equivalence testing rather than preceding it.
