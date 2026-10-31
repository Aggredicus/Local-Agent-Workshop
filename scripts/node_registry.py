#!/usr/bin/env python3
"""Serverless local node registry. No server, paid service or extra Python packages.

The registry stores only *proposed* permissions. GitHub remains responsible for
authenticated PR authorship, required reviews and merge permissions.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from workshop.local_registry import LocalRegistry  # noqa: E402

DB = ROOT / ".local" / "nodes.sqlite3"

def skills(taxonomy_path: Path) -> set[str]:
    if taxonomy_path.is_symlink() or not taxonomy_path.is_file():
        raise ValueError("Provide an accessible, reviewed CAW taxonomy JSON file")
    taxonomy = json.loads(taxonomy_path.read_text("utf-8"))
    if taxonomy.get("schema_version") != 1:
        raise ValueError("Unsupported taxonomy version")
    items = taxonomy["categories"]
    if not isinstance(items, list) or len(items) > 500:
        raise ValueError("Invalid taxonomy list")
    result = {x["id"] for x in items if isinstance(x, dict) and isinstance(x.get("id"),str)}
    if len(result) != len(items):
        raise ValueError("Invalid or duplicate skill IDs")
    return result

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    enroll = sub.add_parser("enroll")
    enroll.add_argument("--kind", choices=("human","computer","agent"), required=True)
    enroll.add_argument("--operator-id")
    enroll.add_argument("--computer-id")
    for k in ("source","version","digest"):
        enroll.add_argument("--" + k)
    change = sub.add_parser("upgrade")
    change.add_argument("--id", required=True)
    for k in ("source","version","digest"):
        change.add_argument("--" + k, required=True)
    inventory = sub.add_parser("inventory")
    inventory.add_argument("--id", required=True)
    inventory.add_argument("--skill", action="append", default=[])
    proposal = sub.add_parser("propose")
    proposal.add_argument("--id", required=True)
    proposal.add_argument("--skill", required=True)
    proposal.add_argument("--action", required=True,
                          choices=("skill.execute","pr.propose","pr.review","pr.merge"))
    probe = sub.add_parser("probe", help="Record local nonidentifying hardware capabilities")
    probe.add_argument("--id", required=True, help="Previously enrolled computer ID")
    sub.add_parser("summary")
    parser.add_argument("--taxonomy", type=Path, help="Path to reviewed CAW skill-inventory/taxonomy.json, required for inventory and proposals")
    args = parser.parse_args()

    try:
        if args.command in {"inventory","propose"} and args.taxonomy is None:
            raise ValueError("This command needs --taxonomy /path/to/reviewed/CAW/skill-inventory/taxonomy.json")
        with LocalRegistry(DB) as store:
            if args.command == "enroll":
                result = store.enroll(args.kind, operator_id=args.operator_id,
                       computer_id=args.computer_id, source=args.source,
                       version=args.version, digest=args.digest)
            elif args.command == "upgrade":
                result = store.upgrade(args.id,source=args.source,
                       version=args.version,digest=args.digest)
            elif args.command == "inventory":
                result = store.capabilities(args.id,args.skill,known=skills(args.taxonomy))
            elif args.command == "propose":
                result = {"proposal_id":store.propose(args.id,args.skill,args.action,
                         known=skills(args.taxonomy)),"authorization":"not-granted"}
            elif args.command == "probe":
                from workshop.hardware_probe import observe
                result = store.record_hardware(args.id, observe())
            else:
                result = store.summary()
        print(json.dumps(result,sort_keys=True) if isinstance(result,dict) else result)
        return 0
    except (ValueError,OSError,KeyError,TypeError,json.JSONDecodeError):
        print("Registry action rejected; private data not shown",file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
