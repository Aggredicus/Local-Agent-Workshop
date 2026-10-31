"""Coarse hardware observations; never collect device identifying information.

These observations assist *local* workload suitability checks. They are not
hardware attestation and may describe host resources rather than cgroup limits.
"""
from __future__ import annotations
import os
import platform

def observe() -> dict[str, object]:
    family = platform.system().lower()
    if family not in {"linux","darwin","windows"}:
        family = "other"
    cpus = os.cpu_count()
    cpus = cpus if isinstance(cpus,int) and 0 < cpus <= 4096 else None
    ram_gib = None
    if hasattr(os, "sysconf"):
        try:
            page = os.sysconf("SC_PAGE_SIZE")
            pages = os.sysconf("SC_PHYS_PAGES")
            if isinstance(page,int) and isinstance(pages,int):
                total = page * pages
                if 0 < total < 2**60:
                    ram_gib = round(total / 2**30)
        except (OSError, ValueError, TypeError):
            pass
    return {
        "schema_version":1,
        "os_family":family,
        "logical_cpus":cpus,
        "memory_gib_estimate":ram_gib,
        "gpu":"unknown-not-probed",
        "scope":"local-advisory-not-attested",
    }
