---
name: ncm-experiment
description: Run evidence-preserving NCM and model-comparison research inside Local Agent Workshop without trusting generated planning facts.
---
# NCM experiment

Use for local, evidence-backed comparisons of model architectures or
coarse-to-fine software planning. Read `me.md`, `skills/README.md`, and
`docs/research/NCM_LAB.md` first. Follow the global skill-use improvement
issue and artifact-update protocol when invoking this skill.

1. Record a canonical task source and explicitly protected names, numbers,
   units, identifiers, constraints and negations.
2. Require matching SHA-256 provenance and literal anchors in **each** outline,
   plan and detail stage. Audit before permitting downstream agent action.
3. Stop on any substitution, source drift, unknown claim, missing stage or
   missing canonical value. Manually review semantic constraints too.
4. Compare only runs with the same task, hardware, evaluation, configuration
   and evidence type. Store raw outputs and execution metadata.
5. Distinguish synthetic demonstration values from measured results in every
   saved report and human-facing comparison.
6. Make experimental backends optional, sandboxed, pinned and offline-ready.
   Never let model evaluation silently modify a protected branch or host state.
7. Run `bash scripts/verify.sh` and NCM-specific tests; report skipped checks,
   limitations, and precise evidence references.
8. Produce a reviewable handoff rather than promoting a new model without
   explicit human approval.

Non-goals: autonomous integration, cloud uploads, production inference,
silent model downloads, and claiming lexical anchor matching proves semantic
correctness.
