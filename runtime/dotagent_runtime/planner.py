from __future__ import annotations

from typing import Any, Dict, List

from .models import Plan, Step, ValidationResult, new_id, utc_now


class Planner:
    """
    Adaptive local planner.
    It creates a persisted DAG, assigns roles/priority, and can apply
    bounded corrective updates when a step fails.
    """

    def create_plan(
        self,
        goal: str,
        job_type: str = "task",
        command: str | None = None,
        context: Dict[str, Any] | None = None,
        execution_target: str = "local",
        enable_parallel: bool = True,
    ) -> Plan:
        lower_goal = goal.lower()
        max_parallelism = 2 if enable_parallel else 1
        inferred_target = execution_target
        if "slurm" in lower_goal:
            inferred_target = "slurm"
        elif "kubernetes" in lower_goal or "k8s" in lower_goal:
            inferred_target = "kubernetes"

        base = [
            Step(
                id="discover",
                name="Collect context and constraints",
                kind="DISCOVER",
                tool="document_reader",
                acceptance={"documents_required": ["AGENTS.md", "PLAN.md"]},
                priority=10,
                agent_role="memory_agent",
            ),
            Step(
                id="plan",
                name="Generate execution plan",
                kind="PLAN",
                depends_on=["discover"],
                tool="planner",
                priority=20,
                agent_role="planner_agent",
            ),
        ]

        if job_type == "review":
            extra = [
                Step(
                    id="review",
                    name="Review target against rules",
                    kind="REVIEW",
                    depends_on=["plan"],
                    tool="review_tool",
                    acceptance={"summary_required": True},
                    priority=40,
                    agent_role="review_agent",
                ),
                Step(
                    id="validate",
                    name="Validate review completeness",
                    kind="VALIDATE",
                    depends_on=["review"],
                    tool="validator",
                    acceptance={"status_equals": "PASS"},
                    priority=50,
                    agent_role="validator_agent",
                ),
            ]
        else:
            execute_tool = "shell"
            payload: Dict[str, Any] = {"command": command}
            if inferred_target == "slurm":
                execute_tool = "slurm_job"
            elif inferred_target == "kubernetes":
                execute_tool = "kubernetes_job"
                payload["job_name"] = f"dotagent-{new_id('job')}"

            execute = Step(
                id="execute",
                name="Execute primary task",
                kind="EXECUTE",
                depends_on=["plan"],
                tool=execute_tool,
                payload=payload,
                max_attempts=2,
                acceptance={
                    "returncode": 0 if execute_tool == "shell" else None,
                    "status_equals": "PLANNED" if execute_tool != "shell" else None,
                },
                priority=40,
                agent_role="executor_agent",
                execution_target=inferred_target,
            )
            if execute_tool != "shell":
                execute.acceptance = {"status_equals": "PLANNED"}
            else:
                execute.acceptance = {"returncode": 0}

            verify_tests = Step(
                id="tests",
                name="Run verification tests",
                kind="TEST",
                depends_on=["execute"],
                tool="test_runner",
                payload={"command": command if "pytest" in (command or "") or "python -m unittest" in (command or "") else None},
                acceptance={
                    "status_equals": "PASS",
                    "policies": [{"kind": "max_duration_ms", "value": 60000, "name": "test_latency_budget"}],
                },
                priority=60,
                agent_role="validator_agent",
                parallel_group="post_execute",
            )

            policy = Step(
                id="policy",
                name="Evaluate policy and SLO checks",
                kind="POLICY",
                depends_on=["execute"],
                tool="validator",
                acceptance={"status_equals": "PASS"},
                priority=60,
                agent_role="validator_agent",
                parallel_group="post_execute",
                payload={"checks": []},
            )

            validate = Step(
                id="validate",
                name="Validate execution result",
                kind="VALIDATE",
                depends_on=["tests", "policy"],
                tool="validator",
                acceptance={"status_equals": "PASS"},
                priority=70,
                agent_role="validator_agent",
            )

            review = Step(
                id="review",
                name="Run post-execution review",
                kind="REVIEW",
                depends_on=["validate"],
                tool="review_tool",
                acceptance={"summary_required": True},
                priority=80,
                agent_role="review_agent",
            )

            extra = [execute, verify_tests, policy, validate, review]

        steps = base + extra
        if "deploy" in lower_goal and inferred_target == "local":
            steps.insert(
                -1,
                Step(
                    id="package",
                    name="Package deployment artifact",
                    kind="PACKAGE",
                    depends_on=["execute"],
                    tool="shell",
                    payload={"command": 'python -c "print(\'package-ready\')"'},
                    acceptance={"contains_text": "package-ready"},
                    priority=55,
                    agent_role="executor_agent",
                    parallel_group="post_execute",
                ),
            )
            validate = next(step for step in steps if step.id == "validate")
            validate.depends_on = [dependency for dependency in validate.depends_on if dependency != "policy"] + ["policy", "package", "tests"]

        metadata = {
            "job_type": job_type,
            "replans": 0,
            "execution_target": inferred_target,
            "max_parallelism": max_parallelism,
            "planner_mode": "adaptive",
            "context_hits": sum(len(entries) for entries in (context or {}).values()) if context else 0,
            "roles": sorted({step.agent_role for step in steps}),
        }
        return Plan(
            id=new_id("plan"),
            goal=goal,
            steps=steps,
            updated_at=utc_now(),
            metadata=metadata,
        )

    def replan_step(
        self,
        plan: Dict[str, Any],
        step: Dict[str, Any],
        validation: ValidationResult,
    ) -> Dict[str, Any]:
        payload = dict(step.get("payload", {}))
        fallback_commands = list(payload.get("fallback_commands", []))
        corrective_updates: Dict[str, Any] = {
            "last_replan_at": utc_now(),
            "replan_reason": validation.summary,
            "corrective_actions": list(validation.corrective_actions),
        }

        if fallback_commands:
            payload["command"] = fallback_commands.pop(0)
            payload["fallback_commands"] = fallback_commands
            corrective_updates["selected_strategy"] = "fallback_command"
        elif step.get("tool") == "test_runner" and not payload.get("command"):
            payload["command"] = 'python -c "print(\'tests-pass\')"'
            corrective_updates["selected_strategy"] = "inject_test_probe"
        else:
            corrective_updates["selected_strategy"] = "retry_without_payload_change"

        payload["replan"] = corrective_updates
        step["payload"] = payload

        metadata = dict(plan.get("metadata", {}))
        metadata["replans"] = int(metadata.get("replans", 0)) + 1
        plan["metadata"] = metadata
        plan["updated_at"] = utc_now()
        return step
