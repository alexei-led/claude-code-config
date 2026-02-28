# Sequential Thinking MCP

Multi-step reasoning for complex analysis and systematic problem solving.

> **Note**: 4.6 models handle most reasoning depth via adaptive thinking. Sequential thinking adds value for **explicit structured reasoning** — numbered steps, branch points, hypothesis tracking, and revision trails that persist visibly across tool calls. Use it when you need the reasoning *artifact*, not just the reasoning.

## When to Use

| Scenario                          | Use Sequential | Use Native Claude |
| --------------------------------- | -------------- | ----------------- |
| Complex debugging (3+ components) | Yes            | No                |
| Architecture decisions            | Yes            | No                |
| Multi-hop code flow tracing       | Yes            | No                |
| Security analysis                 | Yes            | No                |
| Simple function explanation       | No             | Yes               |
| Single file change                | No             | Yes               |
| Straightforward fixes             | No             | Yes               |
| Quick lookups                     | No             | Yes               |

## Decision Criteria

**Use Sequential when:**

- Problem involves 3+ interconnected components
- Need to reason through multiple possible causes
- Architectural trade-offs need evaluation
- Debugging requires hypothesis → test → refine cycle
- Security implications need systematic analysis

**Use Native Claude when:**

- Clear, bounded task with obvious solution
- Single file or function scope
- Direct question with factual answer
- Simple code generation from clear spec

## How It Works

Sequential thinking provides:

1. Structured thought steps (numbered, revisable)
2. Hypothesis generation and verification
3. Branch points for exploring alternatives
4. Explicit uncertainty markers
5. Final validated answer

## Example Usage

```
mcp__sequential-thinking__sequentialthinking(
  thought="Analyzing the slow API response. Step 1: Check if bottleneck is DB, network, or compute...",
  thoughtNumber=1,
  totalThoughts=5,
  nextThoughtNeeded=true
)
```

## Best Practices

1. **Start with estimate**: Begin with reasonable totalThoughts (5-10)
2. **Adjust as needed**: Increase totalThoughts if problem is deeper than expected
3. **Branch for alternatives**: Use branchFromThought when exploring different approaches
4. **Mark revisions**: Set isRevision=true when reconsidering earlier conclusions
5. **Generate hypothesis**: Propose solution before final thought
6. **Verify before done**: Only set nextThoughtNeeded=false when confident

## Combine With

- **warpgrep**: Sequential for reasoning, warpgrep for code exploration
- **Subagents**: Sequential for main reasoning, spawn agents for parallel investigation
- **Native tools**: Use Read/Grep to gather facts, Sequential to analyze them
