# 0.4-B source State, Boolean, WMI and registry fixture test gate

**GitHub Actions research only; not a SCAP 1.4 parity certification.**

| Stage | Most recent push gate outcome |
| --- | --- |
| Source State fixture tests | success |
| Source Boolean fixture tests | success |
| Windows WMI source fixture tests | success |
| Windows registry source fixture tests | success |
| Registry type/value AND same-Item tests | success |
| Shell source command stdout Item tests | success |
| Apache Variable DAG source fixture tests | success |
| Typed Variable value operator tests | failure |

## Failed/skipped test diagnostics

### work/b-corpus/state-test.log

~~~text
test_absent_file_and_nonmatching_file_not_false_pass (tools.test_research_b_source_textfile_state.CollectedStateTests.test_absent_file_and_nonmatching_file_not_false_pass) ... ok
test_all_matching_instances_must_pass (tools.test_research_b_source_textfile_state.CollectedStateTests.test_all_matching_instances_must_pass) ... ok
test_boolean_is_not_a_source_integer_literal (tools.test_research_b_source_textfile_state.CollectedStateTests.test_boolean_is_not_a_source_integer_literal) ... ok
test_compiler_owned_state_survives_typed_json_roundtrip (tools.test_research_b_source_textfile_state.CollectedStateTests.test_compiler_owned_state_survives_typed_json_roundtrip) ... ok
test_duplicate_and_wrong_acquisition_rejected (tools.test_research_b_source_textfile_state.CollectedStateTests.test_duplicate_and_wrong_acquisition_rejected) ... ok
test_incomplete_success_and_failure_preserve_source_state_truth (tools.test_research_b_source_textfile_state.CollectedStateTests.test_incomplete_success_and_failure_preserve_source_state_truth) ... ok
test_invalid_state_regex_rejected_at_compile_and_ir_decode (tools.test_research_b_source_textfile_state.CollectedStateTests.test_invalid_state_regex_rejected_at_compile_and_ir_decode) ... ok
test_less_than_and_less_than_or_equal_keep_exact_comparison (tools.test_research_b_source_textfile_state.CollectedStateTests.test_less_than_and_less_than_or_equal_keep_exact_comparison) ... ok
test_missing_and_bad_entity_fields_fail_without_silent_removal (tools.test_research_b_source_textfile_state.CollectedStateTests.test_missing_and_bad_entity_fields_fail_without_silent_removal) ... ok
test_nonmatching_multiple_capture_groups_are_field_error (tools.test_research_b_source_textfile_state.CollectedStateTests.test_nonmatching_multiple_capture_groups_are_field_error) ... ok
test_source_capture_match_pass_and_fail (tools.test_research_b_source_textfile_state.CollectedStateTests.test_source_capture_match_pass_and_fail) ... ok
test_source_state_pattern_match_keeps_typed_regex_field_semantics (tools.test_research_b_source_textfile_state.CollectedStateTests.test_source_state_pattern_match_keeps_typed_regex_field_semantics) ... ok
test_terminal_flags_and_missing_source (tools.test_research_b_source_textfile_state.CollectedStateTests.test_terminal_flags_and_missing_source) ... ok
test_typed_integer_bounds_and_canonical_capture_gates (tools.test_research_b_source_textfile_state.CollectedStateTests.test_typed_integer_bounds_and_canonical_capture_gates) ... ok
test_unsupported_source_shapes_rejected (tools.test_research_b_source_textfile_state.CollectedStateTests.test_unsupported_source_shapes_rejected) ... ok

----------------------------------------------------------------------
Ran 15 tests in 0.023s

OK
~~~
### work/b-corpus/boolean-test.log

~~~text
test_and_preserves_unknown_if_required_query_missing (tools.test_research_b_source_boolean_lowering.MultiTestTests.test_and_preserves_unknown_if_required_query_missing) ... ok
test_both_tests_lower_to_source_owned_nodes_no_second_author_grammar (tools.test_research_b_source_boolean_lowering.MultiTestTests.test_both_tests_lower_to_source_owned_nodes_no_second_author_grammar) ... ok
test_duplicate_acquisition_identity_is_error_not_arbitrary_first_wins (tools.test_research_b_source_boolean_lowering.MultiTestTests.test_duplicate_acquisition_identity_is_error_not_arbitrary_first_wins) ... ok
test_nested_logic_and_all_source_tests_required (tools.test_research_b_source_boolean_lowering.MultiTestTests.test_nested_logic_and_all_source_tests_required) ... ok
test_or_one_witness_overrides_second_branch_unknown (tools.test_research_b_source_boolean_lowering.MultiTestTests.test_or_one_witness_overrides_second_branch_unknown) ... ok
test_typed_distinct_acquisitions_are_both_required (tools.test_research_b_source_boolean_lowering.MultiTestTests.test_typed_distinct_acquisitions_are_both_required) ... ok
test_unreachable_or_unsupported_check_cannot_be_dropped (tools.test_research_b_source_boolean_lowering.MultiTestTests.test_unreachable_or_unsupported_check_cannot_be_dropped) ... ok

