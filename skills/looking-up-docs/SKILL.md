---
name: looking-up-docs
description: Look up library documentation using Context7 and Ref. Use when needing API reference, library docs, framework documentation, technical documentation lookup, or exploring public GitHub repositories.
---

# Documentation Lookup

## Tools

| Tool         | Use For                                             |
| ------------ | --------------------------------------------------- |
| **Context7** | Library-specific docs (React, Go stdlib, K8s, etc.) |
| **Ref**      | Documentation search, GitHub repo exploration       |

## Context7

1. Resolve library: `mcp__context7__resolve-library-id` with `libraryName`
2. Get docs: `mcp__context7__get-library-docs` with `context7CompatibleLibraryID` and `topic`

Modes: `code` (API/examples) or `info` (concepts/guides)

## Ref

1. Search: `mcp__ref__ref_search_documentation` with `query`
2. Read: `mcp__ref__ref_read_url` with URL from results

## When to Use Which

- **Context7**: Known library, specific API needed
- **Ref**: Broader search, GitHub repos, unknown source
