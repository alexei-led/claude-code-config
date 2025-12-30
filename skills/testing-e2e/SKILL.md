---
name: testing-e2e
description: E2E testing with Playwright MCP for browser automation, test generation, and UI testing. Use when discussing E2E tests, Playwright, browser testing, UI automation, visual testing, or accessibility testing. Supports TypeScript tests and Go/HTMX web applications.
allowed-tools: Task, mcp__playwright__*
---

# E2E Testing with Playwright

Use Playwright MCP tools for browser automation and E2E testing.

## Quick Start

```
/test:e2e run      # Run existing tests
/test:e2e record   # Record browser session
/test:e2e generate # Generate test from URL
```

## Spawn Agent

```
Task(subagent_type="playwright-tester", prompt="<task>")
```

## Key Tools

| Tool                       | Purpose                |
| -------------------------- | ---------------------- |
| `browser_navigate`         | Go to URL              |
| `browser_snapshot`         | Get accessibility tree |
| `browser_click`            | Click elements         |
| `browser_type`             | Type text              |
| `browser_fill_form`        | Fill form fields       |
| `browser_generate_locator` | Get best locator       |
| `browser_verify_text`      | Assert text content    |

## Supported Stacks

- **TypeScript**: Playwright Test with Page Objects
- **Go/HTMX**: Test HTMX interactions, form submissions, partial updates

## HTMX Testing Tips

- Use `browser_snapshot` to verify DOM updates after HTMX swaps
- Test `hx-trigger`, `hx-swap`, `hx-target` behaviors
- Verify `HX-*` response headers in network requests
- Assert partial page updates without full reload
