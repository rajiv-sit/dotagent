from __future__ import annotations

from typing import Any, Dict, List


class PolicyEngine:
    def evaluate(self, step: Dict[str, Any], result: Dict[str, Any]) -> List[Dict[str, Any]]:
        output = result.get("output", {}) or {}
        policies = list(step.get("acceptance", {}).get("policies", []) or [])
        checks: List[Dict[str, Any]] = []

        for policy in policies:
            kind = policy.get("kind")
            name = policy.get("name", kind or "policy")
            if kind == "max_duration_ms":
                actual = output.get("metrics", {}).get("duration_ms", result.get("duration_ms"))
                ok = actual is not None and actual <= policy.get("value")
                checks.append({"name": name, "kind": kind, "actual": actual, "expected_max": policy.get("value"), "ok": ok})
            elif kind == "metric_max":
                metric_name = policy.get("metric")
                actual = output.get("metrics", {}).get(metric_name)
                ok = actual is not None and actual <= policy.get("value")
                checks.append({"name": name, "kind": kind, "metric": metric_name, "actual": actual, "expected_max": policy.get("value"), "ok": ok})
            elif kind == "metric_min":
                metric_name = policy.get("metric")
                actual = output.get("metrics", {}).get(metric_name)
                ok = actual is not None and actual >= policy.get("value")
                checks.append({"name": name, "kind": kind, "metric": metric_name, "actual": actual, "expected_min": policy.get("value"), "ok": ok})
            elif kind == "contains_text":
                actual_text = output.get("stdout", "")
                expected = str(policy.get("value", ""))
                ok = expected in actual_text
                checks.append({"name": name, "kind": kind, "expected": expected, "ok": ok})
            elif kind == "file_exists":
                files = set(output.get("files_created", []) or [])
                expected = str(policy.get("value", ""))
                ok = expected in files
                checks.append({"name": name, "kind": kind, "expected": expected, "ok": ok})

        return checks
