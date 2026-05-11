# Context7 Documentation Commands

Context7 docs lookup is a two-step CLI workflow: resolve a library name to an
ID, then query docs using that ID.

If the user already provided `/org/project` or `/org/project/version`, skip
resolution and pass that ID directly to `ctx7 docs`.

## Resolve a Library

```bash
ctx7 library react "React useEffect cleanup function with async operations"
ctx7 library nextjs "Next.js middleware in app router"
ctx7 library prisma "Prisma one-to-many cascade delete"
```

Always pass a real query. The query affects ranking and disambiguation.

Do not include secrets, credentials, personal data, private payloads, or
proprietary code in queries.

Result fields commonly include:

- Library ID such as `/facebook/react`.
- Name and description.
- Code snippet count.
- Source reputation.
- Benchmark score.
- Versions, when available.

Selection rules:

1. Prefer exact or near-exact library name matches.
2. Prefer descriptions that match the user's actual topic.
3. Prefer higher code snippet count and source reputation.
4. Use version-specific IDs when the requested version appears in results.
5. Ask for clarification when the library name is ambiguous and the best match
   is not obvious.

Limit: do not call `ctx7 library` more than 3 times for one question.

## Query Documentation

```bash
ctx7 docs /facebook/react "React useEffect cleanup function with async operations"
ctx7 docs /vercel/next.js "Next.js middleware in app router"
ctx7 docs /prisma/prisma "Prisma one-to-many cascade delete"
```

Use the resolved ID exactly. The ID must start with `/`.

Use specific queries:

| Quality | Query                                                    |
| ------- | -------------------------------------------------------- |
| Good    | `React useEffect cleanup function with async operations` |
| Good    | `FastAPI dependency overrides in pytest tests`           |
| Bad     | `hooks`                                                  |
| Bad     | `auth`                                                   |

Limit: do not call `ctx7 docs` more than 3 times for one question.

## JSON Output

Use JSON when structure helps selection, quoting, or post-processing:

```bash
ctx7 library react "React hooks state management" --json
ctx7 docs /facebook/react "React hooks state management" --json
```

## Missing CLI

If `ctx7` is not installed, use the package runner:

```bash
npx ctx7@latest library react "React hooks state management"
npx ctx7@latest docs /facebook/react "React hooks state management"
```

## Empty or Weak Results

When the docs are missing or weak:

1. Broaden or rephrase the query once.
2. Try a more specific library name once.
3. Use the best result if it is good enough.
4. Otherwise use available web tools such as `web_search` or `web_answer` for
   official docs or release notes, and say that a fallback was used.
