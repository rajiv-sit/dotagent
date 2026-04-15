import tempfile
import unittest
from dotagent_runtime.bootstrap import setup_runtime
from dotagent_runtime.orchestrator import Orchestrator

class TestOrchestrator(unittest.TestCase):
    def test_prepare_and_execute_task(self):
        with tempfile.TemporaryDirectory() as td:
            setup_runtime(td)
            orch = Orchestrator(td)
            prepared = orch.prepare_task("demo")
            result = orch.execute_plan(prepared["job"]["id"], prepared["plan"]["id"])
            self.assertEqual(result["validation"]["status"], "PASS")
            self.assertEqual(result["job"]["status"], "SUCCESS")

if __name__ == "__main__":
    unittest.main()
