"""Offline, dependency-free evidence guards and benchmark validation for NCM Lab.

This module does NOT implement NCM inference. It gates model-produced outlines and
plans, and validates imported measurements without inventing benchmark results.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import unicodedata
from pathlib import Path
from typing import Any


class NcmLabError(ValueError):
    """Invalid contract, trace or benchmark data."""


def normalize(value: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", value).casefold().split())


def digest(source: str) -> str:
    return hashlib.sha256(source.encode("utf-8")).hexdigest()


def _occurs(text: str, value: str) -> bool:
    """Require a full term/number rather than matching substrings (50 != 500)."""
    value = normalize(value)
    if not value:
        return False
    boundary = r"[\w.]" if re.search(r"\d", value) else r"\w"
    return re.search(r"(?<!" + boundary + r")" + re.escape(value) + r"(?!" + boundary + r")", normalize(text)) is not None


def audit_trace(contract: dict[str, Any], trace: dict[str, Any]) -> dict[str, Any]:
    """Fail closed on substituted, missing or ungrounded critical facts at every stage.

    Each declared stage must explicitly assert AND include each protected anchor
    in its human-readable text. Assertions alone cannot satisfy the evidence gate.
    The check is lexical, not a semantic proof; reviewers still inspect meaning.
    """
    if not isinstance(contract, dict) or not isinstance(trace, dict):
        raise NcmLabError("contract and trace must be JSON objects")
    source = contract.get("source", "")
    if not isinstance(source, str) or not source.strip():
        raise NcmLabError("contract.source must contain the canonical task brief")
    anchors = contract.get("anchors")
    stages_required = contract.get("required_stages", ["outline", "plan", "detail"])
    if not isinstance(anchors, list) or not anchors:
        raise NcmLabError("contract.anchors must be a nonempty list")
    if not isinstance(stages_required, list) or not stages_required or len(stages_required) != len(set(stages_required)) or not all(isinstance(x, str) and x for x in stages_required):
        raise NcmLabError("required_stages must contain unique nonempty strings")
    known: dict[str, str] = {}
    for anchor in anchors:
        if not isinstance(anchor, dict) or not isinstance(anchor.get("id"), str) or not anchor["id"] or anchor["id"] in known:
            raise NcmLabError("anchors must have unique nonempty string IDs")
        value = anchor.get("value")
        if not isinstance(value, str) or not value.strip():
            raise NcmLabError("anchor values must be nonempty strings")
        if anchor.get("kind") not in ("name", "number", "identifier", "constraint"):
            raise NcmLabError("anchor kind must be name, number, identifier or constraint")
        if not _occurs(source, value):
            raise NcmLabError(f"anchor {anchor['id']!r} is not present in canonical source")
        known[anchor["id"]] = value
    if trace.get("contract_id") != contract.get("contract_id") or not contract.get("contract_id"):
        raise NcmLabError("trace.contract_id must match contract.contract_id")
    expected_hash = digest(source)
    if trace.get("source_sha256") != expected_hash:
        raise NcmLabError("trace.source_sha256 does not match canonical source")
    stages = trace.get("stages")
    if not isinstance(stages, list):
        raise NcmLabError("trace.stages must be a list")
    issues = []
    seen = set()
    for stage in stages:
        if not isinstance(stage, dict):
            raise NcmLabError("each stage must be an object")
        name, content, claims = stage.get("name"), stage.get("text"), stage.get("anchors")
        if name not in stages_required or name in seen:
            raise NcmLabError("unknown or duplicate stage")
        seen.add(name)
        if not isinstance(content, str) or not isinstance(claims, dict):
            raise NcmLabError("stage requires text and anchors object")
        if stage.get("source_sha256") != expected_hash:
            issues.append({"stage": name, "anchor": "SOURCE", "code": "source_provenance_changed", "severity": "block"})
        for key in claims:
            if key not in known:
                issues.append({"stage": name, "anchor": key, "code": "unknown_claim", "severity": "block"})
        for anchor_id, value in known.items():
            if anchor_id not in claims:
                issues.append({"stage": name, "anchor": anchor_id, "code": "missing_protected_claim", "severity": "block"})
            elif not isinstance(claims[anchor_id], str) or normalize(claims[anchor_id]) != normalize(value):
                issues.append({"stage": name, "anchor": anchor_id, "code": "substituted_value", "severity": "block"})
            if not _occurs(content, value):
                issues.append({"stage": name, "anchor": anchor_id, "code": "canonical_value_absent_from_text", "severity": "block"})
            wrong = claims.get(anchor_id)
            if isinstance(wrong, str) and normalize(wrong) != normalize(value) and _occurs(content, wrong):
                issues.append({"stage": name, "anchor": anchor_id, "code": "substitution_propagated_to_text", "severity": "block"})
    for missing in stages_required:
        if missing not in seen:
            issues.append({"stage": missing, "anchor": "STAGE", "code": "missing_required_stage", "severity": "block"})
    return {
        "schema_version": "0.1",
        "contract_id": contract["contract_id"],
        "source_sha256": expected_hash,
        "passed": not issues,
        "stages_checked": len(seen),
        "anchors_per_stage": len(known),
        "blocked_issues": len(issues),
        "issues": issues,
        "limitations": "Lexical provenance/anchor check only. Does not certify semantic correctness, logic, or absence of invented facts.",
    }


def validate_benchmarks(data: dict[str, Any]) -> dict[str, Any]:
    """Validate provenance and comparability. Missing values are never zero-filled."""
    if not isinstance(data, dict) or data.get("schema_version") != "0.1" or not isinstance(data.get("runs"), list):
        raise NcmLabError("benchmark file requires schema_version='0.1' and runs list")
    if len(data["runs"]) > 10000:
        raise NcmLabError("run limit exceeded (10000)")
    ids = set()
    allowed = ("latency_ms", "tokens_per_second", "peak_ram_mb", "peak_vram_mb", "energy_wh", "success_rate", "name_integrity_rate", "number_integrity_rate")
    counts = {"measured": 0, "synthetic": 0}
    for i, run in enumerate(data["runs"]):
        if not isinstance(run, dict):
            raise NcmLabError(f"run {i} is not an object")
        for field in ("run_id", "model_id", "task_id", "hardware_id", "evaluation_id", "config_id"):
            if not isinstance(run.get(field), str) or not run[field].strip():
                raise NcmLabError(f"run {i} missing {field}")
        if run["run_id"] in ids:
            raise NcmLabError(f"duplicate run_id {run['run_id']}")
        ids.add(run["run_id"])
        typ = run.get("evidence_type")
        if typ not in counts:
            raise NcmLabError(f"run {i} must declare measured or synthetic")
        counts[typ] += 1
        if typ == "measured" and (not isinstance(run.get("evidence_ref"), str) or not run["evidence_ref"].strip()):
            raise NcmLabError(f"measured run {i} missing evidence_ref")
        n = run.get("samples")
        if type(n) is not int or n < 1:
            raise NcmLabError(f"run {i} must have positive integer samples")
        metrics = run.get("metrics")
        if not isinstance(metrics, dict) or not metrics:
            raise NcmLabError(f"run {i} missing metrics")
        for key, value in metrics.items():
            if key not in allowed:
                raise NcmLabError(f"unsupported metric {key}")
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
                raise NcmLabError(f"invalid metric {key} on run {i}")
            if key.endswith("_rate") and value > 1:
                raise NcmLabError(f"rate {key} must be 0..1")
    groups = {}
    for run in data["runs"]:
        key = tuple(run[k] for k in ("task_id", "hardware_id", "evaluation_id", "config_id", "evidence_type"))
        groups.setdefault(key, []).append(run["run_id"])
    return {"valid": True, "total": len(ids), "by_evidence": counts,
            "comparison_groups": [{"task_id": key[0], "hardware_id": key[1], "evaluation_id": key[2], "config_id": key[3], "evidence_type": key[4], "run_ids": value} for key, value in groups.items()]}


def load_json(path: Path) -> dict[str, Any]:
    if path.stat().st_size > 5_000_000:
        raise NcmLabError("input JSON exceeds 5 MB")
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def save_json(path: Path, obj: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
