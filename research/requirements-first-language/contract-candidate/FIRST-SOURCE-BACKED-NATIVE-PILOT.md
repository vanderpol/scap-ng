# B native compiler pilot against real six-stream source Assessments

**Research only — 17 October 2026. No normative 0.4.0-B, scanner or source-equivalence assertion.** This is capability development for B and **not** a B-vs-A bake-off. Source specimens come from the published converted **SCAP-NG 0.3 six-STIG authoring ZIP**, not original raw SCAP 1.4 XML.

The [complete six-stream source inventory](corpus/feature-inventory.md) revealed a high-volume `independent.textfilecontent54` family in Linux STIGs, together with pure existence tests not naturally expressed by B's old `each / must` grammar. The [12 real source specimens](corpus/source-specimens/README.md) are now published on GitHub for repeatable B development.

## Source-shape pilot 1: mount must exist

[Actual source Assessment](corpus/source-specimens/linux-partition-0-88d5c4811f61.source.yaml) `ng.shared.var-tmp-is-mounted` specifies an OVAL-derived `linux.partition` Test with `existence: one_or_more`, `match: all`, a `mount_point == /var/tmp` selector, and **no States**.

Research B now supports this **native policy**:

~~~yaml
require:
  exists: linux.mounts
  where:
    mount_point: {equals: /var/tmp}
~~~

[Executable native example](examples/09-linux-var-tmp-exists.yaml) and [automatically generated auditor explanation](generated-explanations/09-linux-var-tmp-exists.md). The compiled `exists` form lowers to the existing typed `some`-witness IR with no invented `must` property.

Fixture tests establish B's own evidence logic: completely observed absence -> False, observed matching mount -> True, incomplete zero -> Unknown, observed matching mount even if later discovery incomplete -> True. **The current mountinfo collector only sees the current Linux namespace**, not necessarily the original OVAL `linux.partition` collection. The test pins source-selection and existence *structure*, NOT scanner parity.

## Source-shape pilot 2: text-file regex match must exist

[Actual source Assessment](corpus/source-specimens/independent-textfilecontent54-0-4c14428014be.source.yaml) `ng.shared.etc-chrony-conf-cmdport-option-is-set-to-0` uses `independent.textfilecontent54`, `existence: one_or_more`, `match: all`, an exact `/etc/chrony.conf` source path, anchored whitespace-aware `cmdport 0` regex, `instance >= 1`, `multiline: true`, `singleline: false`, `ignore_case: false` and source-specific `item_creation`.

Research B now supports this **native requirement**:

~~~yaml
require:
  exists: linux.textfile_matches
  using:
    path: /etc/chrony.conf
    pattern: '^[ \t]*cmdport[ \t]+0[ \t]*$'
    ignore_case: false
    multiline: true
    singleline: false
~~~

[Native YAML](examples/10-linux-chrony-cmdport.yaml), [typed provider](../../tools/research_provider_textfile_matches.py), [versioned scope contract](../providers/linux.textfile_matches.v0.1.yaml), and [tests using real temporary files](../../tools/test_research_provider_textfile_matches.py).

The provider returns matched texts, source offsets, 1-based match-instance IDs, explicit source-query identity, and complete/incomplete/error diagnostics for absent file, too-large input, too many matches, symlinks and unreadable encoding. Source matching is **Python `re` over strict UTF-8**, not verified OVAL regex `pattern_match` semantics, filesystem search behavior or source Item-creation rules. It is a new native provider, **not a certified compiler lowering**.

## Where we stand

The two native policy **shapes** are now backed by actual source Assessment files and fixture execution. All source IDs and restrictions remain visible for future parity tests. They do NOT convert the 2,395 referenced Assessments or prove even these two examples' six-state source equivalence. The B importer currently retains the entire remaining corpus as explicitly **nonexecutable source capsules**, never labeling those as converted native policies.

The next engineering gate is to reconcile regex-instance, field status and object creation semantics against original SCAP 1.4 OVAL (including inaccessible files, source `item_creation` flags and repeated matches). Then implement the other high-volume families: Windows registry, audit-event-policy, user rights and WMI, and more general Linux file/search operations.

**No bake-off** until B covers the same full six-stream feature cohort as A with comparable validated functionality.
