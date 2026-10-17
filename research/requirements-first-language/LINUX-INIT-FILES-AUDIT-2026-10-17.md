# Linux initialization files — source scope and permission-mode research

17 October 2026. Research #235 (authoring) and #229 (source semantics), not normative 0.4 or a proven OVAL conversion.

Source: [complete SCAP 1.4-derived source-backed YAML](../assessment-simplification/english-first-04/canonical-operators/linux-files.canonical.research.yaml). New [source-conscious native draft](experiments/linux-init-global-population.yaml). Both remain separate from implemented source-equivalent scanner logic.

## First critical discovery: global file population versus per-account files

The original Assessment has two Tests joined with AND.

- Non-system accounts: username regex, UID 1000 or above, home directory other than /; collect initialization files across all selected users. The test permits the file population to be absent (if_present). Every selected file must satisfy eight permission flags, with all compared fields present.
- Root accounts: UID zero, home directory other than /; collect initialization files across ALL selected root accounts. The Test requires at least one file Item **in the combined collection** (at_least_one) and requires every selected file to comply.

**Falsifying case:** Two UID-0 accounts each have different home directories. One account has no selected files. The other has one compliant mode-0600 initialization file. With complete evidence, the original combined-root-file Test can Pass; the tempting nested model requiring one file for EACH root account would Fail. The earlier [nested candidate](examples/04-linux-initialization-files.yaml) is therefore a known possible semantic regression, not an endorsed faithful converter.

The [new candidate](experiments/linux-init-global-population.yaml) places one minimum_resources: 1 on the selected union of root-derived files. This depends on a general, reusable file collection sourced from account home directories, not an opaque per-STIG compliance-verdict provider.

## Second critical discovery: file mode 0644 fails despite 0644 <= 0740

The original source explicitly compares all EIGHT permission fields to false:

- setuid, setgid, sticky
- group_write, group_execute
- other_read, other_write, other_execute

For a complete POSIX 12-bit mode, these forbidden bits have combined octal mask 07037. The **allowed** bits mask is octal 0740. Hence equivalent native meaning is that the selected mode has *no bits other than bits present in 0740*:

~~~text
(mode & ~0740) == 0
~~~

This is **bitset subset**, not an ordinary numeric less-than-or-equal operation. Octal 0644 is numerically lower than 0740, but its other-read permission is set: it fails. Octal 0600 and 0740 satisfy the eight flags; 0741 and 04740 do not.

The [exhaustive source-oriented test](../../tools/test_research_linux_init_permissions.py) loops through **all 4,096 possible 12-bit POSIX modes**, showing equivalence between the eight field Boolean conditions and permitted-bit subsetting under the restricted complete-value assumption.

A sensible typed native predicate can express:

~~~yaml
must:
  mode: {only_these_bits: '0740'}
~~~

The octal string requires a precise typed interpretation. Generic numerical comparison, lexical ordering, or undocumented max_mode semantics would be unsafe.

## Other source facts not to lose

The original acquisition uses named account sources, difference and union, a filename regex beginning with a dot, max_depth 1, traversal of symlinks, filesystem all, and directory exclusion. The source username regex is unanchored. Full-field presence is mandatory. Our test pins these source configurations, but **does not run them**.

The new sketch has intuitive acquisition instructions, but its filesystem boundaries, symlink recursion, duplicate path identity, Set difference semantics and original OVAL evaluation statuses remain **unproved**. A single numeric mode is not automatically equivalent to eight separately reported fields when fields can be missing, unreadable, or partially collected.

## What changes in the authoring direction

**Keep** the idea of reusable, typed resource providers and the one general requirement engine. For these Linux rules, a well-defined POSIX bitmask operation genuinely simplifies the expected security property. Reusable files-from-accounts discovery remains a provider capability that must expose the source population, union scope, account-to-file provenance and failures.

**Avoid** accidental changes when moving a minimum-resource condition inside nested foreach loops; the boundary being counted is part of policy semantics and belongs in both editor explanations and conversion testing.

This finding is more valuable than shortening the YAML. It identifies a testable technical property and a source-compatibility regression before a scanner exists.

**Review request:** No Gemini task needed yet. A further independent review should receive the original source graph, typed provider contract, and both global-versus-per-account counterexamples, not a vocabulary-only question.
