---
name: brainstorming-ideas
description: Turn ideas into designs through collaborative dialogue. Use when user wants to brainstorm, design features, explore approaches, or think through implementation before coding.
user-invocable: true
context: fork
model: sonnet
allowed-tools:
  - AskUserQuestion
  - Task
  - TodoWrite
  - Read
  - Grep
  - Glob
  - Write
  - mcp__perplexity-ask__perplexity_ask
  - WebFetch
  - Bash(git *)
argument-hint: [<topic>]
---

# Brainstorming Ideas Into Designs

Transform vague ideas into fully-formed designs through structured collaborative dialogue.

**Use TodoWrite** to track these 5 phases:

1. Gather context and understand the idea
2. Explore requirements (Starbursting questions)
3. Research similar solutions (optional)
4. Present approaches with recommendation
5. Validate design incrementally and document

---

## Core Principles

- **One question at a time** - Never batch multiple questions
- **Multiple choice preferred** - Easier to answer than open-ended
- **YAGNI ruthlessly** - Challenge every feature's necessity
- **Incremental validation** - Present design in 200-300 word sections
- **Research when helpful** - Don't research obvious patterns

---

## Phase 1: Gather Context

### 1a. Explore Codebase (Background)

Spawn Explore agent to understand project state:

```
Task(
  subagent_type="Explore",
  prompt="Quick scan: project structure, tech stack, recent changes, existing patterns",
  run_in_background=true
)
```

### 1b. Initial Question

Use AskUserQuestion:

| Header    | Question                           | Options                                                                                                                                                                                       |
| --------- | ---------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Idea type | What would you like to brainstorm? | 1. **New feature** - Add new functionality 2. **Modification** - Change existing behavior 3. **Integration** - Connect with external system 4. **Exploration** - Not sure yet, let's discover |

---

## Phase 2: Explore Requirements (Starbursting)

Ask questions **one at a time** using AskUserQuestion. Adapt based on idea type.

### Question Framework (5WH)

| Question Type | When to Ask                    | Example AskUserQuestion                                                              |
| ------------- | ------------------------------ | ------------------------------------------------------------------------------------ |
| **WHO**       | Always first                   | "Who will use this?" → Options: Existing users, New segment, Internal, API consumers |
| **WHY**       | After WHO                      | "What problem does this solve?" → Options based on detected pain points              |
| **WHAT**      | After WHY is clear             | "What's the core capability?" → Open or options based on research                    |
| **WHERE**     | For integrations/modifications | "Where should this live?" → Options based on codebase exploration                    |
| **HOW**       | After approach research        | "How should we implement?" → Present 2-3 technical approaches                        |

### Adaptive Questioning

- Skip questions when answers are obvious from context
- If user seems certain, move faster to approaches
- If user seems uncertain, explore deeper with sub-questions
- Use "Other" option to allow custom responses

---

## Phase 3: Research Similar Solutions (Optional)

Trigger research when:

- User says "research", "how do others", "best practice"
- Idea is novel or complex
- Multiple valid approaches exist

### 3a. Perplexity Query

```
mcp__perplexity-ask__perplexity_ask({
  messages: [{
    role: "user",
    content: "How do leading [industry] products implement [feature type]? Include architectural patterns, UX approaches, and trade-offs. Focus on [tech stack] implementations."
  }]
})
```

### 3b. Follow Citations

After Perplexity response, WebFetch top 2-3 relevant sources:

```
WebFetch(url="<citation-url>", prompt="Extract implementation details, code patterns, and lessons learned for [feature]")
```

### 3c. Synthesize Findings

Present research summary before asking approach preference:

```markdown
## Research Findings

**Common patterns:**

- [Pattern 1]: Used by X, Y. Trade-off: ...
- [Pattern 2]: Used by Z. Trade-off: ...

**Recommended for our context:** [Pattern] because [reasons]
```

---

## Phase 4: Present Approaches

Use AskUserQuestion with 2-4 options:

| Header   | Question                  | Options                                                                                                                              |
| -------- | ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| Approach | Which approach fits best? | 1. **[Recommended]** - Description + key trade-off 2. **[Alternative]** - Description + key trade-off 3. **Minimal** - YAGNI version |

### Approach Template

For each option, briefly cover:

- **What**: Core implementation
- **Trade-offs**: Complexity vs flexibility, Now vs later
- **Fits when**: Scenario where this shines

---

## Phase 5: Validate Design Incrementally

Present design in sections (~200-300 words each). After each section, use AskUserQuestion:

| Header   | Question                        | Options                                                                                                                    |
| -------- | ------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| Validate | Does this [section] look right? | 1. **Yes, continue** - Move to next section 2. **Needs changes** - I'll explain 3. **Go back** - Revisit earlier decisions |

### Design Sections

1. **Architecture Overview** - Components, responsibilities, relationships
2. **Data Flow** - How information moves through the system
3. **API/Interface** - External contracts and user interactions
4. **Error Handling** - Failure modes and recovery strategies
5. **Testing Strategy** - How to verify it works

### YAGNI Checkpoints

At each section, actively challenge:

- "Do we need this now, or is it speculative?"
- "What's the simplest version that solves the problem?"
- "Can we defer this complexity?"

---

## Phase 6: Document and Next Steps

### 6a. Write Design Document

```
Write(
  file_path="docs/plans/YYYY-MM-DD-<topic>-design.md",
  content="# [Feature] Design\n\n## Problem\n...\n## Solution\n...\n## Architecture\n..."
)
```

### 6b. Commit Design

```bash
git add docs/plans/*.md && git commit -m "docs: add [feature] design document"
```

### 6c. Implementation Handoff

Use AskUserQuestion:

| Header     | Question                              | Options                                                                                                                                                           |
| ---------- | ------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Next steps | Ready to proceed with implementation? | 1. **Create worktree** - Isolated workspace via using-git-worktrees 2. **Create plan** - Detailed implementation steps 3. **Done for now** - Just save the design |

---

## Methodology Reference

This skill incorporates proven brainstorming techniques:

| Technique                 | How It's Used                                                                               |
| ------------------------- | ------------------------------------------------------------------------------------------- |
| **Starbursting (5WH)**    | Structured questions in Phase 2                                                             |
| **Design Thinking**       | Empathize (context) → Define (WHY) → Ideate → Prototype (design sections)                   |
| **SCAMPER**               | For modifications: Substitute, Combine, Adapt, Modify, Put to other use, Eliminate, Reverse |
| **Reverse Brainstorming** | "How could this fail?" during validation                                                    |
| **Mind Mapping**          | Architecture section visualizes relationships                                               |

---

## Examples

```
/brainstorming-ideas                    # Start open-ended brainstorm
/brainstorming-ideas user notifications # Brainstorm notification feature
/brainstorming-ideas auth flow          # Brainstorm authentication changes
```

**Execute this collaborative brainstorming workflow now.**
