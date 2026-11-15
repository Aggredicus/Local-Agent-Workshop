"""A missing security/release gate must never be mistaken for acceptance."""
import subprocess
from pathlib import Path

import pytest


@pytest.mark.parametrize('script', ['security-scan.sh', 'release-check.sh'])
def test_unavailable_acceptance_gates_return_nonzero(script):
    path = Path(__file__).resolve().parents[1] / 'scripts' / script
    result = subprocess.run(['bash', str(path)], capture_output=True, text=True, check=False)
    assert result.returncode == 2
    assert 'UNAVAILABLE:' in result.stderr
