from __future__ import annotations
import argparse
import json
from pathlib import Path
from .bootstrap import setup_runtime
from .orchestrator import Orchestrator

def print_json(data):
    print(json.dumps(data, indent=2))

def main() -> None:
    parser = argparse.ArgumentParser(prog="dotagent")
    parser.add_argument("--project-root", default=".")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("setup")

    p_task = sub.add_parser("task")
    p_task.add_argument("goal")
    p_task.add_argument("--execute", action="store_true")

    p_review = sub.add_parser("review")
    p_review.add_argument("--target", required=True)

    p_run = sub.add_parser("run")
    p_run.add_argument("goal")
    p_run.add_argument("--execute", action="store_true")

    sub.add_parser("status")

    p_result = sub.add_parser("result")
    p_result.add_argument("--id", required=True)

    args = parser.parse_args()
    project_root = str(Path(args.project_root).resolve())

    if args.command == "setup":
        print_json(setup_runtime(project_root))
        return

    orch = Orchestrator(project_root)

    if args.command == "task":
        prepared = orch.prepare_task(args.goal)
        if not args.execute:
            print_json(prepared)
            return
        print_json(orch.execute_plan(prepared["job"]["id"], prepared["plan"]["id"]))
        return

    if args.command == "review":
        prepared = orch.prepare_review(args.target)
        print_json(prepared)
        return

    if args.command == "run":
        prepared = orch.prepare_task(args.goal)
        if args.execute:
            print_json(orch.execute_plan(prepared["job"]["id"], prepared["plan"]["id"]))
        else:
            print_json(prepared)
        return

    if args.command == "status":
        print_json(orch.status())
        return

    if args.command == "result":
        print_json(orch.result(args.id))
        return

if __name__ == "__main__":
    main()
