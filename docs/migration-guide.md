# Migration Guide: Adopt dotagent in Existing Projects

If you have an existing project with docs, code standards, or design artifacts, this guide shows how to adopt dotagent incrementally.

## Overview

You don't have to rewrite everything. Adopt dotagent in phases:

1. **Phase 1 (Week 1):** Install dotagent, inventory existing docs
2. **Phase 2 (Week 2):** Map existing docs to dotagent structure
3. **Phase 3 (Week 3):** Fill gaps and consolidate
4. **Phase 4 (Ongoing):** Use dotagent for new work

---

## Phase 1: Install & Inventory (30 minutes)

### Step 1: Install dotagent

```powershell
cd your-project-root
git clone https://github.com/rajiv-sit/dotagent.git .\dotagent
powershell -ExecutionPolicy Bypass -File .\dotagent\scripts\install-dotagent.ps1 -ProjectRoot .
```

Result: `.agent/` folder with rules, hooks, agents, scripts.

### Step 2: Inventory What You Have

List all existing documentation:

```powershell
# Find markdown files
Get-ChildItem -Recurse -Include *.md | Select-Object FullName

# Find design/architecture docs
Get-ChildItem -Path . -Include "README*", "DESIGN*", "ARCHITECTURE*", "API*" -Recurse
```

Create a file `_MIGRATION_INVENTORY.md`:

```markdown
# Existing Documentation

## Design & Architecture
- [ ] design/ folder
  - [ ] system-overview.md
  - [ ] api.md
  - [ ] database.md
- [ ] docs/ folder
  - [ ] setup.md
  - [ ] contributing.md
- [ ] README.md (general project info)

## Code Standards & Rules
- [ ] .eslintrc.json (linting)
- [ ] CODE_OF_CONDUCT.md
- [ ] CONTRIBUTING.md (pull request guide)

## Team Knowledge
- [ ] Wiki (GitHub, Confluence, Notion)
- [ ] Decisions log
- [ ] Meeting notes (teams, recorded)

## Version Control
- [ ] Previous CONTEXT files (anywhere)
- [ ] Decision records (ADRs)

---

# Mapping Plan

Link each existing doc to a dotagent doc:

| Existing Doc | Maps To | Action |
|--------------|---------|--------|
| design/system-overview.md | docs/design/Architecture.md | Copy content, adapt format |
| docs/api.md | docs/design/Requirement.md (API section) | Include as reference |
| CODE_OF_CONDUCT.md | (Keep separate) | Reference from AGENTS.md |
```

---

## Phase 2: Map & Choose Strategy (1 hour)

### Option A: Copy & Consolidate to dotagent Structure

Best if: You have 2-5 scattered docs that should be consolidated.

**Strategy:**
1. Copy content from existing docs to corresponding dotagent docs
2. Delete redundant docs (keep one source of truth)
3. Update all internal links

**Example:**

**Before:**
```
docs/
|-- architecture/
|   |-- overview.md
|   |-- database.md
|   `-- api.md
|-- contributing.md
`-- setup.md
```

**After:**
```
docs/design/Architecture.md (combines overview + database sections)
docs/design/Requirement.md (API section from api.md)
contributing.md (stays as-is, referenced from AGENTS.md)
README.md (setup guide, kept)
```

---

### Option B: Keep Existing Docs, Reference from dotagent

Best if: Your existing docs are detailed and would be painful to migrate.

**Strategy:**
1. Create brief dotagent docs under `docs/design/` (Requirement.md, Architecture.md, etc.)
2. Link to detailed docs elsewhere
3. Gradually migrate content over time

**Example:**

```markdown
# docs/design/Requirement.md

See detailed spec in your project's docs/requirements-full.md

## Quick Overview

- System provides X, Y, Z
- Users are A, B, C
- Performance targets: response < 200ms

For complete requirements, see your detailed specifications document.
```

---

### Option C: Hybrid (Recommended for Teams)

