# Customize dotcodex for Your Stack

dotcodex rules are language and framework-agnostic by design. This guide shows how to add stack-specific practices without modifying dotcodex itself.

## Overview

After installing dotcodex, you have:

```
.codex/rules/
├── code-quality.md      (generic)
├── testing.md           (generic)
├── security.md          (generic)
├── error-handling.md    (generic)
├── frontend.md          (generic)
├── knowledge-graphs.md  (generic)
```

**To customize:** Create new rule files in `.codex/rules/` for your stack, then add them to `AGENTS.md` under the "Rules" section.

## Stack-Specific Examples

### Python Projects

Create `.codex/rules/python.md`:

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

- `.codex/rules/code-quality.md`
- `.codex/rules/testing.md`
- `.codex/rules/security.md`
- `.codex/rules/error-handling.md`
- `.codex/rules/python.md`
```

### JavaScript/TypeScript Projects

Create `.codex/rules/typescript.md`:

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
├── components/      (React components)
├── hooks/          (Custom React hooks)
├── services/       (Business logic, API clients)
├── types/          (TypeScript definitions)
├── utils/          (Reusable helpers)
└── index.ts
```

## Build & Deployment

- Use Vite or esbuild for development and production builds.
- Use TypeScript in build; check types in CI.
- Split chunks by route; lazy-load above the fold.
```

### Java Projects

Create `.codex/rules/java.md`:

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

Create `.codex/rules/fullstack.md`:

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

## Adding Custom Rules Without Modifying dotcodex

**Pattern:**

1. Create `.codex/rules/my-custom-rule.md` in your project
2. Add it to your `AGENTS.md` under "Rules"
3. Commit to your repo

Your rules supplement (don't override) the generic dotcodex rules.

Example `AGENTS.md` Rules section:

```markdown
## Rules

When present, follow:

- `.codex/rules/code-quality.md`
- `.codex/rules/testing.md`
- `.codex/rules/security.md`
- `.codex/rules/error-handling.md`
- `.codex/rules/frontend.md`
- `.codex/rules/typescript.md`
- `.codex/rules/react.md`
- `.codex/rules/node.md`
```

## Rule Priority & Conflicts

If two rules conflict:

1. **Specific beats generic:** `typescript.md` rules override `code-quality.md` on TypeScript-specific topics
2. **Project-local beats generic:** Your `.codex/rules/` beats dotcodex defaults
3. **Recent beats old:** The rule you updated most recently takes precedence
4. **Comment conflicts:** If truly ambiguous, add to your rule:
   ```markdown
   > **Note:** On TypeScript typing, this rule supersedes code-quality.md rule X.
   ```

## Rules for Microservices

If you maintain multiple services, consider shared and service-specific rules:

```
shared/
├── .codex/
│   └── rules/
│       ├── code-quality.md      (shared)
│       ├── security.md          (shared)
│       └── logging.md           (shared microservices rule)
│
service-a/
├── .codex/
│   └── rules/
│       └── python.md            (service A specific)
│
service-b/
├── .codex/
│   └── rules/
│       └── typescript.md        (service B specific)
```

Then in each service's `AGENTS.md`, reference both shared and local rules.

## Key Patterns

| Pattern | Implementation |
|---------|---|
| **No magic numbers** | Create `.codex/rules/constants.md` listing magic values |
| **Logging standards** | Create `.codex/rules/logging.md` with format, levels, fields |
| **API versioning** | Create `.codex/rules/api-versioning.md` with deprecation policy |
| **Database migrations** | Create `.codex/rules/migrations.md` with rollback requirements |
| **Performance budgets** | Create `.codex/rules/performance.md` with metrics and targets |
| **Data retention** | Create `.codex/rules/data-retention.md` with policies |

## Keeping Rules DRY Across Teams

If multiple teams use dotcodex:

1. Create a private `team-codex` repo with shared rules:
   ```
   team-codex/
   ├── rules/
   │   ├── python.md
   │   ├── typescript.md
   │   ├── logging.md
   │   └── observability.md
   └── README.md
   ```

2. Each project clones both `dotcodex` and `team-codex`

3. In each project's `.codex/rules/`, symlink or copy from `team-codex/rules/`:
   ```powershell
   # In project root
   New-Item -ItemType SymbolicLink -Path '.codex/rules/python.md' `
     -Target '../../../team-codex/rules/python.md'
   ```

4. Commit only the symlinks; the actual rules live in `team-codex`

This prevents copy-paste and keeps standards aligned across teams.

## Example: Complete Customization

For a Node.js + React + TypeScript project:

**Install dotcodex:**
```powershell
.\dotcodex\scripts\install-dotcodex.ps1 -ProjectRoot .
```

**Create stack-specific rules:**
- `.codex/rules/typescript.md`
- `.codex/rules/nodejs.md`
- `.codex/rules/react.md`

**Update AGENTS.md rules section** to include all three.

**Update your build validation** (in hooks or CI):
```bash
npm run lint   # TypeScript linter
npm run test   # Jest tests
npm run build  # Production build
```

Now Codex will:
1. Read your generic rules (code-quality, testing, security, etc.)
2. Read your stack rules (typescript, nodejs, react)
3. Apply all of them when implementing features
4. Respect both generic and specific guidance

## Next Steps

- Review [Rule Hierarchy & Conflicts](rule-hierarchy.md) for detailed precedence
- See [Troubleshooting](troubleshooting.md) if rules aren't being followed
- Check [GitHub Actions Integration](#) if adding CI/CD rules
