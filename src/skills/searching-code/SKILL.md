---
description:
  Intelligent codebase search and zoom-out mapping via WarpGrep. Use when
  user asks "how does X work", "trace flow", "find all implementations", "understand
  codebase", "zoom out", "map this area", or needs cross-file exploration in large
  repos (1000+ files).
name: searching-code
---

# Intelligent Code Search with WarpGrep

WarpGrep is an RL-trained search agent that reasons about code, not just pattern matches. Use zoom-out mode when the user needs a higher-level map before touching code.

## Critical Workflow Rules

- Do not read the whole repo indiscriminately. Convert vague asks into a scoped map question or ask for scope.
- Start search-first and name the commands: use `fd` to find likely files and `rg` to find known symbols, routes, handlers, and types; use WarpGrep for semantic flow across files.
- Before mapping architecture, check for and read `CONTEXT.md`, `CONTEXT-MAP.md`, nearest `*/CONTEXT.md`, and relevant `docs/adr/*.md` files when present.
- Trace callers, callees, shared types/messages, and data/control flow across files. Follow only enough files or line ranges to verify the map.
- Separate known facts from guesses. List unknowns explicitly instead of filling gaps.
- For vague requests like "read this repo and explain everything", refuse the full dump, offer a zoom-out map, say exploration will start with `fd`/`rg`/WarpGrep searches instead of full-file reading, and say the final summary will separate verified facts from guesses/unknowns.

## Final Answer Contract

Return a bounded code map:

1. Flow with `file:line` references.
2. Key modules and responsibilities.
3. Callers/callees and shared types/messages.
4. Unknowns or unverified assumptions.
5. Read-next list, top 3 files only.

## How It Works

- **8 parallel searches** per turn (explores multiple hypotheses)
- **4 reasoning turns** (follows causal chains across files)
- **F1=0.73** in ~3.8 steps (vs 12.4 for standard search)

## When to Use Which Tool

WarpGrep:

- "How does auth flow work?"
- "Trace data from API to DB"
- "Find all error handling"
- Large repos (1000+ files)
- Before major refactoring

Smart Explore (claude-mem):

- "What functions are in this file?"
- "Show me this function's source"
- "Find all types matching X"
- File structure at a glance
- Targeted function extraction

Built-in Grep:

- "Find class UserService"
- Simple regex patterns
- "Where is X defined?"
- Known file patterns
- Quick needle lookups

**When available**, prefer Smart Explore for structural queries (10-20x fewer tokens). Use WarpGrep for semantic/reasoning queries across files.

## Query Formulation

**Good queries** (reasoning required):

```
"How does authentication flow from the login handler to the database?"
"Find all places where user permissions are checked"
"Trace the request lifecycle from router to response"
```

**Bad queries** (use Grep instead):

```
"Find UserService" → use Grep
"Search for 'import React'" → use Grep
```

## Workflow

For trace-flow requests, explicitly say you will first check for `CONTEXT.md`, `CONTEXT-MAP.md`, nearest `*/CONTEXT.md`, and `docs/adr/*.md` when present before naming domain concepts.

1. **Formulate query**: Describe WHAT you want to understand, not just WHAT to find
2. **Load domain docs when present**: `CONTEXT.md`, `CONTEXT-MAP.md`, and relevant ADRs
3. **Run targeted shell search**: `fd 'auth|login|session|user'` for likely files; `rg 'login|authenticate|AuthService|Session|UserRepository'` for entry points, symbols, and shared types
4. **Run semantic code search**: use WarpGrep or another available semantic search tool for cross-file flow
5. **Interpret results**: Ranked snippets with file paths and line numbers
6. **Follow up**: Read specific files or line ranges only when needed for verification

## Zoom-Out Mode

Use when the user says "zoom out", "map this area", "go up a layer", or sounds lost in local details.

Return a map, not a dump:

- relevant modules and callers
- data/control flow across seams
- domain terms from `CONTEXT.md`
- ADR constraints that shape the design
- known facts vs guesses/unknowns
- where to read next, limited to the top 3 files

Avoid line-by-line explanations unless asked. The point is orientation, not drowning the user in snippets.

## Parameters

```
search_string: "natural language description of what to find"
repo_path: "/absolute/path/to/repo"
```

## Tips

- Be specific about the behavior or flow you're investigating
- Include context: "in the API layer" or "during startup"
- WarpGrep handles ambiguity better than exact pattern matching
- Results include surrounding context for understanding
