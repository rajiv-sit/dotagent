from __future__ import annotations

from typing import Any, Dict, List


def _duration_ms(started_at: str, ended_at: str) -> int:
    from datetime import datetime

    start = datetime.fromisoformat(started_at)
    end = datetime.fromisoformat(ended_at)
    return max(0, int((end - start).total_seconds() * 1000))


def build_telemetry_summary(
    job: Dict[str, Any],
    plan: Dict[str, Any],
    outputs: List[Dict[str, Any]],
    final_validation: Dict[str, Any],
) -> Dict[str, Any]:
    traces = []
    retries = 0
    failed_steps = []

    for output in outputs:
        trace = {
            "step_id": output["step_id"],
            "tool": output["tool"],
            "attempt": output.get("attempt", 1),
            "ok": output.get("ok", False),
            "validation_status": output.get("validation", {}).get("status"),
            "started_at": output["started_at"],
            "ended_at": output["ended_at"],
            "duration_ms": _duration_ms(output["started_at"], output["ended_at"]),
        }
        traces.append(trace)
        if trace["attempt"] > 1:
            retries += 1
        if trace["validation_status"] == "FAIL":
            failed_steps.append(trace["step_id"])

    metrics = {
        "step_count": len(plan.get("steps", [])),
        "executed_step_count": len(outputs),
        "success_step_count": sum(1 for step in plan.get("steps", []) if step.get("status") == "SUCCESS"),
        "failed_step_count": sum(1 for step in plan.get("steps", []) if step.get("status") == "FAILED"),
        "retry_count": retries,
        "total_duration_ms": sum(trace["duration_ms"] for trace in traces),
    }

    return {
        "job_id": job["id"],
        "plan_id": plan["id"],
        "job_status": job["status"],
        "final_validation_status": final_validation.get("status"),
        "metrics": metrics,
        "failed_steps": failed_steps,
        "traces": traces,
    }
