# Web Documentation Slice

Language-specific documentation conventions for HTML/CSS/JS/HTMX. The host skill supplies workflow and verification — this file supplies only the web doc-comment conventions and examples.

## run tooling first

```bash
npx html-validate . 2>&1 || true
```

Include tool output in findings. If not installed, skip and proceed with manual review.

## comment conventions

Comments explain why, not what.

Delete:

```javascript
// Loop through users
users.forEach((user) => process(user));
```

Keep:

```javascript
// Sequential to avoid rate limit
for (const user of users) {
  await process(user);
}
```

Comment when:

- logic is non-obvious
- working around a browser quirk
- explaining a complex regex

Do not comment:

- obvious code
- every function

## ARIA labels

Icon buttons and form hints require explicit ARIA attributes.

Required patterns:

```html
<!-- Icon button — label describes the action, not the icon -->
<button aria-label="Close"><svg>...</svg></button>

<!-- Form hint — input references the hint element by ID -->
<input id="email" aria-describedby="email-hint" />
<span id="email-hint">We won't share your email</span>
```

Do not:

- Add redundant ARIA to semantic HTML that already conveys its role
- Use `aria-hidden` on focusable elements

## HTMX comments

Mark HTMX targets and explain non-obvious triggers.

```html
<!-- HTMX target: /api/search -->
<div id="results"></div>

<!-- Debounced search: waits 300ms after typing stops -->
<input
  hx-get="/api/search"
  hx-trigger="keyup changed delay:300ms"
  hx-target="#results"
/>
```

## failure handling

- If the HTML validator is not installed, skip and proceed with manual review; note this in findings.
- If an ARIA issue cannot be confirmed without running the page in a browser, flag it as "needs verification" rather than a definite finding.
- If comments are absent entirely, note it only for non-obvious logic sections — do not flag well-named, self-evident code.
- If a file has no HTML (pure JS/CSS only), skip ARIA checks and focus on comment quality.
