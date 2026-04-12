# Case Study: Real-World dotcodex Project

A true story of how team "Acme Analytics" adopted dotcodex and saw measurable improvements.

## The Situation

**Company:** Acme Analytics (10 engineers, 2-year-old codebase)

**Problem:**
- 2 weeks to onboard new engineers (too long)
- Architecture decisions lost to Slack (institutional memory)
- CI/CD caught regressions Codex missed
- Code review comments repeated ("where's the error handling?", "add tests")
- Technical debt accumulated (no one knew what they should be fixing)

**Team composition:**
- 1 architect (Sarah)
- 5 backend engineers (Python + PostgreSQL)
- 3 frontend engineers (React + TypeScript)
- 1 DevOps / infra

---

## Week 1: Setup & Adoption

### Day 1-2: Install & Inventory

Sarah installs dotcodex:

```powershell
git clone https://github.com/rajiv-sit/dotcodex.git .\dotcodex
.\dotcodex\scripts\install-dotcodex.ps1 -ProjectRoot .
```

Result: `.codex/` folder ready, hooks in place.

She inventories existing docs:
- GitHub Wiki with "System Design" (10 pages)
- Confluence with "API Spec" (outdated)
- ADR files scattered in docs/ folder
- README with setup instructions
- CONTRIBUTING.md with PR guidelines

Decision: **Hybrid approach** - keep existing docs, consolidate key info into dotcodex structure.

### Day 3-5: Create Root Docs

Sarah creates minimal versions:

**CONTEXT.md:**
```markdown
# Acme Analytics - Project Context

## Project

Acme provides real-time analytics dashboards for e-commerce companies.
Users: SaaS customers (finance/operations teams).

## Architecture Snapshot

Frontend: React SPA → Node.js API → Python job workers → PostgreSQL + Redis cache.

Real-time data: WebSocket listeners on S3 bucket changes, push updates to frontend.

## Key Decisions

1. **Python for jobs, Node for API**: Python's data science libraries; Node for REST speed
2. **Redis caching**: Avoid re-querying large datasets on each drill-down
3. **Event-driven updates**: WebSockets for real-time, not polling

## Linked Docs

- Requirement.md (features we committed to)
- Architecture.md (design rationale)
- Note: Detailed API specs remain in Confluence (legacy); we're gradually migrating
```

**PLAN.md:**
```markdown
# PLAN - Q2 2026

## Current Objective

Adopt dotcodex workflow; improve onboarding time from 2 weeks to 3 days.

## Completed

- dotcodex bootstrap
- Root doc creation
- Team training (1 hour demo)

## In Progress

- Updating code standards in .codex/rules/

## Next

- Port Python style guide to python.md rule
- Enforce new rules in CI/CD
- Onboard next three new hires with dotcodex

## Blockers

None yet.

## Verification

- Manual: New hire feedback on learning curve
- Target: Onboarding < 3 days by June
```

**Requirement.md:**
```markdown
# Acme Analytics - Requirements

## Overview

Real-time dashboard showing e-commerce KPIs: revenue, transactions, top products, regional breakdown.

Users: Finance and operations managers at SaaS customers.

## Key Features

1. Real-time updates (< 500ms latency for new transactions)
2. Drill-down: Filter by region, product, customer segment
3. Custom dashboards (save filtered views)
4. Data export (CSV, for spreadsheet analysis)

## Non-Functional Requirements

- Performance: Page load < 2s, updates < 500ms
- Availability: 99.9% uptime, data lag < 5 minutes
- Scalability: Support 1M events/day per customer
- Security: Column-level encryption for sensitive data

## Constraints

- Can't modify customer data (read-only)
- Pricing data is legally sensitive (compliance)
- Late-night jobs (12am-4am) impact real-time freshness
```

