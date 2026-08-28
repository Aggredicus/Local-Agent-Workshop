# /skill-discovery Improvement Log

## 2026-06-07 — v1.0 deterministic local skill selection gate

Skill used: /skill-discovery
Used for: #181 skill-discovery implementation
Outcome: improve later
Observation: An agent missed the existing `/merge-review` skill because it relied on broad GitHub code search and memory instead of checking `skills/merge-review/SKILL.md` directly.
Decision: Add a deterministic local skill-discovery gate that scans `skills/*/SKILL.md`, checks named skill paths directly, validates registry drift, and ranks candidate skills before recommending workflows or new skill creation.
Links: #181
