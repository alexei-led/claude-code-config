---
allowed-tools: Bash, Read, Grep, Glob
description: Consult Gemini for architecture and design decisions
argument-hint: [brainstorm]
---

# Design Consultation

Consult Gemini AI for architecture alternatives, design trade-offs, and brainstorming.

Use the **asking-gemini** skill when evaluating architectural approaches, comparing design options, or generating creative ideas.

## Arguments

- `brainstorm` → Generate multiple creative alternatives
- (empty) → Focused design analysis

## Workflow

1. Gather context from user (architecture, challenge, constraints)
2. Consult Gemini using the asking-gemini skill
3. Present analysis with alternatives and recommendations

## Output Format

```markdown
## Design Analysis

### Current Approach

[Summary]

### Alternatives

1. **Option A**: Pros/Cons
2. **Option B**: Pros/Cons

### Recommendation

[Which approach and why]
```

**Execute consultation now using the asking-gemini skill.**
