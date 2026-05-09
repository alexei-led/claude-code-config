---
name: documenting-code
description: >-
  Update project documentation based on code changes. Use when the user asks to
  update docs, document behavior, add README content, or align docs with recent
  implementation changes.
---

# Documenting Code in Pi

Update docs from code facts, not vibes. Keep docs close to the behavior they
explain.

## Workflow

1. Identify changed files with `git diff --name-only` unless the user supplied
   paths.
2. Read the relevant implementation, tests, and existing docs.
3. Use `context7-cli` only when external API behavior or syntax is uncertain.
4. For large doc audits, launch one bounded `Agent` with `scout` to map changed
   behavior. Verify its claims before editing.
5. Update the smallest set of docs that users or maintainers need.
6. Run docs or repo validation.

## What To Update

- README usage or setup when user-visible behavior changes.
- API docs when parameters, output, or errors change.
- Architecture docs when module boundaries or data flow change.
- Generated catalogs only through their generator scripts.
- Plugin docs when skill, agent, hook, or command behavior changes.

## Rules

- Do not document dead or speculative behavior.
- Do not add promotional filler.
- Prefer examples that can be run.
- Keep private paths or secrets out of docs.
- If docs disagree with code, code wins unless the user says the docs are the
  intended contract.

## Verification

Run the narrowest relevant checks, for example:

```bash
markdownlint-cli2 '**/*.md'
make validate
```

If a tool is missing, state that and run the next available check.
