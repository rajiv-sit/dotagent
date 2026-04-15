from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Protocol
import subprocess

from .models import ExecutionResult, utc_now


class Tool(Protocol):
    name: str

    def execute(self, project_root: str, payload: Dict[str, Any]) -> ExecutionResult: ...


def _elapsed_ms(started_at: str, ended_at: str) -> int:
    from datetime import datetime

    start = datetime.fromisoformat(started_at)
    end = datetime.fromisoformat(ended_at)
    return max(0, int((end - start).total_seconds() * 1000))


class ShellTool:
    name = "shell"

    def execute(self, project_root: str, payload: Dict[str, Any]) -> ExecutionResult:
        command = payload.get("command")
        attempt = int(payload.get("context", {}).get("attempt", 1))
        if not command:
            now = utc_now()
            return ExecutionResult(
                step_id=payload.get("step_id", "unknown"),
                tool=self.name,
                ok=True,
                output={
                    "stdout": "",
                    "stderr": "",
                    "note": "no command provided; dry-run",
                    "returncode": 0,
                    "metrics": {"duration_ms": 0},
                },
                started_at=now,
                ended_at=now,
                attempt=attempt,
                metadata={"mode": "dry-run"},
            )

        started = utc_now()
        proc = subprocess.run(command, cwd=project_root, shell=True, capture_output=True, text=True)
        ended = utc_now()
        return ExecutionResult(
            step_id=payload.get("step_id", "unknown"),
            tool=self.name,
            ok=proc.returncode == 0,
            output={
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "returncode": proc.returncode,
                "metrics": {"duration_ms": _elapsed_ms(started, ended)},
            },
            started_at=started,
            ended_at=ended,
            attempt=attempt,
            metadata={"mode": "shell"},
        )


class DocumentReaderTool:
    name = "document_reader"

    def execute(self, project_root: str, payload: Dict[str, Any]) -> ExecutionResult:
        root = Path(project_root)
        files = payload.get(
            "files",
            ["AGENTS.md", "CONTEXT.md", "PLAN.md", "Requirement.md", "Architecture.md", "HLD.md", "DD.md", "milestone.md"],
        )
        contents = {}
        missing = []
        for rel in files:
            path = root / rel
            if path.exists():
                contents[rel] = path.read_text(encoding="utf-8")[:8000]
            else:
                contents[rel] = ""
                missing.append(rel)
        now = utc_now()
        return ExecutionResult(
            step_id=payload.get("step_id", "unknown"),
            tool=self.name,
            ok=True,
            output={"documents": contents, "missing": missing, "metrics": {"duration_ms": 0}},
            started_at=now,
            ended_at=now,
            attempt=int(payload.get("context", {}).get("attempt", 1)),
            metadata={"mode": "reader"},
        )


class PlannerTool:
    name = "planner"

    def execute(self, project_root: str, payload: Dict[str, Any]) -> ExecutionResult:
        now = utc_now()
        return ExecutionResult(
            step_id=payload.get("step_id", "unknown"),
            tool=self.name,
            ok=True,
            output={"note": "planner step is handled by orchestrator", "metrics": {"duration_ms": 0}},
            started_at=now,
            ended_at=now,
            attempt=int(payload.get("context", {}).get("attempt", 1)),
            metadata={"mode": "planner"},
        )


class ReviewTool:
    name = "review_tool"

    def execute(self, project_root: str, payload: Dict[str, Any]) -> ExecutionResult:
        target = payload.get("target") or payload.get("context", {}).get("goal") or "current workspace"
        memory_hits = payload.get("context", {}).get("memory_hits", {})
        now = utc_now()
        return ExecutionResult(
            step_id=payload.get("step_id", "unknown"),
            tool=self.name,
            ok=True,
            output={
                "summary": f"Prepared review for {target}",
                "issues": [],
                "memory_hits": sum(len(entries) for entries in memory_hits.values()),
                "metrics": {"duration_ms": 0},
            },
            started_at=now,
            ended_at=now,
            attempt=int(payload.get("context", {}).get("attempt", 1)),
            metadata={"mode": "review"},
        )


