#!/usr/bin/env python3
"""Audit every Markdown file without rewriting historical evidence.

Checks repository-local links and heading fragments, flags ambiguous current
entry points, and finds likely duplicate *current* prose for human review.
External websites and links pinned to historical Git commits are not resolved.
"""
from __future__ import annotations

import argparse
import collections
import difflib
import json
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import unquote, urlsplit

LINK_RE = re.compile(r'!?\[[^\]]*\]\((<[^>]+>|[^)]+)\)')
REF_RE = re.compile(r'^\s*\[[^\]]+\]:\s*(\S+)', re.M)
HTML_RE = re.compile(r'(?:href|src)\s*=\s*["\']([^"\']+)["\']', re.I)
HEADER_RE = re.compile(r'^#{1,6}\s+(.+?)\s*#*\s*$', re.M)
FENCE_RE = re.compile(r'^\s*(?:`{3,}|~{3,})')
ABS_SELF_RE = re.compile(r'^https?://(?:www\.)?github\.com/vanderpol/scap-ng/(?:blob|tree)/(main|master)/(.+)$')
HIST_PREFIXES = ('archive/', 'transition/', 'research/', 'board/proposals/',
                 'board/review-content/', 'review/iterations/', 'schema/v0.1.0/',
                 'schema/v0.2.0/', 'tests/assessment-results-0.2.0/',
                 'tests/conditional-0.2.0/', 'tests/reported-elements-0.2.0/',
                 'tests/result-package-0.2.0/', 'tests/collected-items-0.2.0/',
                 'tests/esx-host-0.2.0/', 'tests/item-materialization-0.2.0/')
STOP = set('the and for from with that this into in to of a an on it as by is are be or not can does which now was but how no yes its they their also just has have'.split())


def slug(text: str) -> str:
    text = re.sub(r'!?(?:\[([^]]+)\])\([^)]+\)', r'\1', text)
    text = re.sub(r'<[^>]*>', '', text)
    text = re.sub(r'[\*_~`]', '', text).strip().lower()
    text = unicodedata.normalize('NFKD', text)
    text = re.sub(r'[^\w\-\s]', '', text, flags=re.UNICODE)
    return re.sub(r'\s', '-', text)


def outside_code(body: str) -> str:
    lines, fenced, delimiter = [], False, ''
    for line in body.splitlines():
        m = FENCE_RE.match(line)
        if m:
            marker = m.group().strip()[0]
            if not fenced:
                fenced, delimiter = True, marker
            elif marker == delimiter:
                fenced, delimiter = False, ''
            lines.append('')
        else:
            lines.append('' if fenced else line)
    return '\n'.join(lines)


def classification(path: str) -> str:
    return 'historical' if path.startswith(HIST_PREFIXES) else 'current'


def resolve(root: Path, origin: Path, url: str):
    url = url.strip().lstrip('<').rstrip('>')
    url = re.split(r'\s+["\']', url, 1)[0]
    if url.startswith(('mailto:', 'data:', '#')):
        if url.startswith('#'):
            return origin, url[1:]
        return None
    match = ABS_SELF_RE.match(url)
    if match:
        url = '/' + match.group(2)
    elif url.startswith(('http:', 'https:', 'ftp:', '//', 'tel:', 'javascript:')):
        return None
    parts = urlsplit(url)
    if not parts.path and not parts.fragment:
        return None
    decoded = unquote(parts.path)
    if decoded.startswith('/'):
        path = root / decoded.lstrip('/')
    else:
        path = origin.parent / decoded
    path = path.resolve()
    try:
        path.relative_to(root)
    except ValueError:
        return 'outside', path.as_posix()
    if not decoded:
        path = origin
    if path.is_dir():
        index = path / 'README.md'
        if index.is_file():
            path = index
    return path, unquote(parts.fragment)


def headings(body: str) -> set[str]:
    counter, result = collections.Counter(), set()
    for text in HEADER_RE.findall(outside_code(body)):
        base = slug(text)
        num = counter[base]
        result.add(base if num == 0 else f'{base}-{num}')
        counter[base] += 1
    return result


