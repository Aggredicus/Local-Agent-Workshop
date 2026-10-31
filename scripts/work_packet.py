#!/usr/bin/env python3
"""Validate or preview a CAW work packet; never start an agent."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from workshop.caw_contract import load_and_validate,dry_run  # noqa: E402

def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("action", choices=("validate","plan"))
    ap.add_argument("--schema",type=Path,required=True,help="Path to reviewed CAW/contracts/caw-law-work-packet.v1.json")
    ap.add_argument("--packet",type=Path,required=True,help="Work packet JSON file")
    args=ap.parse_args()
    try:
        packet=load_and_validate(args.schema,args.packet)
        if args.action=="validate":
            print("Valid CAW/LAW v1 work-packet proposal; no permission granted")
        else:
            print(json.dumps(dry_run(packet),indent=2,sort_keys=True))
        return 0
    except (ValueError,OSError,TypeError,KeyError,json.JSONDecodeError):
        print("CAW/LAW work-packet rejected; no command was run",file=sys.stderr)
        return 1
if __name__=="__main__":
    raise SystemExit(main())
