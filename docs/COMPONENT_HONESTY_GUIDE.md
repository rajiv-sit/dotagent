# Component Honesty Guide

**Date**: April 16, 2026  
**Purpose**: Be explicit about what each component actually does vs. what its name might suggest  

---

## Components & Their True Purpose

### execution_engine (`executor.py` / `tool_dispatcher.py`)
**What the name suggests**: Full orchestration  
**What it actually does**: Run tools, capture output, handle timeouts  
**Scope**: Deterministic execution only  
**Does NOT do**: Reason about results, plan next steps  

**Correct usage**:
```python
executor.run_tool("write_file", {"path": "code.py", "content": "..."})
# Returns: {"exit_code": 0, "stdout": "...", "stderr": "..."}
# Nothing more
```

---

### output_validator (`output_validator.py`)
**What the name suggests**: Determine if output solves the problem  
**What it actually does**: Check output properties (syntax, format, tests pass)  
**Scope**: Property validation only  
**Does NOT do**: Decide if solution is correct or appropriate  

**Correct usage**:
```python
validator.validate(step, result)
# Returns: {
#   "syntax_valid": true,
#   "tests_pass": true,
#   "files_exist": true,
#   "errors": [...]
# }
# Tells LLM "output is syntactically valid"
# Does NOT tell LLM "solution is correct"
```

---

### failure_analyzer (`failure_analyzer.py`)
**What the name suggests**: Understand why failures happen  
**What it actually does**: Extract error messages and suggest surface fixes  
**Scope**: Pattern matching on error text  
**Does NOT do**: Root cause analysis, strategic decision-making  

**Correct usage**:
```python
analyzer.analyze_failure(result)
# Returns: {
#   "error_type": "SyntaxError",
#   "detail": "Line 15: missing colon",
#   "suggestion": "Add colon at end of line 15"
# }
# Tells LLM "there's a syntax error here"
# Does NOT tell LLM "this approach is wrong"
```

---

### dag_planner (`dag_planner.py`)
**What the name suggests**: Intelligent problem decomposition  
**What it actually does**: Split goal string on separators, template-based task generation  
**Scope**: Text pattern matching  
**Does NOT do**: Understand problem structure, reason about architecture  

**Correct usage**:
```python
planner.decompose("Build UI + backend")
# Returns: [
#   Task(name="UI", depends_on=[]),
#   Task(name="backend", depends_on=[]),
#   Task(name="integrate", depends_on=["UI", "backend"])
# ]
# Tells LLM "here's a suggested task breakdown"
# LLM must verify this makes sense
```

---

### memory_integration (`memory_integration.py`)
**What the name suggests**: Learn from experience  
**What it actually does**: Store error text, retrieve similar errors  
**Scope**: TF-IDF keyword matching  
**Does NOT do**: Extract learnings, build knowledge, improve over time independently  

**Correct usage**:
```python
memory.retrieve_lessons("Write authentication")
# Returns: [
#   "Previous auth task: missing import jwt",
#   "Previous auth task: needs async/await handling"
# ]
# Tells LLM "here are previous related issues"
# LLM must decide what to do with that information
```

---

### state_manager (`state_store.py` / `orchestrator.py`)
**What the name suggests**: Manage workflow state  
**What it actually does**: Write/read JSON files with job records  
**Scope**: Persistence and retrieval  
**Does NOT do**: Reason about state, make decisions based on state  

**Correct usage**:
```python
state.save_job(job)  # Save job record to JSON
state.read_job(job_id)  # Retrieve job record from JSON
# No intelligence, just I/O
```

---

## What's Currently Mislabeled

| Current Name | Suggests | Actually Is |
|---|---|---|
| `dag_planner` | Smart decomposition | Text pattern splitter |
| `failure_analyzer` | Root cause analysis | Error text extractor |
| `memory_integration` | Learning system | TF-IDF keyword matcher |
| `output_validator` | Correctness checking | Property validator |

**Not wrong.** Just confusing names for what they actually do.

---

## Recommended Refactoring

For clarity, consider renaming:

```
dag_planner.py           → workflow_generator.py
failure_analyzer.py      → error_formatter.py
memory_integration.py    → context_retriever.py
output_validator.py      → keep (acceptable as is)
tool_dispatcher.py       → execution_engine.py
```

But only if you want to be more precise. Current names are acceptable if you accept the limitations.

---

## The Key Insight

**These components are not intelligent.** They are:

- `workflow_generator`: Takes a string, returns a template task list
- `error_formatter`: Takes stderr, returns readable error description
- `context_retriever`: Takes a query, returns similar past errors
- `execution_engine`: Runs tool, returns output
- `property_validator`: Checks output properties

**None of them reason, learn, or decide.**

That's OK. It's actually better to be honest about that.

---

## What This Means for Users

When you use dotagent:

✅ **Expect**: Reliable tool execution, comprehensive validation, clear feedback  
✅ **Get**: Deterministic orchestration, property checking, detailed error reports  

❌ **Don't expect**: Autonomous problem-solving, independent learning, intelligent decisions  
❌ **Won't get**: Reasoning, strategic adaptation, self-improvement  

**Those come from the external LLM.** That's the correct split.

