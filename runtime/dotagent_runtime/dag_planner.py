"""
Real DAG-based planner - decompose goals into independent parallel tasks.

Replaces fixed stage pipeline with dynamic task graph generation.
"""

from typing import Any, Dict, List, Set, Tuple
from dataclasses import dataclass
import re


@dataclass
class Task:
    """Represents an independent task in the DAG."""
    id: str
    name: str
    description: str
    depends_on: List[str]  # Task IDs this depends on
    work_types: List[str]  # security, test, performance, etc.
    subtasks: List[str] = None  # For compound tasks
    can_parallelize: bool = True  # Can run in parallel with dependents


class GoalDecomposer:
    """Decompose goals into independent parallel tasks."""

    def decompose(self, goal: str, context: Dict[str, Any] | None = None) -> List[Task]:
        """
        Analyze goal and return list of independent tasks.
        
        Example:
        Goal: "Build satellite UI + backend with database"
        Returns:
          [
            Task(id="backend", name="Backend implementation", depends_on=[]),
            Task(id="database", name="Database setup", depends_on=[]),
            Task(id="frontend", name="Frontend implementation", depends_on=[]),
            Task(id="integration", name="Backend-Frontend integration", depends_on=["backend", "frontend"]),
            Task(id="deploy", name="Deploy full system", depends_on=["integration", "database"])
          ]
        """
        lower_goal = goal.lower()
        tasks = []

        # 1. Detect if goal has multiple components
        components = self._extract_components(goal)

        if len(components) > 1:
            # Multi-component goal: create parallel subtasks
            dep_map = self._analyze_dependencies(components)
            tasks = self._create_parallel_tasks(components, dep_map)
        else:
            # Single-component goal: default structure
            tasks = self._create_default_tasks(goal)

        return tasks

    def _extract_components(self, goal: str) -> List[str]:
        """Extract independent components from goal."""
        components = []

        # Split on common separators
        parts = re.split(r'\s+and\s+|\s*,\s*|\s*\+\s*', goal, flags=re.IGNORECASE)

        for part in parts:
            part = part.strip()
            if len(part) > 5:  # Ignore very short parts
                # Classify component
                component_type = self._classify_component(part)
                if component_type:
                    components.append(part)

        return components if len(components) > 1 else []

    def _classify_component(self, component: str) -> str | None:
        """Classify what kind of component this is."""
        lower = component.lower()

        # Backend/server
        if any(w in lower for w in ["backend", "server", "api", "service", "database", "db"]):
            return "backend"
        # Frontend/UI
        if any(w in lower for w in ["frontend", "ui", "client", "web", "react", "vue"]):
            return "frontend"
        # Infrastructure
        if any(w in lower for w in ["deploy", "docker", "k8s", "cloud", "infrastructure"]):
            return "infrastructure"
        # Testing
        if any(w in lower for w in ["test", "integration", "e2e", "unit"]):
            return "testing"
        # Documentation
        if any(w in lower for w in ["doc", "readme", "guide", "manual"]):
            return "documentation"

        return None

    def _analyze_dependencies(self, components: List[str]) -> Dict[str, List[str]]:
        """Analyze which components depend on others."""
        dep_map = {}
        lower_goals = [c.lower() for c in components]

        for i, component in enumerate(lower_goals):
            deps = []

            # Backend usually comes before integration
            if "integration" in component or "deploy" in component:
                if any("backend" in c for c in lower_goals):
                    deps.append(components[lower_goals.index("backend")] if "backend" in lower_goals else None)
                if any("frontend" in c for c in lower_goals):
                    deps.append(components[lower_goals.index("frontend")] if "frontend" in lower_goals else None)

            # Frontend might depend on API spec from backend
            if "frontend" in component:
                if any("backend" in c or "api" in c for c in lower_goals):
                    # Frontend can start early but integration needs backend
                    deps.append(None)  # Soft dependency

            # Infrastructure/deploy depends on everything
            if "deploy" in component or "docker" in component:
                deps = [components[j] for j in range(len(components)) if j != i]

            dep_map[components[i]] = [d for d in deps if d is not None]

        return dep_map

    def _create_parallel_tasks(self, components: List[str], dep_map: Dict[str, List[str]]) -> List[Task]:
        """Create DAG tasks from parallel components."""
        tasks = []
        task_ids = {}

        # Create task for each component
        for i, component in enumerate(components):
            task_id = f"task_{i}"
            task_ids[component] = task_id

            deps = dep_map.get(component, [])
            dep_ids = [task_ids.get(d, "") for d in deps if d in task_ids]

            # Remove empty strings
            dep_ids = [d for d in dep_ids if d]

            task = Task(
                id=task_id,
                name=f"Implement: {component}",
                description=component,
                depends_on=dep_ids,
                work_types=self._extract_work_types(component),
                can_parallelize=len(dep_ids) == 0 or "deployment" not in component.lower()
            )
            tasks.append(task)

        # Add integration task if multiple components
        if len(tasks) > 1:
            parallel_task_ids = [t.id for t in tasks if len(t.depends_on) == 0]
            integration_task = Task(
                id="task_integration",
                name="Integrate components",
                description="Combine and test integration",
                depends_on=parallel_task_ids if parallel_task_ids else [t.id for t in tasks],
                work_types=["integration_test", "contract_test"],
                can_parallelize=False
            )
            tasks.append(integration_task)

        return tasks

    def _create_default_tasks(self, goal: str) -> List[Task]:
        """Create default task structure for single-component goals."""
        work_types = self._extract_work_types(goal)

        return [
            Task(
                id="discover",
                name="Discover requirements",
                description="Analyze goal and constraints",
                depends_on=[],
                work_types=["discovery"]
            ),
            Task(
                id="design",
                name="Design approach",
                description="Create architecture and plan",
                depends_on=["discover"],
                work_types=["planning"]
            ),
            Task(
                id="implement",
                name="Implement solution",
                description=goal,
                depends_on=["design"],
                work_types=work_types,
                can_parallelize=False
            ),
            Task(
                id="test",
                name="Validate implementation",
                description="Test and verify correctness",
                depends_on=["implement"],
                work_types=["test", "validation"],
                can_parallelize=False
            ),
            Task(
                id="review",
                name="Review and refine",
                description="Peer review and refinement",
                depends_on=["test"],
                work_types=["review"],
                can_parallelize=False
            )
        ]

    def _extract_work_types(self, goal: str) -> List[str]:
        """Extract work types from goal description."""
        lower_goal = goal.lower()
        work_types = []

        if any(kw in lower_goal for kw in ["auth", "security", "encrypt", "token", "credential", "oauth"]):
            work_types.append("SECURITY_CHECK")

        if any(kw in lower_goal for kw in ["performance", "optimize", "speed", "benchmark", "latency"]):
            work_types.append("PERFORMANCE_CHECK")

        if any(kw in lower_goal for kw in ["test", "coverage", "mock", "unit", "integration"]):
            work_types.append("COVERAGE_ANALYSIS")

        if any(kw in lower_goal for kw in ["database", "migrate", "schema", "sql"]):
            work_types.append("MIGRATION_CHECK")

        if any(kw in lower_goal for kw in ["api", "endpoint", "interface", "contract", "request"]):
            work_types.append("CONTRACT_TEST")

        if any(kw in lower_goal for kw in ["refactor", "restructure", "reorganize"]):
            work_types.append("IMPACT_ANALYSIS")

        if any(kw in lower_goal for kw in ["document", "readme", "guide", "manual"]):
            work_types.append("DOC_VALIDATION")

        if any(kw in lower_goal for kw in ["deploy", "release", "rollout", "docker", "k8s"]):
            work_types.append("DEPLOYMENT_CHECK")

        return work_types if work_types else ["general_validation"]


