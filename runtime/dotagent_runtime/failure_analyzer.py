"""
Failure Analysis and Corrective Action Generation.

Transforms raw error output into specific guidance for retry.
This is what makes the feedback loop intelligent, not just blind retry.
"""

import re
from typing import Any, Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class FailureAnalysis:
    """Analysis of why a step failed."""
    root_causes: List[str]
    corrective_actions: List[str]
    retryable: bool
    confidence: float  # 0.0-1.0


class FailureAnalyzer:
    """Parse error output and generate corrective guidance."""

    # Common error patterns
    PATTERNS = {
        "import_error": r"(ModuleNotFoundError|ImportError|No module named)",
        "syntax_error": r"(SyntaxError|IndentationError|unexpected token)",
        "type_error": r"(TypeError|AttributeError|object.*has no attribute)",
        "file_not_found": r"(FileNotFoundError|No such file|cannot find)",
        "test_failed": r"(FAILED|AssertionError|assert.*==|test.*failed)",
        "build_failed": r"(build failed|error during compilation|FAILED.*BUILD)",
        "dependency_missing": r"(not found|not installed|required.*missing)",
        "permission_denied": r"(Permission denied|EACCES|PermissionError)",
        "timeout": r"(timeout|timed out|exceeded|took too long)",
        "memory_error": r"(MemoryError|out of memory|memory exceeded)",
        "network_error": r"(Connection refused|Connection timeout|NetworkError|ECONNREFUSED)",
    }

    def analyze(
        self,
        step: Dict[str, Any],
        result: Dict[str, Any],
        previous_attempt: int = 0
    ) -> FailureAnalysis:
        """
        Analyze failure and generate corrective actions.
        
        Args:
            step: Step definition
            result: Execution result with stdout/stderr
            previous_attempt: Which attempt this is (0=first)
        
        Returns:
            FailureAnalysis with root causes and corrective actions
        """
        stderr = result.get("output", {}).get("stderr", "")
        stdout = result.get("output", {}).get("stdout", "")
        exit_code = result.get("output", {}).get("exit_code", 1)
        output_file = result.get("output", {}).get("output_file", "")

        combined_output = f"{stderr}\n{stdout}"

        # Detect error patterns
        detected_errors = self._detect_errors(combined_output, exit_code)

        # Generate root cause analysis
        root_causes = self._analyze_root_causes(detected_errors, step, combined_output)

        # Generate corrective actions
        corrective_actions = self._generate_corrections(detected_errors, root_causes, previous_attempt)

        # Determine if retryable
        retryable = self._is_retryable(detected_errors, previous_attempt)

        # Calculate confidence
        confidence = min(len(detected_errors) / 5.0, 1.0) if detected_errors else 0.5

        return FailureAnalysis(
            root_causes=root_causes,
            corrective_actions=corrective_actions,
            retryable=retryable,
            confidence=confidence
        )

    def _detect_errors(self, output: str, exit_code: int) -> List[Tuple[str, str]]:
        """Detect error patterns in output."""
        errors = []
        
        for error_type, pattern in self.PATTERNS.items():
            matches = re.findall(pattern, output, re.IGNORECASE)
            if matches:
                errors.append((error_type, matches[0] if isinstance(matches[0], str) else " ".join(matches[0])))

        # Generic exit code failure
        if exit_code != 0 and not errors:
            errors.append(("process_failure", f"Process exited with code {exit_code}"))

        return errors

    def _analyze_root_causes(
        self,
        detected_errors: List[Tuple[str, str]],
        step: Dict[str, Any],
        output: str
    ) -> List[str]:
        """Analyze root causes from detected errors."""
        causes = []

        for error_type, match_text in detected_errors:
            if error_type == "import_error":
                # Extract module name
                match = re.search(r"named '([^']+)'", output)
                module = match.group(1) if match else "unknown module"
                causes.append(f"Missing dependency: {module} not installed")

            elif error_type == "syntax_error":
                # Extract line if available
                match = re.search(r"line (\d+)", output, re.IGNORECASE)
                line = match.group(1) if match else "unknown"
                causes.append(f"Generated code has syntax error at line {line}")

            elif error_type == "type_error":
                causes.append("Type mismatch: incorrect argument types or object attributes")

            elif error_type == "file_not_found":
                # Try to extract filename
                match = re.search(r"('([^']+)'|\"([^\"]+)\")", output)
                if match:
                    filename = match.group(2) or match.group(3)
                    causes.append(f"Required file not found: {filename}")
                else:
                    causes.append("Required file not found")

            elif error_type == "test_failed":
                # Extract test name if available
                match = re.search(r"(test_\w+)", output)
                test = match.group(1) if match else "unit test"
                causes.append(f"Test assertion failed: {test}")

            elif error_type == "build_failed":
                causes.append("Build process failed; check compilation errors")

            elif error_type == "dependency_missing":
                causes.append("Required dependency not found or not installed")

            elif error_type == "permission_denied":
                causes.append("Permission denied; check file/directory permissions")

            elif error_type == "timeout":
                causes.append("Operation timed out; may need optimization or longer timeout")

            elif error_type == "memory_error":
                causes.append("Out of memory; code may have memory leak or excessive allocation")

            elif error_type == "network_error":
                causes.append("Network error; check connectivity or service availability")

            elif error_type == "process_failure":
                causes.append("Process failed; check logs for details")

        return causes

    def _generate_corrections(
        self,
        detected_errors: List[Tuple[str, str]],
        root_causes: List[str],
        attempt: int
    ) -> List[str]:
        """Generate specific corrective actions."""
        actions = []

        for error_type, _ in detected_errors:
            if error_type == "import_error":
                actions.append("Install missing dependency with: pip install <package> OR add to requirements.txt")
                actions.append("OR use a different/built-in module that's available")

            elif error_type == "syntax_error":
                actions.append("Fix syntax errors in generated code")
                actions.append("Check Python version compatibility (f-strings, type hints, etc.)")

            elif error_type == "type_error":
                actions.append("Verify function signatures and argument types")
                actions.append("Use correct object/attribute access patterns")

            elif error_type == "file_not_found":
                actions.append("Create missing file using write_file tool")
                actions.append("OR use correct relative path to existing file")

            elif error_type == "test_failed":
                actions.append("Fix test assertions to match actual behavior")
                actions.append("OR debug function logic to meet test expectations")

            elif error_type == "build_failed":
                actions.append("Check build configuration (setup.py, pyproject.toml, etc.)")
                actions.append("Fix compilation errors or missing dependencies")

            elif error_type == "permission_denied":
                actions.append("Check file permissions; try chmod if running scripts")
                actions.append("Consider using different directory or elevated privileges")

            elif error_type == "timeout":
                if attempt == 0:
                    actions.append("Optimize code to run faster (reduce loops, cache results)")
                else:
                    actions.append("Skip this step or use async/parallel execution")

            elif error_type == "network_error":
                actions.append("Retry with network-aware error handling")
                actions.append("Use offline-first approach or mock network calls")

            elif error_type == "process_failure":
                actions.append("Add detailed error logging to understand failure")
                actions.append("Enable debug mode or verbose output")

        return actions

    def _is_retryable(self, detected_errors: List[Tuple[str, str]], attempt: int) -> bool:
        """Determine if failure is retryable."""
        if attempt >= 2:
            return False  # Give up after 3 attempts

        retryable_errors = {
            "import_error", "file_not_found", "build_failed",
            "test_failed", "network_error", "timeout"
        }

        non_retryable = {"syntax_error", "type_error"}

        error_types = {e[0] for e in detected_errors}

        # If only retryable errors, retry
        if error_types and error_types.issubset(retryable_errors):
            return True

        # If has non-retryable, don't retry
        if error_types & non_retryable:
            return False

        # If no specific errors detected, retry once
        if not detected_errors:
            return attempt < 1

        return False

    def format_corrective_prompt(self, analysis: FailureAnalysis) -> str:
        """Format analysis as prompt section."""
        lines = [
            "## Failure Analysis - Previous Attempt\n",
            f"**Root Causes** ({analysis.confidence:.0%} confidence):\n"
        ]

        for cause in analysis.root_causes:
            lines.append(f"- {cause}")

        if analysis.corrective_actions:
            lines.append("\n**Corrective Actions:**\n")
            for i, action in enumerate(analysis.corrective_actions, 1):
                lines.append(f"{i}. {action}")

        if not analysis.retryable:
            lines.append("\n⚠️ **This failure may not be retryable.** Fundamental issue detected.")
        else:
            lines.append("\n✓ **This failure is retryable.** Apply corrective actions above.")

        return "\n".join(lines)
