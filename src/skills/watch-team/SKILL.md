---
name: watch-team
description:
  Monitor a Claude Code team in tmux, auto-approve prompts, and report status.
  Use when the user says "watch the team", "monitor agents", "auto-approve", "babysit
  team", or "agents are stuck". NOT for single-agent monitoring, non-tmux setups, or
  general process supervision.
---

# Watch Team

Monitor all panes in a tmux window running a Claude Code team. Detect stuck
agents waiting on approval prompts, auto-approve them, and report task/team
status.

## Steps

1. **Identify team window** — find the tmux window (from a passed argument or
   by listing available windows).
2. **List panes** — get all pane indexes, sizes, commands, and PIDs.
3. **Check task status** — read `~/.claude/tasks/<team>/` for in_progress and
   pending tasks.
4. **Auto-approve loop** — poll all panes for "Do you want to proceed?" every
   3 seconds.
5. **Report** — summarize what was unblocked and current task states.
6. **Warn if lead is stuck** — alert if the lead pane is over 90% budget or
   under 10% context.

## Auto-approver

```bash
WINDOW="ccbot:3"
PANE="1"
DURATION="${2:-300}"
END=$((SECONDS + DURATION))

while [ $SECONDS -lt $END ]; do
  output=$(tmux capture-pane -t $WINDOW.$PANE -p 2>/dev/null)
  if echo "$output" | grep -q "Do you want to proceed?"; then
    tmux send-keys -t $WINDOW.$PANE Enter
    echo "$(date +%H:%M:%S) Approved prompt in pane $PANE"
  fi
  sleep 3
done
```

## Kill stuck lead

If the lead pane is at 100% budget or under 5% context:

```bash
tmux list-panes -t <window> -F '#{pane_index} #{pane_pid}' | while read idx pid; do
  kill $pid 2>/dev/null
done
```

Then commit remaining work manually with git.

## Failure handling

- No tmux session found: list sessions with `tmux ls`; ask the user which window to watch.
- `~/.claude/tasks/<team>/` missing: skip task-status check and note it in the report.
- Auto-approve loop exits with no prompts seen: report "no prompts detected in <N>s" — do not re-run silently.

## Output format

```
## Team Status — <window>

Watched: <duration>s | Panes: <N>

### Unblocked
- pane <N>: approved prompt at <HH:MM:SS>

### Task States
- <task>: in_progress / pending / done

### Warnings
- lead pane at <X>% context budget
```
