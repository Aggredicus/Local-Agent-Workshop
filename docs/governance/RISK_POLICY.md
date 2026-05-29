# Risk Policy

## Low risk

Examples:

- documentation updates,
- tests,
- repo graph updates,
- formatting,
- non-production scripts.

May continue autonomously if verification passes.

## Medium risk

Examples:

- refactors,
- dependency updates,
- architecture changes,
- CI changes.

Requires review card and evidence.

## High risk

Examples:

- auth,
- secrets,
- payments,
- customer data,
- production deploys,
- destructive commands,
- protected branches.

Agents may prepare safe drafts and tests, but must pause before live effects.

## Core rule

Autonomous agents may prepare sensitive work, but may not activate sensitive consequences without approval.
