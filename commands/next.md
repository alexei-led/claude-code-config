---
allowed-tools: all
description: Execute production-quality implementation with strict standards
---

🚨 **CRITICAL WORKFLOW - NO SHORTCUTS!** 🚨

You are tasked with implementing: $ARGUMENTS

**MANDATORY SEQUENCE:**
1. 🔍 **RESEARCH FIRST** - "Let me research the codebase and create a plan before implementing"
2. 📋 **PLAN** - Present a detailed plan and verify approach
3. ✅ **IMPLEMENT** - Execute with validation checkpoints

**YOU MUST SAY:** "Let me research the codebase and create a plan before implementing."

For complex tasks, say: "Let me ultrathink about this architecture before proposing a solution."

**USE MULTIPLE AGENTS** when the task has independent parts:
"I'll spawn agents to tackle different aspects of this problem"

Consult ~/.claude/CLAUDE.md IMMEDIATELY and follow it EXACTLY.

**Critical Requirements:**

🛑 **HOOKS ARE WATCHING** 🛑
The smart-lint.sh hook will verify EVERYTHING. It will:
- Block operations if you ignore linter warnings
- Track repeated violations
- Prevent commits with any issues
- Force you to fix problems before proceeding

**Completion Standards (NOT NEGOTIABLE):**
- The task is NOT complete until ALL linters pass with zero warnings (golangci-lint with all checks enabled)
- ALL tests must pass with meaningful coverage of business logic (skip testing main(), simple CLI parsing, etc.)
- The feature must be fully implemented and working end-to-end
- No placeholder comments, TODOs, or "good enough" compromises

**Reality Checkpoints (MANDATORY):**
- After EVERY 3 file edits: Run linters
- After implementing each component: Validate it works
- Before saying "done": Run FULL test suite
- If hooks fail: STOP and fix immediately

**Code Evolution Rules:**
- This is a feature branch - implement the NEW solution directly
- DELETE old code when replacing it - no keeping both versions
- NO migration functions, compatibility layers, or deprecated methods
- NO versioned function names (e.g., processDataV2, processDataNew)
- When refactoring, replace the existing implementation entirely
- If changing an API, change it everywhere - no gradual transitions

**Language-Specific Quality Requirements:**

**For ALL languages:**
- Follow established patterns in the codebase
- Use language-appropriate linters at MAX strictness
- Delete old code when replacing functionality
- No compatibility shims or transition helpers

**For Go specifically:**
- Absolutely NO interface{} or any{} - use concrete types or properly defined interfaces
- Simple, focused interfaces following the Interface Segregation Principle (prefer many small interfaces over large ones)
- Error handling must use simple error returns or well-established patterns (NO custom error structs unless absolutely necessary)
- Avoid unnecessary type assertions and interface casting - if you need to cast, reconsider your design
- Follow standard Go project layout (cmd/, internal/, pkg/ where appropriate)
- NO time.Sleep() or busy waits - use channels and message passing for synchronization
- Use channels to signal readiness, completion, or state changes between goroutines
- Use select with timeout channels instead of sleep loops for timing operations

**Documentation Requirements:**
- Reference specific sections of relevant documentation (e.g., "Per the Go Memory Model documentation section 3.2...")
- Include links to official Go docs, relevant RFCs, or API documentation as needed
- Document WHY decisions were made, not just WHAT the code does

**Implementation Approach:**
- Start by outlining the complete solution architecture
- When modifying existing code, replace it entirely - don't create parallel implementations
- Run linters after EVERY file creation/modification
- If a linter fails, fix it immediately before proceeding
- Write meaningful tests for business logic, skip trivial tests for main() or simple wiring
- Benchmark critical paths

**Procrastination Patterns (FORBIDDEN):**
- "I'll fix the linter warnings at the end" → NO, fix immediately
- "Let me get it working first" → NO, write clean code from the start
- "This is good enough for now" → NO, do it right the first time
- "The tests can come later" → NO, test as you go
- "I'll refactor in a follow-up" → NO, implement the final design now

**Specific Antipatterns to Avoid:**
- Do NOT create elaborate error type hierarchies
- Do NOT use reflection unless absolutely necessary
- Do NOT keep old implementations alongside new ones
- Do NOT create "transition" or "compatibility" code
- Do NOT stop at "mostly working" - the code must be production-ready
- Do NOT accept any linter warnings as "acceptable" - fix them all
- Do NOT use time.Sleep() for synchronization - use channels instead
- Do NOT poll with loops - use channel selects for event-driven code

**Completion Checklist (ALL must be ✅):**
- [ ] Research phase completed with codebase understanding
- [ ] Plan reviewed and approach validated
- [ ] ALL linters pass with ZERO warnings
- [ ] ALL tests pass (including race detection where applicable)
- [ ] Feature works end-to-end in realistic scenarios
- [ ] Old/replaced code is DELETED
- [ ] Documentation/comments are complete
- [ ] Reality checkpoints were performed regularly
- [ ] NO TODOs, FIXMEs, or "temporary" code remains

**STARTING NOW** with research phase to understand the codebase...

(Remember: The hooks will verify everything. No excuses. No shortcuts.)
