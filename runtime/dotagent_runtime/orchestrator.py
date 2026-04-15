from __future__ import annotations

from typing import Any, Dict, List

from .evidence import build_evidence_bundle
from .executor import StepExecutor
from .memory import MemoryEntry, MemoryManager
from .models import Job, utc_now
from .planner import Planner
from .state_store import StateStore
from .telemetry import build_telemetry_summary
from .tools import default_registry
from .validator import Validator


class Orchestrator:
    def __init__(self, project_root: str) -> None:
        self.project_root = project_root
        self.store = StateStore(project_root)
        self.memory = MemoryManager(project_root)
        self.planner = Planner()
        self.validator = Validator()
        self.executor = StepExecutor(default_registry())

    def prepare_task(
        self,
        goal: str,
        command: str | None = None,
        execution_target: str = "local",
        enable_parallel: bool = True,
    ) -> Dict[str, Any]:
        memory_hits = self.memory.build_context(goal)
        job = Job.create(
            "task",
            {"goal": goal},
            {"prepared_only": True, "memory_hits": memory_hits, "execution_target": execution_target},
        )
        plan = self.planner.create_plan(
            goal,
            job_type="task",
            command=command,
            context=memory_hits,
            execution_target=execution_target,
            enable_parallel=enable_parallel,
        )
        self.store.save_job(job)
        self.store.save_plan(plan)
        self.store.emit_event("job_prepared", {"job_id": job.id, "plan_id": plan.id, "goal": goal})
        return {"job": job.to_dict(), "plan": plan.to_dict(), "memory_hits": memory_hits}

    def prepare_review(self, target: str) -> Dict[str, Any]:
        memory_hits = self.memory.build_context(target)
        job = Job.create("review", {"target": target}, {"prepared_only": True, "memory_hits": memory_hits})
        plan = self.planner.create_plan(f"Review {target}", job_type="review", context=memory_hits)
        self.store.save_job(job)
        self.store.save_plan(plan)
        self.store.emit_event("review_prepared", {"job_id": job.id, "plan_id": plan.id, "target": target})
        return {"job": job.to_dict(), "plan": plan.to_dict(), "memory_hits": memory_hits}

    def execute_plan(self, job_id: str, plan_id: str, target: str | None = None) -> Dict[str, Any]:
        job = self.store.load_job(job_id)
        plan = self.store.load_plan(plan_id)
        if not job or not plan:
            raise ValueError("Job or plan not found")

        query = target or job["input"].get("goal") or job["input"].get("target", "")
        memory_hits = self.memory.build_context(query)
        self.store.update_job(job_id, status="RUNNING", metadata={**job.get("metadata", {}), "prepared_only": False})
        self.store.emit_event("job_running", {"job_id": job_id, "plan_id": plan_id})

        outputs: List[Dict[str, Any]] = []
        final_validation: Dict[str, Any] = {
            "status": "PASS",
            "summary": "Plan completed.",
            "checks": [],
            "corrective_actions": [],
        }

        while True:
            ready_steps = self._get_ready_steps(plan)
            if not ready_steps:
                break

            for step in ready_steps:
                step["status"] = "RUNNING"
                step["attempts"] = int(step.get("attempts", 0)) + 1
                if step.get("tool") == "validator":
                    step.setdefault("payload", {})["checks"] = self._prior_step_checks(outputs, step)
            self._persist_plan(plan_id, plan)

            base_context = {
                "goal": plan.get("goal"),
                "target": target,
                "memory_hits": memory_hits,
            }
            max_parallelism = int(plan.get("metadata", {}).get("max_parallelism", 1))
            results = self.executor.execute_steps(self.project_root, ready_steps, base_context=base_context, max_parallelism=max_parallelism)

            should_break = False
            for result in results:
                step = next(candidate for candidate in ready_steps if candidate["id"] == result.step_id)
                result_dict = {
                    "step_id": result.step_id,
                    "tool": result.tool,
                    "ok": result.ok,
                    "output": result.output,
                    "started_at": result.started_at,
                    "ended_at": result.ended_at,
                    "attempt": result.attempt,
                    "metadata": {
                        **result.metadata,
                        "agent_role": step.get("agent_role"),
                        "execution_target": step.get("execution_target"),
                    },
                    "duration_ms": result.output.get("metrics", {}).get("duration_ms", 0),
                }

                validation = self.validator.validate_step_result(step, result_dict)
                validation_dict = {
                    "status": validation.status,
                    "summary": validation.summary,
                    "checks": validation.checks,
                    "corrective_actions": validation.corrective_actions,
                    "retryable": validation.retryable,
                }
                result_dict["validation"] = validation_dict
                outputs.append(result_dict)
                final_validation = validation_dict

                self.store.emit_event(
                    "step_executed",
                    {
                        "job_id": job_id,
                        "step_id": step["id"],
                        "tool": step.get("tool"),
                        "attempt": step["attempts"],
                        "validation_status": validation.status,
                        "agent_role": step.get("agent_role"),
                        "execution_target": step.get("execution_target"),
                    },
                )

                if validation.status == "PASS":
                    step["status"] = "SUCCESS"
                    step["last_error"] = None
                    continue

                if validation.retryable:
                    step["status"] = "PENDING"
                    step["last_error"] = validation.summary
                    self.planner.replan_step(plan, step, validation)
                    self.store.emit_event(
                        "step_replanned",
                        {
                            "job_id": job_id,
                            "step_id": step["id"],
                            "attempt": step["attempts"],
                            "corrective_actions": validation.corrective_actions,
                        },
                    )
                    continue

                step["status"] = "FAILED"
                step["last_error"] = validation.summary
                should_break = True

            if should_break:
                self._mark_blocked_steps(plan)
                self._persist_plan(plan_id, plan)
                break

            self._persist_plan(plan_id, plan)

        plan_status = self._plan_status(plan)
        final_status = "SUCCESS" if plan_status == "SUCCESS" else "FAILED"
        updated_job = self.store.update_job(
            job_id,
            status=final_status,
            output={"outputs": outputs, "validation": final_validation, "agent_roles": self._role_summary(plan)},
        )

        telemetry = build_telemetry_summary(updated_job, plan, outputs, final_validation)
        telemetry_path = self.store.write_telemetry_summary(job_id, telemetry)
        bundle = build_evidence_bundle(updated_job, plan, outputs, final_validation, telemetry=telemetry)
        evidence_path = self.store.write_evidence_bundle(job_id, bundle)

        self.memory.put(
            MemoryEntry(
                namespace="jobs",
                text=f"{job['type']} {job_id} {final_status}",
                metadata={"job_id": job_id, "status": final_status, "plan_id": plan_id},
            )
        )
        self.memory.put(
            MemoryEntry(
                namespace="runs",
                text=f"{plan.get('goal')} -> {final_status}",
                metadata={"job_id": job_id, "status": final_status, "timestamp": utc_now()},
            )
        )
        self.memory.put_semantic_summary(
            text=f"{plan.get('goal')} {final_status} {' '.join(output['step_id'] for output in outputs)}",
            metadata={"job_id": job_id, "plan_id": plan_id, "status": final_status},
        )

        self.store.emit_event(
            "job_finished",
            {
                "job_id": job_id,
                "status": final_status,
                "evidence_path": str(evidence_path),
                "telemetry_path": str(telemetry_path),
            },
        )
        return {
            "job": updated_job,
            "plan": plan,
            "validation": final_validation,
            "evidence_path": str(evidence_path),
            "telemetry_path": str(telemetry_path),
            "telemetry": telemetry,
            "memory_hits": memory_hits,
            "agent_roles": self._role_summary(plan),
        }

    def status(self) -> Dict[str, Any]:
        jobs = self.store.list_jobs()
        summaries = []
        for job in jobs:
            telemetry = self.store.load_telemetry_summary(job["id"])
            summaries.append(
                {
                    "job": job,
                    "telemetry": telemetry.get("metrics") if telemetry else None,
                    "agent_roles": job.get("output", {}).get("agent_roles"),
                }
            )
        return {"jobs": summaries}

    def result(self, job_id: str) -> Dict[str, Any]:
        job = self.store.load_job(job_id)
        if not job:
            raise ValueError("Job not found")

        evidence = None
        evidence_path = self.store.evidence_dir / f"{job_id}.json"
        if evidence_path.exists():
            import json

            evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        telemetry = self.store.load_telemetry_summary(job_id)
        return {"job": job, "evidence": evidence, "telemetry": telemetry, "agent_roles": job.get("output", {}).get("agent_roles")}

    def _get_ready_steps(self, plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        steps = plan.get("steps", [])
        succeeded = {step["id"] for step in steps if step.get("status") == "SUCCESS"}
        ready = []
        for step in steps:
            if step.get("status") != "PENDING":
                continue
            if all(dependency in succeeded for dependency in step.get("depends_on", [])):
                ready.append(step)
        ready.sort(key=lambda step: (int(step.get("priority", 100)), step["id"]))
        return ready

    def _persist_plan(self, plan_id: str, plan: Dict[str, Any]) -> None:
        plan["updated_at"] = utc_now()
        self.store.update_plan(plan_id, **plan)

    def _plan_status(self, plan: Dict[str, Any]) -> str:
        statuses = {step.get("status") for step in plan.get("steps", [])}
        if "FAILED" in statuses:
            return "FAILED"
        if all(status == "SUCCESS" for status in statuses):
            return "SUCCESS"
        return "RUNNING"

    def _mark_blocked_steps(self, plan: Dict[str, Any]) -> None:
        failed_steps = {step["id"] for step in plan.get("steps", []) if step.get("status") == "FAILED"}
        for step in plan.get("steps", []):
            if step.get("status") != "PENDING":
                continue
            if any(dependency in failed_steps for dependency in step.get("depends_on", [])):
                step["status"] = "SKIPPED"
                step["last_error"] = "Dependency failed"

    def _prior_step_checks(self, outputs: List[Dict[str, Any]], validator_step: Dict[str, Any]) -> List[Dict[str, Any]]:
        dependencies = set(validator_step.get("depends_on", []))
        latest_by_step: Dict[str, Dict[str, Any]] = {}
        for output in outputs:
            latest_by_step[output["step_id"]] = output

        checks = []
        for step_id, output in latest_by_step.items():
            if step_id in dependencies:
                checks.append(
                    {
                        "step_id": output["step_id"],
                        "tool": output["tool"],
                        "ok": output.get("validation", {}).get("status") == "PASS",
                    }
                )
        return checks

    def _role_summary(self, plan: Dict[str, Any]) -> Dict[str, List[str]]:
        summary: Dict[str, List[str]] = {}
        for step in plan.get("steps", []):
            role = step.get("agent_role", "executor_agent")
            summary.setdefault(role, []).append(step["id"])
        return summary
