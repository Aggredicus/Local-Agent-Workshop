# Example — Svara Lab, 2026-10-26

**No human participants.** These are modeled task profiles operated by Playwright, not recorded human experience.

| Round | n (synthetic sessions) | Browser checks passed | Evidence |
|---|---:|---:|---|
| Pilot before | 3 | 12 / 21 | Backspace cleared all pasted content, two-pointer sustain ended early, navigation lacked ARIA state |
| Pilot after repair | 3 | 21 / 21 | All original pilot checks passed |
| Expansion before | 12 | 161 / 165 | Deleting terminal visarga (`ः`) incorrectly removed the preceding consonant |
| Expansion after repair | 12 | 165 / 165 | All scripted checks passed across three roles and four viewports |
| Preexisting regression | 2 viewports | 48 / 48 | Original v1.2 suite remained green |

The 12-cell expansion used roles `novice`, `sanskrit_editor`, and `music_producer`, crossed with viewport widths 320, 360, 390 and 1440 px. The empirical final 12-session run used approximately 9.1 seconds of Chromium wall time, under the 90-second budget; 12 was the finite **coverage matrix**, not a statistical human-user sample size.

Evidence and example runner are maintained with the Svara Lab review branch in `Aggredicus/Svara-Lab`. Developer review remains required. Cannot infer pronunciation correctness, native smartphone multitouch reliability, satisfaction, or accessibility conformance without separate real-world testing.