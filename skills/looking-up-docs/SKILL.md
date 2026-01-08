---
name: looking-up-docs
description: Library documentation via Context7. Use for API references, code examples, framework docs.
allowed-tools:
  - Read
  - Grep
  - Glob
  - mcp__context7__resolve-library-id
  - mcp__context7__query-docs
---

# Documentation Lookup with Context7

Context7 provides up-to-date, version-specific documentation and code examples directly from source libraries.

## Why Context7

- **Current APIs**: No hallucinated or outdated patterns
- **Version-specific**: Gets docs for exact library versions
- **Code examples**: Real, working code from actual documentation

## Workflow

1. **Resolve library ID**: `mcp__context7__resolve-library-id` with `libraryName`
2. **Get documentation**: `mcp__context7__query-docs` with `context7CompatibleLibraryID` and `topic`

## Modes

| Mode   | Use For                                    |
| ------ | ------------------------------------------ |
| `code` | API references, code examples (default)    |
| `info` | Conceptual guides, architecture, tutorials |

## Examples

```
# React hooks
resolve-library-id: "react"
get-library-docs: context7CompatibleLibraryID="/facebook/react", topic="hooks", mode="code"

# Next.js middleware
resolve-library-id: "next.js"
get-library-docs: context7CompatibleLibraryID="/vercel/next.js", topic="middleware"

# Go net/http
resolve-library-id: "go net/http"
get-library-docs: context7CompatibleLibraryID="/golang/go", topic="http server"

# Kubernetes API
resolve-library-id: "kubernetes"
get-library-docs: context7CompatibleLibraryID="/kubernetes/kubernetes", topic="deployment"
```

## Tips for Better Results

**Be specific with queries:**

- BAD: `topic="hooks"` → returns everything hook-related
- GOOD: `topic="useEffect cleanup function"` → precise results

**Filter strategies:**

- Use `topic` with function/method names: `topic="json.Unmarshal"`
- Include version when relevant: `libraryName="react 18"`
- Combine with feature context: `topic="middleware error handling"`

**When results are too broad:**

1. Narrow the `topic` parameter
2. Try `mode="code"` to focus on examples
3. Paginate: `page=2`, `page=3` for additional results
4. Re-resolve library ID with more specific name

**Quality check:**

- Verify code examples match your library version
- Cross-reference with official docs if uncertain
