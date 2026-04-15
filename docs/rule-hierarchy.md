# Rule Hierarchy & Conflicts

How dotagent rules interact, when they conflict, and which takes precedence.

## Rule Sources

Rules come from four levels:

| Level | Location | Scope | Precedence |
|-------|----------|-------|-----------|
| 1. **Dotagent (Generic)** | `.agent/rules/` from dotagent | All projects | Lowest |
| 2. **Project-Local** | `.agent/rules/` customized per project | This project only | Medium |
| 3. **Stack-Specific** | `.agent/rules/python.md`, `typescript.md`, etc. | Language/framework | High |
| 4. **Task/Context-Specific** | In AGENTS.md or task prompt | Current work | Highest |

**Rule of thumb:** More specific rules override more generic rules.

---

## Precedence Examples

### Example 1: Function Length

```
Generic rule (code-quality.md):
  "Keep functions under 30 lines"

Stack rule (python.md):
  "Python data processing functions may be up to 50 lines"

Result:
  For Python files: 50-line limit (python.md wins)
  For JavaScript files: 30-line limit (code-quality.md applies)
```

### Example 2: Test Coverage

```
Generic rule (testing.md):
  "Target 80%+ coverage for new code"

Stack rule (legacy-python.md):
  "Legacy modules excepted; aim for 50%+ on legacy code"

Task instruction:
  "Add 90%+ coverage to the payment module"

Result:
  Payment module: 90% (task instruction wins)
  Legacy modules: 50% (legacy rule applies)
  New modules: 80% (generic rule applies)
```

### Example 3: Error Handling

```
Generic rule (error-handling.md):
  "Return actionable error messages"

Domain rule (payments.md):
  "Payment errors must include transaction ID and retry attempt"

Project rule (.agent/rules/api.md):
  "All API errors must be JSON with code/message/details"

Result:
  For payment API errors: all three apply
  - JSON format (project rule)
  - Include transaction ID + retry attempt (domain rule)
  - Message is actionable (generic rule)
```

---

## How to Resolve Conflicts

### 1. Specific Wins Over Generic

When you find a conflict:

```markdown
# python.md (specific, higher priority)

## Function Length

> **Supersedes:** code-quality.md rule "Keep functions under 30 lines"

For Python data processing, ETL, and ML pipelines:
- Functions may reach 50 lines if well-structured and testable
- Prefer smaller when possible, but don't artificially break cohesive logic

Example: A 45-line data transformation is acceptable if each step is clear.
```

Then in code-quality.md, add a note:

```markdown
# Code Quality

- Keep functions under 30 lines. (Exceptions: see stack-specific rules)
```

### 2. Document Exceptions in the Specific Rule

If your Node.js project deviates from generic testing rules:

```markdown
# nodejs.md

## Testing

> **Differs from generic testing.md:**
> - Generic: "Unit tests for local logic, integration tests for module boundaries"
> - Node.js: "Use Jest for all tests; integration via test doubles (mocks/stubs) to avoid slow DB hits"

Rationale: Node.js async patterns and npm test ecosystem are different from language-agnostic testing.
```

### 3. Use Comments in AGENTS.md to Clarify

```markdown
## Rules

When present, follow:

- `.agent/rules/code-quality.md`
- `.agent/rules/testing.md`
- `.agent/rules/security.md`
- `.agent/rules/error-handling.md`
- `.agent/rules/frontend.md`

### Stack-Specific Rules (override generic for indicated stacks)

- `.agent/rules/typescript.md` (overrides code-quality on type strictness)
- `.agent/rules/react.md` (overrides frontend on component patterns)
- `.agent/rules/nodejs.md` (overrides testing on async/mock patterns)

### Domain-Specific Rules (override generic for indicated domains)

- `.agent/rules/payments.md` (security, audit logging, transaction isolation)
- `.agent/rules/api.md` (error formats, versioning, rate limiting)
```

---

## When Rules Are Ambiguous

### Scenario: Two rules give different advice on the same topic

```
Generic error-handling.md says:
  "Return actionable error messages with enough context"

Your typescript.md says:
  "Use discriminated unions for error types"

Both are correct but represent different levels of abstraction.
```

**Solution:** Make them complementary, not conflicting.

Revised typescript.md:

```markdown
# TypeScript Error Handling

> **Complements:** error-handling.md with TypeScript-specific patterns

Return discriminated union types (for type safety) that include actionable messages:

```typescript
type Result<T> = 
  | { success: true; data: T }
  | { success: false; error: { code: string; message: string; context?: Record<string, any> } }
```

This enforces:
- Type-safe error handling (TypeScript benefit)
- Actionable messages (generic rule)
- Structured context (generic rule)
```

