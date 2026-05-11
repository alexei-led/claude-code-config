# Context7 CLI Setup

The portable workflow only needs the CLI. Prefer a local install when the user
wants repeat use, or `npx ctx7@latest` for one-off use.

## Install

```bash
npm install -g ctx7@latest
```

## One-Off Use

```bash
npx ctx7@latest library react "React hooks state management"
npx ctx7@latest docs /facebook/react "React hooks state management"
```

## Authentication

Most docs commands work without login. Authentication can increase rate limits
and is required for some skill generation commands.

```bash
ctx7 login
ctx7 login --no-browser
ctx7 logout
ctx7 whoami
```

An API key can be provided through the environment when the user already has
one:

```bash
export CONTEXT7_API_KEY=your_key
```

Do not ask the user to paste secrets into chat. If an API key is needed, tell
them to set it in their shell or secret manager.

## Health Check

```bash
ctx7 --help
ctx7 library react "React hooks state management"
```

If the binary is missing, use `npx ctx7@latest` rather than stopping.
