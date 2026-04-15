# Starter Templates

Copy-and-paste templates for common document types. Customize with your project details.

## CONTEXT.md - Starter Template

```markdown
# CONTEXT

## Project

**Name:** [Project Name]

**Purpose:** [What does this system do? Who does it serve? One sentence.]

Example: "Acme Dashboard provides real-time KPI visualization for e-commerce operations teams."

## Architecture Snapshot

[2-3 sentences describing your system architecture and main components.]

Example: "Frontend SPA queries Node.js API for data. API queries PostgreSQL and caches in Redis. Background Python workers process event streams and update aggregates."

## Key Decisions

List major technical decisions and rationale:

1. **[Decision Name]**: [Rationale and impact]
   - Example: "Use Python for data jobs (not Node.js): Data science libraries available, easier aggregations. Impact: Split stack, but job quality is better."

2. **[Decision Name]**: [Rationale and impact]

## Constraints

### Technical

- [Constraint and reason]
- Example: "Cannot modify customer data (read-only access). Reason: Compliance, data stays in customer DB."

### Operational

- [Constraint and reason]
- Example: "Deployments only during maintenance window (2-4am UTC). Reason: EU customer contracts."

## Known Risks

List risks and mitigations:

| Risk | Severity | Mitigation |
|------|----------|-----------|
| [Risk description] | High/Medium/Low | [How you're handling it] |
| Redis data loss on crash | Medium | Persistent RDB snapshot, monitor in DataDog |
| Large queries timeout | High | Add query timeout, implement pagination |

## Important Paths

```
src/
  webapp/          # React frontend
  api/             # Node.js API handlers
  jobs/            # Python worker code
  
tests/
  unit/            # Component tests
  integration/     # API + DB tests
  
docs/
  api-spec.md      # REST API documentation
  database.md      # Schema and indexes
```

## Assumptions

- [Assumption about your system or users]
- Example: "Assume all input from untrusted sources (customer API calls)."
- Example: "Assume PostgreSQL is always available."

## Domain Terms

Define project-specific jargon:

- **Dashboard**: Customizable view of KPIs for a customer
- **Event**: Raw transaction from customer's e-commerce system
- **Aggregation**: Computed totals (revenue, count, etc.)

## Linked Docs

- `Requirement.md` - What we're building
- `Architecture.md` - How it's structured
- `PLAN.md` - What we're working on now
```

---

## PLAN.md - Starter Template

```markdown
# PLAN

## Current Objective

[One short sentence: What is the immediate goal this sprint/week?]

Example: "Implement bulk export feature for dashboards."

## Completed

[What's already done. Include date completed.]

- Bootstrap project structure (2026-04-01)
- Set up CI/CD (2026-04-03)
- API skeleton with auth (2026-04-07)

## In Progress

[What's currently being worked on. Include start date.]

- [ ] Implement export endpoint (started 2026-04-10, owner: @alice)
- [ ] Add export tests (started 2026-04-10, owner: @bob)

## Next

[List of planned work, prioritized.]

1. [ ] Support CSV export format
2. [ ] Add email delivery option
3. [ ] Implement export history/audit trail
4. [ ] Performance optimization (large dataset exports)

## Blockers

[What's preventing progress. Include impact and workaround.]

| Issue | Impact | Workaround |
|-------|--------|-----------|
| Awaiting AWS API credentials | Blocking S3 features | Using local file storage for now |
| Database performance on large queries | Slow export | May need indexing; measuring first |

## Verification

### Tests Run

- Unit tests: âœ“ All passing
- Integration tests: âœ“ All passing
- Manual testing: In progress

### Manual Checks

- [ ] Export endpoint works with real data
- [ ] Performance acceptable (< 30 sec for large exports)
- [ ] Error handling (invalid format, timeout, etc.)

### Known Gaps

- Performance under load (needs load testing)
- Email delivery not yet verified
- Edge case: usernames with special characters (need test)
```

---

## Requirement.md - Starter Template

