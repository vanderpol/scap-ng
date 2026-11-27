# OVAL 6.0 experimental ESXi evidence

The four experimental 0.4.1 mappings use only new OVAL 6.0 Test families,
pinned to `5afcf590fb5d334687bfdc47f98716424cdb7f3d`. The fixtures exercise
independent field comparisons and keep selector identity fixed across
positive and negative evidence. The string category `Unknown` for a VIB
has ordinary comparison semantics.

The Assessment, typed inputs and expected results are in separate files.
The local gate validates authoring and compares the specified known evidence.
Live ESXi and cross-implementation results remain open. The sixteen
proposal-only Test families and their source inventory remain in
[the separate Issue #86 proposal](../../../proposed/issue86-esx-oval6/README.md).
