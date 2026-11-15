# Codebase foundation review — human decision packet

**Decision requested:** select the baseline remediation/rebuild scope before resuming deployment.

[Full review](../../reports/codebase-review/REVIEW.md) · [Validation](../../reports/codebase-review/VALIDATION.md) · [Follow-ups](../../reports/codebase-review/FOLLOW-UPS.md)

Baseline: 22fc0e72f55fa68f98f5f9ffa92127e96c7b9913. Branch: agent/debian-deployment. Review-only artifacts are untracked; no PR/commit/push.

Recommendation: fresh branch from the exact reviewed commit, selective component acceptance, quality gates and regression fixes first, governance refresh separately, maintained-tool-backed deployment slices afterward.

Passed: 47 existing tests in the current checkout and a no-.git source export under a directory containing spaces; CLI doctor; nine schema definitions and two current artifacts; dependency compatibility; no known advisories for the five resolved development packages.

Findings: eight reproducible baseline defect groups, including diagnostic credential leakage and symlink escapes; documented registry-validation limitations; misleading no-op checks; policy/process drift; environment pip advisories. Thirteen probes confirm these observations, not successful product acceptance.

Risks: current helpers do not establish a security/deployment boundary. Experimental new provisioning code has separate unaddressed defects. No physical server, Windows, firewall, reboot, or offline provisioning qualification. GitHub API unavailable; current hosted policy enforcement unknown.

Changed files: report/reproduction/evidence artifacts, this review card, a new append-only Chronicle event, and run checkpoint. Existing tracked source and policy are unchanged. Earlier untracked setup/provisioning experiment is preserved and paused, excluded from baseline acceptance.

HyperKanban: no existing cards were completed or rewritten. Proposed transitions/QA work remain subject to human review; do not mark the deployment mission done.

Resume: read the full review and its follow-ups, agree component acceptance/remediation scope, create a clean remediation branch from the reviewed commit without bringing over the unfinished deployment experiment. Do not deploy to ThinkCentre2 or publish.
