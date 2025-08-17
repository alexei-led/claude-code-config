# Claude Code Configuration

Elite-tier optimized setup with 8 focused commands, 5 specialized agents, and comprehensive MCP integration. Designed for production-quality development with zero-tolerance quality enforcement.

## 🎯 Available Commands

### Quality & Development
- **`/@check`** - Zero-tolerance quality enforcement with parallel agent fixes
- **`/@review`** - Security-focused code review via quality-guardian
- **`/@test-coverage`** - 80% minimum coverage enforcement

### Planning & Documentation  
- **`/@orchestrate`** - Complex task planning with sequential-thinking MCP
- **`/@docs`** - Documentation updates via docs-keeper
- **`/@remember`** - Save decisions/context to basic-memory

### Infrastructure & Git
- **`/@deploy-check`** - K8s/CI configuration validation
- **`/@commit`** - Group changes logically and create bundled commits

## 🤖 Specialized Agents

### **orchestrator** (Sonnet + MCP)
Complex planning and coordination
- **Tools:** sequential-thinking, basic-memory, github, perplexity
- **Use for:** Architecture decisions, multi-step workflows, cross-domain coordination

```bash
/@orchestrate "Design microservice authentication with Redis sessions"
```

### **quality-guardian** (Opus + MCP) 
Testing, security, and code review
- **Tools:** testify/mockery, OWASP patterns, github PR reviews
- **Use for:** Security analysis, test creation, code quality enforcement

```bash
/@review  # Comprehensive security-focused review
/@test-coverage  # Enforce 80% minimum with gap analysis
```

### **go-engineer** (Sonnet + MCP)
Go development specialist
- **Tools:** Context7 docs, clean architecture patterns, performance focus
- **Use for:** Go implementation, API design, microservices

### **docs-keeper** (Haiku + MCP)
Documentation and knowledge management  
- **Tools:** basic-memory, context7, mermaid diagrams
- **Use for:** README updates, API docs, architecture diagrams

```bash
/@docs  # Update all documentation based on recent changes
```

### **deployment-specialist** (Sonnet + MCP)
Infrastructure and deployment automation
- **Tools:** K8s manifests, GitHub Actions, security-first practices
- **Use for:** Deployment validation, CI/CD workflows, infrastructure security

```bash
/@deploy-check  # Validate K8s manifests and CI configurations
```

## 🔧 When to Use Each Command

### Start Complex Work
```bash
/@orchestrate "Implement user notification system with email/SMS/push"
# → Plans architecture, delegates to specialists, manages workflow
```

### Before Committing Code
```bash
/@check
# → Spawns agents to fix ALL linting/test issues in parallel
# → Zero tolerance: must be 100% clean to continue
```

### Security & Quality Review
```bash
/@review
# → Security analysis, vulnerability assessment, best practices check
```

### Test Coverage Validation
```bash
/@test-coverage  
# → Comprehensive test analysis, 80% minimum enforcement
# → Identifies untested paths and improvement recommendations
```

### Documentation Maintenance
```bash
/@docs
# → Updates README, GoDoc comments, API specs, architecture diagrams
```

### Infrastructure Validation
```bash
/@deploy-check
# → K8s manifest validation, GitHub Actions lint, security contexts
```

### Knowledge Preservation
```bash
/@remember "Decided to use pgx over GORM for better performance control"
# → Saves to basic-memory for future reference and team knowledge
```

### Git Workflow Management
```bash
/@commit
# → Analyzes changed files and groups them logically
# → Creates focused commits with descriptive messages
# → Example: Feature + tests + docs as separate atomic commits
```

## 🚀 Quick Start Examples

### Complex Feature Implementation
```bash
# 1. Plan the work
/@orchestrate "Add rate limiting to API with Redis backend"

# 2. Implement following the plan
# (Regular development work)

# 3. Quality check before commit  
/@check

# 4. Security review
/@review

# 5. Validate tests
/@test-coverage

# 6. Update documentation
/@docs

# 7. Remember key decisions
/@remember "Used token bucket algorithm for rate limiting - better for burst handling"

# 8. Commit changes in logical groups
/@commit
```

### Quick Quality Check
```bash
/@check  # Fix ALL issues before continuing
```

### Pre-deployment Validation
```bash
/@deploy-check  # Ensure K8s configs are secure and valid
```

### Smart Git Workflow
```bash
/@commit
# Analyzes: auth.go, auth_test.go, middleware.go, README.md, docs/auth.md
#
# Creates commits:
# 1. "auth: implement JWT validation with middleware"
#    - auth.go, middleware.go
# 2. "auth: add comprehensive validation tests" 
#    - auth_test.go, middleware_test.go
# 3. "docs: add JWT authentication guide"
#    - README.md, docs/auth.md
```

## ⚙️ MCP Integration

### **sequential-thinking** - Complex Problem Analysis
- Multi-step reasoning for architecture decisions
- Trade-off evaluation and risk assessment
- Used by orchestrator for planning

### **basic-memory** - Project Knowledge Persistence  
- Cross-session context retention
- Architecture decisions and patterns
- Team knowledge sharing

### **context7** - Up-to-date Library Documentation
- Go standard library references
- Third-party framework docs
- Real-time API specifications

### **perplexity** - AI Research Assistant
- Latest security practices and vulnerabilities  
- Performance optimization techniques
- Industry best practices research

