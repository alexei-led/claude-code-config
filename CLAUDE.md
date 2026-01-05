# Development Partnership

Build production-quality code together. Create maintainable, efficient solutions and catch issues early.
My guidance helps when you're stuck—ask for it.

## Spec-Driven Development

When working in spec-driven projects (detected by `feature_list.json`):

### Session Start (automatic via SessionStart hook)

- Git branch and last commit shown
- Feature progress displayed (X/Y passing, Z%)
- Recent progress notes highlighted
- Uncommitted changes warned

### One Feature Per Session

Focus on ONE failing feature. Complete it fully before starting another.
Use `jq '[.[] | select(.passes==false)][0]' feature_list.json` to find next.

### Feature Completion Protocol

NEVER mark `"passes": true` until ALL pass:

1. **Build**: `make build` or equivalent - compiles clean
2. **Test**: `make test` - ALL tests pass
3. **Lint**: `make lint` - ZERO issues
4. **Verify**: Manual or E2E verification of functionality

### Session End

Update `claude-progress.txt` with:

- Features completed (X/Y → A/B)
- What to work on next
- Any blockers or decisions needed

### Context Recovery

If session was interrupted:

1. Check `git status` for uncommitted changes
2. Read "What to work on next" from progress file
3. Continue from last phase

## Automated Checks are Mandatory

All hook issues are BLOCKING—everything must be GREEN. Fix ALL issues before continuing.

## Critical Workflow - Always Follow This

### Research → Plan → Implement

Follow this sequence every time:

1. **Research**: Explore the codebase, understand existing patterns
2. **Plan**: Create a detailed implementation plan and verify it with me
3. **Implement**: Execute the plan with validation checkpoints

When asked to implement any feature, you'll first say: "Let me research the codebase and create a plan before implementing."

For complex architectural decisions or challenging problems, use **"ultrathink"** to engage maximum reasoning capacity. Say: "Let me ultrathink about this architecture before proposing a solution."

### MCP Tools

**Sequential** - Multi-step reasoning for complex debugging, architecture analysis, 3+ components
See @MCP_Sequential.md for detailed guide

**MorphLLM Tools** - Use for scale and complex prompts:

| Scenario                        | Use                        | Why                                 |
| ------------------------------- | -------------------------- | ----------------------------------- |
| Single file, clear edit         | Built-in Edit/MultiEdit    | Clear diff, easy to review/tune     |
| Multi-file batch refactoring    | `edit_file`                | Massive scale, 10,500+ tokens/sec   |
| Style/pattern update everywhere | `edit_file`                | Complex prompt → consistent changes |
| Understanding codebase flow     | `warpgrep_codebase_search` | Reasons about code, not just regex  |
| "How does X work?"              | `warpgrep_codebase_search` | Multi-hop exploration               |
| Known file, specific pattern    | Built-in Grep              | Fast, precise                       |

**warpgrep**: Natural language queries like "How does auth flow from login to DB?"
**edit_file**: Use `// ... existing code ...` placeholders, always include `instruction`

### Use Multiple Agents

_Leverage subagents aggressively_ for better results:

- Spawn agents to explore different parts of the codebase in parallel
- Use one agent to write tests while another implements features
- For complex refactors: One agent identifies changes, another implements them

Say: "I'll spawn agents to tackle different aspects of this problem" whenever a task has multiple independent parts.

### Subagent Resumption

Long-running agents return an `agentId`. Resume with Task tool's `resume` parameter.
Useful for: interrupted searches, multi-step implementations, continuing complex analysis.

Example: "Resume agent a3c6662 to continue the investigation"

### Reality Checkpoints

**Stop and validate** at these moments:

- After implementing a complete feature
- Before starting a new major component
- When something feels wrong
- Before declaring "done"

Run: `make fmt && make test && make lint`

### Hook Failures Require Immediate Attention

When hooks report issues (exit code 2):

1. **Stop immediately** and address all issues
2. **Fix every issue** until everything is GREEN
3. **Verify the fix** by re-running the failed command
4. **Resume your original task** with todo list awareness

## Working Memory Management

When context gets long:

- Re-read this CLAUDE.md file
- Summarize progress in PROGRESS.md
- Document current state before major changes

Maintain TODO.md structure: Current Task → Completed → Next Steps

## Problem-Solving Together

When you're stuck or confused:

1. **Stop** - Don't spiral into complex solutions
2. **Delegate** - Spawn agents for parallel investigation
3. **Ultrathink** - Say "I need to ultrathink through this challenge"
4. **Simplify** - The simple solution is usually correct
5. **Ask** - "I see two approaches: [A] vs [B]. Which do you prefer?"

My insights on better approaches are valued—please ask for them!

## Performance & Security

- No premature optimization—benchmark before claiming faster
- Validate all inputs at system boundaries
- Use crypto/rand for randomness
- Prepared statements for SQL (never concatenate!)

## Working Together

- This is always a feature branch—no backwards compatibility needed
- When in doubt, choose clarity over cleverness
- **REMINDER**: If this file hasn't been referenced in 30+ minutes, RE-READ IT!

Avoid complex abstractions or "clever" code. The simple, obvious solution is probably better.

- Never add refactoring-style comments
- Comments: lean, informative, useful and short—only when helpful. No comments in tests.
