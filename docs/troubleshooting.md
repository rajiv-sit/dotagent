# Troubleshooting Guide

Common issues and solutions when using dotcodex.

## Installation & Setup

### Issue: "AGENTS.md not found" or Codex ignores project rules

**Causes:**
1. Install script didn't run or failed silently
2. AGENTS.md is in the wrong location
3. Codex isn't reading project-local config

**Solution:**

1. Verify `.codex/` was created:
   ```powershell
   ls -Recurse .codex | head -20
   ```
   Should show `.codex/agents/`, `.codex/hooks/`, `.codex/rules/`, etc.

2. Verify AGENTS.md exists in project root:
   ```powershell
   cat .\AGENTS.md | head -10
   ```
   Should contain `## Default Agent` section.

3. Re-run the installer:
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\dotcodex\scripts\install-dotcodex.ps1 -ProjectRoot . -Force
   ```

4. Restart Codex or reload the workspace in VS Code.

---

### Issue: "Scripts don't execute" or PowerShell permission denied

**Cause:** ExecutionPolicy blocks script execution.

**Solution:**

```powershell
# Check current policy
Get-ExecutionPolicy

# If Restricted, temporarily bypass:
powershell -ExecutionPolicy Bypass -File .\dotcodex\scripts\install-dotcodex.ps1 -ProjectRoot .

# Or permanently allow (requires admin):
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

### Issue: "Project docs weren't created" (Requirement.md, Architecture.md, etc. missing)

**Cause:** `init-project-docs.ps1` didn't run or failed.

**Solution:**

```powershell
# Check if .codex/scripts/init-project-docs.ps1 exists
ls .codex/scripts/init-project-docs.ps1

# Re-run it
powershell -ExecutionPolicy Bypass -File .\.codex\scripts\init-project-docs.ps1 -ProjectRoot .

# Verify docs were created
ls Requirement.md Architecture.md HLD.md DD.md milestone.md
```

If script is missing, copy it from dotcodex:
```powershell
copy .\dotcodex\scripts\init-project-docs.ps1 .\.codex\scripts\
```

---

## Rules & Validation

### Issue: Codex ignores rules in `.codex/rules/`

**Causes:**
1. Rules file has syntax errors
2. Rules aren't listed in AGENTS.md
3. Codex isn't reading AGENTS.md

**Solution:**

1. Verify rule file syntax (use a JSON/YAML validator if rule has frontmatter):
   ```powershell
   cat .\.codex\rules\code-quality.md | head -20
   ```
   Should be readable markdown.

2. Verify AGENTS.md lists the rule:
   ```powershell
   cat .\AGENTS.md | Select-String "code-quality"
   ```
   Should output: `- `.codex/rules/code-quality.md``

3. If a custom rule was added, verify it's in AGENTS.md:
   ```markdown
   ## Rules

   When present, follow:

   - `.codex/rules/code-quality.md`
   - `.codex/rules/testing.md`
   - `.codex/rules/my-custom-rule.md`  # <-- Did you add this?
   ```

4. Verify dotcodex rules weren't accidentally deleted:
   ```powershell
   ls .codex/rules/ | measure
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

Then alert Codex to the clarification in AGENTS.md or directly in the task prompt.

---

### Issue: "Codex doesn't follow testing rules" (skips tests, poor coverage)

**Causes:**
1. Testing rule isn't listed in AGENTS.md
2. Testing rule is vague or incomplete
3. Codex is using a different agent profile

**Solution:**

1. Verify `.codex/rules/testing.md` exists and is comprehensive:
   ```markdown
   # Testing

   - Add or update tests for behavior changes.
   - Prefer unit tests for local logic and integration tests for module boundaries.
   - Validate happy path, edge cases, and failure paths.
   - Do not advance milestones with failing validation.
   - Record important manual verification when automated tests are not yet available.
   ```

2. Add stack-specific test rule (e.g., `.codex/rules/pytest.md` for Python):
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
   - `.codex/rules/testing.md`
   - `.codex/rules/pytest.md`
   ```

4. Ask Codex explicitly to use the `test-writer` skill:
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
3. Codex hook system isn't initialized

**Solution:**

