#!/usr/bin/env python3
"""
CLI wrapper for FailureAnalyzer - generate intelligent corrective actions.

Usage:
    python -m dotagent_runtime.failure_analyzer_cli --step-json step.json --result-json result.json --attempt 0

Output: JSON analysis with root causes and corrective actions
"""

import json
import sys
from pathlib import Path

from .failure_analyzer import FailureAnalyzer


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Analyze failures and generate corrective actions")
    parser.add_argument("--step-json", required=True, help="Path to step definition JSON")
    parser.add_argument("--result-json", required=True, help="Path to execution result JSON")
    parser.add_argument("--attempt", type=int, default=0, help="Which attempt number (0-based)")
    parser.add_argument("--json-output", action="store_true", help="Output JSON")

    args = parser.parse_args()

    try:
        step_data = json.loads(Path(args.step_json).read_text())
        result_data = json.loads(Path(args.result_json).read_text())

        analyzer = FailureAnalyzer()
        analysis = analyzer.analyze(step_data, result_data, previous_attempt=args.attempt)

        result = {
            "root_causes": analysis.root_causes,
            "corrective_actions": analysis.corrective_actions,
            "retryable": analysis.retryable,
            "confidence": analysis.confidence,
            "formatted_prompt": analyzer.format_corrective_prompt(analysis)
        }

        if args.json_output:
            print(json.dumps(result))
        else:
            print(analyzer.format_corrective_prompt(analysis))

        sys.exit(0 if analysis.retryable else 1)

    except Exception as e:
        error_result = {
            "root_causes": ["Unknown error during analysis"],
            "corrective_actions": [str(e)],
            "retryable": True,  # Assume retryable if analysis fails
            "confidence": 0.0,
            "formatted_prompt": f"Error: {e}"
        }
        if args.json_output:
            print(json.dumps(error_result))
        else:
            print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
