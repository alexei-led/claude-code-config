# Web Architecture Reference

Language-specific over-abstraction and dead-code patterns for modern HTML/CSS/vanilla JS. The shared modularity model lives in [LANGUAGE.md](LANGUAGE.md) and [DEEPENING.md](DEEPENING.md) — this file supplies only the web-specific smells and detection.

The overriding principle: prefer native platform capabilities over libraries and frameworks. Modern browsers have solved most problems that once required JavaScript.

## Run tooling first

```bash
npx html-validate <files>   # if configured (or bunx)
npx stylelint <files>       # if configured (or bunx)
```

If a validator is missing, note it in findings rather than guessing. Ground every finding in tool output or direct code inspection.

## Use HTML instead of JS

Reach for semantic HTML before writing JavaScript. Common replacements:

- **Accordion**: `<details>` / `<summary>`
- **Modal**: `<dialog>` with `showModal()`
- **Popover / tooltip**: `popover` attribute
- **Form validation**: `required`, `pattern`, `type`, `:invalid`
- **Toggle visibility**: `hidden` attribute or `.hidden` class
- **Search section**: `<search>` element

```html
<!-- JS accordion → HTML -->
<details>
  <summary>Click to expand</summary>
  <p>Hidden content</p>
</details>

<!-- JS modal → HTML -->
<dialog id="modal">
  <p>Modal content</p>
  <button onclick="this.closest('dialog').close()">Close</button>
</dialog>
<button onclick="document.getElementById('modal').showModal()">Open</button>

<!-- JS popover → HTML -->
<button popovertarget="info">Show info</button>
<div id="info" popover>Popover content</div>
```

## Use CSS instead of JS

CSS features that eliminate JS:

- Hover effects: `:hover`
- Smooth scroll: `scroll-behavior: smooth`
- Sticky header: `position: sticky`
- Parent selection: `:has()`
- Container queries: `@container`
- Theme switching: CSS custom properties
- Animations: CSS `@keyframes`, `transition`

Stay current with: `@layer`, anchor positioning, `:has()`, `@container`, `popover`.

## Use HTMX instead of fetch

```html
<!-- JS fetch → HTMX -->
<button hx-post="/api/action" hx-target="#result">Do Action</button>

<!-- JS form submit → HTMX -->
<form hx-post="/api/submit" hx-swap="outerHTML">
  <input name="email" type="email" required />
  <button>Submit</button>
</form>
```

## Dead code and bloat

- Unused CSS rules: dead selectors, orphaned classes (use stylelint or grep)
- Wrapper divs: elements that do nothing structurally or stylistically

```html
<!-- BAD: wrapper soup -->
<div class="outer">
  <div class="inner">
    <div class="content"><p>Text</p></div>
  </div>
</div>

<!-- GOOD: minimal -->
<p class="content">Text</p>
```

- Libraries for one function: use native alternatives instead
- Commented-out code: delete — git has history
- Polyfills for modern features: remove if baseline browser support is sufficient

## Simplify CSS

- Flatten deep selectors: `.a .b .c .d` → simpler specificity
- Remove unused classes: check with stylelint or grep
- Use CSS variables instead of repeated magic values:

```css
/* BAD: repeated value */
.header { color: #3b82f6; }
.link   { color: #3b82f6; }
.button { background: #3b82f6; }

/* GOOD: CSS variable */
:root { --primary: #3b82f6; }
.header { color: var(--primary); }
.link   { color: var(--primary); }
.button { background: var(--primary); }
```

- Use modern layout: `grid` and `flexbox` instead of float hacks
- Use logical properties: `margin-inline` instead of `margin-left` / `margin-right`

## Unnecessary JS complexity

- Nested ternaries: use `if/else` or `switch`
- Deep nesting: use early returns
- Over-engineered event handling: simpler delegation patterns
- State management overkill: for simple UIs, direct DOM manipulation is fine

## Failure handling

- If validators are not installed: note it explicitly and proceed with manual review only.
- If a finding cannot be grounded in tool output or direct code inspection: omit it.
- If scope is unclear (whole project vs. changed files): default to recently modified files and state that assumption.
- If a simplification would change behavior: flag it as a risk rather than a recommendation.
