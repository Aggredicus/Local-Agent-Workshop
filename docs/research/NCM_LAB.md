# NCM Lab v0.1 — guarded planning and side-by-side benchmarking

Status: **experimental, opt-in, not an NCM inference engine.**

Upstream: [HazyResearch/ncm](https://github.com/HazyResearch/ncm) and
[Stanford's NCM explanation](https://hazyresearch.stanford.edu/blog/2026-10-12-ncm).

## Scope

This branch adds two useful, dependency-free components:

1. **Critical-fact integrity gate**: reject changes to names, numerals,
   identifiers and explicit constraints across `outline → plan → detail`
   stages, with a canonical input digest. The gate exits nonzero on corruption.
2. **Offline HTML benchmark observatory**: select tasks, devices and metrics;
   import JSON measured results; compare models in columns and bars; export
   filtered CSV; never conflate separate hardware/tasks/evaluation settings.

**No code in this slice downloads or executes Stanford NCM, PyTorch or model
weights.** A future opt-in backend must be independently reviewed and its
checkpoint hashes pinned. Current examples are deliberately synthetic.

## Commands

From the LAW checkout after `pip install -e .`:

```bash
workshop ncm audit \
  --contract experiments/ncm/fixtures/contract.json \
  --trace experiments/ncm/fixtures/trace-good.json \
  --output reports/ncm/good.json

# This MUST exit 1 because the outline, plan and detail silently changed
# Connor to Conner, 500 to 600, 49505 to 49550, etc.
workshop ncm audit \
  --contract experiments/ncm/fixtures/contract.json \
  --trace experiments/ncm/fixtures/trace-corrupt.json

workshop ncm validate-runs \
  --input experiments/ncm/fixtures/synthetic-benchmarks.json \
  --output reports/ncm/validation.json
```

Open `experiments/ncm/dashboard/index.html` directly with a local browser.
Use the **Load benchmark JSON** control to select one or more version 0.1
JSON files. The program does not fetch resources or transmit data.

## Planning integrity contract

A task owner creates a canonical `contract` with its exact original
`source`, `contract_id`, `required_stages` and `anchors`. Each anchor
must be present in the original source and have a unique ID, type and
canonical value. For example: client=Connor, budget=500, ZIP=49505,
machine=ThinkCentre2.

Each generated stage must return:

- an unmodified source SHA-256;
- text containing every protected value as a complete term;
- an explicit map of protected facts keyed by immutable IDs.

All required stages must appear; an unknown or duplicate stage is invalid.
A substituted assertion, missing anchor, missing provenance, or missing
canonical value in text is a blocking failure.

**Critical limitation:** lexical matching and an assertion map can detect
many common substitutions, but cannot prove semantic equivalence. They may
miss conflicts elsewhere in an output, altered logical operators (e.g.
"less than" becoming "greater than"), misleading context, arithmetic
mistakes, incorrect units, or contradictory extra statements. Express
important logical operators, units, negations, and prohibitions as separate
explicitly protected constraints, run domain-specific checks, and review
the actual code or plan. A pass is not approval to act. Structured fact
extraction from untrusted prose remains a separate research topic.

Do not store raw client-identifying source material in public example
fixtures. Local audit reports can contain sensitive values. Maintain
least-privilege access, and avoid committing private run records.

## Benchmark record (v0.1)

```json
{
  "schema_version": "0.1",
  "runs": [
    {
      "run_id": "example-001",
      "model_id": "an-experimental-model",
      "task_id": "summary-task-17",
      "hardware_id": "machine-and-precision-profile",
      "evaluation_id": "scoring-protocol-v1",
      "config_id": "prompt-context-batch-sampling-v1",
      "evidence_type": "measured",
      "evidence_ref": "reports/raw/example-001.json",
      "samples": 10,
      "metrics": {
        "latency_ms": 314.0,
        "name_integrity_rate": 1.0,
        "number_integrity_rate": 0.9,
        "success_rate": 0.8
      }
    }
  ]
}
```

The above values are an **illustrative JSON shape, not a measured result**.
The CLI validates IDs, metric ranges, finite values, sample counts and
declared provenance. The dashboard distinguishes evidence type and
keeps conditions separate: same task, hardware, evaluation, configuration,
and synthetic/measured class. It never treats a missing metric as zero.
A declaration of `measured` is not independent verification.

Do **not** claim two experiments are fairly comparable without checking:

- task corpus, splits, source hashes and prompt equality;
- checkpoint and code revision, dtype/quantization and sampling settings;
- exact GPU/CPU and RAM/VRAM configurations;
- warmup and loading exclusion/inclusion, batching and concurrency;
- repetition count, variance/CI, power methodology, failure accounting;
- external review of name/number anchors and semantic task correctness.

The dashboard shows per-run values, not statistical confidence intervals or
normalized quality-adjusted rankings. Low `name_integrity_rate` or
`number_integrity_rate` signals an investigation, never a green pass.

## Acceptance and quality checks

```bash
workshop doctor --summary
workshop skills validate
workshop hk validate
bash scripts/verify.sh
python -m pytest tests/test_ncm_lab.py tests/test_ncm_dashboard.py
```

The regression fixtures deliberately introduce substitutions at the *outline*
stage and propagate them through *plan* and *detail*. Additional tests reject
substring matches (500 vs 5000), mismatched source hashes, missing stages,
ungrounded anchors, invalid/forged evidence declarations, nonfinite metrics,
and duplicate run IDs.

The gate MUST be called before any agent treats a broad plan as a safe
dependency for downstream tool use. This prototype does not yet wire the
gate into the autonomous scheduler; code using the workflow must explicitly
call it and respect exit code 1 or 2.

## Next slices (not yet implemented)

1. Add signed or checksummed raw output manifests and repeatability packs.
2. Run Stanford NCM in a separately pinned, restricted Python environment.
3. Ingest actual NCM and autoregressive evaluation outputs through adapters.
4. Add confidence intervals, paired tests and matched quality thresholds.
5. Add typed constraints for units, comparisons, negation, dates and
   semantic entailment; fail closed before agent fanout.
6. Gate HyperKanban planning transitions using verified audit reports.