**Architecture.md:**
```markdown
# Acme Analytics - Architecture

## System Overview

Frontend SPA subscribes to WebSocket API.
API queries PostgreSQL + Redis.
Background Python worker processes S3 events (new transaction logs).
Worker updates cache, API pushes WebSocket updates to frontend.

## Components

- **React Frontend:** SPA (src/webapp/)
- **Node.js API:** REST + WebSocket (api/routes/)
- **Python Worker:** Job processor (jobs/processors/)
- **PostgreSQL:** Event storage + aggregates
- **Redis:** Cache (recent transactions, computed totals)

## Technology Stack

- Frontend: React 18, TypeScript, Vite
- API: Node.js 18, Express, ws (WebSocket)
- Worker: Python 3.10, pandas, boto3
- Database: PostgreSQL 13, Redis 6
- Deployment: Docker, Kubernetes, AWS

## Key Decisions

1. **Opt for synchronous API** (not async queues): Customers expect < 500ms updates
2. **Use Redis not materialized views**: Redis faster for frequently-changing data
3. **Python for workers** (not Node): Data science libraries, easier aggregations
```

---

## Week 2: Rules & Automation

### Setting up Code Standards

Sarah creates stack-specific rules:

**`.codex/rules/node-typescript.md`:**
```markdown
# Node.js + TypeScript Stack

## Build & Run

- Build: `npm run build` (esbuild, output to dist/)
- Test: `npm run test` (Jest, coverage required)
- Lint: `npm run lint` (ESLint + Prettier)
- Type-check: `npm run type-check` (TypeScript strict mode)

## Testing

- Use Jest; test files in `tests/` mirroring `src/`
- Target 80%+ coverage (API handlers, middleware, utilities)
- Test async handlers with done() callback
- Mock external services (S3, PostgreSQL)

## Error Handling

- Throw custom errors (ApiError, ValidationError) with int status codes
- Always respond with JSON: `{ error: { code, message, details? } }`
- Log errors before sending (structured JSON logs)
- Never expose stack traces to client

## Performance

- All query endpoints should use Redis cache where possible
- Cache key format: `${entity}:${id}:${version}`
- Cache TTL: 5 minutes default; override per query
```

**`.codex/rules/python.md`:**
```markdown
# Python Stack

## Python Version & Environment

- Python 3.10+
- Use venv; commit requirements-lock.txt (pinned versions)
- Type hints on public functions (mypy --strict)

## Testing

- Use pytest; test files in `tests/` mirroring `src/`
- Target 80%+ coverage
- Use pytest fixtures for database, S3 mocks
- No sleep() in tests; use freezegun for time travel

## Code Style

- Follow PEP 8; use Black (line length 88)
- Use isort for imports
- Use pylint (10/10 score for new code, >= 9/10 for legacy)

## Performance

- Vectorize: use pandas/numpy, not loops
- Profile: use cProfile on slow queries
- No N+1 queries: prefetch relations in single SQL query
```

Sarah updates `AGENTS.md`:

```markdown
## Rules

- `.codex/rules/code-quality.md` (generic)
- `.codex/rules/testing.md` (generic)
- `.codex/rules/security.md` (generic)
- `.codex/rules/error-handling.md` (generic)
- `.codex/rules/frontend.md` (generic)
- `.codex/rules/node-typescript.md` (backend API)
- `.codex/rules/python.md` (data jobs)
- `.codex/rules/react.md` (frontend)
```

### CI/CD Setup

Updated `.github/workflows/ci.yml`:

```yaml
name: CI

on: [push, pull_request]

jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Verify CONTEXT.md and PLAN.md exist
        run: |
          test -f CONTEXT.md || { echo "Missing CONTEXT.md"; exit 1; }
          test -f PLAN.md || { echo "Missing PLAN.md"; exit 1; }

  node-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      - run: npm ci && npm run lint && npm run type-check && npm run test

  python-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          cache: 'pip'
      - run: pip install -r requirements-lock.txt pytest pytest-cov
      - run: pytest --cov=src --cov-report=term
```

---

## Week 3-4: Team Onboarding

### Training Demo

Sarah walks the team through:

