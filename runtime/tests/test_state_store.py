import unittest
from pathlib import Path
import uuid

from dotagent_runtime.models import Job
from dotagent_runtime.state_store import StateStore
from dotagent_runtime.memory import MemoryEntry, MemoryManager


WORKSPACE_TEMP_ROOT = Path(__file__).resolve().parents[2] / "_tmp_runtime_tests"
WORKSPACE_TEMP_ROOT.mkdir(exist_ok=True)


class TestStateStore(unittest.TestCase):
    def test_save_and_load_job(self):
        root = WORKSPACE_TEMP_ROOT / f"state-{uuid.uuid4().hex[:8]}"
        root.mkdir(parents=True, exist_ok=True)
        store = StateStore(str(root))
        job = Job.create("task", {"goal": "hello"})
        store.save_job(job)
        loaded = store.load_job(job.id)
        self.assertEqual(loaded["id"], job.id)
        self.assertEqual(loaded["input"]["goal"], "hello")

    def test_write_and_load_telemetry_summary(self):
        root = WORKSPACE_TEMP_ROOT / f"telemetry-{uuid.uuid4().hex[:8]}"
        root.mkdir(parents=True, exist_ok=True)
        store = StateStore(str(root))
        store.write_telemetry_summary("job-1", {"metrics": {"step_count": 3}})
        loaded = store.load_telemetry_summary("job-1")
        self.assertEqual(loaded["metrics"]["step_count"], 3)

    def test_semantic_memory_search_returns_scored_hits(self):
        root = WORKSPACE_TEMP_ROOT / f"memory-{uuid.uuid4().hex[:8]}"
        root.mkdir(parents=True, exist_ok=True)
        memory = MemoryManager(str(root))
        memory.put_semantic_summary("deploy kubernetes workload", {"kind": "run"})
        hits = memory.search("semantic", "k8s deploy workload", limit=3)
        self.assertTrue(hits)
        self.assertIn("score", hits[0])


if __name__ == "__main__":
    unittest.main()
