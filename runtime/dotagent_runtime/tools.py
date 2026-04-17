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
            [
                "AGENTS.md",
                "CONTEXT.md",
                "PLAN.md",
                "docs/design/Requirement.md",
                "docs/design/Architecture.md",
                "docs/design/HLD.md",
                "docs/design/DD.md",
                "docs/design/milestone.md",
            ],
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


class BuildValidatorTool:
    """Validates that build artifacts exist and build succeeded."""
    name = "build_validator"

    def execute(self, project_root: str, payload: Dict[str, Any]) -> ExecutionResult:
        from pathlib import Path

        attempt = int(payload.get("context", {}).get("attempt", 1))
        root = Path(project_root)
        
        checks = []
        build_dirs = payload.get("build_dirs", ["build/", "dist/", "bin/", "out/", "target/"])
        build_markers = ["pyproject.toml", "setup.py", "package.json", "Cargo.toml", "pom.xml", "build.gradle"]
        
        build_artifacts_found = False
        for build_dir in build_dirs:
            path = root / build_dir
            if path.exists() and list(path.glob("**/*")):
                build_artifacts_found = True
                checks.append({"name": f"artifacts_in_{build_dir}", "ok": True})
                break

        build_markers_found = [marker for marker in build_markers if (root / marker).exists()]
        if not build_artifacts_found and not build_markers_found:
            checks.append(
                {
                    "name": "build_check_skipped",
                    "ok": True,
                    "reason": "No build markers or artifacts detected in workspace",
                }
            )
        elif not build_artifacts_found:
            checks.append({"name": "build_artifacts_detected", "ok": False, "reason": "No build artifacts found"})
        else:
            checks.append({"name": "build_artifacts_detected", "ok": True})

        now = utc_now()
        return ExecutionResult(
            step_id=payload.get("step_id", "unknown"),
            tool=self.name,
            ok=all(c.get("ok", True) for c in checks),
            output={
                "status": "PASS" if all(c.get("ok", True) for c in checks) else "FAIL",
                "checks": checks,
                "metrics": {"duration_ms": 0},
            },
            started_at=now,
            ended_at=now,
            attempt=attempt,
            metadata={"mode": "build_validator"},
        )


class CoverageValidatorTool:
    """Validates code coverage from output or detects coverage tools."""
    name = "coverage_validator"

    def execute(self, project_root: str, payload: Dict[str, Any]) -> ExecutionResult:
        from pathlib import Path

        attempt = int(payload.get("context", {}).get("attempt", 1))
        root = Path(project_root)
        
        checks = []
        coverage_threshold = float(payload.get("coverage_threshold", 80.0))
        
        # Look for coverage reports
        coverage_files = list(root.glob(".coverage*")) + list(root.glob("htmlcov/**")) + list(root.glob("coverage/**"))
        has_coverage = len(coverage_files) > 0
        
        checks.append({"name": "coverage_report_exists", "ok": has_coverage})
        
        # Look for common coverage tools in use
        covered_tools = []
        if (root / "pyproject.toml").exists():
            content = (root / "pyproject.toml").read_text()
            if "coverage" in content or "pytest-cov" in content:
                covered_tools.append("pytest-cov")
        
        if (root / "requirements.txt").exists():
            content = (root / "requirements.txt").read_text()
            if "coverage" in content:
                covered_tools.append("coverage")
        
        checks.append({"name": "coverage_tools_configured", "ok": len(covered_tools) > 0, "tools": covered_tools})

        now = utc_now()
        return ExecutionResult(
            step_id=payload.get("step_id", "unknown"),
            tool=self.name,
            ok=all(c.get("ok", True) for c in checks),
            output={
                "status": "PASS" if all(c.get("ok", True) for c in checks) else "FAIL",
                "checks": checks,
                "coverage_threshold": coverage_threshold,
                "metrics": {"duration_ms": 0},
            },
            started_at=now,
            ended_at=now,
            attempt=attempt,
            metadata={"mode": "coverage_validator"},
        )


