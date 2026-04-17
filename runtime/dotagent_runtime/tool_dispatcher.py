"""
Internal tool dispatch - handles execution without delegating to CLI for everything.

This gives the system actual agency over execution, not just orchestration.
Falls back to agent CLI only for reasoning/planning tasks.
"""

import subprocess
import shutil
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ToolResult:
    """Result from tool execution."""
    success: bool
    stdout: str
    stderr: str
    exit_code: int
    output: Optional[str] = None  # File path for file operations


class InternalToolDispatcher:
    """Handles common tools directly; delegates complex reasoning to CLI agent."""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)

    def can_handle(self, tool: str) -> bool:
        """Check if this tool can be handled internally."""
        internal_tools = {
            "write_file", "read_file", "run_tests", "run_linter",
            "build", "copy_file", "delete_file", "list_files",
            "run_command"
        }
        return tool in internal_tools

    def dispatch(self, tool: str, payload: Dict[str, Any]) -> ToolResult:
        """
        Execute tool internally.
        
        Returns ToolResult with execution details.
        """
        if tool == "write_file":
            return self._write_file(payload)
        elif tool == "read_file":
            return self._read_file(payload)
        elif tool == "run_tests":
            return self._run_tests(payload)
        elif tool == "run_linter":
            return self._run_linter(payload)
        elif tool == "build":
            return self._build(payload)
        elif tool == "copy_file":
            return self._copy_file(payload)
        elif tool == "delete_file":
            return self._delete_file(payload)
        elif tool == "list_files":
            return self._list_files(payload)
        elif tool == "run_command":
            return self._run_command(payload)
        else:
            return ToolResult(
                success=False,
                stdout="",
                stderr=f"Unknown tool: {tool}",
                exit_code=1
            )

    def _write_file(self, payload: Dict[str, Any]) -> ToolResult:
        """Write content to file."""
        try:
            path = Path(payload.get("path", ""))
            content = payload.get("content", "")
            
            if not path:
                return ToolResult(False, "", "No path specified", 1)

            # Security: ensure path is within project root
            full_path = (self.project_root / path).resolve()
            if not str(full_path).startswith(str(self.project_root.resolve())):
                return ToolResult(
                    False, "", 
                    f"Path {path} is outside project root (security violation)", 
                    1
                )

            # Create parent directories
            full_path.parent.mkdir(parents=True, exist_ok=True)

            # Write file
            full_path.write_text(content, encoding="utf-8")
            
            return ToolResult(
                success=True,
                stdout=f"Wrote {len(content)} bytes to {path}",
                stderr="",
                exit_code=0,
                output=str(full_path)
            )
        except Exception as e:
            return ToolResult(False, "", f"Write failed: {e}", 1)

    def _read_file(self, payload: Dict[str, Any]) -> ToolResult:
        """Read file content."""
        try:
            path = Path(payload.get("path", ""))
            if not path:
                return ToolResult(False, "", "No path specified", 1)

            full_path = (self.project_root / path).resolve()
            if not str(full_path).startswith(str(self.project_root.resolve())):
                return ToolResult(
                    False, "", 
                    f"Path {path} is outside project root", 
                    1
                )

            if not full_path.exists():
                return ToolResult(False, "", f"File not found: {path}", 1)

            content = full_path.read_text(encoding="utf-8")
            return ToolResult(
                success=True,
                stdout=content,
                stderr="",
                exit_code=0,
                output=str(full_path)
            )
        except Exception as e:
            return ToolResult(False, "", f"Read failed: {e}", 1)

    def _run_tests(self, payload: Dict[str, Any]) -> ToolResult:
        """Run test suite."""
        try:
            test_dir = payload.get("test_dir", "tests")
            test_command = [
                "python", "-m", "pytest",
                test_dir,
                "-v",
                "--tb=short",
                f"--maxfail={payload.get('max_fail', 1)}"
            ]

            proc = subprocess.run(
                test_command,
                cwd=str(self.project_root),
                capture_output=True,
                timeout=payload.get("timeout", 60)
            )

            return ToolResult(
                success=proc.returncode == 0,
                stdout=proc.stdout.decode("utf-8", errors="ignore"),
                stderr=proc.stderr.decode("utf-8", errors="ignore"),
                exit_code=proc.returncode
            )
        except subprocess.TimeoutExpired:
            return ToolResult(False, "", "Tests timed out", 124)
        except Exception as e:
            return ToolResult(False, "", f"Test run failed: {e}", 1)

    def _run_linter(self, payload: Dict[str, Any]) -> ToolResult:
        """Run code linter (flake8, pylint, ruff, etc.)."""
        try:
            linter = payload.get("linter", "flake8")
            target = payload.get("target", ".")

            if linter == "flake8":
                cmd = ["python", "-m", "flake8", target]
            elif linter == "pylint":
                cmd = ["python", "-m", "pylint", target, "--exit-zero"]
            elif linter == "ruff":
                cmd = ["ruff", "check", target]
            elif linter == "black":
                cmd = ["black", "--check", target]
            else:
                return ToolResult(False, "", f"Unknown linter: {linter}", 1)

            proc = subprocess.run(
                cmd,
                cwd=str(self.project_root),
                capture_output=True,
                timeout=30
            )

            return ToolResult(
                success=proc.returncode == 0,
                stdout=proc.stdout.decode("utf-8", errors="ignore"),
                stderr=proc.stderr.decode("utf-8", errors="ignore"),
                exit_code=proc.returncode
            )
        except Exception as e:
            return ToolResult(False, "", f"Linter failed: {e}", 1)

    def _build(self, payload: Dict[str, Any]) -> ToolResult:
        """Build project (python setup, npm build, etc.)."""
        try:
            build_type = payload.get("type", "python")
            
            if build_type == "python":
                cmd = ["python", "-m", "pip", "install", "-e", "."]
            elif build_type == "npm":
                cmd = ["npm", "install"]
            elif build_type == "npm-build":
                cmd = ["npm", "run", "build"]
            elif build_type == "cargo":
                cmd = ["cargo", "build", "--release"]
            elif build_type == "make":
                cmd = ["make", payload.get("target", "all")]
            else:
                return ToolResult(False, "", f"Unknown build type: {build_type}", 1)

            proc = subprocess.run(
                cmd,
                cwd=str(self.project_root),
                capture_output=True,
                timeout=payload.get("timeout", 120)
            )

            return ToolResult(
                success=proc.returncode == 0,
                stdout=proc.stdout.decode("utf-8", errors="ignore"),
                stderr=proc.stderr.decode("utf-8", errors="ignore"),
                exit_code=proc.returncode
            )
        except subprocess.TimeoutExpired:
            return ToolResult(False, "", "Build timed out", 124)
        except Exception as e:
            return ToolResult(False, "", f"Build failed: {e}", 1)

    def _copy_file(self, payload: Dict[str, Any]) -> ToolResult:
        """Copy file."""
        try:
            src = Path(payload.get("src", ""))
            dst = Path(payload.get("dst", ""))

            src_full = (self.project_root / src).resolve()
            dst_full = (self.project_root / dst).resolve()

            # Security checks
            if not str(src_full).startswith(str(self.project_root.resolve())):
                return ToolResult(False, "", "Source outside project", 1)
            if not str(dst_full).startswith(str(self.project_root.resolve())):
                return ToolResult(False, "", "Destination outside project", 1)

            if not src_full.exists():
                return ToolResult(False, "", f"Source not found: {src}", 1)

            dst_full.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_full, dst_full)

            return ToolResult(
                success=True,
                stdout=f"Copied {src} to {dst}",
                stderr="",
                exit_code=0
            )
        except Exception as e:
            return ToolResult(False, "", f"Copy failed: {e}", 1)

    def _delete_file(self, payload: Dict[str, Any]) -> ToolResult:
        """Delete file."""
        try:
            path = Path(payload.get("path", ""))
            full_path = (self.project_root / path).resolve()

            if not str(full_path).startswith(str(self.project_root.resolve())):
                return ToolResult(False, "", "Path outside project", 1)

            if not full_path.exists():
                return ToolResult(False, "", f"File not found: {path}", 1)

            full_path.unlink()
            return ToolResult(
                success=True,
                stdout=f"Deleted {path}",
                stderr="",
                exit_code=0
            )
        except Exception as e:
            return ToolResult(False, "", f"Delete failed: {e}", 1)

    def _list_files(self, payload: Dict[str, Any]) -> ToolResult:
        """List files in directory."""
        try:
            path = Path(payload.get("path", "."))
            pattern = payload.get("pattern", "*")
            recursive = payload.get("recursive", False)

            full_path = (self.project_root / path).resolve()
            if not str(full_path).startswith(str(self.project_root.resolve())):
                return ToolResult(False, "", "Path outside project", 1)

            if recursive:
                files = list(full_path.rglob(pattern))
            else:
                files = list(full_path.glob(pattern))

            file_list = "\n".join(str(f.relative_to(self.project_root)) for f in files)
            return ToolResult(
                success=True,
                stdout=file_list,
                stderr="",
                exit_code=0
            )
        except Exception as e:
            return ToolResult(False, "", f"List failed: {e}", 1)

    def _run_command(self, payload: Dict[str, Any]) -> ToolResult:
        """Run arbitrary shell command."""
        try:
            command = payload.get("command", "")
            if not command:
                return ToolResult(False, "", "No command specified", 1)

            # Whitelist safe commands; reject dangerous ones
            dangerous_patterns = ["rm -rf /", "sudo", "rm -rf *"]
            if any(p in command for p in dangerous_patterns):
                return ToolResult(False, "", "Command is potentially dangerous", 1)

            proc = subprocess.run(
                command,
                shell=True,
                cwd=str(self.project_root),
                capture_output=True,
                timeout=payload.get("timeout", 60)
            )

            return ToolResult(
                success=proc.returncode == 0,
                stdout=proc.stdout.decode("utf-8", errors="ignore"),
                stderr=proc.stderr.decode("utf-8", errors="ignore"),
                exit_code=proc.returncode
            )
        except subprocess.TimeoutExpired:
            return ToolResult(False, "", "Command timed out", 124)
        except Exception as e:
            return ToolResult(False, "", f"Command failed: {e}", 1)
