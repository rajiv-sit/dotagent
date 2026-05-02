import unittest

from dotagent_runtime.executor import StepExecutor
from dotagent_runtime.tools import ToolRegistry


class ExplodingTool:
    name = "explode"

    def execute(self, project_root, payload):
        raise RuntimeError("boom")


class TestExecutor(unittest.TestCase):
    def test_missing_tool_returns_structured_failure(self):
        executor = StepExecutor(ToolRegistry())
        result = executor.execute_step(
            ".",
            {"id": "missing", "tool": "not_registered", "attempts": 1},
            context={"attempt": 1},
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.tool, "not_registered")
        self.assertEqual(result.output["returncode"], 1)
        self.assertIn("Tool not registered", result.output["stderr"])
        self.assertEqual(result.metadata["mode"], "tool_error")

    def test_tool_exception_returns_structured_failure(self):
        registry = ToolRegistry()
        registry.register(ExplodingTool())
        executor = StepExecutor(registry)

        result = executor.execute_step(
            ".",
            {"id": "explode-step", "tool": "explode", "attempts": 1},
            context={"attempt": 1},
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.tool, "explode")
        self.assertIn("RuntimeError: boom", result.output["stderr"])
        self.assertEqual(result.metadata["error_type"], "RuntimeError")


if __name__ == "__main__":
    unittest.main()