def words(body: str) -> set[str]:
    plain = re.sub(r'[^a-z0-9]+', ' ', outside_code(body).lower())
    return {x for x in plain.split() if len(x) > 3 and x not in STOP}


def audit(root: Path):
    docs = sorted(root.rglob('*.md'))
    texts = {p: p.read_text(encoding='utf-8', errors='replace') for p in docs}
    fragments = {p: headings(s) for p, s in texts.items()}
    broken, checked, external = [], 0, 0
    for path, body in texts.items():
        relative = path.relative_to(root).as_posix()
        plain = outside_code(body)
        refs = [m.group(1) for m in LINK_RE.finditer(plain)]
        refs += [m.group(1) for m in REF_RE.finditer(plain)]
        refs += [m.group(1) for m in HTML_RE.finditer(plain)]
        for url in refs:
            item = resolve(root, path, url)
            if item is None:
                external += 1
                continue
            target, anchor = item
            checked += 1
            reason = None
            if target == 'outside':
                reason = 'escapes_repository'
            elif not (target.is_file() or target.is_dir()):
                reason = 'missing_target'
            elif anchor and target.suffix.lower() == '.md':
                if slug(anchor) not in fragments.get(target, set()):
                    reason = 'missing_heading'
            if reason:
                broken.append({'source': relative, 'url': url,
                               'target': str(target) if target == 'outside'
                               else target.relative_to(root).as_posix(),
                               'reason': reason, 'scope': classification(relative)})
    active = [p for p in docs if classification(p.relative_to(root).as_posix()) == 'current']
    candidates = []
    # Jaccard similarity is an advisory cross-reference, not a deletion rule.
    tokens = {p: words(texts[p]) for p in active}
    for i, p in enumerate(active):
        a = tokens[p]
        if len(a) < 35:
            continue
        for q in active[i+1:]:
            b = tokens[q]
            if len(b) < 35:
                continue
            overlap = len(a & b)
            score = round(overlap / len(a | b), 3)
            if score >= .72 or (score >= .58 and min(len(a), len(b)) >= 100):
                candidates.append({'a': p.relative_to(root).as_posix(),
                                   'b': q.relative_to(root).as_posix(),
                                   'jaccard': score, 'overlap_words': overlap})
    candidates.sort(key=lambda a: a['jaccard'], reverse=True)
    by_scope = collections.Counter(classification(p.relative_to(root).as_posix()) for p in docs)
    return {'total_markdown': len(docs), 'by_scope': dict(by_scope),
            'local_links_checked': checked, 'external_or_nonfile_refs': external,
            'broken': broken, 'broken_current': sum(x['scope']=='current' for x in broken),
            'broken_historical': sum(x['scope']=='historical' for x in broken),
            'similarity_candidates': candidates[:80]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('root', nargs='?', default='.')
    ap.add_argument('--output', default='documentation-audit.json')
    ap.add_argument('--summary', default='documentation-audit.md')
    ap.add_argument('--strict-current', action='store_true')
    args = ap.parse_args()
    root = Path(args.root).resolve()
    result = audit(root)
    Path(args.output).write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    lines = ['# Markdown cross-reference audit', '',
             f"Scanned **{result['total_markdown']}** Markdown files "
             f"({result['by_scope'].get('current', 0)} current, "
             f"{result['by_scope'].get('historical', 0)} historical).",
             f"Checked **{result['local_links_checked']}** local references. "
             f"Broken current: **{result['broken_current']}**; "
             f"broken historical: **{result['broken_historical']}**.", '',
             '## Current broken links', '']
    for x in result['broken']:
        if x['scope'] == 'current':
            lines.append(f"- \`{x['source']}\` → \`{x['url']}\` ({x['reason']})")
    lines += ['', '## Likely overlapping current prose (review, do not auto-delete)', '']
    for x in result['similarity_candidates'][:35]:
        lines.append(f"- {x['jaccard']:.3f}: \`{x['a']}\` / \`{x['b']}\`")
    Path(args.summary).write_text('\n'.join(lines)+'\n', encoding='utf-8')
    print('\n'.join(lines[:20]))
    if args.strict_current and result['broken_current']:
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
