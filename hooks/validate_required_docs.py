from pathlib import Path

REQUIRED = [
    "AGENTS.md",
    "CONTEXT.md",
    "PLAN.md",
    "docs/design/Requirement.md",
    "docs/design/Architecture.md",
    "docs/design/HLD.md",
    "docs/design/DD.md",
    "docs/design/milestone.md",
]

def run(project_root: str) -> list[str]:
    root = Path(project_root)
    missing = [name for name in REQUIRED if not (root / name).exists()]
    return missing
