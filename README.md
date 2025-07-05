# Claude Code Configuration

A comprehensive configuration setup for Claude Code that enforces high code quality standards through automated hooks, custom commands, and strict development guidelines.

## 📁 What's Included

### **CLAUDE.md** - Development Guidelines
Core development principles that override Claude's default behavior:
- Enforces Research → Plan → Implement workflow
- Zero-tolerance policy for linting/formatting issues
- Promotes parallel agent usage for complex tasks
- Language-specific rules (especially strict for Go)

### **hooks/** - Automated Quality Checks
- **smart-lint.sh**: Multi-language linter that auto-detects project type and runs appropriate formatters/linters. ALL issues are blocking - code must be 100% clean.

### **commands/** - Custom Slash Commands
- **/check**: Comprehensive quality verification that requires fixing ALL issues
- **/next**: Enforces proper feature implementation workflow
- **/prompt**: Synthesizes complete prompts from templates
- **/ask_gemini**: Query Gemini AI for additional insights

### **.settings.json** - Claude Code Configuration
Configures Claude to use Opus model and automatically run smart-lint hook after file modifications.

## 🚀 Why This Configuration?

1. **Quality First**: Every code change must pass ALL checks - no exceptions
2. **Efficiency**: Parallel agent usage and automated workflows save time
3. **Consistency**: Same high standards across all languages and projects
4. **No Surprises**: Deterministic hooks ensure code quality before problems arise

## 💡 Usage

1. Clone this repository to your project root
2. Claude Code will automatically detect and apply these configurations
3. All file edits trigger automatic quality checks
4. Use slash commands for common workflows

The configuration enforces production-ready code standards while maximizing development efficiency through intelligent automation.