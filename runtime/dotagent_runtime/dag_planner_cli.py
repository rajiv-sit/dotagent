#!/usr/bin/env python3
"""
CLI wrapper for DAG Planner - generates real task graphs with parallelization.

Usage:
    python -m dotagent_runtime.dag_planner_cli --goal "Build satellite UI + backend" --project-root .

Output: JSON DAG with parallel execution paths
"""

import json
import sys
from pathlib import Path

from .dag_planner import GoalDecomposer, DAGOptimizer


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate real task DAG with parallelization")
    parser.add_argument("--goal", required=True, help="Project goal")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--json-output", action="store_true", help="Output JSON")

    args = parser.parse_args()

    try:
        decomposer = GoalDecomposer()
        optimizer = DAGOptimizer()

        # Decompose goal into tasks
        tasks = decomposer.decompose(args.goal)

        # Optimize for parallel execution
        optimized_tasks = optimizer.optimize(tasks)

        # Serialize to JSON
        dag = optimizer.serialize(optimized_tasks)

        result = {
            "goal": args.goal,
            "task_count": len(optimized_tasks),
            "has_parallelization": any(len(t["depends_on"]) == 0 for t in dag[1:]),  # Skip first
            "tasks": dag
        }

        if args.json_output:
            print(json.dumps(result))
        else:
            print(f"Goal: {args.goal}")
            print(f"Tasks: {len(optimized_tasks)}")
            print(f"Parallelizable: {sum(1 for t in optimized_tasks if t.can_parallelize)} tasks can run in parallel")
            print("\nTask DAG:")
            for task in optimized_tasks:
                deps = f" (depends on: {', '.join(task.depends_on)})" if task.depends_on else " (independent)"
                print(f"  {task.id}: {task.name}{deps}")

        sys.exit(0)

    except Exception as e:
        error_result = {
            "error": str(e),
            "goal": args.goal
        }
        if args.json_output:
            print(json.dumps(error_result))
        else:
            print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
