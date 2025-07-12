# Claude Code Configuration

A comprehensive configuration setup for Claude Code that enforces production-quality code standards through automated hooks, intelligent commands, and strict development guidelines.

## 🏗️ Architecture Overview

This configuration transforms Claude Code into a zero-tolerance quality enforcement system that automatically detects project types, runs appropriate linters/formatters, and ensures every code change meets production standards.

### **Key Philosophy: Zero Tolerance for Issues**
- **ALL** linting/formatting issues are blocking - no exceptions
- **ALL** tests must pass before proceeding
- **ALL** hooks must show ✅ GREEN status
- Real-time quality enforcement prevents technical debt accumulation

## 📁 Project Structure

### **CLAUDE.md** - Development Guidelines
Comprehensive development standards that override Claude's default behavior:
- **Research → Plan → Implement** mandatory workflow
- **Multiple agent usage** for parallel problem-solving
- **Language-specific rules** with strict Go standards
- **Quality checkpoints** at every stage
- **Code evolution rules** (delete old code, no compatibility layers)

### **settings.json** - Hook Configuration
Configures automated hooks:
- **PostToolUse**: Runs after file edits (Write|Edit|MultiEdit)
- **Notification**: macOS notification system for status updates

### **hooks/** - Automated Quality Enforcement

#### **smart-lint.sh** - Universal Code Quality Engine
Multi-language linter with automatic project detection:
- **Auto-detects**: Go, Python, JavaScript/TypeScript, Rust, Nix
- **Zero tolerance**: ALL issues must be fixed before proceeding
- **Comprehensive checks**: Formatting, linting, security, complexity
- **Custom rules**: Project-specific overrides via `.claude-hooks-config.sh`
- **Language-specific**: golangci-lint, ruff, eslint, clippy, etc.

#### **notify.sh** - macOS Integration
Native macOS notification system:
- Provides visual feedback for hook status
- Uses osascript for system notifications
- JSON input format for structured messages

#### **test-runner.sh** - Automated Testing
Project-aware test execution:
- Auto-detects test frameworks (go test, npm test, pytest, cargo test)
- Integrates with Makefile if available
- Provides detailed test result reporting

### **commands/** - Intelligent Slash Commands

#### **/check** - Comprehensive Quality Verification
**Critical**: This is a FIXING command, not a reporting command
- Identifies ALL issues across linting, testing, building
- **MANDATORY**: Must fix every single issue found
- **Multi-agent**: Spawns parallel agents to fix issues
- **No stopping**: Continues until everything shows ✅ GREEN
- **Forbidden**: Just reporting issues without fixing them

#### **/next** - Production Implementation Workflow
Enforces the Research → Plan → Implement sequence:
- **MANDATORY**: "Let me research the codebase and create a plan before implementing"
- **Multi-agent support**: Spawn agents for independent task components
- **Reality checkpoints**: Validation after every 3 file edits
- **Code evolution**: Delete old code, no compatibility layers
- **Quality gates**: Linters must pass after every change

#### **/ask_gemini** - Second Opinion System
Query Gemini AI for additional insights:
- Architectural decisions and alternatives
- Security analysis and best practices
- Performance optimization strategies
- Code review and design validation
- Uses gemini-2.5-pro for comprehensive analysis

#### **/prompt** - Template Synthesizer
Combines next.md workflow with specific tasks:
- Merges next.md structure with user arguments
- Creates complete, copy-ready prompts
- Context-aware enhancement based on technologies mentioned
- Emphasizes relevant language-specific rules

#### **/perf** - Performance Analysis
Comprehensive performance profiling:
- **Go**: pprof CPU/memory profiles, benchmarks
- **Python**: cProfile, memory_profiler, N+1 query detection
- **JavaScript**: Chrome DevTools, Lighthouse, bundle analysis
- **Rust**: criterion benchmarks, perf integration

#### **/reset** - State Management
Clean working directory and reset to known good state:
- Run all formatters and linters
- Clear temporary files and caches
- Verify git status and uncommitted changes
- Regenerate TODO.md from current state
- Optional `--hard`, `--cache`, `--format` flags

### **Configuration Files**

#### **.claude-hooks-config.sh** - Project Overrides
Customizable settings for project-specific requirements:
- **Language toggles**: Enable/disable specific language checks
- **Tool selection**: Choose formatters (black/yapf, nixpkgs-fmt/alejandra)
- **Quality thresholds**: Coverage percentages, complexity limits
- **Custom checks**: Add project-specific validation functions
- **Debug options**: Timing information, verbose output

#### **.claude-hooks-ignore** - Exclusion Patterns
Define files and directories to exclude from quality checks.

## 🚀 Language Support

### **Go** (Strict Mode)
- **golangci-lint** with all checks enabled
- **Forbidden patterns**: interface{}, any{}, time.Sleep() for sync
- **Required**: Channels for synchronization, early returns, godoc
- **Auto-format**: gofmt, goimports
- **Race detection**: Automatic -race flag testing

### **Python**
- **Formatters**: black (default), yapf, autopep8
- **Linters**: ruff (default), flake8, pylint
- **Import sorting**: isort integration
- **Type checking**: mypy when configured

### **JavaScript/TypeScript**
- **Package managers**: npm (default), yarn, pnpm
- **Linting**: eslint with project configuration
- **Formatting**: prettier integration
- **Type checking**: tsc for TypeScript projects

### **Rust**
- **Linting**: clippy with `-D warnings`
- **Formatting**: rustfmt
- **Testing**: cargo test integration

### **Nix**
- **Formatters**: nixpkgs-fmt (default), alejandra
- **Validation**: nix-instantiate checks

## 🔧 Installation & Setup

### Quick Start
```bash
# Clone to your project root or ~/.claude/
git clone https://github.com/your-repo/claude-code-config ~/.claude

# Claude Code will automatically detect and apply configurations
# Start using slash commands immediately: /check, /next, etc.