class DAGOptimizer:
    """Optimize DAG for parallel execution."""

    def optimize(self, tasks: List[Task]) -> List[Task]:
        """
        Optimize task order and parallelization.
        
        Returns tasks in order suitable for parallel execution.
        """
        # Group by dependency level
        levels = self._compute_levels(tasks)

        # Mark tasks that can run in parallel
        for level_num, task_ids in levels.items():
            if len(task_ids) > 1:
                for task_id in task_ids:
                    task = self._find_task(tasks, task_id)
                    if task:
                        task.can_parallelize = True

        return tasks

    def _compute_levels(self, tasks: List[Task]) -> Dict[int, List[str]]:
        """Compute execution levels (tasks at same depth can run in parallel)."""
        levels = {}
        task_map = {t.id: t for t in tasks}

        for task in tasks:
            level = self._compute_level(task, task_map)
            if level not in levels:
                levels[level] = []
            levels[level].append(task.id)

        return levels

    def _compute_level(self, task: Task, task_map: Dict[str, Task]) -> int:
        """Compute execution level (depth in dependency graph)."""
        if not task.depends_on:
            return 0

        max_dep_level = 0
        for dep_id in task.depends_on:
            dep_task = task_map.get(dep_id)
            if dep_task:
                dep_level = self._compute_level(dep_task, task_map)
                max_dep_level = max(max_dep_level, dep_level)

        return max_dep_level + 1

    def _find_task(self, tasks: List[Task], task_id: str) -> Task | None:
        """Find task by ID."""
        for task in tasks:
            if task.id == task_id:
                return task
        return None

    def serialize(self, tasks: List[Task]) -> List[Dict[str, Any]]:
        """Convert tasks to JSON-serializable format."""
        result = []
        for task in tasks:
            result.append({
                "id": task.id,
                "name": task.name,
                "description": task.description,
                "depends_on": task.depends_on,
                "work_types": task.work_types,
                "can_parallelize": task.can_parallelize
            })
        return result