----------------------------------------------------------------------
Ran 7 tests in 0.025s

OK
~~~
### work/b-corpus/wmi-test.log

~~~text
test_incomplete_query_cannot_prove_clean_but_a_bad_disk_is_decisive (tools.test_research_b_source_wmi.WmiSourceTests.test_incomplete_query_cannot_prove_clean_but_a_bad_disk_is_decisive) ... ok
test_malformed_rows_fail_closed (tools.test_research_b_source_wmi.WmiSourceTests.test_malformed_rows_fail_closed) ... ok
test_no_non_ntfs_local_disks_is_true_and_any_bad_disk_is_false (tools.test_research_b_source_wmi.WmiSourceTests.test_no_non_ntfs_local_disks_is_true_and_any_bad_disk_is_false) ... ok
test_query_errors_and_not_applicable_are_preserved (tools.test_research_b_source_wmi.WmiSourceTests.test_query_errors_and_not_applicable_are_preserved) ... ok
test_real_w11_ntfs_source_structure_and_compiled_ir (tools.test_research_b_source_wmi.WmiSourceTests.test_real_w11_ntfs_source_structure_and_compiled_ir) ... ok
test_status_with_items_and_duplicate_ids_are_not_accepted (tools.test_research_b_source_wmi.WmiSourceTests.test_status_with_items_and_duplicate_ids_are_not_accepted) ... ok
test_unsafe_or_unsupported_source_shapes_rejected (tools.test_research_b_source_wmi.WmiSourceTests.test_unsafe_or_unsupported_source_shapes_rejected) ... ok
test_wrong_query_cannot_prove_absence (tools.test_research_b_source_wmi.WmiSourceTests.test_wrong_query_cannot_prove_absence) ... ok

----------------------------------------------------------------------
Ran 8 tests in 0.010s

OK
~~~
### work/b-corpus/registry-test.log

~~~text
test_bluetooth_source_provenance_and_no_assumed_registry_view (tools.test_research_b_source_registry.RegistrySourceTests.test_bluetooth_source_provenance_and_no_assumed_registry_view) ... ok
test_incomplete_sources_cannot_claim_a_matched_clean_state (tools.test_research_b_source_registry.RegistrySourceTests.test_incomplete_sources_cannot_claim_a_matched_clean_state) ... ok
test_invalid_snapshot_row_does_not_prove_absence (tools.test_research_b_source_registry.RegistrySourceTests.test_invalid_snapshot_row_does_not_prove_absence) ... ok
test_numeric_zero_is_not_source_lexical_string_zero (tools.test_research_b_source_registry.RegistrySourceTests.test_numeric_zero_is_not_source_lexical_string_zero) ... ok
test_one_match_is_not_the_same_as_one_collected_item (tools.test_research_b_source_registry.RegistrySourceTests.test_one_match_is_not_the_same_as_one_collected_item) ... ok
test_registry_views_disagree_then_result_is_unknown_not_64bit_default (tools.test_research_b_source_registry.RegistrySourceTests.test_registry_views_disagree_then_result_is_unknown_not_64bit_default) ... ok
test_source_metadata_or_dynamic_operators_fail_closed (tools.test_research_b_source_registry.RegistrySourceTests.test_source_metadata_or_dynamic_operators_fail_closed) ... ok
test_terminal_statuses_and_missing_snapshot_are_not_equivalent_to_absence (tools.test_research_b_source_registry.RegistrySourceTests.test_terminal_statuses_and_missing_snapshot_are_not_equivalent_to_absence) ... ok
test_wrong_view_identity_untrusted_types_and_duplicates_fail_closed (tools.test_research_b_source_registry.RegistrySourceTests.test_wrong_view_identity_untrusted_types_and_duplicates_fail_closed) ... ok

----------------------------------------------------------------------
Ran 9 tests in 0.016s

