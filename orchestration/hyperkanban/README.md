# HyperKanban Orchestration State

HyperKanban is the current operational project-state projection for Local Agent Workshop.

It is not the historical source of truth. Chronicle events are the long-term append-only memory layer. HyperKanban state is the compact working map that agents can validate, inspect, and use for task selection.

## Files

```text
orchestration/hyperkanban/state.json
orchestration/hyperkanban/packet.txt
```

## State contract

```text
axes[]  = registered dimensions
cards[] = inode-like project/task records
deps[]  = graph edges between cards
coords  = per-axis coordinate values
byte    = 8-bit compact state summary
tags[]  = optional routing and behavior hints
```

## Byte flags

```text
bit 0 = ready
bit 1 = active
bit 2 = blocked
bit 3 = done
bit 4 = review
bit 5 = secret
bit 6 = risk
bit 7 = portal
```

## Packet contract

`packet.txt` is a low-token handoff format for agents. It must remain deterministic and synchronized with `state.json`.

## Validation

Run:

```sh
python scripts/validate_hyperkanban.py orchestration/hyperkanban/state.json
```

The validator checks uniqueness, dependency integrity, dependency cycles, axis/coordinate integrity, byte ranges, and packet synchronization.
