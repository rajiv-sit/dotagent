import unittest

from dotagent_runtime.validator import Validator


class TestValidator(unittest.TestCase):
    def test_pass_when_all_ok(self):
        validator = Validator()
        result = validator.validate_step_result(
            {"id": "execute", "acceptance": {"returncode": 0}, "attempts": 1, "max_attempts": 2},
            {"tool": "shell", "ok": True, "output": {"returncode": 0}},
        )
        self.assertEqual(result.status, "PASS")

    def test_fail_when_any_not_ok(self):
        validator = Validator()
        result = validator.validate_step_result(
            {"id": "execute", "acceptance": {"returncode": 0}, "attempts": 1, "max_attempts": 2},
            {"tool": "shell", "ok": False, "output": {"returncode": 1}},
        )
        self.assertEqual(result.status, "FAIL")
        self.assertTrue(result.corrective_actions)
        self.assertTrue(result.retryable)

    def test_policy_engine_checks_duration_budget(self):
        validator = Validator()
        result = validator.validate_step_result(
            {
                "id": "tests",
                "acceptance": {
                    "policies": [{"kind": "max_duration_ms", "value": 10, "name": "fast_enough"}],
                },
                "attempts": 1,
                "max_attempts": 1,
            },
            {"tool": "test_runner", "ok": True, "output": {"metrics": {"duration_ms": 25}}},
        )
        self.assertEqual(result.status, "FAIL")
        self.assertTrue(any(check["name"] == "fast_enough" for check in result.checks))


if __name__ == "__main__":
    unittest.main()
