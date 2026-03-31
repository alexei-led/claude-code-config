# cc-thingz

A Claude Code plugin marketplace with 9 installable plugins for development workflows, language-specific tooling, infrastructure ops, and more.

## Installation

Add the marketplace:

```bash
/plugin marketplace add alexei-led/cc-thingz
```

Install plugins you want:

```bash
/plugin install dev-workflow@cc-thingz
/plugin install go-dev@cc-thingz
/plugin install python-dev@cc-thingz
```

## Prerequisites

Some plugins use MCP servers for enhanced capabilities. These are optional — plugins degrade gracefully without them, but you'll get the best experience with all four configured.

| MCP Server                                                                                              | Purpose                                     | Used By                                                                  |
| ------------------------------------------------------------------------------------------------------- | ------------------------------------------- | ------------------------------------------------------------------------ |
| [Context7](https://github.com/upstash/context7)                                                         | Library and framework documentation lookup  | All 9 plugins                                                            |
| [Perplexity](https://github.com/ppl-ai/modelcontextprotocol)                                            | Web research and technical comparisons      | dev-workflow, dev-tools, infra-ops                                       |
| [Sequential Thinking](https://github.com/modelcontextprotocol/servers/tree/main/src/sequentialthinking) | Step-by-step reasoning for complex planning | go-dev, python-dev, typescript-dev, infra-ops, spec-system               |
| [MorphLLM](https://github.com/morphllm/morph-claude-code)                                               | Fast codebase search and batch file editing | dev-workflow, go-dev, python-dev, typescript-dev, infra-ops, spec-system |

See [GUIDE.md](GUIDE.md#mcp-servers) for details on what each MCP enables.

## Plugins

| Plugin             | Skills | Agents | Description                                                                        |
| ------------------ | ------ | ------ | ---------------------------------------------------------------------------------- |
| **dev-workflow**   | 7      | 25     | Code review, fixes, commits, linting hooks, and 24 language-specific review agents |
| **go-dev**         | 1      | 1      | Idiomatic Go development with stdlib-first patterns, testing, and CLI tooling      |
| **python-dev**     | 1      | 1      | Python 3.12+ development with uv/ruff/pyright toolchain                            |
| **typescript-dev** | 1      | 1      | TypeScript with strict typing, React patterns, and modern tooling                  |
| **web-dev**        | 1      | 1      | Web frontend with vanilla HTML, CSS, JavaScript, and HTMX                          |
| **infra-ops**      | 3      | 1      | Kubernetes, Terraform, Helm, GitHub Actions, AWS, GCP                              |
| **dev-tools**      | 10     | 2      | Modern CLI, git worktrees, docs lookup, web research, brainstorming                |
| **spec-system**    | 0      | 1      | Spec-driven development: requirements, tasks, and planning workflows               |
| **testing-e2e**    | 2      | 1      | E2E testing with Playwright: browser automation and test generation                |

**Totals**: 26 skills, 34 agents, 9 hooks, 9 commands

## Structure

```
.claude-plugin/marketplace.json
plugins/
├── dev-workflow/    # Core dev loop + review agents + hooks
├── go-dev/          # Go development
├── python-dev/      # Python development
├── typescript-dev/  # TypeScript development
├── web-dev/         # Web frontend
├── infra-ops/       # Infrastructure & cloud
├── dev-tools/       # Utilities & research
├── spec-system/     # Spec-driven development
└── testing-e2e/     # E2E testing with Playwright
```

## License

[MIT](LICENSE)

## Documentation

See [GUIDE.md](GUIDE.md) for detailed usage: per-plugin breakdowns, skill invocation, agent coordination, hook behavior, and spec-driven workflows.
