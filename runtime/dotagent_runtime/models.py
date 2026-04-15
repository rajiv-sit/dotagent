from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


@dataclass
class Step:
    id: str
    name: str
    kind: str
    status: str = "PENDING"
    depends_on: List[str] = field(default_factory=list)
    tool: Optional[str] = None
    payload: Dict[str, Any] = field(default_factory=dict)
    max_attempts: int = 1
    attempts: int = 0
    acceptance: Dict[str, Any] = field(default_factory=dict)
    last_error: Optional[str] = None
    priority: int = 100
    agent_role: str = "executor"
    execution_target: str = "local"
    parallel_group: Optional[str] = None


@dataclass
class Plan:
    id: str
    goal: str
    steps: List[Step]
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["steps"] = [asdict(step) for step in self.steps]
        return data


@dataclass
class Job:
    id: str
    type: str
    status: str
    created_at: str
    updated_at: str
    input: Dict[str, Any]
    output: Optional[Dict[str, Any]]
    metadata: Dict[str, Any]

    @classmethod
    def create(
        cls,
        job_type: str,
        user_input: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "Job":
        now = utc_now()
        return cls(
            id=new_id(job_type),
            type=job_type,
            status="PENDING",
            created_at=now,
            updated_at=now,
            input=user_input,
            output=None,
            metadata=metadata or {},
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ValidationResult:
    status: str
    summary: str
    checks: List[Dict[str, Any]]
    corrective_actions: List[str] = field(default_factory=list)
    retryable: bool = False


@dataclass
class ExecutionResult:
    step_id: str
    tool: str
    ok: bool
    output: Dict[str, Any]
    started_at: str
    ended_at: str
    attempt: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)