```markdown
# Requirement

## Overview

### Purpose

[What is this system for? Who uses it? One paragraph.]

### Scope

**In Scope:**
- [Feature A]
- [Feature B]

**Out of Scope:**
- [Explicitly something we're NOT doing]

## Functional Requirements

### Feature 1: [Feature Name]

**Description:** [What the feature does from user perspective.]

**Example Use Case:** [Concrete scenario.]

**Success Criteria:**
- [ ] User can [action]
- [ ] System validates [constraint]
- [ ] Error message shows [helpful guidance]

### Feature 2: [Feature Name]

[Repeat above structure]

## Non-Functional Requirements

| Category | Requirement | Reason |
|----------|-------------|--------|
| **Performance** | Page load < 2s, API response < 500ms | User experience |
| **Scalability** | Handle 1M events/day | Support target customer size |
| **Reliability** | 99.9% uptime | Customer SLAs |
| **Security** | Encrypt sensitive data in transit, at rest | Compliance |
| **Usability** | Accessible to screen readers (WCAG AA) | Inclusive design |

## Data Definitions

### Entity: [Entity Name]

- **user_id**: Unique identifier (UUID, not nullable)
- **created_at**: Timestamp (UTC, auto-set, not nullable)
- **role**: User role (enum: admin, user, guest)
- **status**: User status (enum: active, suspended, deleted)

## Edge Cases

- What if user has no data? â†’ Show empty state with guidance
- What if request is malformed? â†’ Return 400 with validation error
- What if external API timeouts? â†’ Retry 3x, then error to user

## Glossary

- **Dashboard**: Customizable view of metrics
- **Event**: Individual transaction record
- **Aggregate**: Pre-computed summary (revenue total, count, etc.)
```

---

## Architecture.md - Starter Template

```markdown
# Architecture

## System Overview

[1-2 paragraphs describing your overall system.]

Example:
```
User opens React app in browser. App makes REST API calls to Node.js server.
Server queries PostgreSQL for stored data, queries Redis for cached results.
If data is stale, server triggers Python background job to re-compute.
Job fetches fresh data from S3, updates PostgreSQL, invalidates Redis cache.
Next API call sees fresh data.
```

## Architecture Diagram

[Text description or link to diagram tool (draw.io, Miro, etc.)]

Example:
```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  React  â”‚ (Browser)
â””â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”˜
     â”‚ REST API
     â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚   Node.js API   â”‚
â””â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”˜
     â”‚        â”‚
     â”‚ SQL    â”‚ Redis
     â–¼        â–¼
  â”Œâ”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”
  â”‚ PG   â”‚  â”‚ Cache  â”‚
  â””â”€â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”€â”€â”€â”˜

          â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
          â”‚ Python Jobs  â”‚ (Background)
          â””â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”˜
                 â”‚ S3
                 â–¼
          â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
          â”‚S3 Bucket â”‚
          â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

## Components

### Frontend (React)

**Responsibility:** Render dashboards, handle user interactions.

**Interfaces:**
- REST API calls to /api/v1/
- WebSocket for real-time updates

**Dependencies:**
- Node.js API (required)
- Redux for state (internal)

### API Server (Node.js)

**Responsibility:** Handle REST requests, query data, serve WebSocket updates.

**Interfaces:**
- HTTP (port 3000)
- WebSocket (port 3000)

**Dependencies:**
- PostgreSQL (required)
- Redis (optional but recommended for performance)

### Data Jobs (Python)

**Responsibility:** Process event streams, compute aggregates, update cache.

**Interfaces:**
- Event queue (SQS or similar)
- PostgreSQL (write)
- Redis (write)

**Dependencies:**
- PostgreSQL (required)
- pandas for data processing
- boto3 for S3 access

## Technology Stack

| Layer | Technology | Version | Reason |
|-------|------------|---------|--------|
| **Frontend** | React | 18.2 | Component-based, large ecosystem |
| **API** | Node.js | 18 LTS | Fast, async-friendly, Express mature |
| **Worker** | Python | 3.10 | Data science libraries (pandas, numpy) |
| **Database** | PostgreSQL | 13 | ACID, advanced query optimization |
| **Cache** | Redis | 6 | Fast in-memory, TTL support |
| **Deployment** | Docker + Kubernetes | K8s 1.24 | Container orchestration |
| **CI/CD** | GitHub Actions | n/a | Native to GitHub |

## Key Architectural Decisions

### 1. Separation of Frontend and Backend

**Decision:** Build React SPA separate from Node.js API.

**Rationale:**
- Teams can work independently
- APIs can be consumed by mobile apps later
- Frontend can cache responses locally

**Implications:**
- Must manage API versioning
- CORS configuration required

### 2. Use Redis for High-Frequency Queries

**Decision:** Cache dashboard aggregates in Redis before querying PostgreSQL.

