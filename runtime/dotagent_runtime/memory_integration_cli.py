#!/usr/bin/env python3
"""
CLI wrapper for Memory Integration - retrieve and store lessons.

Usage:
    # Retrieve lessons before planning
    python -m dotagent_runtime.memory_integration_cli --goal "Add authentication" --mode retrieve

    # Store failure lesson after failure   
    python -m dotagent_runtime.memory_integration_cli --goal "Write tests" --step-json step.json --result-json result.json --mode store

Output: JSON with lessons or storage confirmation
"""

import json
import sys
from pathlib import Path

from .memory_integration import LearningIntegrator


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Manage learning and memory integration")
    parser.add_argument("--goal", required=True, help="Project goal")
    parser.add_argument("--mode", default="retrieve", choices=["retrieve", "store"],
                        help="Mode: retrieve lessons or store failure")
    parser.add_argument("--step-json", help="Path to step definition JSON (for store mode)")
    parser.add_argument("--result-json", help="Path to result JSON (for store mode)")
    parser.add_argument("--attempt", type=int, default=0, help="Attempt number")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--json-output", action="store_true", help="Output JSON")

    args = parser.parse_args()

    try:
        integrator = LearningIntegrator(project_root=args.project_root)

        if args.mode == "retrieve":
            # Retrieve lessons before planning
            lessons = integrator.retrieve_lessons_for_goal(args.goal, limit=5)
            lessons_prompt = integrator.format_lessons_for_prompt(args.goal, lessons)

            result = {
                "mode": "retrieve",
                "goal": args.goal,
                "lessons": lessons,
                "lessons_prompt": lessons_prompt,
                "success": True
            }

            if args.json_output:
                print(json.dumps(result))
            else:
                if lessons_prompt:
                    print(lessons_prompt)
                else:
                    print("No previous lessons found for this goal.")

            sys.exit(0)

        elif args.mode == "store":
            # Store failure lesson
            if not args.step_json or not args.result_json:
                raise ValueError("store mode requires --step-json and --result-json")

            step_data = json.loads(Path(args.step_json).read_text())
            result_data = json.loads(Path(args.result_json).read_text())

            success = integrator.store_failure_lesson(step_data, result_data, attempt=args.attempt)

            result = {
                "mode": "store",
                "goal": args.goal,
                "step_id": step_data.get("step_id"),
                "stored": success,
                "message": "Lesson stored successfully" if success else "Failed to store lesson"
            }

            if args.json_output:
                print(json.dumps(result))
            else:
                print(result["message"])

            sys.exit(0 if success else 1)

    except Exception as e:
        error_result = {
            "error": str(e),
            "goal": args.goal,
            "mode": args.mode
        }
        if args.json_output:
            print(json.dumps(error_result))
        else:
            print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