1. Verify hooks.json is valid JSON:
   ```powershell
   $json = Get-Content .\.codex\hooks.json | ConvertFrom-Json
   # If this throws an error, JSON is invalid
   ```

2. Verify hook paths exist:
   ```powershell
   ls .codex/hooks/*.ps1
   ```
   Should show: session-start.ps1, pre-bash-context.ps1, doc-presence.ps1, path-guard.ps1, graph-staleness.ps1

3. Test a hook manually:
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\.codex\hooks\session-start.ps1
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
               "command": "powershell -ExecutionPolicy Bypass -File .\\.codex\\hooks\\session-start.ps1"
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

**Cause:** Codex hook system is enabled but not firing.

**Solution:**

1. Verify you're using Codex (not GitHub Copilot Chat alone):
   ```
   @codex What's in CONTEXT.md?
   ```

2. Restart VS Code or Codex chat window.

3. If using API mode, verify hooks are configured in your Codex setup.

---

## Documentation & Context

### Issue: "Codex asks me to create Requirement.md when it already exists"

**Causes:**
1. Root doc paths incorrect in AGENTS.md
2. Doc is in `.codex/` instead of project root
3. Codex is using wrong agent profile

**Solution:**

1. Verify root docs are in project root, not `.codex/`:
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
   - `.codex/CONTEXT.md`
   - `.codex/rules/CONTEXT.md`
   ```

3. Verify docs aren't empty or only whitespace:
   ```powershell
   cat Requirement.md | Measure-Object -Line
   ```
   Should show >0 lines of actual content.

---

### Issue: "CONTEXT.md or PLAN.md is stale or never gets updated"

**Cause:** Codex updates files but they're not persisted or you're not asking for updates.

**Solution:**

1. After each task, explicitly ask Codex:
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
   - Updated PLAN.md with completion ✓
   - Updated CONTEXT.md with decisions ✓
   ```

---

### Issue: "graphify output exists but Codex doesn't prefer it"

**Causes:**
1. Hook that checks for graphify isn't running
2. graphify-out path is wrong
3. Codex doesn't see the GRAPH_REPORT.md file

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
   powershell -ExecutionPolicy Bypass -File .\.codex\hooks\graph-staleness.ps1
   ```
   Should output a message if the graph is stale.

4. Ask Codex explicitly to use graphify:
   ```
   Use graphify-out/GRAPH_REPORT.md as your source for architecture context.
   ```

---

## Performance & Token Usage

### Issue: "Codex spends too many tokens exploring the codebase"

**Causes:**
1. graphify output missing (hooks warn but aren't stopping exploration)
2. path-guard hook isn't preventing broad searches
3. Rules or docs incomplete (Codex explores to fill gaps)

**Solution:**

1. Generate graphify output:
   ```powershell
   graphify .
   ```

2. Verify path-guard hook runs before bash/terminal commands:
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\.codex\hooks\path-guard.ps1
   ```
   Should warn about broad file exploration.

3. Complete root design docs (Requirement.md, Architecture.md) so Codex doesn't need to infer.

4. Add a hook to AGENTS.md:
   ```markdown
   ## Guardrails

   - Prefer `.codex/` local files and root docs over broad searches.
   - If graphify-out/GRAPH_REPORT.md exists, use it instead of grepping the repo.
   - Ask for missing context instead of exploring whole-repo.
   ```

---

## Multi-Team & Shared Rules

### Issue: "Two teams have conflicting rules"

**Example:** Team A uses Python 3.9; Team B uses Python 3.12.

**Solution:**

1. Create team-specific rules:
   - `.codex/rules/python-team-a.md` (Python 3.9, Django)
   - `.codex/rules/python-team-b.md` (Python 3.12, FastAPI)

2. Each team's AGENTS.md lists only their rules:
   - Team A: references `python-team-a.md`
   - Team B: references `python-team-b.md`

3. Or create a central `team-rules` repo and symlink:
   ```powershell
   New-Item -ItemType SymbolicLink `
     -Path '.codex/rules/team-standards.md' `
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

4. **Ask Codex explicitly:**
   ```
   Why aren't you following rule X from .codex/rules/code-quality.md?
   ```
   Codex will explain its reasoning.

5. **File an issue** on the dotcodex repo if you find a genuine bug.
