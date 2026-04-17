from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import Job, Plan, utc_now
from .utils import append_jsonl, ensure_dir, read_json, write_json


class StateStore:
    def __init__(self, project_root: str) -> None:
        self.project_root = Path(project_root).resolve()
        self.state_root = ensure_dir(self.project_root / ".dotagent-state")
        self.jobs_dir = ensure_dir(self.state_root / "jobs")
        self.plans_dir = ensure_dir(self.state_root / "plans")
        self.events_dir = ensure_dir(self.state_root / "events")
        self.evidence_dir = ensure_dir(self.state_root / "evidence")
        self.memory_dir = ensure_dir(self.state_root / "memory")
        self.telemetry_dir = ensure_dir(self.state_root / "telemetry")

    def job_path(self, job_id: str) -> Path:
        return self.jobs_dir / f"{job_id}.json"

    def plan_path(self, plan_id: str) -> Path:
        return self.plans_dir / f"{plan_id}.json"

    def save_job(self, job: Job) -> None:
        write_json(self.job_path(job.id), job.to_dict())

    def load_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        return read_json(self.job_path(job_id))

    def update_job(self, job_id: str, **fields: Any) -> Dict[str, Any]:
        current = self.load_job(job_id) or {}
        current.update(fields)
        current["updated_at"] = utc_now()
        write_json(self.job_path(job_id), current)
        return current

    def list_jobs(self) -> List[Dict[str, Any]]:
        jobs = [read_json(path, {}) for path in sorted(self.jobs_dir.glob("*.json"))]
        return [job for job in jobs if job]

    def save_plan(self, plan: Plan) -> None:
        write_json(self.plan_path(plan.id), plan.to_dict())

    def load_plan(self, plan_id: str) -> Optional[Dict[str, Any]]:
        return read_json(self.plan_path(plan_id))

    def update_plan(self, plan_id: str, **fields: Any) -> Dict[str, Any]:
        current = self.load_plan(plan_id) or {}
        current.update(fields)
        current["updated_at"] = utc_now()
        write_json(self.plan_path(plan_id), current)
        return current

    def emit_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        append_jsonl(
            self.events_dir / "events.jsonl",
            {
                "time": utc_now(),
                "type": event_type,
                "payload": payload,
            },
        )

    def write_evidence_bundle(self, job_id: str, bundle: Dict[str, Any]) -> Path:
        path = self.evidence_dir / f"{job_id}.json"
        write_json(path, bundle)
        return path

    def write_telemetry_summary(self, job_id: str, summary: Dict[str, Any]) -> Path:
        path = self.telemetry_dir / f"{job_id}.json"
        write_json(path, summary)
        return path

    def load_telemetry_summary(self, job_id: str) -> Optional[Dict[str, Any]]:
        return read_json(self.telemetry_dir / f"{job_id}.json")

    def append_memory(self, namespace: str, item: Dict[str, Any]) -> None:
        append_jsonl(self.memory_dir / f"{namespace}.jsonl", item)
