---
allowed-tools:
- Bash(ccgram msg *)
- Bash(ccgram msg send *)
- Bash(ccgram msg reply *)
- Bash(ccgram msg inbox *)
- Bash(ccgram msg list-peers *)
- Bash(ccgram msg find *)
- Bash(ccgram msg broadcast *)
- Bash(ccgram msg register *)
- Bash(ccgram msg spawn *)
- Bash(ccgram msg read *)
- Bash(ccgram msg sweep *)
argument-hint: '[inbox|send|broadcast|peers|spawn]'
description: 'Inter-agent messaging via ccgram swarm. Use when communicating with
  other agents in the same tmux session — send messages, check inbox, discover peers,
  broadcast status, reply to requests, or spawn new agents. Activates on: peer messages,
  inbox, swarm, ccgram, broadcast, agent collaboration, ask another agent.'
name: ccgram-messaging
---

<!-- Platform guidance for non-Claude models (Codex CLI, Gemini CLI) -->
<!-- Persistence: Keep going until the task is fully resolved. Do not stop at the first obstacle. -->
<!-- Tool use: Use available tools to verify — do not guess at file contents, paths, or command output. -->
<!-- Planning: Reflect between steps. Decompose complex problems into logical sub-steps before acting. -->
<!-- Reliability: Assess risk before irreversible actions. Ask for clarification on ambiguity. -->
<!-- Completeness: Generate complete responses without truncating. Review your output against the original constraints. -->

# Inter-Agent Messaging (ccgram swarm)

You are part of a multi-agent swarm managed by ccgram. Each agent runs in its own tmux window. Use `ccgram msg` commands to collaborate with peers.

Your window ID is in `$CCGRAM_WINDOW_ID` (format: `session:@N`, e.g. `ccgram:@3`).

## Step 1: Register

Declare your identity so peers can discover you:

```bash
ccgram msg register --task "brief description of current work" --team "team-name"
```

Update registration when your task changes.

## Step 2: Discover Peers

```bash
ccgram msg list-peers              # all active windows
ccgram msg find --team backend     # filter by team
ccgram msg find --provider claude  # filter by provider
ccgram msg find --cwd "*/api-*"   # filter by working directory glob
```

Peer IDs use `session:@N` format. Pass them directly to `send`.

## Step 3: Check Inbox

```bash
ccgram msg inbox          # pending messages
ccgram msg inbox --json   # machine-readable
ccgram msg read <msg-id>  # mark as read + display full message
```

**When you have peer messages:**

1. Summarize them to the user
2. Ask before processing (unless spawned with `--auto`)

**When to check inbox:** after completing a task, when idle, or when the user asks.

## Step 4: Send Messages

```bash
# Fire-and-forget
ccgram msg send <peer-id> "your message" --subject "topic"

# Block until reply (60s default timeout)
ccgram msg send <peer-id> "question?" --wait

# Reply to a received message (use the msg-id from inbox)
ccgram msg reply <msg-id> "your answer"
```

**Message types:**

- `send` — request to a specific peer (TTL: 60min)
- `reply` — response to a received message (TTL: 120min)
- `broadcast` — notification to multiple peers (TTL: 480min)

## Step 5: Broadcast

Notify all matching peers at once:

```bash
ccgram msg broadcast "API contract changed — regenerate clients" --team backend
ccgram msg broadcast "v2 migration complete" --provider claude
```

## Step 6: Spawn New Agents

Request a new agent window (requires Telegram approval):

```bash
ccgram msg spawn --provider claude --cwd ~/project --prompt "implement feature X"
ccgram msg spawn --provider claude --cwd ~/project --prompt "run tests" --auto
```

Use `--auto` only for autonomous tasks that need no user interaction.

**Prefer messaging an existing peer over spawning** when someone is already working in the relevant codebase.

## Handling Incoming Messages

When a message is injected into your context (format: `[MSG <id> from ...]`), extract the `msg-id` and reply:

```bash
ccgram msg reply <msg-id> "your answer"
```

## Rate Limits and Safety

- **10 messages per 5 minutes** per window (send + broadcast combined)
- **3 spawns per hour** per window
- The broker detects A-B-A-B message loops and pauses delivery automatically
- Messages over 10KB: use `--file <path>` instead of inline body
- Merged delivery: multiple pending messages may arrive as a single batch

## Cleanup

```bash
ccgram msg sweep   # remove expired messages from all inboxes
```

---

## Output Format

When reporting messaging status to the user:

```
## Swarm Status

**My ID**: ccgram:@3 (api-gateway)
**Peers**: 4 active

| Peer | Window | Team | Task | Branch |
|------|--------|------|------|--------|
| ccgram:@0 | payment-svc | backend | refactor checkout | feat/checkout |
| ccgram:@5 | web-ui | frontend | dashboard | feat/dashboard |

**Inbox**: 2 pending messages
1. [request] from @0 (payment-svc): "Need API schema for /orders endpoint"
2. [notify] from @5 (web-ui): "Dashboard types updated"
```

## Examples

```
/ccgram-messaging inbox              # check and summarize inbox
/ccgram-messaging send               # discover peers, pick one, send message
/ccgram-messaging broadcast          # broadcast status to team
/ccgram-messaging peers              # list all active peers
/ccgram-messaging spawn              # spawn a new agent for a subtask
```

**Execute this workflow now.**
