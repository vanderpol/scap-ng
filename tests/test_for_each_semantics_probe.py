from tools.for_each_semantics_probe import run, oval_cartesian_product, bound_elementwise_product, equals_with_var_check, iterate_values_exist

def test_cartesian_not_same_item_pairing():
    rows=[{"a":2,"b":10},{"a":3,"b":20}]
    assert oval_cartesian_product(rows,"a","b")==[20,40,30,60]
    assert bound_elementwise_product(rows,"a","b")==[20,60]

def test_var_check_all_is_not_iteration_all():
    vals=["/a","/b"]
    assert equals_with_var_check("/a",vals,"all") is False
    assert iterate_values_exist({"/a","/b"},vals,"all") is True

def test_probe_suite():
    run()
