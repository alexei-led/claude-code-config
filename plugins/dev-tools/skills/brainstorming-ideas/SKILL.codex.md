---
name: brainstorming-ideas
description: Collaborative design workflow — gather context through prose dialogue, explore the codebase for existing patterns, propose 2-3 approaches with trade-offs, ask the user to choose, then detail the chosen approach and write a design document.
---

# Brainstorming Ideas Into Designs

Turn a vague idea into a well-formed design through structured dialogue and codebase exploration. Work through the phases in order. Ask questions as natural prose — one question at a time. Do not move to the next phase until you have a clear answer from the user.

## Core principles

- Ask before exploring — understand the idea first, then look at code
- One question at a time — never bundle multiple questions together
- YAGNI at every step — actively challenge whether each piece is needed now
- Present design in small sections (~200 words each) and confirm before continuing
- Propose 2-3 concrete options with trade-offs; let the user pick

## Step 1: Understand the idea

Ask the user to describe what they want to brainstorm. A simple open question works: "What's the idea you'd like to explore?" Wait for their answer.

Based on their response, ask targeted follow-up questions one at a time:

- What triggered this idea — is there a concrete pain point it addresses?
- Who will use it (end users, internal tooling, API consumers)?
- Is there an existing feature this builds on or replaces?

Stop when you can state the problem in one sentence and move on.

## Step 2: Surface requirements (5WH)

Work through these questions in order, skipping any whose answer is already clear. Ask each as plain conversational prose — not as a list of options.

1. **WHO** — who uses this feature?
2. **WHY** — what does it solve that isn't solved today?
3. **WHAT** — what is the core capability, in one sentence?
4. **WHERE** — where in the system does it live?
5. **HOW** — any strong preferences on implementation approach?

After gathering answers, state the assumptions you are carrying forward explicitly:

> "Based on what you've described, I'm assuming: (1) ... (2) ... (3) ..."

Ask: "Are any of these wrong?" Adjust before continuing if needed.

## Step 3: Explore the codebase

Now that you understand the idea, use Glob and Read to explore relevant parts of the codebase. Do not assume what exists — look.

Find:

- Similar features or modules that do something adjacent
- The tech stack and conventions in use (frameworks, data access, testing patterns)
- Integration points the new feature would need to touch
- Any prior attempts at solving this, even incomplete ones

Summarize in 3-5 bullet points what you found and what it means for the design. Call out constraints (e.g., "the auth layer uses middleware X, so new routes should follow the same pattern").

If the user asked to research external solutions, go to Step 4. Otherwise skip to Step 5.

## Step 4: Research external solutions (only if requested)

Look up how comparable products or open-source projects solve this problem. Focus on:

- Architectural patterns that apply to this tech stack
- Known trade-offs and common failure modes
- Anything that would change your approach

Summarize in a short paragraph before moving to approaches.

## Step 5: Propose 2-3 approaches

Present distinct options. For each:

- **What**: one sentence describing the approach
- **Trade-offs**: complexity vs. simplicity, flexibility vs. speed to ship
- **Best when**: the scenario where this option wins

Mark one as recommended and explain briefly why it fits the current context. Then ask: "Which of these fits best, or would you like to adjust one of them?"

Wait for the user's choice before continuing.

## Step 6: Detail the chosen design

Present the design in sections of ~200 words each. After each section, ask "Does this look right?" and wait for confirmation before continuing.

Cover these sections in order:

1. **Architecture overview** — components, responsibilities, and how they relate
2. **Data flow** — how information moves through the system end-to-end
3. **API or interface** — external contracts and how callers interact
4. **Error handling** — failure modes and recovery strategies
5. **Testing strategy** — what to test and how

At each section apply a YAGNI check: "Is this piece needed now, or can it be deferred?" Cut anything speculative.

## Step 7: Write design document and propose next steps

Write the completed design to:

```
docs/plans/YYYY-MM-DD-<topic>-design.md
```

Include: Problem, Solution, Architecture, Data Flow, API, Error Handling, Testing Strategy, Open Questions.

Then ask the user: "Ready to move to implementation? I can set up a git worktree for isolated work, write a detailed task plan, or just leave you with the saved design."

## Output format

The design document is the primary artifact. In the chat, summarize:

```
DESIGN COMPLETE
===============
Topic: <topic>
Approach chosen: <name>
Document: docs/plans/YYYY-MM-DD-<topic>-design.md

Key decisions:
- <decision 1>
- <decision 2>

Open questions:
- <anything left unresolved>
```
