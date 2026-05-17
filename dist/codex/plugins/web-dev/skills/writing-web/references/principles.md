# Web principles and verification

Read this before generating web code. Covers the HTML-first philosophy, the
no-destructive-commands safety rule, and the post-generation verification plan.

## Safety

Do not run destructive shell commands. For broad or risky changes, state the risk and ask before acting.

## Philosophy

- HTML first: semantic markup does the work
- CSS second: small stylesheets, fluid layout, mobile-first, media/container queries only when needed
- HTMX third: server-driven interactivity
- JS last: only when nothing else works

## Verify Generated Code

After generating code, validate HTML and check behavior:

```bash
npx html-validate . 2>&1 || true
# or, with Bun:
# bunx html-validate . 2>&1 || true
```

Verification plan must include:

1. Manual/browser check for the changed page or component.
2. Responsive check at mobile and desktop widths.
3. Playwright or equivalent browser test when behavior changed.
4. Screenshot or concise pass/fail notes for visual changes.
