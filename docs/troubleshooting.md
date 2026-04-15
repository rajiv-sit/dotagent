# Troubleshooting Guide

Common issues and solutions when using dotagent.

## Installation & Setup

### Issue: "AGENTS.md not found" or Agent ignores project rules

**Causes:**
1. Install script didn't run or failed silently
2. AGENTS.md is in the wrong location
3. Agent isn't reading project-local config

**Solution:**

1. Verify `.agent/` was created:
   ```powershell
   ls -Recurse .agent | head -20
   ```
   Should show `.agent/agents/`, `.agent/hooks/`, `.agent/rules/`, etc.

2. Verify AGENTS.md exists in project root:
   ```powershell
   cat .\AGENTS.md | head -10
   ```
   Should contain `## Default Agent` section.

3. Re-run the installer:
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\dotagent\scripts\install-dotagent.ps1 -ProjectRoot . -Force
   ```

4. Restart Agent or reload the workspace in VS Code.

---

### Issue: "Scripts don't execute" or PowerShell permission denied

**Cause:** ExecutionPolicy blocks script execution.

**Solution:**

```powershell
# Check current policy
Get-ExecutionPolicy

# If Restricted, temporarily bypass:
powershell -ExecutionPolicy Bypass -File .\dotagent\scripts\install-dotagent.ps1 -ProjectRoot .

# Or permanently allow (requires admin):
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

### Issue: "Project docs weren't created" (Requirement.md, Architecture.md, etc. missing)

**Cause:** `init-project-docs.ps1` didn't run or failed.

**Solution:**

```powershell
# Check if .agent/scripts/init-project-docs.ps1 exists
ls .agent/scripts/init-project-docs.ps1

# Re-run it
powershell -ExecutionPolicy Bypass -File .\.agent\scripts\init-project-docs.ps1 -ProjectRoot .

# Verify docs were created
ls Requirement.md Architecture.md HLD.md DD.md milestone.md
```

If script is missing, copy it from dotagent:
```powershell
copy .\dotagent\scripts\init-project-docs.ps1 .\.agent\scripts\
```

---

## Rules & Validation

### Issue: Agent ignores rules in `.agent/rules/`

**Causes:**
1. Rules file has syntax errors
2. Rules aren't listed in AGENTS.md
3. Agent isn't reading AGENTS.md

**Solution:**

1. Verify rule file syntax (use a JSON/YAML validator if rule has frontmatter):
   ```powershell
   cat .\.agent\rules\code-quality.md | head -20
   ```
   Should be readable markdown.

2. Verify AGENTS.md lists the rule:
   ```powershell
   cat .\AGENTS.md | Select-String "code-quality"
   ```
   Should output: `- `.agent/rules/code-quality.md``

3. If a custom rule was added, verify it's in AGENTS.md:
   ```markdown
   ## Rules

   When present, follow:

   - `.agent/rules/code-quality.md`
   - `.agent/rules/testing.md`
   - `.agent/rules/my-custom-rule.md`  # <-- Did you add this?
   ```

4. Verify dotagent rules weren't accidentally deleted:
   ```powershell
   ls .agent/rules/ | measure
   ```
   Should show at least 6 files (code-quality, testing, security, error-handling, frontend, knowledge-graphs).

---

### Issue: Rules conflict or give contradictory guidance

**Example:** code-quality.md says "keep functions small" but Python-specific rule says "use 50-line functions."

**Solution:**

Add a clarification comment in the more-specific rule:

```markdown
# Python

## Function Length

> **Note:** Generic code-quality.md prefers functions under 30 lines. 
> For Python data processing and ETL functions, 50 lines is acceptable 
> if readability and testability are maintained. This rule supersedes 
> code-quality.md on Python-specific functions only.

- Aim for <50 lines for most functions
- Complex ETL/ML pipelines may exceed 50 lines if well-documented
```

Then alert Agent to the clarification in AGENTS.md or directly in the task prompt.

