"""
Real output validation - checks what the agent actually PRODUCED, not just exit codes.

Replaces weak exit-code validation with:
- Output file verification
- Syntax/format validation
- Test execution
- Requirement matching
"""

import ast
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class ValidationError:
    """Specific validation failure with remediation."""
    category: str  # "syntax", "test", "requirement", "artifact"
    detail: str
    severity: str  # "error" (fail), "warning" (continue)
    fix_suggestion: str


class OutputValidator:
    """Validates what the agent produced, not just whether process exited."""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)

    def validate(
        self,
        step: Dict[str, Any],
        result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Comprehensive output validation.
        
        Returns:
        {
            "status": "PASS" | "FAIL" | "WARNING",
            "errors": [ValidationError],
            "checks": {
                "syntax": bool,
                "tests": bool,
                "requirements": bool,
                "artifacts": bool
            },
            "corrective_actions": [str],
            "retryable": bool
        }
        """
        errors: List[ValidationError] = []
        checks = {
            "syntax": True,
            "tests": True,
            "requirements": True,
            "artifacts": True
        }

        # 1. Check if output files exist and are valid
        if not self._validate_artifacts(result, errors):
            checks["artifacts"] = False

        # 2. Check syntax of generated code
        if not self._validate_syntax(result, errors):
            checks["syntax"] = False

        # 3. Run tests if test suite exists
        if not self._validate_tests(result, errors):
            checks["tests"] = False

        # 4. Check requirements from step acceptance criteria
        if not self._validate_requirements(step, result, errors):
            checks["requirements"] = False

        # Determine status
        hard_failures = [e for e in errors if e.severity == "error"]
        has_failures = len(hard_failures) > 0
        status = "FAIL" if has_failures else ("WARNING" if errors else "PASS")

        # Generate corrective actions
        corrective_actions = self._generate_corrective_actions(errors)
        retryable = any(e.severity == "error" for e in errors)

        return {
            "status": status,
            "errors": [
                {
                    "category": e.category,
                    "detail": e.detail,
                    "severity": e.severity,
                    "fix_suggestion": e.fix_suggestion,
                }
                for e in errors
            ],
            "checks": checks,
            "corrective_actions": corrective_actions,
            "retryable": retryable
        }

    def _validate_artifacts(self, result: Dict[str, Any], errors: List[ValidationError]) -> bool:
        """Check if output files exist and have content."""
        output = result.get("output", {})
        output_file = output.get("output_file")

        if not output_file:
            errors.append(ValidationError(
                category="artifact",
                detail="No output file produced",
                severity="error",
                fix_suggestion="Check that agent produced output; verify output_file path is set"
            ))
            return False

        if not Path(output_file).exists():
            errors.append(ValidationError(
                category="artifact",
                detail=f"Output file does not exist: {output_file}",
                severity="error",
                fix_suggestion=f"Verify output was written to {output_file}; check file permissions"
            ))
            return False

        # Check file has content
        size = Path(output_file).stat().st_size
        if size == 0:
            errors.append(ValidationError(
                category="artifact",
                detail=f"Output file is empty: {output_file}",
                severity="error",
                fix_suggestion="Agent produced no output; check task definition and agent execution"
            ))
            return False

        return True

    def _validate_syntax(self, result: Dict[str, Any], errors: List[ValidationError]) -> bool:
        """Check syntax of generated code files."""
        output_file = result.get("output", {}).get("output_file")
        if not output_file or not Path(output_file).exists():
            return True  # Can't validate if no output

        try:
            content = Path(output_file).read_text(encoding="utf-8")
        except Exception as e:
            errors.append(ValidationError(
                category="syntax",
                detail=f"Cannot read output file: {e}",
                severity="warning",
                fix_suggestion="Check file encoding and permissions"
            ))
            return False

        # Check for Python syntax errors in output
        if "```python" in content or content.count("def ") > 0:
            try:
                # Extract code blocks if markdown
                code = content
                if "```python" in content:
                    for block in content.split("```python"):
                        if "```" in block:
                            code = block.split("```")[0]
                            try:
                                ast.parse(code)
                            except SyntaxError as e:
                                errors.append(ValidationError(
                                    category="syntax",
                                    detail=f"Python syntax error in generated code: {e.msg} at line {e.lineno}",
                                    severity="error",
                                    fix_suggestion=f"Fix syntax error: {e.msg}. Line: {e.text}"
                                ))
                                return False
            except Exception:
                pass  # Not python code, skip

        # Check for JSON if output looks like JSON
        if output_file.endswith(".json"):
            try:
                json.loads(content)
            except json.JSONDecodeError as e:
                errors.append(ValidationError(
                    category="syntax",
                    detail=f"Invalid JSON in output: {e}",
                    severity="error",
                    fix_suggestion="Verify JSON format; use JSON validator to identify issues"
                ))
                return False

        return True

    def _validate_tests(self, result: Dict[str, Any], errors: List[ValidationError]) -> bool:
        """Run tests if test suite exists in project."""
        # Check for pytest
        if (self.project_root / "tests").exists() or (self.project_root / "test").exists():
            try:
                proc = subprocess.run(
                    ["python", "-m", "pytest", "-q"],
                    cwd=str(self.project_root),
                    capture_output=True,
                    timeout=30
                )
                if proc.returncode != 0:
                    stderr = proc.stderr.decode("utf-8", errors="ignore")
                    stdout = proc.stdout.decode("utf-8", errors="ignore")
                    errors.append(ValidationError(
                        category="test",
                        detail=f"Tests failed. Output: {stdout[:200]}",
                        severity="error",
                        fix_suggestion=f"Fix test failures: {stderr[:300]}"
                    ))
                    return False
            except subprocess.TimeoutExpired:
                errors.append(ValidationError(
                    category="test",
                    detail="Tests timed out (>30s)",
                    severity="warning",
                    fix_suggestion="Tests taking too long; optimize or increase timeout"
                ))
            except Exception as e:
                errors.append(ValidationError(
                    category="test",
                    detail=f"Could not run tests: {e}",
                    severity="warning",
                    fix_suggestion="Check pytest installation and test directory structure"
                ))
                return False

        return True

    def _validate_requirements(
        self,
        step: Dict[str, Any],
        result: Dict[str, Any],
        errors: List[ValidationError]
    ) -> bool:
        """Check acceptance criteria from step definition."""
        acceptance = step.get("acceptance", {}) or {}
        output = result.get("output", {}) or {}

        # Check explicit requirements
        for key, expected in acceptance.items():
            if key.startswith("_"):
                continue

            actual = output.get(key)
            if actual != expected and key not in ["returncode", "status_equals"]:
                errors.append(ValidationError(
                    category="requirement",
                    detail=f"Requirement '{key}' not met. Expected: {expected}, Got: {actual}",
                    severity="error",
                    fix_suggestion=f"Ensure agent produces {key}={expected}"
                ))
                return False

        # Check returncode if specified
        if "returncode" in acceptance:
            actual = output.get("returncode", 1)
            if actual != acceptance["returncode"]:
                stderr = output.get("stderr", "")[:200]
                stdout = output.get("stdout", "")[:200]
                errors.append(ValidationError(
                    category="requirement",
                    detail=f"Process exit code incorrect. Expected: {acceptance['returncode']}, Got: {actual}",
                    severity="error",
                    fix_suggestion=f"Check execution. stderr: {stderr}; stdout: {stdout}"
                ))
                return False

        return True

    def _generate_corrective_actions(self, errors: List[ValidationError]) -> List[str]:
        """Generate specific fix suggestions from validation errors."""
        actions = []
        for error in errors:
            if error.severity == "error":
                actions.append(f"[{error.category.upper()}] {error.fix_suggestion}")
        return actions


def create_corrective_prompt(validation_result: Dict[str, Any]) -> str:
    """Generate corrective prompt from validation failures."""
    if validation_result["status"] == "PASS":
        return ""

    lines = [
        "## Validation Feedback - Previous Attempt Issues\n",
        f"Status: {validation_result['status']}\n"
    ]

    for check, result in validation_result["checks"].items():
        if not result:
            lines.append(f"❌ {check} validation failed")

    if validation_result["corrective_actions"]:
        lines.append("\n### Specific Issues:")
        for action in validation_result["corrective_actions"]:
            lines.append(f"- {action}")

    return "\n".join(lines)
