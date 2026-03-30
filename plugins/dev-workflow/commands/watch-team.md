---
description: Monitor a Claude Code team in tmux, auto-approve prompts, and report status
allowed-tools: [Bash, Read]
argument-hint: "<tmux-window> [duration-seconds]"
---

# Watch Team

Monitor all panes in a tmux window running a Claude Code team. Detect stuck agents waiting on approval prompts, auto-approve them, and report task/team status.

## Steps

1. **Identify team window** — find the tmux window (from arg or list windows)
2. **List panes** — get all pane indexes, sizes, commands, and PIDs
3. **Check task status** — read `~/.claude/tasks/<team>/` for in_progress/pending tasks
4. **Auto-approve loop** — poll all panes for "Do you want to proceed?" every 3s
5. **Report** — summarize what was unblocked and current task states
6. **Warn if lead is stuck** — alert if lead pane is at >90% budget or <10% context

## Usage

```
/watch-team ccbot:3        # Watch window 3 for 5 minutes (default)
/watch-team ccbot:pumba 120  # Watch pumba window for 2 minutes
```

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

If lead is at 100% budget / <5% context:

```bash
tmux list-panes -t <window> -F '#{pane_index} #{pane_pid}' | while read idx pid; do
  kill $pid 2>/dev/null
done
```

Then commit remaining work manually with git.
