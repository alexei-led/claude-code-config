---
allowed-tools:
- Read
- Grep
- Glob
argument-hint: <question or topic>
description: Dialectic thinking — spawn thesis and antithesis agents to stress-test
  ideas, then synthesize and verify against code. Use when user says "debate", "argue
  both sides", "devil's advocate", "stress test this idea", "pros and cons of approach",
  or wants rigorous evaluation of a design decision.
name: debating-ideas
---

<!-- Platform guidance for non-Claude models (Codex CLI, Gemini CLI) -->
<!-- Persistence: Keep going until the task is fully resolved. Do not stop at the first obstacle. -->
<!-- Tool use: Use available tools to verify — do not guess at file contents, paths, or command output. -->
<!-- Planning: Reflect between steps. Decompose complex problems into logical sub-steps before acting. -->
<!-- Reliability: Assess risk before irreversible actions. Ask for clarification on ambiguity. -->
<!-- Completeness: Generate complete responses without truncating. Review your output against the original constraints. -->

# Dialectic Debate

Stress-test ideas by spawning competing perspectives, then synthesize and ground-truth against code.

**`$ARGUMENTS` is the question or topic to debate.**

If no argument provided, ask the user what they want to evaluate.


1. Frame the debate
2. Spawn thesis + antithesis agents
3. Synthesize positions
4. Verify claims against code

---

## Phase 1: Frame the Debate

Parse the topic from `$ARGUMENTS`. Identify:

- **The core tension** — what are the two opposing positions?
- **Stakes** — what depends on getting this right?
- **Scope** — bound the debate to avoid sprawl

Frame as a clear binary or spectrum question. Examples:

- "Should we use microservices or a monolith for X?"
- "Is caching worth the complexity here?"
- "Should this be a library or an inline implementation?"

---

## Phase 2: Spawn Thesis + Antithesis (Parallel)

Spawn two Explore agents in a single message:


---

## Phase 3: Synthesize

Collect both results:


Synthesize into a structured verdict:

1. **Where they agree** — shared facts, common ground
2. **Where they conflict** — genuine disagreements with evidence
3. **Weak arguments** — flag claims that lack code evidence or rely on generalities
4. **Verdict** — which position has stronger grounding, and why
5. **Conditions** — when would the other position win instead?

---

## Phase 4: Verify Claims

For any factual claims made by either side (file references, pattern assertions, dependency claims):

- Read the cited files to confirm accuracy
- Flag any misrepresentations or hallucinated evidence
- Adjust verdict if verification changes the balance

---

## Output

```
DEBATE: {topic}
==============

Thesis: {position A}
  Confidence: {high/medium/low}
  Key evidence: {1-2 strongest points with file refs}

Antithesis: {position B}
  Confidence: {high/medium/low}
  Key evidence: {1-2 strongest points with file refs}

Verdict: {position} wins because {reason}
Caveat: {position} would win if {conditions}

Verified claims: {N}/{M} checked, {K} corrected
```

---

## Examples

```
/debating-ideas Should we split the API into microservices?
/debating-ideas Is it worth adding Redis caching to the auth flow?
/debating-ideas Monorepo vs polyrepo for our frontend packages
```

---

If the debate reaches no clear conclusion, present both positions with evidence and let the user decide.

**Frame the debate now.**
