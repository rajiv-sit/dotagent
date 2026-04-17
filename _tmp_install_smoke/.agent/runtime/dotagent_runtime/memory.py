from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List
import json
import math
import re

from .models import utc_now
from .utils import append_jsonl, ensure_dir


TOKEN_RE = re.compile(r"[a-zA-Z0-9_]+")


@dataclass
class MemoryEntry:
    namespace: str
    text: str
    metadata: Dict[str, Any]


class MemoryManager:
    def __init__(self, project_root: str) -> None:
        self.root = ensure_dir(Path(project_root) / ".dotagent-state" / "memory")

    def put(self, entry: MemoryEntry) -> None:
        tokens = self._tokenize(entry.text)
        vector = self._vectorize(tokens)
        append_jsonl(
            self.root / f"{entry.namespace}.jsonl",
            {
                "time": utc_now(),
                "text": entry.text,
                "metadata": entry.metadata,
                "tokens": tokens,
                "vector": vector,
            },
        )

    def search(self, namespace: str, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        path = self.root / f"{namespace}.jsonl"
        if not path.exists():
            return []

        query_tokens = self._tokenize(query)
        query_vector = self._vectorize(query_tokens)
        scored: List[tuple[float, Dict[str, Any]]] = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            item = json.loads(line)
            haystack = (
                item.get("text", "")
                + " "
                + " ".join(f"{k}:{v}" for k, v in item.get("metadata", {}).items())
            ).lower()
            lexical = sum(1 for token in query_tokens if token in haystack)
            semantic = self._cosine_similarity(query_vector, item.get("vector", {}))
            total = lexical + semantic
            if total > 0:
                item["score"] = round(total, 4)
                scored.append((total, item))

        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [item for _, item in scored[:limit]]

    def build_context(self, query: str, limit: int = 5) -> Dict[str, List[Dict[str, Any]]]:
        return {
            "jobs": self.search("jobs", query, limit=limit),
            "runs": self.search("runs", query, limit=limit),
            "semantic": self.search("semantic", query, limit=limit),
        }

    def put_semantic_summary(self, text: str, metadata: Dict[str, Any]) -> None:
        self.put(MemoryEntry(namespace="semantic", text=text, metadata=metadata))

    def put_failure_lesson(self, pattern: str, corrective_action: str, keywords: List[str]) -> None:
        """
        Record a learned lesson from a failure for future adaptive planning.
        
        Args:
            pattern: Description of the failure pattern (e.g., "timeout_on_large_data")
            corrective_action: Recommended action or workaround
            keywords: Relevant keywords to match against future goals
        """
        self.put(MemoryEntry(
            namespace="lessons",
            text=f"{pattern}: {corrective_action}",
            metadata={
                "pattern": pattern,
                "corrective_action": corrective_action,
                "keywords": keywords,
                "learned_at": utc_now(),
            },
        ))

    def get_applicable_lessons(self, goal: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Retrieve lessons learned that might apply to the current goal."""
        return self.search("lessons", goal, limit=limit)

    def put_success_pattern(self, goal_pattern: str, successful_approach: str) -> None:
        """
        Record a successful execution pattern for reuse.
        
        Args:
            goal_pattern: Pattern of goals this approach worked for
            successful_approach: Description of the successful approach
        """
        self.put(MemoryEntry(
            namespace="success_patterns",
            text=goal_pattern,
            metadata={
                "approach": successful_approach,
                "recorded_at": utc_now(),
            },
        ))

    def get_success_patterns(self, goal: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Retrieve similar successful patterns from prior runs."""
        return self.search("success_patterns", goal, limit=limit)

    def _tokenize(self, text: str) -> List[str]:
        return [token.lower() for token in TOKEN_RE.findall(text)]

    def _vectorize(self, tokens: List[str]) -> Dict[str, float]:
        if not tokens:
            return {}
        counts: Dict[str, int] = {}
        for token in tokens:
            counts[token] = counts.get(token, 0) + 1
        norm = math.sqrt(sum(value * value for value in counts.values())) or 1.0
        return {token: value / norm for token, value in counts.items()}

    def _cosine_similarity(self, left: Dict[str, float], right: Dict[str, float]) -> float:
        if not left or not right:
            return 0.0
        shared = set(left).intersection(right)
        return sum(left[token] * right[token] for token in shared)
