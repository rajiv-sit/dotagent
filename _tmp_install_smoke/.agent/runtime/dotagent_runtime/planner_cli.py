#!/usr/bin/env python3
"""
CLI wrapper for Planner - generates dynamic DAG from goal + context.

Usage:
    python -m dotagent_runtime.planner_cli --goal "Implement auth" --project-root .

Output: JSON DAG
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

from .planner import Planner
from .models import Plan


def load_context(project_root: str) -> Dict[str, Any]:
    """Load project context from root docs."""
    context = {}
    for doc_name in ["CONTEXT.md", "PLAN.md", "Architecture.md"]:
        doc_path = Path(project_root) / doc_name
        if doc_path.exists():
            try:
                context[doc_name] = doc_path.read_text(encoding="utf-8")[:2000]
            except Exception:
                context[doc_name] = ""
    return context


def plan_to_dag(plan: Plan) -> Dict[str, Any]:
    """Convert Plan to DAG format: [{ id, action, deps }, ...]"""
    dag = []
    for step in plan.steps:
        dag.append({
            "id": step.id,
            "action": step.name,
            "kind": step.kind,
            "tool": step.tool,
            "deps": step.depends_on or [],
            "priority": step.priority,
            "max_attempts": step.max_attempts,
        })
    return {
        "plan_id": plan.id,
        "goal": plan.goal,
        "dag": dag,
        "metadata": plan.metadata,
    }


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate dynamic DAG from goal")
    parser.add_argument("--goal", required=True, help="Software goal to plan")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--job-type", choices=["task", "review"], default="task")
    parser.add_argument("--execution-target", default="local")
    parser.add_argument("--enable-parallel", action="store_true", default=True)
    parser.add_argument("--json-output", action="store_true", default=True)

    args = parser.parse_args()

    try:
        context = load_context(args.project_root)
        planner = Planner()
        plan = planner.create_plan(
            goal=args.goal,
            job_type=args.job_type,
            context=context,
            execution_target=args.execution_target,
            enable_parallel=args.enable_parallel,
        )

        if args.json_output:
            dag_output = plan_to_dag(plan)
            print(json.dumps(dag_output, indent=2))
            return 0
        else:
            print(f"Plan ID: {plan.id}")
            print(f"Goal: {plan.goal}")
            print(f"Steps: {len(plan.steps)}")
            for step in plan.steps:
                print(f"  - {step.id}: {step.name}")
            return 0

    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
