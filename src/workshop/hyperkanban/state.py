"""HyperKanban state operations.

This module keeps core orchestration behavior testable outside GitHub Actions.
Early commands are intentionally small: load, validate, list, show, select the
next unblocked card, emit a compact packet, and complete a card with evidence.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
import stat
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from workshop.hyperkanban.validation import HyperKanbanError, validate_data

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


class _LoadedState(dict):
    """In-memory revision metadata is never serialized into project state."""
    revision: str
    source: Path


def _read_regular(path: Path, label: str) -> bytes:
    info = path.lstat()
    if (not stat.S_ISREG(info.st_mode)
            or getattr(info, 'st_file_attributes', 0) & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0x400)):
        raise HyperKanbanError(f'{label} must be a regular file, not a link or special file')
    return path.read_bytes()


def load_state(path: Path = DEFAULT_STATE_PATH) -> dict[str, Any]:
    try:
        raw = _read_regular(path, 'state')
        data = json.loads(raw)
    except OSError as exc:
        raise HyperKanbanError(f"missing or unreadable state file: {path}") from exc
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise HyperKanbanError("invalid JSON in state file") from exc
    validate_state(data)
    loaded = _LoadedState(data)
    loaded.revision = hashlib.sha256(raw).hexdigest()
    loaded.source = path.resolve()
    return loaded


def validate_packet(state: dict[str, Any], state_path: Path) -> None:
    packet = state_path.parent / "packet.txt"
    try:
        current = _read_regular(packet, 'packet').decode('utf-8') if packet.exists() or packet.is_symlink() else None
    except (OSError, UnicodeError) as exc:
        raise HyperKanbanError('packet is unreadable UTF-8; repair it from canonical state') from exc
    if current is not None and current != build_packet(state):
        raise HyperKanbanError(f"packet out of sync: {packet}")


def validate_state_file(path: Path) -> dict[str, Any]:
    state = load_state(path)
    validate_packet(state, path)
    return state


def _atomic_write(path: Path, content: str) -> None:
    if path.is_symlink():
        raise HyperKanbanError("refusing symlink state or packet")
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as output:
            output.write(content)
            output.flush()
            os.fsync(output.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def _packet_path(path: Path) -> Path:
    packet = path.parent / "packet.txt"
    if (path.resolve() == packet.resolve()
            or (path.exists() and packet.exists() and os.path.samefile(path, packet))):
        raise HyperKanbanError("canonical state cannot alias its derived packet")
    if packet.is_symlink():
        raise HyperKanbanError("refusing symlink packet")
    return packet


@contextmanager
def _state_lock(path: Path):
    _packet_path(path)  # Check aliases before any canonical write.
    if path.is_symlink():
        raise HyperKanbanError("refusing symlink state")
    lock = path.with_name(f".{path.name}.lock")
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise HyperKanbanError("state is locked; check active writers before removing a stale lock") from None
    try:
        os.close(fd)
        yield
    finally:
        lock.unlink()


def _check_revision(path: Path, state: dict[str, Any]) -> None:
    if isinstance(state, _LoadedState):
        if (not path.exists() or state.source != path.resolve()
                or hashlib.sha256(path.read_bytes()).hexdigest() != state.revision):
            raise HyperKanbanError("state changed or was removed; reload before saving")
    elif path.exists():
        raise HyperKanbanError("state changed or was not loaded with a revision; reload before saving")


def _commit(path: Path, state: dict[str, Any]) -> None:
    validate_state(state)
    _check_revision(path, state)
    content = json.dumps(state, indent=2) + "\n"
    _atomic_write(path, content)
    if isinstance(state, _LoadedState):
        state.revision = hashlib.sha256(content.encode("utf-8")).hexdigest()


def save_state(path: Path, state: dict[str, Any]) -> None:
    with _state_lock(path):
        _commit(path, state)


def save_packet(state_path: Path, state: dict[str, Any]) -> None:
    with _state_lock(state_path):
        _check_revision(state_path, state)
        canonical = load_state(state_path)
        if state != canonical:
            raise HyperKanbanError("packet must derive from unchanged canonical state")
        _atomic_write(_packet_path(state_path), build_packet(canonical))


def save_state_and_packet(path: Path, state: dict[str, Any]) -> None:
    with _state_lock(path):
        _commit(path, state)
        try:
            _atomic_write(_packet_path(path), build_packet(state))
        except OSError as exc:
            raise HyperKanbanError("state saved; packet refresh failed. Run workshop hk --state PATH repair-packet.") from exc


def validate_state(state: dict[str, Any]) -> None:
    validate_data(state)


def validate_completion_evidence(card: dict[str, Any]) -> None:
    if completion_requires_evidence(card) and not completion_has_evidence_or_exception(card):
        raise HyperKanbanError(f"card {card['id']} is done but lacks required evidence or exception")


def completion_requires_evidence(card: dict[str, Any]) -> bool:
    test_contract = card.get("test_contract", {})
    doc_contract = card.get("doc_contract", {})
    return bool(test_contract.get("required") or doc_contract.get("required"))


def completion_has_evidence_or_exception(card: dict[str, Any]) -> bool:
    return bool(card.get("evidence_paths") or card.get("open_exceptions"))


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
        if not is_done(by_id[dep]):
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


def complete_card(state: dict[str, Any], card_id: str, evidence: list[str] | None = None,
                  exception: str | None = None, *, evidence_root: Path | None = None) -> dict[str, Any]:
    """Record completion evidence; this projection never grants authorization.

    Exceptions remain legacy, unverified annotations. File existence and a hash
    identify an artifact, not proof that it contains passing results.
    """
    card = copy.deepcopy(find_card(state, card_id))
    if is_blocked(state, card):
        raise HyperKanbanError(f"card {card_id} is blocked and cannot be completed")
    if evidence:
        paths = card.setdefault("evidence_paths", [])
        paths.extend(item for item in evidence if item not in paths)
    root = (evidence_root or Path.cwd()).resolve()
    for item in card.get("evidence_paths", []):
        if not isinstance(item, str) or Path(item).is_absolute() or ".." in Path(item).parts:
            raise HyperKanbanError("evidence must name contained relative artifact files")
        path = (root / item).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise HyperKanbanError("evidence file is missing or escapes the evidence root")
        card.setdefault("evidence_sha256", {})[item] = hashlib.sha256(path.read_bytes()).hexdigest()
    if exception:
        if not exception.strip():
            raise HyperKanbanError("exception annotation cannot be empty")
        exceptions = card.setdefault("open_exceptions", [])
        if exception not in exceptions:
            exceptions.append(exception)
    if completion_requires_evidence(card) and not completion_has_evidence_or_exception(card):
        raise HyperKanbanError(f"card {card_id} requires evidence or review-card exception before completion")
    card["byte"] = (card["byte"] | DONE) & ~(READY | ACTIVE | BLOCKED)
    card["coords"]["state"] = "done"
    candidate = dict(state)
    candidate["cards"] = [card if item["id"] == card_id else item for item in state["cards"]]
    validate_state(candidate)
    state["cards"] = candidate["cards"]
    return card


def format_card(card: dict[str, Any]) -> str:
    flags = ",".join(decoded_flags(card["byte"])) or "none"
    deps = ",".join(card.get("deps", [])) or "-"
    coords = ";".join(f"{key}={value}" for key, value in card.get("coords", {}).items())
    evidence = ",".join(card.get("evidence_paths", [])) or "-"
    return "\n".join(
        [
            f"{card['id']}: {card['title']}",
            f"byte=0x{card['byte']:02X} flags={flags}",
            f"deps={deps}",
            f"coords={coords}",
            f"tags={','.join(card.get('tags', [])) or '-'}",
            f"evidence={evidence}",
            card.get("desc", ""),
        ]
    )