---

## Rule Hierarchy Matrix

Use this matrix when deciding which rule applies:

| Situation | Rule Applied | Reason |
|-----------|--------------|--------|
| Generic topic, no stack/domain rule | Generic rule | It's the baseline |
| Topic in generic + stack-specific rule | Stack-specific | More specific wins |
| Topic in generic + domain rule | Domain rule | Domain is most specific |
| Generic + stack + domain rules exist | Use all three, ensuring no contradictions | Combine complementary guidance |
| Generic rule contradicts task prompt | Task prompt | Immediate context is highest |
| Two project rules conflict | Whichever is more recent | Last update wins; document the change |
| Rule conflicts with PLAN.md milestone | Milestone takes precedence | Current objective beats standing rules |

---

## Adding Rules Without Breaking Precedence

### Pattern 1: Extend, Don't Replace

```markdown
# python-testing.md

> **Extends:** .agent/rules/testing.md with Python specifics

Generic rule: Test happy path, edge cases, and failure paths.

Python specifics:
- Use pytest; organize tests in tests/ mirroring src/.
- Use fixtures for shared state.
- Use @pytest.mark.parametrize for edge cases.
```

### Pattern 2: Override with Clear Rationale

```markdown
# fastapi.md

> **Overrides:** generic testing.md on integration testing.

Generic rule: "Integration tests for module boundaries."

FastAPI override:
- Use pytest fixtures to inject mocked databases (avoid real DB in tests).
- Use TestClient for route testing (faster than full HTTP calls).
- Rationale: FastAPI's async/await and dependency injection work best with fixtures, not integration DBs.
```

### Pattern 3: Opt-Out for Specific Contexts

```markdown
# legacy-module-rules.md

Applies to: src/legacy/ only.

Override code-quality.md: Allow functions up to 80 lines in legacy modules.

Rationale: Refactoring legacy code is expensive; keep code-review focus on new bugs, not structural improvements.
```

Then in AGENTS.md:

```markdown
- `.agent/rules/legacy-module-rules.md` (applies to src/legacy/ only; overrides code-quality.md)
```

---

## Cross-Team Rule Consistency

If multiple teams share dotagent:

### Option 1: Shared Core + Local Variants

```
core-agent/
|-- rules/
|   |-- code-quality.md        (shared, all teams)
|   |-- testing.md             (shared, all teams)
|   `-- security.md            (shared, all teams)

team-a-agent/
|-- rules/
|   |-- python.md              (Team A specific)
|   `-- django.md              (Team A specific)

team-b-agent/
`-- rules/
    |-- typescript.md          (Team B specific)
    `-- react.md               (Team B specific)
```

Each project references:
- Shared rules from core-agent
- Team rules from team-specific repo

### Option 2: Monorepo with Layered Rules

```
monorepo/
|-- .agent/
|   `-- rules/
|       |-- core/
|       |   |-- code-quality.md
|       |   |-- testing.md
|       |   `-- security.md
|       |-- services/
|       |   |-- payment-service.md
|       |   `-- auth-service.md
|       `-- team-a/
|           |-- python.md
|           `-- django.md

services/payment/
`-- AGENTS.md (references)
    - .agent/rules/core/*.md
    - .agent/rules/services/payment-service.md
```

### Option 3: Inheritance Chain

```markdown
# .agent/rules/security.md (core)

Universal security rules apply to all projects.

---

# .agent/rules/security-payments.md (extends)

> **Extends:** security.md with payment-domain specifics

Generic: Validate all input at boundaries.

Payments: Additionally, validate amount >= 0.01, currency is ISO 4217, recipient is whitelisted.
```

---

## Testing Rule Application

To verify rules are being applied correctly:

1. **Ask Agent to explain its reasoning:**
   ```
   Why did you implement error handling this way? Which rules guided you?
   ```

2. **Review the code against all applicable rules:**
   - Generic rules (code-quality, testing, security, error-handling, frontend, knowledge-graphs)
   - Stack-specific rules (python.md, typescript.md, etc.)
   - Project-local rules

3. **Check for conflicts:**
   If Agent seems to violate a rule, it may be following a higher-precedence rule. Ask:
   ```
   This seems to violate .agent/rules/code-quality.md. What other rule guided you?
   ```

---

## Summary

- **Generic rules** apply everywhere unless overridden
- **Stack-specific rules** override generic for their stack
- **Domain rules** override both generic and stack for their domain
- **Task instructions** override all standing rules
- **Document overrides** in comments so future readers understand why

When in doubt:
1. Ask Agent to explain which rule it's following
2. Add a clarifying comment to the rule file
3. Update AGENTS.md to document the precedence
4. Test with concrete examples


