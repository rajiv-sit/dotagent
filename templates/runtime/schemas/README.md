# Schemas

These schemas define structured output contracts and document templates for projects.

## Included

### Output Contracts

- `job.schema.json`
  - Formal persisted job contract with lifecycle states, input/output sections, and orchestration metadata
- `workflow.schema.json`
  - DAG-oriented workflow contract for chained stages and dependency edges
- `review-output.schema.json`
  - Structures review findings with verdict, severity levels, and verification gaps
- `task-output.schema.json`
  - Structures task completion with facts, inferences, files touched, and risks

### Document Templates

- `requirement.schema.json`
  - Structure for docs/design/Requirement.md: functional/non-functional requirements, constraints, glossary
- `architecture.schema.json`
  - Structure for docs/design/Architecture.md: components, data flows, key decisions, technology stack, quality attributes
- `context.schema.json`
  - Structure for CONTEXT.md durable memory: purpose, key decisions, constraints, risks, important paths, assumptions, domain terms
- `plan.schema.json`
  - Structure for PLAN.md execution tracker: current objective, completed/in-progress/next items, blockers, verification status

## Notes

Schemas are intentionally simple so teams can evolve them without coupling to a plugin runtime. Use them to enforce consistency across projects rather than strict validation.

## Related Docs

- [templates/README.md](../../README.md)
- [runtime/rules/README.md](../rules/README.md)
