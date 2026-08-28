from __future__ import annotations

import argparse
import sys
from pathlib import Path

from workshop.doctor import format_checks, has_failures, run_doctor
from workshop.hyperkanban.state import (
    DEFAULT_STATE_PATH,
    HyperKanbanError,
    build_packet,
    cards,
    complete_card,
    find_card,
    format_card,
    load_state,
    next_card,
    save_state_and_packet,
)
from workshop.skills import discover_skills, sync_skills, validate_skills


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="workshop", description="Local Agent Workshop CLI")
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")
    subparsers = parser.add_subparsers(dest="command")

    doctor = subparsers.add_parser("doctor", help="Check whether this checkout is ready for local agent work")
    doctor.add_argument("--repo", type=Path, default=Path.cwd(), help="Repository root (default: current directory)")

    skills = subparsers.add_parser("skills", help="Inspect and synchronize Agent Skills")
    skills.add_argument("--root", type=Path, default=Path("skills"), help="Canonical skills directory")
    skills_subparsers = skills.add_subparsers(dest="skills_command")
    skills_subparsers.add_parser("list", help="List canonical skills")
    validate = skills_subparsers.add_parser("validate", help="Validate canonical skills for Agent Skills synchronization")
    validate.add_argument("--strict", action="store_true", help="Require every source SKILL.md to already conform to the Agent Skills frontmatter spec")
    sync = skills_subparsers.add_parser("sync", help="Copy canonical skills to a client-discoverable project directory")
    sync.add_argument("--target", type=Path, default=Path(".agents/skills"), help="Generated project skill directory")

    hk = subparsers.add_parser("hk", help="Read and update HyperKanban orchestration state")
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

    complete = hk_subparsers.add_parser("complete", help="Complete a HyperKanban card with evidence")
    complete.add_argument("card_id", help="HyperKanban card ID, e.g. HK-001")
    complete.add_argument(
        "--evidence",
        action="append",
        default=[],
        help="Evidence path proving completion; may be supplied multiple times",
    )
    complete.add_argument(
        "--exception",
        help="Review-card exception allowing completion when required evidence is absent",
    )

    return parser


def handle_doctor(args: argparse.Namespace) -> int:
    checks = run_doctor(args.repo)
    print(format_checks(checks))
    return 1 if has_failures(checks) else 0


def handle_skills(args: argparse.Namespace) -> int:
    if args.skills_command == "list":
        items = discover_skills(args.root)
        if not items:
            print(f"No skills found under {args.root}")
            return 1
        for item in items:
            status = "INVALID" if item.errors else ("LEGACY" if item.legacy else "OK")
            print(f"{status}\t{item.name}\t{item.description or '-'}")
        return 0

    if args.skills_command == "validate":
        items = discover_skills(args.root)
        if not items:
            print(f"Skill validation failed: no skills found under {args.root}", file=sys.stderr)
            return 1
        invalid = validate_skills(args.root, strict=args.strict)
        if invalid:
            for item in invalid:
                print(f"INVALID {item.path}: {'; '.join(item.errors)}", file=sys.stderr)
            return 1
        legacy = sum(1 for item in items if item.legacy)
        suffix = f"; {legacy} legacy source skill(s) will be normalized during sync" if legacy and not args.strict else ""
        print(f"Agent Skills source validation passed: {len(items)} skill(s){suffix}")
        return 0

    if args.skills_command == "sync":
        try:
            copied = sync_skills(args.root, args.target)
        except ValueError as exc:
            print(f"Skill sync failed: {exc}", file=sys.stderr)
            return 1
        print(f"Synchronized {len(copied)} skill(s) to {args.target}")
        return 0

    print("Missing skills subcommand. Choose list, validate, or sync.", file=sys.stderr)
    return 2


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

    if args.hk_command == "complete":
        completed = complete_card(state, args.card_id, evidence=args.evidence, exception=args.exception)
        save_state_and_packet(args.state, state)
        print(f"Completed {completed['id']} with byte=0x{completed['byte']:02X}")
        return 0

    raise HyperKanbanError("missing hk subcommand")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "doctor":
        return handle_doctor(args)

    if args.command == "skills":
        return handle_skills(args)

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
