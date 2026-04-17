"""
Memory Integration - Orchestrator hooks for learning from failures and successes.

Coordinates between failure analysis, memory storage, and prompt enhancement.
Closes the learning loop so system improves over time.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from .memory import MemoryManager
from .failure_analyzer import FailureAnalyzer


class LearningIntegrator:
    """Integrates learning into orchestration."""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.memory = MemoryManager(project_root=str(self.project_root))
        self.analyzer = FailureAnalyzer()

    def retrieve_lessons_for_goal(self, goal: str, limit: int = 5) -> Dict[str, Any]:
        """
        Retrieve applicable lessons before planning.
        
        Returns:
        {
            "applicable_lessons": [
                {goal_pattern, successful_approach, confidence},
                ...
            ],
            "failure_patterns": [
                {pattern, corrective_action, keywords},
                ...
            ]
        }
        """
        try:
            # Get success patterns
            success_patterns = self.memory.get_success_patterns(goal, limit=limit)

            # Get failure lessons
            failure_patterns = self.memory.get_applicable_lessons(goal, limit=limit)

            return {
                "applicable_lessons": success_patterns,
                "failure_patterns": failure_patterns,
                "context": f"Retrieved {len(success_patterns)} successes and {len(failure_patterns)} lessons for goal: {goal}"
            }
        except Exception as e:
            return {
                "applicable_lessons": [],
                "failure_patterns": [],
                "context": f"Error retrieving lessons: {e}"
            }

    def store_failure_lesson(self, step: Dict[str, Any], result: Dict[str, Any], attempt: int = 0) -> bool:
        """
        Analyze failure and store as lesson for future use.
        
        Returns: True if stored successfully
        """
        try:
            # Run failure analysis
            analysis = self.analyzer.analyze(step, result, previous_attempt=attempt)

            # Extract keywords from step
            keywords = self._extract_keywords(step)

            # Store each root cause as a lesson
            for root_cause in analysis.root_causes:
                corrective_actions = analysis.corrective_actions
                self.memory.put_failure_lesson(
                    pattern=root_cause,
                    corrective_action=" | ".join(corrective_actions) if corrective_actions else "Retry",
                    keywords=keywords
                )

            return True
        except Exception as e:
            print(f"Error storing failure lesson: {e}")
            return False

    def store_success_pattern(self, goal: str, approach: str, step_count: int = 0):
        """Store successful approach for future reference."""
        try:
            self.memory.put_success_pattern(
                goal_pattern=goal,
                successful_approach=approach,
                metadata={
                    "step_count": step_count,
                    "confidence": min(0.95, 0.5 + (step_count * 0.1))  # Higher confidence for fewer steps
                }
            )
        except Exception as e:
            print(f"Error storing success: {e}")

    def format_lessons_for_prompt(self, goal: str, lessons: Dict[str, Any]) -> str:
        """Format retrieved lessons into prompt section."""
        if not lessons.get("applicable_lessons") and not lessons.get("failure_patterns"):
            return ""

        sections = []

        if lessons.get("applicable_lessons"):
            sections.append("## LEARN FROM SUCCESS")
            sections.append("Previous similar goals were solved with these approaches:")
            for pattern in lessons["applicable_lessons"][:3]:
                approach = pattern.get("successful_approach", "")
                confidence = pattern.get("confidence", 0)
                sections.append(f"- {approach} ({confidence:.0%} confidence)")

        if lessons.get("failure_patterns"):
            sections.append("\n## AVOID THESE MISTAKES")
            sections.append("Related tasks failed with these issues:")
            for failure in lessons["failure_patterns"][:3]:
                pattern = failure.get("pattern", "")
                fix = failure.get("corrective_action", "")
                if fix:
                    sections.append(f"- Problem: {pattern}")
                    sections.append(f"  Solution: {fix}")
                else:
                    sections.append(f"- {pattern}")

        return "\n".join(sections)

    def _extract_keywords(self, step: Dict[str, Any]) -> List[str]:
        """Extract keywords from step for memory categorization."""
        keywords = []

        step_id = step.get("step_id", "")
        if step_id:
            keywords.append(step_id)

        kind = step.get("kind", "")
        if kind:
            keywords.append(kind)

        step_name = step.get("name", "")
        if step_name:
            # Extract significant words
            for word in step_name.lower().split():
                if len(word) > 4:  # Skip short words
                    keywords.append(word.rstrip('.,!?'))

        return keywords


class MemoryEnhancedOrchestrator:
    """Adds memory learning to orchestration steps."""

    def __init__(self, project_root: str = "."):
        self.integrator = LearningIntegrator(project_root=project_root)

    def enrich_planning_context(self, goal: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Before planning, retrieve and inject learned lessons.
        
        Returns: Enhanced context with lessons
        """
        lessons = self.integrator.retrieve_lessons_for_goal(goal)

        context["learned_lessons"] = lessons
        lessons_prompt = self.integrator.format_lessons_for_prompt(goal, lessons)

        if lessons_prompt:
            context["lessons_section"] = lessons_prompt

        return context

    def record_attempt_outcome(
        self,
        goal: str,
        step: Dict[str, Any],
        result: Dict[str, Any],
        status: str,  # SUCCESS | FAILED
        attempt: int = 0
    ) -> None:
        """Record outcome of attempt for learning."""
        if status == "FAILED":
            # Learn from failure
            self.integrator.store_failure_lesson(step, result, attempt=attempt)
        elif status == "SUCCESS" and attempt == 0:
            # First-try success: store as pattern
            approach = f"Solved {step.get('name', '')} successfully"
            self.integrator.store_success_pattern(goal, approach, step_count=1)


class LessonPromptBuilder:
    """Build enhanced prompts that include lessons."""

    @staticmethod
    def inject_lessons_into_prompt(base_prompt: str, lessons_section: str) -> str:
        """Inject lessons at appropriate point in prompt."""
        if not lessons_section:
            return base_prompt

        # Insert lessons after initial task description
        lines = base_prompt.split("\n")
        insert_idx = min(5, len(lines))  # Insert after first section

        lines.insert(insert_idx, "\n" + lessons_section + "\n")
        return "\n".join(lines)

    @staticmethod
    def inject_failure_analysis_into_prompt(base_prompt: str, failure_analysis: str) -> str:
        """Inject failure analysis for retry attempt."""
        if not failure_analysis:
            return base_prompt

        return base_prompt + "\n\n" + failure_analysis


def integrate_memory_into_workflow(
    workflow_objective: str,
    context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    High-level function to integrate memory into workflow planning.
    
    Call this in New-Workflow before generating plan.
    """
    integrator = LearningIntegrator()
    lessons = integrator.retrieve_lessons_for_goal(workflow_objective)
    lessons_prompt = integrator.format_lessons_for_prompt(workflow_objective, lessons)

    return {
        "lessons": lessons,
        "lessons_prompt": lessons_prompt,
        "enriched_context": context
    }
