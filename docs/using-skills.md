# Using Skills - Deep Dive Guide

Skills are reusable workflow patterns. This guide shows how to use each skill with step-by-step examples and expected outputs.

## What Are Skills?

Skills are workflow guides that help Codex apply a specific pattern. Each skill:
- Defines a repeatable process (e.g., TDD, debugging, refactoring)
- Connects to project rules (e.g., testing.md for test-writer)
- Produces predictable output

You invoke a skill by asking Codex to use it:

```
Use the TDD skill to implement a login validator.
```

---

## setupdotcodex — Initial Project Setup

**Purpose:** Customize dotcodex for your specific stack and build system.

**When to use:** After installing dotcodex, once per project.

**Duration:** 30 minutes.

### Workflow

1. Review your actual build/test/lint/check commands
2. Document them in `.codex/rules/` (create stack-specific rules)
3. Update AGENTS.md with your project details
4. Verify Codex can invoke the right commands

### Step-by-Step

**Step 1:** Ask Codex to examine your project:

```
Use the setupdotcodex skill.
Examine our actual:
- Build command (our package.json or Makefile)
- Test command (our test runner)
- Lint command (our ESLint or similar)
- Type-check command (our TypeScript or similar)
Tell me what you find.
```

**Step 2:** Codex reports back:

```
Found:
- Package.json with "build": "vite build"
- Tests: "test": "vitest" with coverage
- Lint: "lint": "eslint src/"
- Type: "type-check": "tsc --noEmit"

Recommendation: Create .codex/rules/vite-vitest.md documenting this stack.
```

**Step 3:** Ask Codex to create/update rules:

```
Create .codex/rules/node-typescript.md with:
- Build command and how to run it
- Test command and coverage expectations
- Lint command and our specific rules
- Type-check success criteria

Include examples of typical errors and how to fix them.
```

**Step 4:** Verify by asking Codex a task question:

```
What would you run to verify the build on this project?
```

Codex should cite the commands from your new rule.

### Expected Output

After setupdotcodex, you should have:
- `.codex/rules/[language].md` documenting your stack
- Updated `AGENTS.md` with project-specific guidance
- Codex can cite your actual build/test commands, not generic ones

---

## tdd — Test-Driven Development

**Purpose:** Drive implementation through small failing tests → minimal implementation → refactor.

**When to use:** When implementing a new feature from scratch.

**Duration:** 15-30 minutes per feature.

**Rules it enforces:** testing.md (happy path, edge cases, failure paths).

### Workflow

1. Write one failing test (simplest case)
2. Implement minimal code to pass it
3. Refactor without changing behavior
4. Repeat from simple to complex

### Step-by-Step Example

**Feature:** Implement a `validateEmail()` function.

**Step 1:** Ask Codex to start TDD:

```
Use the TDD skill to implement validateEmail(email: string): boolean.

Start with the simplest test case (happy path):
- A valid email should return true
- An invalid email should return false

Keep tests extremely focused. One test at a time.
```

**Step 2:** Codex writes first failing test:

```typescript
describe('validateEmail', () => {
  it('should return true for valid email', () => {
    expect(validateEmail('user@example.com')).toBe(true);
  });
});

// Function doesn't exist yet - test will fail
```

Then minimal implementation:

```typescript
function validateEmail(email: string): boolean {
  return email.includes('@');
}
```

**Step 3:** Move to edge cases:

```
Next test: validateEmail should reject emails without domain
```

Codex writes test:

```typescript
it('should return false for email without domain', () => {
  expect(validateEmail('user@')).toBe(false);
  expect(validateEmail('@example.com')).toBe(false);
});
```

Codex updates implementation to pass.

**Step 4:** Continue until complete:

Each iteration:
- Write failing test
- Implement to pass
- Refactor
- Repeat

### Expected Output

After TDD:
- Tests for happy path, edge cases, and failure scenarios
- Minimal implementation that passes all tests
- No speculative code (no "just in case" logic)
- High test-code ratio (roughly 1:1 or more tests than code)

### How TDD Connects to testing.md

Rule says: _"Validate happy path, edge cases, and failure paths."_

TDD ensures this through its process: each case becomes a test that drives implementation.

---

## debug-fix — Reproduce, Root Cause, Fix, Verify

**Purpose:** Fix a reported bug systematically.

**When to use:** When you have a bug report or find a defect.

