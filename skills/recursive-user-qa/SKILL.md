---
name: recursive-user-qa
description: Run bounded evidence-based, multi-persona QA/QC cycles for interactive software, beginning with n=3 and scaling to a coverage- and compute-budgeted cohort. Separates simulated users from actual humans; writes reproducible failures, verified patches, and reviewable outcomes.
---

# /recursive-user-qa

A **test-and-improve loop**, not a claim that artificial personas are human research participants or that any model has trained itself. A tester side proposes tasks, assumptions and adversarial edge cases. A defender side changes small, reversible implementation slices. An **independent deterministic verifier** reruns the same tasks and a regression suite. Repeat until the stopping rule triggers. Do not label synthetic comments as actual user reports.

## Place in Local Agent Workshop

Read `me.md`, `skills/README.md`, `docs/protocols/QUALITY_ANALYSIS_PROTOCOL.md`, and `docs/protocols/GRIND_PROTOCOL.md`. This skill augments `/quality-analysis`, `/grind` and `/self-improvement`; it does not replace the established approvals. Operate on an `agent/*` branch, checkpoint each iteration, issue a reviewable PR, and never merge protected branches automatically.

**After every use**, obey `skills/README.md`: open one scoped skill-improvement issue and either update this `SKILL.md` for a learned behavior change or append to `IMPROVEMENT_LOG.md` for a no-change audit. Do not recurse infinitely creating issues.

## Inputs

- Repo, branch / working tree, application entrypoint, tested build or commit SHA.
- Tasks and independent **observable** assertions (not only subjective goals).
- Persona hypotheses (roles, skills, devices, assistive technology modes); initial `n=3`.
- Simulator / real-user labels, available browsers, permissions and test tools.
- Resource ceiling: wall-clock seconds, browser instances, token budget, number of iterations, optional monetary limit.
- For actual human recordings: **prior opt-in consent**, content redaction, retention policy, deletion pathway; never enable silent telemetry.

## Procedure

1. **Baseline and provenance.** Freeze a baseline commit/source snapshot. Record exact test environment, browser versions when available, seed and timestamp. Mark every piece of evidence `observed_automation`, `simulated_feedback`, `human_report`, or `hypothesis`. Do not conflate their sample sizes.
2. **Pilot `n=3`.** Select three **different task/skill archetypes** relevant to the application, not copies of one chat response. Run explicit task scripts end-to-end and record expected vs observed results, JavaScript errors, UX geometry, exports, interactions, duration and blocking failures. Collect consented human feedback only if humans actually participated.
3. **Red-team critique.** For each failed assertion or independently observed ergonomic risk, create a finding with severity, confidence, reproduction, evidence path and minimal candidate repair. Prefer targeted changes over broad rewrites.
4. **Defender patch.** Implement one small reversible patch per issue cluster on an isolated branch. Never silently fix protected-branch, data, authentication or production concerns.
5. **Verifier.** Retest the *unchanged original assertions*, add a regression test capturing each fix, and run the pre-existing suite. Preserve failing and successful outputs with run IDs. Do not delete the failing evidence.
6. **Allocate expansion `x`.** Use new coverage cells, not artificial repetitions: e.g., `3 task archetypes × 4 viewport/input contexts = 12`. Compute `x=min(unique_cells, session_cap, floor(remaining_time / max(observed_seconds_per_session, 0.1)))`. Default total time ceiling 90 s and session cap 12; reduce x when tools or memory are constrained. A failed pilot should be repaired before expanding. Record why x was selected and do not claim statistical confidence for synthetic personas.
7. **Adversarial expansion.** Exercise edge inputs, Unicode and grapheme behavior, concurrent fingers/keys, screen geometry, accessibility semantics, undo, exports, malformed data and state continuity. Sample distinct cells deterministically; log actual outcomes and simulated qualitative reactions separately.
8. **Recur boundedly.** If a new failure emerges, patch, rerun the expanded test matrix and original regressions. Limit to `max_iterations=3` by default; stop at a hard blocker, budget exhaustion, an unresolved unsafe change, coverage plateau, or all acceptance checks passing. Never assert perfect product quality from test success.
9. **Review/handoff.** Produce a compact report: baseline vs final pass totals; unique scenarios; failures + reproductions; patches; runtimes; links to raw logs, screen captures, WAV/ZIP integrity evidence; untested and human-only risks; approval decision; rollback steps. Request human review for protected-branch merge or real-world telemetry.

## Output artifact contract

```text
runs/<run-id>/manifest.json            # tested SHA, mode, consent, seed, environment, budget
runs/<run-id>/pilot_before.json         # 3 simulated task profiles or 3 consented humans
runs/<run-id>/pilot_after.json
runs/<run-id>/expanded_before.json      # if issues identified during scale-up
runs/<run-id>/expanded_after.json
runs/<run-id>/findings.json             # severity/reproduction/evidence/provenance
runs/<run-id>/report.md                 # explicit limits and release gate
```

The corresponding example schema is in `templates/session.json`. Prefer machine-readable logs over unverifiable narrative. The optional `scripts/plan_and_score.py` validates provenance and proposes a bounded next cohort. Domain-specific Playwright/cypress/pytest scripts remain in the *target application repo*, not hardcoded into this cross-project skill.

## Quality rubric and stopping rules

Pass/fail comes from **observable assertions**; synthetic persona sentiment never increases measured pass rate. Score issues by impact (1–5), reproducibility (1–5), reach (1–5), and cost (1–5); address high impact/reproducibility/reach first, balancing repair cost. Any unresolved high-severity corruption, privacy violation, security issue or audio/export crash is a blocker regardless of average score.

A **PASS** means the named automated checks passed on the stated test environments. It does **not** mean all users will succeed, true user satisfaction improved, audio sounds authentic or production is certified. Mark missing hardware, browsers, Sanskrit/native-speaker evaluation, and human assistive-technology audits **UNVERIFIED**, not PASS.

## Human experimentation boundary

For real users: seek informed consent before recording voice, screens, keystrokes or transcripts; minimize stored personal data; enable export/revoke/delete; avoid storing Sanskrit input content by default; separate identifying info from session events. Human studies get separate `human_report` evidence records and must not be pooled with synthetic cohorts. Do not invent interviews, recordings, satisfaction percentages or retention metrics.

## Example: Svara Lab 2026-10-26

See `references/svara-lab-example.md` for the n=3 → x=12 iterative case. Reuse the *method*, not its task-specific assumptions or outcomes.