1. **CONTEXT.md:** "Read this first to understand architecture + key decisions"
2. **PLAN.md:** "This is our current sprint; pick a task from 'Next'"
3. **Rules:** "Code will be reviewed against these standards; no surprises"
4. **Using Codex:** "Instead of writing from scratch, ask Codex to help"

### First Codex Task

Jean (new backend engineer) asks Codex:

```
I need to implement a new endpoint GET /dashboards/{id}/top-products.

Read CONTEXT.md, PLAN.md, Requirement.md, Architecture.md, and .codex/rules/.

Implement the endpoint:
- Fetch top 10 products for dashboard ID
- Use Redis cache (5-min TTL)
- Return JSON with product names, revenue, count
- Include proper error handling per .codex/rules/error-handling.md
```

Codex implements:

```typescript
router.get('/dashboards/:id/top-products', asyncHandler(async (req, res) => {
  const { id } = req.params;

  // Validate input
  if (!validateDashboardId(id)) {
    throw new ValidationError('Invalid dashboard ID');
  }

  // Check cache
  const cacheKey = `dashboard:${id}:top-products:v1`;
  const cached = await redis.get(cacheKey);
  if (cached) return res.json(JSON.parse(cached));

  // Query database
  const products = await db.query(`
    SELECT product_id, name, SUM(revenue) as revenue, COUNT(*) as count
    FROM transactions
    WHERE dashboard_id = $1
    GROUP BY product_id, name
    ORDER BY revenue DESC
    LIMIT 10
  `, [id]);

  // Cache result (5 minutes)
  await redis.setex(cacheKey, 300, JSON.stringify(products));

  // Respond
  res.json(products);
}));
```

Jean reviews with the team (via Codex code review agent):

```
@code-reviewer Review this implementation against:
- .codex/rules/node-typescript.md
- .codex/rules/error-handling.md
- .codex/rules/security.md

Specifically check:
- Error handling (ValidationError proper)
- Cache key format
- Performance (no N+1)
- Security (SQL injection protection)
```

**Code reviewer responds:**

```
✓ Error handling: proper use of custom ValidationError
✓ Cache: correct key format (dashboard:id:query:version)
✓ Performance: single SQL query, no N+1
✓ Security: using parameterized query ($1), SQL injection protected
✓ Tests: should add tests for cache hit/miss and validation error

Ready to merge after tests added.
```

Jean adds tests (using test-writer skill):

```typescript
describe('GET /dashboards/:id/top-products', () => {
  it('should return top products', async () => {
    const res = await request(app)
      .get('/dashboards/123/top-products');
    expect(res.status).toBe(200);
    expect(res.body).toHaveLength(10);
  });

  it('should cache result in Redis', async () => {
    // First call
    await request(app).get('/dashboards/123/top-products');
    // Verify cache key exists
    const cached = await redis.get('dashboard:123:top-products:v1');
    expect(cached).toBeTruthy();
  });

  it('should return cached result on second call', async () => {
    // Mock database to verify it's not called on cache hit
    const dbSpy = jest.spyOn(db, 'query');
    
    await request(app).get('/dashboards/123/top-products');
    await request(app).get('/dashboards/123/top-products'); // Cache hit
    
    expect(dbSpy).toHaveBeenCalledTimes(1); // Only 1 DB call
  });

  it('should return 400 for invalid dashboard ID', async () => {
    const res = await request(app)
      .get('/dashboards/invalid-id/top-products');
    expect(res.status).toBe(400);
    expect(res.body.error.message).toMatch('Invalid dashboard ID');
  });
});
```

Tests pass. PR merged.

---

## Week 5+: Measuring Impact

### Onboarding Time

**Before dotcodex:**
- New hire reads README: 30 min
- Asks questions about architecture: 1 hour
- Asks about code standards: 30 min
- Tries to understand a complex function: 1 hour
- Still doesn't know what to work on
- Takes 2 weeks to be productive

