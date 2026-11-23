from __future__ import annotations

import argparse
import hashlib
import subprocess

import pytest

from workshop.ncm_lab import NcmLabError
from workshop.ncm_upstream import prepare_upstream, run_tinystories


def fake_checkout(tmp_path):
    root = tmp_path / "ncm"
    for item in ["generate.py", "configs/generation/tinystories.yaml",
                 "artifacts/tinystories/generator.pt", "artifacts/tinystories/tokenizer.pt"]:
        dest = root / item
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(item.encode("utf-8"))
    generator = root / "artifacts/tinystories/generator.pt"
    tokenizer = root / "artifacts/tinystories/tokenizer.pt"
    return root, hashlib.sha256(generator.read_bytes()).hexdigest(), hashlib.sha256(tokenizer.read_bytes()).hexdigest()


def parameters(tmp_path, root, generator, tokenizer):
    return argparse.Namespace(
        root=root, expected_commit="a" * 40,
        generator_sha256=generator, tokenizer_sha256=tokenizer,
        python=tmp_path / "venv/bin/python", samples=1, seed=42,
        timeout=30, output=tmp_path / "samples.jsonl",
        report=tmp_path / "report.json", acknowledge_third_party_code=True,
    )


def test_revision_and_checkpoint_hashes_are_mandatory(tmp_path, monkeypatch):
    root, generator, tokenizer = fake_checkout(tmp_path)
    monkeypatch.setattr("workshop.ncm_upstream.git_revision", lambda _: "a" * 40)
    result = prepare_upstream(root, "a" * 40, generator, tokenizer)
    assert result["commit"] == "a" * 40
    with pytest.raises(NcmLabError, match="generator checkpoint"):
        prepare_upstream(root, "a" * 40, "0" * 64, tokenizer)
    with pytest.raises(NcmLabError, match="tokenizer checkpoint"):
        prepare_upstream(root, "a" * 40, generator, "0" * 64)
    with pytest.raises(NcmLabError, match="pinned"):
        prepare_upstream(root, "b" * 40, generator, tokenizer)


def test_missing_checkout_fails_without_downloading(tmp_path):
    with pytest.raises(NcmLabError, match="not found"):
        prepare_upstream(tmp_path, "a" * 40, "a" * 64, "b" * 64)


def test_requires_explicit_approval_before_external_execution(tmp_path):
    root, generator, tokenizer = fake_checkout(tmp_path)
    args = parameters(tmp_path, root, generator, tokenizer)
    args.acknowledge_third_party_code = False
    with pytest.raises(NcmLabError, match="acknowledge"):
        run_tinystories(args)


def test_bounded_samples_and_timeout(tmp_path):
    root, generator, tokenizer = fake_checkout(tmp_path)
    args = parameters(tmp_path, root, generator, tokenizer)
    args.samples = 99
    with pytest.raises(NcmLabError, match="bounds"):
        run_tinystories(args)


def test_cannot_overwrite_existing_evidence(tmp_path, monkeypatch):
    root, generator, tokenizer = fake_checkout(tmp_path)
    monkeypatch.setattr("workshop.ncm_upstream.git_revision", lambda _: "a" * 40)
    args = parameters(tmp_path, root, generator, tokenizer)
    args.output.write_text("historical run")
    with pytest.raises(NcmLabError, match="already exists"):
        run_tinystories(args)
    assert args.output.read_text() == "historical run"


def test_opt_in_exec_records_loading_inclusive_runtime_without_claiming_benchmark(tmp_path, monkeypatch):
    root, generator, tokenizer = fake_checkout(tmp_path)
    monkeypatch.setattr("workshop.ncm_upstream.git_revision", lambda _: "a" * 40)
    monkeypatch.setenv("GITHUB_TOKEN", "never-forward-this")
    args = parameters(tmp_path, root, generator, tokenizer)

    def process(command, **kwargs):
        assert command[0] == str(args.python)
        assert command[1] == "generate.py"
        assert "--trajectory" in command
        assert kwargs["env"]["HF_HUB_OFFLINE"] == "1"
        assert "GITHUB_TOKEN" not in kwargs["env"]
        args.output.write_text('{"generated":"synthetic test only"}\n')
        return subprocess.CompletedProcess(command, 0, stdout="generated", stderr="")

    monkeypatch.setattr("workshop.ncm_upstream.subprocess.run", process)
    result = run_tinystories(args)
    assert result["status"] == "completed"
    assert result["benchmark_compatible"] is False
    assert result["source_commit"] == "a" * 40
    assert args.report.exists()
