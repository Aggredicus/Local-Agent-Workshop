"""Offline CAW→LAW contract validation and safe dry-run execution planning.

The canonical contract lives in CAW/contracts/caw-law-work-packet.v1.json.
No duplicate static schema is bundled here. Input does NOT authorize execution.
"""
from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
import re

ID = "caw.law.work-packet"

def _read_json(path: Path) -> dict:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 100_000:
        raise ValueError("Contract/packet must be a regular local JSON file under 100KB")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("Expected a JSON object")
    return value

def load_contract(path: Path) -> dict:
    contract = _read_json(path)
    if (contract.get("contract_id") != ID or contract.get("schema_version") != 1
            or contract.get("contract_status") != "proposal"
            or contract.get("security", {}).get("self_grant_forbidden") is not True):
        raise ValueError("Unsupported or unsafe contract definition")
    if not isinstance(contract.get("required"), list) or not isinstance(contract.get("fields"), dict):
        raise ValueError("Invalid contract field map")
    return contract

def _path(value: str) -> bool:
    if not isinstance(value, str) or not (1 <= len(value) <= 200):
        return False
    if "\\" in value or "\x00" in value or value.startswith("/") or ":" in value or "*" in value:
        return False
    parts = PurePosixPath(value).parts
    return bool(parts) and all(x not in {".","..",""} for x in value.split("/")) and parts[0] not in {".git",".local"}

def _check(value: object, rule: dict) -> bool:
    typ = rule["type"]
    if typ == "integer":
        valid = type(value) is int
    elif typ == "string":
        valid = isinstance(value, str)
        if valid:
            if len(value) > rule.get("max_length", 4096) or len(value) < rule.get("min_length", 0):
                return False
            if "pattern" in rule and not re.fullmatch(rule["pattern"], value):
                return False
            if "enum" in rule and value not in rule["enum"]:
                return False
    elif typ == "array":
        valid = isinstance(value, list) and len(value) <= rule["max_items"]
        if valid:
            valid = len(set(json.dumps(v, sort_keys=True) for v in value)) == len(value)
            valid = valid and all(_check(v, rule["items"]) for v in value)
    elif typ == "object":
        valid = isinstance(value, dict)
        if valid:
            valid = set(rule["required"]) <= set(value) and set(value) <= set(rule["fields"])
            valid = valid and all(_check(v, rule["fields"][k]) for k,v in value.items())
    elif typ == "skill-id" or typ == "slug":
        valid = isinstance(value, str) and re.fullmatch(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*", value) is not None and len(value) <= 64
    elif typ == "repo-relative-path":
        valid = _path(value)
    elif typ == "sha256":
        valid = isinstance(value, str) and re.fullmatch(r"sha256:[a-f0-9]{64}", value) is not None
    elif typ == "short-text":
        valid = isinstance(value, str) and 1 <= len(value) <= 300 and "\x00" not in value
    else:
        raise ValueError("Unknown schema type")
    return bool(valid) and ("const" not in rule or value == rule["const"])

def validate_packet(packet: dict, contract: dict) -> dict:
    required, fields = contract["required"], contract["fields"]
    if set(required) - set(packet) or set(packet) - set(fields):
        raise ValueError("Missing or unrecognized work-packet keys")
    for key in sorted(packet):
        if not _check(packet[key], fields[key]):
            raise ValueError("Invalid work-packet field: " + key)
    if not packet["allowed_paths"] or not packet["evidence_required"] or not packet["stop_conditions"]:
        raise ValueError("Missing task execution boundary")
    allowed = set(packet["allowed_paths"])
    if allowed & set(packet["forbidden_paths"]):
        raise ValueError("Allowed and forbidden paths overlap")
    if packet["governance"]["authority"] != "github-verified-human-review":
        raise ValueError("Invalid governance authority")
    return packet

def dry_run(packet: dict) -> dict:
    """Data-only proposal, NOT an executable sandbox configuration."""
    return {
        "schema_version": 1,
        "task_id": packet["task_id"],
        "repository": packet["repository"],
        "agent_origin_digest": packet["requested_agent"]["origin_digest"],
        "required_skills": packet["required_skills"],
        "allowed_worktree_paths": packet["allowed_paths"],
        "forbidden_paths": packet["forbidden_paths"],
        "network": "deny",
        "host_credentials": "deny",
        "host_filesystem": "deny",
        "workspace_write": "deny-until-trusted-runner",
        "execution_enabled": False,
        "approval_state": "requires-trusted-human-verification",
        "enforcement_notice": "No sandbox is started. Enforcement requires a separately reviewed LAW runner and host OS isolation.",
    }

def load_and_validate(schema: Path, packet: Path) -> dict:
    return validate_packet(_read_json(packet), load_contract(schema))
