---
description: Simple web development with HTML, CSS, JS, and HTMX. Auto-activates when
  working with .html, .css, or .htmx files, web templates, stylesheets, or vanilla
  JS scripts. NOT for React/Vue/Angular (use writing-typescript) or Node.js backends.
name: writing-web
---

# Web Development (Simple, Modern)

## Philosophy

1. **HTML first** - Semantic markup does the work
2. **Responsive simple CSS second** - Small stylesheets, fluid layout, mobile-first sizing, and media/container queries only when needed
3. **HTMX third** - Server-driven interactivity
4. **JS last** - Only when nothing else works

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

- Destructive shell commands; ask before deleting or overwriting user files
- JS for things HTML can do (accordions, modals)
- CSS for things HTML can do (form validation)
- Fetch when HTMX works
- Deep selector nesting
- Wrapper div soup

## Verify Generated Code

After generating code, validate HTML and check behavior:

```bash
npx html-validate . 2>&1 || true
# or, with Bun:
# bunx html-validate . 2>&1 || true
```

For small HTMX/form answers, explicitly mention simple responsive CSS and include a basic browser/manual or Playwright verification plan.

Verification plan must include:

1. Manual/browser check for the changed page or component.
2. Responsive check at mobile and desktop widths.
3. Playwright or equivalent browser test when behavior changed.
4. Screenshot or concise pass/fail notes for visual changes.
