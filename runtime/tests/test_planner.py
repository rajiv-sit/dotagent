import unittest
from dotagent_runtime.planner import Planner

class TestPlanner(unittest.TestCase):
    def test_create_plan_contains_execute_for_task(self):
        planner = Planner()
        plan = planner.create_plan("build x", job_type="task")
        kinds = [step.kind for step in plan.steps]
        self.assertIn("EXECUTE", kinds)
        self.assertIn("VALIDATE", kinds)
        self.assertIn("TEST", kinds)
        self.assertIn("POLICY", kinds)

    def test_create_plan_contains_review_for_review_job(self):
        planner = Planner()
        plan = planner.create_plan("review x", job_type="review")
        kinds = [step.kind for step in plan.steps]
        self.assertIn("REVIEW", kinds)
        self.assertIn("VALIDATE", kinds)

    def test_create_plan_infers_external_target(self):
        planner = Planner()
        plan = planner.create_plan("deploy on kubernetes", job_type="task")
        execute = next(step for step in plan.steps if step.id == "execute")
        self.assertEqual(execute.tool, "kubernetes_job")
        self.assertEqual(plan.metadata["execution_target"], "kubernetes")

if __name__ == "__main__":
    unittest.main()
