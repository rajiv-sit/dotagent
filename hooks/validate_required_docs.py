from pathlib import Path

REQUIRED = ["AGENTS.md", "CONTEXT.md", "PLAN.md", "Requirement.md", "Architecture.md", "HLD.md", "DD.md", "milestone.md"]

def run(project_root: str) -> list[str]:
    root = Path(project_root)
    missing = [name for name in REQUIRED if not (root / name).exists()]
    return missing
