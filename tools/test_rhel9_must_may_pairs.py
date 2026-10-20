# RHEL 9 item requirement vocabulary: executable reversible subset
# Research only; no changes to 0.4-A or claim of scanner parity.
# Refs #227, #246. Run: python3 tools/test_rhel9_must_may_pairs.py
A_TO_WORDS = {
    'at_least_one_exists_and_all_match': ('one_or_more', 'all_items_must'),
    'may_be_absent_and_all_match': ('may_be_absent', 'all_items_must'),
    'none_exist': ('none', None),
    'only_one_exists': ('exactly_one', None),
    'only_one_exists_and_matches': ('exactly_one', 'all_items_must'),
}
WORDS_TO_A = {v: k for k, v in A_TO_WORDS.items()}

def to_words(token, has_states):
    if token not in A_TO_WORDS:
        raise ValueError('unsupported token')
    items, quant = A_TO_WORDS[token]
    if (quant is None) == has_states:
        raise ValueError('Stateful/State-free Test token mismatch')
    return {'items': items, **({quant: True} if quant else {})}

def to_a(words, has_states):
    if not isinstance(words, dict) or 'items' not in words:
        raise ValueError('explicit Item existence is required')
    if any(k not in {'items', 'all_items_must'} for k in words):
        raise ValueError('unsupported matching vocabulary')
    if words.get('all_items_must', True) is not True:
        raise ValueError('invalid must operand')
    quant = 'all_items_must' if 'all_items_must' in words else None
    if (quant is None) == has_states:
        raise ValueError('Stateful/State-free Test mismatch')
    try:
        return WORDS_TO_A[(words['items'], quant)]
    except (KeyError, TypeError):
        raise ValueError('unproven existence/matching combination')

def test():
    for token in A_TO_WORDS:
        has_states = token not in ('none_exist', 'only_one_exists')
        assert to_a(to_words(token, has_states), has_states) == token
    for words, states in [
        ({'items': 'none', 'all_items_must': True}, True),
        ({'items': 'one_or_more', 'no_items_may': True}, True),
        ({'items': 'one_or_more'}, True),
        ({'items': 'none'}, True),
        ({'items': 'one_or_more', 'all_items_must': False}, True),
        ({'items': 'one_or_more', 'all_items_must': True}, False),
        ({'items': 'exactly_one', 'exactly_one_item_must': True}, True),
    ]:
        try:
            to_a(words, states)
        except ValueError:
            continue
        raise AssertionError((words, states))
    print('5 pair roundtrips + 7 ambiguity/unsupported rejections passed')

if __name__ == '__main__':
    test()
