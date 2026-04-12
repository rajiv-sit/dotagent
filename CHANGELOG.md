# Changelog & Version History

All notable changes to dotcodex are documented here.

## [Unreleased]

### Added
- Documentation navigation hub (docs/README.md)
- Link validation script (validate-links.ps1)
- Setup health check script (health-check.ps1)

### Changed
- Improved docs/ folder organization with role-based entry points
- Enhanced FAQ with more stack-specific examples

### Fixed
- Broken links in migration guide examples

---

## [1.0.0] - 2026-04-12

### Release Summary
dotcodex v1.0 is production-ready with comprehensive documentation, validation tools, and community guidelines.

### Added

#### Documentation (15 New Guides)
- **docs/quick-start.md** — 5-minute setup guide
- **docs/index.md** — Navigation hub by role/question/time
- **docs/faq.md** — 30+ questions and answers
- **docs/troubleshooting.md** — Solutions for 20+ issues
- **docs/migration-guide.md** — 5-phase adoption strategy
- **docs/customize-for-your-stack.md** — Python, JS, Java, microservices
- **docs/rule-hierarchy.md** — Rule precedence and conflict resolution
- **docs/using-skills.md** — Deep dive into all 6 skills
- **docs/github-actions-integration.md** — 5 CI/CD workflows
- **docs/case-study.md** — Real team metrics and validation
- **docs/obsidian-integration.md** — Obsidian vault setup
- **docs/starter-templates.md** — Copy-paste templates for all docs
- **docs/README.md** — Documentation orientation guide
- **rules/knowledge-graphs.md** — Knowledge network standards

#### Schemas (4 New JSON Schemas)
- **schemas/requirement.schema.json** — Requirement document template
- **schemas/architecture.schema.json** — Architecture document template
- **schemas/context.schema.json** — CONTEXT.md template
- **schemas/plan.schema.json** — PLAN.md template

#### Automation Scripts
- **scripts/health-check.ps1** — Validate dotcodex setup (8 checks)
- **scripts/validate-links.ps1** — Verify all markdown links work

#### Enhancements
- **hooks/README.md** — Comprehensive hook execution flow documentation
- **agents/README.md** — All 6 specialist agents documented
- **skills/README.md** — Full description of all 6 skills
- **README.md** — Added guide links and "When to use" sections

### Changed

#### Documentation Structure
- Reorganized /docs folder with clear role-based navigation
- Updated all internal cross-references for clarity
- Added time estimates to all guides (5 min to 20 min expected reads)
- Included real case study metrics (2 weeks → 3 days onboarding, 2x token efficiency)

#### Rules & Standards
- Added rule hierarchy documentation (global → project → local precedence)
- Included conflict resolution strategies
- Added testing examples for each rule level

#### Templates
- Created copy-paste starter templates for all root docs
- Added both minimal and comprehensive examples
- Included stack-specific variations (Python, JavaScript, Java)

### Fixed
- Documentation completeness gap (was: limited user guidance, now: 15 comprehensive guides)
- Rule precedence confusion (was: implicit, now: 4-level hierarchy documented)
- Skill discoverability (was: abstract, now: 6 full walkthroughs with examples)
- Integration examples missing (was: none, now: GitHub Actions, Obsidian, Jira)

### Breaking Changes

**None** — dotcodex v1.0 is backward compatible with all prior usage patterns. New documentation and tools are purely additive.

### Dates

**Release Date:** April 12, 2026  
**Documentation Complete:** April 12, 2026  
**Production Ready:** Yes  
**Status:** Stable

---

## Release Versioning

### Version Format
`MAJOR.MINOR.PATCH` following semantic versioning

- **MAJOR** — Breaking changes or major reorganization
- **MINOR** — New features, guides, rules, or significant enhancements
- **PATCH** — Bug fixes, doc updates, correction of links/examples

### When Changes Are Made

#### New Rules Added
- Document in CHANGELOG under "Rules [section]"
- Update `rules/README.md` with new rule description
- Add rule to hierarchy docs if it affects precedence
- Reference from relevant guides (quick-start, customization, etc.)

#### Documentation Reorganized
- Document structure changes in CHANGELOG
- Update `docs/README.md` index
- Verify all internal links still resolve
- Check external references are current

#### Breaking Changes
- Document clearly in CHANGELOG with "BREAKING:"
- Provide migration path if applicable
- Update all affected documentation
- Add upgrade instructions to migration guide

### Maintenance Cadence

| Activity | Frequency | Owner |
|----------|-----------|-------|
| CHANGELOG updates | Per commit | Author |
| Version tagger | Per release | Maintainer |
| Doc review | Per quarter | Community |
| Rule additions | Ad-hoc | Teams |
| Security fixes | ASAP | Maintainer |

---

## Archive

### Previous Releases (Pre-v1.0)

**v0.x (Pre-release)**
- Initial dotcodex structure and core agents
- Foundation: AGENTS.md, CONTEXT.md, PLAN.md
- Core rules, skills, and prompts
- Basic README and setup scripts

---

## How to Contribute

### Proposing Changes

1. **Found a bug?**
   - Open GitHub Issue with [BUG] prefix
   - Include version and reproduction steps
   - Reference this CHANGELOG

2. **Have a new rule?**
   - Create rules/your-rule.md
   - Document in "Rules" section of CHANGELOG
   - Add to rule-hierarchy.md

3. **Want to add documentation?**
   - Create in docs/
   - Update docs/README.md index
   - Add to CHANGELOG "Documentation" section

4. **Major feature or breaking change?**
   - Open GitHub Discussion first
   - Document impact on existing workflows
   - Plan migration path
   - Add detailed entry to CHANGELOG

### CHANGELOG Format

```markdown
## [Version] - YYYY-MM-DD

### Added
- New features or docs

### Changed
- Modifications to existing features

### Fixed
- Bug fixes

### Deprecated
- Soon-to-be-removed features

### Removed
- Removed features

### Breaking Changes
- Major incompatibilities

### Dates
- Release Date: ...
- Status: Stable / Beta / Deprecated
```

---

## Questions?

**About dotcodex?** → See [FAQ](docs/faq.md)  
**About this version?** → Open a GitHub Issue  
**About upgrading?** → See [Migration Guide](docs/migration-guide.md)  
**Found a gap?** → Submit an enhancement
