from __future__ import annotations

from typing import Any, Dict, List

from .models import ValidationResult
from .policy import PolicyEngine


class Validator:
    def __init__(self) -> None:
        self.policy_engine = PolicyEngine()

    def validate_step_result(
        self,
        step: Dict[str, Any],
        result: Dict[str, Any],
    ) -> ValidationResult:
        checks: List[Dict[str, Any]] = []
        corrective: List[str] = []
        acceptance = step.get("acceptance", {}) or {}
        output = result.get("output", {}) or {}

        execution_ok = bool(result.get("ok", False))
        checks.append({"name": "execution_ok", "ok": execution_ok})
        if not execution_ok:
            corrective.append(f"Investigate failing step {step.get('id')} using tool {result.get('tool')}")

        if "returncode" in acceptance:
            actual = output.get("returncode")
            ok = actual == acceptance["returncode"]
            checks.append({"name": "returncode", "expected": acceptance["returncode"], "actual": actual, "ok": ok})
            if not ok:
                corrective.append(
                    f"Expected return code {acceptance['returncode']} for step {step.get('id')}, got {actual}"
                )

        if "contains_text" in acceptance:
            stdout = output.get("stdout", "")
            expected = str(acceptance["contains_text"])
            ok = expected in stdout
            checks.append({"name": "contains_text", "expected": expected, "ok": ok})
            if not ok:
                corrective.append(f"Expected stdout for step {step.get('id')} to contain '{expected}'")

        if "not_in_stderr" in acceptance:
            stderr = output.get("stderr", "")
            forbidden = str(acceptance["not_in_stderr"])
            ok = forbidden not in stderr
            checks.append({"name": "not_in_stderr", "expected": forbidden, "ok": ok})
            if not ok:
                corrective.append(f"stderr for step {step.get('id')} contains forbidden text '{forbidden}'")

        if "documents_required" in acceptance:
            documents = output.get("documents", {})
            missing = [doc for doc in acceptance["documents_required"] if not documents.get(doc)]
            ok = not missing
            checks.append({"name": "documents_required", "missing": missing, "ok": ok})
            if not ok:
                corrective.append(f"Missing required documents for discovery: {', '.join(missing)}")

        if acceptance.get("summary_required"):
            summary = str(output.get("summary", "")).strip()
            ok = bool(summary)
            checks.append({"name": "summary_required", "ok": ok})
            if not ok:
                corrective.append(f"Review step {step.get('id')} did not produce a summary")

        if "status_equals" in acceptance:
            status = output.get("status")
            ok = status == acceptance["status_equals"]
            checks.append({"name": "status_equals", "expected": acceptance["status_equals"], "actual": status, "ok": ok})
            if not ok:
                corrective.append(f"Expected validator status {acceptance['status_equals']} for step {step.get('id')}")

        metrics = output.get("metrics", {}) or {}
        for name, threshold in (acceptance.get("metrics_max", {}) or {}).items():
            actual = metrics.get(name)
            ok = actual is not None and actual <= threshold
            checks.append({"name": f"metric_max:{name}", "expected_max": threshold, "actual": actual, "ok": ok})
            if not ok:
                corrective.append(f"Metric {name} exceeded max threshold {threshold}")

        for name, threshold in (acceptance.get("metrics_min", {}) or {}).items():
            actual = metrics.get(name)
            ok = actual is not None and actual >= threshold
            checks.append({"name": f"metric_min:{name}", "expected_min": threshold, "actual": actual, "ok": ok})
            if not ok:
                corrective.append(f"Metric {name} fell below min threshold {threshold}")

        for policy_check in self.policy_engine.evaluate(step, result):
            checks.append(policy_check)
            if not policy_check["ok"]:
                corrective.append(f"Policy {policy_check['name']} failed for step {step.get('id')}")

        status = "PASS" if all(c["ok"] for c in checks) else "FAIL"
        retryable = status == "FAIL" and int(step.get("attempts", 0)) < int(step.get("max_attempts", 1))
        summary = "All checks passed." if status == "PASS" else "One or more checks failed."
        return ValidationResult(
            status=status,
            summary=summary,
            checks=checks,
            corrective_actions=corrective,
            retryable=retryable,
        )
