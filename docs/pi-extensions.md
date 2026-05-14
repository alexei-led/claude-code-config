# Pi Extensions

Extensions bundled with cc-thingz that run inside [Pi](https://pi.dev). All
extensions install automatically when you `pi install` this package.

## Included Extensions

### hook-runner

Bridges Pi's lifecycle events to the same CC-compatible hook scripts used by
Claude Code, Codex, and Gemini. This is the primary integration point between
Pi and the rest of cc-thingz.

**What it wires:**

| Pi event                   | Hook script         | Behavior                                                 |
| -------------------------- | ------------------- | -------------------------------------------------------- |
| `session_start`            | `session-start.py`  | Prints project context to chat on startup                |
| `session_start` / all      | `ccgram hook`       | Tracks sessions in ccgram (async)                        |
| `before_agent_start`       | `skill-enforcer.sh` | Suggests relevant skills before each prompt              |
| `tool_call` (Write/Edit)   | `file-protector.py` | Blocks writes to protected paths                         |
| `tool_call` (Bash)         | `git-guardrails.sh` | Blocks destructive git commands                          |
| `tool_result` (Write/Edit) | `smart-lint.sh`     | Injects lint errors into tool result (LLM feedback loop) |
| `tool_result` (Write/Edit) | `test-runner.sh`    | Runs tests after edits (async, notifies on failure)      |
| `agent_end`                | `ccgram hook`       | Tracks session end in ccgram (async)                     |
| `agent_end`                | `notify.sh`         | Fires a macOS notification banner when the agent is idle |

**User hooks:** Merge additional hooks on top of built-ins by adding a `hooks`
key to `~/.pi/agent/settings.json` or `.pi/settings.json`:

```jsonc
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "/usr/local/bin/my-audit.sh",
            "timeout": 10,
          },
        ],
      },
    ],
  },
}
```

Hook commands run via `bash -c`, so shell features and PATH resolution work.
User hooks are appended after built-ins. The `matcher` field is a
case-insensitive regex matched against the CC tool name (e.g. `Write`, `Bash`,
`MultiEdit`).

**Exit code semantics** (same as Claude Code):

- `0` — allow; stdout shown to user (SessionStart) or injected as LLM context (UserPromptSubmit)
- `1` — non-blocking error; logged and shown to user, execution continues
- `2` — significant: blocks the tool call (PreToolUse), injects stderr into tool result so the LLM self-corrects (PostToolUse), or injects context before the prompt (UserPromptSubmit)

### ask-user-question

Registers an `ask_user_question` tool that lets the LLM ask the user
structured questions (single-select, multi-select, or free text). Used by
`smart-lint.sh` when it needs a decision before applying a fix.

No configuration.

### permission-gate

Intercepts `bash` tool calls matching dangerous patterns (`rm -rf`, `sudo`,
`chmod/chown 777`) and prompts the user before proceeding. In non-interactive
mode, blocks automatically.

No configuration needed. If you want to disable it, remove or rename the
extension after install.

### plan-mode

Adds a plan mode that intercepts the agent's plan output, extracts numbered
steps, and surfaces a progress tracker in the Pi TUI. Destructive bash
commands are blocked while plan mode is active.

No configuration.

### structured-output

Registers a `structured_output` tool for the LLM to emit machine-readable
JSON. Used by skills that need to pass structured data to follow-on tools.

No configuration.

### subagent

Provides `spawn_subagent`, `steer_subagent`, and `get_subagent_result` tools,
enabling multi-agent orchestration inside a single Pi session.

No configuration.

### todo

Registers a `todo` tool for the LLM to maintain a persistent todo list across
an agent session. Displayed in the Pi TUI sidebar.

No configuration.

---

## Recommended Third-Party Extensions

These extensions are used by cc-thingz skills or complement the workflow.
Install each with `pi install`.

### pi-powerline-footer

Adds a configurable powerline-style status footer to the Pi TUI.

```bash
pi install npm:pi-powerline-footer
```

No skills depend on this directly, but it improves session readability.

### @tintinweb/pi-subagents

Provides the agent loader that reads agents from `~/.pi/agent/agents/`. Required
for cc-thingz Pi agents to work:

```bash
pi install npm:@tintinweb/pi-subagents
ln -snf \
  ~/.pi/agent/git/github.com/alexei-led/cc-thingz/dist/pi/agents \
  ~/.pi/agent/agents
```

Project-local custom agents are read from `.pi/agents/*.md`. This repo adds
an `advisor` agent in source layout:

- `src/agents/advisor/AGENT.md`
- `src/agents/advisor/pi/frontmatter.yaml`

Compiled artifact: `dist/pi/agents/advisor.md`.

Advisor can use read-only exploration tools (`read`, `grep`, `find`, `ls`,
read-only `bash`) and must avoid file edits.

Expected advisor output:

- `Verdict`
- `Top Risks` (ranked)
- `Next Actions` (ordered, concrete)

Invoke with `Agent({ subagent_type: "advisor", ... })`.

### revdiff

Used by the `reviewing-code` skill for rendering code review diffs in Pi.

```bash
pi install git:github.com/umputun/revdiff
```

### pi-web-providers

Adds web search and research providers to Pi (used by `researching-web` and
`looking-up-docs` skills).

```bash
pi install npm:pi-web-providers
```

### @latentminds/pi-quotas

Tracks token and cost quotas per session. Useful when running long coding
sessions.

```bash
pi install npm:@latentminds/pi-quotas
```

---

## Extension Loading

Pi loads extensions from the directories declared in `package.json`:

```json
"pi": {
  "extensions": ["./dist/pi/extensions"],
  "skills": ["./dist/pi/skills"]
}
```

After `make build`, run `pi install "$(pwd)"` (or `pi install git:github.com/alexei-led/cc-thingz`)
to register the latest build. Run `/reload` in Pi or restart it to pick up changes.

Test files (`*.test.ts`) are excluded from `dist/pi/extensions/` by the build
compiler and are never loaded by Pi.
