# Customize dotagent for Your Stack

dotagent rules are language and framework-agnostic by design. This guide shows how to add stack-specific practices without modifying dotagent itself.

## Overview

After installing dotagent, you have:

```
.agent/rules/
|-- code-quality.md      (generic)
|-- testing.md           (generic)
|-- security.md          (generic)
|-- error-handling.md    (generic)
|-- frontend.md          (generic)
`-- knowledge-graphs.md  (generic)
```

**To customize:** Create new rule files in `.agent/rules/` for your stack, then add them to `AGENTS.md` under the "Rules" section.

## Stack-Specific Examples

### Python Projects

Create `.agent/rules/python.md`:

```markdown
# Python

## Style & Quality

- Follow PEP 8; use Black for formatting and isort for imports.
- Use type hints on public APIs.
- Prefer dataclasses or NamedTuple over plain dicts for structured data.
- Keep functions under 50 lines; break complex logic into testable units.

## Testing

- Use pytest; organize tests in `tests/` mirroring `src/` structure.
- Target 80%+ code coverage for new code; accept lower for legacy.
- Use pytest fixtures for shared test state.

## Dependencies

- Pin versions in requirements-lock.txt; keep requirements.txt flexible.
- Use virtual environments; never install globally.
- Review security advisories monthly with `pip audit`.

## Deployment

- Use Docker; follow Python layer caching best practices.
- Use environment variables for config; never embed secrets.
- Use pytest coverage in CI; fail if coverage drops.
```

Then add to `AGENTS.md`:

```markdown
## Rules

When present, follow:

- `.agent/rules/code-quality.md`
- `.agent/rules/testing.md`
- `.agent/rules/security.md`
- `.agent/rules/error-handling.md`
- `.agent/rules/python.md`
```

### JavaScript/TypeScript Projects

Create `.agent/rules/typescript.md`:

```markdown
# TypeScript

## Typing

- Use strict mode: `"strict": true` in tsconfig.json.
- No `any` types without justification and a comment explaining why.
- Use discriminated unions for variant types instead of optional fields.
- Use `readonly` for immutable properties.

## Linting & Formatting

- Use ESLint with @typescript-eslint/eslint-plugin.
- Use Prettier for consistent formatting.
- Run lint and format in CI; fail if violations found.

## Testing

- Use Vitest or Jest for unit tests.
- Use React Testing Library for component tests (not implementation details).
- Aim for 80%+ coverage on new code.

## Project Structure

```
src/
|-- components/      (React components)
|-- hooks/           (Custom React hooks)
|-- services/        (Business logic, API clients)
|-- types/           (TypeScript definitions)
|-- utils/           (Reusable helpers)
`-- index.ts
```

## Build & Deployment

- Use Vite or esbuild for development and production builds.
- Use TypeScript in build; check types in CI.
- Split chunks by route; lazy-load above the fold.
```

### Java Projects

Create `.agent/rules/java.md`:

```markdown
# Java

## Build & Dependencies

- Use Maven or Gradle.
- Centralize dependency versions in parent pom.xml or gradle.properties.
- Use dependabot or renovate to track security updates.

## Code Quality

- Use Checkstyle for style enforcement.
- Use SpotBugs for common bugs.
- Use Code Coverage (JaCoCo) in CI; fail if coverage drops below 70%.

## Testing

- Use JUnit 5 for unit tests.
- Use Mockito for mocks; avoid deep stubs.
- Use Testcontainers for integration tests (databases, message queues).
- Organize tests in `src/test/java/` mirroring `src/main/java/`.

## API Design

- Use Spring Boot for REST APIs.
- Document endpoints with OpenAPI/Swagger.
- Validate input with @Valid and custom validators.
- Return structured error responses with status codes and messages.

## Deployment

- Build Docker images in CI; scan for vulnerabilities.
- Use Spring profiles for environment-specific config.
- Run mutation tests monthly to validate test quality.
```

### Full-Stack (Frontend + Backend)

Create `.agent/rules/fullstack.md`:

```markdown
# Full-Stack Integration

## API Contract

- Document APIs in OpenAPI 3.0.
- Use versioning: /api/v1/, /api/v2/.
- Use standard HTTP status codes.
- Return structured errors: `{ error: { code, message } }`.

## Data Flow

- Backend: Accept JSON, validate, transform to domain model.
- Frontend: Type JSON responses using OpenAPI schema generators.
- Frontend: Cache API responses by URL; invalidate on mutation.
- Backend: Include cache headers (ETag, Cache-Control).

## Deployment Pipeline

1. Backend: run tests, lint, build, push image to registry
2. Frontend: run tests, lint, build, push to CDN or container
3. E2E: run integration tests against staging
4. Release: tag both versions, deploy in lockstep

## Monitoring

- Backend: log structured events (timestamp, level, context); trace request IDs.
- Frontend: capture user errors and send to observability platform.
- Alert on errors above threshold; page on-call for critical paths.
```

