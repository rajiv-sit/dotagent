# Hooks

This folder contains helper scripts used by `.agent/hooks.json`.

## How Hooks Work

Hooks are PowerShell scripts that fire at specific Agent events:
- **SessionStart:** When Agent starts (once per chat session)
- **PreToolUse:** Before Agent uses a specific tool (e.g., Read, Edit, Bash)

Each hook emits a message that Agent sees, guiding its behavior without blocking execution.

## Included Hooks

### session-start.ps1

**When:** Fires once at the start of each Agent session  
**Purpose:** Remind Agent of available context sources  
**Output:** Tells Agent about graphify reports, Obsidian vaults, and design docs

**What it does:**
- Checks if `graphify-out/GRAPH_REPORT.md` exists and reports it
- Checks if project uses Obsidian and reports graph nav capabilities
- Reminds Agent to read operational root docs plus `docs/design/` design docs first

**Why:** Reduces token waste by surfacing available context once instead of Agent rediscovering it each turn.

---

### doc-presence.ps1

**When:** Fires before Agent reads, edits, or writes files  
**Matcher:** Read, Edit, Write tools  
**Purpose:** Surface design documents before broad codebase work  
**Output:** Reminds Agent to read design docs if they exist

**What it does:**
- Checks for docs/design/Requirement.md, docs/design/Architecture.md, docs/design/HLD.md, docs/design/DD.md, docs/design/milestone.md
- If they exist, reminds Agent to read them before implementation

**Why:** Prevents Agent from inferring design from code when design docs already exist.

---

### pre-bash-context.ps1

**When:** Fires before Agent runs shell/bash commands  
**Matcher:** Bash tool  
**Purpose:** Remind Agent to use graphify and Obsidian context instead of exploring  
**Output:** Lists available graph-based and doc-based context sources

**What it does:**
- Lists available graphify-out, GRAPH_REPORT.md, Obsidian vault
- Reminds Agent these are preferred over broad file exploration

**Why:** Shell exploration is token-expensive; guides toward pre-built summaries.

---

### path-guard.ps1

**When:** Fires before Agent runs bash commands  
**Matcher:** Bash tool  
**Purpose:** Warn before broad whole-repo exploration (grep, find, ls '**/...')  
**Output:** Nudges away from inefficient searches

**What it does:**
- Warns if Agent is about to search many files
- Suggests using graphify-out, GRAPH_REPORT.md, or asking directly
- Does NOT block; just reminds

**Why:** Prevents accidental token waste from whole-repo searches when context already exists.

---

### graph-staleness.ps1

**When:** Fires before bash commands that might explore codebase  
**Matcher:** Bash tool  
**Purpose:** Warn if graphify output is older than the source tree  
**Output:** Alerts Agent if graph context may be out of date

**What it does:**
- Checks graphify-out/GRAPH_REPORT.md modification time vs. recent source changes
- If graph is older than 1 week AND code changed recently, warns it may be stale
- Suggests regenerating with `graphify .`

**Why:** Stale graphs lead Agent in wrong directions; warns before proceeding.

---

## Hook Execution Flow

```
Session Starts
    |
    v
SessionStart hooks fire
    |- session-start.ps1: "graphify reports available, design docs exist"
    |
    v
User asks Agent to work on task
    |
    v
Agent reads files
    |- PreToolUse: doc-presence.ps1 -> "Read design docs first"
    |
    v
Agent needs to explore codebase
    |- PreToolUse: pre-bash-context.ps1 -> "Use graphify instead"
    |- PreToolUse: path-guard.ps1 -> "Don't explore whole repo"
    |- PreToolUse: graph-staleness.ps1 -> "Graph may be stale"
    |
    v
Agent makes decision
    |- Uses graphify-out if available
    |- Reads CONTEXT.md instead of exploring
    `- Asks for clarification instead of guessing