**Strategy:**
1. Create lightweight dotagent structure under `docs/design/` (Architecture.md, etc.)
2. Link to existing detailed docs
3. Gradually adopt dotagent as you refactor
4. Migrate 10-20% per sprint

**Example:**

```
docs/design/Architecture.md
|-- Brief system overview
`-- Link to detailed design wiki (if you have one)

HLD.md
|-- Modules overview
`-- Link to module specs (if you have detailed module documentation)

Contributing.md
|-- Code standards summary
`-- Link to style guide (if you have a separate style guide)
```

---

## Phase 3: Fill In Dotagent Docs (1-2 hours)

### Minimum Viable Content

Create these (others can be expanded later):

```markdown
# CONTEXT.md

## Project

Name: [Your Project]
Purpose: [One-sentence description]

## Architecture Snapshot

[3-sentence overview of system shape]

## Key Decisions

[Copy from existing decision log or ADRs]

## Linked Docs

- `docs/design/Requirement.md`
- `docs/design/Architecture.md`
- `PLAN.md`

---

# PLAN.md

## Current Objective

[What are you working on this sprint/month?]

## Completed

- Project bootstrap
- Dotagent migration
- [Any other finished work]

## In Progress

[Current work]

## Next

[Prioritized backlog items]

---

# docs/design/Requirement.md

## Overview

**Purpose:** [What does the system do?]

**Scope:** [What's included? What's explicitly NOT included?]

## Key Features

1. [Feature A]
2. [Feature B]

## Non-Functional Requirements

- Performance: [target]
- Scalability: [target]
- Reliability: [target]

---

# docs/design/Architecture.md

## Overview

[Paragraph describing system components and flow]

## Components

- **Component A:** [responsibility]
- **Component B:** [responsibility]

## Technology Stack

- Language: [language]
- Frameworks: [frameworks]
- Database: [db]

## Key Decisions

1. [Why did you choose X over Y?]
```

### Filling From Existing Docs

If you have existing docs:

1. Copy the relevant sections
2. Reformat to dotagent section names
3. Keep original doc as reference or archive

Example:
```
# Old: docs/api-design.md (section "Request/Response")
-> # New: docs/design/Requirement.md (section "API Contract")

# Old: design/decisions.txt (line "Use Redis for caching")
-> # New: CONTEXT.md (section "Key Decisions")
```

---

## Phase 4: Set Up Rules (30 minutes)

### Keep Existing Standards

Don't create new standards. Map existing ones to `.agent/rules/`:

**If you have:**
- ESLint config -> Create `.agent/rules/javascript.md` that references it
- Python style guide -> Create `.agent/rules/python.md` that references it
- Security checklist -> Create `.agent/rules/security.md` that includes items

**Example:**

```markdown
# .agent/rules/javascript.md

## Style & Quality

Follow your project's ESLint config and Prettier configuration.

- Use `npm run lint` before committing
- Use `npm run format` to auto-fix
- No `any` types in TypeScript

## Testing

- Use Jest; organize in tests/ mirroring src/
- Target 80%+ coverage

## See Also

