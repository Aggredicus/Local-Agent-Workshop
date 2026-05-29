#!/usr/bin/env python3
"""Validate the starter HyperKanban orchestration state.

This intentionally uses only the Python standard library. It is not a full
JSON Schema validator; it enforces the project-specific invariants needed for
safe early orchestration.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

DEFAULT_STATE = Path("orchestration/hyperkanban/state.json")
DEFAULT_PACKET = Path("orchestration/hyperkanban/packet.txt")

REQUIRED_STATE_KEYS = {"schema_version", "project", "rank", "axes", "cards"}
REQUIRED_AXIS_KEYS = {"key", "name", "type", "default", "values", "role"}
REQUIRED_CARD_KEYS = {"id", "title", "desc", "deps", "coords", "byte", "tags"}


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"missing file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("state root must be an object")
    return data


def require_keys(obj: dict[str, Any], required: set[str], label: str) -> None:
    missing = sorted(required - set(obj))
    if missing:
        raise ValueError(f"{label} missing required keys: {', '.join(missing)}")


def validate_axes(state: dict[str, Any]) -> dict[str, dict[str, Any]]:
    axes = state.get("axes")
    if not isinstance(axes, list) or not axes:
        raise ValueError("axes must be a non-empty list")

    registry: dict[str, dict[str, Any]] = {}
    for index, axis in enumerate(axes):
        if not isinstance(axis, dict):
            raise ValueError(f"axis {index} must be an object")
        require_keys(axis, REQUIRED_AXIS_KEYS, f"axis {index}")
        key = axis["key"]
        if not isinstance(key, str) or not key:
            raise ValueError(f"axis {index} key must be a non-empty string")
        if key in registry:
            raise ValueError(f"duplicate axis key: {key}")
        if axis["type"] not in {"integer", "enum", "text", "boolean"}:
            raise ValueError(f"axis {key} has unsupported type: {axis['type']}")
        if not isinstance(axis["values"], list):
            raise ValueError(f"axis {key} values must be a list")
        registry[key] = axis
    return registry


def validate_card_shape(cards: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(cards, list):
        raise ValueError("cards must be a list")
    registry: dict[str, dict[str, Any]] = {}
    for index, card in enumerate(cards):
        if not isinstance(card, dict):
            raise ValueError(f"card {index} must be an object")
        require_keys(card, REQUIRED_CARD_KEYS, f"card {index}")
        card_id = card["id"]
        if not isinstance(card_id, str) or not card_id:
            raise ValueError(f"card {index} id must be a non-empty string")
        if card_id in registry:
            raise ValueError(f"duplicate card id: {card_id}")
        if not isinstance(card["deps"], list) or not all(isinstance(dep, str) for dep in card["deps"]):
            raise ValueError(f"card {card_id} deps must be a list of strings")
        if len(card["deps"]) != len(set(card["deps"])):
            raise ValueError(f"card {card_id} has duplicate deps")
        if not isinstance(card["coords"], dict):
            raise ValueError(f"card {card_id} coords must be an object")
        if not isinstance(card["byte"], int) or not 0 <= card["byte"] <= 255:
            raise ValueError(f"card {card_id} byte must be an integer from 0 to 255")
        if not isinstance(card["tags"], list) or not all(isinstance(tag, str) for tag in card["tags"]):
            raise ValueError(f"card {card_id} tags must be a list of strings")
        registry[card_id] = card
    return registry


def validate_dependencies(cards: dict[str, dict[str, Any]]) -> None:
    for card_id, card in cards.items():
        for dep in card["deps"]:
            if dep not in cards:
                raise ValueError(f"card {card_id} depends on missing card {dep}")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(card_id: str, path: list[str]) -> None:
        if card_id in visiting:
            cycle = " -> ".join(path + [card_id])
            raise ValueError(f"dependency cycle detected: {cycle}")
        if card_id in visited:
            return
        visiting.add(card_id)
        for dep in cards[card_id]["deps"]:
            visit(dep, path + [card_id])
        visiting.remove(card_id)
        visited.add(card_id)

    for card_id in cards:
        visit(card_id, [])


def validate_coords(cards: dict[str, dict[str, Any]], axes: dict[str, dict[str, Any]]) -> None:
    axis_keys = set(axes)
    for card_id, card in cards.items():
        coord_keys = set(card["coords"])
        missing = sorted(axis_keys - coord_keys)
        extra = sorted(coord_keys - axis_keys)
        if missing:
            raise ValueError(f"card {card_id} missing coords for axes: {', '.join(missing)}")
        if extra:
            raise ValueError(f"card {card_id} has coords for unknown axes: {', '.join(extra)}")
        for key, axis in axes.items():
            value = card["coords"][key]
            axis_type = axis["type"]
            values = axis.get("values", [])
            if axis_type == "integer" and not isinstance(value, int):
                raise ValueError(f"card {card_id} coord {key} must be an integer")
            if axis_type == "boolean" and not isinstance(value, bool):
                raise ValueError(f"card {card_id} coord {key} must be a boolean")
            if values and value not in values:
                raise ValueError(f"card {card_id} coord {key} has invalid value {value!r}")


def build_packet(state: dict[str, Any]) -> str:
    axes = state["axes"][: state["rank"]]
    axis_keys = [axis["key"] for axis in axes]
    project = state.get("project", {}).get("name", "project").replace(" ", "_")
    lines = [
        f"HK/{state['schema_version']} project={project} rank={state['rank']} axes={','.join(axis_keys)}",
        "FLAGS=0:ready,1:active,2:blocked,3:done,4:review,5:secret,6:risk,7:portal",
    ]
    for card in state["cards"]:
        deps = ".".join(card["deps"]) if card["deps"] else "-"
        path = ";".join(f"{key}={card['coords'][key]}" for key in axis_keys)
        tags = ".".join(card["tags"])
        lines.append(f"{card['id']}|{card['byte']:02X}|d:{deps}|p:{path}|t:{tags}")
    return "\n".join(lines) + "\n"


def validate_packet(state: dict[str, Any], state_path: Path) -> None:
    packet_path = state_path.parent / "packet.txt"
    if not packet_path.exists():
        return
    expected = build_packet(state)
    actual = packet_path.read_text(encoding="utf-8")
    if actual != expected:
        raise ValueError(f"packet out of sync: {packet_path}")


def validate_state(path: Path) -> None:
    state = load_json(path)
    require_keys(state, REQUIRED_STATE_KEYS, "state")
    if not isinstance(state["rank"], int) or state["rank"] < 1:
        raise ValueError("rank must be a positive integer")
    axes = validate_axes(state)
    if state["rank"] > len(axes):
        raise ValueError("rank cannot exceed axis count")
    cards = validate_card_shape(state["cards"])
    validate_dependencies(cards)
    validate_coords(cards, axes)
    validate_packet(state, path)


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    path = Path(args[0]) if args else DEFAULT_STATE
    try:
        validate_state(path)
    except ValueError as exc:
        print(f"HyperKanban validation failed: {exc}", file=sys.stderr)
        return 1
    print(f"HyperKanban validation passed: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