OK
~~~
### work/b-corpus/registry-and-test.log

~~~text
test_compound_state_rejects_extra_unknown_required_fields (tools.test_research_b_source_registry_and.RegistryAndSourceTests.test_compound_state_rejects_extra_unknown_required_fields) ... ok
test_incomplete_and_conflicting_views_do_not_claim_complete_success (tools.test_research_b_source_registry_and.RegistryAndSourceTests.test_incomplete_and_conflicting_views_do_not_claim_complete_success) ... ok
test_ir_validation_refuses_split_item_bypass (tools.test_research_b_source_registry_and.RegistryAndSourceTests.test_ir_validation_refuses_split_item_bypass) ... ok
test_real_wdigest_source_and_same_item_field_identity (tools.test_research_b_source_registry_and.RegistryAndSourceTests.test_real_wdigest_source_and_same_item_field_identity) ... ok
test_type_and_value_must_both_match_on_each_collected_item (tools.test_research_b_source_registry_and.RegistryAndSourceTests.test_type_and_value_must_both_match_on_each_collected_item) ... ok

----------------------------------------------------------------------
Ran 5 tests in 0.011s

OK
~~~
### work/b-corpus/source-shell-test.log

~~~text
test_direct_real_dns_source_retains_literal_command_identity (tools.test_research_b_source_shell.SourceShellTests.test_direct_real_dns_source_retains_literal_command_identity) ... ok
test_dns_enable_proven_only_with_exact_single_item_stdout_entity (tools.test_research_b_source_shell.SourceShellTests.test_dns_enable_proven_only_with_exact_single_item_stdout_entity) ... ok
test_dynamic_apache_command_cannot_be_guessed (tools.test_research_b_source_shell.SourceShellTests.test_dynamic_apache_command_cannot_be_guessed) ... ok
test_incomplete_collection_and_terminal_errors_cannot_claim_false_pass (tools.test_research_b_source_shell.SourceShellTests.test_incomplete_collection_and_terminal_errors_cannot_claim_false_pass) ... ok
test_multivalued_stdout_does_not_become_several_source_items (tools.test_research_b_source_shell.SourceShellTests.test_multivalued_stdout_does_not_become_several_source_items) ... ok
test_snapshot_source_flags_must_be_honored_when_true (tools.test_research_b_source_shell.SourceShellTests.test_snapshot_source_flags_must_be_honored_when_true) ... ok
test_source_change_to_unsupported_shell_or_regex_fails_closed (tools.test_research_b_source_shell.SourceShellTests.test_source_change_to_unsupported_shell_or_regex_fails_closed) ... ok
test_source_literal_stdout_empty_is_not_absence_of_stdout (tools.test_research_b_source_shell.SourceShellTests.test_source_literal_stdout_empty_is_not_absence_of_stdout) ... ok
test_wrong_command_or_malformed_line_array_is_not_accepted (tools.test_research_b_source_shell.SourceShellTests.test_wrong_command_or_malformed_line_array_is_not_accepted) ... ok

----------------------------------------------------------------------
Ran 9 tests in 0.018s

OK
~~~
### work/b-corpus/source-apache-test.log

~~~text
test_compiled_graph_tampering_rejected (tools.test_research_b_apache_version_graph.ApacheVariableGraphTests.test_compiled_graph_tampering_rejected) ... ok
test_compiler_census_rebuilds_apache_source_leaf_and_rejects_tampering (tools.test_research_b_apache_version_graph.ApacheVariableGraphTests.test_compiler_census_rebuilds_apache_source_leaf_and_rejects_tampering) ... ok
test_duplicate_source_paths_are_not_implicitly_unique (tools.test_research_b_apache_version_graph.ApacheVariableGraphTests.test_duplicate_source_paths_are_not_implicitly_unique) ... ok
test_dynamic_query_name_must_match_exact_derived_executable (tools.test_research_b_apache_version_graph.ApacheVariableGraphTests.test_dynamic_query_name_must_match_exact_derived_executable) ... ok
test_multivalued_version_entity_aggregation_within_one_item (tools.test_research_b_apache_version_graph.ApacheVariableGraphTests.test_multivalued_version_entity_aggregation_within_one_item) ... ok
test_process_path_derived_without_executing_shell (tools.test_research_b_apache_version_graph.ApacheVariableGraphTests.test_process_path_derived_without_executing_shell) ... ok
test_provider_provenance_cannot_be_swapped_without_failure (tools.test_research_b_apache_version_graph.ApacheVariableGraphTests.test_provider_provenance_cannot_be_swapped_without_failure) ... ok
test_real_apache_source_variables_and_executable_ir (tools.test_research_b_apache_version_graph.ApacheVariableGraphTests.test_real_apache_source_variables_and_executable_ir) ... ok
test_renamed_variables_preserve_graph_semantics_without_magic_ids (tools.test_research_b_apache_version_graph.ApacheVariableGraphTests.test_renamed_variables_preserve_graph_semantics_without_magic_ids) ... ok
test_unknown_graph_shapes_rejected_by_lowerer (tools.test_research_b_apache_version_graph.ApacheVariableGraphTests.test_unknown_graph_shapes_rejected_by_lowerer) ... ok
test_unresolved_dependency_not_blind_true_or_false (tools.test_research_b_apache_version_graph.ApacheVariableGraphTests.test_unresolved_dependency_not_blind_true_or_false) ... ok
test_unverified_version_suffix_and_bad_evidence_are_errors (tools.test_research_b_apache_version_graph.ApacheVariableGraphTests.test_unverified_version_suffix_and_bad_evidence_are_errors) ... ok

