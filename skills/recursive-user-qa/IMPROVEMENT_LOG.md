# Recursive User QA — Improvement log

## 2026-10-26 — first instrumented Svara Lab application

Skill used: /recursive-user-qa
Used for: Svara Lab v1.3 QA pilot (n=3) and expanded synthetic matrix (x=12)
Outcome: log-only update
Observation: The first fixes passed the pilot, but expansion exposed a visarga Unicode editing edge case; further testing corrected it. Synthetic personas are not human user reports.
Decision: Preserve a pilot→patch→scale→patch→retest recipe with explicit provenance and coverage-budget rules in SKILL.md v0.1.0; no further skill behavior change during closeout.
Links: https://github.com/Aggredicus/Svara-Lab/pull/1 ; https://github.com/Aggredicus/Local-Agent-Workshop/issues/189
## 2026-10-26 — consonant audio and flick regression

Skill used: /recursive-user-qa
Used for: Svara Lab v1.4 exhaustive 34-consonant gesture/audio review; n=12 synthetic browser sessions
Outcome: behavior updated
Observation: Text-entry pass rates concealed lost consonant sound previews and capture-dependent swipe reliability. Exhaustive per-key mapped direction coverage and a browser-native multitouch test were required.
Decision: Added the Input-modality regression gate to SKILL.md, requiring separate audio pathway evidence and human-validation caveats.
Links: https://github.com/Aggredicus/Local-Agent-Workshop/issues/191 ; https://github.com/Aggredicus/Svara-Lab/pull/1
