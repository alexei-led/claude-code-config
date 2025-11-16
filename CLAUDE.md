# Development Partnership

Build production-quality code together. Create maintainable, efficient solutions and catch issues early.
My guidance helps when you're stuck—ask for it.

## Automated Checks are Mandatory

All hook issues are BLOCKING—everything must be GREEN. No errors, formatting issues, or linting problems. Fix ALL issues before continuing.

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
**Morphllm** - Bulk pattern edits across files (style enforcement, framework updates)
See @MCP_Sequential.md and @MCP_Morphllm.md for detailed guides

### Use Multiple Agents

_Leverage subagents aggressively_ for better results:

- Spawn agents to explore different parts of the codebase in parallel
- Use one agent to write tests while another implements features
- Delegate research tasks: "I'll have an agent investigate the database schema while I analyze the API structure"
- For complex refactors: One agent identifies changes, another implements them

Say: "I'll spawn agents to tackle different aspects of this problem" whenever a task has multiple independent parts.

### Reality Checkpoints

**Stop and validate** at these moments:

- After implementing a complete feature
- Before starting a new major component
- When something feels wrong
- Before declaring "done"
- **WHEN HOOKS FAIL WITH ERRORS** ❌

Run: `make fmt && make test && make lint`

> Why: You can lose track of what's actually working. These checkpoints prevent cascading failures.

### Hook Failures Require Immediate Attention

When hooks report any issues (exit code 2):

1. **Stop immediately** and address all issues
2. **Fix every issue** until everything is GREEN
3. **Verify the fix** by re-running the failed command
4. **Resume your original task** with awareness of what you were doing
5. **Track both** the fix and original task in the todo list

This includes formatting issues, linting violations, and pattern checks. Your code must be 100% clean before proceeding.

## Code Editing Guidelines

IMPORTANT: ALWAYS use `mcp__morphllm-fast-apply__edit_file` tool to make any code edits.

## Modern CLI Tools

Use `fd` (find files), `rg` (grep text), `sg` (code structure), `bat` (view files), `jq`/`yq` (JSON/YAML), `sd` (find/replace), `lazygit` (interactive git).

## Working Memory Management

### When context gets long

- Re-read this CLAUDE.md file
- Summarize progress in PROGRESS.md
- Document current state before major changes

### Maintain TODO.md structure

Current Task → Completed → Next Steps

## Go-Specific Rules

### Code Patterns - Automated Enforcement

The smart-lint hook enforces these patterns:

- **Use concrete types** instead of interface{} or any{}
- **Use channels for synchronization** instead of time.Sleep()
- **Delete old code** when replacing it
- **Avoid migration functions** or compatibility layers
- **Use direct names** instead of versioned functions (processV2, handleNew)
- **Keep error handling simple** without custom struct hierarchies
- **Remove TODOs** before final code

When you see pattern violations, fix them immediately.

### Required Standards

- **Delete** old code when replacing it
- **Meaningful names**: `userID` not `id`
- **Early returns** to reduce nesting
- **Concrete types** from constructors: `func NewServer() *Server`
- **Simple errors**: `return fmt.Errorf("context: %w", err)`
- **Table-driven tests** for complex logic
- **Channels for synchronization**: Use channels to signal readiness, not sleep
- **Select for timeouts**: Use `select` with timeout channels, not sleep loops

## Implementation Standards

### Our code is complete when

- ? All linters pass with zero issues
- ? All tests pass
- ? Feature works end-to-end
- ? Old code is deleted
- ? Godoc on all exported symbols

### Testing Strategy

- Complex business logic ? Write tests first
- Simple CRUD ? Write tests after
- Hot paths ? Add benchmarks
- Skip tests for main() and simple CLI parsing
- Use table-driven test structure
- Use testify and asserts for test result validation
- Avoid pointless tests

### Project Structure

cmd/ - Application entrypoints
internal/ - Private code (the majority goes here)
pkg/ - Public libraries (only if truly reusable)

## Problem-Solving Together

When you're stuck or confused:

1. **Stop** - Don't spiral into complex solutions
2. **Delegate** - Consider spawning agents for parallel investigation
3. **Ultrathink** - For complex problems, say "I need to ultrathink through this challenge" to engage deeper reasoning
4. **Step back** - Re-read the requirements
5. **Simplify** - The simple solution is usually correct
6. **Ask** - "I see two approaches: [A] vs [B]. Which do you prefer?"

My insights on better approaches are valued - please ask for them!

## Performance & Security

### Measure First

- No premature optimization
- Benchmark before claiming something is faster
- Use pprof for real bottlenecks

### Security Always

- Validate all inputs
- Use crypto/rand for randomness
- Prepared statements for SQL (never concatenate!)

## Communication Protocol

### Progress Updates

✓ Implemented authentication (all tests passing)
✓ Added rate limiting
✗ Found issue with token expiration - investigating

### Suggesting Improvements

"The current approach works, but I notice [observation].
Would you like me to [specific improvement]?"

## Git Commit Standards

### Commit Messages

- **Concise and specific**: "Fix auth token validation" not "fix bug"
- **Present tense**: "Add feature" not "Added feature"
- **Focus on WHY**: "Prevent XSS in user inputs" not "Update validation"
- **Reference issues**: "Fix memory leak (#123)"
- **NO AI attribution** or emoji unless project requires it

Good: "Fix race condition in connection pool"
Bad: "Update code" or "Generated with Claude"

## Working Together

- This is always a feature branch - no backwards compatibility needed
- When in doubt, we choose clarity over cleverness
- **REMINDER**: If this file hasn't been referenced in 30+ minutes, RE-READ IT!

Avoid complex abstractions or "clever" code. The simple, obvious solution is probably better, and my guidance helps you stay focused on what matters.
- never add refactoring-style comments