---

### Issue: "Agent doesn't follow testing rules" (skips tests, poor coverage)

**Causes:**
1. Testing rule isn't listed in AGENTS.md
2. Testing rule is vague or incomplete
3. Agent is using a different agent profile

**Solution:**

1. Verify `.agent/rules/testing.md` exists and is comprehensive:
   ```markdown
   # Testing

   - Add or update tests for behavior changes.
   - Prefer unit tests for local logic and integration tests for module boundaries.
   - Validate happy path, edge cases, and failure paths.
   - Do not advance milestones with failing validation.
   - Record important manual verification when automated tests are not yet available.
   ```

2. Add stack-specific test rule (e.g., `.agent/rules/pytest.md` for Python):
   ```markdown
   # Python Testing (pytest)

   - Use pytest; organize tests in `tests/` mirroring `src/`.
   - Target 80%+ coverage for new code.
   - Use pytest fixtures for shared state.
   - Run `pytest --cov` in CI; fail if coverage drops.
   ```

3. Verify AGENTS.md mentions testing:
   ```markdown
   ## Rules
   - `.agent/rules/testing.md`
   - `.agent/rules/pytest.md`
   ```

4. Ask Agent explicitly to use the `test-writer` skill:
   ```
   Use the test-writer skill to add focused tests for:
   - Happy path
   - Edge cases
   - Error paths
   ```

---

## Hooks & Automation

### Issue: Hooks not firing (session-start, pre-bash-context, etc.)

**Causes:**
1. hooks.json syntax error
2. Hook script doesn't exist or has wrong path
3. Agent hook system isn't initialized

**Solution:**

1. Verify hooks.json is valid JSON:
   ```powershell
   $json = Get-Content .\.agent\hooks.json | ConvertFrom-Json
   # If this throws an error, JSON is invalid
   ```

2. Verify hook paths exist:
   ```powershell
   ls .agent/hooks/*.ps1
   ```
   Should show: session-start.ps1, pre-bash-context.ps1, doc-presence.ps1, path-guard.ps1, graph-staleness.ps1

3. Test a hook manually:
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\.agent\hooks\session-start.ps1
   ```
   Should output a message (example: "Reading graphify context from graphify-out/GRAPH_REPORT.md").

4. Verify hooks.json matches actual hook paths:
   ```json
   {
     "hooks": {
       "SessionStart": [
         {
           "hooks": [
             {
               "type": "command",
               "command": "powershell -ExecutionPolicy Bypass -File .\\.agent\\hooks\\session-start.ps1"
             }
           ]
         }
       ]
     }
   }
   ```
   Paths should use `\\` (escaped backslashes) in JSON.

---

### Issue: "Hook runs but message doesn't appear"

**Cause:** Agent hook system is enabled but not firing.

**Solution:**

1. Verify you're using Agent (not GitHub Copilot Chat alone):
   ```
   @agent What's in CONTEXT.md?
   ```

2. Restart VS Code or Agent chat window.

3. If using API mode, verify hooks are configured in your Agent setup.

---

## Documentation & Context

### Issue: "Agent asks me to create Requirement.md when it already exists"

**Causes:**
1. Root doc paths incorrect in AGENTS.md
2. Doc is in `.agent/` instead of project root
3. Agent is using wrong agent profile

**Solution:**

1. Verify root docs are in project root, not `.agent/`:
   ```powershell
   ls Requirement.md Architecture.md HLD.md DD.md milestone.md
   ```
   Should list files in project root.

2. Verify AGENTS.md doesn't specify full paths:
   ```markdown
   - `CONTEXT.md`
   - `PLAN.md`
   - `Requirement.md`
   # NOT
   - `.agent/CONTEXT.md`
   - `.agent/rules/CONTEXT.md`
   ```

3. Verify docs aren't empty or only whitespace:
   ```powershell
   cat Requirement.md | Measure-Object -Line
   ```
   Should show >0 lines of actual content.

---

### Issue: "CONTEXT.md or PLAN.md is stale or never gets updated"

**Cause:** Agent updates files but they're not persisted or you're not asking for updates.

**Solution:**

1. After each task, explicitly ask Agent:
   ```
   Update PLAN.md and CONTEXT.md with:
   - What was completed
   - Any decisions discovered
   - New risks or constraints
   ```

2. Check that files are writable:
   ```powershell
   (Get-Item PLAN.md).IsReadOnly
   # Should be False
   ```

3. Add a Step to `PLAN.md` to remind yourself:
   ```markdown
   ## Completed (2026-04-12)

   - Implemented auth
   - Updated PLAN.md with completion [PASS]
   - Updated CONTEXT.md with decisions [PASS]
   ```

---

### Issue: "graphify output exists but Agent doesn't prefer it"

**Causes:**
1. Hook that checks for graphify isn't running
2. graphify-out path is wrong
3. Agent doesn't see the GRAPH_REPORT.md file

**Solution:**

1. Verify graphify output exists:
   ```powershell
   ls graphify-out/GRAPH_REPORT.md
   ```
   If missing, run graphify on your repo.

2. Verify the file isn't empty:
   ```powershell
   (Get-Content graphify-out/GRAPH_REPORT.md).Length -gt 100
   # Should be $true
   ```

3. Verify hook `graph-staleness.ps1` runs:
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\.agent\hooks\graph-staleness.ps1
   ```
   Should output a message if the graph is stale.

