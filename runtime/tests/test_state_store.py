import json
import tempfile
import unittest
from pathlib import Path
from dotagent_runtime.models import Job
from dotagent_runtime.state_store import StateStore

class TestStateStore(unittest.TestCase):
    def test_save_and_load_job(self):
        with tempfile.TemporaryDirectory() as td:
            store = StateStore(td)
            job = Job.create("task", {"goal": "hello"})
            store.save_job(job)
            loaded = store.load_job(job.id)
            self.assertEqual(loaded["id"], job.id)
            self.assertEqual(loaded["input"]["goal"], "hello")

if __name__ == "__main__":
    unittest.main()
