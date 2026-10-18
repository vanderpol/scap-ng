# 0.4-B source State and Boolean fixture test gate

**GitHub Actions research only; not a SCAP 1.4 parity certification.**

| Stage | Most recent push gate outcome |
| --- | --- |
| Source State fixture tests | success |
| Source Boolean fixture tests | success |
| Windows WMI source fixture tests |  |

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
Ran 15 tests in 0.018s

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
Ran 7 tests in 0.027s

OK
~~~
### work/b-corpus/wmi-test.log

~~~text
Step skipped; inspect Actions earlier steps.
~~~
