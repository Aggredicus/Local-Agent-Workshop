# Review Workflow

Every meaningful patch should produce a review card.

A review card answers:

- What changed?
- Why?
- What passed?
- What failed?
- What risks remain?
- What decision is needed?
- What happens next?

Possible actions:

- approve,
- reject,
- modify,
- split,
- continue,
- resume,
- promote to develop,
- create release candidate.

Review cards live under `reviews/pending/` until a human decision moves them to an approved, rejected, or modified queue.
