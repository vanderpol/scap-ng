#!/usr/bin/env python3
"""Bounded local OS observations, not a SCAP-NG collector or evaluator."""
import argparse
import errno
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile


def observe():
    shell = shutil.which('sh')
    if os.name != 'posix' or not shell:
        raise RuntimeError('POSIX shell witness environment unavailable; no Windows claim')
    cases = [
        ('stdout', "printf '%s\\n' example", 0, b'example\n', b''),
        ('no-bytes', ':', 0, b'', b''),
        ('empty-line', "printf '\\n'", 0, b'\n', b''),
        ('duplicates', "printf '%s\\n' example example", 0, b'example\nexample\n', b''),
        ('conflicting', "printf '%s\\n' example other", 0, b'example\nother\n', b''),
        ('nonzero', "printf '%s\\n' example; exit 7", 7, b'example\n', b''),
        ('stderr', "printf '%s\\n' warning >&2", 0, b'', b'warning\n'),
        ('malformed-utf8', "printf '\\377'", 0, b'\xff', b''),
    ]
    observations = []
    for name, command, code, stdout, stderr in cases:
        result = subprocess.run([shell, '-c', command], stdin=subprocess.DEVNULL,
                                capture_output=True, timeout=5, check=False)
        if (result.returncode, result.stdout, result.stderr) != (code, stdout, stderr):
            raise AssertionError('Independent OS byte/exit witness failed: ' + name)
        observations.append(dict(id=name, exit_status=result.returncode,
                                 stdout_hex=result.stdout.hex(), stderr_hex=result.stderr.hex(),
                                 os_expectation_matched=True))
    with tempfile.TemporaryDirectory(prefix='scapng-os-witness-') as temporary:
        root = Path(temporary)
        for name, path, expected_errno in [('interpreter-missing', root / 'missing', errno.ENOENT),
                                           ('launch-denied', root / 'not-executable', errno.EACCES)]:
            if expected_errno == errno.EACCES:
                path.write_text('#!/bin/sh\nexit 0\n')
                path.chmod(0o600)
            try:
                subprocess.run([str(path)], capture_output=True, timeout=5, check=False)
            except OSError as error:
                if error.errno != expected_errno:
                    raise
                observations.append(dict(id=name, launched=False, errno=error.errno,
                                         exit_status=None, os_expectation_matched=True))
            else:
                raise AssertionError('Expected launch failure: ' + name)
        target = root / 'target'
        target.write_bytes(b'x')
        target.chmod(0o640)
        link = root / 'link'
        link.symlink_to(target.name)
        dangling = root / 'dangling'
        dangling.symlink_to('missing-target')
        os.utime(target, ns=(1700000000123456789, 1700000000123456789))
        observations.append(dict(id='file-link-identity',
                                 link_is_symlink=stat.S_ISLNK(link.lstat().st_mode),
                                 target_is_regular=stat.S_ISREG(target.stat().st_mode),
                                 dangling_link_exists=stat.S_ISLNK(dangling.lstat().st_mode),
                                 dangling_target_exists=dangling.exists(),
                                 target_mode=oct(stat.S_IMODE(target.stat().st_mode)),
                                 target_mtime_ns=target.stat().st_mtime_ns))
        target.chmod(0)
        try:
            target.read_bytes()
            read_status = 'read_succeeded_no_denial_proof'
        except PermissionError:
            read_status = 'permission_denied'
        finally:
            target.chmod(0o600)
        observations.append(dict(id='file-mode-versus-access', effective_uid=os.geteuid(),
                                 zero_mode_read_observation=read_status,
                                 qualification='OS observation only; privileged access may bypass mode denial.'))
    return dict(format='scap-ng/developer-os-witnesses/1',
                qualification='Local POSIX process/filesystem observations; no native scanner or OVAL equivalence.',
                interpreter=shell, observations=observations,
                not_executed=['Windows Registry', 'Windows file/service', 'mount boundaries',
                              'ACL unsupported mapping', 'native timeout/output policy', 'SCAP-NG evaluation'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.write_text(json.dumps(observe(), indent=2) + '\n', encoding='utf-8', newline='\n')
    print('12 bounded OS observations recorded; no native scanner evaluation')


if __name__ == '__main__':
    main()
