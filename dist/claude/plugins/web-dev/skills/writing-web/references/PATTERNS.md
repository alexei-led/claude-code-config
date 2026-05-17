# Web Patterns Reference

## Contents

- [Semantic HTML](#semantic-html)
- [Modern CSS](#modern-css)
- [Minimal JavaScript](#minimal-javascript)
- [Style Summary](#style-summary)

## Semantic HTML

### Use Proper Elements

- `<header>`, `<main>`, `<footer>`, `<nav>` for structure
- `<button>` for actions (never `<div onclick>`)
- `<a>` for navigation
- `<details>`/`<summary>` for accordions
- `<dialog>` for modals

### Headings

- One `<h1>` per page
- No skipped levels (`h1` → `h3` is wrong)

### Forms

- `<label>` for every input
- `<fieldset>`/`<legend>` for groups
- Proper input types: `email`, `tel`, `number`

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

## Modern CSS

### Layout

- Grid for 2D, Flexbox for 1D
- `gap` instead of margin hacks
- CSS custom properties (`--var`) for theming — no magic numbers

### Responsive

- Mobile-first: `@media (min-width: ...)`
- `rem` units for scalable sizing
- `:focus-visible` for keyboard focus

### Avoid

- Floats for layout
- Deep selector nesting
- `!important` overuse

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

## Minimal JavaScript

### Prefer HTML/CSS

- `<details>` over a JS accordion
- `<dialog>` over a JS modal
- CSS `:hover` over JS hover effects
- HTMX over `fetch` for server calls

### When JS Is Needed

- `const`/`let`, never `var`
- `querySelector` over `getElementById`
- Event delegation for dynamic content
- `textContent` over `innerHTML`

```javascript
// Only when HTML/CSS/HTMX can't do it
document.body.addEventListener("click", (e) => {
  if (e.target.matches("[data-copy]")) {
    navigator.clipboard.writeText(e.target.dataset.copy);
  }
});
```

## Style Summary

- HTML first: semantic markup does the work
- CSS second: small stylesheets, fluid layout, mobile-first
- HTMX third: server-driven interactivity
- JS last: only when nothing else works
- One `<h1>` per page, no skipped heading levels
- `<button>`/`<a>`/`<dialog>`/`<details>` over `<div>` + JS
- CSS custom properties over magic numbers
- `const`/`let` only; `textContent` over `innerHTML`
