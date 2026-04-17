# FAQ - Frequently Asked Questions

## Project Structure & Documentation

### Q: Can I skip some design docs (like `docs/design/DD.md`) if we're a small team?

**A:** Yes, adjust for your team size:

| Team Size | Keep | Skip |
|-----------|------|------|
| **Solo** | CONTEXT.md, PLAN.md, docs/design/Requirement.md, docs/design/Architecture.md | docs/design/DD.md, docs/design/HLD.md, docs/design/milestone.md (optional) |
| **2-3 people** | + docs/design/HLD.md, docs/design/milestone.md | docs/design/DD.md (if not complex) |
| **4-10 people** | All 7 docs | None |
| **10+ people** | All 7 docs + custom docs | None |

**Rule of thumb:** If you can describe the system in 30 minutes verbally, you can skip `docs/design/DD.md`. If implementation details matter (algorithms, error codes, performance constraints), include it.

---

### Q: Should I put rules in `.agent/rules/` or somewhere else?

**A:** Use `.agent/rules/` for project rules that your assistant reads.

- **In `.agent/rules/`:** Project coding standards, test requirements, security rules
- **Elsewhere:** Team handbook, onboarding guide, legal/compliance docs
- **Both:** Standards that are both assistant-actionable and team-readable (for example, "Use pytest")

If a rule needs human explanation beyond what the assistant needs, put the full guide elsewhere and reference it from `.agent/rules/`:

```markdown
# .agent/rules/python.md

Use pytest. See team handbook for Python Testing Standards
```

---

### Q: What's the difference between HLD and DD?

**A:** 

| Document | Scope | Readers | Example |
|----------|-------|---------|---------|
| **HLD** (High-Level Design) | Modules and their relationships | Architects, leads, mid-level engineers | "We have Auth Service, User Service, and Billing Service. Auth calls User, Billing calls both." |
| **DD** (Detailed Design) | Classes, algorithms, and error handling within a module | Implementers (developers writing code) | "AuthService.validateToken() uses JWT library X, throws InvalidTokenError on expiry, retries once on timeout." |

**In practice:**
- 1-2 person team: Skip DD, put algorithm details in comments in the code
- 3-5 person team: Light HLD, skip DD unless the code is complex
- 5+ person team: Both (HLD for coordination, DD for onboarding)

---

### Q: How often should we update CONTEXT.md and PLAN.md?

**A:**

- **PLAN.md:** After every milestone completion or when blockers change (weekly or per-sprint)
- **CONTEXT.md:** When a major decision changes, when you discover a risk, or when architecture shifts (monthly or as-needed)

**Minimum cadence:**
- Update PLAN.md before asking your assistant for a new task
- Update CONTEXT.md before starting a new sprint/milestone

**Pattern:**
```markdown
# PLAN.md Update Checklist

After each task:
- [ ] Move completed item to "Completed" section
- [ ] Pick next item from "Next" section
- [ ] Record date completed
- [ ] Update "Blockers" if any changed

Monthly:
- [ ] Review and prune old "Completed" items (keep last 3 months)
- [ ] Review CONTEXT.md for stale decisions
```

---

### Q: Can I use dotagent with Codex, Claude, Copilot, or another assistant?

**A:** Yes, with different levels of automation depending on the tool.

**What works across most assistants:**
- Reference `AGENTS.md`, `CONTEXT.md`, `PLAN.md`, and the design docs in prompts or repo context
- Keep project rules in `.agent/rules/`
- Use task and review templates as reusable prompt inputs

**What may vary by assistant:**
- Hooks: some assistants do not support local hook execution
- Automatic `AGENTS.md` reading: some assistants require you to point them at the files explicitly
- Session persistence: browser or chat-based tools may not preserve local context between sessions

**Recommendation:**
- If you have a local assistant CLI available, use that because it works best with hooks and prepared prompts
- If you use a chat-only assistant, create a "rules summary" file you can paste into each chat:
  ```
  [Copy .agent/rules/ files into a startup prompt]
  ```

---

## Workflow & Execution

### Q: How do I onboard a new team member to a dotagent project?

**A:** Give them this checklist:

```markdown
# Onboarding Checklist

## Read These First (15 minutes)

1. Open CONTEXT.md
2. Open PLAN.md
3. Open docs/design/Architecture.md
4. Open current docs/design/milestone.md

## Understand the Workflow (15 minutes)

1. Read [Quick Start > Minimal Ongoing Workflow](quick-start.md#minimal-ongoing-workflow)
2. Watch or ask for a demo of "ask the assistant for a task"

## Set Up Your Environment (30 minutes)

1. Clone/pull the repo
2. Set up per development environment (install deps, build, test)
3. Verify the assistant is working: `@agent What's in CONTEXT.md?`
4. Run one task with the assistant to show how it works

## You're Ready! (Done)

Ask lead which task to pick from PLAN.md Next section.
```

---

### Q: Can I use dotagent incrementally? (e.g., rules only, no design docs)

**A:** Yes. Maturity levels:

| Level | Use | Benefit |
|-------|-----|---------|
| **Rules only** | `.agent/rules/` without design docs | Enforce code standards without doc burden |
| **Rules + PLAN** | Add PLAN.md | Track what you're working on |
| **Rules + PLAN + Design** | Add `CONTEXT.md`, `PLAN.md`, and `docs/design/` | Full architecture as code |

**Typical progression:**
1. Install dotagent (get rules into .agent/)
2. Fill CONTEXT.md (capture decisions)
3. Fill PLAN.md (track work)
4. Add docs/design/Requirement.md (define what you're building)
5. Add docs/design/Architecture.md (design the system)
6. Add docs/design/HLD.md (module boundaries)
7. Add docs/design/DD.md (implementation details)
8. Add docs/design/milestone.md (break into milestones)

You don't have to do all at once.

---

### Q: What if we have conflicting opinions on rules?

**A:** Document the decision and the exception:

```markdown
# .agent/rules/code-quality.md

