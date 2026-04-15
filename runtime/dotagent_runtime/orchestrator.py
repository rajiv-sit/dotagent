from __future__ import annotations
from typing import Dict, Any, List
from .planner import Planner
from .validator import Validator
from .tools import default_registry
from .state_store import StateStore
from .memory import MemoryManager, MemoryEntry
from .evidence import build_evidence_bundle
from .models import Job

class Orchestrator:
    def __init__(self, project_root: str) -> None:
        self.project_root = project_root
        self.store = StateStore(project_root)
        self.memory = MemoryManager(project_root)
        self.planner = Planner()
        self.validator = Validator()
        self.tools = default_registry()

    def prepare_task(self, goal: str) -> Dict[str, Any]:
        job = Job.create("task", {"goal": goal}, {"prepared_only": True})
        plan = self.planner.create_plan(goal, job_type="task")
        self.store.save_job(job)
        self.store.save_plan(plan)
        self.store.emit_event("job_prepared", {"job_id": job.id, "plan_id": plan.id, "goal": goal})
        return {"job": job.to_dict(), "plan": plan.to_dict()}

    def prepare_review(self, target: str) -> Dict[str, Any]:
        job = Job.create("review", {"target": target}, {"prepared_only": True})
        plan = self.planner.create_plan(f"Review {target}", job_type="review")
        self.store.save_job(job)
        self.store.save_plan(plan)
        self.store.emit_event("review_prepared", {"job_id": job.id, "plan_id": plan.id, "target": target})
        return {"job": job.to_dict(), "plan": plan.to_dict()}

    def execute_plan(self, job_id: str, plan_id: str, target: str | None = None) -> Dict[str, Any]:
        job = self.store.load_job(job_id)
        plan = self.store.load_plan(plan_id)
        if not job or not plan:
            raise ValueError("Job or plan not found")

        self.store.update_job(job_id, status="RUNNING", metadata={**job.get("metadata", {}), "prepared_only": False})
        self.store.emit_event("job_running", {"job_id": job_id, "plan_id": plan_id})

        outputs: List[Dict[str, Any]] = []

        for step in plan["steps"]:
            tool_name = step.get("tool") or "shell"
            tool = self.tools.get(tool_name)
            payload = {"step_id": step["id"]}

            if tool_name == "shell":
                payload["command"] = step.get("payload", {}).get("command")
            elif tool_name == "review_tool":
                payload["target"] = target or job["input"].get("target") or job["input"].get("goal")
            elif tool_name == "validator":
                payload["checks"] = [{"source": "orchestrator"}]

            result = tool.execute(self.project_root, payload)
            result_dict = {
                "step_id": result.step_id,
                "tool": result.tool,
                "ok": result.ok,
                "output": result.output,
                "started_at": result.started_at,
                "ended_at": result.ended_at,
            }
            outputs.append(result_dict)
            self.store.emit_event("step_executed", {"job_id": job_id, "step_id": step["id"], "tool": tool_name, "ok": result.ok})

            if not result.ok:
                break

        validation = self.validator.validate_job_outputs(outputs)
        validation_dict = {
            "status": validation.status,
            "summary": validation.summary,
            "checks": validation.checks,
            "corrective_actions": validation.corrective_actions
        }

        final_status = "SUCCESS" if validation.status == "PASS" else "FAILED"
        updated_job = self.store.update_job(job_id, status=final_status, output={"outputs": outputs, "validation": validation_dict})

        bundle = build_evidence_bundle(updated_job, plan, outputs, validation_dict)
        evidence_path = self.store.write_evidence_bundle(job_id, bundle)

        self.memory.put(MemoryEntry(namespace="jobs", text=f"{job['type']} {job_id} {final_status}", metadata={
            "job_id": job_id,
            "status": final_status,
            "plan_id": plan_id
        }))

        self.store.emit_event("job_finished", {"job_id": job_id, "status": final_status, "evidence_path": str(evidence_path)})
        return {"job": updated_job, "plan": plan, "validation": validation_dict, "evidence_path": str(evidence_path)}

    def status(self) -> Dict[str, Any]:
        return {"jobs": self.store.list_jobs()}

    def result(self, job_id: str) -> Dict[str, Any]:
        job = self.store.load_job(job_id)
        if not job:
            raise ValueError("Job not found")
        evidence = None
        evidence_path = self.store.evidence_dir / f"{job_id}.json"
        if evidence_path.exists():
            import json
            evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        return {"job": job, "evidence": evidence}