class ValidatorTool:
    name = "validator"

    def execute(self, project_root: str, payload: Dict[str, Any]) -> ExecutionResult:
        now = utc_now()
        checks = payload.get("checks", [])
        status = "PASS" if all(check.get("ok", True) for check in checks) else "FAIL"
        return ExecutionResult(
            step_id=payload.get("step_id", "unknown"),
            tool=self.name,
            ok=status == "PASS",
            output={"status": status, "checks": checks, "metrics": {"duration_ms": 0}},
            started_at=now,
            ended_at=now,
            attempt=int(payload.get("context", {}).get("attempt", 1)),
            metadata={"mode": "validator"},
        )


class TestRunnerTool:
    name = "test_runner"

    def execute(self, project_root: str, payload: Dict[str, Any]) -> ExecutionResult:
        command = payload.get("command")
        attempt = int(payload.get("context", {}).get("attempt", 1))
        if not command:
            now = utc_now()
            return ExecutionResult(
                step_id=payload.get("step_id", "unknown"),
                tool=self.name,
                ok=True,
                output={"status": "PASS", "tests_run": 0, "metrics": {"duration_ms": 0}},
                started_at=now,
                ended_at=now,
                attempt=attempt,
                metadata={"mode": "dry-run"},
            )

        started = utc_now()
        proc = subprocess.run(command, cwd=project_root, shell=True, capture_output=True, text=True)
        ended = utc_now()
        return ExecutionResult(
            step_id=payload.get("step_id", "unknown"),
            tool=self.name,
            ok=proc.returncode == 0,
            output={
                "status": "PASS" if proc.returncode == 0 else "FAIL",
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "returncode": proc.returncode,
                "tests_run": 1,
                "metrics": {"duration_ms": _elapsed_ms(started, ended)},
            },
            started_at=started,
            ended_at=ended,
            attempt=attempt,
            metadata={"mode": "test_runner"},
        )


class SlurmTool:
    name = "slurm_job"

    def execute(self, project_root: str, payload: Dict[str, Any]) -> ExecutionResult:
        command = payload.get("command", "echo noop")
        dry_run = bool(payload.get("dry_run", True))
        now = utc_now()
        submission = f"sbatch --wrap \"{command}\""
        return ExecutionResult(
            step_id=payload.get("step_id", "unknown"),
            tool=self.name,
            ok=True,
            output={
                "status": "SUBMITTED" if not dry_run else "PLANNED",
                "submission_command": submission,
                "scheduler": "slurm",
                "metrics": {"duration_ms": 0},
            },
            started_at=now,
            ended_at=now,
            attempt=int(payload.get("context", {}).get("attempt", 1)),
            metadata={"mode": "external", "target": "slurm"},
        )


class KubernetesTool:
    name = "kubernetes_job"

    def execute(self, project_root: str, payload: Dict[str, Any]) -> ExecutionResult:
        command = payload.get("command", "echo noop")
        namespace = payload.get("namespace", "default")
        job_name = payload.get("job_name", payload.get("step_id", "job"))
        now = utc_now()
        manifest = {
            "apiVersion": "batch/v1",
            "kind": "Job",
            "metadata": {"name": job_name, "namespace": namespace},
            "spec": {"template": {"spec": {"restartPolicy": "Never", "containers": [{"name": job_name, "image": "python:3.12", "command": ["sh", "-lc", command]}]}}},
        }
        return ExecutionResult(
            step_id=payload.get("step_id", "unknown"),
            tool=self.name,
            ok=True,
            output={
                "status": "PLANNED",
                "scheduler": "kubernetes",
                "manifest": manifest,
                "metrics": {"duration_ms": 0},
            },
            started_at=now,
            ended_at=now,
            attempt=int(payload.get("context", {}).get("attempt", 1)),
            metadata={"mode": "external", "target": "kubernetes"},
        )


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: Dict[str, Any] = {}

    def register(self, tool: Any) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Any:
        if name not in self._tools:
            raise KeyError(f"Tool not registered: {name}")
        return self._tools[name]


def default_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(ShellTool())
    registry.register(DocumentReaderTool())
    registry.register(PlannerTool())
    registry.register(ReviewTool())
    registry.register(ValidatorTool())
    registry.register(TestRunnerTool())
    registry.register(SlurmTool())
    registry.register(KubernetesTool())
    return registry
