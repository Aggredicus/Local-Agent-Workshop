#!/usr/bin/env python3
"""CLI adapter for the shared HyperKanban validator; no duplicate rules."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from workshop.hyperkanban.state import build_packet, validate_packet, validate_state_file  # noqa: E402,F401
from workshop.hyperkanban.validation import (  # noqa: E402,F401
    validate_axes, validate_card_shape, validate_coords, validate_dependencies,
)

DEFAULT_STATE = Path("orchestration/hyperkanban/state.json")


def validate_state(path: Path) -> None:
    validate_state_file(path)


def main(argv=None) -> int:
    args = sys.argv[1:] if argv is None else argv
    path = Path(args[0]) if args else DEFAULT_STATE
    try:
        validate_state(path)
    except (ValueError, OSError):
        print("HyperKanban validation failed; inspect state and regenerate its packet.", file=sys.stderr)
        return 1
    print(f"HyperKanban validation passed: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