Generic: Keep functions under 30 lines.

Team note: We debated this in sprint 5. See decision in CONTEXT.md.
Some functions (data transformations) can reach 40 lines if cohesive.
This is documented in python-specific rule.
```

Then in CONTEXT.md:

```markdown
## Key Decisions

### Function Length (Debated Sprint 5)

- **Decision:** Allow up to 40 lines for Python data transformations
- **Reason:** Splitting cohesive logic harms readability more than 40-line limit helps
- **Impact:** Code reviews should focus on cohesion, not line count
- **Dissenters:** Alice wanted 30-line hard limit; overruled by team consensus
```

This prevents re-debating and shows why the rule exists.

---

## Rules & Validation

### Q: My assistant ignores my custom rule. Why?

**A:** Check in this order:

1. Is the rule in `.agent/rules/my-rule.md`?
2. Is `my-rule.md` listed in AGENTS.md under "Rules"?
3. Does the rule have valid markdown syntax?
4. Did you restart the assistant or reload VS Code?
5. Is the rule name specific enough? (e.g., "use pytest" not "write tests")

If still ignored, ask the assistant:
```
Why aren't you following .agent/rules/my-rule.md?
```

The assistant should explain if it's using a different rule instead.

---

### Q: Can rules reference external URLs or files?

**A:** Yes, use markdown links:

```markdown
# .agent/rules/security.md

For detailed security guidelines, see [OWASP Top 10](https://owasp.org/www-project-top-ten/).

For project-specific security checklists, see security-checklist.md (if your project has one).
```

The assistant will see these references, but will only follow them if the file is in the project.

---

### Q: How do I know if my assistant is following MY rules or generic dotagent rules?

**A:** Ask the assistant directly:

```
You just implemented error handling. Which rule from .agent/rules/ guided you?
```

The assistant will cite the rule. If it's wrong, it may be:
1. Using a more-specific rule you forgot about
2. Using a generic rule because your custom rule isn't working
3. Making a judgment call because the situation wasn't covered

---

## Integrations & Advanced

### Q: Can we enforce dotagent rules in CI/CD?

**A:** Yes. See [GitHub Actions Integration](github-actions-integration.md) for examples:
- Lint check that verifies CONTEXT.md exists
- Test check that verifies coverage meets testing.md requirements
- Pre-merge check that PLAN.md was updated

---

### Q: Can multiple teams share rules?

**A:** Yes. See [Customize for Your Stack > Multi-Team Governance](customize-for-your-stack.md#keeping-rules-dry-across-teams).

Common pattern:
```
shared-dotagent/
|-- rules/
|   |-- code-quality.md
|   |-- security.md
|   `-- logging.md

team-a-project/
`-- .agent/
    `-- rules/
        |-- [symlink to shared/rules/code-quality.md]
        |-- [symlink to shared/rules/security.md]
        `-- python.md (team A specific)
```

---

### Q: Can we use dotagent with Jira?

**A:** Not automatically, but manually:

- Jira issues -> items in PLAN.md Next section
- PLAN.md Completed -> Jira resolved/closed
- CONTEXT.md decisions -> Jira decision link in issue description
- docs/design/milestone.md -> Jira epic

No built-in sync (would require custom script), but manual sync is straightforward.

---

### Q: Can we publish `docs/design/Architecture.md` or `docs/design/Requirement.md` to Confluence?

**A:** Yes, manually:

1. Export markdown to HTML or Confluence format
2. Upload to Confluence
3. Keep markdown as source of truth (Confluence as read-only mirror)

Or use a tool like [Portkey](https://portkey.cloud/) or [Obsidian Publish](https://obsidian.md/publish) to auto-sync.

---

## Troubleshooting Questions

### Q: "AGENTS.md is present but my assistant doesn't read it"

**A:** See [Troubleshooting > Issue: AGENTS.md Not Found](troubleshooting.md#issue-agentsmd-not-found-or-agent-ignores-project-rules)

Quick check:
```powershell
cat .\AGENTS.md | head -10
# Should show "## Default Agent" or "## Project Instructions"

ls .agent/agents/ | Measure-Object
# Should show agent files (default-agent.md, etc.)
```

---

### Q: "I updated a rule but my assistant doesn't follow it"

**A:** Rules might be cached. Try:

1. Restart VS Code or reload the assistant chat
2. Paste the rule directly into your prompt:
   ```
   Here's updated rule: [paste rule content]
   ```
3. Ask the assistant to re-read it:
   ```
   Re-read .agent/rules/my-rule.md and confirm you understand it.
   ```

---

### Q: "Graphify context isn't being used even though GRAPH_REPORT.md exists"

**A:** Verify hooks are working:

```powershell
powershell -ExecutionPolicy Bypass -File .\.agent\hooks\graph-staleness.ps1
# Should output a message about graphify availability
```

If no output, see [Troubleshooting > Hooks Not Firing](troubleshooting.md#issue-hooks-not-firing-session-start-pre-bash-context-etc).

---

## More Help

- Not sure where to start? -> [Navigation Hub](index.md)
- Setting up your first project? -> [Quick Start](quick-start.md)
- Moving existing project to dotagent? -> [Migration Guide](migration-guide.md)
- Still stuck? -> [Troubleshooting](troubleshooting.md)