----------------------------------------------------------------------
Ran 12 tests in 0.034s

OK
~~~
### work/b-corpus/variable-ops-test.log

~~~text
test_actual_apache_regex_capture_and_concat_preserve_source_graph (tools.test_research_b_variable_value_ops.VariableValueOpsTests.test_actual_apache_regex_capture_and_concat_preserve_source_graph) ... ok
test_cartesian_cardinality_is_capped_not_truncated (tools.test_research_b_variable_value_ops.VariableValueOpsTests.test_cartesian_cardinality_is_capped_not_truncated) ... ok
test_no_values_not_equivalent_to_false_or_empty_string (tools.test_research_b_variable_value_ops.VariableValueOpsTests.test_no_values_not_equivalent_to_false_or_empty_string) ... FAIL
test_regex_capture_requires_one_group_and_bounded_strings (tools.test_research_b_variable_value_ops.VariableValueOpsTests.test_regex_capture_requires_one_group_and_bounded_strings) ... FAIL
test_two_different_executables_produce_two_query_identities (tools.test_research_b_variable_value_ops.VariableValueOpsTests.test_two_different_executables_produce_two_query_identities) ... ok
test_typed_envelope_cannot_carry_partial_unverified_values (tools.test_research_b_variable_value_ops.VariableValueOpsTests.test_typed_envelope_cannot_carry_partial_unverified_values) ... ok
test_unique_explicitly_reduces_duplicates_only_when_requested (tools.test_research_b_variable_value_ops.VariableValueOpsTests.test_unique_explicitly_reduces_duplicates_only_when_requested) ... ok
test_unknown_and_error_do_not_become_empty_or_success (tools.test_research_b_variable_value_ops.VariableValueOpsTests.test_unknown_and_error_do_not_become_empty_or_success) ... ok

======================================================================
FAIL: test_no_values_not_equivalent_to_false_or_empty_string (tools.test_research_b_variable_value_ops.VariableValueOpsTests.test_no_values_not_equivalent_to_false_or_empty_string)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/scap-ng/scap-ng/tools/test_research_b_variable_value_ops.py", line 50, in test_no_values_not_equivalent_to_false_or_empty_string
    self.assertEqual(capture(values(["unrelated-process"]),r"(httpd)"),
AssertionError: {'status': 'values', 'values': ['']} != {'status': 'no_values', 'values': []}
- {'status': 'values', 'values': ['']}
?                                 --

+ {'status': 'no_values', 'values': []}
?             +++


======================================================================
FAIL: test_regex_capture_requires_one_group_and_bounded_strings (tools.test_research_b_variable_value_ops.VariableValueOpsTests.test_regex_capture_requires_one_group_and_bounded_strings)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/scap-ng/scap-ng/tools/test_research_b_variable_value_ops.py", line 83, in test_regex_capture_requires_one_group_and_bounded_strings
    self.assertEqual(capture(values(["a1"]),r"(a)(1)"),
AssertionError: {'status': 'values', 'values': ['a']} != {'status': 'error', 'values': []}
- {'status': 'values', 'values': ['a']}
?             ---- ^              ---

+ {'status': 'error', 'values': []}
?              ^^^^


----------------------------------------------------------------------
Ran 8 tests in 0.006s

FAILED (failures=2)
~~~
