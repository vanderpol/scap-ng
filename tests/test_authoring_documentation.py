"""Author-facing schema text must not expose internal decision provenance."""
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1] / 'schema'
# Technical terms such as OVAL, State and legacy are allowed. These markers are
# implementation history and belong in provenance/issues, not hover text.
INTERNAL_MARKERS = (
    re.compile(r'\bDecision\s*\d+\b', re.IGNORECASE),
    re.compile(r'\bPR\s*#?\d+\b', re.IGNORECASE),
    re.compile(r'(?<!\w)#\d+\b'),
    re.compile(r'\bimplementation history\b', re.IGNORECASE),
    re.compile(r'\bactive alignment\b', re.IGNORECASE),
)


def text_nodes(value, path=''):
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f'{path}/{key}'
            if key in {'title', 'description'} and isinstance(child, str):
                yield child_path, child
            elif key == 'examples':
                yield from text_nodes(child, child_path)
            yield from text_nodes(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from text_nodes(child, f'{path}/{index}')


class AuthoringDocumentationTests(unittest.TestCase):
    def test_schema_hover_text_has_no_internal_decision_markers(self):
        failures = []
        for path in sorted(ROOT.glob('*.schema.json')):
            document = json.loads(path.read_text())
            for location, text in text_nodes(document):
                for marker in INTERNAL_MARKERS:
                    if marker.search(text):
                        failures.append(f'{path.name}{location}: {text}')
        self.assertEqual(failures, [])

    def test_variable_expression_values_have_hover_descriptions(self):
        document = json.loads((ROOT / 'variable-expression.schema.json').read_text())
        missing = []
        def visit(node, path=''):
            if isinstance(node, dict):
                properties = node.get('properties', {})
                if isinstance(properties, dict):
                    for key, child in properties.items():
                        if key in {'value', 'literal', 'regex_capture', 'concat', 'values'} and isinstance(child, dict):
                            if not child.get('description'):
                                missing.append(f'{path}/{key}')
                        visit(child, f'{path}/{key}')
                for key, child in node.items():
                    if key != 'properties':
                        visit(child, f'{path}/{key}')
            elif isinstance(node, list):
                for index, child in enumerate(node):
                    visit(child, f'{path}/{index}')
        visit(document)
        self.assertEqual(missing, [])

    def test_variable_expression_descriptions_match_expression_semantics(self):
        document = json.loads((ROOT / 'variable-expression.schema.json').read_text())
        expressions = document['$defs']['expression']['oneOf']
        regex = expressions[4]['properties']['regex_capture']['properties']
        merge = expressions[6]['properties']['merge']['properties']
        values = expressions[2]['properties']['values']['properties']
        self.assertEqual(regex['value']['title'], 'Input expression')
        self.assertIn('string value', regex['value']['description'])
        self.assertEqual(merge['values']['title'], 'Values expression')
        self.assertIn('values to join', merge['values']['description'])
        self.assertEqual(values['field']['title'], 'Collected field')
        self.assertIn('collected field', values['field']['description'])

    def test_documentation_audit_covers_every_schema_root(self):
        roots = sorted(ROOT.glob('*.schema.json'))
        self.assertEqual(len(roots), 35)
        for path in roots:
            document = json.loads(path.read_text())


if __name__ == '__main__':
    unittest.main()
