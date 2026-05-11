# Learn from Session

## Phase 1: Discover

Read existing Claude Code customization files:

- `CLAUDE.md` or `.claude/CLAUDE.md` — project memory
- `.claude/skills/*/SKILL.md` — project skills
- `.claude/agents/*.md` — project subagents
- `.claude/commands/*.md` — project commands
- `.claude/settings.json` — hooks and permissions
- `.claude/rules/*.md` — rules (if used)
- `CONTEXT.md`, `CONTEXT-MAP.md` — domain language
- `docs/adr/*.md` — durable decisions
- `.out-of-scope/*.md` — rejected scope with reasoning

Record counts for the budget check.

## Phase 3: Categorize

Pick exactly one target per learning:

- Reusable workflow or coding instruction → `CLAUDE.md` or `.claude/CLAUDE.md`
- Domain term → `CONTEXT.md`
- Hard-to-reverse decision with real trade-off → `docs/adr/NNNN-slug.md`
- Repeated multi-step workflow → `.claude/skills/<name>/SKILL.md`
- Blocking, validation, or approval automation → `.claude/settings.json` hooks
- Rejected feature with reasoning → `.out-of-scope/<concept>.md`

If no target is justified, drop the learning.
