import unittest
from pathlib import Path
import uuid

from dotagent_runtime.bootstrap import setup_runtime
from dotagent_runtime.orchestrator import Orchestrator


WORKSPACE_TEMP_ROOT = Path(__file__).resolve().parents[2] / "_tmp_runtime_tests"
WORKSPACE_TEMP_ROOT.mkdir(exist_ok=True)


class TestOrchestrator(unittest.TestCase):
    def _make_test_root(self) -> Path:
        root = WORKSPACE_TEMP_ROOT / f"case-{uuid.uuid4().hex[:8]}"
        root.mkdir(parents=True, exist_ok=True)
        return root

    def _seed_required_docs(self, root: Path) -> None:
        for name, content in {
            "AGENTS.md": "# Agents\n",
            "PLAN.md": "# Plan\n",
        }.items():
            (root / name).write_text(content, encoding="utf-8")

    def test_prepare_and_execute_task(self):
        root = self._make_test_root()
        self._seed_required_docs(root)
        setup_runtime(str(root))
        orch = Orchestrator(str(root))
        prepared = orch.prepare_task("demo", command='python -c "print(\'ok\')"')

        plan = orch.store.load_plan(prepared["plan"]["id"])
        execute_step = next(step for step in plan["steps"] if step["id"] == "execute")
        execute_step["acceptance"]["contains_text"] = "ok"
        orch.store.update_plan(plan["id"], **plan)

        result = orch.execute_plan(prepared["job"]["id"], prepared["plan"]["id"])
        self.assertEqual(result["validation"]["status"], "PASS")
        self.assertEqual(result["job"]["status"], "SUCCESS")
        self.assertIn("telemetry", result)
        self.assertGreaterEqual(result["telemetry"]["metrics"]["executed_step_count"], 1)
        self.assertTrue(Path(result["telemetry_path"]).exists())
        self.assertIn("validator_agent", result["agent_roles"])

    def test_execute_plan_replans_with_fallback_command(self):
        root = self._make_test_root()
        self._seed_required_docs(root)
        setup_runtime(str(root))
        orch = Orchestrator(str(root))
        prepared = orch.prepare_task("recover")

        plan = orch.store.load_plan(prepared["plan"]["id"])
        execute_step = next(step for step in plan["steps"] if step["id"] == "execute")
        execute_step["payload"] = {
            "command": 'python -c "import sys; sys.exit(1)"',
            "fallback_commands": ['python -c "print(\'recovered\')"'],
        }
        execute_step["acceptance"] = {"returncode": 0, "contains_text": "recovered"}
        orch.store.update_plan(plan["id"], **plan)

        result = orch.execute_plan(prepared["job"]["id"], prepared["plan"]["id"])
        updated_plan = orch.store.load_plan(prepared["plan"]["id"])
        updated_execute = next(step for step in updated_plan["steps"] if step["id"] == "execute")

        self.assertEqual(result["job"]["status"], "SUCCESS")
        self.assertEqual(updated_execute["attempts"], 2)
        self.assertEqual(updated_plan["metadata"]["replans"], 1)
        self.assertEqual(updated_execute["status"], "SUCCESS")
        self.assertEqual(result["telemetry"]["metrics"]["retry_count"], 1)

    def test_prepare_task_supports_external_target(self):
        root = self._make_test_root()
        self._seed_required_docs(root)
        setup_runtime(str(root))
        orch = Orchestrator(str(root))
        prepared = orch.prepare_task("deploy to slurm cluster", execution_target="slurm")
        execute = next(step for step in prepared["plan"]["steps"] if step["id"] == "execute")
        self.assertEqual(execute["tool"], "slurm_job")

    def test_semantic_memory_is_written_after_run(self):
        root = self._make_test_root()
        self._seed_required_docs(root)
        setup_runtime(str(root))
        orch = Orchestrator(str(root))
        prepared = orch.prepare_task("analyze adaptive planner", command='python -c "print(\'ok\')"')
        plan = orch.store.load_plan(prepared["plan"]["id"])
        execute_step = next(step for step in plan["steps"] if step["id"] == "execute")
        tests_step = next(step for step in plan["steps"] if step["id"] == "tests")
        execute_step["acceptance"]["contains_text"] = "ok"
        tests_step["payload"]["command"] = 'python -c "print(\'tests-pass\')"'
        plan["metadata"]["max_parallelism"] = 2
        orch.store.update_plan(plan["id"], **plan)

        result = orch.execute_plan(prepared["job"]["id"], prepared["plan"]["id"])
        semantic_hits = orch.memory.search("semantic", "adaptive planner", limit=5)
        self.assertEqual(result["job"]["status"], "SUCCESS")
        self.assertTrue(semantic_hits)

    def test_cancel_marks_job_and_plan(self):
        root = self._make_test_root()
        self._seed_required_docs(root)
        setup_runtime(str(root))
        orch = Orchestrator(str(root))
        prepared = orch.prepare_task("cancel me")

        cancelled = orch.cancel(prepared["job"]["id"])

        self.assertEqual(cancelled["job"]["status"], "CANCELLED")
        self.assertIsNotNone(cancelled["plan"])
        self.assertTrue(cancelled["plan"]["metadata"]["cancelled"])
        self.assertTrue(
            all(
                step["status"] == "CANCELLED"
                for step in cancelled["plan"]["steps"]
                if step["status"] == "CANCELLED"
            )
        )


if __name__ == "__main__":
    unittest.main()
