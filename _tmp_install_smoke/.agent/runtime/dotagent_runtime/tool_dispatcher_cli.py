#!/usr/bin/env python3
"""
CLI wrapper for InternalToolDispatcher - execute tools without delegating to agent.

Usage:
    python -m dotagent_runtime.tool_dispatcher_cli --tool write_file --payload '{"path":"file.py","content":"print(1)"}' --project-root .

Output: JSON tool result
"""

import json
import sys
from pathlib import Path

from .tool_dispatcher import InternalToolDispatcher, ToolResult


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Dispatch internal tools (write_file, run_tests, build, etc.)")
    parser.add_argument("--tool", required=True, help="Tool name (write_file, read_file, run_tests, run_linter, build, etc.)")
    parser.add_argument("--payload", required=True, help="JSON payload for tool")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--json-output", action="store_true", help="Output JSON")

    args = parser.parse_args()

    try:
        payload = json.loads(args.payload)
        dispatcher = InternalToolDispatcher(project_root=args.project_root)

        if not dispatcher.can_handle(args.tool):
            result = ToolResult(
                success=False,
                stdout="",
                stderr=f"Unknown tool: {args.tool}",
                exit_code=1
            )
        else:
            result = dispatcher.dispatch(args.tool, payload)

        result_dict = {
            "success": result.success,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.exit_code,
            "output": result.output
        }

        if args.json_output:
            print(json.dumps(result_dict))
        else:
            print(f"Exit Code: {result.exit_code}")
            if result.stdout:
                print(f"Output:\n{result.stdout}")
            if result.stderr:
                print(f"Error:\n{result.stderr}", file=sys.stderr)

        sys.exit(result.exit_code if result.success else 1)

    except json.JSONDecodeError as e:
        error_result = {
            "success": False,
            "stdout": "",
            "stderr": f"Invalid JSON payload: {e}",
            "exit_code": 2
        }
        if args.json_output:
            print(json.dumps(error_result))
        else:
            print(f"Error: Invalid JSON payload: {e}")
        sys.exit(2)

    except Exception as e:
        error_result = {
            "success": False,
            "stdout": "",
            "stderr": str(e),
            "exit_code": 1
        }
        if args.json_output:
            print(json.dumps(error_result))
        else:
            print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
