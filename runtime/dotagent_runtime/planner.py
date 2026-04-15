from __future__ import annotations
from typing import List
from .models import Plan, Step, new_id

class Planner:
    """
    Deterministic baseline planner.
    Replace or extend with an LLM-backed planner later.
    """

    def create_plan(self, goal: str, job_type: str = "task") -> Plan:
        base = [
            Step(id="discover", name="Collect context and constraints", kind="DISCOVER", tool="document_reader"),
            Step(id="plan", name="Generate execution plan", kind="PLAN", depends_on=["discover"], tool="planner"),
        ]

        if job_type == "review":
            extra = [
                Step(id="review", name="Review target against rules", kind="REVIEW", depends_on=["plan"], tool="review_tool"),
                Step(id="validate", name="Validate review completeness", kind="VALIDATE", depends_on=["review"], tool="validator"),
            ]
        else:
            extra = [
                Step(id="execute", name="Execute primary task", kind="EXECUTE", depends_on=["plan"], tool="shell"),
                Step(id="test", name="Run task-level validation", kind="TEST", depends_on=["execute"], tool="validator"),
                Step(id="review", name="Run post-execution review", kind="REVIEW", depends_on=["test"], tool="review_tool"),
            ]

        steps = base + extra
        return Plan(id=new_id("plan"), goal=goal, steps=steps)
