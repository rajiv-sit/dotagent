from __future__ import annotations
from pathlib import Path
from .utils import ensure_dir, write_json

def setup_runtime(project_root: str) -> dict:
    root = Path(project_root)
    ensure_dir(root / ".dotagent-state")
    ensure_dir(root / ".dotagent-state" / "jobs")
    ensure_dir(root / ".dotagent-state" / "plans")
    ensure_dir(root / ".dotagent-state" / "events")
    ensure_dir(root / ".dotagent-state" / "evidence")
    ensure_dir(root / ".dotagent-state" / "memory")
    ensure_dir(root / ".dotagent-state" / "telemetry")
    ensure_dir(root / ".agent")
    return {"ok": True, "project_root": str(root.resolve())}
