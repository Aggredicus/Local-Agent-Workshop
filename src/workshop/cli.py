from __future__ import annotations

import argparse
import sys
from pathlib import Path

from workshop.hyperkanban.state import (
    DEFAULT_STATE_PATH,
    HyperKanbanError,
    build_packet,
    cards,
    find_card,
    format_card,
    load_state,
    next_card,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="workshop", description="Local Agent Workshop CLI")
    subparsers = parser.add_subparsers(dest="command")

    hk = subparsers.add_parser("hk", help="Read HyperKanban orchestration state")
    hk.add_argument(
        "--state",
        type=Path,
        default=DEFAULT_STATE_PATH,
        help="Path to HyperKanban state.json",
    )
    hk_subparsers = hk.add_subparsers(dest="hk_command")

    hk_subparsers.add_parser("validate", help="Validate HyperKanban state")
    hk_subparsers.add_parser("packet", help="Print compact HyperKanban packet")
    hk_subparsers.add_parser("next", help="Print the next unblocked unfinished card")
    hk_subparsers.add_parser("list", help="List HyperKanban cards")

    show = hk_subparsers.add_parser("show", help="Show one HyperKanban card")
    show.add_argument("card_id", help="HyperKanban card ID, e.g. HK-001")

    return parser


def handle_hk(args: argparse.Namespace) -> int:
    state = load_state(args.state)

    if args.hk_command == "validate":
        print(f"HyperKanban validation passed: {args.state}")
        return 0

    if args.hk_command == "packet":
        print(build_packet(state), end="")
        return 0

    if args.hk_command == "next":
        selected = next_card(state)
        if selected is None:
            print("No unblocked unfinished HyperKanban card found.")
            return 1
        print(format_card(selected))
        return 0

    if args.hk_command == "list":
        for card in cards(state):
            print(f"{card['id']}\t0x{card['byte']:02X}\t{card['coords'].get('state')}\t{card['title']}")
        return 0

    if args.hk_command == "show":
        print(format_card(find_card(state, args.card_id)))
        return 0

    raise HyperKanbanError("missing hk subcommand")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "hk":
        try:
            return handle_hk(args)
        except HyperKanbanError as exc:
            print(f"workshop hk failed: {exc}", file=sys.stderr)
            return 1

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
