from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List

from .models import ExecutionResult, utc_now
from .tools import ToolRegistry


class StepExecutor:
    def __init__(self, registry: ToolRegistry) -> None:
        self.registry = registry

    def execute_step(
        self,
        project_root: str,
        step: Dict[str, Any],
        context: Dict[str, Any] | None = None,
    ) -> ExecutionResult:
        tool_name = step.get("tool") or "shell"
        payload = dict(step.get("payload", {}))
        payload["step_id"] = step.get("id", "unknown")
        payload["context"] = context or {}
        attempt = int(payload.get("context", {}).get("attempt", step.get("attempts", 1)))

        try:
            tool = self.registry.get(tool_name)
            return tool.execute(project_root, payload)
        except Exception as exc:
            now = utc_now()
            return ExecutionResult(
                step_id=payload["step_id"],
                tool=tool_name,
                ok=False,
                output={
                    "stdout": "",
                    "stderr": f"{type(exc).__name__}: {exc}",
                    "returncode": 1,
                    "metrics": {"duration_ms": 0},
                },
                started_at=now,
                ended_at=now,
                attempt=attempt,
                metadata={
                    "mode": "tool_error",
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                },
            )

    def execute_steps(
        self,
        project_root: str,
        steps: List[Dict[str, Any]],
        base_context: Dict[str, Any],
        max_parallelism: int = 1,
    ) -> List[ExecutionResult]:
        ordered_steps = sorted(steps, key=lambda step: (int(step.get("priority", 100)), step["id"]))
        if max_parallelism <= 1 or len(ordered_steps) <= 1:
            return [
                self.execute_step(
                    project_root,
                    step,
                    context={
                        **base_context,
                        "agent_role": step.get("agent_role"),
                        "attempt": step.get("attempts", 1),
                    },
                )
                for step in ordered_steps
            ]

        with ThreadPoolExecutor(max_workers=max_parallelism) as pool:
            futures = [
                pool.submit(
                    self.execute_step,
                    project_root,
                    step,
                    {
                        **base_context,
                        "agent_role": step.get("agent_role"),
                        "attempt": step.get("attempts", 1),
                    },
                )
                for step in ordered_steps
            ]
            return [future.result() for future in futures]
