---
allowed-tools:
- Read
- Grep
- Glob
- Bash(gh repo view *)
- Bash(gh api *)
- Bash(gh search *)
- Bash(gh release *)
- Bash(gh issue *)
- mcp__deepwiki__read_wiki_structure
- mcp__deepwiki__read_wiki_contents
- mcp__deepwiki__ask_question
- mcp__context7__resolve-library-id
- mcp__context7__query-docs
- mcp__perplexity-ask__perplexity_ask
description: Explore public GitHub repositories via DeepWiki AI-generated documentation.
  Use for understanding architecture, patterns, design decisions, and code organization
  of popular open-source projects. Use when user asks "how does X repo work", "explain
  architecture of Y", "what patterns does Z use", "explore repo", "deepwiki", or needs
  codebase-level understanding beyond API docs.
name: exploring-repos
---

<!-- Platform guidance for non-Claude models (Codex CLI, Gemini CLI) -->
<!-- Persistence: Keep going until the task is fully resolved. Do not stop at the first obstacle. -->
<!-- Tool use: Use available tools to verify — do not guess at file contents, paths, or command output. -->
<!-- Planning: Reflect between steps. Decompose complex problems into logical sub-steps before acting. -->
<!-- Reliability: Assess risk before irreversible actions. Ask for clarification on ambiguity. -->
<!-- Completeness: Generate complete responses without truncating. Review your output against the original constraints. -->

# Explore GitHub Repositories with DeepWiki

DeepWiki provides AI-generated wiki documentation for 30,000+ popular public GitHub repositories — architecture overviews, design patterns, component relationships, and semantic Q&A powered by Cognition's Devin.

## When to Use DeepWiki vs Context7

| Need                                                       | Tool                                              | Why                                           |
| ---------------------------------------------------------- | ------------------------------------------------- | --------------------------------------------- |
| Repo architecture, design patterns, how components connect | **DeepWiki**                                      | AI-generated wiki from full codebase analysis |
| API references, code examples, version-specific docs       | **Context7**                                      | Sourced from official library documentation   |
| "How does this repo work?"                                 | **DeepWiki**                                      | Codebase-level understanding                  |
| "How do I use this library?"                               | **Context7**                                      | Usage-level documentation                     |
| Cross-repo comparison                                      | **DeepWiki** (`ask_question` with multiple repos) | Accepts up to 10 repos                        |

## Workflow


## Query Strategies

**Start broad, then narrow:**

1. `read_wiki_structure` — scan available topics
2. `read_wiki_contents` — read the full wiki for an overview
3. `ask_question` — drill into specifics

**For architecture understanding:**

- "What is the high-level architecture?"
- "How do the core modules interact?"
- "What design patterns are used?"
- "How is error handling structured?"

**For implementation reference:**

- "How does X feature handle Y edge case?"
- "What is the authentication/authorization flow?"
- "How are database migrations managed?"
- "What testing patterns are used?"

**For cross-repo comparison:**

- Pass multiple repos to `ask_question`
- Ask about specific architectural differences
- Compare approaches to the same problem

## Examples

```
# Understand a framework's architecture
read_wiki_structure: "vercel/next.js"
ask_question: "vercel/next.js" — "How does the app router handle server components?"

# Compare two similar projects
ask_question: ["expressjs/express", "fastify/fastify"] — "How do these handle middleware differently?"

# Explore a tool's internals
read_wiki_structure: "hashicorp/terraform"
ask_question: "hashicorp/terraform" — "How does the provider plugin system work?"

# Understand patterns in a Go project
ask_question: "kubernetes/kubernetes" — "How is the controller pattern implemented?"
```

## Fallback: Repository Not Indexed

DeepWiki indexes 30,000+ popular public repos. If a repo is not indexed:

```
DeepWiki returns empty or error?
├── Check repo name format (must be "owner/repo")
├── Try the canonical repo name (not a fork)
├── Still not indexed?
│   ├── Any public repo → gh CLI (works for all GitHub repos)
│   ├── Popular library → Try Context7 for docs instead
│   ├── Open-source repo → Clone + local exploration
│   └── Niche/private → Perplexity for general info
```

### Fallback Strategies

1. **GitHub CLI** — works for any public repo, no indexing needed:

   ```bash
   # Quick overview: description, stars, language, topics
   gh repo view owner/repo

   # Full file tree (find key directories, config files)
   gh api repos/owner/repo/git/trees/main?recursive=1 --jq '.tree[].path'

   # Read specific files (README, go.mod, package.json, Makefile)
   gh api repos/owner/repo/contents/README.md --jq '.content' | base64 -d

   # Search for patterns across the repo
   gh search code "func main" --repo owner/repo --limit 20

   # Search for repos by topic, language, or description
   gh search repos "kubernetes operator" --language go --sort stars

   # Recent activity: issues, PRs, releases
   gh release list --repo owner/repo --limit 5
   gh issue list --repo owner/repo --state open --sort comments --limit 10
   ```

   **Best for:** file tree exploration, finding entry points, reading key files,
   searching code patterns, checking recent activity. Combine multiple `gh` calls
   to build a mental model when DeepWiki is unavailable.

2. **Context7** — for library API documentation:

3. **Perplexity** — for repos not in DeepWiki or Context7:

4. **Direct exploration** — clone and read:

   ```bash
   git clone --depth=1 <repo-url>
   # Use smart-explore skill for token-efficient AST navigation
   ```

## Combining with Context7

DeepWiki and Context7 are complementary. A typical research flow:

1. **DeepWiki** — understand the architecture and design decisions
2. **Context7** — get specific API references and code examples
3. **DeepWiki ask_question** — clarify how specific APIs fit into the larger design

Do not use DeepWiki when:

- You need version-specific API syntax → use Context7
- You need official getting-started guides → use Context7
- The repo is private or very new (<1 month) → use Perplexity or local exploration
