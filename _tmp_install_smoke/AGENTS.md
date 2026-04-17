# Project Instructions

## Default Agent

The default operating profile for this project is `.agent/agents/default-agent.md` when present.

If `.agent/agents/default-agent.md` is not present, follow these rules directly.

## Root Docs First

Before substantial implementation, read these root markdown files directly when they exist:

- `CONTEXT.md`
- `PLAN.md`
- `Requirement.md`
- `Architecture.md`
- `HLD.md`
- `DD.md`
- `milestone.md`

If they are missing or incomplete, prefer completing them before major implementation.

## Workflow

- implement one milestone at a time
- validate after each milestone before moving on
- prefer minimal diffs and root-cause fixes
- do not bypass architecture and design context when it exists

## graphify

- if `GRAPH.md` exists, it provides visual architecture and component connections
- complementary to code-level graphs from graphify tool
- shows how agents, rules, skills, hooks, scripts, schemas, and docs connect
- if `graphify-out/GRAPH_REPORT.md` exists, read it before broad architecture or codebase analysis
- if `graphify-out/wiki/index.md` exists, prefer it over broad raw-file exploration
- use graph context as durable project memory when available

## Traceability

- use `CONTEXT.md` as durable project memory across sessions
- use `PLAN.md` as the active execution tracker

## Obsidian

- if project architecture docs live in an Obsidian vault, prefer linked markdown navigation over broad raw-file search
- open `GRAPH.md` in Obsidian to see component connections and network topology
- use Obsidian Graph View (Ctrl+G) to visualize backlinks and relationships
- keep root design notes cross-linked so Obsidian Graph and Local Graph stay useful as low-token navigation tools

## Rules

When present, follow:

- `.agent/rules/code-quality.md`
- `.agent/rules/testing.md`
- `.agent/rules/security.md`
- `.agent/rules/error-handling.md`
- `.agent/rules/frontend.md`

