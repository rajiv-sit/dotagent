# Obsidian Integration Guide

This guide explains how to use Obsidian with `dotagent` projects for maximum effectiveness.

## Why Obsidian?

Obsidian's graph view and local graph make it easier to navigate cross-linked architecture docs without broad file searches. This reduces token usage and keeps documentation as durable project memory.

## Setup

### 1. Create the Vault

Place your `dotagent` project root as an Obsidian vault:

```
your-project/
|-- .obsidian/              (Obsidian metadata - gitignore this)
|-- AGENTS.md
|-- CONTEXT.md
|-- PLAN.md
|-- Requirement.md
|-- Architecture.md
|-- HLD.md
|-- DD.md
|-- milestone.md
|-- .agent/
|-- dotagent/
|-- src/
`-- ...
```

Open the project root as a vault in Obsidian: `File > Open folder as vault > select project root`

If you want an example starter note, see [obsidian/Welcome.md](../obsidian/Welcome.md).

### 2. Enable Core Plugins

In Obsidian settings:

1. Go to **Settings > Core Plugins**
2. Enable **Graph View** (default: enabled)
3. Enable **Backlinks** (default: enabled)
4. Keep **Quick Switcher** enabled for fast navigation

### 3. Recommended Settings

**Editor:**
- Enable **Strict line breaks** (preserves markdown formatting)
- Enable **Readability** (better line length)

**Graph View:**
- Set **Node size by** -> Links (visually emphasize heavily linked docs)
- Set **Link direction** -> Bidirectional (shows relationships both ways)
- Increase **Link Distance** to 2-3 (show nearby neighbors)

**Display:**
- Set **Vault files as footnotes** (shows file structure)

## Best Practices

### 1. Cross-Link Architecture Docs

In `Requirement.md`:
```markdown
## Related Docs
- [[Architecture.md]] - system design
- [[CONTEXT.md]] - key decisions
```

In `Architecture.md`:
```markdown
## Related Docs
- [[Requirement.md]] - functional/non-functional requirements
- [[HLD.md]] - module boundaries
- [[CONTEXT.md]] - technology choices rationale
```

In `HLD.md`:
```markdown
## Related Docs
- [[Architecture.md]] - system overview
- [[DD.md]] - implementation details
- [[milestone.md]] - current work
```

In `DD.md`:
```markdown
## Related Docs
- [[HLD.md]] - module structure
- [[Architecture.md]] - design constraints
```

In `CONTEXT.md`:
```markdown
## Linked Docs
- [[Requirement.md]] - what we're building
- [[Architecture.md]] - how it's structured
- [[milestone.md]] - what we're doing now
- [[PLAN.md]] - execution status
```

In `PLAN.md`:
```markdown
## Reference
- [[CONTEXT.md]] - durable decisions
- [[milestone.md]] - current objective
```

### 2. Use Local Graph Before Reading Large Docs

When opening a doc in Obsidian:
1. Open **Local Graph** (command: `Open local graph`)
2. See which docs link to this doc and which docs this links to
3. Read the docs in your neighborhood first (prioritize most-linked)
4. Then read the full doc if needed

This reduces rereading and speeds up context gathering.

### 3. Keep Domain Terms in CONTEXT.md

Structure CONTEXT.md with a **Glossary** section:

```markdown
## Glossary

- **Ledger**: immutable record of all transactions
- **Journal Entry**: proposed debit/credit pair
- **Reconciliation**: matching ledger entries to bank statements
- **Accrual**: non-cash revenue or expense
```

Use `[[CONTEXT.md#Glossary]]` backlinks when mentioning terms elsewhere.

### 4. Use Tags for Quick Filtering

Add tags to doc headers:

```markdown
# Architecture.md
#architecture #design #approved

## Components
- API Service #service
- Data Store #infrastructure
```

Then query in Obsidian: search for `tag:#architecture` to see all architecture decisions.

### 5. Track Changes in PLAN.md

Structure PLAN.md to show timeline:

```markdown
## Completed (2026-04-12)
- Auth skeleton
- Database schema
- API routing

## In Progress
- Admin dashboard (started 2026-04-10)

## Next
- Integration tests
- Deployment script

## Blockers
- Wait on OAuth credentials (started 2026-04-08, impact: blocks auth testing)
```

The dated format makes it easy to trace decisions by date in backlinks.

## Graph Navigation Example

Scenario: You need to understand payment flow for a new feature.

1. Open `CONTEXT.md` in Obsidian
2. Open **Local Graph** - see it links to `Architecture.md`, `HLD.md`, and `milestone.md`
3. Click on `Architecture.md` in the graph - open it and see payment flows mentioned
4. Click on `HLD.md` in the graph - see payment module boundary and interdependencies
5. Now you understand the structure without searching; read the relevant sections in those 3 docs

Total context gathered: 3 highly relevant docs instead of grepping the whole repo.

## Obsidian + dotagent Workflow

**Session start:**
1. Open the project vault in Obsidian
2. Open `CONTEXT.md` in one pane
3. Open `PLAN.md` in another pane
4. Open Local Graphs for both to see what's connected
5. Read related architecture docs first (Architecture.md, HLD.md, milestone.md)
6. Then ask Agent to work on the task

**During implementation:**
1. Keep `PLAN.md` open and update it as you progress
2. Read `CONTEXT.md` when decisions are unclear
3. Refer back to architecture docs via backlinks (don't search)
4. Add notes to docs as edge cases or constraints emerge

**After milestone completion:**
1. Update `PLAN.md` with completion status and date
2. Update `CONTEXT.md` with new decisions or risks discovered
3. Add backlinks from `Architecture.md` or `HLD.md` if the design changed

## Gitignore .obsidian/

In `.gitignore`:
```
.obsidian/
!.obsidian/vault.json
```

This keeps personal Obsidian customizations (window state, plugin configs) out of the repo while preserving the vault definition.

## Advanced: Obsidian Templater

If your team uses Obsidian regularly, consider [Obsidian Templater](https://github.com/SilentVoid13/Templater) to auto-generate decision logs:

```markdown
<%* 
let date = tp.date.now("YYYY-MM-DD HH:mm");
%>

## Decision (<%- date %>)

**Decision:** 

**Rationale:** 

**Impact:** 

[[CONTEXT.md#Key Decisions]] | [[Architecture.md]]
```

This ensures all decisions are timestamped and cross-linked automatically.

## Summary

- Obsidian's graph view turns your markdown docs into a navigable knowledge base
- Cross-linking Architecture, HLD, DD, Requirement, and CONTEXT reduces search overhead
- Local Graph shows you the doc neighborhood before reading
- Enables faster decision-finding and reduces context switching
- Pairs well with dotagent's doc-first workflow

