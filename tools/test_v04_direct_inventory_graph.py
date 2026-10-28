from copy import deepcopy
from types import SimpleNamespace
import unittest
from v04_direct_inventory import SourceInventory

class InventoryGraphTests(unittest.TestCase):
    def graph(self, rows):
        return SimpleNamespace(nodes={('source', ident): {'id': ident, 'kind': kind,
            'references': [{'id': target, 'kind': expected} for target, expected in edges]}
            for ident, kind, edges in rows})

    def test_deep_shared_graph_retains_nodes_and_component_scope(self):
        count = 5000
        graph = self.graph([('definition', 'definition', [('0', 'variable'), ('4999', 'variable')])] + [
            (str(i), 'variable', [(str(i + 1), 'variable')] if i + 1 < count else []) for i in range(count)])
        graph.nodes['other', '0'] = {'id': '0', 'kind': 'object', 'references': []}
        original = deepcopy(graph.nodes)
        found, problems = SourceInventory.closure(graph, 'source', 'definition')
        self.assertEqual(problems, [])
        self.assertEqual(len(found), count + 1)
        self.assertEqual([n['id'] for n in found], sorted(ident for scope, ident in original if scope == 'source'))
        self.assertEqual(graph.nodes, original)

    def test_cycles_wrong_kinds_and_missing_edges_keep_original_order(self):
        graph = self.graph([
            ('root', 'definition', [('left', 'variable'), ('right', 'variable'), ('shared', 'state')]),
            ('left', 'variable', [('shared', 'variable'), ('root', 'definition'), ('missing-left', 'variable')]),
            ('right', 'variable', [('shared', 'variable'), ('missing-right', 'state')]),
            ('shared', 'variable', []),
        ])
        found, problems = SourceInventory.closure(graph, 'source', 'root')
        self.assertEqual([n['id'] for n in found], ['left', 'right', 'root', 'shared'])
        self.assertEqual([p['message'] for p in problems], [
            'cyclic dependency: root -> left -> root', 'unresolved/wrong-kind variable: missing-left',
            'unresolved/wrong-kind state: missing-right', 'unresolved/wrong-kind state: shared'])
        self.assertTrue(all(p['category'] == 'source-invalid' and p['component'] == 'source' for p in problems))
