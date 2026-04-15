import unittest
from dotagent_runtime.validator import Validator

class TestValidator(unittest.TestCase):
    def test_pass_when_all_ok(self):
        v = Validator()
        result = v.validate_job_outputs([{"step_id":"a","tool":"x","ok":True}])
        self.assertEqual(result.status, "PASS")

    def test_fail_when_any_not_ok(self):
        v = Validator()
        result = v.validate_job_outputs([{"step_id":"a","tool":"x","ok":False}])
        self.assertEqual(result.status, "FAIL")
        self.assertTrue(result.corrective_actions)

if __name__ == "__main__":
    unittest.main()