- Your Contributing Guide
- Your API Guidelines documentation
```

---

## Phase 5: Ongoing Adoption (Per Sprint)

After migration, use dotagent for all new work:

1. **Start of sprint:** Ask Agent to read CONTEXT.md, PLAN.md, docs/design/Requirement.md, docs/design/Architecture.md
2. **During sprint:** Use Agent with your rules for implementation
3. **End of sprint:** Update PLAN.md and CONTEXT.md with completion + new decisions

---

## Common Migration Scenarios

### Scenario 1: Wiki + Scattered Docs

**Before:**
- GitHub Wiki (design docs)
- Notion (team notes)
- ADR files (decision records)
- README.md (project overview)
- docs/ folder (contributing guide)

**After:**
```
docs/design/Architecture.md -> [Condensed from GitHub Wiki]
CONTEXT.md     -> [Decisions from ADR files]
README.md      -> [Keep as-is or link to quick-start.md]
CONTRIBUTING   -> [Keep as-is, referenced from AGENTS.md]
```

### Scenario 2: Heavy Design Docs

**Before:**
- Very detailed Architecture Doc (50 pages, in PDF or Confluence)
- UML diagrams
- API specifications (OpenAPI)
- Database schema docs

**After Strategy:**
- docs/design/Architecture.md: Link to detailed docs (don't migrate)
- docs/design/Requirement.md: Include API contracts (extract from OpenAPI)
- docs/design/HLD.md: Add if you break into 5+ modules
- Keep PDFs/UML as reference; point to them from dotagent docs

### Scenario 3: No Existing Docs

**Before:**
- Just code
- Slack discussions of decisions

**After Strategy:**
Same as [Quick Start](quick-start.md) - you're starting fresh, no migration needed.

---

## Migration Checklist

Use this to track progress:

```markdown
# Dotagent Migration Checklist

## Phase 1: Install
- [ ] Run install-dotagent.ps1
- [ ] Verify .agent/ folder created
- [ ] Create _MIGRATION_INVENTORY.md

## Phase 2: Map & Plan
- [ ] List all existing docs
- [ ] Choose strategy (A, B, or C)
- [ ] Identify what maps to what

## Phase 3: Create Dotagent Docs
- [ ] Create CONTEXT.md (minimal)
- [ ] Create PLAN.md (minimal)
- [ ] Create docs/design/Requirement.md (minimal)
- [ ] Create docs/design/Architecture.md (minimal)
- [ ] Create other docs/design files as needed

## Phase 4: Set Up Rules
- [ ] Map existing code standards to .agent/rules/
- [ ] Create stack-specific rules (python.md, typescript.md, etc.)
- [ ] Update AGENTS.md to list rules

## Phase 5: Verify
- [ ] Ask Agent: "What's in CONTEXT.md?"
- [ ] Agent reads AGENTS.md without errors
- [ ] Run first task with Agent using new rules

## Post-Migration
- [ ] Archive or delete old docs (or mark as deprecated with links)
- [ ] Add migration notes to README ("Docs moved to CONTEXT.md, etc.")
- [ ] Train team on new workflow (quick demo)
```

---

## Rollback Strategy

If migration causes problems:

1. **Keep git branch:** Before starting, create branch:
   ```powershell
   git checkout -b dotagent-migration
   # Work on migration...
   # If it fails, git reset --hard origin/main
   ```

2. **Keep old docs:** Don't delete old docs immediately:
   ```
   docs.deprecated/
   `-- architecture-old.md (has "# DEPRECATED - See docs/design/Architecture.md instead")
   ```

3. **Gradual switch:** You don't have to switch everything at once. Start with CONTEXT.md + PLAN.md, keep everything else as-is.

---

## FAQ on Migration

### Q: Will migration break anything?

**A:** No if you keep old docs and link from new ones. Gradual migration is safest.

### Q: How long does migration take?

**A:** 
- Small project (1-5 docs): 1-2 hours
- Medium project (10-20 docs): 4-8 hours
- Large project (50+ docs spread across teams): 1-2 days

### Q: Do we need to migrate RIGHT NOW?

**A:** No. You can start using dotagent incrementally. Start with rules + PLAN, add design docs later.

### Q: Can we keep the old docs?

**A:** Yes! Link from dotagent docs to them. Gradually migrate content over sprints.

### Q: What if we have 20 conflicting architecture docs?

**A:** This is the real value of migration. Create ONE `docs/design/Architecture.md` that references the others, then gradually consolidate. Use this as a chance to clean up.

---

## Next Steps

- [Quick Start](quick-start.md) - Learn the minimal workflow
- [FAQ](faq.md) - Answers to common questions
- [Customize for Your Stack](customize-for-your-stack.md) - Set up rules for your language
- [Navigation Hub](index.md) - Find the guide you need


