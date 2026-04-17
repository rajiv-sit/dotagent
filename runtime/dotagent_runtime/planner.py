from __future__ import annotations

from typing import Any, Dict, List

from .models import Plan, Step, ValidationResult, new_id, utc_now


class Planner:
    """
    Adaptive local planner.
    It creates a persisted DAG, assigns roles/priority, and can apply
    bounded corrective updates when a step fails.
    
    Goal decomposition patterns:
    - auth/security -> add security validation
    - performance/optimize -> add benchmarking
    - refactor -> add impact analysis
    - deploy -> add packaging and rollout
    - test/coverage -> add coverage analysis
    - database/migrate -> add migration safety checks
    - api -> add contract testing
    - documentation -> add doc validation
    """

    def _decompose_goal(self, goal: str, context: Dict[str, Any] | None = None) -> List[str]:
        """
        Analyze goal and return content-specific work types to include in plan.
        Returns list of step kinds to add beyond base discover/plan/execute/validate/review.
        """
        lower_goal = goal.lower()
        work_types = []

        # Security/auth patterns
        if any(keyword in lower_goal for keyword in ["auth", "security", "encrypt", "token", "credential"]):
            work_types.append("SECURITY_CHECK")
        
        # Performance patterns
        if any(keyword in lower_goal for keyword in ["performance", "optimize", "speed", "benchmark", "latency"]):
            work_types.append("PERFORMANCE_CHECK")
        
        # Testing patterns
        if any(keyword in lower_goal for keyword in ["test", "coverage", "mock"]):
            work_types.append("COVERAGE_ANALYSIS")
        
        # Database patterns
        if any(keyword in lower_goal for keyword in ["database", "migrate", "schema", "sql"]):
            work_types.append("MIGRATION_CHECK")
        
        # API patterns
        if any(keyword in lower_goal for keyword in ["api", "endpoint", "interface"]):
            work_types.append("CONTRACT_TEST")
        
        # Refactor patterns
        if any(keyword in lower_goal for keyword in ["refactor", "restructure", "reorganize"]):
            work_types.append("IMPACT_ANALYSIS")
        
        # Documentation patterns
        if any(keyword in lower_goal for keyword in ["document", "readme", "guide"]):
            work_types.append("DOC_VALIDATION")
        
        # Deployment patterns
        if any(keyword in lower_goal for keyword in ["deploy", "release", "rollout"]):
            work_types.append("PACKAGING")
            work_types.append("DEPLOYMENT_CHECK")
        
        return work_types

    def _create_specialized_steps(self, work_types: List[str], base_priority: int = 45) -> List[Step]:
        """Create specialized validation/check steps based on goal decomposition."""
        steps = []
        priority = base_priority

        if "SECURITY_CHECK" in work_types:
            steps.append(Step(
                id="security_check",
                name="Security and authentication review",
                kind="SECURITY_CHECK",
                depends_on=["execute"],
                tool="security_validator",
                payload={"exclude_patterns": ["*.pyc", "__pycache__"]},
                acceptance={"status_equals": "PASS"},
                priority=priority,
                agent_role="security_agent",
                parallel_group="post_execute",
            ))
            priority += 1

        if "PERFORMANCE_CHECK" in work_types:
            steps.append(Step(
                id="performance_check",
                name="Performance profiling and benchmarking",
                kind="PERFORMANCE_CHECK",
                depends_on=["execute"],
                tool="performance_validator",
                payload={},
                acceptance={"status_equals": "PASS"},
                priority=priority,
                agent_role="performance_agent",
                parallel_group="post_execute",
            ))
            priority += 1

        if "COVERAGE_ANALYSIS" in work_types:
            steps.append(Step(
                id="coverage",
                name="Code coverage analysis",
                kind="COVERAGE_ANALYSIS",
                depends_on=["execute"],
                tool="coverage_validator",
                payload={"coverage_threshold": 80.0},
                acceptance={"status_equals": "PASS"},
                priority=priority,
                agent_role="validator_agent",
                parallel_group="post_execute",
            ))
            priority += 1

        if "MIGRATION_CHECK" in work_types:
            steps.append(Step(
                id="migration_check",
                name="Database migration safety check",
                kind="MIGRATION_CHECK",
                depends_on=["execute"],
                tool="validator",
                payload={"checks": ["migration_reversible", "no_data_loss"]},
                acceptance={"status_equals": "PASS"},
                priority=priority,
                agent_role="validator_agent",
                parallel_group="post_execute",
            ))
            priority += 1

        if "CONTRACT_TEST" in work_types:
            steps.append(Step(
                id="contract_test",
                name="API contract and interface testing",
                kind="CONTRACT_TEST",
                depends_on=["execute"],
                tool="test_runner",
                payload={"command": None},
                acceptance={"status_equals": "PASS"},
                priority=priority,
                agent_role="validator_agent",
                parallel_group="post_execute",
            ))
            priority += 1

        if "IMPACT_ANALYSIS" in work_types:
            steps.append(Step(
                id="impact_analysis",
                name="Refactoring impact analysis",
                kind="IMPACT_ANALYSIS",
                depends_on=["execute"],
                tool="validator",
                payload={"checks": ["no_breaking_changes", "backwards_compatible"]},
                acceptance={"status_equals": "PASS"},
                priority=priority,
                agent_role="validator_agent",
                parallel_group="post_execute",
            ))
            priority += 1

        if "DOC_VALIDATION" in work_types:
            steps.append(Step(
                id="doc_validation",
                name="Documentation accuracy and completeness",
                kind="DOC_VALIDATION",
                depends_on=["execute"],
                tool="validator",
                payload={"checks": ["no_broken_links", "commands_valid"]},
                acceptance={"status_equals": "PASS"},
                priority=priority,
                agent_role="doc_agent",
                parallel_group="post_execute",
            ))
            priority += 1

        # Add build and lint validators if not already covered
        if not any(w in work_types for w in ["PERFORMANCE_CHECK", "SECURITY_CHECK"]):
            steps.append(Step(
                id="build_check",
                name="Build artifact and lint validation",
                kind="BUILD_CHECK",
                depends_on=["execute"],
                tool="build_validator",
                payload={"build_dirs": ["build/", "dist/", "bin/", "out/", "target/"]},
                acceptance={"status_equals": "PASS"},
                priority=priority,
                agent_role="executor_agent",
                parallel_group="post_execute",
            ))
            steps.append(Step(
                id="lint_check",
                name="Code quality and linting validation",
                kind="LINT_CHECK",
                depends_on=["execute"],
                tool="lint_validator",
                payload={},
                acceptance={"status_equals": "PASS"},
                priority=priority + 1,
                agent_role="validator_agent",
                parallel_group="post_execute",
            ))

        return steps

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

        # Decompose goal to determine specialized steps
        work_types = self._decompose_goal(goal, context)

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

            # Add specialized steps based on goal decomposition
            specialized_steps = self._create_specialized_steps(work_types, base_priority=45)

            validate = Step(
                id="validate",
                name="Validate execution result",
                kind="VALIDATE",
                depends_on=["tests", "policy"] + [s.id for s in specialized_steps],
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

            extra = [execute, verify_tests, policy] + specialized_steps + [validate, review]

        steps = base + extra
        if "deploy" in lower_goal and inferred_target == "local":
            # Insert package step before the final validate and review
            package_step = Step(
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
            )
            validate_step = next((s for s in steps if s.id == "validate"), None)
            if validate_step:
                validate_step.depends_on = list(set(validate_step.depends_on + [package_step.id]))
                # Insert package step right before validate
                validate_idx = steps.index(validate_step)
                steps.insert(validate_idx, package_step)
            else:
                steps.insert(-1, package_step)

        metadata = {
            "job_type": job_type,
            "replans": 0,
            "execution_target": inferred_target,
            "max_parallelism": max_parallelism,
            "planner_mode": "adaptive",
            "context_hits": sum(len(entries) for entries in (context or {}).values()) if context else 0,
            "roles": sorted({step.agent_role for step in steps}),
            "work_types": work_types,
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