**Duration:** 30 minutes to 2 hours depending on complexity.

**Rules it enforces:** error-handling.md (loud failures, actionable messages).

### Workflow

1. Reproduce the bug
2. Trace to the actual root cause (not a symptom)
3. Implement the minimum safe fix
4. Add a regression test
5. Verify the fix

### Step-by-Step Example

**Bug:** "Admin can delete other users' data."

**Step 1:** Ask Codex to reproduce:

```
Use the debug-fix skill.

Bug report: "Users can delete other users' data via API."
The bug is in the DELETE /users/:id endpoint.

Helper:
- Auth user: user123 (regular user)
- Target user: user456 (different user)
- Expected: Permission denied
- Actual: User is deleted

Reproduce the bug first. Show the exact request and response.
```

**Step 2:** Codex reproduces:

```
Test case:
- POST login as user123
- DELETE /users/user456
- Expected: 403 Forbidden
- Actual: 200 OK (user456 deleted)

Bug confirmed.
```

**Step 3:** Trace root cause:

```
Continue debugging. Show me the code path:
- Which route handler called?
- Which permission check failed?
- What allowed user123 to delete user456?
```

Codex traces:

```
Found:
1. DELETE /users/:id calls deleteUser(userId)
2. No permission check before deletion
3. deleteUser() only checks if user exists, not if requester is authorized

Root cause: Missing authorization check.
```

**Step 4:** Implement minimal fix:

```
Implement the minimum fix that:
1. Prevents user123 from deleting user456
2. Allows users to delete themselves
3. Allows admins to delete anyone
4. Returns 403 Forbidden if user lacks permission

Show the code change.
```

Codex implements:

```typescript
async function deleteUser(requestingUser, targetUserId) {
  // Minimal fix: check if user has permission
  if (requestingUser.id !== targetUserId && requestingUser.role !== 'admin') {
    throw new ForbiddenError('Cannot delete other users');
  }
  
  // Rest of deletion logic
  await db.users.delete(targetUserId);
}
```

**Step 5:** Add regression test:

```
Add a test to prevent this bug from happening again.
Test cases:
- Regular user can delete themselves
- Regular user cannot delete others
- Admin can delete anyone
```

**Step 6:** Verify:

```
Verify the fix:
1. Run the new test - should pass
2. Run all tests - should pass
3. Show that the bug no longer happens
```

### Expected Output

After debug-fix:
- Exact reproduction steps (repeatable)
- Root cause identified (not symptoms)
- Minimal change that fixes it (not over-engineered)
- Regression test added (prevents re-occurrence)
- All tests passing
- Bug verified as fixed

### How debug-fix Connects to error-handling.md

Rule says: _"Fail loudly on invalid state at boundaries; return actionable error messages."_

debug-fix enforces this by:
- Checking at the boundary (auth check)
- Failing loudly (403 instead of silent deletion)
- Returning actionable message ("Cannot delete other users" is clear)

---

## refactor — Improve Structure Without Changing Behavior

**Purpose:** Restructure code for clarity/maintainability without changing what it does.

**When to use:** When code is hard to understand or maintain, but works correctly.

**Duration:** 30 minutes to 2 hours.

**Rules it enforces:** code-quality.md (Keep modules cohesive, fix root causes).

### Workflow

1. Establish safety net (tests)
2. Make small structural changes
3. Verify behavior is unchanged after each step

### Step-by-Step Example

**Goal:** The `processOrder()` function is 120 lines and hard to follow.

**Step 1:** Establish safety net:

```
Use the refactor skill.

We want to refactor the processOrder() function:
- It's 120 lines
- It handles: validation, payment, inventory, notification
- Everything is mixed together

Before refactoring, show me:
1. Current test coverage for processOrder
2. Which tests pass right now
3. Whether refactoring would keep all tests passing

DO NOT refactor yet. Just analyze.
```

Codex reports:

```
Current test coverage:
- 8 tests covering processOrder
- All tests pass
- Coverage: 85%

Plan: Refactor will split into smaller functions, keep all tests passing.
Safety net is ready.
```

**Step 2:** Make first small refactor:

```
First refactor: Extract validation into validateOrder()

New structure:
function processOrder(order) {
  validateOrder(order);  // <-- extracted
  // ... rest of logic
}

function validateOrder(order) {
  // Move validation checks here
}

Show the changes and confirm all tests still pass.
```