### **github** - Repository Management
- Pull request analysis and reviews
- GitHub Actions workflow management
- Automated code review integration

## 🛡️ Quality Standards

### Zero-Tolerance Enforcement
- **ALL** linting warnings must be fixed
- **ALL** tests must pass with meaningful coverage
- **80%** minimum test coverage enforced
- **Security** analysis required for all changes

### Language-Specific Requirements

**Go Projects:**
- No `interface{}`/`any{}` - use concrete types
- Channels for synchronization, never `time.Sleep()`
- `go test -race` for race detection
- Error wrapping with context
- mockery for test mocks

**TypeScript Projects:**
- Strict mode enabled, avoid 'any' type
- Proper async/await patterns
- ESLint clean with zero warnings

**Python Projects:**
- Type hints on all functions
- mypy validation passes
- pytest patterns, no broad exceptions

## 📊 Performance Monitoring

### Built-in Monitoring Tools

#### **smart-lint.sh** (Automatic)
Shows token usage with every command execution:
```bash
# Automatic output from any command
markdown project ✅ Style OK 📊 ~2,666 tokens
```

#### **performance-monitor.sh** (Manual Analysis)
Comprehensive configuration health check - run manually when needed:

```bash
# Full configuration analysis
~/.claude/hooks/performance-monitor.sh
```

**Purpose:**
- Analyze context usage efficiency 
- Identify optimization opportunities
- Monitor configuration health over time
- Get detailed breakdown of all files

**Sample Output:**
```bash
📊 Claude Code Performance Analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Context Files:
  CLAUDE.md              1100 words  184 lines
  settings.json           103 words   74 lines
  @check.md               308 words   65 lines
  @deploy-check.md         44 words   16 lines
  @docs.md                106 words   26 lines
  @orchestrate.md          54 words   12 lines
  @remember.md            137 words   27 lines
  @review.md              100 words   26 lines
  @test-coverage.md        48 words   17 lines

Total Context: ~2666 tokens (2000 words, 447 lines)
Context Usage: ~1% of 200K limit
Largest File: CLAUDE.md (1100 words)

Optimization Insights:
✅ Context usage is efficient
⚠️  Large file detected: CLAUDE.md - consider optimization
📝 Active commands: 7
✅ Command count is optimal

Hook Performance:
  smart-lint.sh         395 lines
  notify.sh              16 lines
  test-runner.sh        108 lines

✅ Performance analysis complete
```

**When to Use:**
```bash
# Monthly configuration health check
~/.claude/hooks/performance-monitor.sh

# After adding new commands or major changes
~/.claude/hooks/performance-monitor.sh

# When context feels slow or bloated
~/.claude/hooks/performance-monitor.sh

# Before major refactoring of commands
~/.claude/hooks/performance-monitor.sh
```

**Optimization Alerts:**
- **High context usage** (>10% of 200K limit) - suggests trimming verbose commands
- **Large files** (>1000 words) - identifies files that might need optimization
- **Too many commands** (>10) - recommends consolidation
- **Hook performance** - tracks complexity of hook scripts

**Current Metrics:**
- **Context Usage:** ~1% of 200K limit (excellent)
- **Commands:** 8 focused, optimized commands
- **Token Efficiency:** ~2,666 tokens total context
- **Largest File:** CLAUDE.md (1,100 words)

## 🔍 Hook System

### smart-lint.sh (Automatic Hook)
**Trigger:** Runs automatically with every command execution  
**Purpose:** Code quality enforcement + basic token monitoring

Auto-detects project types and runs appropriate linters:
- **Go:** golangci-lint, gofmt, go test -race
- **TypeScript/JS:** prettier, eslint  
- **Python:** black, ruff, mypy
- **YAML:** yamllint
- **Shell:** shellcheck, shfmt
- **K8s:** kubeval, actionlint

**Output:** `markdown project ✅ Style OK 📊 ~2,666 tokens`

### performance-monitor.sh (Manual Tool)
**Trigger:** Run manually when needed  
**Purpose:** Comprehensive configuration analysis and optimization insights

Features:
- Token usage breakdown by file
- Context efficiency recommendations  
- Hook performance metrics
- Optimization alerts and suggestions
- Configuration health assessment

**Usage:** `~/.claude/hooks/performance-monitor.sh`

## 🎯 Best Practices

### Development Workflow
1. **Plan first:** Use `/@orchestrate` for complex features
2. **Quality gate:** Run `/@check` before every commit
3. **Security focus:** Use `/@review` for security analysis
4. **Test coverage:** Maintain 80% with `/@test-coverage`
5. **Documentation:** Keep current with `/@docs`
6. **Knowledge sharing:** Use `/@remember` for key decisions
7. **Smart commits:** Use `/@commit` for logical change grouping

### Agent Coordination
- **Spawn multiple agents** for parallel work when appropriate
- **Use sequential-thinking** for complex architectural decisions
- **Leverage basic-memory** for context across sessions
- **Delegate appropriately** based on task complexity and domain

### Memory Management
- Save important architectural decisions with `/@remember`
- Use basic-memory for cross-session knowledge retention
- Document patterns and conventions for team consistency
- Build searchable project knowledge over time

---

**Optimized for developers who value efficiency, security, and maintainable code.**