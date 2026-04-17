# Documentation Guide

This folder contains comprehensive guides for understanding, using, and extending dotagent. Choose your entry point based on your role or question.

## Quick Entry Points

### I'm New to dotagent
Start here for fastest onboarding:
1. [Quick Start](quick-start.md) - 5-minute setup and first task (5 min)
2. [Navigation Hub](index.md) - Find guides by role, question, or time (2 min)
3. [FAQ](faq.md) - Common questions answered (5-10 min)

### I'm Integrating dotagent into My Project
Follow this path:
1. [Migration Guide](migration-guide.md) - Adopt dotagent to an existing project (20 min)
2. [Customize for Your Stack](customize-for-your-stack.md) - Python, JS, Java, microservices (10 min)
3. [Rule Hierarchy](rule-hierarchy.md) - Understand precedence and conflicts (5 min)

### I'm Reviewing or Enhancing dotagent
These guides are for contributors and architects:
1. [Using Skills](using-skills.md) - All 6 reusable workflows with walkthroughs (15 min)
2. [GitHub Actions Integration](github-actions-integration.md) - CI/CD workflows and enforcement (10 min)
3. [Case Study](case-study.md) - Real team metrics and validation (5 min)

### I Need Help or Have Questions
Browse by topic:
- [Troubleshooting](troubleshooting.md) - 20+ solutions for common problems
- [FAQ](faq.md) - 30+ questions and answers
- [Navigation Hub](index.md) - Find anything by role, question, or time

## Guide Index

All guides organized by purpose:

| Guide | Purpose | Audience | Time |
|-------|---------|----------|------|
| [Quick Start](quick-start.md) | Get running in 5 minutes | New users | 5 min |
| [Navigation Hub](index.md) | Find guides by role, question, time | Any | 2 min |
| [FAQ](faq.md) | Common questions answered | Any | 5-10 min |
| [Troubleshooting](troubleshooting.md) | Solve 20+ common issues | Stuck users | 5 min |
| [Migration Guide](migration-guide.md) | Adopt dotagent to existing projects | Team leads | 20 min |
| [Customize for Your Stack](customize-for-your-stack.md) | Config for Python, JS, Java, microservices | Developers | 10 min |
| [Rule Hierarchy](rule-hierarchy.md) | Understand rule conflicts and precedence | Architects | 5 min |
| [Using Skills](using-skills.md) | Learn 6 reusable workflows | Developers | 15 min |
| [GitHub Actions Integration](github-actions-integration.md) | Set up CI/CD and rule enforcement | DevOps | 10 min |
| [Case Study](case-study.md) | Real team metrics and results | Leaders | 5 min |
| [Obsidian Integration](obsidian-integration.md) | Use Obsidian vault for navigation | Knowledge workers | 10 min |
| [Starter Templates](starter-templates.md) | Copy-paste templates for all key docs | New projects | 5 min |
| [CHANGELOG](../CHANGELOG.md) | Version history and what changed | Everyone | 5 min |

## Documentation Organization

```
docs/
|-- README.md (you are here)
|-- quick-start.md - Fastest path to value
|-- index.md - Navigation hub by role/question
|-- faq.md - Common Q&As with answers
|-- troubleshooting.md - Solutions for 20+ issues
|-- migration-guide.md - Adopt to existing projects
|-- customize-for-your-stack.md - Language and framework configs
|-- rule-hierarchy.md - Rule precedence and conflict resolution
|-- using-skills.md - Deep dive into all 6 skills
|-- github-actions-integration.md - CI/CD workflows
|-- case-study.md - Real team metrics and validation
|-- obsidian-integration.md - Obsidian vault setup
`-- starter-templates.md - Copy-paste templates
```

## Reading Order by Role

### Product Manager / Team Lead
1. [Case Study](case-study.md) - Validate business value (5 min)
2. [Quick Start](quick-start.md) - Understand basic flow (5 min)
3. [FAQ](faq.md) - Address team concerns (10 min)
4. [Migration Guide](migration-guide.md) - Plan adoption (20 min)

### Developer
1. [Quick Start](quick-start.md) - Get set up (5 min)
2. [Using Skills](using-skills.md) - Learn workflows (15 min)
3. [Customize for Your Stack](customize-for-your-stack.md) - Configure your language (10 min)
4. [Rule Hierarchy](rule-hierarchy.md) - Understand project rules (5 min)

### Architect / Senior Engineer
1. [Navigation Hub](index.md) - Overview of all docs (2 min)
2. [Rule Hierarchy](rule-hierarchy.md) - Design your rules (5 min)
3. [GitHub Actions Integration](github-actions-integration.md) - Automate enforcement (10 min)
4. [Case Study](case-study.md) - Real-world patterns (5 min)

### DevOps / Infrastructure
1. [GitHub Actions Integration](github-actions-integration.md) - Set up CI/CD (10 min)
2. [Customize for Your Stack](customize-for-your-stack.md) - Understand project types (10 min)
3. [Troubleshooting](troubleshooting.md) - Debug issues (5 min)

### Stuck or Lost
1. [Navigation Hub](index.md) - Find what you need (2 min)
2. [FAQ](faq.md) - Check common questions (5 min)
3. [Troubleshooting](troubleshooting.md) - Find your issue (5 min)

## Document Formats

All guides use consistent formatting:
- **Headings** organize sections
- **Tables** summarize options
- **Code blocks** show examples
- **Bullet lists** present alternatives
- **Links** connect related guides
- **Time estimates** show reading duration

## Feedback and Contributions

To contribute:
- Report missing documentation via GitHub Issues
- Suggest improvements or enhancements
- Submit rules, templates, or skills
- Share case studies or starter templates

## Key Root Files

The main project documentation lives in the root folder:

| File | Purpose |
|------|---------|
| [GRAPH.md](../GRAPH.md) | Component architecture and how everything connects |
| [CHANGELOG.md](../CHANGELOG.md) | Version history, what changed, when |
| [CONTEXT.md](../CONTEXT.md) | Durable project memory (purpose, architecture, decisions) |
| [PLAN.md](../PLAN.md) | Active execution tracker (completed, in-progress, next steps) |
| [AGENTS.md](../AGENTS.md) | Project setup and assistant instructions |
| [README.md](../README.md) | Project overview and getting started |

## Design Docs

The required design artifacts live under [`docs/design/`](design/README.md):

- [Design Docs Hub](design/README.md)
- [Requirement.md](design/Requirement.md)
- [Architecture.md](design/Architecture.md)
- [HLD.md](design/HLD.md)
- [DD.md](design/DD.md)
- [milestone.md](design/milestone.md)

## Maintainer References

If you are extending dotagent itself, use these indexes:

- [Agents Index](../agents/README.md)
- [Rules Index](../rules/README.md)
- [Skills Index](../skills/README.md)
- [Prompts Index](../prompts/README.md)
- [Templates Index](../templates/README.md)
- [Implementation Index](IMPLEMENTATION_INDEX.md)

## Next Steps

1. **New to dotagent?** -> [Quick Start](quick-start.md)
2. **Have a problem?** -> [Troubleshooting](troubleshooting.md)
3. **Want to integrate?** -> [Migration Guide](migration-guide.md)
4. **Need help?** -> [FAQ](faq.md)

