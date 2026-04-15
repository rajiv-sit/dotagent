import unittest
from dotagent_runtime.planner import Planner

class TestPlanner(unittest.TestCase):
    def test_create_plan_contains_execute_for_task(self):
        planner = Planner()
        plan = planner.create_plan("build x", job_type="task")
        kinds = [step.kind for step in plan.steps]
        self.assertIn("EXECUTE", kinds)
        self.assertIn("TEST", kinds)

    def test_create_plan_contains_review_for_review_job(self):
        planner = Planner()
        plan = planner.create_plan("review x", job_type="review")
        kinds = [step.kind for step in plan.steps]
        self.assertIn("REVIEW", kinds)
        self.assertIn("VALIDATE", kinds)

if __name__ == "__main__":
    unittest.main()
