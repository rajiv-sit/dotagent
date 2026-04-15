# GitHub Actions Integration

Enforce dotagent standards in CI/CD with GitHub Actions workflows.

## Overview

GitHub Actions can:
- Verify design docs exist before merging
- Check PLAN.md was updated with completion
- Enforce rules via linters and tests
- Generate coverage reports
- Block PRs that break standards

## Basic Validation Workflow

Create `.github/workflows/dotagent-validate.yml`:

```yaml
name: dotagent Validation

on:
  pull_request:
    branches: [main]

jobs:
  validate-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Check required root docs exist
        run: |
          files=(CONTEXT.md PLAN.md Requirement.md Architecture.md HLD.md DD.md milestone.md)
          missing=()
          for file in "${files[@]}"; do
            if [ ! -f "$file" ]; then
              missing+=("$file")
            fi
          done
          if [ ${#missing[@]} -gt 0 ]; then
            echo "âŒ Missing required docs: ${missing[*]}"
            exit 1
          fi
          echo "âœ“ All required docs present"
      
      - name: Check CONTEXT.md has Key Decisions
        run: |
          if ! grep -q "## Key Decisions" CONTEXT.md; then
            echo "âŒ CONTEXT.md missing 'Key Decisions' section"
            exit 1
          fi
          echo "âœ“ CONTEXT.md properly formatted"
      
      - name: Check PLAN.md updated
        run: |
          # Modified if changed in this PR
          if git diff origin/main -- PLAN.md | grep -q "^+"; then
            echo "âœ“ PLAN.md was updated in this PR"
          else
            echo "âš ï¸  PLAN.md was not updated. Did you forget to record completion?"
          fi
      
      - name: Verify Architecture.md has Components section
        run: |
          if ! grep -q "## Components" Architecture.md; then
            echo "âš ï¸  Architecture.md missing 'Components' section"
            exit 1
          fi
          echo "âœ“ Architecture.md has Components"
```

## Language-Specific Rules Enforcement

### Python + pytest

```yaml
  test-coverage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      
      - name: Install dependencies
        run: pip install -r requirements.txt pytest pytest-cov
      
      - name: Run tests with coverage
        run: pytest --cov=src --cov-report=xml --cov-report=term
      
      - name: Enforce coverage threshold
        run: |
          coverage_pct=$(grep 'data-coverage=' coverage.xml | \
            sed 's/.*data-coverage="\([^"]*\)".*/\1/')
          echo "Coverage: ${coverage_pct}%"
          if (( ${coverage_pct%.*} < 80 )); then
            echo "âŒ Coverage below 80%: ${coverage_pct}%"
            exit 1
          fi
          echo "âœ“ Coverage meets threshold"
      
      - name: Lint with flake8
        run: flake8 src --max-line-length=100 --count --exit-zero-on-exit
```

### Node.js + Jest

```yaml
  test-coverage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run tests with coverage
        run: npm run test -- --coverage
      
      - name: Check line coverage >= 80%
        run: |
          coverage=$(npx nyc report | grep 'Lines')
          percentage=$(echo $coverage | grep -oP '\d+(?=%)' | head -1)
          if [ "$percentage" -lt 80 ]; then
            echo "âŒ Coverage $percentage% below 80%"
            exit 1
          fi
          echo "âœ“ Coverage: $percentage%"
      
      - name: Lint with ESLint
        run: npm run lint
      
      - name: Type check with TypeScript
        run: npm run type-check
```

### Java + Maven

```yaml
  test-coverage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-java@v3
        with:
          java-version: '17'
          distribution: 'temurin'
      
      - name: Run tests with coverage
        run: mvn clean test jacoco:report
      
      - name: Check JaCoCo coverage
        run: |
          coverage=$(grep -oP 'covered="\K[^"]*' target/site/jacoco/index.html | head -1)
          if [ $(echo "$coverage < 0.80" | bc) -eq 1 ]; then
            echo "âŒ Coverage below 80%"
            exit 1
          fi
          echo "âœ“ Coverage: $(echo "$coverage * 100" | bc)%"
      
      - name: Run SpotBugs
        run: mvn spotbugs:check
```

## Rules & Standards Enforcement

### Custom Rules Lint

```yaml
  rules-validation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Check code follows .agent/rules
        run: |
          echo "Checking .agent/rules/"
          if [ ! -d ".agent/rules" ]; then
            echo "âš ï¸  No .agent/rules directory"
            exit 0
          fi
          
          rules_count=$(ls .agent/rules/*.md 2>/dev/null | wc -l)
          echo "âœ“ Found $rules_count rule files"
          
          if grep -r "TODO" src/ 2>/dev/null; then
            echo "âš ï¸  Found TODO comments (consider opening issues instead)"
          fi
```

### Security Checks

