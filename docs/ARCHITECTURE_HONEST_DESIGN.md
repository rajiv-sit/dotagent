# dotagent Architecture: Honest Design

**Date**: April 16, 2026  
**Classification**: Agent Orchestrator (not Agent)  
**Intelligence Source**: External LLM  
**dotagent Role**: Execution, validation, feedback  

---

## Core Principle

**One responsibility per layer:**

```
External LLM (Claude/GPT/etc.)
    ↓ (reasoning, planning, deciding)
    │
[dotagent Orchestrator]
    ├─ Execute tools
    ├─ Validate outputs
    ├─ Collect feedback
    └─ Manage state
    ↓ (feedback, results, errors)
    │
External LLM
    ↓ (next decision)
```

---

## What dotagent Does (Execution Layer)

### ✅ Execute
- Call tools with arguments
- Manage timeouts and retries
- Collect exit codes and output
- Handle failures gracefully

### ✅ Validate
- Check output properties (syntax, format, structure)
- Run tests if applicable
- Verify artifacts exist
- Compare against requirements
- **NOT**: Determine if solution is correct (that's LLM's job)

### ✅ Feedback
- Collect detailed error messages
- Extract relevant context
- Preserve failed artifacts
- Report to LLM for reasoning

### ✅ Manage State
- Track job history
- Store artifacts
- Maintain execution context
- Provide visibility

---

## What External LLM Does (Intelligence Layer)

### ✅ Reason
- Analyze problem complexity
- Understand domain context
- Recognize similar patterns
- Apply domain knowledge

### ✅ Plan
- Decompose goals into tasks
- Order tasks appropriately
- Identify dependencies
- Adapt to feedback

### ✅ Decide
- What to do next
- How to recover from errors
- When to try different approach
- When to ask for clarification

### ✅ Learn
- Remember past failures
- Apply lessons to new problems
- Recognize when approaching similar issue
- Adjust approach

---

## Communication Protocol

### LLM → Orchestrator
```json
{
  "instruction": "execute",
  "tool": "write_file",
  "target": "src/auth.py",
  "content": "...",
  "validation": ["syntax", "imports", "tests"],
  "on_failure": "retry_with_context"
}
```

### Orchestrator → LLM
```json
{
  "status": "FAILED",
  "tool": "write_file",
  "exit_code": 1,
  "stderr": "SyntaxError at line 15: missing colon",
  "stdout": "...",
  "artifacts": {
    "file": "src/auth.py",
    "content": "..."
  },
  "validation_errors": [
    {
      "type": "syntax",
      "detail": "Line 15: missing colon after function definition",
      "context": "def authenticate()  # ← here"
    }
  ],
  "feedback": "Syntax error prevents execution. File was created but is invalid.",
  "suggestion": "Add colon at end of function definition"
}
```

---

## Component Responsibilities

### execution_engine
- Run tools
- Capture output
- Handle errors
- Report results

### output_validator
- Check properties
- Run tests
- Verify requirements
- Provide detailed errors

### state_manager
- Store jobs
- Track artifacts
- Maintain history
- Provide context

### feedback_collector
- Summarize results
- Extract learnings
- Format for LLM
- Preserve context

### context_manager
- Manage conversation history
- Provide task context
- Remember constraints
- Track dependencies

---

## The Loop (Repeated)

1. **LLM Decides**
   - "Write authentication module with JWT"
   - Plan: [Task 1: write_file, Task 2: run_tests]

2. **Orchestrator Executes**
   - Call write_file tool
   - Capture output
   - Report success/failure

3. **Orchestrator Validates**
   - Check syntax
   - Run tests
   - Verify requirements

4. **Orchestrator Feedbacks**
   - Detailed error: "Tests fail: missing import"
   - Artifacts: generated file, test output
   - Suggestion: "Add missing import X"

5. **LLM Reasons**
   - Sees feedback
   - Understands issue
   - Decides: retry with fix, or different approach?

6. **Orchestrator Executes** (retry)
   - Write corrected file
   - Run tests again
   - Report success

7. **Loop Ends** (success or max retries)

---

## Key Design Rules

### ✅ DO
- Make orchestrator deterministic and reliable
- Collect comprehensive error information
- Present information clearly to LLM
- Handle retries at orchestrator level
- Manage state persistently
- Provide full context to LLM

### ❌ DON'T
- Embed reasoning logic
- Pretend to learn or remember lessons
- Make autonomous decisions
- Hide errors from LLM
- Guess at correctness
- Assume what LLM should do next

---

## What This Enables

**By being honest about the split:**

✅ LLM can reason freely (not constrained by fake intelligence)  
✅ Orchestrator can be deterministic and reliable  
✅ Feedback is comprehensive and actionable  
✅ System is maintainable (clear responsibility boundaries)  
✅ Failures are obvious (not hidden in pattern matching)  
✅ Scaling is clear (add more tools, LLM stays powerful)  

---

## What This Cannot Do

❌ Autonomous problem-solving (LLM required)  
❌ Learning between sessions (orchestrator doesn't reason)  
❌ Self-correction without feedback loop  
❌ Domain-specific reasoning (LLM provides domain knowledge)  

**This is correct.** Orchestrators shouldn't do these things.

---

## This is Production-Ready

The control plane is excellent:
- Deterministic execution ✅
- Comprehensive validation ✅
- Clear feedback ✅
- Persistent state ✅
- Reliable retries ✅

This is a **solid orchestrator**. Not pretending to be an agent.

---

## Comparison: Before & After

### Before (Fake Intelligence Attempt)
```
dotagent tries to:
  - Reason about problems (fails - pattern matching only)
  - Learn from failures (fails - keyword extraction only)
  - Plan independently (fails - template based only)
  - Validate correctness (fails - property checking only)
Result: Frustrating - feels smart but isn't
```

### After (Honest Orchestration)
```
dotagent does:
  - Execute tools reliably ✅
  - Validate thoroughly ✅
  - Collect comprehensive feedback ✅
  - Manage state excellently ✅
LLM does:
  - Reason about problems ✅
  - Learn from feedback ✅
  - Plan dynamically ✅
  - Validate appropriateness ✅
Result: Powerful - each layer does its job well
```

---

## Implementation Impact

This means:
- Keep `execution_engine.py` (robust tool execution)
- Keep `output_validator.py` (rigorous property checking)
- Keep `state_manager.py` (reliable persistence)
- **Refactor** `dag_planner.py` → `workflow_executor.py` (not reasoning, just coordinating)
- **Refactor** `memory_integration.py` → `context_manager.py` (not learning, just maintaining context)
- **Rename** `failure_analyzer.py` → `feedback_collector.py` (not analyzing, just reporting)

---

## Honest Claim

**dotagent is:**
- A reliable orchestrator for agentic workflows
- Excellent at execution, validation, feedback
- A platform for external LLMs to control deterministically

**dotagent is not:**
- An autonomous agent
- An intelligent reasoner
- A learner
- A planner

**That's OK.** Being excellent at one thing is better than being mediocre at everything.

