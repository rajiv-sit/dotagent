# FAQ - Frequently Asked Questions

## Project Structure & Documentation

### Q: Can I skip some root docs (like DD.md) if we're a small team?

**A:** Yes, adjust for your team size:

| Team Size | Keep | Skip |
|-----------|------|------|
| **Solo** | CONTEXT.md, PLAN.md, Requirement.md, Architecture.md | DD.md, HLD.md, milestone.md (optional) |
| **2-3 people** | + HLD.md, milestone.md | DD.md (if not complex) |
| **4-10 people** | All 7 docs | None |
| **10+ people** | All 7 docs + custom docs | None |

**Rule of thumb:** If you can describe the system in 30 minutes verbally, you can skip DD.md. If implementation details matter (algorithms, error codes, performance constraints), include DD.md.

---

### Q: Should I put rules in `.codex/rules/` or somewhere else?

**A:** Use `.codex/rules/` for project rules that Codex reads.

- **In `.codex/rules/`:** Project coding standards, test requirements, security rules
- **Elsewhere:** Team handbook, onboarding guide, legal/compliance docs
- **Both:** Standards that are both Codex-actionable AND team-readable (e.g., "Use pytest" is both)

If a rule needs human explanation beyond what Codex needs, put the full guide elsewhere and reference it from `.codex/rules/`:

```markdown
# .codex/rules/python.md

Use pytest. See team handbook: [Python Testing Standards](../handbook/python-testing.md)
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
- Update PLAN.md before asking Codex for a new task
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

### Q: Can I use dotcodex with GitHub Copilot Chat (not local Codex)?

**A:** Partially, but not optimally:

**What works:**
- Copy rules from `.codex/rules/` into Copilot Chat messages (manually)
- Reference CONTEXT.md, PLAN.md, Requirement.md in prompts
- Use task.md and review.md templates as prompts

**What doesn't work:**
- Hooks (GitHub Copilot Chat doesn't have hook system)
- Automatic AGENTS.md reading (you must copy rules into chat)
- Session-start context (no persistent session data)

**Recommendation:** 
- If you have local Codex available, use that (hooks + AGENTS.md reading save tokens)
- If GitHub Copilot Chat only, create a "rules summary" file you paste into each chat:
  ```
  [Copy .codex/rules/ files into a Copilot Chat startup prompt]
  ```

---

## Workflow & Execution

### Q: How do I onboard a new team member to a dotcodex project?

**A:** Give them this checklist:

```markdown
# Onboarding Checklist

## Read These First (15 minutes)

1. Open CONTEXT.md
2. Open PLAN.md
3. Open Architecture.md
4. Open current milestone.md

## Understand the Workflow (15 minutes)