```yaml
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Check no secrets in code
        run: |
          # Check for common secret patterns
          patterns=(
            'api_key.*='
            'password.*='
            'secret.*='
            'token.*='
          )
          found=0
          for pattern in "${patterns[@]}"; do
            if grep -ri "$pattern" src/ --include="*.js" --include="*.py" --include="*.java" --include="*.ts"; then
              echo "âŒ Potential secret found"
              found=1
            fi
          done
          [ $found -eq 0 ] && echo "âœ“ No secrets detected"
          exit $found
      
      - uses: dependabot/github-actions@main
```

## PR Checks Summary

```yaml
  pr-summary:
    runs-on: ubuntu-latest
    if: always()
    needs: [validate-docs, test-coverage, rules-validation, security]
    steps:
      - name: PR Check Summary
        run: |
          echo "## dotagent CI/CD Summary"
          echo ""
          echo "âœ“ Docs validated"
          echo "âœ“ Tests passed (${{ env.COVERAGE }}% coverage)"
          echo "âœ“ Rules checked"
          echo "âœ“ Security verified"
          echo ""
          echo "Ready to merge!"
```

## Block Merge on Failure

Add branch protection rule in GitHub:
1. Go to Settings â†’ Branches
2. Add rule for main/master
3. Require status checks to pass:
   - `dotagent Validation / validate-docs`
   - `dotagent Validation / test-coverage`
   - `dotagent Validation / rules-validation`

## Review Checklist Comment

Post automated comment on PRs:

```yaml
  add-checklist:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Comment PR with dotagent checklist
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `## dotagent Review Checklist

- [ ] PLAN.md updated with completion
- [ ] CONTEXT.md updated if decisions changed
- [ ] Tests added for new behavior
- [ ] Code follows .agent/rules/
- [ ] No secrets or hardcoded keys
- [ ] Documentation updated

See [Using Skills](./using-skills.md) for workflow guides.`
            })
```

## Real-World Example: Node.js Full Stack

Complete workflow for a typescript/react project:

```yaml
name: dotagent CI/CD

on: [push, pull_request]

jobs:
  docs:
    runs-on: ubuntu-latest
    name: Documentation
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
      
      - name: Check docs exist
        run: |
          for doc in CONTEXT.md PLAN.md Requirement.md Architecture.md; do
            test -f "$doc" || {
              echo "âŒ Missing $doc"
              exit 1
            }
          done
          echo "âœ“ All required docs present"
      
      - name: Check PLAN.md changed
        run: |
          if git diff origin/main...HEAD -- PLAN.md | grep -q "Completed"; then
            echo "âœ“ PLAN.md was updated"
          else
            echo "âš ï¸ PLAN.md not updated - did you record completion?"
          fi

  lint:
    runs-on: ubuntu-latest
    name: Lint & Type Check
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - run: npm ci
      - run: npm run lint
      - run: npm run type-check

  test:
    runs-on: ubuntu-latest
    name: Tests & Coverage
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - run: npm ci
      - run: npm run test -- --coverage
      
      - name: Report Coverage
        run: |
          coverage=$(npx nyc report | grep Lines | grep -oP '\d+(?=%)' | head -1)
          echo "Coverage: $coverage%"
          if [ "$coverage" -lt 80 ]; then
            echo "âŒ Coverage $coverage% below 80%"
            exit 1
          fi

  security:
    runs-on: ubuntu-latest
    name: Security
    steps:
      - uses: actions/checkout@v3
      
      - name: Check for secrets
        run: |
          if grep -r "process.env\." src/ | grep -v "process.env\.NODE_ENV" | wc -l | grep -v "^0$"; then
            echo "â„¹ï¸  Environment variables detected - ensure they're secure"
          fi
      
      - name: Audit dependencies
        run: |
          if npm audit --audit-level=moderate 2>&1 | grep -q "found.*vulnerabilities"; then
            echo "âš ï¸  Vulnerabilities detected - review above"
          fi

  build:
    runs-on: ubuntu-latest
    name: Build
    needs: [test, lint]
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - run: npm ci
      - run: npm run build
      - run: npm run build-storybook  # if you have storybook
```

## Tips

- **Fail fast:** Put cheapest checks first (docs, lint) before expensive tests
- **Informative messages:** Include links to guides ([Quick Start](quick-start.md), [FAQ](faq.md))
- **Don't over-enforce:** Warnings for soft requirements, errors for hard requirements
- **Token efficiency:** Cache node_modules, pip packages, Maven artifacts
- **Gradient enforcement:** Start lenient (warn on PLAN.md not updated), then stricter over time

## Next Steps

- Set up CI/CD using template above
- Configure branch protection rules
- Add PR checklist comment
- Review [Troubleshooting > GitHub Actions](troubleshooting.md#issue-github-actions-integration) if issues arise

