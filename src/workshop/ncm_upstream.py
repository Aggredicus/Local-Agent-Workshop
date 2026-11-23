"""Pinned, opt-in upstream NCM TinyStories smoke-run adapter.

This runs reviewed external code with the invoking user's privileges. It is NOT
a security sandbox: use an offline, locked-down container for untrusted code.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import time
from pathlib import Path

from workshop.ncm_lab import NcmLabError


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for part in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(part)
    return h.hexdigest()


def git_revision(root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            check=True, capture_output=True, text=True, timeout=10,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        raise NcmLabError("cannot verify upstream Git revision") from exc
    return result.stdout.strip()


def prepare_upstream(
    root: Path, expected_commit: str, generator_sha256: str, tokenizer_sha256: str
) -> dict[str, str]:
    """Check exact source revision and both model artifacts before execution."""
    root = root.resolve()
    for name, value, length in (
        ("expected_commit", expected_commit, 40),
        ("generator_sha256", generator_sha256, 64),
        ("tokenizer_sha256", tokenizer_sha256, 64),
    ):
        if not isinstance(value, str) or not re.fullmatch("[0-9a-fA-F]{" + str(length) + "}", value):
            raise NcmLabError(name + " must be a full hexadecimal digest")
    script = root / "generate.py"
    config = root / "configs" / "generation" / "tinystories.yaml"
    generator = root / "artifacts" / "tinystories" / "generator.pt"
    tokenizer = root / "artifacts" / "tinystories" / "tokenizer.pt"
    if not all(p.is_file() for p in (script, config, generator, tokenizer)):
        raise NcmLabError("upstream TinyStories code/config/weights not found; no downloads were attempted")
    actual_revision = git_revision(root)
    if actual_revision.lower() != expected_commit.lower():
        raise NcmLabError("upstream checkout differs from pinned expected_commit")
    if sha256_file(generator).lower() != generator_sha256.lower():
        raise NcmLabError("generator checkpoint checksum mismatch")
    if sha256_file(tokenizer).lower() != tokenizer_sha256.lower():
        raise NcmLabError("tokenizer checkpoint checksum mismatch")
    return {"root": str(root), "commit": actual_revision, "generator_sha256": generator_sha256.lower(),
            "tokenizer_sha256": tokenizer_sha256.lower()}


def run_tinystories(args) -> dict:
    if not args.acknowledge_third_party_code:
        raise NcmLabError("explicit --acknowledge-third-party-code required: upstream Python runs with user permissions")
    if not 1 <= args.samples <= 8 or not 0 <= args.seed <= 2**31 - 1 or not 10 <= args.timeout <= 600:
        raise NcmLabError("bounds: samples 1..8, seed 0..2147483647, timeout 10..600 seconds")
    verified = prepare_upstream(
        args.root, args.expected_commit, args.generator_sha256, args.tokenizer_sha256
    )
    output = args.output.resolve()
    report_path = args.report.resolve()
    if output == report_path or output.exists() or report_path.exists():
        raise NcmLabError("output/report already exists or paths collide; existing evidence is never overwritten")
    if not output.parent.is_dir() or not report_path.parent.is_dir():
        raise NcmLabError("output/report parent directories must exist; refusing implicit external path creation")
    command = [
        str(args.python), "generate.py", "--config", "configs/generation/tinystories.yaml",
        "--checkpoint-dir", "artifacts/tinystories",
        "--samples", str(args.samples), "--seed", str(args.seed),
        "--trajectory", "--out", str(output),
    ]
    # Do not pass user credentials, tokens, proxy settings, GitHub variables, etc.
    allowed = {
        "PATH", "HOME", "USERPROFILE", "SYSTEMROOT", "WINDIR", "TEMP", "TMP",
        "TMPDIR", "LOCALAPPDATA", "APPDATA", "VIRTUAL_ENV", "CUDA_VISIBLE_DEVICES",
        "LD_LIBRARY_PATH", "CUDA_PATH",
    }
    environment = {k: v for k, v in os.environ.items() if k in allowed}
    environment.update({
        "HF_HUB_OFFLINE": "1", "HF_DATASETS_OFFLINE": "1",
        "TRANSFORMERS_OFFLINE": "1", "WANDB_MODE": "offline",
        "GIT_TERMINAL_PROMPT": "0", "NO_PROXY": "*",
    })
    start = time.monotonic()
    try:
        proc = subprocess.run(
            command, cwd=verified["root"], env=environment,
            capture_output=True, text=True, timeout=args.timeout, check=False,
        )
        exit_code = proc.returncode
        stderr = proc.stderr[-10000:]
        stdout = proc.stdout[-10000:]
    except subprocess.TimeoutExpired as exc:
        exit_code = 124
        stderr = "upstream generation timed out"
        stdout = ""
    except OSError as exc:
        exit_code = 127
        stderr = str(exc)
        stdout = ""
    elapsed_ms = round((time.monotonic() - start) * 1000, 2)
    result = {
        "schema_version": "0.1",
        "runner": "NCM upstream TinyStories opt-in",
        "source_commit": verified["commit"],
        "generator_sha256": verified["generator_sha256"],
        "tokenizer_sha256": verified["tokenizer_sha256"],
        "task": "tinystories",
        "samples_requested": args.samples,
        "seed": args.seed,
        "status": "completed" if exit_code == 0 and output.exists() else "failed",
        "exit_code": exit_code,
        "elapsed_ms_including_model_loading": elapsed_ms,
        "benchmark_compatible": False,
        "security_note": "This local subprocess is not a sandbox; environment flags do not guarantee network isolation.",
        "stdout_tail": stdout, "stderr_tail": stderr,
        "output_jsonl": str(output) if output.exists() else None,
    }
    with report_path.open("x", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
        handle.write("\\n")
    return result
