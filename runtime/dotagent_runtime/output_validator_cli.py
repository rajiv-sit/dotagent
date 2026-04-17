#!/usr/bin/env python3
"""
CLI wrapper for OutputValidator - real output validation.

Usage:
    python -m dotagent_runtime.output_validator_cli --step-json step.json --result-json result.json

Output: JSON validation result
"""

import json
import sys
from pathlib import Path

from .output_validator import OutputValidator


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Validate execution output (not just exit code)")
    parser.add_argument("--step-json", required=True, help="Path to step definition JSON")
    parser.add_argument("--result-json", required=True, help="Path to execution result JSON")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--json-output", action="store_true", help="Output JSON")

    args = parser.parse_args()

    try:
        step_data = json.loads(Path(args.step_json).read_text())
        result_data = json.loads(Path(args.result_json).read_text())

        validator = OutputValidator(project_root=args.project_root)
        validation = validator.validate(step_data, result_data)

        if args.json_output:
            print(json.dumps(validation))
        else:
            print(f"Status: {validation['status']}")
            for category, result in validation['checks'].items():
                status = "✓" if result else "✗"
                print(f"  {status} {category}")
            if validation['corrective_actions']:
                print("Suggested fixes:")
                for action in validation['corrective_actions']:
                    print(f"  - {action}")

        sys.exit(0 if validation['status'] == 'PASS' else 1)

    except Exception as e:
        error_result = {
            "status": "ERROR",
            "errors": [{"detail": str(e), "category": "system", "severity": "error"}],
            "checks": {},
            "corrective_actions": [str(e)],
            "retryable": False
        }
        if args.json_output:
            print(json.dumps(error_result))
        else:
            print(f"Error: {e}")
        sys.exit(2)


if __name__ == "__main__":
    main()
