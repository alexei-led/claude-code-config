---
model: haiku
allowed-tools: []
description: Quick methodology guide for spec-driven development
---

# Spec-Driven Development Guide

**Print this guide directly - no tools needed.**

---

## Output

```
╭──────────────────── SPEC-DRIVEN DEVELOPMENT ────────────────────╮
│                                                                 │
│         DESIGN ──────▶ PLAN ──────▶ IMPLEMENT                  │
│       /spec:interview  /spec:plan   /spec:work                 │
│       (requirements)   (tasks)      (code)                     │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ PHASE 1: DESIGN (WHAT/WHY)                                      │
│   /spec:interview <idea>    Deep questioning → REQ-*.md         │
│   /spec:interview REQ-xxx   Refine existing requirement         │
│                                                                 │
│ PHASE 2: PLAN (HOW)                                             │
│   /spec:plan REQ-xxx        Create EPIC + TASK files            │
│   /spec:plan EPIC-xxx       Refine existing epic                │
│                                                                 │
│ PHASE 3: IMPLEMENT                                              │
│   /spec:work                Start next ready task               │
│   /spec:work EPIC-xxx       Work on specific epic               │
│   /spec:work TASK-xxx       Work on specific task               │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ OTHER COMMANDS                                                  │
│   /spec:init          Initialize .spec/ folder                  │
│   /spec:status        Show progress overview                    │
│   /spec:done TASK-xxx Mark task complete                        │
│   /spec:new task xxx  Create new task file                      │
│   /spec:help          This guide                                │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ CLI HELPER (specctl)                                            │
│   specctl ready           Unblocked tasks in priority order     │
│   specctl start TASK-xxx  Mark task in_progress                 │
│   specctl done TASK-xxx   Mark done with evidence               │
│   specctl validate        Check for issues                      │
│   specctl status          Progress overview                     │
│   specctl dep add A B     A depends on B                        │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ FILE STRUCTURE                                                  │
│   .spec/                                                        │
│   ├── reqs/REQ-*.md      Requirements (WHAT) - from interview   │
│   ├── epics/EPIC-*.md    Epics grouping tasks                   │
│   ├── tasks/TASK-*.md    Tasks with dependencies                │
│   └── PROGRESS.md        Session activity log                   │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ KEY PRINCIPLES                                                  │
│   • REQ = WHAT/WHY (business requirements, success criteria)    │
│   • TASK = HOW (implementation steps, acceptance criteria)      │
│   • One task per session - complete before starting next        │
│   • Quality gates: make build && make test && make lint         │
│   • You approve every edit - no hidden automation               │
│                                                                 │
╰─────────────────────────────────────────────────────────────────╯

START HERE:
  No .spec/ folder? → /spec:init
  Have an idea?     → /spec:interview "your feature idea"
  Have REQ files?   → /spec:plan REQ-xxx
  Have TASK files?  → /spec:work
```

**Print this exactly as shown above.**