1. Read [Quick Start > Minimal Ongoing Workflow](quick-start.md#minimal-ongoing-workflow)
2. Watch/ask for demo of "ask Codex for a task"

## Set Up Your Environment (30 minutes)

1. Clone/pull the repo
2. Set up per development environment (install deps, build, test)
3. Verify Codex is working: `@codex What's in CONTEXT.md?`
4. Run one task with Codex to show how it works

## You're Ready! (Done)

Ask lead which task to pick from PLAN.md Next section.
```

---

### Q: Can I use dotcodex incrementally? (e.g., rules only, no design docs)

**A:** Yes. Maturity levels:

| Level | Use | Benefit |
|-------|-----|---------|
| **Rules only** | `.codex/rules/` without root docs | Enforce code standards without doc burden |
| **Rules + PLAN** | Add PLAN.md | Track what you're working on |
| **Rules + PLAN + Design** | Add all root docs | Full architecture as code |

**Typical progression:**
1. Install dotcodex (get rules into .codex/)
2. Fill CONTEXT.md (capture decisions)
3. Fill PLAN.md (track work)
4. Add Requirement.md (define what you're building)
5. Add Architecture.md (design the system)
6. Add HLD.md (module boundaries)
7. Add DD.md (implementation details)
8. Add milestone.md (break into milestones)

You don't have to do all at once.

---

### Q: What if we have conflicting opinions on rules?

**A:** Document the decision and the exception:

```markdown
# .codex/rules/code-quality.md

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

### Q: Codex ignores my custom rule. Why?

**A:** Check in this order:

1. Is the rule in `.codex/rules/my-rule.md`?
2. Is `my-rule.md` listed in AGENTS.md under "Rules"?
3. Does the rule have valid markdown syntax?
4. Did you restart Codex or reload VS Code?
5. Is the rule name specific enough? (e.g., "use pytest" not "write tests")

If still ignored, ask Codex:
```
Why aren't you following .codex/rules/my-rule.md?
```

Codex will explain if it's using a different rule instead.

---

### Q: Can rules reference external URLs or files?

**A:** Yes, use markdown links:

```markdown
# .codex/rules/security.md

For detailed security guidelines, see [OWASP Top 10](https://owasp.org/www-project-top-ten/).

For project-specific security checklists, see [security-checklist.md](../security-checklist.md).
```

Codex will see these references, but will only follow them if the file is in the project.

---

### Q: How do I know if Codex is following MY rules or generic dotcodex rules?

**A:** Ask Codex directly:

```
You just implemented error handling. Which rule from .codex/rules/ guided you?
```

Codex will cite the rule. If it's wrong, it may be:
1. Using a more-specific rule you forgot about
2. Using a generic rule because your custom rule isn't working
3. Making a judgment call because the situation wasn't covered

---

## Integrations & Advanced

### Q: Can we enforce dotcodex rules in CI/CD?

**A:** Yes. See [GitHub Actions Integration](github-actions-integration.md) for examples:
- Lint check that verifies CONTEXT.md exists
- Test check that verifies coverage meets testing.md requirements
- Pre-merge check that PLAN.md was updated

---

### Q: Can multiple teams share rules?

**A:** Yes. See [Customize for Your Stack > Multi-Team Governance](customize-for-your-stack.md#keeping-rules-dry-across-teams).

Common pattern:
```
shared-dotcodex/
├── rules/
│   ├── code-quality.md
│   ├── security.md
│   └── logging.md

team-a-project/
├── .codex/
│   └── rules/
│       ├── [symlink to shared/rules/code-quality.md]
│       ├── [symlink to shared/rules/security.md]
│       └── python.md (team A specific)
```

---

### Q: Can we use dotcodex with Jira?

**A:** Not automatically, but manually:

- Jira issues → items in PLAN.md Next section
- PLAN.md Completed → Jira resolved/closed
- CONTEXT.md decisions → Jira decision link in issue description
- milestone.md → Jira epic

No built-in sync (would require custom script), but manual sync is straightforward.

---

### Q: Can we publish Architecture.md or Requirement.md to Confluence?

**A:** Yes, manually:

1. Export markdown to HTML or Confluence format
2. Upload to Confluence
3. Keep markdown as source of truth (Confluence as read-only mirror)

Or use a tool like [Portkey](https://portkey.cloud/) or [Obsidian Publish](https://obsidian.md/publish) to auto-sync.

---

## Troubleshooting Questions

### Q: "AGENTS.md is present but Codex doesn't read it"

**A:** See [Troubleshooting > Issue: AGENTS.md Not Found](troubleshooting.md#issue-agentsmd-not-found-or-codex-ignores-project-rules)

Quick check:
```powershell
cat .\AGENTS.md | head -10
# Should show "## Default Agent" or "## Project Instructions"

ls .codex/agents/ | Measure-Object
# Should show agent files (default-agent.md, etc.)
```

---

### Q: "I updated a rule but Codex doesn't follow it"

**A:** Rules might be cached. Try:

1. Restart VS Code or reload Codex chat
2. Paste the rule directly into your prompt:
   ```
   Here's updated rule: [paste rule content]
   ```
3. Ask Codex to re-read it:
   ```
   Re-read .codex/rules/my-rule.md and confirm you understand it.
   ```

---

### Q: "Graphify context isn't being used even though GRAPH_REPORT.md exists"

**A:** Verify hooks are working:

```powershell
powershell -ExecutionPolicy Bypass -File .\.codex\hooks\graph-staleness.ps1
# Should output a message about graphify availability
```

If no output, see [Troubleshooting > Hooks Not Firing](troubleshooting.md#issue-hooks-not-firing-session-start-pre-bash-context-etc).

---

## More Help

- Not sure where to start? → [Navigation Hub](index.md)
- Setting up your first project? → [Quick Start](quick-start.md)
- Moving existing project to dotcodex? → [Migration Guide](migration-guide.md)
- Still stuck? → [Troubleshooting](troubleshooting.md)
