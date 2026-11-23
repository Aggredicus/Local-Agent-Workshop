from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "experiments" / "ncm" / "dashboard" / "index.html"


def test_dashboard_is_single_file_offline_and_has_safe_data_labels():
    source = HTML.read_text(encoding="utf-8")
    assert "<script src=" not in source
    assert "<link rel=\"stylesheet\"" not in source
    assert "SYNTHETIC DEMO" in source
    assert "NOT MEASURED" in source
    assert 'type="file"' in source
    assert "Export filtered CSV" in source
    assert "name_integrity_rate" in source
    assert "number_integrity_rate" in source
    assert 'evidence_type==="measured"' in source
    assert "replaceChildren()" in source
    assert "textContent" in source
    assert "eval(" not in source


def test_dashboard_embedded_js_parses_with_node_when_available(tmp_path):
    executable = shutil.which("node")
    if not executable:
        pytest.skip("Node.js not installed; JS syntax test skipped")
    source = HTML.read_text(encoding="utf-8")
    script = source.split("<script>", 1)[1].split("</script>", 1)[0]
    path = tmp_path / "dashboard.js"
    path.write_text(script, encoding="utf-8")
    result = subprocess.run([executable, "--check", str(path)], text=True, capture_output=True, timeout=10, check=False)
    assert result.returncode == 0, result.stderr
