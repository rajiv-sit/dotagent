#!/usr/bin/env python3
"""
CLI wrapper for Validator - evaluates step execution results.

Usage:
    python -m dotagent_runtime.validator_cli --step-json step.json --result-json result.json

Output: JSON validation result
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict

from .validator import Validator
from .models import ExecutionResult


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Validate step execution result")
    parser.add_argument("--step-json", required=True, help="Path to step definition JSON")
    parser.add_argument("--result-json", required=True, help="Path to execution result JSON")
    parser.add_argument("--project-root", default=".")

    args = parser.parse_args()

    try:
        # Load step and result
        step_data = json.loads(Path(args.step_json).read_text())
        result_data = json.loads(Path(args.result_json).read_text())

        validator = Validator()
        
        # Convert result dict to ExecutionResult if needed
        if isinstance(result_data, dict):
            result = ExecutionResult(
                step_id=result_data.get("step_id"),
                tool=result_data.get("tool"),
                ok=result_data.get("ok", False),
                output=result_data.get("output", {}),
                started_at=result_data.get("started_at", ""),
                ended_at=result_data.get("ended_at", ""),
                attempt=result_data.get("attempt", 1),
                metadata=result_data.get("metadata", {}),
            )
        else:
            result = result_data

        validation = validator.validate_step_result(step_data, result_data)

        output = {
            "status": validation.status,
            "summary": validation.summary,
            "checks": validation.checks,
            "corrective_actions": validation.corrective_actions,
            "retryable": validation.retryable,
        }
        
        print(json.dumps(output, indent=2))
        return 0 if validation.status == "PASS" else 1

    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