Codex makes change and verifies:

```
✓ All 8 tests still pass
✓ Behavior unchanged
✓ Code is cleaner

Next refactor?
```

**Step 3:** Continue extracting:

```
Next: Extract payment handling into processPayment()
Then: Extract inventory update into updateInventory()
Then: Extract notification into sendNotification()

Do all three one at a time. After each, verify tests pass.
```

Codex refactors:

```
After extraction 1 (payment):
✓ All 8 tests pass

After extraction 2 (inventory):
✓ All 8 tests pass

After extraction 3 (notification):
✓ All 8 tests pass

Final structure:
function processOrder(order) {
  validateOrder(order);
  processPayment(order);
  updateInventory(order);
  sendNotification(order);
}

Each function has one responsibility, tests pass.
```

### Expected Output

After refactor:
- Same behavior (all tests pass)
- Clearer structure (each function does one thing)
- Easier to test individual pieces
- Easier to modify one part without breaking others

### How refactor Connects to code-quality.md

Rule says: _"Keep modules cohesive and responsibilities explicit."_

refactor enforces this by separating concerns:
- validateOrder() is cohesive (only validation)
- processPayment() is cohesive (only payment)
- etc.

---

## explain — Understand Code Before Changing It

**Purpose:** Document code behavior so you understand risks before modifying.

**When to use:** Before refactoring or modifying unfamiliar code.

**Duration:** 10-20 minutes.

**Rules it enforces:** code-quality.md (Fix root causes, not symptoms).

### Workflow

1. Ask Codex to explain the code
2. Understand: purpose, data flow, non-obvious behavior, modification risks
3. NOW you can safely modify it

### Step-by-Step Example

**Situation:** You need to modify the `calculateDiscount()` function but it's complex.

**Step 1:** Ask Codex to explain:

```
Use the explain skill.

Explain src/pricing/calculateDiscount.ts

Include:
- What is it responsible for?
- How does data flow through it?
- What's non-obvious or tricky?
- What breaks if I change X?
```

**Step 2:** Codex explains:

```
calculateDiscount(cart, user, coupon):

Responsibility:
- Takes a shopping cart, user profile, coupon code
- Returns discount amount (in cents)

Data flow:
1. Parse coupon code → extract discount type + percentage/amount
2. Check user's "promotions_used" history (prevents coupon reuse)
3. Calculate: base_price * category_multiplier * (1 - discount)
4. Cap discount to $50 max (per business rule)
5. Return discount amount

Non-obvious:
- Line 23: category_multiplier is loaded from database, not calculated
  (Electronics = 1.0, Luxury = 0.8, Food = 1.2)
- Line 35: Coupons can be user-specific (check user.id in coupon.valid_for)
- Line 47: 50-dollar cap is hardcoded (not in config)

Modification risks:
- If you remove line 23 check, luxury items get full discount (loss)
- If you skip line 35 user check, anyone can use single-use coupons
- If you increase the $50 cap without approval, profit margin changes
```

**Step 3:** Now you can safely modify:

```
Based on your explanation, I can now:
- Add support for seasonal discounts (update data flow)
- Know NOT to remove the category check
- Know the $50 cap is intentional (won't remove it without asking PM)
- Know to preserve the user-specific coupon check
```

### Expected Output

After explain:
- Clear understanding of the code's purpose
- Data flow traced from input to output
- Non-obvious behavior documented
- Risks of modification identified
- You can now modify safely

### How explain Connects to code-quality.md

Rule says: _"Keep comments focused on intent, constraints, or non-obvious tradeoffs."_

explain reinforces this by:
- Documenting intent (why does this code exist?)
- Surfacing constraints (you must NOT remove this check)
- Explaining non-obvious behavior (category_multiplier from DB)

---

## test-writer — Add Focused Tests for New/Changed Behavior

**Purpose:** Ensure new code is tested without over-specifying implementation.

**When to use:** After implementing a new feature or modifying behavior.

**Duration:** 15-30 minutes per feature.

