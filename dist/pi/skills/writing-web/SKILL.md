---
description: Simple web development with HTML, CSS, JS, and HTMX. Auto-activates when
  working with .html, .css, or .htmx files, web templates, stylesheets, or vanilla
  JS scripts. NOT for React/Vue/Angular (use writing-typescript) or Node.js backends.
name: writing-web
---

<!-- Pi platform guidance -->
<!-- Use Pi tool names exactly: read, bash, edit, write, ask_user_question, structured_output, todo, Agent, get_subagent_result, steer_subagent, web_search, web_answer, web_research. -->
<!-- Use Agent, get_subagent_result, and steer_subagent for delegated work. -->
<!-- Use ctx7 or npx ctx7@latest through bash when Context7 documentation lookup is required. -->

# Web Development (Simple, Modern)

## Critical Output Rules

- Use semantic HTML elements before reaching for CSS or JS: `<button>`, `<dialog>`, `<details>`, `<summary>`, `<nav>`, `<article>`.
- CSS custom properties (`--var`) for all repeated values; no magic numbers.
- HTMX for server-driven interactivity; vanilla JS only when HTML/CSS/HTMX cannot do it.
- Include a verification plan for every generated page or component: manual browser check, responsive check at mobile/desktop, and a Playwright step when behavior changed.
- Do not run destructive shell commands. For broad or risky changes, state the risk and ask before acting.

## Philosophy

The HTML-first philosophy, the no-destructive-commands safety rule, and the post-generation verification plan are in [references/principles.md](references/principles.md) — read it before generating code.

## Patterns

### Semantic HTML

```html
<header>
  <nav><a href="/">Home</a></nav>
</header>
<main>
  <h1>Title</h1>
  <article>Content</article>
</main>
<footer>&copy; 2024</footer>
```

### Use native elements

- `<button>` for actions
- `<a>` for navigation
- `<details>`/`<summary>` for accordions
- `<dialog>` for modals

### Simple CSS

```css
:root {
  --primary: #2563eb;
  --spacing: 1rem;
}

.container {
  display: grid;
  gap: var(--spacing);
}

@media (min-width: 768px) {
  .container {
    grid-template-columns: 1fr 1fr;
  }
}
```

### HTMX (with Go)

```html
<!-- Load content -->
<div hx-get="/items" hx-trigger="load"></div>

<!-- Form -->
<form hx-post="/create" hx-target="#result">
  <input name="title" required />
  <button>Create</button>
</form>

<!-- Delete with confirmation -->
<button hx-delete="/item/123" hx-confirm="Delete?">Delete</button>

<!-- CSRF token -->
<body hx-headers='{"X-CSRF-Token": "{{.Token}}"}'></body>
```

### Minimal JS

```javascript
// Only when HTML/CSS/HTMX can't do it
document.body.addEventListener("click", (e) => {
  if (e.target.matches("[data-copy]")) {
    navigator.clipboard.writeText(e.target.dataset.copy);
  }
});
```

## Avoid

- JS for things HTML can do (accordions, modals)
- CSS for things HTML can do (form validation)
- Fetch when HTMX works
- Deep selector nesting
- Wrapper div soup

## References

- [principles.md](references/principles.md) - Philosophy, safety rule, and verification plan (read before generating code)
- [PATTERNS.md](references/PATTERNS.md) - Semantic HTML, modern CSS, and minimal-JS idioms

## Failure Cases

- **html-validate reports errors**: fix semantic/attribute issues before considering the task done; do not suppress with `|| true` in CI.
- **HTMX request not firing**: check `hx-trigger`, `hx-target` selector, and CSRF header presence before adding JS fallback.
