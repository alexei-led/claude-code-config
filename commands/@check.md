---
allowed-tools: all
description: Fix ALL issues via parallel agents - zero tolerance quality enforcement
---

# 🚨 CRITICAL: FIX ALL ISSUES - NOT A REPORTING TASK! 🚨

**MANDATORY BEHAVIOR:**
1. **SPAWN MULTIPLE AGENTS** immediately for parallel fixing:
   - "Found X issues. Spawning agents: Agent 1 (linting), Agent 2 (tests), Agent 3 (build)"
2. **FIX EVERYTHING** - zero tolerance for warnings/errors
3. **REPEAT** until ALL GREEN ✅

**FORBIDDEN:** Reporting without fixing, stopping before 100% clean
**WORKFLOW:** smart-lint.sh + checks → spawn agents → fix ALL → verify → repeat

Re-read ~/.claude/CLAUDE.md first. Hooks block on violations.

**Universal Protocol:**
1. Run `~/.claude/hooks/smart-lint.sh` + `make lint`/`make test`
2. **SPAWN AGENTS** immediately for ALL issues
3. Repeat until zero warnings ✅

**Universal Standards:**
- Zero warnings across all languages
- All tests pass, meaningful coverage
- Proper formatting (auto-detected by smart-lint.sh)
- Security validation, no hardcoded secrets
- Performance awareness, no obvious bottlenecks

**Context-Specific Guidance (when relevant):**

**Go Projects:**
□ No interface{}/any{} - use concrete types
□ Channels for sync, never time.Sleep()
□ go test -race for race detection
□ Error wrapping with context
□ mockery for test mocks

**TypeScript Projects:**
□ Strict mode enabled, avoid 'any' type
□ Proper async/await patterns
□ ESLint clean with zero warnings

**Python Projects:**
□ Type hints on all functions
□ mypy validation passes
□ pytest for testing, no broad exceptions

**Terraform Projects:**
□ terraform validate passes
□ Security scanning clean
□ Proper resource naming conventions

**Agent Response Protocol:**
When issues found:
1. **SPAWN AGENTS:** "Found X issues. Agents: Agent 1 (linting A,B), Agent 2 (tests), Agent 3 (build)"
2. **FIX ALL** - no excuses ("just formatting" → fix NOW)
3. **VERIFY** - re-run smart-lint.sh + tests
4. **REPEAT** until ALL GREEN ✅

**Ready When:**
✓ smart-lint.sh passes ✓ All tests pass ✓ Context-specific checks clean ✓ End-to-end works

**Executing validation and FIXING ALL ISSUES...**
