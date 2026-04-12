# Quick Start Guide

Get a dotcodex project running in 10 minutes.

## Prerequisites

- Windows with PowerShell
- Local `codex` or `codex.cmd` available in your PATH
- Existing Git repo (or create one)

## 5-Minute Setup

### Step 1: Add dotcodex to Your Project

```powershell
cd your-project-root
git clone https://github.com/rajiv-sit/dotcodex.git .\dotcodex
```

Or copy the dotcodex folder manually if you don't have git submodules set up.

### Step 2: Install Project Files

```powershell
powershell -ExecutionPolicy Bypass -File .\dotcodex\scripts\install-dotcodex.ps1 -ProjectRoot .
```

This copies `AGENTS.md`, `CONTEXT.md`, `PLAN.md`, and `.codex/` into your project root.

**Result:** You now have project-local Codex configuration.

### Step 3: Initialize Design Docs

```powershell
powershell -ExecutionPolicy Bypass -File .\.codex\scripts\init-project-docs.ps1 -ProjectRoot .
```

This creates the required root design documents:
- `Requirement.md`
- `Architecture.md`
- `HLD.md`
- `DD.md`
- `milestone.md`

**Result:** Basic document templates ready for your team to fill in.

## Next: Minimal Project Context

Fill in these sections **only** (skip the rest for now):

### CONTEXT.md

```markdown
# CONTEXT

## Project

**Name:** My Project

**Purpose:** What this system does and who it serves.

## Architecture Snapshot

[One-paragraph system overview]

## Linked Docs

- `Requirement.md`
- `Architecture.md`
- `HLD.md`
- `DD.md`
- `PLAN.md`
```

### PLAN.md

```markdown
# PLAN

## Current Objective

[One short statement of what you're working on now]

## Completed

- Project bootstrap
- Dotcodex setup

## In Progress

- Document requirements

## Next

- Implement first feature
- Add tests

### Blockers

None yet.
```

### Requirement.md

```markdown
# Requirement

## Overview

**Purpose:** What the system does.

**Scope:** What's in scope, what's explicitly out.

## Functional Requirements

1. [Feature 1]
2. [Feature 2]

## Non-Functional Requirements

- Performance: [target]
- Scalability: [target]
- Reliability: [target]
```

### Architecture.md

```markdown
# Architecture

## Overview

[One paragraph system shape]

## Components

- **Component 1:** [responsibility]
- **Component 2:** [responsibility]

## Technology Stack

- Language: [language]
- Frameworks: [frameworks]
- Database: [db]
- Deployment: [platform]

## Key Decisions

1. [Decision]: [Rationale]
2. [Decision]: [Rationale]
```

## Your First Task

Now ask Codex to implement something small:

```powershell
# Option 1: Prepare the task (renders prompt to console)
powershell -ExecutionPolicy Bypass -File .\.codex\scripts\dotcodex.ps1 task "Implement basic project structure and build script"

# Option 2: Run it through Codex CLI (requires codex.cmd)
powershell -ExecutionPolicy Bypass -File .\.codex\scripts\dotcodex.ps1 task "Implement basic project structure and build script" -Execute
```

Expected flow:
1. Codex reads your CONTEXT.md, PLAN.md, and Requirement.md
2. Codex implements the feature
3. Codex validates against `.codex/rules/`
4. You review the result
5. Update PLAN.md when done

## After Your First Task

1. Update `PLAN.md`: move item to "Completed" and pick next item
2. Update `CONTEXT.md` if you discovered new constraints or decisions
3. Ask Codex to implement the next milestone

## Common Next Steps

| Goal | Command |
|------|---------|
| **Review a change** | `dotcodex.ps1 review -Target "branch-name vs main"` |
| **Fix a bug** | Ask default-agent to use `debug-fix` skill |
| **Improve code structure** | Ask default-agent to use `refactor` skill |
| **Add tests** | Ask default-agent to use `test-writer` skill |
| **Understand code** | Ask default-agent to use `explain` skill |

## When to Deepen Documentation

After your first 2-3 features:

- **Requirement.md:** Add edge cases, data definitions, failure scenarios
- **Architecture.md:** Add data flow diagrams, rationale for technology choices
- **HLD.md:** Add module boundaries and dependencies
- **DD.md:** Add algorithm details, error handling, complexity analysis
- **milestone.md:** Add specific file modifications and verification steps

## Minimal Ongoing Workflow

Every session:

1. Open `CONTEXT.md` and `PLAN.md` in editor
2. Read the "Current Objective" in PLAN.md
3. Ask Codex to work on one item from PLAN.md → Next
4. After completion, update PLAN.md
5. When a milestone finishes, update CONTEXT.md with new decisions

That's it. Repeat.

## Next: Learn the Agents

When you're ready, learn about specialist agents:

- [When to Use Each Agent](../README.md#when-to-use-each-agent)
- [When to Use Each Skill](../README.md#when-to-use-each-skill)

When stuck, check [Troubleshooting](troubleshooting.md).
