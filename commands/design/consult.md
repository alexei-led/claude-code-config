---
allowed-tools: Bash, Read, Grep, Glob
description: Consult Gemini for architecture and design decisions
argument-hint: [brainstorm]
---

# Design Consultation

Use the **asking-gemini** skill to consult Gemini AI for architecture alternatives and design trade-offs.

## Arguments

Parse `$ARGUMENTS`:

- `brainstorm` → Generate multiple creative alternatives
- (empty) → Focused design analysis

## Workflow

### Step 1: Gather Context

Ask user what they want to explore:

- Current architecture or approach
- Specific design question or challenge
- Constraints or requirements

### Step 2: Consult Gemini

Invoke `gemini` CLI with appropriate mode:

**For brainstorming** (if `brainstorm` in arguments):

```bash
gemini "Brainstorm solutions for: <challenge>

Generate 5-10 creative approaches. For each:
- Brief description
- Key advantages
- Potential drawbacks
- When to prefer this approach"
```

**For focused analysis** (default):

```bash
gemini "Review and analyze: I'm designing <system>. Current approach: <desc>.

Provide:
1. Trade-offs of current approach
2. Alternative patterns to consider
3. Potential scaling or maintenance concerns
4. Recommendations with rationale"
```

**For comparing options**:

```bash
gemini "Compare options: <option A> vs <option B> for <use case>

For each option analyze:
- Performance characteristics
- Maintainability
- Complexity
- When to prefer each"
```

### Step 3: Present Results

Format response as:

```markdown
## Design Analysis

### Current Approach

[Summary of what was evaluated]

### Alternatives Considered

1. **Option A**: [description]
   - Pros: ...
   - Cons: ...

2. **Option B**: [description]
   - Pros: ...
   - Cons: ...

### Recommendation

[Which approach and why]

### Trade-offs to Consider

- [Key trade-off 1]
- [Key trade-off 2]
```

**Execute consultation now.**
