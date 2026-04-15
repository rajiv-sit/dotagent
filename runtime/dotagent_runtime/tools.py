from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, Protocol
import subprocess
from .models import ExecutionResult, utc_now

class Tool(Protocol):
    name: str
    def execute(self, project_root: str, payload: Dict[str, Any]) -> ExecutionResult: ...

class ShellTool:
    name = "shell"

    def execute(self, project_root: str, payload: Dict[str, Any]) -> ExecutionResult:
        command = payload.get("command")
        if not command:
            return ExecutionResult(step_id=payload.get("step_id","unknown"), tool=self.name, ok=True,
                                   output={"stdout": "", "stderr": "", "note": "no command provided; dry-run"},
                                   started_at=utc_now(), ended_at=utc_now())
        started = utc_now()
        proc = subprocess.run(command, cwd=project_root, shell=True, capture_output=True, text=True)
        ended = utc_now()
        return ExecutionResult(step_id=payload.get("step_id","unknown"), tool=self.name, ok=proc.returncode == 0,
                               output={"stdout": proc.stdout, "stderr": proc.stderr, "returncode": proc.returncode},
                               started_at=started, ended_at=ended)

class DocumentReaderTool:
    name = "document_reader"

    def execute(self, project_root: str, payload: Dict[str, Any]) -> ExecutionResult:
        root = Path(project_root)
        files = payload.get("files", ["AGENTS.md", "CONTEXT.md", "PLAN.md", "Requirement.md", "Architecture.md", "HLD.md", "DD.md", "milestone.md"])
        contents = {}
        for rel in files:
            p = root / rel
            contents[rel] = p.read_text(encoding="utf-8")[:8000] if p.exists() else ""
        now = utc_now()
        return ExecutionResult(step_id=payload.get("step_id","unknown"), tool=self.name, ok=True,
                               output={"documents": contents}, started_at=now, ended_at=now)

class PlannerTool:
    name = "planner"

    def execute(self, project_root: str, payload: Dict[str, Any]) -> ExecutionResult:
        now = utc_now()
        return ExecutionResult(step_id=payload.get("step_id","unknown"), tool=self.name, ok=True,
                               output={"note": "planner step is handled by orchestrator"}, started_at=now, ended_at=now)

class ReviewTool:
    name = "review_tool"

    def execute(self, project_root: str, payload: Dict[str, Any]) -> ExecutionResult:
        target = payload.get("target", "current workspace")
        now = utc_now()
        return ExecutionResult(step_id=payload.get("step_id","unknown"), tool=self.name, ok=True,
                               output={"summary": f"Prepared review for {target}", "issues": []}, started_at=now, ended_at=now)

class ValidatorTool:
    name = "validator"

    def execute(self, project_root: str, payload: Dict[str, Any]) -> ExecutionResult:
        now = utc_now()
        return ExecutionResult(step_id=payload.get("step_id","unknown"), tool=self.name, ok=True,
                               output={"status": "PASS", "checks": payload.get("checks", [])}, started_at=now, ended_at=now)

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
    return registry
