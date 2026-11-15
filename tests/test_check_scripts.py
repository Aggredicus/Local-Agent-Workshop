"""A missing security/release gate must never be mistaken for acceptance."""
import subprocess
import os
from pathlib import Path

import pytest


@pytest.mark.parametrize('script', ['security-scan.sh', 'release-check.sh'])
def test_unavailable_acceptance_gates_return_nonzero(script):
    path = Path(__file__).resolve().parents[1] / 'scripts' / script
    result = subprocess.run(['bash', str(path)], capture_output=True, text=True, check=False)
    assert result.returncode == 2
    assert 'UNAVAILABLE:' in result.stderr


@pytest.mark.parametrize('mode', [[], ['--quiet']])
@pytest.mark.parametrize('failure', ['hyperkanban', 'contracts', 'tests'])
def test_verify_modes_preserve_failed_checks_and_stop(tmp_path, mode, failure):
    shim = tmp_path / 'python'
    shim.write_text('''#!/bin/sh
case "$*" in
  *validate_hyperkanban.py*) phase=hyperkanban ;;
  *validate_repo_contracts.py*) phase=contracts ;;
  '-m pytest'*) phase=tests ;;
  *) exit 97 ;;
esac
printf '%s\\n' "$phase" >> "$LAW_TEST_TRACE"
if [ "$phase" = "$LAW_TEST_FAILURE" ]; then
  printf 'synthetic %s failure\\n' "$phase" >&2
  exit 23
fi
''')
    shim.chmod(0o755)
    trace = tmp_path / 'trace'
    env = os.environ | {'PATH': str(tmp_path) + os.pathsep + os.environ['PATH'],
                        'LAW_TEST_TRACE': str(trace), 'LAW_TEST_FAILURE': failure}
    path = Path(__file__).resolve().parents[1] / 'scripts/verify.sh'
    result = subprocess.run(['bash', str(path), *mode], cwd=tmp_path, env=env, text=True, capture_output=True)
    assert result.returncode == 23
    assert f'synthetic {failure} failure' in result.stderr
    expected = ['hyperkanban', 'contracts', 'tests']
    assert trace.read_text().splitlines() == expected[:expected.index(failure) + 1]
