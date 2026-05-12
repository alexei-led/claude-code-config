---
description: >
  Cut a release for cc-thingz: bump plugin versions, update CHANGELOG, commit, tag, and push.
  Use when the user says "release", "cut a release", "bump version", "tag vX.Y.Z", or asks
  to publish a new version of the plugins.
name: releasing
---

# Releasing cc-thingz

Cut a new release: version bump, CHANGELOG, tag, push. Script: `scripts/release/release-tag`.

## Preflight

1. Check current version: `grep '^version:' src/plugins/marketplace.yaml`
2. List unreleased commits: `git log $(git describe --tags --abbrev=0)..HEAD --oneline`
3. Confirm the working tree is clean: `git status --porcelain`
   - If dirty: commit or stash pending changes first, then return here.
4. Determine the version bump (user provides it or suggest based on commits):
   - **patch** — bug fixes, docs, test cleanup, dependency updates
   - **minor** — new skills, new hooks, new features
   - **major** — breaking changes to existing skill/hook interfaces

## CHANGELOG

Update `CHANGELOG.md` before running the script:

- Add a `## [X.Y.Z] - YYYY-MM-DD` section under `## [Unreleased]`
- Summarize commits under `### Added`, `### Changed`, `### Fixed` as appropriate
- Commit: `git add CHANGELOG.md && git commit -m "docs: update changelog for vX.Y.Z"`

## Cut the release

```bash
scripts/release/release-tag vX.Y.Z
```

The script: bumps `src/plugins/marketplace.yaml` and all `src/plugins/*/plugin.yaml`, runs
`make build` to regenerate `dist/`, commits version bump, creates annotated tag.

## Push

```bash
git push origin master vX.Y.Z
```

The pre-push hook auto-commits any stale `dist/` before pushing.

## If anything goes wrong

- Tag already exists: `git tag -d vX.Y.Z` then rerun.
- `make build` fails: fix the build error, `git stash` if needed, rerun `release-tag`.
- Working tree not clean when running script: commit or stash the pending change first.
