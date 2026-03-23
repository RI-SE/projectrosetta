# Project Rosetta Roadmap & Future Improvements

This document outlines recommended next steps and enhancements for the Project Rosetta repository.

## Near-Term Priorities

### Architecture Documentation

**Why:** External contributors need to understand the system design and scope to contribute effectively.

**Action:** Create `docs/architecture/`:

- System overview and component diagram
- Data flow (scenario → test track → correlation)
- Key interfaces and formats (OpenSCENARIO, OpenDRIVE)
- Design decisions and rationale

## Medium-Term Enhancements

### Code Quality

- **Type hints + mypy** — Add Python type annotations and enforce with CI
- **Unit tests** — Establish test directory structure, run tests in CI
- **Code coverage** — Track % of code tested, set minimum thresholds
- **Integration tests** — Test scenario transformations end-to-end

### Documentation

- **API/Interface reference** — Formal specification for scenario formats
- **Usage examples** — Sample scenarios and step-by-step walkthroughs
- **Troubleshooting guide** — Common issues and solutions
- **Contributing guide expansions** — Naming conventions, code style details

### Project Visibility

- **Roadmap** — Public priorities and planned features (linked from README)
- **Release process** — Semantic versioning, changelog automation
- **Community guidelines** — Decision-making process, RFCs for major changes

## Project-Specific Tasks

### For Scenario Correlation

1. Document correlation metric definitions formally
2. Provide reference implementations with test cases
3. Include sample input/output files for testing
4. Create validation tooling for scenario format compliance

### For Test Track Integration

1. Define robot file format requirements
2. Provide transformation examples (OpenSCENARIO → robot format)
3. Document known limitations and edge cases

### For Community Growth

1. Add "good first issue" labels to encourage new contributors
2. Create starter tasks for onboarding
3. Consider a CONTRIBUTORS.md file to acknowledge contributors

## Setup Instructions

When ready, implement in this order...

## Current Status

✅ **Already in place:**

- Branch governance (CCB-only merge to main)
- Python lint/format (ruff)
- Markdown lint (markdownlint-cli2)
- Contributing guide with quality standards
- Professional README and docs structure
- GitHub issue and PR templates
- Pre-commit hooks

⏳ **Not yet started:**

- Architecture documentation
- All medium-term enhancements listed above

---

For questions or discussion about priorities, open an issue on GitHub.
