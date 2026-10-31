"""CAW-to-LAW data contract security tests.

Tests use an in-memory stand-in contract. Production reads one canonical
contract JSON from a reviewed CAW checkout; LAW does not bundle a fork.
"""
import copy
import json
from pathlib import Path

import pytest
from workshop.caw_contract import dry_run, load_contract, load_and_validate, validate_packet

DIGEST = "sha256:" + "a"*64

@pytest.fixture
def schema():
    # Minimal fixture tests the generic interpreter, not a second source-of-truth contract.
    return {
        "schema_version":1, "contract_id":"caw.law.work-packet",
        "contract_status":"proposal",
        "security":{"self_grant_forbidden":True},
        "required":["schema_version","contract_id","task_id","repository","objective",
                    "risk","required_skills","allowed_paths","forbidden_paths",
                    "evidence_required","stop_conditions","requested_agent","governance"],
        "fields":{
            "schema_version":{"type":"integer","const":1},
            "contract_id":{"type":"string","const":"caw.law.work-packet"},
            "task_id":{"type":"string","pattern":"^[A-Z0-9][A-Z0-9_-]{1,63}$"},
            "repository":{"type":"string","pattern":"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$"},
            "objective":{"type":"string","min_length":8,"max_length":1500},
            "risk":{"type":"string","enum":["low","medium","high"]},
            "required_skills":{"type":"array","max_items":50,"items":{"type":"skill-id"}},
            "allowed_paths":{"type":"array","max_items":100,"items":{"type":"repo-relative-path"}},
            "forbidden_paths":{"type":"array","max_items":100,"items":{"type":"repo-relative-path"}},
            "evidence_required":{"type":"array","max_items":40,"items":{"type":"short-text"}},
            "stop_conditions":{"type":"array","max_items":40,"items":{"type":"short-text"}},
            "requested_agent":{"type":"object","required":["runtime","origin_digest"],
                "fields":{"runtime":{"type":"slug"},"origin_digest":{"type":"sha256"}}},
            "governance":{"type":"object","required":["approval_state","authority"],
                "fields":{"approval_state":{"type":"string","enum":["proposal","needs-human-review"]},
                          "authority":{"type":"string","const":"github-verified-human-review"}}}
        }
    }

@pytest.fixture
def packet():
    return {
        "schema_version":1,"contract_id":"caw.law.work-packet",
        "task_id":"CAW-21","repository":"Aggredicus/ConsciOS",
        "objective":"Implement a small, reversible documentation fix",
        "risk":"low","required_skills":["python"],
        "allowed_paths":["docs"],"forbidden_paths":[".github","secrets"],
        "evidence_required":["reproducible test log"],"stop_conditions":["unknown credential required"],
        "requested_agent":{"runtime":"codex","origin_digest":DIGEST},
        "governance":{"approval_state":"proposal","authority":"github-verified-human-review"}
    }

def test_valid_packet_is_never_executable(schema,packet):
    validated = validate_packet(packet,schema)
    plan = dry_run(validated)
    assert plan["execution_enabled"] is False
    assert plan["network"] == "deny"
    assert plan["host_credentials"] == "deny"
    assert plan["workspace_write"] == "deny-until-trusted-runner"
    assert plan["allowed_worktree_paths"] == ["docs"]

@pytest.mark.parametrize("bad", [
    "../private","/etc/passwd","src\\..\\private",".git/config","/home/user",
    "src/*","C:/Users/name","src//docs",".local/nodes.sqlite3"
])
def test_paths_reject_escape(schema,packet,bad):
    packet["allowed_paths"]=[bad]
    with pytest.raises(ValueError):
        validate_packet(packet,schema)

def test_requires_review_and_rejects_extra_fields(schema,packet):
    packet["governance"]["approval_state"]="approved"
    with pytest.raises(ValueError):
        validate_packet(packet,schema)
    packet["governance"]["approval_state"]="proposal"
    packet["credentials"]={"token":"not-allowed"}
    with pytest.raises(ValueError):
        validate_packet(packet,schema)

def test_skill_lists_reject_duplicates(schema,packet):
    packet["required_skills"]=["python","python"]
    with pytest.raises(ValueError):
        validate_packet(packet,schema)

def test_unsupported_and_symlinked_schema_fails(tmp_path,schema,packet):
    s=tmp_path/"schema.json";s.write_text(json.dumps(schema))
    p=tmp_path/"packet.json";p.write_text(json.dumps(packet))
    assert load_and_validate(s,p)["task_id"]=="CAW-21"
    schema["schema_version"]=2
    s.write_text(json.dumps(schema))
    with pytest.raises(ValueError):
        load_contract(s)
    s.write_text(json.dumps({**schema,"schema_version":1}))
    symlink=tmp_path/"link.json";symlink.symlink_to(s)
    with pytest.raises(ValueError):
        load_contract(symlink)

def test_high_risk_still_dry_run(schema,packet):
    packet["risk"]="high"
    assert not dry_run(validate_packet(packet,schema))["execution_enabled"]
