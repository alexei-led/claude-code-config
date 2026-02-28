# Changelog

All notable changes to this Claude Code configuration are documented here.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html):
major = breaking config/hook changes, minor = new skills/features, patch = fixes.

## [1.0.0] - 2026-02-28

Initial versioned release of the Claude Code configuration.

### Added

- 23 skills: brainstorming, committing, debating, deploying-infra, documenting,
  evolving-config, fixing, improving-tests, learning-patterns, looking-up-docs,
  managing-infra, refactoring, researching-web, reviewing, searching,
  testing-e2e, using-cloud-cli, using-git-worktrees, using-modern-cli,
  writing-go, writing-python, writing-typescript, writing-web
- 14 agents for Go, Python, TypeScript, web, infrastructure, and planning
- Spec-driven development system (specctl + spec skills)
- Environment switcher (`ce`) supporting 6 providers
- CI workflow with config validation, linting, and tests
- Global CLAUDE.md with universal development practices
- Project CLAUDE.md with config-repo-specific guidance
- Git hooks: gitleaks pre-commit, enforcer post-tool-use