```

## Token Reduction Purpose

These hooks save tokens by:

1. **Surfacing context early** (session-start)
   - Graphify reports available? Use them
   - Design docs exist? Read them now instead of inferring

2. **Preventing redundant exploration** (doc-presence, pre-bash-context)
   - Design doc exists? Don't rebuild understanding from code
   - Graphify report exists? Don't grep

3. **Guarding against expensive searches** (path-guard)
   - Whole-repo grep? Suggest graphify instead
   - Repeated file listing? Ask directly instead

4. **Warning about stale context** (graph-staleness)
   - Graph is 2 weeks old but code changed yesterday? Warn before using it

## Hook Configuration

Hooks are registered in `.agent/hooks.json`:

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
    ],
    "PreToolUse": [
      {
        "matcher": "Read|Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "powershell -ExecutionPolicy Bypass -File .\\.agent\\hooks\\doc-presence.ps1"
          }
        ]
      },
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "powershell -ExecutionPolicy Bypass -File .\\.agent\\hooks\\pre-bash-context.ps1"
          },
          {
            "type": "command",
            "command": "powershell -ExecutionPolicy Bypass -File .\\.agent\\hooks\\path-guard.ps1"
          },
          {
            "type": "command",
            "command": "powershell -ExecutionPolicy Bypass -File .\\.agent\\hooks\\graph-staleness.ps1"
          }
        ]
      }
    ]
  }
}
```

- `matcher`: When to fire (tool name or regex; empty = always)
- `type: "command"`: Run a shell command
- `command`: PowerShell path to the hook script

## Customizing Hooks

### Disable a Hook

Comment out the hook in `.agent/hooks.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          // Disabled: too verbose
          // {
          //   "type": "command",
          //   "command": "powershell -ExecutionPolicy Bypass -File .\\.agent\\hooks\\doc-presence.ps1"
          // },
          {
            "type": "command",
            "command": "powershell -ExecutionPolicy Bypass -File .\\.agent\\hooks\\path-guard.ps1"
          }
        ]
      }
    ]
  }
}
```

### Create a Custom Hook

1. Create `.agent/hooks/my-hook.ps1`:
   ```powershell
   # my-hook.ps1
   # Fired before Agent runs tests

   Write-Host "Running tests in CI; check mutation coverage"
   ```

2. Add to `.agent/hooks.json`:
   ```json
   {
     "matcher": "Bash",
     "hooks": [
       {
         "type": "command",
         "command": "powershell -ExecutionPolicy Bypass -File .\\.agent\\hooks\\my-hook.ps1"
       }
     ]
   }
   ```

### Project-Specific Hooks

If you override hooks.json for your project, you can:
- Add team-specific context (e.g., Jira board status)
- Warn about deprecated code areas
- Remind about security-sensitive modules

Example `.agent/hooks/security-boundary.ps1`:

```powershell
# Warn before editing auth or payment modules
$editingSecurityModule = $false
if ($env:VSCODE_CURRENT_FILE -like "*auth*" -or $env:VSCODE_CURRENT_FILE -like "*payment*") {
    $editingSecurityModule = $true
}

if ($editingSecurityModule) {
    Write-Host "WARNING: Editing security-sensitive code. Review against .agent/rules/security.md"
}
```

## Best Practices

- **Keep hooks deterministic:** Same input -> same output
- **Avoid side effects:** Don't modify files or state
- **Keep output concise:** 1-3 lines; Agent will read longer output but it costs tokens
- **Prefer context injection:** Tell Agent what exists rather than running tests/checks
- **Exit cleanly:** Don't fail if a file doesn't exist (just don't report it)

## Troubleshooting Hooks

### Hooks not firing?

1. Verify hooks.json is valid JSON:
   ```powershell
   $hooks = Get-Content .\.agent\hooks.json | ConvertFrom-Json
   ```

2. Verify hook files exist:
   ```powershell
   ls .agent/hooks/*.ps1
   ```

3. Test a hook manually:
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\.agent\hooks\session-start.ps1
   ```

4. Restart Agent or VS Code.

### Hook output not visible?

- Output appears in Agent context, not in terminal
- Check Agent chat history for the hook message
- If using API mode, verify hook system is initialized

### Hook is too verbose?

- Edit the .ps1 file and reduce output to 1 line
- Or disable via hooks.json

See [Troubleshooting](../../../docs/troubleshooting.md) for more help.