**Rationale:**
- Dashboards hit same queries repeatedly
- PostgreSQL becomes bottleneck at scale
- Redis TTL (5 min) acceptable for analytics data

**Implications:**
- Cache invalidation complexity
- Additional infrastructure (Redis cluster)
- Must monitor cache hit rate

### 3. Python for Background Jobs

**Decision:** Use Python (not Node.js) for event processing.

**Rationale:**
- pandas/numpy essential for data aggregations
- Easier to write complex logic in Python
- Data science team comfortable with Python

**Implications:**
- Maintain two runtimes
- Different deployment process for Python

## Data Flow

### Happy Path: User Views Dashboard

```
1. User navigates to /dashboard/123
2. React calls GET /api/v1/dashboards/123
3. Node.js checks Redis for cached data
4. Cache hit: Return cached JSON
5. React renders dashboard with data
```

### Cache Miss: User Views Dashboard

```
1. User navigates to /dashboard/123
2. React calls GET /api/v1/dashboards/123
3. Node.js checks Redis cache: miss
4. Node.js queries PostgreSQL (aggregations)
5. Node.js caches result in Redis (5 min TTL)
6. Node.js returns JSON to React
7. React renders dashboard
```

### Background: Data Updated

```
1. Python job listens to S3 bucket
2. New transaction log arrives
3. Job reads and parses transactions
4. Job updates PostgreSQL aggregates
5. Job invalidates Redis cache keys
6. Next API call will re-compute from fresh data
```

## Quality Attributes

### Performance

- Page load < 2 seconds (including network)
- Dashboard render < 500ms
- API response < 200ms (with cache hit)
- Aggregate computation < 30 seconds (with 1M events)

### Scalability

- Support 1M events/day per customer
- Handle 1000 concurrent users on single deployment
- Horizontal scaling: add more Node.js and Python pods

### Reliability

- 99.9% uptime target
- Graceful degradation (cached data if DB down)
- Retry transient failures (S3, network)

### Security

- HTTPS only
- CORS whitelist to allowed domains
- Secrets (DB password, API keys) in environment variables
- SQL injection prevention (parameterized queries)
- OWASP Top 10 compliance (input validation, etc.)
```

---

## Template: .agent/rules/[stack].md

```markdown
# [Stack Name] Stack Rules

Follow these rules when implementing [stack] features.

## Build & Deployment

**Build command:** `[npm run build / mvn clean package / python -m build]`

**Test command:** `[npm test / mvn test / pytest]`

**Lint command:** `[npm run lint / mvn spotbugs / pylint]`

**Type check:** (if applicable)`[npm run type-check / mypy]`

## Code Style

- [Standard (PEP 8, AirBnB, etc.)]
- [Formatting tool (Prettier, Black, etc.)]
- Max line length: [80 / 100 / 120]
- Naming conventions: [example: use_snake_case for functions]

## Testing

- Test framework: [Jest / pytest / JUnit]
- Test location: [tests/ mirroring src/]
- Coverage target: [70% / 80% / 90%]
- What to test: [unit only / unit + integration]
- Mocking: [how to mock external services]

## Dependencies

- How to add: [npm install / pip install]
- Pinning strategy: [exact versions / semver / ~]
- Reviewing for vulnerabilities: [npm audit / pip audit / dependabot]

## Performance Considerations

- Avoid [N+1 queries / re-computing data / blocking I/O]
- Prefer [batching / caching / async operations]
- Profile with: [Node profiler / Python cProfile / JVM JFR]

## Error Handling

- Custom error types: [list them]
- Logging: [what to log, where, format]
- User-facing errors: [format and tone]

## Deployment

- Container: [Docker / OCI]
- Orchestration: [Kubernetes / ECS]
- Pre-flight checks: [tests pass / coverage meets threshold / etc.]

## Examples

[Link to example in actual codebase, or include code snippet]

## Tools & Run Commands

```bash
# Quick development
$ npm run dev

# Run tests
$ npm test

# Check coverage
$ npm test -- --coverage

# Lint and fix
$ npm run lint -- --fix

# Type check
$ npm run type-check

# Build for production
$ npm run build
```
```

---

## Use These Templates

1. **Copy the text** from the template matching your needs
2. **Customize** with your project details
3. **Share** with your team
4. **Refine** based on feedback

All templates are markdownâ€”easy to version control and edit collaboratively.

