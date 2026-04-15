from __future__ import annotations
from typing import Dict, Any, List
from .models import ValidationResult

class Validator:
    def validate_job_outputs(self, outputs: List[Dict[str, Any]]) -> ValidationResult:
        checks = []
        corrective = []

        for item in outputs:
            ok = bool(item.get("ok", False))
            checks.append({
                "step_id": item.get("step_id"),
                "tool": item.get("tool"),
                "ok": ok
            })
            if not ok:
                corrective.append(f"Re-run or replan step {item.get('step_id')} using tool {item.get('tool')}")

        status = "PASS" if all(c["ok"] for c in checks) else "FAIL"
        summary = "All executed steps passed." if status == "PASS" else "One or more executed steps failed."
        return ValidationResult(status=status, summary=summary, checks=checks, corrective_actions=corrective)
