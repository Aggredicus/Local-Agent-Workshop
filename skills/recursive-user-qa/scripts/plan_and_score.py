#!/usr/bin/env python3
"""Local-only synthetic-cohort planning and provenance checks. Standard library."""
import argparse, json, math
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument("pilot",type=Path)
p.add_argument("--expanded",type=Path)
p.add_argument("--budget-seconds",type=float,default=90)
p.add_argument("--per-session",type=float,default=1.2)
p.add_argument("--roles",type=int,default=3)
p.add_argument("--contexts",type=int,default=4)
p.add_argument("--session-cap",type=int,default=12)
a=p.parse_args()
def read(path):
 d=json.loads(path.read_text())
 if d.get("n",d.get("completed_n")) is None:raise ValueError("Missing completed session count")
 if d.get("passed",0)>d.get("total",0):raise ValueError("Passed exceeds total")
 if d.get("source_of_personas","synthetic").startswith("human"):raise ValueError("Human cohort must be separate")
 for s in d.get("sessions",[]):
  if s.get("source_type","").startswith("human"):raise ValueError("Mixed human cohort")
 return d
pilot=read(a.pilot)
if pilot.get("n",pilot.get("completed_n"))!=3:raise ValueError("n=3 pilot required")
cap=min(a.roles*a.contexts,a.session_cap,math.floor(max(0,a.budget_seconds)/max(a.per_session,.1)))
good=pilot["passed"]==pilot["total"]
out={"pilot_passed":pilot["passed"],"pilot_total":pilot["total"],"pilot_green":good,"unique_coverage_cells":a.roles*a.contexts,"proposed_x":cap,"budget_seconds":a.budget_seconds,"decision":"FIX_AND_RETEST_PILOT" if not good else ("EXPAND" if cap>=3 else "STOP_RESOURCE_BUDGET"),"provenance":"Simulated personas; not human user data"}
if a.expanded:
 d=read(a.expanded)
 out.update({"expanded_passed":d["passed"],"expanded_total":d["total"],"expanded_green":d["passed"]==d["total"],"actual_x":d.get("completed_n")})
print(json.dumps(out,indent=2))