**Rules it enforces:** testing.md (happy path, edge cases, failure paths; don't advance without passing tests).

### Workflow

1. Identify the behavior that changed
2. Write tests for: happy path, edge cases, error paths
3. Verify all tests pass
4. Verify coverage improved

### Step-by-Step Example

**Situation:** You added a "bulk upload" feature to the API.

**Step 1:** Ask Codex to write tests:

```
Use the test-writer skill.

New feature: POST /uploads/bulk

What it does:
- Accept 1-100 files
- Validate each file
- Store in S3
- Return list of upload IDs

Write tests for:
- Happy path: upload 5 valid files
- Edge case: upload exactly 1 file
- Edge case: upload exactly 100 files (max)
- Error case: upload 101 files (over limit)
- Error case: file too large (>100MB)
- Error case: file type not allowed (e.g., .exe)
- Error case: S3 upload fails

For each test, show the HTTP request and expected response.
```

**Step 2:** Codex writes tests:

```typescript
describe('POST /uploads/bulk', () => {
  
  // Happy path
  it('should upload 5 valid files', async () => {
    const files = [
      { name: 'doc1.pdf', size: 1000, type: 'application/pdf' },
      // ... 4 more files
    ];
    const res = await post('/uploads/bulk', { files });
    expect(res.status).toBe(200);
    expect(res.body.uploads).toHaveLength(5);
    expect(res.body.uploads[0]).toHaveProperty('id');
  });

  // Edge cases
  it('should accept exactly 1 file', async () => {
    // ... test with 1 file
  });

  it('should accept exactly 100 files (max)', async () => {
    // ... test with 100 files
  });

  // Error cases
  it('should reject 101 files (over limit)', async () => {
    // ... test with 101 files
    expect(res.status).toBe(400);
    expect(res.body.error).toMatch('max 100 files');
  });

  it('should reject files > 100MB', async () => {
    // ... test with 150MB file
    expect(res.status).toBe(413);
  });

  it('should reject disallowed file types', async () => {
    // ... test with .exe file
    expect(res.status).toBe(415);
  });

  it('should handle S3 failure gracefully', async () => {
    // Mock S3 to fail
    expect(res.status).toBe(500);
    expect(res.body.error).toMatch('Upload failed');
  });
});
```

**Step 3:** Verify tests pass:

```
Run these tests:
npm test -- /uploads/bulk

Show me:
1. All tests pass
2. Coverage improved (what was the percentage before? After?)
3. Any assertion that feels wrong (let me review)
```

Codex reports:

```
✓ 7 tests passed
✓ Coverage: /routes/uploads.ts went from 60% → 92%
✓ All assertions are correct (testing behavior, not implementation)
```

### Expected Output

After test-writer:
- Tests for happy path (normal usage)
- Tests for edge cases (boundary conditions)
- Tests for error paths (what goes wrong)
- Tests for integration boundaries (API, database, external services)
- Coverage improved
- All tests pass

### How test-writer Connects to testing.md

Rule says: _"Validate happy path, edge cases, and failure paths; do not advance with failing validation."_

test-writer ensures this by:
- Writing tests for each path
- Checking coverage (are all paths tested?)
- Requiring all tests to pass before considering work done

---

## Summary: When to Use Each Skill

| Skill | Trigger | Expected Output |
|-------|---------|-----------------|
| **setupdotcodex** | Starting a new dotcodex project | Stack rules, updated AGENTS.md |
| **tdd** | Implementing a new feature from scratch | Tests + implementation, high test coverage |
| **debug-fix** | Bug reported or defect found | Root cause identified, fix applied, regression test added |
| **refactor** | Code is hard to understand but works | Same behavior, clearer structure, all tests pass |
| **explain** | Need to understand code before modifying | Documented purpose, data flow, risks, constraints |
| **test-writer** | New behavior added or changed | Tests for happy/edge/error paths, coverage improved |

---

## Combining Skills

Skills work well together:

### Feature Implementation Workflow
1. **explain** — Read related code
2. **tdd** — Implement feature test-first
3. **refactor** — Clean up if needed
4. **test-writer** — Add edge case tests (if not covered by TDD)

### Bugfix Workflow
1. **explain** — Understand the code that has the bug
2. **debug-fix** — Reproduce, fix, test
3. **test-writer** — Add regression test (if not covered)

### Code Improvement Workflow
1. **explain** — Understand what you're improving
2. **refactor** — Restructure
3. **test-writer** — Verify nothing broke

---

## Quick Reference

Need reminders? Ask Codex:

```
Remind me of the TDD workflow.
What should I do for the debug-fix skill?
Which tests should test-writer write?
```

Codex will re-explain any skill on demand.
