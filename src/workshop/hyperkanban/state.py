"""Read-only HyperKanban state operations.

The first CLI slice intentionally stays read-only: load, validate, list, show,
select the next unblocked card, and emit the deterministic compact packet.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DEFAULT_STATE_PATH = Path("orchestration/hyperkanban/state.json")
READY = 1 << 0
ACTIVE = 1 << 1
BLOCKED = 1 << 2
DONE = 1 << 3
REVIEW = 1 << 4
SECRET = 1 << 5
RISK = 1 << 6
PORTAL = 1 << 7

FLAG_NAMES = [
    "ready",
    "active",
    "blocked",
    "done",
    "review",
    "secret",
    "risk",
    "portal",
]


class HyperKanbanError(ValueError):
    """Raised when HyperKanban state is invalid or a card is missing."""


def load_state(path: Path = DEFAULT_STATE_PATH) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise HyperKanbanError(f"missing state file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise HyperKanbanError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise HyperKanbanError("state root must be an object")
    validate_state(data)
    return data


def validate_state(state: dict[str, Any]) -> None:
    required = {"schema_version", "project", "rank", "axes", "cards"}
    missing = sorted(required - set(state))
    if missing:
        raise HyperKanbanError(f"state missing keys: {', '.join(missing)}")
    axes = state.get("axes")
    cards = state.get("cards")
    if not isinstance(axes, list) or not axes:
        raise HyperKanbanError("axes must be a non-empty list")
    if not isinstance(cards, list):
        raise HyperKanbanError("cards must be a list")
    axis_keys = [axis.get("key") for axis in axes if isinstance(axis, dict)]
    if len(axis_keys) != len(axes) or any(not isinstance(key, str) or not key for key in axis_keys):
        raise HyperKanbanError("every axis needs a non-empty string key")
    if len(axis_keys) != len(set(axis_keys)):
        raise HyperKanbanError("axis keys must be unique")
    rank = state.get("rank")
    if not isinstance(rank, int) or rank < 1 or rank > len(axis_keys):
        raise HyperKanbanError("rank must be a positive integer no larger than axis count")
    card_ids: set[str] = set()
    for card in cards:
        if not isinstance(card, dict):
            raise HyperKanbanError("each card must be an object")
        card_id = card.get("id")
        if not isinstance(card_id, str) or not card_id:
            raise HyperKanbanError("each card needs a non-empty string id")
        if card_id in card_ids:
            raise HyperKanbanError(f"duplicate card id: {card_id}")
        card_ids.add(card_id)
        if not isinstance(card.get("byte"), int) or not 0 <= card["byte"] <= 255:
            raise HyperKanbanError(f"card {card_id} byte must be an integer from 0 to 255")
        if not isinstance(card.get("deps"), list):
            raise HyperKanbanError(f"card {card_id} deps must be a list")
        coords = card.get("coords")
        if not isinstance(coords, dict):
            raise HyperKanbanError(f"card {card_id} coords must be an object")
        if set(coords) != set(axis_keys):
            raise HyperKanbanError(f"card {card_id} coords must match registered axes")
    for card in cards:
        card_id = card["id"]
        for dep in card["deps"]:
            if dep not in card_ids:
                raise HyperKanbanError(f"card {card_id} depends on missing card {dep}")


def build_packet(state: dict[str, Any]) -> str:
    axes = state["axes"][: state["rank"]]
    axis_keys = [axis["key"] for axis in axes]
    project = state.get("project", {}).get("name", "project").replace(" ", "_")
    lines = [
        f"HK/{state['schema_version']} project={project} rank={state['rank']} axes={','.join(axis_keys)}",
        "FLAGS=" + ",".join(f"{index}:{name}" for index, name in enumerate(FLAG_NAMES)),
    ]
    for card in state["cards"]:
        deps = ".".join(card["deps"]) if card["deps"] else "-"
        path = ";".join(f"{key}={card['coords'][key]}" for key in axis_keys)
        tags = ".".join(card.get("tags", []))
        lines.append(f"{card['id']}|{card['byte']:02X}|d:{deps}|p:{path}|t:{tags}")
    return "\n".join(lines) + "\n"


def decoded_flags(byte: int) -> list[str]:
    return [name for index, name in enumerate(FLAG_NAMES) if byte & (1 << index)]


def cards(state: dict[str, Any]) -> list[dict[str, Any]]:
    return list(state["cards"])


def find_card(state: dict[str, Any], card_id: str) -> dict[str, Any]:
    for card in state["cards"]:
        if card["id"] == card_id:
            return card
    raise HyperKanbanError(f"unknown card id: {card_id}")


def dependency_done(state: dict[str, Any], card: dict[str, Any]) -> bool:
    by_id = {item["id"]: item for item in state["cards"]}
    for dep in card.get("deps", []):
        if not (by_id[dep]["byte"] & DONE):
            return False
    return True


def is_done(card: dict[str, Any]) -> bool:
    return bool(card["byte"] & DONE) or card.get("coords", {}).get("state") == "done"


def is_blocked(state: dict[str, Any], card: dict[str, Any]) -> bool:
    return bool(card["byte"] & BLOCKED) or card.get("coords", {}).get("state") == "blocked" or not dependency_done(state, card)


def next_card(state: dict[str, Any]) -> dict[str, Any] | None:
    candidates = [card for card in state["cards"] if not is_done(card) and not is_blocked(state, card)]
    if not candidates:
        return None
    return sorted(
        candidates,
        key=lambda card: (
            int(card["coords"].get("ring", 0)),
            int(card["coords"].get("shell", 0)),
            int(card["coords"].get("branch", 0)),
            str(card["coords"].get("risk", "none")),
            card["id"],
        ),
    )[0]


def format_card(card: dict[str, Any]) -> str:
    flags = ",".join(decoded_flags(card["byte"])) or "none"
    deps = ",".join(card.get("deps", [])) or "-"
    coords = ";".join(f"{key}={value}" for key, value in card.get("coords", {}).items())
    return "\n".join(
        [
            f"{card['id']}: {card['title']}",
            f"byte=0x{card['byte']:02X} flags={flags}",
            f"deps={deps}",
            f"coords={coords}",
            f"tags={','.join(card.get('tags', [])) or '-'}",
            card.get("desc", ""),
        ]
    )
