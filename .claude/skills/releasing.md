---
description: >
  Cut a release for cc-thingz: bump plugin versions, update CHANGELOG, commit, tag, and push.
  Use when the user says "release", "cut a release", "bump version", "tag vX.Y.Z", or asks
  to publish a new version of the plugins.
name: releasing
---

# Releasing cc-thingz

Cut a new release: CHANGELOG → `scripts/release/release-tag vX.Y.Z` → push.

## CRITICAL: Do NOT use `gh release create`

The GitHub Actions `release.yml` workflow creates the GitHub release automatically
when an annotated tag is pushed. Running `gh release create` before pushing commits
creates the release pointing to the remote HEAD at call time — the wrong commit if
local commits haven't been pushed yet.

**Correct flow**: annotated tag push → CI validates → CI creates release.

## Preflight

1. Ensure working tree is clean: `git status --porcelain`
   - The `release-tag` script fails if the tree is dirty — commit or stash first.
2. Check current version: `grep '^version:' src/plugins/marketplace.yaml`
3. List unreleased commits: `git log $(git describe --tags --abbrev=0)..HEAD --oneline`
4. Determine version bump:
   - **patch** — bug fixes, docs, test cleanup
   - **minor** — new skills, new agents, new hooks, new features
   - **major** — breaking changes to existing skill/hook interfaces

## Update CHANGELOG

Add a `## [X.Y.Z] - YYYY-MM-DD` section under `## [Unreleased]` with `### Added`,
`### Changed`, `### Fixed` as appropriate. The `release-tag` script adds a blank
placeholder if the section is missing, but it's better to write it first.

## Cut the release

```bash
scripts/release/release-tag vX.Y.Z
```

The script: bumps `src/plugins/marketplace.yaml` and all `src/plugins/*/plugin.yaml`,
runs `make build`, commits version bump + CHANGELOG, creates annotated tag `vX.Y.Z`.

## Push

```bash
git push origin master vX.Y.Z
```

The pre-push hook runs the full test suite. If it fails, fix the failures, delete the
local tag (`git tag -d vX.Y.Z`), commit the fixes, recreate the tag, and push again.

Once the push succeeds, GitHub Actions creates the release automatically.

## Recovery: if something went wrong

If the remote tag exists but points to the wrong commit (e.g., `gh release create`
was run before commits were pushed):

```bash
# 1. Delete GitHub release and remote tag
gh release delete vX.Y.Z --yes
gh api -X DELETE repos/<owner>/<repo>/git/refs/tags/vX.Y.Z

# 2. Delete local tag
git tag -d vX.Y.Z

# 3. Fix whatever is broken, commit

# 4. Recreate tag at correct HEAD
git tag -a vX.Y.Z -m "Release X.Y.Z"

# 5. Push
git push origin master vX.Y.Z
```
