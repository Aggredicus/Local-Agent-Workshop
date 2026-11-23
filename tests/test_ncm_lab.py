from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from workshop.cli import main
from workshop.ncm_lab import NcmLabError, audit_trace, digest, validate_benchmarks

ROOT = Path(__file__).resolve().parents[1] / "experiments" / "ncm" / "fixtures"


def fixture(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def test_canonical_fixture_passes():
    result = audit_trace(fixture("contract.json"), fixture("trace-good.json"))
    assert result["passed"]
    assert result["blocked_issues"] == 0


def test_substitution_propagates_and_is_blocked_at_every_stage():
    result = audit_trace(fixture("contract.json"), fixture("trace-corrupt.json"))
    assert not result["passed"]
    for stage in ("outline", "plan", "detail"):
        stage_issues = [i for i in result["issues"] if i["stage"] == stage]
        assert any(i["anchor"] == "client" and i["code"] == "substituted_value" for i in stage_issues)
        assert any(i["anchor"] == "budget" and i["code"] == "substituted_value" for i in stage_issues)
        assert any(i["anchor"] == "machine" and i["code"] == "substituted_value" for i in stage_issues)


@pytest.mark.parametrize(("source","incorrect"), [("500", "5000"), ("4", "40"), ("Connor", "Connorson")])
def test_no_substring_false_positive(source, incorrect):
    from workshop.ncm_lab import _occurs
    assert not _occurs(incorrect, source)


def test_correct_assertion_without_grounded_prose_is_rejected():
    trace = fixture("trace-good.json")
    trace["stages"][0]["text"] = "There will be five beds."
    issues = audit_trace(fixture("contract.json"), trace)["issues"]
    assert any(i["code"] == "canonical_value_absent_from_text" and i["stage"] == "outline" for i in issues)


def test_missing_or_swapped_source_hash_fails_closed():
    trace = fixture("trace-good.json")
    trace["source_sha256"] = "00" * 32
    with pytest.raises(NcmLabError, match="source_sha256"):
        audit_trace(fixture("contract.json"), trace)


def test_modified_stage_provenance_blocks():
    trace = fixture("trace-good.json")
    trace["stages"][0]["source_sha256"] = "00" * 32
    assert not audit_trace(fixture("contract.json"), trace)["passed"]


def test_missing_critical_stage_blocks():
    trace = fixture("trace-good.json")
    trace["stages"].pop(0)
    assert any(i["code"] == "missing_required_stage" for i in audit_trace(fixture("contract.json"), trace)["issues"])


def test_anchor_not_in_original_is_rejected():
    contract = fixture("contract.json")
    contract["anchors"][0]["value"] = "Conner"
    with pytest.raises(NcmLabError, match="canonical source"):
        audit_trace(contract, fixture("trace-good.json"))


def test_unknown_anchor_not_accepted():
    trace = fixture("trace-good.json")
    trace["stages"][0]["anchors"]["secret_new_id"] = "x"
    assert any(i["code"] == "unknown_claim" for i in audit_trace(fixture("contract.json"), trace)["issues"])


def test_fixture_digest_matches_source():
    contract = fixture("contract.json")
    assert digest(contract["source"]) == fixture("trace-good.json")["source_sha256"]


def test_benchmark_validation_and_grouping():
    result = validate_benchmarks(fixture("synthetic-benchmarks.json"))
    assert result["total"] >= 4
    assert result["by_evidence"]["measured"] == 0
    assert any(len(group["run_ids"]) >= 2 for group in result["comparison_groups"])


def test_benchmark_falsified_evidence_rejected():
    runs = fixture("synthetic-benchmarks.json")
    run = copy.deepcopy(runs["runs"][0])
    run["evidence_type"] = "measured"
    run.pop("evidence_ref", None)
    with pytest.raises(NcmLabError, match="evidence_ref"):
        validate_benchmarks({"schema_version": "0.1", "runs": [run]})


@pytest.mark.parametrize("bad", [float("nan"), -1, float("inf"), True])
def test_invalid_metrics_rejected(bad):
    data = fixture("synthetic-benchmarks.json")
    data["runs"][0]["metrics"]["latency_ms"] = bad
    with pytest.raises(NcmLabError, match="invalid metric"):
        validate_benchmarks(data)


def test_cli_returns_nonzero_on_corruption(tmp_path):
    output = tmp_path / "audit.json"
    code = main(["ncm", "audit", "--contract", str(ROOT / "contract.json"), "--trace", str(ROOT / "trace-corrupt.json"), "--output", str(output)])
    assert code == 1
    assert output.exists() and not json.loads(output.read_text())["passed"]


def test_cli_validates_benchmark(tmp_path):
    report = tmp_path / "verified.json"
    assert main(["ncm", "validate-runs", "--input", str(ROOT / "synthetic-benchmarks.json"), "--output", str(report)]) == 0
    assert json.loads(report.read_text())["by_evidence"]["measured"] == 0
