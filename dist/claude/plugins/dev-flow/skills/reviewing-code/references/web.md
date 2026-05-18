# Web Review Slice

Language-specific review material for HTML/CSS/JS/HTMX. The host skill supplies scope, workflow, and the findings/output contract — this file supplies only the web tooling and focus-area checks.

## Run tooling first

Execute these before manual review to catch issues programmatically:

```bash
npx html-validate <files>  # if configured (or bunx)
npx stylelint <files>      # if configured (or bunx)
```

If a validator is missing, note it in findings rather than guessing. Ground every finding in tool output — quote the line of output that drives each finding.

## Security

- XSS: don't use `innerHTML` with user data; use `textContent`
- CSRF: forms need tokens (HTMX: `hx-headers` with CSRF token)
- Secrets: no API keys or passwords in JS/HTML
- Links: validate URLs before `window.location` redirect

```html
<!-- HTMX CSRF pattern -->
<body hx-headers='{"X-CSRF-Token": "{{.CSRFToken}}"}'></body>
```

## Performance

- Scripts: use `defer` on `<script>` tags
- Images: add `loading="lazy"` for below-fold images
- Images: include `width`/`height` to prevent layout shift
- CSS: one stylesheet, no `@import` chains

## Accessibility

- Images need `alt` text
- Form inputs need `<label>`
- Color contrast: 4.5:1 for text
- Interactive elements must be keyboard-accessible
- Don't remove focus outlines without a replacement

## Failure handling

- Validators not installed: note it and proceed with manual review only.
- Security issue cannot be confirmed without server-side context (e.g., CSRF token source): flag as "needs server-side verification" rather than a definite finding.
- Contrast ratios cannot be measured without tooling: note the limitation and flag visually suspect colors for manual check.
- Codebase uses a framework outside this scope: note it and limit findings to the HTML/CSS/JS layer only.
