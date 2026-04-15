from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List
from .models import utc_now
from .utils import append_jsonl, ensure_dir

@dataclass
class MemoryEntry:
    namespace: str
    text: str
    metadata: Dict[str, str]

class MemoryManager:
    def __init__(self, project_root: str) -> None:
        self.root = ensure_dir(Path(project_root) / ".dotagent-state" / "memory")

    def put(self, entry: MemoryEntry) -> None:
        append_jsonl(self.root / f"{entry.namespace}.jsonl", {
            "time": utc_now(),
            "text": entry.text,
            "metadata": entry.metadata
        })

    def search(self, namespace: str, query: str, limit: int = 5) -> List[Dict[str, str]]:
        path = self.root / f"{namespace}.jsonl"
        if not path.exists():
            return []
        scored = []
        tokens = set(query.lower().split())
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            import json
            item = json.loads(line)
            hay = (item.get("text","") + " " + " ".join(f"{k}:{v}" for k,v in item.get("metadata",{}).items())).lower()
            score = sum(1 for t in tokens if t in hay)
            if score > 0:
                scored.append((score, item))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in scored[:limit]]