4. Ask Agent explicitly to use graphify:
   ```
   Use graphify-out/GRAPH_REPORT.md as your source for architecture context.
   ```

---

## Performance & Token Usage

### Issue: "Agent spends too many tokens exploring the codebase"

**Causes:**
1. graphify output missing (hooks warn but aren't stopping exploration)
2. path-guard hook isn't preventing broad searches
3. Rules or docs incomplete (Agent explores to fill gaps)

**Solution:**

1. Generate graphify output:
   ```powershell
   graphify .
   ```

2. Verify path-guard hook runs before bash/terminal commands:
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\.agent\hooks\path-guard.ps1
   ```
   Should warn about broad file exploration.

3. Complete root design docs (Requirement.md, Architecture.md) so Agent doesn't need to infer.

4. Add a hook to AGENTS.md:
   ```markdown
   ## Guardrails

   - Prefer `.agent/` local files and root docs over broad searches.
   - If graphify-out/GRAPH_REPORT.md exists, use it instead of grepping the repo.
   - Ask for missing context instead of exploring whole-repo.
   ```

---

## Multi-Team & Shared Rules

### Issue: "Two teams have conflicting rules"

**Example:** Team A uses Python 3.9; Team B uses Python 3.12.

**Solution:**

1. Create team-specific rules:
   - `.agent/rules/python-team-a.md` (Python 3.9, Django)
   - `.agent/rules/python-team-b.md` (Python 3.12, FastAPI)

2. Each team's AGENTS.md lists only their rules:
   - Team A: references `python-team-a.md`
   - Team B: references `python-team-b.md`

3. Or create a central `team-rules` repo and symlink:
   ```powershell
   New-Item -ItemType SymbolicLink `
     -Path '.agent/rules/team-standards.md' `
     -Target '../../../team-rules/standards.md'
   ```

---

## Getting More Help

1. **Read the main docs:**
   - [Quick Start](quick-start.md)
   - [Customize for Your Stack](customize-for-your-stack.md)
   - [Rule Hierarchy](rule-hierarchy.md)

2. **Check AGENTS.md and rules** in your project for context-specific guidance.

3. **Inspect hook output** to see what warnings or context is being injected.

4. **Ask Agent explicitly:**
   ```
   Why aren't you following rule X from .agent/rules/code-quality.md?
   ```
   Agent will explain its reasoning.

5. **File an issue** on the dotagent repo if you find a genuine bug.


