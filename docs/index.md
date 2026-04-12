# Navigation Hub

Not sure where to start? Use this guide to find the right documentation.

---

## By User Role

### 👨‍💼 I'm a **Project Lead or Architect**

You want to establish project standards and keep the team aligned.

**Start here:**
1. [Quick Start](quick-start.md) (10 min) — Understand what dotcodex provides
2. [Customize for Your Stack](customize-for-your-stack.md) (30 min) — Define team rules
3. [Rule Hierarchy](rule-hierarchy.md) (15 min) — Understand how rules work
4. [CONTEXT.md template](quick-start.md#contextmd) — Set up project memory

**Then:**
- Run [setupdotcodex skill](using-skills.md#setupdotcodex) to document your specific build/test process
- Share [When to Use Each Agent](../README.md#when-to-use-each-agent) with your team

---

### 👨‍💻 I'm a **Developer on an Existing Project**

Your project already has dotcodex installed. You just need to know how to work with it.

**Start here:**
1. Read `CONTEXT.md` (project memory)
2. Read `PLAN.md` (what we're working on)
3. [Quick Start > Minimal Ongoing Workflow](quick-start.md#minimal-ongoing-workflow) (5 min)

**When you get stuck:**
- [Troubleshooting](troubleshooting.md) — Common issues
- [FAQ](faq.md) — Answer-oriented quick reference

**To deepen your skills:**
- [Using Skills](using-skills.md) — How to invoke tdd, debug-fix, refactor, etc.
- [When to Use Each Agent](../README.md#when-to-use-each-agent) — Which specialist to ask for

---

### 🚀 I'm **Starting a New Project**

You're building something from scratch and want to use dotcodex from day one.

**Start here:**
1. [Quick Start](quick-start.md) (10 min) — Install and set up
2. Fill minimal docs (CONTEXT.md, PLAN.md, Requirement.md, Architecture.md)
3. [When to Use Each Skill](../README.md#when-to-use-each-skill) — Understand the workflow
4. Ask Codex to implement your first feature

**After your first feature:**
- [Customize for Your Stack](customize-for-your-stack.md) — Add language-specific rules
- [Rule Hierarchy](rule-hierarchy.md) — Understand rule precedence if conflicts arise

---

### 🏗️ I'm **Migrating an Existing Project** to dotcodex

You have an existing project with docs/standards and want to adopt dotcodex.

**Start here:**
1. [Migration Guide](migration-guide.md) (1-2 hours) — Map your existing docs
2. [Quick Start > 5-Minute Setup](quick-start.md#5-minute-setup) — Install dotcodex
3. Fill required docs (reuse existing content where possible)

**Options:**
- **Option A:** Copy existing docs into dotcodex structure (clean migration)
- **Option B:** Keep existing docs, reference from dotcodex (gradual migration)
- **Option C:** Hybrid — Some consolidated, some referenced (recommended for teams)

---

### 🔍 I'm **Debugging a Problem**

Something isn't working as expected.

**Start here:**
1. [Troubleshooting](troubleshooting.md) — Index of common issues
2. Find your issue in the table of contents
3. If not found, check [FAQ](faq.md) for related questions

**Common problems:**
- [AGENTS.md not found](troubleshooting.md#issue-agentsmd-not-found-or-codex-ignores-project-rules)
- [Rules aren't being followed](troubleshooting.md#issue-codex-ignores-rules-in-codexrules)
- [Hooks not firing](troubleshooting.md#issue-hooks-not-firing-session-start-pre-bash-context-etc)
- [Documentation is stale](troubleshooting.md#issue-contextmd-or-planmd-is-stale-or-never-gets-updated)

---

### 📚 I'm **Learning by Example**

You want to see how dotcodex works in a real project.

**Start here:**
1. [Case Study: Real-World Project](case-study.md) — How a team used dotcodex
2. [Quick Start](quick-start.md) — Minimal template project
3. [Starter Templates](starter-templates.md) — Example docs you can copy

---

### 📖 I'm **Using a Specific Tool or Skill**

You know what you want to do, just need the how-to.

**Skill reference:**
- [Using Skills](using-skills.md) — TDD, debugging, refactoring, explaining, testing

**Agent reference:**
- [When to Use Each Agent](../README.md#when-to-use-each-agent) — Which specialist to ask

**Integration reference:**
- [Obsidian Integration](obsidian-integration.md) — Using Obsidian for docs
- [GitHub Actions Integration](github-actions-integration.md) — CI/CD validation

**Rule reference:**
- [Customize for Your Stack](customize-for-your-stack.md) — Language-specific rules
- [Rule Hierarchy](rule-hierarchy.md) — How rules interact

---

## By Question Type

### 📋 How Do I...?

| Question | Guide |
|----------|-------|
| **Set up a new project?** | [Quick Start](quick-start.md) |
| **Migrate an existing project?** | [Migration Guide](migration-guide.md) |
| **Adopt Obsidian for docs?** | [Obsidian Integration](obsidian-integration.md) |
| **Add GitHub Actions CI?** | [GitHub Actions Integration](github-actions-integration.md) |
| **Create stack-specific rules?** | [Customize for Your Stack](customize-for-your-stack.md) |
| **Use the TDD skill?** | [Using Skills > TDD](using-skills.md#tdd) |
| **Debug a bug?** | [Using Skills > debug-fix](using-skills.md#debug-fix) |
| **Write good tests?** | [Using Skills > test-writer](using-skills.md#test-writer) |
| **Understand code?** | [Using Skills > explain](using-skills.md#explain) |
| **Improve code structure?** | [Using Skills > refactor](using-skills.md#refactor) |
| **Onboard someone new?** | [FAQ > Onboarding](faq.md#q-how-do-i-onboard-a-new-team-member-to-a-dotcodex-project) |

### ❌ What's Wrong?

| Problem | Guide |
|---------|-------|
| **Codex ignores my rules** | [Troubleshooting > Rules Ignored](troubleshooting.md#issue-codex-ignores-rules-in-codexrules) |
| **AGENTS.md not found** | [Troubleshooting > AGENTS.md Missing](troubleshooting.md#issue-agentsmd-not-found) |
| **Hooks won't fire** | [Troubleshooting > Hooks Not Firing](troubleshooting.md#issue-hooks-not-firing) |
| **Documentation is stale** | [Troubleshooting > Stale Docs](troubleshooting.md#issue-contextmd-or-planmd-is-stale) |
| **Scripts won't run** | [Troubleshooting > Scripts Fail](troubleshooting.md#issue-scripts-dont-execute) |
| **Can't find the right doc** | [This page (Navigation Hub)](index.md) |

### ❓ I Have a Question

| Question | Guide |
|----------|-------|
| **Can I skip DD.md?** | [FAQ > Skipping Docs](faq.md#q-can-i-skip-some-root-docs) |
| **How often update PLAN.md?** | [FAQ > Cadence](faq.md#q-how-often-should-we-update-contextmd-and-planmd) |
| **What's the difference between HLD and DD?** | [FAQ > HLD vs DD](faq.md#q-whats-the-difference-between-hld-and-dd) |
| **Can I use GitHub Copilot Chat instead of local Codex?** | [FAQ > GitHub Copilot Chat](faq.md#q-can-i-use-dotcodex-with-github-copilot-chat-not-local-codex) |
| **How do I share rules across teams?** | [Customize for Your Stack > Multi-Team](customize-for-your-stack.md#rules-for-microservices) |
| **Can I enforce rules in CI/CD?** | [GitHub Actions Integration](github-actions-integration.md) |
| **Can Codex ignore a rule for specific code?** | [Rule Hierarchy > Exceptions](rule-hierarchy.md#2-document-exceptions-in-the-specific-rule) |

---

## Reading Paths by Time Available

### ⏱️ I Have 10 Minutes

1. [Quick Start > 5-Minute Setup](quick-start.md#5-minute-setup)
2. [Quick Start > Your First Task](quick-start.md#your-first-task)

### ⏱️ I Have 30 Minutes

1. [Navigation Hub (this page)](index.md) (5 min) — Orient yourself
2. [Quick Start](quick-start.md) (15 min) — Full walkthrough
3. [FAQ](faq.md) (10 min) — Browse common questions

### ⏱️ I Have 1 Hour

1. [Navigation Hub](index.md) (5 min)
2. [Quick Start](quick-start.md) (20 min)
3. [Customize for Your Stack](customize-for-your-stack.md) (20 min)
4. [When to Use Each Agent](../README.md#when-to-use-each-agent) (5 min)
5. [When to Use Each Skill](../README.md#when-to-use-each-skill) (5 min)

### ⏱️ I Have 2+ Hours

1. Full onboarding path:
   - [Navigation Hub](index.md)
   - [Quick Start](quick-start.md)
   - [Customize for Your Stack](customize-for-your-stack.md)
   - [Rule Hierarchy](rule-hierarchy.md)
   - [Using Skills](using-skills.md)
2. Choose specialized guides:
   - [Obsidian Integration](obsidian-integration.md) if you use Obsidian
   - [GitHub Actions](github-actions-integration.md) if you have CI/CD
   - [Migration Guide](migration-guide.md) if migrating from existing project

---

## Complete Guide Index

| Document | Time | For Whom |
|----------|------|----------|
| [Quick Start](quick-start.md) | 10 min | Anyone starting a project |
| [Navigation Hub](index.md) | 5 min | Anyone who's lost |
| [FAQ](faq.md) | 15 min | Anyone with quick questions |
| [Customize for Your Stack](customize-for-your-stack.md) | 30 min | Team leads, architects |
| [Rule Hierarchy](rule-hierarchy.md) | 20 min | Anyone managing rules |
| [Migration Guide](migration-guide.md) | 60 min | Teams adopting dotcodex |
| [Troubleshooting](troubleshooting.md) | As needed | Anyone debugging |
| [Using Skills](using-skills.md) | 20 min | Developers using skills |
| [Obsidian Integration](obsidian-integration.md) | 25 min | Teams using Obsidian |
| [GitHub Actions Integration](github-actions-integration.md) | 30 min | Teams with CI/CD |
| [Case Study](case-study.md) | 15 min | Learning by example |
| [Starter Templates](starter-templates.md) | 10 min | Copying example docs |

---

## Quick Links to Key Sections

**Core Concepts:**
- [What is dotcodex?](../README.md#what-it-is)
- [When to use each agent](../README.md#when-to-use-each-agent)
- [When to use each skill](../README.md#when-to-use-each-skill)

**Getting Started:**
- [5-minute setup](quick-start.md#5-minute-setup)
- [Minimal docs template](quick-start.md#next-minimal-project-context)
- [First task example](quick-start.md#your-first-task)

**Rules & Standards:**
- [Creating stack rules](customize-for-your-stack.md)
- [Rule precedence](rule-hierarchy.md)
- [Multi-team governance](customize-for-your-stack.md#keeping-rules-dry-across-teams)

**Troubleshooting:**
- [Installation issues](troubleshooting.md#installation--setup)
- [Rules not working](troubleshooting.md#rules--validation)
- [Performance issues](troubleshooting.md#performance--token-usage)

---

**Still not sure?** Ask Codex directly:

```
@codex I'm [your role]. Where should I start with dotcodex?
```

Or check the most relevant section above and dive in!