## Adding Custom Rules Without Modifying dotagent

**Pattern:**

1. Create `.agent/rules/my-custom-rule.md` in your project
2. Add it to your `AGENTS.md` under "Rules"
3. Commit to your repo

Your rules supplement (don't override) the generic dotagent rules.

Example `AGENTS.md` Rules section:

```markdown
## Rules

When present, follow:

- `.agent/rules/code-quality.md`
- `.agent/rules/testing.md`
- `.agent/rules/security.md`
- `.agent/rules/error-handling.md`
- `.agent/rules/frontend.md`
- `.agent/rules/typescript.md`
- `.agent/rules/react.md`
- `.agent/rules/node.md`
```

## Rule Priority & Conflicts

If two rules conflict:

1. **Specific beats generic:** `typescript.md` rules override `code-quality.md` on TypeScript-specific topics
2. **Project-local beats generic:** Your `.agent/rules/` beats dotagent defaults
3. **Recent beats old:** The rule you updated most recently takes precedence
4. **Comment conflicts:** If truly ambiguous, add to your rule:
   ```markdown
   > **Note:** On TypeScript typing, this rule supersedes code-quality.md rule X.
   ```

## Rules for Microservices

If you maintain multiple services, consider shared and service-specific rules:

```
shared/
|-- .agent/
|   `-- rules/
|       |-- code-quality.md      (shared)
|       |-- security.md          (shared)
|       `-- logging.md           (shared microservices rule)
|
|-- service-a/
|   `-- .agent/
|       `-- rules/
|           `-- python.md        (service A specific)
|
`-- service-b/
    `-- .agent/
        `-- rules/
            `-- typescript.md    (service B specific)
```

Then in each service's `AGENTS.md`, reference both shared and local rules.

## Key Patterns

| Pattern | Implementation |
|---------|---|
| **No magic numbers** | Create `.agent/rules/constants.md` listing magic values |
| **Logging standards** | Create `.agent/rules/logging.md` with format, levels, fields |
| **API versioning** | Create `.agent/rules/api-versioning.md` with deprecation policy |
| **Database migrations** | Create `.agent/rules/migrations.md` with rollback requirements |
| **Performance budgets** | Create `.agent/rules/performance.md` with metrics and targets |
| **Data retention** | Create `.agent/rules/data-retention.md` with policies |

## Keeping Rules DRY Across Teams

If multiple teams use dotagent:

1. Create a private `team-agent` repo with shared rules:
   ```
   team-agent/
   |-- rules/
   |   |-- python.md
   |   |-- typescript.md
   |   |-- logging.md
   |   `-- observability.md
   `-- README.md
   ```

2. Each project clones both `dotagent` and `team-agent`

3. In each project's `.agent/rules/`, symlink or copy from `team-agent/rules/`:
   ```powershell
   # In project root
   New-Item -ItemType SymbolicLink -Path '.agent/rules/python.md' `
     -Target '../../../team-agent/rules/python.md'
   ```

4. Commit only the symlinks; the actual rules live in `team-agent`

This prevents copy-paste and keeps standards aligned across teams.

## Example: Complete Customization

For a Node.js + React + TypeScript project:

**Install dotagent:**
```powershell
.\dotagent\scripts\install-dotagent.ps1 -ProjectRoot .
```

**Create stack-specific rules:**
- `.agent/rules/typescript.md`
- `.agent/rules/nodejs.md`
- `.agent/rules/react.md`

**Update AGENTS.md rules section** to include all three.

**Update your build validation** (in hooks or CI):
```bash
npm run lint   # TypeScript linter
npm run test   # Jest tests
npm run build  # Production build
```

Now your assistant will:
1. Read your generic rules (code-quality, testing, security, etc.)
2. Read your stack rules (typescript, nodejs, react)
3. Apply all of them when implementing features
4. Respect both generic and specific guidance

## Next Steps

- Review [Rule Hierarchy & Conflicts](rule-hierarchy.md) for detailed precedence
- See [Troubleshooting](troubleshooting.md) if rules aren't being followed
- Check [GitHub Actions Integration](#) if adding CI/CD rules

