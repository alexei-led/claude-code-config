# Context7 Skill Commands

The `ctx7 skills` commands manage AI coding skills from the Context7 registry.
Use them only when the user explicitly asks to search, install, list, remove,
or generate Context7 skills. They are not required for normal documentation
lookup.

## Install

Repository format is `/owner/repo`.

```bash
ctx7 skills install /anthropics/skills
ctx7 skills install /anthropics/skills pdf
ctx7 skills install /anthropics/skills --all
```

Target portable installs when the user has not asked for an assistant-specific
location:

```bash
ctx7 skills install /anthropics/skills pdf --universal
ctx7 skills install /anthropics/skills --all --global
```

## Search

```bash
ctx7 skills search pdf
ctx7 skills search typescript testing
ctx7 skills search react nextjs
```

## Suggest

```bash
ctx7 skills suggest
ctx7 skills suggest --global
```

This scans common dependency files such as `package.json`, `pyproject.toml`,
`requirements.txt`, `go.mod`, `Cargo.toml`, `Gemfile`, and similar manifests.

## List and Remove

```bash
ctx7 skills list
ctx7 skills list --global
ctx7 skills remove pdf
ctx7 skills remove pdf --global
```

## Generate

```bash
ctx7 skills generate
ctx7 skills generate --global
```

Generation requires login and may send user-provided instructions to the
service. Do not include secrets, credentials, personal data, private payloads,
or proprietary code in generation prompts.

## Preview Repository Skills

```bash
ctx7 skills info /anthropics/skills
```

Use this before installing unfamiliar skills. Installing mystery prompts from
the internet without reading them first is how machines get haunted.