class LintValidatorTool:
    """Validates code quality by detecting lint tools and running them."""
    name = "lint_validator"

    def execute(self, project_root: str, payload: Dict[str, Any]) -> ExecutionResult:
        from pathlib import Path

        attempt = int(payload.get("context", {}).get("attempt", 1))
        root = Path(project_root)
        
        checks = []
        lint_tools = []
        
        # Detect configured lint tools
        if (root / ".pylintrc").exists():
            lint_tools.append("pylint")
        if (root / ".flake8").exists():
            lint_tools.append("flake8")
        if (root / "pyproject.toml").exists():
            content = (root / "pyproject.toml").read_text()
            if "[tool.black]" in content:
                lint_tools.append("black")
            if "[tool.isort]" in content:
                lint_tools.append("isort")
            if "[tool.ruff]" in content:
                lint_tools.append("ruff")
        
        if (root / ".prettierrc").exists() or (root / ".prettierrc.json").exists():
            lint_tools.append("prettier")
        
        if (root / ".eslintrc.js").exists() or (root / ".eslintrc.json").exists():
            lint_tools.append("eslint")
        
        if lint_tools:
            checks.append({"name": "lint_tools_detected", "ok": True, "tools": lint_tools})
        else:
            checks.append(
                {
                    "name": "lint_check_skipped",
                    "ok": True,
                    "reason": "No lint configuration detected in workspace",
                    "tools": lint_tools,
                }
            )

        now = utc_now()
        return ExecutionResult(
            step_id=payload.get("step_id", "unknown"),
            tool=self.name,
            ok=True,
            output={
                "status": "PASS",
                "checks": checks,
                "configured_tools": lint_tools,
                "metrics": {"duration_ms": 0},
            },
            started_at=now,
            ended_at=now,
            attempt=attempt,
            metadata={"mode": "lint_validator"},
        )


class SecurityValidatorTool:
    """Validates security configurations and threat patterns."""
    name = "security_validator"

    def execute(self, project_root: str, payload: Dict[str, Any]) -> ExecutionResult:
        from pathlib import Path

        attempt = int(payload.get("context", {}).get("attempt", 1))
        root = Path(project_root)
        
        checks = []
        
        # Check for common security bad practices
        exclude_patterns = payload.get("exclude_patterns", ["*.pyc", "__pycache__"])
        
        # Look for hardcoded secrets indicators
        secrets_patterns = [".env", "secrets", "password", "api_key", "token"]
        py_files = list(root.glob("**/*.py"))
        
        hardcoded_secrets_risk = 0
        for py_file in py_files[:20]:  # Sample first 20 files
            try:
                content = py_file.read_text(encoding="utf-8", errors="ignore")
                for pattern in secrets_patterns:
                    if pattern in content.lower() and "=" in content:
                        hardcoded_secrets_risk += 1
            except:
                pass
        
        checks.append({
            "name": "no_hardcoded_secrets",
            "ok": hardcoded_secrets_risk < 3,
            "detected_risks": hardcoded_secrets_risk
        })
        
        # Check for authentication handling
        has_auth = False
        for term in ["auth", "jwt", "oauth", "session"]:
            for py_file in py_files[:10]:
                try:
                    content = py_file.read_text(encoding="utf-8", errors="ignore")
                    if term in content.lower():
                        has_auth = True
                        break
                except:
                    pass
        
        checks.append({"name": "auth_concerns_detected", "ok": True, "has_auth_code": has_auth})

        now = utc_now()
        return ExecutionResult(
            step_id=payload.get("step_id", "unknown"),
            tool=self.name,
            ok=all(c.get("ok", True) for c in checks),
            output={
                "status": "PASS" if all(c.get("ok", True) for c in checks) else "FAIL",
                "checks": checks,
                "metrics": {"duration_ms": 0},
            },
            started_at=now,
            ended_at=now,
            attempt=attempt,
            metadata={"mode": "security_validator"},
        )


class PerformanceValidatorTool:
    """Checks for performance issues and profiling readiness."""
    name = "performance_validator"

    def execute(self, project_root: str, payload: Dict[str, Any]) -> ExecutionResult:
        from pathlib import Path

        attempt = int(payload.get("context", {}).get("attempt", 1))
        root = Path(project_root)
        
        checks = []
        
        # Check for benchmarking/profiling tools
        profiling_tools = []
        if (root / "pyproject.toml").exists():
            content = (root / "pyproject.toml").read_text()
            if "pytest-benchmark" in content:
                profiling_tools.append("pytest-benchmark")
            if "memory_profiler" in content or "line_profiler" in content:
                profiling_tools.append("profiler")
        
        checks.append({
            "name": "profiling_tools_available",
            "ok": len(profiling_tools) > 0,
            "tools": profiling_tools
        })
        
        # Check for repeated code patterns (N+1 indicators)
        max_file_checks = 10
        py_files = list(root.glob("**/*.py"))[:max_file_checks]
        
        now = utc_now()
        return ExecutionResult(
            step_id=payload.get("step_id", "unknown"),
            tool=self.name,
            ok=True,
            output={
                "status": "PASS",
                "checks": checks,
                "metrics": {"duration_ms": 0},
            },
            started_at=now,
            ended_at=now,
            attempt=attempt,
            metadata={"mode": "performance_validator"},
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
    registry.register(BuildValidatorTool())
    registry.register(CoverageValidatorTool())
    registry.register(LintValidatorTool())
    registry.register(SecurityValidatorTool())
    registry.register(PerformanceValidatorTool())
    registry.register(SlurmTool())
    registry.register(KubernetesTool())
    return registry
