"""Shared, standard-library semantic validation for all HyperKanban entrypoints."""
from __future__ import annotations

from typing import Any

REQUIRED_STATE_KEYS = {"schema_version", "project", "rank", "axes", "cards"}
REQUIRED_AXIS_KEYS = {"key", "name", "type", "default", "values", "role"}
REQUIRED_CARD_KEYS = {"id", "title", "desc", "deps", "coords", "byte", "tags"}


class HyperKanbanError(ValueError):
    """Invalid or conflicting HyperKanban state."""


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
        if type(card["byte"]) is not int or not 0 <= card["byte"] <= 255:
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

    visited: set[str] = set()
    # Iterative depth-first traversal handles long valid chains without recursion
    # limits or copying the whole ancestry path for every edge.
    for root in cards:
        if root in visited:
            continue
        path = [root]
        active = {root: 0}
        stack = [iter(cards[root]['deps'])]
        while stack:
            dep = next(stack[-1], None)
            if dep is None:
                finished = path.pop()
                visited.add(finished)
                del active[finished]
                stack.pop()
            elif dep in active:
                cycle = path[active[dep]:] + [dep]
                preview = cycle if len(cycle) <= 8 else cycle[:4] + ['...'] + cycle[-4:]
                shown = ' -> '.join(node[:40] for node in preview)
                raise ValueError(f'dependency cycle detected: {shown}')
            elif dep not in visited:
                active[dep] = len(path)
                path.append(dep)
                stack.append(iter(cards[dep]['deps']))


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
            if axis_type == "integer" and type(value) is not int:
                raise ValueError(f"card {card_id} coord {key} must be an integer")
            if axis_type == "boolean" and not isinstance(value, bool):
                raise ValueError(f"card {card_id} coord {key} must be a boolean")
            if values and value not in values:
                raise ValueError(f"card {card_id} coord {key} has invalid value {value!r}")



def validate_data(state: Any) -> None:
    try:
        if not isinstance(state, dict):
            raise ValueError("state root must be an object")
        require_keys(state, REQUIRED_STATE_KEYS, "state")
        if state["schema_version"] != "0.1.0":
            raise ValueError("unsupported HyperKanban schema_version")
        project = state["project"]
        if not isinstance(project, dict) or not isinstance(project.get("name"), str) or not project["name"].strip() or not isinstance(project.get("purpose"), str):
            raise ValueError("project needs a name and purpose")
        axes = validate_axes(state)
        if type(state["rank"]) is not int or not 1 <= state["rank"] <= len(axes):
            raise ValueError("rank must be a positive integer no larger than axis count")
        for key, axis in axes.items():
            expected = {"integer": int, "enum": str, "text": str, "boolean": bool}[axis["type"]]
            if type(axis["default"]) is not expected or any(type(v) is not expected for v in axis["values"]):
                raise ValueError(f"axis {key} has invalid default or allowed values")
            if axis["values"] and axis["default"] not in axis["values"]:
                raise ValueError(f"axis {key} default must be an allowed value")
        cards = validate_card_shape(state["cards"])
        validate_dependencies(cards)
        validate_coords(cards, axes)
        for card in cards.values():
            for key, axis in axes.items():
                if axis["type"] in {"text", "enum"} and not isinstance(card["coords"][key], str):
                    raise ValueError(f"card {card['id']} coord {key} must be text")
            for field in ("evidence_paths", "open_exceptions", "validation_commands", "generated_reports", "changed_docs"):
                if field in card and (not isinstance(card[field], list) or any(not isinstance(item, str) or not item.strip() for item in card[field])):
                    raise ValueError(f"card {card['id']} {field} must be a list of nonempty strings")
            for field in ("test_contract", "doc_contract"):
                if field in card and (not isinstance(card[field], dict) or ("required" in card[field] and type(card[field]["required"]) is not bool)):
                    raise ValueError(f"card {card['id']} {field} must be a contract object with boolean required")
            done = bool(card["byte"] & 8)
            if "state" in axes and done != (card["coords"]["state"] == "done"):
                raise ValueError(f"card {card['id']} done flag and coordinate disagree")
            required = card.get("test_contract", {}).get("required") or card.get("doc_contract", {}).get("required")
            if done and required and not (card.get("evidence_paths") or card.get("open_exceptions")):
                raise ValueError(f"card {card['id']} is done but lacks required evidence or exception")
    except (KeyError, TypeError, ValueError) as exc:
        raise HyperKanbanError(str(exc)) from exc
