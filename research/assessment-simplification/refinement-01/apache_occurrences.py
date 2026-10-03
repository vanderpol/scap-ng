"""Acquisition-library experiment over precollected native file snapshots.

No filesystem reads, process discovery, commands, globs or effective-config
interpretation. Unimplemented grammar is explicit error, never silent omission.
"""
import posixpath
import shlex


def collect(files, entry, *, installation='one', server_root='/srv/httpd', maximum_files=100):
    rows, diagnostics, active = [], [], []
    visits = 0

    def issue(code, path):
        diagnostics.append({'code': code, 'path': path})

    def walk(path, context=()):
        nonlocal visits
        visits += 1
        if visits > maximum_files:
            issue('resource_limit', path)
            return
        if path in active:
            issue('include_cycle', path)
            return
        if path not in files:
            issue('required_include_missing', path)
            return
        snapshot = files[path]
        if snapshot['status'] != 'complete':
            issue('native_collection_' + snapshot['status'], path)
            return
        active.append(path)
        current = list(context)
        for line_no, line in enumerate(snapshot['text'].splitlines(), 1):
            text = line.strip()
            if not text or text.startswith('#'):
                continue
            if '${' in text or text.endswith('\\'):
                issue('unsupported_expansion_or_continuation', path)
                continue
            if text.startswith('</'):
                if not current or text.lower() != '</' + current[-1][0].lower() + '>':
                    issue('unbalanced_context', path)
                else:
                    current.pop()
                continue
            if text.startswith('<'):
                if not text.endswith('>'):
                    issue('unsupported_context', path)
                    continue
                try:
                    tokens = shlex.split(text[1:-1])
                except ValueError:
                    issue('parse_error', path)
                    continue
                if not tokens or tokens[0].lower() not in ('virtualhost', 'directory'):
                    issue('unsupported_conditional_context', path)
                    break
                current.append((tokens[0], tuple(tokens[1:])))
                continue
            try:
                tokens = shlex.split(text, comments=False, posix=True)
            except ValueError:
                issue('parse_error', path)
                continue
            name, args = tokens[0], tokens[1:]
            if name.lower() == 'serverroot' and args != [server_root]:
                # Applying subsequent relative Includes against the old root
                # would silently select different policy-bearing files.
                issue('unsupported_server_root_change', path)
                break
            if name.lower() in ('include', 'includeoptional'):
                if len(args) != 1 or any(c in args[0] for c in '*?['):
                    issue('unsupported_include_pattern', path)
                    continue
                target = args[0] if args[0].startswith('/') else posixpath.join(server_root, args[0])
                target = posixpath.normpath(target)
                if (name.lower() == 'includeoptional' and target in files
                        and files[target]['status'] == 'does_not_exist'):
                    continue
                walk(target, tuple(current))
            else:
                rows.append({'installation': installation, 'context': [list(x) for x in current],
                             'path': path, 'line': line_no, 'occurrence': len(rows),
                             'directive': name, 'arguments': args})
        if tuple(current) != context:
            issue('unbalanced_context', path)
        active.pop()

    walk(entry)
    return {'status': 'error' if diagnostics else 'complete', 'rows': rows, 'diagnostics': diagnostics}