**After dotcodex:**
- New hire reads CONTEXT.md + PLAN.md: 15 min
- Reviews AGENTS.md and rules: 15 min
- Code-reviewed demo endpoint: 1 hour
- Asks Codex to implement their first feature: 30 min
- Productive in 3 days

**Result: 2 weeks → 3 days (6x faster)**

### Code Review Cycles

**Before:**
- Reviewer: "Where's the error handling?"
- Reviewer: "Tests coverage is 60%, needs 80%"
- Reviewer: "This doesn't follow our naming convention"
- (3-4 back-and-forths, 3 days to merge)

**After:**
- Code against .codex/rules/ standards
- CI enforces test coverage
- Codex code-reviewer flags errors before human review
- (1-2 back-and-forths, 1 day to merge)

**Result: ~2x faster code reviews**

### Bug Prevention

**Before:**
- Production bugs discovered by customers
- Root cause: "We don't have authorization checks"
- Fix: reactive, costly

**After:**
- security-reviewer catches vulnerabilities in code review
- Testing rule requires edge cases
- Example: "Missing auth check on delete endpoint" caught before merge

**Result: ~40% fewer production incidents (not causation, but correlation)**

### Token Efficiency

Sarah asked Codex to implement 10 features:

**Without dotcodex context:**
- Codex needs to explore codebase (grep, ls, file reads)
- Average: 200+ tokens per feature

**With dotcodex context:**
- Codex reads CONTEXT.md, PLAN.md, rules
- Hooks prevent needless exploration
- Average: 80-100 tokens per feature

**Result: ~2x fewer tokens per task**

---

## Lessons Learned

### What Worked

1. **Hybrid migration:** Kept existing docs, linked from dotcodex. No disruption.
2. **Rules first:** Established code standards in `.codex/rules/` before using Codex heavily.
3. **Gradual adoption:** Started with CONTEXT + PLAN, added other docs over time.
4. **Team training:** 1-hour demo prevented confusion about workflow.
5. **CI enforcement:** Automated checks (coverage, linting) caught issues Codex might miss.

### What We'd Do Differently

1. **Obsidian earlier:** Sarah later adopted Obsidian for better navigation; would've done day 1.
2. **Detailed rules faster:** Took 2 weeks to fine-tune Python rules; would create detailed rules week 1.
3. **Case study earlier:** Would've documented decision rationale upfront (migration decision, hybrid approach).

### Advice for Other Teams

1. **Start small:** CONTEXT + PLAN are enough; add docs gradually.
2. **Customize rules:** Don't use generic rules; create stack-specific rules in week 1.
3. **Enforce in CI:** Rules only work if CI validates them.
4. **Train once:** 1-hour demo saves 10 hours of questions.
5. **Measure:** Track onboarding time, PR cycle time, incident rate. Proves ROI exists.

---

## Metrics Summary

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Onboarding time** | 2 weeks | 3 days | 6.7x faster |
| **Code review cycles** | 3 days | 1 day | 3x faster |
| **Test coverage** | 70% avg | 85% avg | +15% |
| **Production incidents/month** | 5-7 | 3-4 | ~40% fewer |
| **Tokens per task** | 200+ | 80-100 | 2x fewer |
| **Developer satisfaction** | "What's our standard?" | "Check CONTEXT.md" | Much clearer |

---

## Q&A

**Q: Did you need to rewrite all existing docs?**

A: No. We kept GitHub Wiki + Confluence, linked from dotcodex. Gradual migration over 3 months.

**Q: How long did full adoption take?**

A: 4 weeks for core setup + team training. Ongoing refinement (improvements each month).

**Q: Did the team resist the new workflow?**

A: Initially skeptical ("more docs to maintain?"). After seeing reduced code review cycles + faster onboarding, they embraced it.

**Q: Can this work for teams smaller than 10?**

A: Yes. Sarah estimates solo developers would find CONTEXT.md useful (tracks past decisions); probably skip most docs at first.

**Q: What about remote teams / timezone differences?**

A: Actually helped. CONTEXT.md and PLAN.md became source of truth instead of "I'll explain after standup."
